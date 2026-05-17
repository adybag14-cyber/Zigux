# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet plus two directly readable starter bindings, one directly readable starter export shim companion built on the shared ABI binding surface, one separate focused policy helper slice that reuses the shared ABI bindings, one adjacent notifier binding helper, and one directly readable shared ABI header-and-binding surface with chrdev and notifier layout evidence, rather than the broader shared Phase 3 ABI replay family, so this note stays a repo-reality report instead of a completion claim`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair, two starter UAPI companion files, three directly readable starter bindings, one starter export shim companion, one shared ABI header, one shared ABI binding, one adjacent notifier binding helper, one separate focused policy helper slice built on shared ABI bindings, one starter manifest, and one focused starter replay route, but it still lacks the broader shared Phase 3 ABI replay route, shared tests-root wiring for the policy packet, the broader export/UAPI layout family, and the wider validator packet that earlier shared reminders described`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-17 now reaches the starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, and zigux/tests/phase3_dev_t_starter_packet_manifest.json; it also reaches the shared ABI evidence packet through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py, while representative broader Phase 3 paths still remain absent, including zigux/tests/phase3_abi.zig, zigux/tests/phase3_abi_dump.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3.py, and zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_NEXT_SAFE_STEP=keep Phase 3 narrowed to the next smallest current-master truthfulness or wiring repair that builds on this starter packet, the export shim companion, and the already-landed shared ABI header-and-binding surface without widening into broader bindings, wrapper, or runtime-shim claims`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all`
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/build.zig` is still the next shared tests-root surface to narrow so it stops exposing only the `dev_t` starter packet while the dedicated policy packet already has its own committed replay route
- `zigux/tests/README.md` is still the next shared reminder surface to narrow so it stops parking `include/zigux/abi.h`, `zigux/bindings/abi.zig`, and `zigux/bindings/notifier_abi.zig` as missing routes even though they are directly readable on current `master`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`

## Bounded Starter Packet Present On Master

- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/bindings/abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`

## Shared ABI Header And Binding Evidence Present On Master

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`

## Remaining Sampled Gaps

- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_export_uapi_layout.zig`

## Current Gap

The Phase 3 roadmap still calls for a narrow exported header and starter UAPI boundary. Current `master` now provides that starter header-family packet through one Linux-facing header pair, two small UAPI companions, three starter bindings, one starter export shim companion, one starter manifest, and one focused starter replay route, and it also carries a directly readable shared ABI surface through `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, the helper-local panic, allocator, and unsafe policy decoders, a machine-readable policy manifest, and a dedicated checker route. That shared ABI surface already exposes `zigux_boundary_header`, `zigux_export_status`, `zigux_interop_policy`, the current chrdev notify-ack window structs, and the notifier block layout plus nonincreasing-priority helper on `master`.

That means the immediate requirement in this lane is to keep the directly readable starter packet, its export shim companion, and the adjacent shared ABI surface honest and reviewable without conflating them with Phase 3 completion. Reviewers can now inspect a real starter packet, a machine-readable manifest, bounded checker routes, a direct Zig compile replay, three starter bindings, one starter export shim companion, a shared ABI header-and-binding surface, an adjacent notifier helper shard, and a separate policy helper slice on `master`, but the lane still must not imply that the wider Phase 3 binding family, export/UAPI layout packet, shared tests-root replay, or shared validator routes already ship.

Broader ABI and runtime progress should therefore keep landing one real current-master slice at a time. Do not treat this starter header-family packet, starter manifest, checker-route pair, direct compile replay, starter bindings, export shim companion, shared ABI header-and-binding surface, adjacent notifier helper shard, and separate policy helper slice as Phase 3 completion, and do not widen it into a larger UAPI family, broader bindings packet, low-level-wrapper claim, or runtime shim claim until the corresponding files are directly readable on `master`.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records the directly readable starter header-family packet, the starter bindings, the starter export shim companion, the directly readable shared ABI header-and-binding surface, the adjacent notifier helper shard, the separate focused policy slice, the machine-readable starter and policy manifests, the starter checker routes, and the direct Zig compile replay route, names a sampled set of broader Phase 3 gaps that remain absent on current `master`, and preserves a narrow next-step recommendation. It does not claim that the broader Phase 3 export/UAPI replay files, validator routes, low-level-wrapper surfaces, or runtime shims already ship on current `master`.
