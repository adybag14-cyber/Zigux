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
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "artifact_diff.py",
    "check-artifact-diff-contract.py",
    "validate-phase4.py",
    "check-phase4-gate-evidence.py",
    "check-phase6-shared-surface.py",
    "validate-phase7.py",
    "check-phase7-make-wrapper.py",
    "check-phase7-argv-split-packet.py",
    "check-phase7-rbtree-parity.py",
    "validate-phase8.py",
    "check-phase8-exec-cmd-packet.py",
    "check-phase9-build-only-surface.py",
    "check-phase10-core-packet.py",
    "check-phase10-input-packet.py",
    "check-phase10-mmio-packet.py",
    "check-phase11-shared-replay-contract.py",
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
    "check-genksyms-crc-diff.py",
    "check-kconfig-bridge.py",
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

PHASE6_VALIDATE_TARGET = "phase6-validate"
PHASE6_VALIDATE_HELPERS = ("check-phase6-shared-surface.py",)

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
    "- The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-catalog-selftest.py`, `validate-phase3-policy-unsafe-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.",
    "- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replays are `make -C zigux phase6-checksum-perf` and `make -C zigux phase6-hexdump-perf`, which keep the checksum slowdown ceiling and the formatter-sensitive hexdump fixture packet wired into Linux-style entrypoints without overstating perf coverage for the rest of the Phase 6 helper packet.",
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


def _validate_target_helpers(
    issues: list[str], makefile: str, target: str, required_helpers: tuple[str, ...]
) -> None:
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


def _validate_target_commands(
    issues: list[str], makefile: str, target: str, required_commands: tuple[str, ...]
) -> None:
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

    _validate_target_helpers(issues, makefile, PHASE6_VALIDATE_TARGET, PHASE6_VALIDATE_HELPERS)
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
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "Current bootstrap helpers",
            helper_lines,
            "",
            "Phase 3 flow",
            REQUIRED_README_SNIPPETS[0],
            "",
            "Phase 6 flow",
            REQUIRED_README_SNIPPETS[1],
            "",
            "Phase 9 flow",
            REQUIRED_README_SNIPPETS[2],
            "",
            "Phase 10 flow",
            REQUIRED_README_SNIPPETS[3],
            "",
            "Phase 12 flow",
            REQUIRED_README_SNIPPETS[4],
            "",
            "Phase 13 flow",
            REQUIRED_README_SNIPPETS[5],
            "",
        )
    )


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "phase6-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
            "",
            "phase6-test:",
            "\t@true",
            "",
            "phase6: phase6-validate phase6-test",
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
        if validate(root):
            raise SystemExit("phase3-readme-tooling-inventory-self-test:baseline_failed")
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace("- `check-phase3-catalog-selftest.py`\n", "", 1),
        )
        _assert_only(
            validate(root),
            [
                "missing_readme_helper_entry:check-phase3-catalog-selftest.py",
                "readme_helper_order_drift",
            ],
            "missing_catalog_selftest_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace(
                "- `check-phase3-catalog-selftest.py`\n",
                "- `check-phase3-catalog-selftest.py`\n- `check-phase3-catalog-selftest.py`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "duplicate_readme_helper_entry:check-phase3-catalog-selftest.py",
                "readme_helper_order_drift",
            ],
            "duplicate_catalog_selftest_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace("- `check-phase11-shared-replay-contract.py`\n", "", 1),
        )
        _assert_only(
            validate(root),
            [
                "missing_readme_helper_entry:check-phase11-shared-replay-contract.py",
                "readme_helper_order_drift",
            ],
            "missing_phase11_shared_replay_contract_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace("- `check-phase15-scripts-readme-alignment.py`\n", "", 1),
        )
        _assert_only(
            validate(root),
            [
                "missing_readme_helper_entry:check-phase15-scripts-readme-alignment.py",
                "readme_helper_order_drift",
            ],
            "missing_phase15_scripts_readme_alignment_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace("- `validate-phase7.py`\n", "", 1),
        )
        _assert_only(
            validate(root),
            [
                "missing_readme_helper_entry:validate-phase7.py",
                "readme_helper_order_drift",
            ],
            "missing_phase7_validator_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace("- `validate-phase8.py`\n", "", 1),
        )
        _assert_only(
            validate(root),
            [
                "missing_readme_helper_entry:validate-phase8.py",
                "readme_helper_order_drift",
            ],
            "missing_phase8_validator_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        _write(
            root / README_REL,
            baseline_readme.replace(
                "- `check-mk-elfconfig-diff.py`\n",
                "- `check-mk-elfconfig-diff.py`\n- `unexpected-helper.py`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["unexpected_readme_helper_entry:unexpected-helper.py"],
            "unexpected_helper_entry_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        (root / "scripts" / "zigux" / "validate-phase4.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/validate-phase4.py"],
            "missing_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "validate-phase4.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "validate-phase7.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/validate-phase7.py"],
            "missing_phase7_validator_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "validate-phase7.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase7-make-wrapper.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase7-make-wrapper.py"],
            "missing_phase7_make_wrapper_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase7-make-wrapper.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "validate-phase8.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/validate-phase8.py"],
            "missing_phase8_validator_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "validate-phase8.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase8-exec-cmd-packet.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase8-exec-cmd-packet.py"],
            "missing_phase8_exec_cmd_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase8-exec-cmd-packet.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "validate-phase13-release.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/validate-phase13-release.py"],
            "missing_phase13_release_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "validate-phase13-release.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase15-scripts-readme-alignment.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase15-scripts-readme-alignment.py"],
            "missing_phase15_alignment_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase15-scripts-readme-alignment.py", "# stub\n")
        case_count += 1

        (root / "scripts" / "zigux" / "check-phase10-mmio-packet.py").unlink()
        _assert_only(
            validate(root),
            ["missing_repo_file:scripts/zigux/check-phase10-mmio-packet.py"],
            "missing_phase10_mmio_repo_file_guard_failed",
        )
        _write(root / "scripts" / "zigux" / "check-phase10-mmio-packet.py", "# stub\n")
        case_count += 1

        _write(root / MAKEFILE_REL, baseline_makefile.replace("phase6-validate:\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_makefile_target:phase6-validate"],
            "missing_phase6_validate_target_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_helper:phase6-validate:check-phase6-shared-surface.py",
                "makefile_helper_order_drift:phase6-validate",
            ],
            "missing_phase6_helper_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "unexpected_makefile_helper_count:phase6-validate:check-phase6-shared-surface.py:2",
                "makefile_helper_order_drift:phase6-validate",
            ],
            "duplicate_phase6_helper_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(root / MAKEFILE_REL, baseline_makefile + "phase9-validate:\n\t@true\n")
        _assert_only(
            validate(root),
            ["unexpected_makefile_target:phase9-validate"],
            "unexpected_phase9_validate_target_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(root / MAKEFILE_REL, baseline_makefile + "phase12-validate:\n\t@true\n")
        _assert_only(
            validate(root),
            ["unexpected_makefile_target:phase12-validate"],
            "unexpected_phase12_validate_target_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_helper:phase13-validate:validate-phase13-release.py",
                "missing_makefile_helper:phase13-validate:check-phase13-devres-packet.py",
                "makefile_helper_order_drift:phase13-validate",
            ],
            "missing_phase13_helper_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "unexpected_makefile_helper_count:phase13-validate:validate-phase13-release.py:2",
                "unexpected_makefile_helper_count:phase13-validate:check-phase13-devres-packet.py:2",
                "makefile_helper_order_drift:phase13-validate",
            ],
            "duplicate_phase13_helper_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/unexpected-phase13.py\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["unexpected_makefile_helper:phase13-validate:unexpected-phase13.py"],
            "unexpected_phase13_helper_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase15-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
                "makefile_command_order_drift:phase15-validate",
            ],
            "missing_phase15_alignment_self_test_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "unexpected_makefile_command_count:phase15-validate:2:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
                "makefile_command_order_drift:phase15-validate",
            ],
            "duplicate_phase15_alignment_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase15-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
                "makefile_command_order_drift:phase15-validate",
            ],
            "missing_phase15_self_test_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "unexpected_makefile_command_count:phase15-validate:2:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
                "makefile_command_order_drift:phase15-validate",
            ],
            "duplicate_phase15_self_test_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/unexpected-phase15.py\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_makefile_command:phase15-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
                "unexpected_makefile_command:phase15-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/unexpected-phase15.py",
                "makefile_command_order_drift:phase15-validate",
            ],
            "unexpected_phase15_command_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        missing_snippet = REQUIRED_README_SNIPPETS[3]
        _write(root / README_REL, baseline_readme.replace(missing_snippet, "", 1))
        _assert_only(
            validate(root),
            [f"missing_readme_snippet:{missing_snippet}"],
            "missing_readme_snippet_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        duplicate_snippet = REQUIRED_README_SNIPPETS[4]
        _write(root / README_REL, baseline_readme + duplicate_snippet + "\n")
        _assert_only(
            validate(root),
            [f"unexpected_readme_snippet_count:2:{duplicate_snippet}"],
            "duplicate_readme_snippet_guard_failed",
        )
        case_count += 1

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    print(f"PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the scripts/zigux README tooling inventory aligned with the shipped repo-tooling packet."
    )
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
