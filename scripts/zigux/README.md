# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Phase 1 flow
- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.
- `Documentation/zigux/README.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` stay aligned as the bounded Phase 1 helper inventory and validator-first replay packet.
- `check-phase1-bitmap-validator-anchors.py --self-test`, `check-phase1-bitmap-validator-anchors.py`, `check-phase1-find-bit-validator-anchors.py --self-test`, `check-phase1-find-bit-validator-anchors.py`, `check-phase1-route-summary-counts.py --self-test`, `check-phase1-route-summary-counts.py`, `check-phase1-validation-route-inventory.py --self-test`, `check-phase1-validation-route-inventory.py`, `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.
- `check-phase1-find-bit-validator-anchors.py`
- `check-phase1-find-bit-validator-anchors.py --self-test` and `check-phase1-find-bit-validator-anchors.py` keep the Phase 1 `find_bit` review packet explicit, matching `phase1_helper_manifest.json` tail-start and zero-sized anchor checks plus the paired tail-word-boundary anchor review.

Phase 2 flow
- `make -C zigux phase2-tools` is the Linux-style entrypoint for the bounded fixdep, genksyms, genksyms CRC, and mk_elfconfig replay packet.
- that direct `phase2-tools` path now begins with `artifact_diff.py --self-test` and `check-artifact-diff-contract.py`, so shared artifact-diff drift fails before the tool-specific self-tests, parity replays, and Zig unit lanes run.
- `check-genksyms-bridge.py --self-test` exercises the bounded `genksyms` bridge checker packet itself before the Linux-style `phase2-tools` entrypoint replays live bridge artifacts, so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing bridge replay.
- `check-phase2-genksyms-bridge-selftest-alignment.py --self-test` and `check-phase2-genksyms-bridge-selftest-alignment.py` keep the bridge checker self-test markers, the shared validator pair, the workflow route, the Makefile route, and the scripts index aligned before the live bridge replay claims bounded closure evidence.
- `check-genksyms-crc-diff.py --self-test` keeps the bounded genksyms CRC checker packet reviewable before the Linux-style `phase2-tools` replay, so mismatch-contract drift and repeat-run compare coverage fail closed before the parity lane relies on local tool availability.
- that same committed bridge packet currently spans 26 reviewable cases under `zigux/tests/fixtures/genksyms_bridge/`, including the minimal, clustered short-inline, abbreviated long-option, lone-dash passthrough, explicit-terminator positional, missing-argument, and reference-limit fixtures that keep the widened wrapper-first surface explicit.
- `scripts/genksyms/genksyms.c` remains the authoritative parser and export engine for parser-heavy symbol semantics, while `scripts/zigux/genksyms.zig` is intentionally limited to the bounded getopt-style wrapper-first bridge that Phase 2 can prove safely.

Phase 2 implementation surface addendum
- `check-kconfig-bridge.py --self-test` stays paired with `check-kconfig-bridge.py` before live bounded replay.
- The bounded Phase 2 implementation roots remain `genksyms.zig`, `genksyms_crc.zig`, `mk_elfconfig.zig`, `kconfig/conf_bridge.zig`, and `kconfig/confdata_bridge.zig` so the scripts index names the same implementation surface the shared closure validator expects.

Phase 2 toolchain pin scope
- `check-phase2-toolchain-pin-scope.py --self-test` and `check-phase2-toolchain-pin-scope.py` keep `scripts/zigux/zig-toolchain-policy.json`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, and the workflow bootstrap install and verification route aligned before `make -C zigux phase2-validate` or `make -C zigux phase2` claims bounded closure evidence.
- the current bootstrap archive pin remains `x86_64-linux`, and that kbuild-facing review path stays limited to the current workflow host target until first-class evidence exists for widening the archive pin.

Phase 5 flow
- `validate-phase5.py` keeps the shared Phase 5 reference-sample packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the four sample-backed survey notes, `samples/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` before the bundled sample replays claim reviewable coverage.
- `make -C zigux phase5-validate` and `make -C zigux phase5` are the validator-first entrypoints for the four landed Phase 5 anchors, their paired survey replays, and the shared `samples/zigux/README.md` contributor packet.
- keep the direct sample replays and paired survey replays explicit in this scripts-root guide too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test zigux/tests/phase5_bytestream_fifo.zig`, `zig test samples/zigux/kobject_example.zig`, `zig test samples/zigux/kretprobe_example.zig`, `zig test samples/zigux/trace_events_sample.zig`, `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`, `zig test zigux/tests/phase5_kobject_example_survey.zig`, `zig test zigux/tests/phase5_kretprobe_example_survey.zig`, and `zig test zigux/tests/phase5_trace_events_sample_survey.zig`, so contributors can review one landed sample family without having to infer the focused replay surface from the shared build alone.
- keep the later runtime follow-ons distinct here too: `samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig` stay the separate Phase 9 runtime bitmap survey packet, and `samples/zigux/runtime_trace_events.zig` stays the sample-only blocked Phase 9 pilot even though the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is now shipped.

Phase 6 flow
- `validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.
- `make -C zigux phase6-perf`, `make -C zigux phase6-base64-perf`, `make -C zigux phase6-bsearch-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` are the shared and helper-local perf-gate replays for the current bounded Phase 6 helper packet, keeping the aggregate microbench lane explicit beside the validator-first and external-parity checks.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`, `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and `python3 scripts/zigux/check-phase6-hexdump-c-parity.py` are the bounded external portability spot checks for the current base64, bsearch, checksum, and hexdump helper packet.
- `check-phase6-docs-root-external-parity.py`
- `check-phase6-base64-catalog-evidence.py`
- `validate-phase6.py --self-test` exercises the shared Phase 6 marker walk in a compact synthetic tree and fails if catalog-head provenance, script-README wording, perf-survey markers, shared-gates inventory, manifest `surveyed_commit`, or helper-local determinism evidence drifts.

Phase 10 flow
- `validate-phase10.py`, `validate-phase10-closure.py`, and `make -C zigux phase10-validate` keep the Phase 10 ring-plus-input-plus-MMIO lab packet aligned before the shared replay claims closure evidence.
- that shared validation surface spans `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-survey.md`, alongside the closure-inventory and harness-coverage checkers.
- the ring manifest-backed packet keeps the ring reset-reuse replay explicit through `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, while the input packet still names the blocked registration-lifecycle contract even after the landed probe-preflight helper and the MMIO packet stays parked at the bounded MMIO interrupt-ack rung.
- the current reviewer-facing Phase 10 packet counts eleven shared test entrypoints across the core, ring, input, and MMIO bundle, so focused harness shards stay visible without being mistaken for separate closure claims.
