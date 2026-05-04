# Phase 8 Perf-Buffer Poll Slice

This note records the bounded Phase 8 helper-first slice around the pure wait-result and ready-buffer bookkeeping surface inside `perf_buffer__poll(timeout_ms)`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=perf-buffer-poll-helper`
- scope: pure wait-result classification plus ready-buffer bookkeeping only
- product boundary:
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The remaining `perf-buffer-online-cpu-routing` packet is still too large to land honestly in one step because it crosses `/sys` reads, online CPU filtering, perf-event-array updates, epoll-backed registration, and interrupt-routing-sensitive delivery behavior.

The narrower `perf_buffer__poll(timeout_ms)` bookkeeping surface is smaller and safer. Zigux can model normalized negative errno-or-ready-count wait results, ready-buffer counting, first-ready indexing, first-error surfacing, fail-fast ready-buffer processing order, the cumulative processed-record count returned before the first failing ready buffer, and the final return-path choice between a successful ready count and the first processing failure without claiming direct `epoll_wait()` parity or broader timer or clockevent ownership.

## Current helper contract

The helper now keeps these bounded rules explicit:

- timeout requests stay classified as nonblocking, bounded, or indefinite based only on the already-observed `timeout_ms` input
- normalized negative errno-or-ready-count wait results stay compact through explicit `timed_out`, `interrupted`, `ready_events`, and `failed(errno)` variants before buffer bookkeeping starts
- ready-buffer bookkeeping counts ready buffers, remembers the first ready index, and surfaces the first buffer-local error without claiming record decoding
- the ordered `perf_buffer__process_records()` pass can now be summarized separately as successful ready-buffer processing until the first failing ready buffer, plus the cumulative processed-record count returned before that failure, keeping libbpf's fail-fast loop explicit without claiming callback delivery or record decoding parity
- final poll return keeps successful ready counts and first processing failures explicit, so the helper can preserve the observed ready-event count on success or surface the first process-record failure without widening into the broader routing loop
- ready-buffer processing attempts cannot exceed observed ready events, so the helper keeps `epoll_wait()`'s bounded ready-event budget visible before any wider routing work
- non-ready wait observations cannot claim record processing, matching the live loop's timeout, interrupted, and already-failed early returns without widening into broader poll parity claims
- observed wait outcomes stay compact instead of hiding error or ready-state intent inside broader loop behavior
- inconsistent states such as more ready buffers than observed ready events still fail fast
- timed-out, interrupted, and already-failed wait observations now reject impossible post-wait buffer state combinations because the live loop never processes records on those paths

## Non-goals

This helper does not yet claim:

- direct `epoll_wait()` parity
- epoll-backed perf FD registration
- `/sys/devices/system/cpu/online` reads
- cached `libbpf_num_possible_cpus()` behavior
- online CPU filtering
- per-CPU perf-event-array map updates
- direct `perf_buffer__poll(timeout_ms)` timeout parity for the broader routing loop
- callback delivery or record decoding parity inside `perf_buffer__process_records()`
- no standalone timer helper
- no standalone clockevent helper
- interrupt-routing-sensitive perf-buffer delivery behavior

## Gates

The shared review path now fail-closes through the shared Phase 8 validator, the validator-route audit, the dedicated tests-readme alignment checker, the dedicated perf-buffer poll gate checker, and all four built-in self-tests before the focused perf-buffer poll build shard and the shared Phase 8 build replay run, so this slice stays tied to the same validator-first Phase 8 tooling packet as the docs root, tests root, Makefile, workflow, and broader segmented libbpf notes.

1. `python3 scripts/zigux/validate-phase8.py --self-test`
2. `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`
3. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`
4. `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test`
5. `python3 scripts/zigux/validate-phase8.py`
6. `python3 scripts/zigux/check-phase8-validator-flow.py`
7. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`
8. `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
9. `make -C zigux phase8-validate`
10. `make -C zigux phase8-perf-buffer-poll-test`
11. `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
12. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

`scripts/zigux/check-phase8-validator-flow.py` now stays inside that same published wrapper path instead of sitting beside it, and it currently publishes `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=17`.

## Latest committed gate snapshot

- provenance and anchor alignment rechecked against inspected `master` head `897cdd2f62c4428d2a050275a187950e161b66eb`
- the committed `phase8-validate` bundle in `zigux/Makefile` now routes through `validate-phase8.py`, `check-phase8-validator-flow.py`, `check-phase8-tests-readme-alignment.py`, and `check-phase8-perf-buffer-poll-gate.py` in both self-test and live modes before the focused and shared replay steps
- `scripts/zigux/check-phase8-tests-readme-alignment.py` currently publishes `PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=45`
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py` currently publishes `PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=8`
- `scripts/zigux/check-phase8-validator-flow.py` currently publishes `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=17` while auditing that the published validator route still names `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `phase8-perf-buffer-poll-test`, and the shared bridge-boundary survey alongside the other landed Phase 8 checker surfaces
- `.github/workflows/zigux-bootstrap.yml` currently keeps a dedicated `Run focused Phase 8 perf-buffer poll tests` step wired to `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md` and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` both keep the dedicated checker plus the focused perf-buffer poll shard explicit inside the same shared Phase 8 tooling packet

## Next bounded step

Keep the helper parked unless the live `perf_buffer__poll()` loop changes shape. The remaining same-family follow-on is still the shared `perf-buffer-online-cpu-routing` boundary, not a wider timer or clockevent claim.
