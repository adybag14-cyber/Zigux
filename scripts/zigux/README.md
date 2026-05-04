# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

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

Phase 6 flow
- `validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`, `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and `python3 scripts/zigux/check-phase6-hexdump-c-parity.py` are the bounded external portability spot checks for the current base64, bsearch, checksum, and hexdump helper packet.
- `check-phase6-docs-root-external-parity.py`
- `check-phase6-base64-catalog-evidence.py`
- `validate-phase6.py --self-test` exercises the shared Phase 6 marker walk in a compact synthetic tree and fails if catalog-head provenance, script-README wording, perf-survey markers, shared-gates inventory, manifest `surveyed_commit`, or helper-local determinism evidence drifts.

Phase 10 flow
- `validate-phase10.py`, `validate-phase10-closure.py`, and `make -C zigux phase10-validate` keep the Phase 10 ring-plus-input-plus-MMIO lab packet aligned before the shared replay claims closure evidence.
- that shared validation surface spans `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-survey.md`, alongside the closure-inventory and harness-coverage checkers.
- the ring manifest-backed packet keeps the ring reset-reuse replay explicit through `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, while the input packet still names the blocked registration-lifecycle contract even after the landed probe-preflight helper and the MMIO packet stays parked at the bounded MMIO interrupt-ack rung.
- the current reviewer-facing Phase 10 packet counts eleven shared test entrypoints across the core, ring, input, and MMIO bundle, so focused harness shards stay visible without being mistaken for separate closure claims.
