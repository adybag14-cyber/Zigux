#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd().resolve()
README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
README_HELPER_SECTION = "Current bootstrap helpers"

REQUIRED_HELPERS = (
    "check-zig-toolchain.py",
    "validate-bootstrap.py",
    "install-zig.py",
    "validate-phase1.py",
    "check-phase1-bench.py",
    "validate-phase1-closure.py",
    "validate-phase2.py",
    "validate-phase2-closure.py",
    "validate-phase3.py",
    "validate_phase3_selftest.py",
    "check-phase3-selftest-surface.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-bindings-syntax.py",
    "artifact_diff.py",
    "check-artifact-diff-contract.py",
    "validate-phase4.py",
    "check-phase4-gate-evidence.py",
    "check-phase6-shared-surface.py",
    "validate-phase7.py",
    "check-phase7-make-wrapper.py",
    "check-phase7-argv-split-packet.py",
    "check-phase7-rbtree-parity.py",
    "check-phase7-build-wiring.py",
    "validate-phase8.py",
    "check-phase8-exec-cmd-packet.py",
    "check-phase9-build-only-surface.py",
    "check-phase10-core-packet.py",
    "check-phase10-input-packet.py",
    "check-phase10-mmio-packet.py",
    "check-phase11-shared-replay-contract.py",
    "check-phase11-header-boundary-packet.py",
    "check-build-only-phase12-surface.py",
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
    "validate-phase14.py",
    "check-phase14-rollback-threshold-sequencing.py",
    "check-phase14-release-boundary-exact-counts.py",
    "check-phase15-review-process-handoff.py",
    "check-phase15-scripts-readme-alignment.py",
    "run-phase3-checks.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "check-phase1-parity.py",
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

ABSENT_VALIDATE_TARGETS = (
    "phase9-validate",
    "phase12-validate",
)

PHASE3_VALIDATE_TARGET = "phase3-validate"
PHASE3_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
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

PHASE6_VALIDATE_TARGET = "phase6-validate"
PHASE6_VALIDATE_HELPERS = ("check-phase6-shared-surface.py",)

PHASE7_VALIDATE_TARGET = "phase7-validate"
PHASE7_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
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
)
PHASE13_VALIDATE_TARGET = "phase13-validate"
PHASE13_VALIDATE_HELPERS = (
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
)
PHASE15_VALIDATE_TARGET = "phase15-validate"
PHASE15_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
)
REQUIRED_README_SNIPPETS = (
    "- The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-catalog-selftest.py`, `check-phase3-abi-dump-gate.py`, `validate-phase3-policy-unsafe-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-abi-bindings-syntax.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.",
    "- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replays are `make -C zigux phase6-checksum-perf` and `make -C zigux phase6-hexdump-perf`, which keep the checksum slowdown ceiling and the formatter-sensitive hexdump fixture packet wired into Linux-style entrypoints without overstating perf coverage for the rest of the Phase 6 helper packet.",
    "- the current shared Phase 7 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `samples/zigux/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/phase7_build.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "- `make -C zigux phase7-validate` keeps the shared Phase 7 validator plus the dedicated make-wrapper, argvSplit packet, rbtree parity, and build-wiring checkers wired through the Linux-style validation entrypoint.",
    "- the current shared Phase 8 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-exec-cmd-packet.py`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "- `make -C zigux phase8-validate` keeps `validate-phase8.py` plus the focused `check-phase8-exec-cmd-packet.py` checker wired through the Linux-style validation entrypoint before the tooling replays run.",
    "- there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`; future runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate, validation, or review-surface step that keeps those four loader handoffs plus the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` allocator/init-flow contract reviewable without widening into a larger runtime-module implementation.",
    "- `python3 scripts/zigux/check-phase10-core-packet.py` keeps the restored core survey note, core manifest, core survey gate, reset-queue replay, and driver-id replay aligned around that shared review packet, and `python3 scripts/zigux/check-phase10-input-packet.py` keeps the input slice, input module slice, input survey note, build wiring, and status-drain replay markers aligned inside that same bounded Phase 10 route while `zig build test --build-file zigux/tests/phase10_build.zig` and `make -C zigux phase10` rerun the same bounded virtio core, virtio ring, virtio input, and virtio mmio packet.",
    "- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make surfaces until new validator files actually land.",
    "- `make -C zigux phase13-validate` keeps that same release packet wired through the Linux-style validation entrypoint.",
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


def _collect_makefile_target_lines(makefile: str, target: str) -> list[str] | None:
    in_target = False
    lines: list[str] = []
    target_header = f"{target}:"
    for raw in makefile.splitlines():
        stripped = raw.strip()
        if not in_target:
            if stripped == target_header:
                in_target = True
            continue
        if stripped.endswith(":") and not raw.startswith((" ", "\t")):
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


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        readme = _read(root / README_REL)
    except FileNotFoundError:
        return [f"missing_readme:{README_REL}"]
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
    _validate_target_commands(issues, makefile, PHASE3_VALIDATE_TARGET, PHASE3_VALIDATE_COMMANDS)
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
    return issues


def _baseline_readme() -> str:
    helper_lines = "\n".join(f"- `{helper}`" for helper in REQUIRED_HELPERS)
    sections = ["# scripts/zigux", "", README_HELPER_SECTION, helper_lines]
    flow_pairs = (
        ("Phase 3 flow", REQUIRED_README_SNIPPETS[0]),
        ("Phase 6 flow", REQUIRED_README_SNIPPETS[1]),
        ("Phase 7 flow", REQUIRED_README_SNIPPETS[2]),
        ("Phase 7 flow", REQUIRED_README_SNIPPETS[3]),
        ("Phase 8 flow", REQUIRED_README_SNIPPETS[4]),
        ("Phase 8 flow", REQUIRED_README_SNIPPETS[5]),
        ("Phase 9 flow", REQUIRED_README_SNIPPETS[6]),
        ("Phase 10 flow", REQUIRED_README_SNIPPETS[7]),
        ("Phase 12 flow", REQUIRED_README_SNIPPETS[8]),
        ("Phase 13 flow", REQUIRED_README_SNIPPETS[9]),
    )
    for title, snippet in flow_pairs:
        sections.extend(("", title, snippet))
    sections.append("")
    return "\n".join(sections)


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "phase3-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-selftest-surface.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-selftest-surface.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py",
            "",
            "phase3-selftest:",
            "\t@true",
            "",
            "phase3-abi:",
            "\t@true",
            "",
            "phase3-interop:",
            "\t@true",
            "",
            "phase3: phase3-validate phase3-abi phase3-interop",
            "",
            "phase6-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
            "",
            "phase6-test:",
            "\t@true",
            "",
            "phase6: phase6-validate phase6-test",
            "",
            "phase7-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
            "",
            "phase7-test:",
            "\t@true",
            "",
            "phase7: phase7-validate phase7-test",
            "",
            "phase8-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-exec-cmd-packet.py",
            "",
            "phase8-test:",
            "\t@true",
            "",
            "phase8: phase8-validate phase8-test",
            "",
            "phase9-test:",
            "\t@true",
            "",
            "phase9: phase9-test",
            "",
            "phase12-test:",
            "\t@true",
            "",
            "phase12: phase12-test",
            "",
            "phase13-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
            "",
            "phase15-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
            "",
        )
    )


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase3-readme-tooling-inventory-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    baseline_readme = _baseline_readme()
    baseline_makefile = _baseline_makefile()
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        _write(root / README_REL, baseline_readme)
        _write(root / MAKEFILE_REL, baseline_makefile)
        for helper in REQUIRED_HELPERS:
            _write(root / "scripts" / "zigux" / helper, "# stub\n")
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1
        export_uapi_live = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py\n"
        _write(root / MAKEFILE_REL, baseline_makefile.replace(export_uapi_live, "", 1))
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase3-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
                "makefile_command_order_drift:phase3-validate",
            ],
            "missing_phase3_export_uapi_live_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1
        export_uapi_selftest = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n"
        _write(root / MAKEFILE_REL, baseline_makefile.replace(export_uapi_selftest, export_uapi_selftest + export_uapi_selftest, 1))
        _assert_only(
            validate(root),
            [
                "unexpected_makefile_command_count:phase3-validate:2:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
                "makefile_command_order_drift:phase3-validate",
            ],
            "duplicate_phase3_export_uapi_selftest_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1
        abi_dump_live = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py\n"
        _write(root / MAKEFILE_REL, baseline_makefile.replace(abi_dump_live, abi_dump_live + abi_dump_live, 1))
        _assert_only(
            validate(root),
            [
                "unexpected_makefile_command_count:phase3-validate:2:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
                "makefile_command_order_drift:phase3-validate",
            ],
            "duplicate_phase3_abi_dump_gate_live_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1
        catalog_selftest = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test\n"
        _write(root / MAKEFILE_REL, baseline_makefile.replace(catalog_selftest, "", 1))
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase3-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
                "makefile_command_order_drift:phase3-validate",
            ],
            "missing_phase3_catalog_selftest_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1
        for helper in (
            "check-phase3-abi-dump-gate.py",
            "check-phase3-catalog-selftest.py",
            "validate-phase3-export-uapi-survey.py",
            "validate-phase3-abi-bindings-syntax.py",
        ):
            marker = f"- `{helper}`\n"
            _write(root / README_REL, baseline_readme.replace(marker, "", 1))
            _assert_only(
                validate(root),
                [f"missing_readme_helper_entry:{helper}", "readme_helper_order_drift"],
                f"missing_{helper}_readme_guard_failed",
            )
            _write(root / README_REL, baseline_readme)
            case_count += 1
        for helper in (
            "check-phase3-abi-dump-gate.py",
            "check-phase3-catalog-selftest.py",
            "validate-phase3-export-uapi-survey.py",
            "validate-phase3-abi-bindings-syntax.py",
        ):
            path = root / "scripts" / "zigux" / helper
            path.unlink()
            _assert_only(validate(root), [f"missing_repo_file:scripts/zigux/{helper}"], f"missing_{helper}_repo_file_guard_failed")
            _write(path, "# stub\n")
            case_count += 1
        snippet = REQUIRED_README_SNIPPETS[0]
        _write(root / README_REL, baseline_readme.replace(snippet, "", 1))
        _assert_only(validate(root), [f"missing_readme_snippet:{snippet}"], "missing_phase3_support_packet_snippet_guard_failed")
        _write(root / README_REL, baseline_readme)
        case_count += 1
        _write(root / README_REL, baseline_readme.replace(snippet, snippet + "\n" + snippet, 1))
        _assert_only(validate(root), [f"unexpected_readme_snippet_count:2:{snippet}"], "duplicate_phase3_support_packet_snippet_guard_failed")
        _write(root / README_REL, baseline_readme)
        case_count += 1
        _write(
            root / README_REL,
            baseline_readme.replace(
                "- `check-phase3-abi-dump-gate.py`\n",
                "- `check-phase3-abi-dump-gate.py`\n- `check-phase3-abi-dump-gate.py`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["duplicate_readme_helper_entry:check-phase3-abi-dump-gate.py", "readme_helper_order_drift"],
            "duplicate_phase3_abi_dump_gate_helper_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1
        _write(root / MAKEFILE_REL, baseline_makefile + "phase9-validate:\n\t@true\n")
        _assert_only(validate(root), ["unexpected_makefile_target:phase9-validate"], "unexpected_phase9_validate_target_guard_failed")
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase7-make-wrapper.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/check-phase7-make-wrapper.py"], "missing_phase7_make_wrapper_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "check-phase7-make-wrapper.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/check-phase7-argv-split-packet.py"], "missing_phase7_argv_split_packet_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase7-rbtree-parity.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/check-phase7-rbtree-parity.py"], "missing_phase7_rbtree_parity_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "check-phase7-rbtree-parity.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase7-build-wiring.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/check-phase7-build-wiring.py"], "missing_phase7_build_wiring_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "check-phase7-build-wiring.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "validate-phase8.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/validate-phase8.py"], "missing_phase8_validator_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "validate-phase8.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase8-exec-cmd-packet.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/check-phase8-exec-cmd-packet.py"], "missing_phase8_exec_cmd_packet_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "check-phase8-exec-cmd-packet.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "validate-phase13-release.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/validate-phase13-release.py"], "missing_phase13_release_validator_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "validate-phase13-release.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py"],
            "missing_phase2_genksyms_selftest_alignment_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase2-kconfig-selftest-alignment.py"],
            "missing_phase2_kconfig_selftest_alignment_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase2-tests-readme-alignment.py"],
            "missing_phase2_tests_readme_alignment_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase2-cross-selftest-alignment.py"],
            "missing_phase2_cross_selftest_alignment_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase2-toolchain-pin-scope.py"],
            "missing_phase2_toolchain_pin_scope_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase2-cross.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase2-cross.py"],
            "missing_phase2_cross_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase2-cross.py", "# stub\n")
        case_count += 1
        (root / "scripts" / "zigux" / "check-phase13-devres-packet.py").unlink()
        _assert_only(validate(root), ["missing_repo_file:scripts/zigux/check-phase13-devres-packet.py"], "missing_phase13_devres_packet_repo_file_guard_failed")
        _write(root / "scripts" / "zigux" / "check-phase13-devres-packet.py", "# stub\n")
        case_count += 1
        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase7-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
                "makefile_command_order_drift:phase7-validate",
            ],
            "missing_phase7_rbtree_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1
        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase7-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
                "makefile_command_order_drift:phase7-validate",
            ],
            "missing_phase7_build_wiring_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
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
