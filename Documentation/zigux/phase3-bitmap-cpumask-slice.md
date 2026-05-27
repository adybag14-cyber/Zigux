# Phase 3 bitmap/cpumask Slice

This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.
On current `master`, that formerly missing slice is now present as a helper-local starter packet plus a narrow C parity fixture pair, so the honest remaining interop gap against the roadmap's `lib/bitmap.c` and `lib/cpumask.c` anchors is wider exported or scheduler-facing behavior rather than helper absence.

## Current Slice

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`

## Bounded Contract

- `bitmap_view.zig` keeps pointer-sized bitmap word access, set-bit counting, first-set discovery, first-clear discovery, and bounded next-bit traversal explicit inside a declared bit range.
- `cpumask_view.zig` layers cpu membership, population count, first-present discovery, first-missing discovery, bounded next-cpu traversal, subset checks, and overlap checks on top of that bounded bitmap view.
- `phase3_bitmap_cpumask_starter_packet.zig` proves that both helpers stay inside the declared capacity, do not let padding bits in trailing words distort the shared-helper answer surface, and can advance to the next eligible CPU without wandering outside the bounded mask.
- `phase3_bitmap_cpumask_c_harness.c` mirrors the same bounded helper-local cases in C so the fixture stays anchored to Linux-shaped word and mask semantics without widening into exported ABI or scheduler policy.
- `expected.json` keeps the narrow parity answers directly readable for the starter packet and the C harness.
- `phase3_bitmap_cpumask_manifest.json` keeps the current helper-local packet inventory and replay routes explicit without pretending that broader exported or affinity-facing behavior has already landed.
- `check-phase3-bitmap-cpumask.py` fail-closes the doc, helper, test, C fixture, expected fixture, and manifest packet so future runs can detect drift without widening beyond helper-local bitmap and cpumask semantics.

## Replay Routes

- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py --repo-root . --cc gcc`
- `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

## Scope

This slice is intentionally helper-local. It does not yet claim exported ABI structs, scheduler-affinity policy, or full kernel cpumask traversal parity beyond bounded next-cpu helper walking.
