# Phase 3 Validator Support Surface

This note records the validator-facing Phase 3 starter packet that current `master` actually ships today.

It stays narrow on purpose: current `master` materially carries one Linux-facing starter header pair, one starter `dev_t` binding, and one focused replay route. The older broader Phase 3 validator, export/UAPI layout, low-level-wrapper, and catalog packet is not treated here as shipped current-tree evidence.

## Current packet

Documentation/zigux/phase3-abi-slice.md
Documentation/zigux/phase3-validator-support-surface.md
Documentation/zigux/review-checklist.md
scripts/zigux/README.md
zigux/tests/README.md
include/linux/zigux.h
include/zigux/dev_t.h
zigux/uapi/version.zig
zigux/uapi/dev_t.zig
zigux/bindings/dev_t.zig
zigux/tests/phase3_dev_t_starter_packet.zig
zigux/tests/phase3_dev_t_starter_packet_build.zig
zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig
starter header-family and `dev_t` companion packet on current `master`
broader Phase 3 validators, export/UAPI layout routes, and low-level-wrapper routes remain repo-reality gaps until the corresponding files are directly readable again

## Review boundary

This review boundary stays narrow: it records the directly readable starter header-family packet and the focused `dev_t` replay route that current `master` actually ships. It does not claim that the broader Phase 3 export/UAPI layout, low-level-wrapper, policy, catalog, or shared `make -C zigux phase3*` routes are currently materialized.

## Shared reminder

Documentation/zigux/phase3-abi-slice.md
Documentation/zigux/review-checklist.md
scripts/zigux/README.md
zigux/tests/README.md
include/linux/zigux.h
include/zigux/dev_t.h
zigux/uapi/version.zig
zigux/uapi/dev_t.zig
zigux/bindings/dev_t.zig
zigux/tests/phase3_dev_t_starter_packet.zig
zigux/tests/phase3_dev_t_starter_packet_build.zig
zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig
starter header-family and `dev_t` companion packet on current `master`
broader Phase 3 validators, export/UAPI layout routes, and low-level-wrapper routes remain repo-reality gaps until the corresponding files are directly readable again
