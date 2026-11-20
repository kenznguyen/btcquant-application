"""Deterministic event replay helpers; pure functions with no storage or I/O."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable, Iterable

from persistent_state.contracts import Checkpoint, EventRecord, canonical_json


class ReplayValidationError(ValueError):
    """Event tail cannot be safely replayed from the supplied state boundary."""


@dataclass(frozen=True, slots=True)
class ReplayResult:
    state_json: str
    last_event_sequence: int
    event_count: int


Reducer = Callable[[dict, EventRecord], dict]


def replay_events(
    initial_state_json: str,
    events: Iterable[EventRecord],
    *,
    starting_sequence: int,
    reducer: Reducer,
    account_scope_id: str | None = None,
) -> ReplayResult:
    """Replay a strictly contiguous event tail using a deterministic reducer.

    The caller owns reducer purity. The function validates every event boundary
    and canonicalizes each reducer result before it becomes the next input state.
    """
    if isinstance(starting_sequence, bool) or not isinstance(starting_sequence, int) or starting_sequence < 0:
        raise ReplayValidationError("starting_sequence must be an integer >= 0")
    if not callable(reducer):
        raise ReplayValidationError("reducer must be callable")
    if account_scope_id is not None and (
        not isinstance(account_scope_id, str) or not account_scope_id.strip()
    ):
        raise ReplayValidationError("account_scope_id must be a non-empty string when supplied")
    try:
        state = json.loads(initial_state_json)
        if not isinstance(state, dict) or canonical_json(state) != initial_state_json:
            raise ValueError("initial state must be a canonical JSON object")
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ReplayValidationError("initial state must be valid canonical JSON") from exc

    last_sequence = starting_sequence
    seen_event_ids: set[str] = set()
    event_count = 0
    for event in events:
        if not isinstance(event, EventRecord):
            raise ReplayValidationError("event tail must contain EventRecord values")
        if account_scope_id is not None and event.account_scope_id != account_scope_id:
            raise ReplayValidationError("event belongs to a different account scope")
        if event.event_sequence != last_sequence + 1:
            raise ReplayValidationError(
                f"event sequence gap or ordering conflict: expected {last_sequence + 1}, "
                f"got {event.event_sequence}"
            )
        if event.event_id in seen_event_ids:
            raise ReplayValidationError("event_id is duplicated in the replay tail")
        seen_event_ids.add(event.event_id)
        try:
            next_state = reducer(state, event)
            next_state_json = canonical_json(next_state)
            # Decode the canonical representation so the next reducer call sees
            # an isolated JSON value, not a mutable object retained by a reducer.
            state = json.loads(next_state_json)
        except Exception as exc:
            raise ReplayValidationError(
                f"reducer failed or returned invalid state at event {event.event_id}"
            ) from exc
        last_sequence = event.event_sequence
        event_count += 1

    return ReplayResult(
        state_json=canonical_json(state),
        last_event_sequence=last_sequence,
        event_count=event_count,
    )


def replay_from_checkpoint(
    checkpoint: Checkpoint,
    events: Iterable[EventRecord],
    *,
    reducer: Reducer,
) -> ReplayResult:
    """Replay committed events strictly after a validated checkpoint boundary."""
    if not isinstance(checkpoint, Checkpoint):
        raise ReplayValidationError("checkpoint must be a validated Checkpoint")
    return replay_events(
        checkpoint.payload_json,
        events,
        starting_sequence=checkpoint.covered_event_sequence,
        reducer=reducer,
        account_scope_id=checkpoint.account_scope_id,
    )


__all__ = [
    "Reducer", "ReplayResult", "ReplayValidationError",
    "replay_events", "replay_from_checkpoint",
]
