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
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `scripts/zigux/check-phase6-hexdump-packet.py`
- `lib/hexdump.zig` now also carries direct same-file coverage for the landed `hexToBin`/`hex_to_bin`, `hex2Bin`/`hex2bin`, and `bin2Hex`/`bin2hex` helper parity surface, including mixed-case decode, malformed-input rejection, and lowercase re-encode checks
- the non-truncating helper path now uses a direct full-buffer formatter so the grouped ASCII perf replays do not pay the truncating writer's per-byte bounds checks
- a dedicated hexdump-only build step now reruns the focused helper replay while the helper-local perf gate keeps its threshold matrix preflight beside the ReleaseSafe slowdown replay
- the preserved grouped-ASCII ceiling rationale now stays helper-local through `Documentation/zigux/phase6-hexdump-perf-refresh.md`, so any reopen must keep that note aligned with the same hexdump-owned review packet instead of handing it back to a shared Phase 6 perf lane
- a dedicated Linux-style review route now keeps the helper-local checker, focused replay, perf-matrix preflight, and perf gate under the same `PYTHON` and `ZIG` environment plumbing without widening the shared `phase6` route
- direct local checker route: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-hexdump-review`
- current review posture: focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle; `16B-plain-g1` stays capped at `max_slowdown_pct = 175`, `32B-ascii-g2` and `16B-ascii-g4` stay capped at `max_slowdown_pct = 550`, and `16B-ascii-g8` stays capped at `max_slowdown_pct = 600`, with `zigux/tests/phase6_hexdump_perf_matrix.zig` exact-checking the documented case labels, lengths, row sizes, group sizes, ascii flags, replay counts, slowdown caps, and buffer-fit guard before `zigux/tests/phase6_hexdump_perf.zig` times expected output and required length for every fixture-backed perf case
- the directly coupled serialized `length_cases` packet in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` now keeps both empty plain and empty ASCII zero-length rows aligned with the focused replay and the helper's landed empty-input contract

## Next Step
Leave this slice parked unless a fresh hexdump packet reread shows drift across the helper-local serialized `length_cases` packet, the focused helper replay, the exact four-case perf packet, or the newly landed same-file hex conversion helpers. If it reopens, rerun `python3 scripts/zigux/check-phase6-hexdump-packet.py` and `make -C zigux phase6-hexdump-test` first, then keep the repair to one same-packet surface only.
