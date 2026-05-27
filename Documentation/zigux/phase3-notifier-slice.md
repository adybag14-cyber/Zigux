# Phase 3 notifier Slice

This note records one bounded Phase 3 notifier starter packet on current `master`.

## Current Slice

- `Documentation/zigux/phase3-notifier-slice.md`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_notifier_starter_packet.zig`
- `zigux/tests/phase3_notifier_starter_packet_build.zig`
- `zigux/tests/phase3_notifier_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-notifier-starter-packet.py`

## Bounded Contract

This packet stays intentionally small:

- `zigux/bindings/notifier_abi.zig` keeps notifier result bytes, priority ordering, list backlink checks, and hlist prev-link checks reviewable without widening into callback execution or ownership transfer.
- `zigux/tests/phase3_notifier_starter_packet.zig` keeps the result constants, layout anchors, bounded priority-chain replay, list backlink drift witness, and hlist prev-link drift witness explicit.
- `zigux/tests/phase3_notifier_starter_packet_build.zig` provides one focused replay route for the starter packet instead of expanding the wider shared tests-root aggregate.
- `zigux/tests/phase3_notifier_starter_packet_manifest.json` and `scripts/zigux/check-phase3-notifier-starter-packet.py` keep the packet fail-closed and reviewable.

## Current Gap

This is still not a full notifier callback runtime port, notifier ownership proof, or broader chain mutation surface. The landed packet only closes the bounded notifier ABI replay slice.

## Scope

This note is limited to one notifier ABI binding surface, one focused starter packet, one focused build file, one manifest, and one checker. It does not claim callback dispatch semantics, notifier registration lifecycle coverage, or broader runtime chain ownership behavior.
