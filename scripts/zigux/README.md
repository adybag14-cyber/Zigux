# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- committed parity fixture generation and checking
- future ABI/layout guards
- artifact diff helpers for host-side tools

Current bootstrap helpers
- `artifact_diff.py`
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `validate-phase4.py`
- `validate-phase5.py`
- `validate-phase6.py`
- `validate-phase7.py`
- `validate-phase8.py`
- `validate-phase9.py`
- `validate-phase10.py`
- `validate-phase10-closure.py`
- `check-phase11-build-inventory.py`
- `validate-phase11.py`
- `check-phase12-build-inventory.py`
- `check-phase12-libbpf-snapshot.py`
- `validate-phase12.py`
- `validate-phase13-release.py`
- `validate-phase14.py`
- `validate-phase3-roadmap-gap-survey.py`
- `validate-phase3-export-uapi-survey.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-cross.py`
- `check-mk-elfconfig-diff.py`
- `check-phase6-base64-c-parity.py`
- `check-phase6-bsearch-c-parity.py`

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.

Phase 2 flow
- `artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths before the bounded Phase 2 artifact lanes run.
- `check-artifact-diff-contract.py` keeps the outward artifact-diff CLI surface reviewable inside the closed Phase 2 packet so missing-file, malformed-JSON, and SHA-256 contract drift cannot hide behind the helper's built-in self-test.
- `validate-phase1.py` now also checks that `zigux/tests/fixtures/phase1_helpers.json` keeps the exact committed top-level helper sections and evidence-key shape, so stale Phase 1 expected-output drift fails before parity replay.
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including the multi-target, escaped-whitespace, comment-only no-target, and missing-dependency failure artifacts under `zigux/tests/fixtures/fixdep/`, reruns both the C tool and Zig tool to prove repeat-run artifact determinism, and now also fails if any success-path fixdep case starts emitting unexpected stderr noise.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane, including success-path stderr silence and repeat-run stderr determinism for the stdout-json bridge fixtures.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C harness and Zig tool before fixture comparison.
- `check-kconfig-bridge.py --self-test` exercises the bounded kconfig bridge checker packet itself before the Linux-style `phase2-kconfig` entrypoint replays the live bridge artifacts.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes and now proves repeat-run JSON determinism for both bridge outputs before fixture comparison.
- `check-phase2-cross.py --self-test` exercises the bounded cross-target checker packet itself before the Linux-style `phase2-cross` entrypoint replays live Zig compiles, so manifest-count and explicit-target failure drift cannot hide behind local tool availability.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py --self-test` exercises the bounded mk_elfconfig checker packet itself before the Linux-style `phase2-tools` entrypoint replays the live artifact lane, so fixture-shape and explicit-tool drift cannot hide behind local compiler or Zig availability.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C tool and Zig tool before fixture comparison.
- `check-phase1-parity.py` now reruns the bounded C harness after fixture comparison so the shared Phase 1 parity artifact also proves repeat-run JSON determinism instead of only a single-pass match.
- `check-phase1-bench.py --self-test` exercises the bounded Phase 1 benchmark checker itself before the live benchmark smoke runs, so parser, expected-key, and undeclared-key drift cannot hide behind a locally passing Zig bench replay.

Phase 3 flow
- `validate-phase3-roadmap-gap-survey.py` checks that `Documentation/zigux/phase3-roadmap-gap-survey.md` stays aligned with the live repo-backed Phase 3 substrate, the published README note, the current export shim and current `zigux/uapi/version.zig` boundary, the current roadmap-backed `rbtree` gap, and the already-landed Phase 1 plus Phase 7 `rbtree` evidence that still falls short of a Phase 3 boundary-facing packet.
- `validate-phase3-roadmap-gap-survey.py --self-test` exercises the survey-marker and README-hook checks without needing the full repo tree.
- `validate-phase3-export-uapi-survey.py` checks that `Documentation/zigux/phase3-export-uapi-boundary-survey.md` stays aligned with the live export-shim and bounded `zigux/uapi/version.zig` surface, the published README notes, and the shared `make -C zigux phase3-validate` entrypoint.
- `validate-phase3-export-uapi-survey.py --self-test` exercises the export-shim and UAPI survey-marker checks without needing the full repo tree.
- `validate-phase3-policy-unsafe-survey.py --self-test` exercises the policy, narrow-unsafe, and MMIO survey-marker checks without needing the full repo tree, and it now emits its own `PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass` token so isolated validator coverage stays distinguishable from a live survey replay.
- `validate-phase3.py` now requires the focused `phase3-policy-unsafe` build and test files plus the published `PHASE3_POLICY_UNSAFE_GATE` ABI-slice marker, so the landed policy and unsafe substrate no longer hides only inside the broader ABI replay and keeps the dedicated interop-policy unsafe-byte decoding gate reviewable on its own.
- the same validator now keeps `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_policy_unsafe.zig`, and `zigux/tests/phase3_policy_unsafe_build.zig` aligned with `zigux/tests/fixtures/phase3_abi_manifest.json` and `Documentation/zigux/phase3-abi-slice.md`, so allocator-owned init and reset requirements plus the scoped narrow-unsafe and MMIO helper path cannot drift out of the published packet silently.
- the same validator surface now also carries the latest focused policy evidence: `zigux/tests/phase3_policy_unsafe.zig` covers overflow-checked unsafe address math, and the Phase 3 source-audit self-test keeps the layout-assert, panic-policy, allocator-policy, and narrow-unsafe markers reviewable even when the full repo tree is not under replay.
- the same validator now also treats the focused low-level wrapper gate as a real anti-regression surface instead of a presence-only file list: it restores the shared self-test import path, checks the exact exported atomic, barrier, and MMIO helper surface against the published Phase 3 ABI slice, and still checks the scoped `read16`, `write16`, `read32`, and `write32` MMIO entry points plus the low-level replay’s compare-exchange mismatch, barrier probe, denied-scope, and allowed scoped-MMIO assertions so width-specific, scope-specific, or undocumented wrapper-surface drift fails before Phase 3 review claims stay green.

Phase 5 flow
- `validate-phase5.py` keeps the shipped Phase 5 contributor packet aligned across `samples/zigux/README.md`, the four sample-backed survey notes, the four manifest-backed surveys, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, and the bootstrap workflow before any shared sample replay claims stay green.
- `validate-phase5.py --self-test` exercises the marker-sync checks for the sample-backed survey packet and fails if a manifest-side `surveyed_commit` drift stops matching the paired survey note.
- `make -C zigux phase5-validate` is the validator-first entrypoint for the approved sample ports, reviewable Zigux idioms, contributor guidance, and `Documentation/zigux` material that Phase 5 ships today.
- `make -C zigux phase5` and `zig build test --build-file zigux/tests/phase5_build.zig --summary all` are the shared replay surface for the four roadmap-backed reference samples after the validator gate passes.
- `zigux/tests/phase5_build.zig` is the shared build entrypoint for the bytestream FIFO, kobject, kretprobe, and trace-events sample packets, including their paired direct-sample and manifest-backed survey replays.
- `samples/zigux/README.md` is the contributor-facing sample-root catalog for the approved Phase 5 anchors and the explicit boundary that keeps later `runtime_*` starters out of the sample-pattern lane.

Phase 8 flow
- `validate-phase8.py` keeps the parked repo-hosted tooling packet aligned across `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` so the shared review surface stays explicit.
- `make -C zigux phase8-validate` is the validator-first entrypoint for the current Phase 8 flow.
- `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, and `zigux/tests/phase8_build.zig` keep the focused and shared replay paths visible in one place.
- `tools/lib/subcmd/exec-cmd.zig`, the deferred execution notes around `execvp()`, and the separate `kernel/workqueue.c` freeze boundary remain helper-only review surfaces rather than new process-launch claims.
- the segmented libbpf packet stays bounded to helper-first slices such as `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/type_names.zig` plus the shared `phase8-libbpf-segment-survey.md` and `phase8-userspace-kernel-bridge-boundary-survey.md` notes.
- `make -C zigux phase8-test` and `zig build test --build-file zigux/tests/phase8_build.zig --summary all` remain the shared replay path after the validator passes.

Phase 13 flow
- `validate-phase13-release.py` keeps `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned as one shared release-discipline packet instead of leaving the Phase 13 review path split across isolated docs or build wiring.
- `make -C zigux phase13-validate` runs that dedicated release validator before the broader shared replay.
- `make -C zigux phase13` routes through the validator before the shared replay, so the local convenience path matches the release-facing review contract.
- `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, and `zigux/tests/phase13_devres_reviewability.zig` keep the helper-first `devres` packet explicit about live DMA-backed mappings and scatterlist ownership staying blocked rather than implied.

Phase 14 flow
- `validate-phase14.py` keeps the shared Phase 14 smoke packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, and the four anchor-local manifests plus survey notes so the shared stay-in-C boundary remains reviewable as one validator-backed packet.
- `make -C zigux phase14-validate` is the validator-first entrypoint for the shared Phase 14 smoke packet before any broader replay claims stay green.
- `make -C zigux phase14-smoke` is the focused smoke-shard replay contract and intentionally routes through the shared `zigux/tests/phase14_build.zig` entrypoint instead of bypassing the reviewable wrapper path.
- `zigux/tests/phase14_build.zig` is the shared Phase 14 build entrypoint: it keeps the focused smoke-shard replay contract explicit, records the same shared Phase 14 smoke packet boundary, and leaves the deeper bridge or survey slices under the broader bundle.
- the shared packet keeps the roadmap stay-in-C boundary explicit by recording the named owner, validation gate, rollback owner, and roadmap risk bundle (`hidden runtime behavior`, `memory-ordering mistakes`, `overpromising full parity`, `deep-core scope creep`) beside the focused wrapper path.
- the same packet also keeps the rollback threshold, fallback path, and automatic return-to-blocked trigger catalog explicit so the shared smoke path fails closed before it overstates Phase 14 delivery.
