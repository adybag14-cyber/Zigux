# Phase 6 Hexdump Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=hexdump-leaf-helper`
- helper anchor: `lib/hexdump.zig`

## Review Surface
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/phase6_hexdump_perf_matrix.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `scripts/zigux/check-phase6-hexdump-packet.py`
- the non-truncating helper path now uses a direct full-buffer formatter so the grouped ASCII perf replays do not pay the truncating writer's per-byte bounds checks
- a dedicated hexdump-only build step now reruns the focused helper replay while the helper-local perf gate keeps its threshold matrix preflight beside the ReleaseSafe slowdown replay
- a dedicated Linux-style review route now keeps the helper-local checker, focused replay, perf-matrix preflight, and perf gate under the same `PYTHON` and `ZIG` environment plumbing without widening the shared `phase6` route
- direct local checker route: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-hexdump-review`
- current review posture: focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle; `16B-plain-g1` stays capped at `max_slowdown_pct = 175`, `32B-ascii-g2` and `16B-ascii-g4` stay capped at `max_slowdown_pct = 550`, and `16B-ascii-g8` stays capped at `max_slowdown_pct = 600`, with `zigux/tests/phase6_hexdump_perf_matrix.zig` exact-checking the documented case labels, lengths, row sizes, group sizes, ascii flags, replay counts, slowdown caps, and buffer-fit guard before `zigux/tests/phase6_hexdump_perf.zig` times expected output and required length for every fixture-backed perf case
- the live helper already returns zero required length for empty input in both plain and ASCII modes, but the directly coupled serialized `length_cases` packet in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still keeps only the empty-plain row, so the parked helper packet should reopen only to promote that already-landed empty-ASCII zero-length contract into the serialized fixture and the focused replay

## Next Step
Leave this slice parked unless helper formatting semantics, fixture evidence, or the dedicated perf replay drifts on current `master`. If it reopens, keep the follow-through helper-local and bounded: add the missing empty-ASCII zero-length `LengthCase` row to `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, replay that row in `zigux/tests/phase6_hexdump.zig`, and rerun `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig` or `make -C zigux phase6-hexdump-test`.
