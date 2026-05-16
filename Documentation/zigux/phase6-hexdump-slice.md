# Phase 6 Hexdump Slice

## Status
- `PHASE6_STATUS=parked_reviewable`
- `PHASE6_SLICE=hexdump-leaf-helper`
- helper anchor: `lib/hexdump.zig`

## Review Surface
- `lib/hexdump.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/phase6_hexdump_perf_matrix.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `scripts/zigux/check-phase6-hexdump-packet.py`
- `zigux/tests/phase6_build.zig`
- `lib/hexdump.zig` now also carries direct same-file coverage for the landed `hexToBin`/`hex_to_bin`, `hex2Bin`/`hex2bin`, and `bin2Hex`/`bin2hex` helper parity surface
- `lib/hexdump.zig` now also carries direct same-file coverage for the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, and `hexDumpLineLength` helper parity surface, including lowercase and uppercase nibble helpers, destination-too-small rejection, required-length aliasing, and grouped `g8` ASCII formatting coverage
- the directly coupled serialized `length_cases` packet in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` now keeps both the empty plain and empty ASCII zero-length rows aligned with the focused replay and the helper's landed empty-input contract
- focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable
- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`
- direct local packet checker route: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-hexdump-review`

## Next Step
Keep this slice parked unless a concrete new helper-local parity, fixture, or perf-threshold gap appears in the hexdump packet.
