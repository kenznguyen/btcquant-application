"""Deterministic lifecycle tests for T0 feeder scheduling, retry and runtime.

All collaborators are fakes; tests do not start the production composition,
open a canonical database, or access an exchange/network service.
"""
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from market_data.feeder import (
    FeederConfig,
    FeederRuntime,
    FeederScheduler,
    RetryPolicy,
    SchedulerExecutionError,
)
from market_data.store import INTERVAL_MS

BASE = 1_800_000_000_000
M15 = INTERVAL_MS["15m"]
H1 = INTERVAL_MS["1h"]


def complete_coverage(start_ms, end_ms, gaps=()):
    gaps = list(gaps)
    return {
        "startMs": start_ms,
        "endMs": end_ms,
        "coverage": {"complete": not gaps, "gaps": gaps},
    }


class RetryPolicyLifecycleTest(unittest.TestCase):
    def test_retries_transient_errors_with_deterministic_exponential_backoff(self):
        operation = Mock(side_effect=[TimeoutError("first"), ConnectionError("second"), "ok"])
        delays = []
        policy = RetryPolicy(
            max_attempts=3,
            base_delay_seconds=1,
            max_delay_seconds=10,
            jitter_ratio=0,
            random_fn=lambda: 0.5,
            sleep=delays.append,
        )

        self.assertEqual(policy.execute(operation), "ok")
        self.assertEqual(operation.call_count, 3)
        self.assertEqual(delays, [1.0, 2.0])

    def test_does_not_retry_non_transient_errors(self):
        operation = Mock(side_effect=ValueError("invalid response"))
        sleep = Mock()
        policy = RetryPolicy(sleep=sleep)

        with self.assertRaisesRegex(ValueError, "invalid response"):
            policy.execute(operation)

        operation.assert_called_once_with()
        sleep.assert_not_called()

    def test_honors_retry_after_header_above_local_delay_cap(self):
        error = RuntimeError("rate limited")
        error.status_code = 429
        error.headers = {"Retry-After": "9"}
        delays = []
        policy = RetryPolicy(
            max_attempts=2,
            base_delay_seconds=1,
            max_delay_seconds=2,
            jitter_ratio=0,
            random_fn=lambda: 0.5,
            sleep=delays.append,
        )
        operation = Mock(side_effect=[error, "ok"])

        self.assertEqual(policy.execute(operation), "ok")
        self.assertEqual(delays, [9.0])

    def test_stops_after_max_attempts_and_raises_last_error(self):
        operation = Mock(side_effect=TimeoutError("still unavailable"))
        sleep = Mock()
        policy = RetryPolicy(max_attempts=2, sleep=sleep, jitter_ratio=0)

        with self.assertRaisesRegex(TimeoutError, "still unavailable"):
            policy.execute(operation)

        self.assertEqual(operation.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_rejects_malformed_retry_after_without_another_attempt(self):
        error = RuntimeError("rate limited")
        error.status_code = 429
        error.headers = {"Retry-After": "not-a-number"}
        operation = Mock(side_effect=error)
        sleep = Mock()
        policy = RetryPolicy(sleep=sleep)

        with self.assertRaisesRegex(ValueError, "Retry-After"):
            policy.execute(operation)

        operation.assert_called_once_with()
        sleep.assert_not_called()


class FeederSchedulerLifecycleTest(unittest.TestCase):
    def make_scheduler(self, *, now_ms, timeframes=("15m",), sync=None, coverage=None):
        sync = sync if sync is not None else Mock(return_value="synced")
        coverage = coverage if coverage is not None else (
            lambda frame, start, end: complete_coverage(start, end)
        )
        config = FeederConfig(
            close_grace_seconds=5,
            timeframes=timeframes,
        )
        clock_value = [BASE]
        scheduler = FeederScheduler(
            config=config,
            clock=lambda: clock_value[0],
            sync_callback=sync,
            coverage_reader=coverage,
        )
        clock_value[0] = now_ms
        return scheduler

    def test_close_grace_excludes_candle_until_boundary_is_reached(self):
        before_grace = BASE + M15 + 4_999
        scheduler = self.make_scheduler(now_ms=before_grace)
        self.assertEqual(scheduler.due_timeframes(), ())

        at_boundary = self.make_scheduler(now_ms=BASE + M15 + 5_000)
        self.assertEqual(at_boundary.due_timeframes(), ("15m",))

    def test_m15_and_h1_watermarks_advance_independently(self):
        sync = Mock(return_value="m15")
        scheduler = self.make_scheduler(
            now_ms=BASE + M15 + 5_000,
            timeframes=("15m", "1h"),
            sync=sync,
        )

        result = scheduler.run_due()

        self.assertEqual(result, {"15m": "m15"})
        self.assertEqual(sync.call_count, 1)
        self.assertEqual(sync.call_args.args, ("15m", BASE, BASE + M15))
        self.assertEqual(scheduler.last_completed_end_ms["15m"], BASE + M15)
        self.assertEqual(scheduler.last_completed_end_ms["1h"], BASE)

    def test_sync_failure_preserves_watermark_and_clears_running_state(self):
        sync = Mock(side_effect=TimeoutError("sync failed"))
        scheduler = self.make_scheduler(
            now_ms=BASE + M15 + 5_000,
            sync=sync,
        )

        with self.assertRaises(SchedulerExecutionError) as raised:
            scheduler.run_due()

        self.assertIn("15m", raised.exception.failures)
        self.assertEqual(scheduler.last_completed_end_ms["15m"], BASE)
        self.assertEqual(scheduler.running_timeframes, frozenset())

    def test_remaining_coverage_gap_prevents_watermark_advance(self):
        def with_gap(frame, start, end):
            return complete_coverage(
                start, end, [{"startMs": start, "endMs": end}]
            )

        scheduler = self.make_scheduler(
            now_ms=BASE + M15 + 5_000,
            coverage=with_gap,
        )

        with self.assertRaises(SchedulerExecutionError):
            scheduler.run_due()

        self.assertEqual(scheduler.last_completed_end_ms["15m"], BASE)

    def test_successful_timeframe_remains_committed_when_another_fails(self):
        def sync(frame, start, end):
            if frame == "1h":
                raise TimeoutError("H1 unavailable")
            return frame

        scheduler = self.make_scheduler(
            now_ms=BASE + H1 + 5_000,
            timeframes=("15m", "1h"),
            sync=sync,
        )

        with self.assertRaises(SchedulerExecutionError) as raised:
            scheduler.run_due()

        self.assertEqual(raised.exception.completed, {"15m": "15m"})
        self.assertIn("1h", raised.exception.failures)
        self.assertEqual(
            scheduler.last_completed_end_ms["15m"], BASE + H1
        )
        self.assertEqual(scheduler.last_completed_end_ms["1h"], BASE)

    def test_running_timeframe_is_not_admitted_twice(self):
        scheduler = self.make_scheduler(now_ms=BASE + M15 + 5_000)
        self.assertTrue(scheduler.mark_running("15m"))
        self.assertFalse(scheduler.mark_running("15m"))
        self.assertEqual(scheduler.due_timeframes(), ())

    def test_stop_rejects_new_work(self):
        sync = Mock()
        scheduler = self.make_scheduler(
            now_ms=BASE + M15 + 5_000,
            sync=sync,
        )

        scheduler.stop()

        self.assertEqual(scheduler.run_due(), {})
        sync.assert_not_called()
        self.assertFalse(scheduler.mark_running("15m"))

    def test_wait_for_idle_reports_active_work_then_completes(self):
        scheduler = self.make_scheduler(now_ms=BASE)
        self.assertTrue(scheduler.mark_running("15m"))
        self.assertFalse(scheduler.wait_for_idle(timeout=0))
        scheduler.mark_failed("15m")
        self.assertTrue(scheduler.wait_for_idle(timeout=0))


class FakeScheduler:
    def __init__(self, order=None, idle_results=None, sync_callback=None):
        self.order = order if order is not None else []
        self.idle_results = list(idle_results or [])
        self.sync_callback = sync_callback
        self.started = False
        self.stopped = False
        self.run_count = 0

    def start(self):
        self.order.append("scheduler_start")
        self.started = True

    def stop(self):
        self.order.append("scheduler_stop")
        self.stopped = True

    def wait_for_idle(self, timeout=None):
        self.order.append("scheduler_drain")
        if self.idle_results:
            return self.idle_results.pop(0)
        return True

    def run_due(self):
        self.run_count += 1
        return {"15m": "done"}


class FakeLeaseStore:
    def __init__(self, order=None, *, available=True, current=True,
                 heartbeat_result=True, authorize_results=None):
        self.order = order if order is not None else []
        self.available = available
        self.current = current
        self.heartbeat_result = heartbeat_result
        self.authorize_results = list(authorize_results or [])
        self.releases = []
        self.heartbeat_calls = 0

    def acquire(self, owner, now_ms=None, ttl_seconds=60):
        self.order.append("lease_acquire")
        return SimpleNamespace(generation=7) if self.available else None

    def release(self, owner, generation):
        self.order.append("lease_release")
        self.releases.append((owner, generation))
        return True

    def is_current(self, owner, generation, now_ms=None):
        return self.current

    def authorize_write(self, owner, generation, now_ms=None):
        if self.authorize_results:
            return self.authorize_results.pop(0)
        return self.current

    def heartbeat(self, owner, generation, now_ms=None, ttl_seconds=60):
        self.heartbeat_calls += 1
        return self.heartbeat_result


class FakeRecovery:
    def __init__(self, order=None, result=True, error=None):
        self.order = order if order is not None else []
        self.result = result
        self.error = error

    def recover_all(self):
        self.order.append("recovery")
        if self.error is not None:
            raise self.error
        return self.result


class FakeWalKeeper:
    def __init__(self, order=None):
        self.order = order if order is not None else []
        self.opened = False
        self.closed = False

    def open(self):
        self.order.append("wal_open")
        self.opened = True

    def close(self):
        self.order.append("wal_close")
        self.closed = True


class FeederRuntimeLifecycleTest(unittest.TestCase):
    def make_runtime(self, *, scheduler=None, lease_store=None, recovery=None,
                    wal_keeper=None, event_sink=None, retry_policy=None):
        config = FeederConfig(lease_heartbeat_seconds=1)
        scheduler = scheduler if scheduler is not None else FakeScheduler()
        lease_store = lease_store if lease_store is not None else FakeLeaseStore()
        return FeederRuntime(
            config=config,
            scheduler=scheduler,
            lease_store=lease_store,
            owner_id="test-owner",
            recovery=recovery,
            wal_keeper=wal_keeper,
            event_sink=event_sink,
            clock=lambda: BASE,
            retry_policy=retry_policy,
        )

    def test_lease_unavailable_fails_closed_without_recovery_or_scheduler_start(self):
        scheduler = FakeScheduler()
        recovery = FakeRecovery()
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=FakeLeaseStore(available=False),
            recovery=recovery,
        )

        self.assertFalse(runtime.start())
        self.assertEqual(runtime.state, "FAILED")
        self.assertFalse(scheduler.started)
        self.assertEqual(recovery.order, [])

    def test_incomplete_recovery_releases_owned_lease_and_closes_wal(self):
        order = []
        scheduler = FakeScheduler(order)
        leases = FakeLeaseStore(order)
        wal = FakeWalKeeper(order)
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=leases,
            recovery=FakeRecovery(order, result=False),
            wal_keeper=wal,
        )

        self.assertFalse(runtime.start())
        self.assertEqual(runtime.state, "FAILED")
        self.assertEqual(leases.releases, [("test-owner", 7)])
        self.assertFalse(scheduler.started)
        self.assertTrue(wal.closed)
        self.assertLess(order.index("lease_release"), order.index("wal_close"))

    def test_successful_start_runs_recovery_before_scheduler_and_becomes_running(self):
        order = []
        scheduler = FakeScheduler(order)
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=FakeLeaseStore(order),
            recovery=FakeRecovery(order),
        )

        self.assertTrue(runtime.start())
        self.assertEqual(runtime.state, "RUNNING")
        self.assertLess(order.index("recovery"), order.index("scheduler_start"))
        self.assertEqual(runtime.health_snapshot({})["startup_complete"], True)
        self.assertTrue(runtime.stop(timeout=2))

    def test_scheduler_start_exception_releases_lease_and_cleans_wal(self):
        order = []

        class BrokenScheduler(FakeScheduler):
            def start(self):
                order.append("scheduler_start")
                raise RuntimeError("scheduler failed to start")

        scheduler = BrokenScheduler(order)
        leases = FakeLeaseStore(order)
        wal = FakeWalKeeper(order)
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=leases,
            recovery=FakeRecovery(order),
            wal_keeper=wal,
        )

        with self.assertRaisesRegex(RuntimeError, "scheduler failed"):
            runtime.start()

        self.assertEqual(runtime.state, "FAILED")
        self.assertEqual(leases.releases, [("test-owner", 7)])
        self.assertTrue(wal.closed)

    def test_run_once_checks_lease_before_admitting_scheduler_work(self):
        scheduler = FakeScheduler()
        leases = FakeLeaseStore(current=False)
        runtime = self.make_runtime(scheduler=scheduler, lease_store=leases)
        self.assertTrue(runtime.start())

        self.assertEqual(runtime.run_once(), {})
        self.assertEqual(runtime.state, "LEASE_LOST")
        self.assertTrue(scheduler.stopped)
        self.assertEqual(scheduler.run_count, 0)
        self.assertTrue(runtime.stop(timeout=2))
        self.assertEqual(leases.releases, [])

    def test_run_once_executes_only_while_lease_is_current(self):
        scheduler = FakeScheduler()
        runtime = self.make_runtime(scheduler=scheduler)
        self.assertTrue(runtime.start())

        self.assertEqual(runtime.run_once(), {"15m": "done"})
        self.assertEqual(scheduler.run_count, 1)
        self.assertTrue(runtime.stop(timeout=2))

    def test_heartbeat_failure_marks_lease_lost_and_stops_scheduler(self):
        lost = threading.Event()
        scheduler = FakeScheduler()
        leases = FakeLeaseStore(heartbeat_result=False)
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=leases,
            event_sink=lambda event: lost.set() if event == "lease_lost" else None,
        )
        self.assertTrue(runtime.start())

        self.assertTrue(lost.wait(timeout=3))
        self.assertEqual(runtime.state, "LEASE_LOST")
        self.assertTrue(scheduler.stopped)
        self.assertTrue(runtime.stop(timeout=2))
        self.assertEqual(leases.releases, [])

    def test_shutdown_drains_before_releasing_lease_and_closing_wal(self):
        order = []
        scheduler = FakeScheduler(order)
        leases = FakeLeaseStore(order)
        wal = FakeWalKeeper(order)
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=leases,
            wal_keeper=wal,
        )
        self.assertTrue(runtime.start())

        self.assertTrue(runtime.stop(timeout=2))

        self.assertEqual(runtime.state, "STOPPED")
        self.assertLess(order.index("scheduler_drain"), order.index("lease_release"))
        self.assertLess(order.index("lease_release"), order.index("wal_close"))

    def test_drain_timeout_retains_lease_and_wal_until_a_later_successful_drain(self):
        order = []
        scheduler = FakeScheduler(order, idle_results=[False, True])
        leases = FakeLeaseStore(order)
        wal = FakeWalKeeper(order)
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=leases,
            wal_keeper=wal,
        )
        self.assertTrue(runtime.start())

        with self.assertRaises(TimeoutError):
            runtime.stop(timeout=2)

        self.assertEqual(runtime.state, "STOPPING")
        self.assertEqual(leases.releases, [])
        self.assertFalse(wal.closed)

        self.assertTrue(runtime.stop(timeout=2))
        self.assertEqual(leases.releases, [("test-owner", 7)])
        self.assertTrue(wal.closed)

    def test_lease_loss_never_releases_a_replacement_generation(self):
        leases = FakeLeaseStore()
        runtime = self.make_runtime(lease_store=leases)
        self.assertTrue(runtime.start())

        runtime.on_lease_lost()
        self.assertTrue(runtime.stop(timeout=2))

        self.assertEqual(runtime.state, "STOPPED")
        self.assertEqual(leases.releases, [])

    def test_retry_wrapper_rechecks_write_authorization_before_each_attempt(self):
        original_sync = Mock(side_effect=TimeoutError("first attempt"))
        scheduler = FakeScheduler(sync_callback=original_sync)
        leases = FakeLeaseStore(authorize_results=[True, False])
        retry = RetryPolicy(
            max_attempts=2,
            jitter_ratio=0,
            random_fn=lambda: 0.5,
            sleep=lambda delay: None,
        )
        runtime = self.make_runtime(
            scheduler=scheduler,
            lease_store=leases,
            retry_policy=retry,
        )
        self.assertTrue(runtime.start())

        with self.assertRaisesRegex(PermissionError, "lease is not current"):
            scheduler.sync_callback("15m", BASE, BASE + M15)

        self.assertEqual(original_sync.call_count, 1)
        self.assertEqual(runtime.state, "LEASE_LOST")
        self.assertTrue(runtime.stop(timeout=2))


if __name__ == "__main__":
    unittest.main()
