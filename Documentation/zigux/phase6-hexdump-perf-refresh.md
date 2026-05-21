# Phase 6 Hexdump Perf Refresh Evidence

* owner lane: `P6-Y09`
* packet anchor: `Documentation/zigux/phase6-hexdump-slice.md` plus `scripts/zigux/check-phase6-hexdump-packet.py`
* current perf sources: `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile`

## Threshold Packet

- `16B-plain`: `max_slowdown_pct = 175` remains the narrow plain formatter ceiling for the direct one-byte grouping case.
- `32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`.
- `16B-ascii-g4`: the grouped ASCII formatter replay keeps the four-byte grouping ceiling at `max_slowdown_pct = 550`.
- `16B-ascii-g8`: the widest grouped ASCII formatter case keeps `max_slowdown_pct = 600`.

## Why The Ceilings Differ

The plain formatter path only serializes hex bytes, while the grouped ASCII packet also pays for native-endian chunk formatting, alignment padding out to the ASCII column, and printable-character projection. This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case.

`zigux/tests/phase6_helper_parity_manifest.json` records the same helper-local hexdump replay and threshold cases, so the shared Phase 6 parity packet can point at one current rationale note instead of leaving the grouped formatter thresholds implicit.

## Replay Routes

- `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `python3 scripts/zigux/check-phase6-hexdump-route.py`
- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-review`
- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-perf-matrix-test`
- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- `make -C zigux phase6-hexdump-perf`
