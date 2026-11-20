"""Deterministic recovery and reconciliation for application-owned paper state."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable

from persistent_state.contracts import Checkpoint, EventRecord, canonical_json
from persistent_state.replay import ReplayValidationError, replay_events
from persistent_state.repository import CheckpointIntegrityError


class RecoveryValidationError(ValueError):
    """Persisted history, checkpoint or materialized aggregate cannot be reconciled."""


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    state_json: str
    last_event_sequence: int
    replayed_event_count: int
    checkpoint_id: str | None
    aggregate_versions_json: str


Reducer = Callable[[dict, EventRecord], dict]


def _aggregate_versions(events: tuple[EventRecord, ...]) -> dict[str, int]:
    versions: dict[str, int] = {}
    for expected, event in enumerate(events, start=1):
        if not isinstance(event, EventRecord):
            raise RecoveryValidationError("persisted event history contains an invalid event")
        if event.event_sequence != expected:
            raise RecoveryValidationError(
                f"persisted event history is not contiguous: expected {expected}, got {event.event_sequence}"
            )
        if not event.aggregate_id:
            raise RecoveryValidationError(
                f"event {event.event_id} has no aggregate identity"
            )
        if event.aggregate_state_json is None:
            raise RecoveryValidationError(
                f"event {event.event_id} has no committed aggregate-state snapshot"
            )
        try:
            event_state = json.loads(event.aggregate_state_json)
            if not isinstance(event_state, dict) or canonical_json(event_state) != event.aggregate_state_json:
                raise ValueError("aggregate state snapshot is not canonical")
        except (TypeError, json.JSONDecodeError, ValueError) as exc:
            raise RecoveryValidationError(
                f"event {event.event_id} has an invalid aggregate-state snapshot"
            ) from exc
        if event.aggregate_id in versions and event.aggregate_version != versions[event.aggregate_id] + 1:
            raise RecoveryValidationError(
                f"aggregate version is not contiguous for {event.aggregate_id}"
            )
        if event.aggregate_id not in versions and event.aggregate_version != 1:
            raise RecoveryValidationError(
                f"aggregate {event.aggregate_id} does not begin at version 1"
            )
        versions[event.aggregate_id] = event.aggregate_version
    return versions


def _replay_with_snapshot_validation(
    initial_state_json: str,
    events: tuple[EventRecord, ...],
    *,
    starting_sequence: int,
    account_scope_id: str,
    reducer: Reducer,
):
    def checked_reducer(state: dict, event: EventRecord) -> dict:
        next_state = reducer(state, event)
        aggregates = next_state.get("aggregates") if isinstance(next_state, dict) else None
        item = aggregates.get(event.aggregate_id) if isinstance(aggregates, dict) else None
        expected = {
            "aggregateVersion": event.aggregate_version,
            "state": json.loads(event.aggregate_state_json),
        }
        if item != expected:
            raise ValueError(
                f"event aggregate snapshot does not match deterministic replay: {event.aggregate_id}"
            )
        return next_state

    return replay_events(
        initial_state_json, events, starting_sequence=starting_sequence,
        reducer=checked_reducer, account_scope_id=account_scope_id,
    )


def _validate_checkpoint_prefix(
    checkpoint: Checkpoint,
    prefix_events: tuple[EventRecord, ...],
    reducer: Reducer,
) -> dict:
    if len(prefix_events) != checkpoint.covered_event_sequence:
        raise RecoveryValidationError("checkpoint boundary is not backed by a complete event prefix")
    versions = _aggregate_versions(prefix_events)
    try:
        declared_versions = json.loads(checkpoint.aggregate_versions_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RecoveryValidationError("checkpoint aggregate versions are unreadable") from exc
    if declared_versions != versions:
        raise RecoveryValidationError("checkpoint aggregate versions do not match committed event prefix")
    try:
        replayed_prefix = _replay_with_snapshot_validation(
            canonical_json({"aggregates": {}}),
            prefix_events,
            starting_sequence=0,
            reducer=reducer,
            account_scope_id=checkpoint.account_scope_id,
        )
    except ReplayValidationError as exc:
        raise RecoveryValidationError("checkpoint prefix cannot be deterministically replayed") from exc
    if replayed_prefix.state_json != checkpoint.payload_json:
        raise RecoveryValidationError("checkpoint payload does not reconcile with its event prefix")
    return versions


def recover_repository_state(
    repository,
    account_scope_id: str,
    reducer: Reducer,
) -> RecoveryResult:
    """Recover without writing: verify checkpoint, replay tail, reconcile live aggregates.

    The repository must provide read_active_checkpoint(), read_events(), and
    read_aggregate(). The reducer must be deterministic and side-effect free.
    """
    if not isinstance(account_scope_id, str) or not account_scope_id.strip():
        raise RecoveryValidationError("account_scope_id must be a non-empty string")
    if not callable(reducer):
        raise RecoveryValidationError("reducer must be callable")

    try:
        checkpoint = repository.read_active_checkpoint(account_scope_id)
        events = tuple(repository.read_events(account_scope_id, after_sequence=0))
    except CheckpointIntegrityError as exc:
        raise RecoveryValidationError("active checkpoint integrity validation failed") from exc
    except Exception as exc:
        raise RecoveryValidationError("persisted recovery inputs are unavailable") from exc

    all_versions = _aggregate_versions(events)
    checkpoint_id = None
    if checkpoint is None:
        initial_state = canonical_json({"aggregates": {}})
        starting_sequence = 0
        tail = events
    else:
        if not isinstance(checkpoint, Checkpoint) or checkpoint.account_scope_id != account_scope_id:
            raise RecoveryValidationError("active checkpoint belongs to another account scope")
        boundary = checkpoint.covered_event_sequence
        if boundary > len(events):
            raise RecoveryValidationError("checkpoint covers an uncommitted event sequence")
        prefix = events[:boundary]
        _validate_checkpoint_prefix(checkpoint, prefix, reducer)
        initial_state = checkpoint.payload_json
        starting_sequence = boundary
        tail = events[boundary:]
        checkpoint_id = checkpoint.checkpoint_id

    try:
        result = _replay_with_snapshot_validation(
            initial_state, tail, starting_sequence=starting_sequence,
            reducer=reducer, account_scope_id=account_scope_id,
        )
    except ReplayValidationError as exc:
        raise RecoveryValidationError("committed event tail cannot be replayed") from exc

    if result.last_event_sequence != len(events):
        raise RecoveryValidationError("replay result does not reach the committed event head")

    try:
        state = json.loads(result.state_json)
        aggregates = state["aggregates"]
        if not isinstance(aggregates, dict):
            raise TypeError("aggregates must be an object")
        if set(aggregates) != set(all_versions):
            raise ValueError("replayed aggregate set differs from committed event history")
        for aggregate_id, version in all_versions.items():
            item = aggregates[aggregate_id]
            if not isinstance(item, dict) or item.get("aggregateVersion") != version:
                raise ValueError(f"replayed aggregate version mismatch: {aggregate_id}")
            aggregate_state = item.get("state")
            if not isinstance(aggregate_state, dict):
                raise ValueError(f"replayed aggregate state is missing: {aggregate_id}")
            persisted = repository.read_aggregate(account_scope_id, aggregate_id)
            if persisted is None:
                raise ValueError(f"materialized aggregate is missing: {aggregate_id}")
            if persisted.aggregate_version != version:
                raise ValueError(f"materialized aggregate version mismatch: {aggregate_id}")
            if persisted.state_json != canonical_json(aggregate_state):
                raise ValueError(f"materialized aggregate state mismatch: {aggregate_id}")
    except (KeyError, TypeError, ValueError) as exc:
        raise RecoveryValidationError("replayed state does not reconcile with materialized aggregates") from exc

    return RecoveryResult(
        state_json=result.state_json,
        last_event_sequence=result.last_event_sequence,
        replayed_event_count=result.event_count,
        checkpoint_id=checkpoint_id,
        aggregate_versions_json=canonical_json(all_versions),
    )


__all__ = ["RecoveryResult", "RecoveryValidationError", "recover_repository_state"]
