# Phase 3 bitmap/cpumask Slice

This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.
On current `master`, that formerly missing slice is now present as a helper-local starter packet, so the honest remaining interop gap against the roadmap's `lib/bitmap.c` and `lib/cpumask.c` anchors is the still-absent narrow C harness and expected fixture rather than helper absence.

## Current Slice

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`

## Bounded Contract

- `bitmap_view.zig` keeps pointer-sized bitmap word access, set-bit counting, first-set discovery, and first-clear discovery explicit inside a declared bit range.
- `cpumask_view.zig` layers cpu membership, population count, first-present discovery, first-missing discovery, subset checks, and overlap checks on top of that bounded bitmap view.
- `phase3_bitmap_cpumask_starter_packet.zig` proves that both helpers stay inside the declared capacity and do not let padding bits in trailing words distort the shared-helper answer surface.
- `phase3_bitmap_cpumask_manifest.json` keeps the current helper-local packet inventory and replay routes explicit without pretending that broader C parity companions have already landed.
- `check-phase3-bitmap-cpumask.py` fail-closes the doc, helper, test, and manifest packet so future runs can detect drift without widening into scheduler-affinity or exported-ABI claims.

## Replay Routes

- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py`
- `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

## Scope

This slice is intentionally helper-local. It does not yet claim C parity fixtures, exported ABI structs, scheduler-affinity semantics, or wider kernel cpumask traversal behavior.

Current repo-reality gaps remain explicit through:

- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
