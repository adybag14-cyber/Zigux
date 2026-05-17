# Phase 3 Validator Support Surface

This note records the narrow validator-facing Phase 3 surface that is directly readable on current `master`.

## Current packet
Documentation/zigux/phase3-abi-slice.md
include/linux/zigux.h
include/zigux/dev_t.h
zigux/uapi/dev_t.zig
zigux/uapi/version.zig
zigux/bindings/dev_t.zig
zigux/tests/phase3_dev_t_starter_packet.zig
zigux/tests/phase3_dev_t_starter_packet_build.zig

## Current repo-reality gaps
include/zigux/abi.h
zigux/tests/phase3_export_uapi_layout.zig
scripts/zigux/validate-phase3-export-uapi-survey.py
zigux/kernel/export_shim.zig

## Review boundary
This review boundary stays narrow: it records the directly readable starter header-family packet and sampled broader gaps without widening into the older shared Phase 3 validator packet.

## Shared reminder
Documentation/zigux/phase3-abi-slice.md
Documentation/zigux/phase3-validator-support-surface.md
scripts/zigux/README.md still carries a broader Phase 3 packet summary and should be narrowed in a follow-on truthfulness repair
zigux/tests/README.md still carries a broader Phase 3 packet summary and should be narrowed in a follow-on truthfulness repair
Documentation/zigux/review-checklist.md still carries a broader Phase 3 packet prompt and should be narrowed in a follow-on truthfulness repair
keep the current starter `dev_t` packet explicit here instead of implying the broader exported UAPI and validator routes
future Phase 3 follow-up should land one directly readable validator, replay, or binding slice at a time
