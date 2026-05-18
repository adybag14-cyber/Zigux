# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the earlier `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
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
- rollback owner and reversible-delivery drill: restore the last truthful survey wording in this note, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `python3 scripts/zigux/validate-phase12.py`; keep `make -C zigux phase12-validate` explicit only as reminder-only wrapper vocabulary until `zigux/Makefile` rematerializes it on current `master`; then rerun `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12` so the shared Phase 12 release packet stays reviewable without pretending those shared routes already exercise the parked direct `phase12_libbpf_*` replay files directly

## Why this slice exists
The roadmap places `tools/lib/bpf/libbpf.c` in Phase 12 alongside the other high-risk production-facing consumers because the file is both large and semantically dense even though it lives under `tools/`.

That matters because current `master` still exposes a bounded directly readable `zigux_segments` footing through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `verify.zig`, and the legacy `manifest.json` catalog, while the direct `phase12_libbpf_*` replay files plus `file_path_handle_bridge.zig` remain parked note-owned boundaries. That mixed state preserves real segmented progress while also keeping the broader reviewability packet smaller than the shipped replay order.

Those are still useful footholds, but the live Phase 12 survey has to explain how that earlier helper work fits the heavy-helper roadmap without overstating the current replay packet. The directly readable helper-first footing remains roadmap-relevant, while the broader parked libbpf reviewability packet has to stay described through the survey, verify-shard, anti-overlap notes, and snapshot anchor until the shared replay order actually adopts it.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, bridge, queue-routing, object-model, relocation, and verifier-facing concerns in one file.
- current `master` still exposes a bounded directly readable libbpf segment footing under `tools/lib/bpf/zigux_segments/` through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `verify.zig`, and the legacy `manifest.json` catalog.
- the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still stay recorded only through the survey, verify-shard, and anti-overlap notes until they land again on current `master`, while the directly readable `tools/lib/bpf/zigux_segments/verify.zig` compile-together shard now sits beside the helper subset without implying shipped smoke-first adoption; `scripts/zigux/check-phase12-libbpf-snapshot.py` and the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` file now keep only the same four note-owned support anchors explicit (`Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`), so the shared survey wording should not imply that a separate checked-in `phase12_libbpf_reviewability` gate is still present on current `master`.
- the shared shipped replay order is still narrower than that mixed direct-plus-parked libbpf packet. Current `zigux/tests/phase12_build.zig` wires only the `virtio_net` and `virtio_scsi` Phase 12 shards, and current `zigux/Makefile` keeps `phase12-smoke`, `phase12-test`, and `phase12` tied to that same build file.
- `scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.
- current `master` now also ships the validator-side support bundle through `scripts/zigux/check-phase12-release-readiness-packet.py` and `scripts/zigux/validate-phase12.py`, while `make -C zigux phase12-validate` remains reminder-only vocabulary because current `zigux/Makefile` still omits that wrapper; that smaller support bundle still complements the smoke-first shared replay order instead of proving that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shared direct replay order.
- the directly readable helper-first segmentation is still roadmap-relevant, while the shared Phase 12 validator-first then smoke-and-test order is still narrower than the combined directly readable helper and parked reviewability packet described only through the survey, verify-shard, anti-overlap notes, and the historical snapshot anchor.
- the current lane therefore needs survey truthfulness more than a new helper claim. The real boundary is no longer "libbpf is missing" versus "libbpf is landed"; it is "a bounded directly readable helper-first and checked-in reviewability packet is present on current `master`" versus "the shared shipped replay order has not adopted the absent direct `phase12_libbpf_*` replay packet into the active smoke-first route."

## Recorded gap
The highest-value honest gap is the survey boundary itself.

Current `master` still exposes the bounded directly readable helper subset plus `pin_path.zig`, `verify.zig`, and the checked-in `tools/lib/bpf/zigux_segments/manifest.json` legacy helper catalog. It still does not expose the direct `phase12_libbpf_*` replay files or `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and the shared shipped replay packet still stops at `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and the active driver-facing release order described by the Phase 12 PMO notes.

That means this survey should keep three facts explicit at the same time:
- the bounded directly readable helper-first libbpf footing remains visible on current `master` through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `verify.zig`, and the legacy `manifest.json` catalog, and it still counts as roadmap-relevant Phase 12 progress
- the broader parked libbpf reviewability packet is still carried primarily through this survey plus the verify-shard and anti-overlap notes, with `zigux/tests/fixtures/phase12_libbpf_snapshot.json` kept only as a parked historical visibility anchor because the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` are still absent from current `master`, even though `pin_path.zig` and `verify.zig` are now directly readable again
- the shared Phase 12 validator-first support bundle and smoke-and-test routes still do not exercise that broader parked packet directly

Keeping those three facts aligned is the bounded roadmap gap for this lane. It prevents Phase 12 libbpf wording from erasing the still-present directly readable helper segmentation, and it also prevents the release-facing Phase 12 packet from quietly promoting the absent replay set into shipped replay evidence before `zigux/tests/phase12_build.zig` or `zigux/Makefile` actually adopt it.

The same boundary applies to the current checked-in `tools/lib/bpf/zigux_segments/manifest.json` story: current Phase 12 wording should keep treating the directly readable helper subset plus `pin_path.zig`, `verify.zig`, and that legacy catalog as present on current `master`, while the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still remain outside the shipped smoke-first route.

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
   - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
   - `python3 scripts/zigux/validate-phase12.py`
   - reminder-only wrapper vocabulary until it returns: `make -C zigux phase12-validate`
3. rerun the current shipped smoke-first Phase 12 replay order as shared packet evidence, not as a focused libbpf replay
   - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-smoke`
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-test`
   - `make -C zigux phase12`
4. if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and reuse only the shipped Make routes with `ZIG=<attached-zig-path>` while leaving `make -C zigux phase12-validate` explicit only as reminder vocabulary until that wrapper returns
   - reminder-only wrapper vocabulary until it returns: `make -C zigux phase12-validate`
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12-test ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`

## Next bounded step
Keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` aligned around the same directly readable-helper-versus-parked-reviewability-versus-shipped-replay boundary.

If this lane reopens, prefer the next one-file truthfulness repair that keeps clear that the bounded directly readable helper subset on current `master` is `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `verify.zig`, and the legacy `manifest.json` catalog, while the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through the parked reviewability packet until those direct files land again on current `master`. The same reread should keep the smaller validator-first support bundle explicit beside the smoke-first shared replay order instead of treating either route as direct libbpf packet evidence.
