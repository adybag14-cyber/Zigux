#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd().resolve()
README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
MAKEFILE_REL = "zigux/Makefile"
README_HELPER_SECTION = "Current bootstrap helpers"

REQUIRED_HELPERS = (
    "check-zig-toolchain.py",
    "validate-bootstrap.py",
    "install-zig.py",
    "check-phase1-installer-review-surfaces.py",
    "validate-phase1.py",
    "check-phase1-bench.py",
    "validate-phase1-closure.py",
    "validate-phase2.py",
    "validate-phase2-closure.py",
    "check-phase2-tool-manifest-packets.py",
    "validate-phase3.py",
    "validate_phase3_selftest.py",
    "check-phase3-selftest-surface.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "check-phase3-policy-byte-guards.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-bindings-syntax.py",
    "survey-phase3-abi-constant-parity.py",
    "artifact_diff.py",
    "check-artifact-diff-contract.py",
    "validate-phase4.py",
    "check-phase4-gate-evidence.py",
    "check-phase4-artifact-diff-determinism.py",
    "check-phase6-shared-surface.py",
    "validate-phase7.py",
    "check-phase7-make-wrapper.py",
    "check-phase7-make-wrapper-selftest-alignment.py",
    "check-phase7-argv-split-packet.py",
    "check-phase7-rbtree-parity.py",
    "check-phase7-build-wiring.py",
    "validate-phase8.py",
    "check-phase8-exec-cmd-packet.py",
    "check-phase8-help-kallsyms-packet.py",
    "check-phase9-build-only-surface.py",
    "check-phase10-core-packet.py",
    "check-phase10-ring-packet.py",
    "check-phase10-input-packet.py",
    "check-phase10-mmio-packet.py",
    "check-phase10-mmio-freeze-boundary.py",
    "check-phase11-shared-replay-contract.py",
    "check-phase11-bcm2835-wdt-packet.py",
    "check-phase11-dw-wdt-packet.py",
    "check-phase11-header-boundary-packet.py",
    "check-phase11-hvc-survey-packet.py",
    "check-build-only-phase12-surface.py",
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
    "check-phase13-landlock-ruleset-packet.py",
    "check-phase13-notifier-packet.py",
    "validate-phase14.py",
    "check-phase14-docs-root-smoke-summary.py",
    "check-phase14-rollback-threshold-sequencing.py",
    "check-phase14-release-boundary-exact-counts.py",
    "validate-phase15.py",
    "check-phase15-review-process-handoff.py",
    "check-phase15-scripts-readme-alignment.py",
    "run-phase3-checks.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "check-phase1-parity.py",
    "check-phase2-fixdep-gate.py",
    "check-fixdep-diff.py",
    "check-genksyms-bridge.py",
    "check-phase2-genksyms-bridge-selftest-alignment.py",
    "check-genksyms-crc-diff.py",
    "check-kconfig-bridge.py",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-tests-readme-alignment.py",
    "check-phase2-cross-selftest-alignment.py",
    "check-phase2-toolchain-pin-scope.py",
    "check-phase2-cross.py",
    "check-mk-elfconfig-diff.py",
)

ABSENT_VALIDATE_TARGETS = ("phase9-validate", "phase12-validate")

PHASE2_TOOLCHAIN_TARGET = "phase2-toolchain"
PHASE2_TOOLCHAIN_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
)
PHASE2_KCONFIG_TARGET = "phase2-kconfig"
PHASE2_KCONFIG_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
)
PHASE2_CROSS_TARGET = "phase2-cross"
PHASE2_CROSS_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
)

PHASE3_VALIDATE_TARGET = "phase3-validate"
PHASE3_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-selftest-surface.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py",
)
PHASE3_SELFTEST_TARGET = "phase3-selftest"
PHASE3_SELFTEST_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py",
)

PHASE4_VALIDATE_TARGET = "phase4-validate"
PHASE4_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
)

PHASE6_VALIDATE_TARGET = "phase6-validate"
PHASE6_VALIDATE_HELPERS = ("check-phase6-shared-surface.py",)
PHASE7_VALIDATE_TARGET = "phase7-validate"
PHASE7_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
)
PHASE8_VALIDATE_TARGET = "phase8-validate"
PHASE8_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-exec-cmd-packet.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-help-kallsyms-packet.py",
)
PHASE13_VALIDATE_TARGET = "phase13-validate"
PHASE13_VALIDATE_HELPERS = (
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
    "check-phase13-landlock-ruleset-packet.py",
    "check-phase13-notifier-packet.py",
)
PHASE15_VALIDATE_TARGET = "phase15-validate"
PHASE15_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
)

PHASE4_VALIDATE_ROUTE_SNIPPET = (
    "- `make -C zigux phase4-validate` reruns the validator-first Phase 4 route, "
    "including `scripts/zigux/check-artifact-diff-contract.py`, "
    "`scripts/zigux/check-phase4-artifact-diff-determinism.py`, and "
    "`scripts/zigux/check-phase4-gate-evidence.py`, before the shared "
    "`zigux/tests/phase4_build.zig` replay."
)

REQUIRED_README_SNIPPETS = (
    "- The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-catalog-selftest.py`, `check-phase3-abi-dump-gate.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-byte-guards.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-abi-bindings-syntax.py`, `survey-phase3-abi-constant-parity.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.",
    PHASE4_VALIDATE_ROUTE_SNIPPET,
    "- there is no separate shared `validate-phase6.py` or broader external portability checker packet beyond `check-phase6-shared-surface.py` on `master`; the shipped dedicated perf replays are `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, while `make -C zigux phase6-perf` remains the narrow aggregate route for the checksum and hexdump perf packet rather than a bundle-wide Phase 6 perf closure",
    "- the current shared Phase 7 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `samples/zigux/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/phase7_build.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "- `make -C zigux phase7-validate` keeps the shared Phase 7 validator plus the dedicated make-wrapper, make-wrapper selftest-alignment, argv_split packet, rbtree parity, and build-wiring checkers wired through the Linux-style validation entrypoint, and `make -C zigux phase7` remains the full Linux-style replay route for that same parked helper packet.",
    "- the current shared Phase 8 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-exec-cmd-packet.py`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "- `make -C zigux phase8-validate` keeps `validate-phase8.py` plus the focused `check-phase8-exec-cmd-packet.py` and `check-phase8-help-kallsyms-packet.py` checkers wired through the Linux-style validation entrypoint, while `make -C zigux phase8-help-test`, `make -C zigux phase8-help-kallsyms-test`, and `make -C zigux phase8-kallsyms-test` keep the parked help-plus-kallsyms shard explicit before the broader tooling replays run, and `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, and `make -C zigux phase8-perf-buffer-poll-test` keep the parked libbpf shard trio visible beside the shared owner-map note instead of letting the scripts-root reminder collapse back toward the older starter-only packet.",
    "- there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`; future runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate, validation, or review-surface step that keeps those four loader handoffs plus the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` allocator/init-flow contract reviewable without widening into a larger runtime-module implementation.",
    "- `python3 scripts/zigux/check-phase10-core-packet.py` keeps the restored core survey note, core manifest, core survey gate, reset-queue replay, and driver-id replay aligned around that shared review packet, and `python3 scripts/zigux/check-phase10-input-packet.py` keeps the input slice, input module slice, input survey note, build wiring, and status-drain replay markers aligned inside that same bounded Phase 10 route while `zig build test --build-file zigux/tests/phase10_build.zig` and `make -C zigux phase10` rerun the same bounded virtio core, virtio ring, virtio input, and virtio mmio packet.",
    "- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make surfaces until new validator files actually land.",
    "- `make -C zigux phase13-validate` keeps that same release packet wired through the Linux-style validation entrypoint.",
    "- `check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` keep `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with the committed `fixdep`, `genksyms`, `artifact_tools` (`genksyms_crc` plus `mk_elfconfig`), `kconfig`, and `confdata` packet manifests so the shared Phase 2 tool inventory, self-test route, and live gate wiring stay explicit before the direct Zig replays run.",
)

TESTS_README_PHASE3_MARKERS = (
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py --self-test",
    "scripts/zigux/phase3_check_lib.py --self-test",
    "scripts/zigux/generate-phase3-check-wrappers.py --check",
    "scripts/zigux/run-phase3-checks.py --self-test",
    "scripts/zigux/run-phase3-checks.py",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "make -C zigux phase3-selftest",
    "opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`",
)

TESTS_README_PHASE8_MARKERS = (
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
    "make -C zigux phase8-help-kallsyms-test",
    "make -C zigux phase8-file-path-handle-bridge-test",
    "make -C zigux phase8-libbpf-segments-test",
    "make -C zigux phase8-perf-buffer-poll-test",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _collect_helper_entries(readme: str) -> tuple[list[str], list[str]]:
    found = False
    entries: list[str] = []
    issues: list[str] = []
    for line in readme.splitlines():
        stripped = line.strip()
        if not found:
            if stripped == README_HELPER_SECTION:
                found = True
            continue
        if stripped.startswith("- `") and stripped.endswith("`"):
            entries.append(stripped[3:-1])
            continue
        if not stripped:
            continue
        break
    if not found:
        issues.append(f"missing_readme_section:{README_HELPER_SECTION}")
    elif not entries:
        issues.append("missing_readme_helper_entries")
    return entries, issues


def _is_makefile_target_header(raw: str) -> bool:
    if raw.startswith((" ", "\t")):
        return False
    stripped = raw.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if ":=" in stripped or "?=" in stripped or "+=" in stripped or "!=" in stripped:
        return False
    return ":" in stripped


def _collect_makefile_target_lines(makefile: str, target: str) -> list[str] | None:
    in_target = False
    lines: list[str] = []
    target_header = f"{target}:"
    for raw in makefile.splitlines():
        stripped = raw.strip()
        if not in_target:
            if stripped.startswith(target_header):
                in_target = True
            continue
        if _is_makefile_target_header(raw):
            break
        lines.append(raw)
    return lines if in_target else None


def _collect_target_helpers(makefile: str, target: str) -> list[str]:
    lines = _collect_makefile_target_lines(makefile, target)
    if lines is None:
        return []
    helpers: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if "scripts/zigux/" not in stripped:
            continue
        rel = stripped.split("scripts/zigux/", 1)[1].split()[0]
        if rel.endswith(".py"):
            helpers.append(Path(rel).name)
    return helpers


def _validate_target_helpers(issues: list[str], makefile: str, target: str, required_helpers: tuple[str, ...]) -> None:
    lines = _collect_makefile_target_lines(makefile, target)
    if lines is None:
        issues.append(f"missing_makefile_target:{target}")
        return
    helpers = _collect_target_helpers(makefile, target)
    for helper in required_helpers:
        count = helpers.count(helper)
        if count == 0:
            issues.append(f"missing_makefile_helper:{target}:{helper}")
        elif count != 1:
            issues.append(f"unexpected_makefile_helper_count:{target}:{helper}:{count}")
    for helper in helpers:
        if helper not in required_helpers:
            issues.append(f"unexpected_makefile_helper:{target}:{helper}")
    if [helper for helper in helpers if helper in required_helpers] != list(required_helpers):
        issues.append(f"makefile_helper_order_drift:{target}")


def _validate_target_commands(issues: list[str], makefile: str, target: str, required_commands: tuple[str, ...]) -> None:
    lines = _collect_makefile_target_lines(makefile, target)
    if lines is None:
        issues.append(f"missing_makefile_target:{target}")
        return
    commands = [raw.strip() for raw in lines if raw.strip()]
    expected = list(required_commands)
    for command in expected:
        count = commands.count(command)
        if count == 0:
            issues.append(f"missing_makefile_command:{target}:{command}")
        elif count != 1:
            issues.append(f"unexpected_makefile_command_count:{target}:{count}:{command}")
    for command in commands:
        if command not in required_commands:
            issues.append(f"unexpected_makefile_command:{target}:{command}")
    if [command for command in commands if command in required_commands] != expected:
        issues.append(f"makefile_command_order_drift:{target}")


def _validate_tests_readme_phase3_markers(issues: list[str], text: str) -> None:
    for marker in TESTS_README_PHASE3_MARKERS:
        if marker.startswith("opt-in safety check"):
            count = text.count(marker)
        else:
            count = text.count(f"`{marker}`")
            count += sum(1 for line in text.splitlines() if line.strip() == marker)
        if count == 0:
            issues.append(f"missing_tests_readme_phase3_marker:{marker}")
        elif count != 1:
            issues.append(f"unexpected_tests_readme_phase3_marker_count:{count}:{marker}")


def _validate_tests_readme_phase8_markers(issues: list[str], text: str) -> None:
    for marker in TESTS_README_PHASE8_MARKERS:
        count = text.count(f"`{marker}`")
        count += sum(1 for line in text.splitlines() if line.strip() == marker)
        if count == 0:
            issues.append(f"missing_tests_readme_phase8_marker:{marker}")
        elif count != 1:
            issues.append(f"unexpected_tests_readme_phase8_marker_count:{count}:{marker}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        readme = _read(root / README_REL)
    except FileNotFoundError:
        return [f"missing_readme:{README_REL}"]
    try:
        tests_readme = _read(root / TESTS_README_REL)
    except FileNotFoundError:
        return [f"missing_tests_readme:{TESTS_README_REL}"]
    try:
        makefile = _read(root / MAKEFILE_REL)
    except FileNotFoundError:
        return [f"missing_makefile:{MAKEFILE_REL}"]

    helper_entries, helper_issues = _collect_helper_entries(readme)
    issues.extend(helper_issues)
    if helper_entries:
        seen: set[str] = set()
        for entry in helper_entries:
            if entry in seen:
                issues.append(f"duplicate_readme_helper_entry:{entry}")
            seen.add(entry)
        expected = list(REQUIRED_HELPERS)
        for helper in expected:
            if helper not in helper_entries:
                issues.append(f"missing_readme_helper_entry:{helper}")
            if not (root / "scripts" / "zigux" / helper).exists():
                issues.append(f"missing_repo_file:scripts/zigux/{helper}")
        for helper in helper_entries:
            if helper not in REQUIRED_HELPERS:
                issues.append(f"unexpected_readme_helper_entry:{helper}")
        if [entry for entry in helper_entries if entry in REQUIRED_HELPERS] != expected:
            issues.append("readme_helper_order_drift")

    for target in ABSENT_VALIDATE_TARGETS:
        if _collect_makefile_target_lines(makefile, target) is not None:
            issues.append(f"unexpected_makefile_target:{target}")

    _validate_target_commands(issues, makefile, PHASE2_TOOLCHAIN_TARGET, PHASE2_TOOLCHAIN_COMMANDS)
    _validate_target_commands(issues, makefile, PHASE2_KCONFIG_TARGET, PHASE2_KCONFIG_COMMANDS)
    _validate_target_commands(issues, makefile, PHASE2_CROSS_TARGET, PHASE2_CROSS_COMMANDS)
    _validate_target_commands(issues, makefile, PHASE3_VALIDATE_TARGET, PHASE3_VALIDATE_COMMANDS)
    _validate_target_commands(issues, makefile, PHASE3_SELFTEST_TARGET, PHASE3_SELFTEST_COMMANDS)
    _validate_target_commands(issues, makefile, PHASE4_VALIDATE_TARGET, PHASE4_VALIDATE_COMMANDS)
    _validate_target_helpers(issues, makefile, PHASE6_VALIDATE_TARGET, PHASE6_VALIDATE_HELPERS)
    _validate_target_commands(issues, makefile, PHASE7_VALIDATE_TARGET, PHASE7_VALIDATE_COMMANDS)
    _validate_target_commands(issues, makefile, PHASE8_VALIDATE_TARGET, PHASE8_VALIDATE_COMMANDS)
    _validate_target_helpers(issues, makefile, PHASE13_VALIDATE_TARGET, PHASE13_VALIDATE_HELPERS)
    _validate_target_commands(issues, makefile, PHASE15_VALIDATE_TARGET, PHASE15_VALIDATE_COMMANDS)

    for snippet in REQUIRED_README_SNIPPETS:
        count = readme.count(snippet)
        if count == 0:
            issues.append(f"missing_readme_snippet:{snippet}")
        elif count != 1:
            issues.append(f"unexpected_readme_snippet_count:{count}:{snippet}")

    _validate_tests_readme_phase3_markers(issues, tests_readme)
    _validate_tests_readme_phase8_markers(issues, tests_readme)
    return issues


def _baseline_readme() -> str:
    helper_lines = "\n".join(f"- `{helper}`" for helper in REQUIRED_HELPERS)
    return "\n".join(["# scripts/zigux", "", README_HELPER_SECTION, helper_lines, "", *REQUIRED_README_SNIPPETS, ""])


def _baseline_tests_readme() -> str:
    return "\n".join(["# zigux/tests", "", *TESTS_README_PHASE3_MARKERS, *TESTS_README_PHASE8_MARKERS, ""])


def _baseline_makefile() -> str:
    return "\n".join((
        "phase2-toolchain:",
        *PHASE2_TOOLCHAIN_COMMANDS,
        "",
        "phase2-kconfig:",
        *PHASE2_KCONFIG_COMMANDS,
        "",
        "phase2-cross:",
        *PHASE2_CROSS_COMMANDS,
        "",
        "phase3-validate:",
        *PHASE3_VALIDATE_COMMANDS,
        "",
        "phase3-selftest:",
        *PHASE3_SELFTEST_COMMANDS,
        "",
        "phase4-validate:",
        *PHASE4_VALIDATE_COMMANDS,
        "",
        "phase6-validate:",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "",
        "phase7-validate:",
        *PHASE7_VALIDATE_COMMANDS,
        "",
        "phase8-validate:",
        *PHASE8_VALIDATE_COMMANDS,
        "",
        "phase13-validate:",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py",
        "",
        "phase15-validate:",
        *PHASE15_VALIDATE_COMMANDS,
        "",
    ))


def _populate_repo(root: Path) -> None:
    _write(root / README_REL, _baseline_readme())
    _write(root / TESTS_README_REL, _baseline_tests_readme())
    _write(root / MAKEFILE_REL, _baseline_makefile())
    for helper in REQUIRED_HELPERS:
        _write(root / "scripts" / "zigux" / helper, "# stub\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        _populate_repo(root)
        assert validate(root) == []
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/check-phase3-selftest-surface.py\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/check-phase3-selftest-surface.py"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/check-phase3-readme-tooling-inventory.py\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/check-phase3-readme-tooling-inventory.py"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/check-phase3-abi-dump-gate.py\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/check-phase3-abi-dump-gate.py"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/phase3_catalog.py --self-test\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/phase3_catalog.py --self-test"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/phase3_check_lib.py --self-test\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/phase3_check_lib.py --self-test"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/generate-phase3-check-wrappers.py --check\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/generate-phase3-check-wrappers.py --check"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/run-phase3-checks.py --self-test\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/run-phase3-checks.py --self-test"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("scripts/zigux/run-phase3-checks.py\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:scripts/zigux/run-phase3-checks.py"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("python3 scripts/zigux/validate_phase3_selftest.py\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase3_marker:python3 scripts/zigux/validate_phase3_selftest.py"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace(
            "scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
            "scripts/zigux/check-phase3-readme-tooling-inventory.py\nscripts/zigux/check-phase3-readme-tooling-inventory.py\n",
            1,
        )
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == [
            "unexpected_tests_readme_phase3_marker_count:2:scripts/zigux/check-phase3-readme-tooling-inventory.py"
        ]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("zigux/tests/phase8_help_kallsyms_only_build.zig\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase8_marker:zigux/tests/phase8_help_kallsyms_only_build.zig"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("make -C zigux phase8-help-kallsyms-test\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase8_marker:make -C zigux phase8-help-kallsyms-test"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace(
            "make -C zigux phase8-help-kallsyms-test\n",
            "make -C zigux phase8-help-kallsyms-test\nmake -C zigux phase8-help-kallsyms-test\n",
            1,
        )
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == [
            "unexpected_tests_readme_phase8_marker_count:2:make -C zigux phase8-help-kallsyms-test"
        ]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace("make -C zigux phase8-perf-buffer-poll-test\n", "", 1)
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == ["missing_tests_readme_phase8_marker:make -C zigux phase8-perf-buffer-poll-test"]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        tests = _baseline_tests_readme().replace(
            "make -C zigux phase8-file-path-handle-bridge-test\n",
            "make -C zigux phase8-file-path-handle-bridge-test\nmake -C zigux phase8-file-path-handle-bridge-test\n",
            1,
        )
        _write(root / TESTS_README_REL, tests)
        assert validate(root) == [
            "unexpected_tests_readme_phase8_marker_count:2:make -C zigux phase8-file-path-handle-bridge-test"
        ]
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "phase3-selftest:\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py\n",
            "phase3-selftest:\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"missing_makefile_command:{PHASE3_SELFTEST_TARGET}:{PHASE3_SELFTEST_COMMANDS[0]}",
            f"makefile_command_order_drift:{PHASE3_SELFTEST_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "phase3-selftest:\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py\n",
            "phase3-selftest:\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"unexpected_makefile_command_count:{PHASE3_SELFTEST_TARGET}:2:{PHASE3_SELFTEST_COMMANDS[0]}",
            f"makefile_command_order_drift:{PHASE3_SELFTEST_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"missing_makefile_command:{PHASE2_KCONFIG_TARGET}:{PHASE2_KCONFIG_COMMANDS[0]}",
            f"makefile_command_order_drift:{PHASE2_KCONFIG_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test\n",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"unexpected_makefile_command_count:{PHASE2_KCONFIG_TARGET}:2:{PHASE2_KCONFIG_COMMANDS[2]}",
            f"makefile_command_order_drift:{PHASE2_KCONFIG_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"missing_makefile_command:{PHASE2_CROSS_TARGET}:{PHASE2_CROSS_COMMANDS[0]}",
            f"makefile_command_order_drift:{PHASE2_CROSS_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"unexpected_makefile_command_count:{PHASE2_CROSS_TARGET}:2:{PHASE2_CROSS_COMMANDS[1]}",
            f"makefile_command_order_drift:{PHASE2_CROSS_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"missing_makefile_command:{PHASE4_VALIDATE_TARGET}:{PHASE4_VALIDATE_COMMANDS[-1]}",
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        readme = _baseline_readme().replace(PHASE4_VALIDATE_ROUTE_SNIPPET, "", 1)
        _write(root / README_REL, readme)
        assert validate(root) == [f"missing_readme_snippet:{PHASE4_VALIDATE_ROUTE_SNIPPET}"]
        _write(root / README_REL, _baseline_readme())
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase4-artifact-diff-determinism.py").unlink()
        assert validate(root) == ["missing_repo_file:scripts/zigux/check-phase4-artifact-diff-determinism.py"]
        _write(root / "scripts" / "zigux" / "check-phase4-artifact-diff-determinism.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py").unlink()
        assert validate(root) == ["missing_repo_file:scripts/zigux/check-phase2-toolchain-pin-scope.py"]
        _write(root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "validate-phase2.py").unlink()
        assert validate(root) == ["missing_repo_file:scripts/zigux/validate-phase2.py"]
        _write(root / "scripts" / "zigux" / "validate-phase2.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "validate-phase2-closure.py").unlink()
        assert validate(root) == ["missing_repo_file:scripts/zigux/validate-phase2-closure.py"]
        _write(root / "scripts" / "zigux" / "validate-phase2-closure.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase2-cross.py").unlink()
        assert validate(root) == ["missing_repo_file:scripts/zigux/check-phase2-cross.py"]
        _write(root / "scripts" / "zigux" / "check-phase2-cross.py", "# stub\n")
        case_count += 1

        readme = _baseline_readme().replace(
            "while `make -C zigux phase6-perf` remains the narrow aggregate route for the checksum and hexdump perf packet rather than a bundle-wide Phase 6 perf closure",
            "and there is no `make -C zigux phase6-perf` route on `master`",
            1,
        )
        _write(root / README_REL, readme)
        assert validate(root) == [f"missing_readme_snippet:{REQUIRED_README_SNIPPETS[2]}"]
        _write(root / README_REL, _baseline_readme())
        case_count += 1

        readme = _baseline_readme().replace("`zigux/tests/phase8_help_kallsyms_only_build.zig`, ", "", 1)
        _write(root / README_REL, readme)
        assert validate(root) == [f"missing_readme_snippet:{REQUIRED_README_SNIPPETS[5]}"]
        _write(root / README_REL, _baseline_readme())
        case_count += 1

        readme = _baseline_readme().replace(
            ", and `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, and `make -C zigux phase8-perf-buffer-poll-test` keep the parked libbpf shard trio visible beside the shared owner-map note instead of letting the scripts-root reminder collapse back toward the older starter-only packet.",
            ".",
            1,
        )
        _write(root / README_REL, readme)
        assert validate(root) == [f"missing_readme_snippet:{REQUIRED_README_SNIPPETS[6]}"]
        _write(root / README_REL, _baseline_readme())
        case_count += 1

        readme = _baseline_readme().replace(REQUIRED_README_SNIPPETS[8], "", 1)
        _write(root / README_REL, readme)
        assert validate(root) == [f"missing_readme_snippet:{REQUIRED_README_SNIPPETS[8]}"]
        _write(root / README_REL, _baseline_readme())
        case_count += 1

        readme = _baseline_readme().replace(REQUIRED_README_SNIPPETS[-1], "", 1)
        _write(root / README_REL, readme)
        assert validate(root) == [f"missing_readme_snippet:{REQUIRED_README_SNIPPETS[-1]}"]
        case_count += 1

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    print(f"PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the scripts/zigux README tooling inventory aligned with the shipped repo-tooling packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE3_README_TOOLING_INVENTORY=pass")
    print(f"PHASE3_README_TOOLING_INVENTORY_HELPER_COUNT={len(REQUIRED_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
