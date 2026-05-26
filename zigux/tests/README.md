# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

## Phase 1 host-tools review packet

  * current direct-readback Phase 1 reminder packet:
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/README.md`

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

Tests-root reviewer prompt:
- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?

## Phase 5 shared sample packet

Keep `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `zigux/tests/README.md`, and `zigux/tests/phase5_build.zig` explicit as the shared Phase 5 tests-root reminder packet.

Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.

Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.

Keep `Documentation/zigux/phase5-trace-events-sample-survey.md` explicit with the shared Phase 5 reminder packet as the directly readable survey note for that anchor, while `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay framed as public-tree-backed companion or repo-reality-gap references until a fresh authenticated reread returns that broader four-file trace-events packet directly again.

Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.

Keep the restored kretprobe tests packet explicit too through `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example_survey.zig`, `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig`, and `zigux/tests/phase5_kretprobe_example_probe_spec.zig`, while `zigux/tests/phase5_build.zig` stays the shared rerun handle rather than sample-local proof.

Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.

Tests-root reviewer prompt:
- Does the bounded Phase 5 reminder keep the four approved non-runtime anchors, the direct bytestream replay packet, the mixed kobject split, the restored direct kretprobe packet plus companion replays, the narrower trace-events survey-note split, the shipped guide-surface guard, and the returned shared `zigux/tests/phase5_build.zig` rerun handle aligned without widening into runtime families or extra-sample claims?

## Phase 10 shared virtio closure packet

Keep `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` explicit as the shared Phase 10 tests-root reminder packet.

Keep the returned checker-backed build gate explicit through `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/tests/phase10_build.zig` so the tests-root reminder stays aligned with the same bounded closure packet already named by the docs root, the lane-sequencing note, the shared review companion, and the scripts-root Phase 10 packet.

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Keep the bounded ring and MMIO reminder packet explicit too through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` so the tests-root reminder keeps the virtqueue-wrapper and MMIO-wrapper packet visible beside the shared closure gate without widening into risky transport work.

Keep the bounded input packet explicit too through `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `zigux/tests/phase10_virtio_input_manifest.json`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_survey.zig` so the tests-root reminder stays aligned with the same bounded input packet already carried by the survey, slice, module-slice, checker, closure manifest, and shared build gate instead of collapsing it back into core-only closure wording.

Keep the dedicated teardown-preflight helper and replay explicit here too so the current tests-root packet records the reset-local ready-or-blocked handoff beside the queue-facing and status-drain reminder surfaces without promoting transport-backed lifecycle completion.

Keep the queue-callback-preflight, registration-preflight, status-drain, and teardown-observation replays explicit here so the current tests-root packet still records queue-readiness ordering, registration blockers, in-memory status reclamation, and teardown-reset parity without widening into input registration lifecycle closure, transport callbacks, IRQ delivery, or DMA behavior.
