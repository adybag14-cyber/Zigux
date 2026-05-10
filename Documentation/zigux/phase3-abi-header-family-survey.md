# Phase 3 ABI Header-Family Survey

## Scope

This note records the current bounded Phase 3 review surface around the shared Zigux ABI header family.

Primary anchors:
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `zigux/Makefile`

## Why This Survey Exists

The Phase 3 ABI/runtime lane already ships a dedicated survey checker, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, and the shared validation route already reruns it through `make -C zigux phase3-validate`.

That checker exists to keep the broad review packet honest around one narrow question: when the repo talks about the Zigux ABI header family, the same shared surfaces should keep the Linux-side governance note and the dedicated survey route visible together instead of leaving the boundary implicit.

## Current Shared Review Surface

The current shipped packet is intentionally small:
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `make -C zigux phase3-validate`

The intent is reviewability, not expansion. This survey does not claim a broader allocator, panic, atomic, barrier, MMIO, or runtime-service step.

## Boundaries

Keep this packet narrow:
- centralize ABI assumptions in `include/zigux/abi.h`, `include/linux/zigux.h`, and `zigux/bindings/abi.zig`
- keep the checker focused on shared-surface truthfulness rather than turning it into another full Phase 3 validator
- keep unsafe and runtime policy discussion in their dedicated Phase 3 notes instead of folding them into this header-family survey
- treat docs-root and scripts-root wording drift as the normal follow-through surface unless the header family itself changes

## Validation Route

The dedicated checker should remain visible through:
- `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test`
- `make -C zigux phase3-validate`

## Next Step

Use `Documentation/zigux/phase3-abi-h-boundary-next-step.md` for the next bounded same-lane wording repair when the broad docs-root or tests-root reminders drift away from this survey packet.