# Phase 6 Hexdump Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=hexdump-leaf-helper`
- helper anchor: `lib/hexdump.zig`

## Review Surface
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `scripts/zigux/check-phase6-hexdump-packet.py`
- the non-truncating helper path now uses a direct full-buffer formatter so the grouped ASCII perf replays do not pay the truncating writer's per-byte bounds checks
- a dedicated hexdump-only build step now reruns the focused helper replay without dragging the full shared Phase 6 helper packet along
- a dedicated Linux-style review route now keeps the helper-local checker, focused replay, and perf gate under the same `PYTHON` and `ZIG` environment plumbing without widening the shared `phase6` route
- direct local checker route: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-hexdump-review`
- current review posture: focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle; `16B-plain-g1` stays capped at `max_slowdown_pct = 175`, `32B-ascii-g2` and `16B-ascii-g4` stay capped at `max_slowdown_pct = 550`, and `16B-ascii-g8` stays capped at `max_slowdown_pct = 600`, with `zigux/tests/phase6_hexdump_perf.zig` exact-checking expected output and required length for every fixture-backed perf case before timing

## Next Step
Leave this slice parked unless helper formatting semantics, fixture evidence, or the dedicated perf replay drifts on current `master`.
