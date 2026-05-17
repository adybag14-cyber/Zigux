# Phase 3 Validator Support Surface

This note keeps the current validator-facing Phase 3 packet truthful on `master`. Current `master` now carries a bounded starter header-family and `dev_t` packet, not the broader shared ABI and export packet that older reminder surfaces still describe.

## Current direct packet

- `Documentation/zigux/phase3-abi-slice.md`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-linux-zigux-header-governance.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`

## Reminder surfaces that must stay aligned

- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase3-validator-support-surface.md`

## Repo-reality gaps still named by older reminders

- `include/zigux/abi.h`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/kernel/export_shim.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Review boundary

Keep Phase 3 narrowed to the directly readable starter header-family packet and its validator-facing support cues. Treat the broader ABI substrate, export and UAPI layout packet, export shim, and shared Phase 3 convenience routes as repo-reality gaps until those files return on current `master`.

## Current gap

Current `master` does provide a real Linux-facing header pair, two starter UAPI companions, one starter binding, and one focused replay route. That is enough to keep Phase 3 reviewable, but it is not the same thing as the older broad Phase 3 packet.

The validator-facing job in this lane is therefore truthfulness first: keep the direct starter packet explicit, keep the missing broader packet files named as gaps, and avoid implying that `make -C zigux phase3`, `make -C zigux phase3-selftest`, `make -C zigux phase3-validate`, or the export and low-level-wrapper routes are current shipped evidence unless those files are directly readable again on `master`.

## Next safe step

Narrow the remaining broad reminder surfaces in `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` so they match the starter-packet reality already recorded in `Documentation/zigux/phase3-abi-slice.md` and this note.
