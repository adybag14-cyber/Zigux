# Phase 6 Hexdump Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=hexdump-leaf-helper`
- helper anchor: `lib/hexdump.zig`

## Review Surface
- `lib/hexdump.zig`
- `zigux/tests/phase6_build.zig`
- `zigux/tests/phase6_hexdump_perf_matrix.zig`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `scripts/zigux/check-phase6-hexdump-packet.py`
- `zigux/tests/phase6_helper_parity_manifest.json`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `lib/hexdump.zig` now also carries direct same-file coverage for the landed `hexToBin`/`hex_to_bin`, `hex2Bin`/`hex2bin`, and `bin2Hex`/`bin2hex` helper parity surface, including mixed-case decode, malformed-input rejection, and lowercase re-encode checks
- the non-truncating helper path now uses a direct full-buffer formatter so the grouped ASCII perf replays do not pay the truncating writer's per-byte bounds checks
- current `master` still advertises the helper-local replay packet through `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_parity_manifest.json`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `scripts/zigux/check-phase6-hexdump-packet.py`, but the directly owned replay files `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, and `zigux/tests/fixtures/phase6_hexdump_vectors.zig` are absent from current `master`
- a dedicated hexdump-only build step is still wired in `zigux/tests/phase6_build.zig`, but it cannot honestly be treated as runnable committed evidence again until those three directly owned files return
- the preserved grouped-ASCII ceiling rationale now stays helper-local through `Documentation/zigux/phase6-hexdump-perf-refresh.md`, so any reopen must keep that note aligned with the same hexdump-owned review packet instead of handing it back to a shared Phase 6 perf lane
- a dedicated Linux-style review route is still named for the helper-local checker, focused replay, perf-matrix preflight, and perf gate, but that route is currently blocked by the missing replay files rather than by helper semantics or freeze-map policy
- direct local checker route: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-hexdump-review`
- current review posture: blocked; the helper source, perf-refresh note, build wiring, and perf-matrix preflight still show the intended bounded Phase 6 packet, but current `master` cannot honestly claim a runnable helper-local parity or perf gate until `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, and `zigux/tests/fixtures/phase6_hexdump_vectors.zig` are restored
- once the replay packet returns, the next helper-local follow-through can revisit whether the serialized `length_cases` fixture should also grow the still-unserialized empty ASCII zero-length row

## Next Step
Keep this slice blocked until the missing replay packet is restored. The current bounded next safe step is not another perf-note tweak: restore `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, and `zigux/tests/fixtures/phase6_hexdump_vectors.zig` so `scripts/zigux/check-phase6-hexdump-packet.py`, `make -C zigux phase6-hexdump-test`, and `make -C zigux phase6-hexdump-perf` once again point at committed helper-local evidence on `master`. Only after that restore lands should this lane reopen the narrower empty-ASCII length-packet follow-through.