# Phase 3 bitmap/cpumask Slice

This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.

## Current Slice

- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

## Bounded Contract

- `bitmap_view.zig` keeps pointer-sized bitmap word access, set-bit counting, first-set discovery, and first-clear discovery explicit inside a declared bit range.
- `cpumask_view.zig` layers cpu membership, population count, first-present discovery, first-missing discovery, subset checks, and overlap checks on top of that bounded bitmap view.
- `phase3_bitmap_cpumask_starter_packet.zig` proves that both helpers stay inside the declared capacity and do not let padding bits in trailing words distort the shared-helper answer surface.

## Replay Route

- `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

## Scope

This slice is intentionally helper-local. It does not yet claim C parity fixtures, exported ABI structs, scheduler-affinity semantics, or wider kernel cpumask traversal behavior.
