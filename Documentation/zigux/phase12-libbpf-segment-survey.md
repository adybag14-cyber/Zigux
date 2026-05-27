# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the earlier `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- `PHASE12_LANE_KEY=P12-L16`
- scope: Phase 12 roadmap comparison, shared survey truthfulness, the parked libbpf verify-shard plus snapshot companions, and the boundary between the still-present direct helper-first segment footing and the still-unadopted shared replay packet
- product boundary:
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this libbpf note is not a commit-pinned raw GitHub fallback artifact
- rollback owner and reversible-delivery drill: restore the last truthful survey wording in this note, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/validate-phase12.py`, and the shipped wrapper `make -C zigux phase12-validate`; then rerun `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12` so the shared Phase 12 release packet stays reviewable without pretending those shared routes already exercise the parked direct `phase12_libbpf_*` replay files directly

## Why this slice exists
The roadmap places `tools/lib/bpf/libbpf.c` in Phase 12 alongside the other high-risk production-facing consumers because the file is both large and semantically dense even though it lives under `tools/`.

That matters because current `master` still exposes a bounded directly readable `zigux_segments` footing through the helper-first core `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `perf_buffer_poll.zig`, and `online_cpu_routing.zig` files plus the directly readable compile-together `verify.zig` shard and its current companion family (`cpu_mask_verify.zig`, `logging_verify.zig`, `online_cpu_routing_mask_bridge.zig`, `online_cpu_routing_mask_bridge_verify.zig`, `online_cpu_routing_verify.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `file_path_handle_bridge_verify.zig`, `pin_path_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_lookup.zig`, `ready_buffer_fd_verify.zig`, `ready_buffer_window_verify.zig`, and `type_names_verify.zig`), while the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` remain parked note-owned boundaries. The readable `tools/lib/bpf/zigux_segments/manifest.json` catalog still helps map that helper-first packet, but it is not by itself proof that the shared replay order adopted those parked direct files. That mixed state preserves real segmented progress while also keeping the broader reviewability packet smaller than the shipped replay order.

Those are still useful footholds, but the live Phase 12 survey has to explain how that earlier helper work fits the heavy-helper roadmap without overstating the current replay packet. The directly readable helper-first footing remains roadmap-relevant, while the broader parked libbpf reviewability packet has to stay described through the survey, verify-shard, anti-overlap notes, the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate, and the snapshot anchor until the shared replay order actually adopts it.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, bridge, queue-routing, object-model, relocation, and verifier-facing concerns in one file.
- current `master` still exposes a bounded directly readable libbpf segment footing under `tools/lib/bpf/zigux_segments/` through the helper-first core `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `perf_buffer_poll.zig`, and `online_cpu_routing.zig` files plus the compile-together `verify.zig` shard and its directly readable companion family `cpu_mask_verify.zig`, `logging_verify.zig`, `online_cpu_routing_mask_bridge.zig`, `online_cpu_routing_mask_bridge_verify.zig`, `online_cpu_routing_verify.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `file_path_handle_bridge_verify.zig`, `pin_path_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_lookup.zig`, `ready_buffer_fd_verify.zig`, `ready_buffer_window_verify.zig`, and `type_names_verify.zig`, while `manifest.json` now remains directly readable as a historical lane map for that helper packet rather than proof of a current shared replay route.
- the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still stay recorded only through the survey, verify-shard, and anti-overlap notes until they land again on current `master`, while the directly readable `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper and the `tools/lib/bpf/zigux_segments/verify.zig` compile-together companion family now sit beside the helper subset without implying shipped smoke-first adoption; `scripts/zigux/check-phase12-libbpf-snapshot.py` now fails closed on both the same four note-owned support anchors recorded in `zigux/tests/fixtures/phase12_libbpf_snapshot.json` (`Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`) and the directly readable `pin_path.zig` shard recorded in `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, while the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate still pins the legacy five-path reviewability packet on current `master`, so the shared survey wording should keep both that direct gate and the helper-local determinism companion explicit without implying that the broader direct `phase12_libbpf_*` replay set has re-landed.
- the shared shipped replay order is still narrower than that mixed direct-plus-parked libbpf packet. Current `zigux/tests/phase12_build.zig` wires only the six-file `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate sextet, and current `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` around that same shared build file while `virtio_scsi` remains a driver-local rollback-lab packet outside the shared route.
- `scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.
- current `master` now also ships the validator-side support bundle through `scripts/zigux/check-phase12-libbpf-snapshot.py`, its direct `--self-test` replay, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and the returned wrapper `make -C zigux phase12-validate`; that smaller support bundle still complements the smoke-first shared replay order instead of proving that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shared direct replay order.
- the directly readable helper-first segmentation is still roadmap-relevant, while the shared Phase 12 validator-first then smoke-and-test order is still narrower than the combined directly readable helper and parked reviewability packet described through the survey, verify-shard, anti-overlap notes, the checked-in reviewability gate, and the historical snapshot anchor.
- the current lane therefore needs survey truthfulness more than a new helper claim. The real boundary is no longer "libbpf is missing" versus "libbpf is landed"; it is "a bounded directly readable helper-first and checked-in reviewability packet is present on current `master`" versus "the shared shipped replay order has not adopted the absent direct `phase12_libbpf_*` replay packet into the active smoke-first route."

## Recorded gap
The highest-value honest gap is the survey boundary itself.

Current `master` still exposes the bounded directly readable helper-first core plus the compile-together companion family. It still does not expose the direct `phase12_libbpf_*` replay files or `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and the shared shipped replay packet still stops at `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and the active driver-facing release order described by the Phase 12 PMO notes.

That means this survey should keep three facts explicit at the same time:
- the bounded directly readable helper-first libbpf footing remains visible on current `master` through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `perf_buffer_poll.zig`, `online_cpu_routing.zig`, `verify.zig`, `cpu_mask_verify.zig`, `logging_verify.zig`, `online_cpu_routing_mask_bridge.zig`, `online_cpu_routing_mask_bridge_verify.zig`, `online_cpu_routing_verify.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `file_path_handle_bridge_verify.zig`, `pin_path_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_lookup.zig`, `ready_buffer_fd_verify.zig`, `ready_buffer_window_verify.zig`, and `type_names_verify.zig`, and it still counts as roadmap-relevant Phase 12 progress while `manifest.json` stays readable as the helper-first packet catalog rather than as shared replay proof
- the broader parked libbpf reviewability packet is still carried through this survey plus the verify-shard and anti-overlap notes together with the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate and `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, because the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` are still absent from current `master`, even though the helper-first core plus the directly readable companion family are now present again
- the shared Phase 12 validator-first support bundle and smoke-and-test routes still do not exercise that broader parked packet directly

Keeping those three facts aligned is the bounded roadmap gap for this lane. It prevents Phase 12 libbpf wording from erasing the still-present directly readable helper segmentation, and it also prevents the release-facing Phase 12 packet from quietly promoting the absent replay set into shipped replay evidence before `zigux/tests/phase12_build.zig` or `zigux/Makefile` actually adopt it.

The same boundary applies to the `tools/lib/bpf/zigux_segments/manifest.json` story too: current Phase 12 wording should keep treating the directly readable helper subset plus the companion family as present on current `master`, keep `manifest.json` explicit as the readable helper-first packet catalog, and keep the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` outside the shipped smoke-first route.

## Non-goals
This survey slice does not claim:
- direct Zig parity for `tools/lib/bpf/libbpf.c`
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- direct procfs reads, bpffs opens, token creation, pinned-object reopen flow, or descriptor ownership side effects
- direct `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, online-CPU routing, or callback delivery
- skeleton population
- ELF collection or object loading
- BTF relocation or load-time verifier interaction
- that the shared Phase 12 validator-first support bundle or smoke-and-test packet already compiles or runs the parked libbpf reviewability files

## Gates
1. rerun the shared build-only Phase 12 surface checker self-test
   - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
2. rerun the shipped validator-side support bundle as shared packet evidence, not as a focused libbpf replay
   - `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`
   - `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`
   - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
   - `python3 scripts/zigux/validate-phase12.py`
   - shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
3. rerun the current shipped smoke-first Phase 12 replay order as shared packet evidence, not as a focused libbpf replay
   - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-smoke`
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-test`
   - `make -C zigux phase12`
4. if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and reuse the shipped Make routes with `ZIG=<attached-zig-path>` while leaving `make -C zigux phase12-validate` explicit as shipped current-route proof ahead of the attached-Zig reruns
   - shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12-test ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`

## Next bounded step
Keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` aligned around the same directly readable-helper-versus-parked-reviewability-versus-shipped-replay boundary.

If this lane reopens, prefer the next one-file truthfulness repair that keeps clear that the bounded directly readable helper-first footing on current `master` includes the core helper set `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `perf_buffer_poll.zig`, and `online_cpu_routing.zig` together with `verify.zig` and its current companion family `cpu_mask_verify.zig`, `logging_verify.zig`, `online_cpu_routing_mask_bridge.zig`, `online_cpu_routing_mask_bridge_verify.zig`, `online_cpu_routing_verify.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `file_path_handle_bridge_verify.zig`, `pin_path_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_lookup.zig`, `ready_buffer_fd_verify.zig`, `ready_buffer_window_verify.zig`, and `type_names_verify.zig`, that `manifest.json` remains directly readable as the helper-first packet catalog, and that the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through the parked reviewability packet until those direct files land again on current `master`. The same reread should keep the smaller validator-first support bundle explicit beside the smoke-first shared replay order instead of treating either route as direct libbpf packet evidence.