# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet plus two directly readable starter bindings, one directly readable starter export shim companion built on the shared ABI binding surface, one separate focused policy helper slice that reuses the shared ABI bindings, one adjacent notifier binding helper, one directly readable shared ABI header-and-binding surface with chrdev and notifier layout evidence, and one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, one directly readable barrier helper companion, the shared unsafe-scope decoder, and the dedicated survey validator, rather than the broader shared Phase 3 ABI replay family or a complete low-level-wrapper verification packet, so this note stays a repo-reality report instead of a completion claim`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair, two starter UAPI companion files, three directly readable starter bindings, one starter export shim companion, one shared ABI header, one shared ABI binding, one adjacent notifier binding helper, one separate focused policy helper slice built on shared ABI bindings, one starter manifest, one focused starter replay route, and one adjacent low-level-wrapper reminder surface built around zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, but it still lacks the broader shared Phase 3 ABI replay route, shared tests-root wiring for the policy packet, the remaining MMIO helper follow-through, the focused low-level-wrapper replay route, the broader export/UAPI layout family, and the wider shared validator packet that earlier shared reminders described`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-17 now reaches the starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, and zigux/tests/phase3_dev_t_starter_packet_manifest.json; it also reaches the shared ABI evidence packet through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while representative broader Phase 3 paths still remain absent, including zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/phase3_abi.zig, zigux/tests/phase3_abi_dump.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3.py, and zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_NEXT_SAFE_STEP=keep Phase 3 narrowed to the next smallest current-master truthfulness or wiring repair that builds on this starter packet, the export shim companion, the already-landed shared ABI header-and-binding surface, and the partial low-level-wrapper reminder surface without widening into broader bindings, runtime-shim claims, or a premature full low-level-wrapper packet claim`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
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
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
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

## Adjacent Low-Level Wrapper Reminder Surface Present On Master

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

## Sampled Low-Level Wrapper Gaps Still Absent On Current `master`

- `zigux/helpers/mmio.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`

## Remaining Sampled Gaps

- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_export_uapi_layout.zig`

## Current Gap

The Phase 3 roadmap still calls for a narrow exported header and starter UAPI boundary plus approved low-level wrappers. Current `master` now provides that starter header-family packet through one Linux-facing header pair, two small UAPI companions, three starter bindings, one starter export shim companion, one starter manifest, and one focused starter replay route, and it also carries a directly readable shared ABI surface through `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, the helper-local panic, allocator, and unsafe policy decoders, a machine-readable policy manifest, and a dedicated checker route.

Current `master` also separately exposes only a partial low-level-wrapper reminder surface through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/unsafe/narrow.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`. That means the immediate requirement in this lane is to keep the directly readable starter packet, its export shim companion, the adjacent shared ABI surface, and the partial low-level-wrapper reminder surface honest and reviewable without conflating them with Phase 3 completion or with a shipped MMIO companion, focused replay route, or broader shared validator route.

Reviewers can now inspect a real starter packet, a machine-readable manifest, bounded checker routes, a direct Zig compile replay, three starter bindings, one starter export shim companion, a shared ABI header-and-binding surface, an adjacent notifier helper shard, a separate policy helper slice, one directly readable atomic helper shard, one directly readable barrier helper companion, the shared unsafe-scope decoder, and one dedicated low-level-wrapper survey validator on `master`, but the lane still must not imply that the wider Phase 3 binding family, export/UAPI layout packet, full low-level-wrapper helper trio, focused low-level replay route, shared tests-root replay, or broader shared validator routes already ship.

Broader ABI and runtime progress should therefore keep landing one real current-master slice at a time. Do not treat this starter header-family packet, starter manifest, checker-route pair, direct compile replay, starter bindings, export shim companion, shared ABI header-and-binding surface, adjacent notifier helper shard, separate policy helper slice, and partial low-level-wrapper reminder surface as Phase 3 completion, and do not widen that evidence into a larger UAPI family, broader bindings packet, full low-level-wrapper verification packet, or runtime shim claim until the corresponding files are directly readable on `master`.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records the directly readable starter header-family packet, the starter bindings, the starter export shim companion, the directly readable shared ABI header-and-binding surface, the adjacent notifier helper shard, the separate focused policy slice, the machine-readable starter and policy manifests, the starter checker routes, the direct Zig compile replay route, and the partial low-level-wrapper reminder surface built around `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/unsafe/narrow.zig`, the dedicated survey note, and the dedicated survey validator; names a sampled set of broader Phase 3 gaps that remain absent on current `master`; and preserves a narrow next-step recommendation. It does not claim that the broader Phase 3 export/UAPI replay files, the wider shared validator routes, the full low-level-wrapper helper trio, the focused low-level-wrapper replay and validator packet, or runtime shims already ship on current `master`.
