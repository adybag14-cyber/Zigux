#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
DOCS_ALIGNMENT_CHECKER_REL = "scripts/zigux/check-phase15-docs-readme-alignment.py"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
SHARED_SUMMARY_CHECKER_REL = "scripts/zigux/check-phase15-shared-summary-gap.py"
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"

REQUIRED_FILES = (
    README_REL,
    MAKEFILE_REL,
    DOCS_ALIGNMENT_CHECKER_REL,
    HANDOFF_CHECKER_REL,
    SHARED_SUMMARY_CHECKER_REL,
    VALIDATOR_REL,
)

README_REQUIRED_MARKERS = (
    "Phase 15 flow",
    "`check-phase15-shared-summary-gap.py` remains the dedicated shared-summary drift guard for the parked Phase 15 governance packet's docs-root, checklist, scripts-root, and tests-root reminder wording, including the no-approval and reopen-trigger maintenance posture that must stay explicit without widening into a freeze-map status change.",
    "`validate-phase15.py` keeps the shared `phase15-validate` route fail-closed on the parked Phase 15 readiness packet and the parity scorecard's machine-reported review-field and aggregate-metric surface before the narrower handoff checkers run.",
    "`make -C zigux phase15-validate` now reruns `validate-phase15.py`, `check-phase15-docs-readme-alignment.py`, `check-phase15-scripts-readme-alignment.py`, `check-phase15-review-process-handoff.py`, and `check-phase15-shared-summary-gap.py` together so the shipped validator-first route covers the broad readiness packet, the docs-root and scripts-root shared-summary guards, and the dedicated parity-scorecard reporting packet before `make -C zigux phase15-test` replays `zigux/tests/phase15_build.zig`.",
)

MAKEFILE_REQUIRED_MARKERS = (
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/validate-phase15.py --self-test",
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-docs-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py --self-test",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    readme = _read(root / README_REL)
    makefile = _read(root / MAKEFILE_REL)

    for marker in README_REQUIRED_MARKERS:
        count = readme.count(marker)
        if count == 0:
            issues.append(f"readme:missing:{marker}")
        elif count != 1:
            issues.append(f"readme:count:{count}:{marker}")

    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile:
            issues.append(f"makefile:missing:{marker}")

    return issues


def _seed_fixture_tree(root: Path) -> None:
    _write(
        root / README_REL,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "Phase 15 flow",
                README_REQUIRED_MARKERS[1],
                README_REQUIRED_MARKERS[2],
                README_REQUIRED_MARKERS[3],
                "",
            )
        ),
    )
    _write(
        root / MAKEFILE_REL,
        "\n".join(
            (
                "PHONY += phase15-validate phase15-test phase15",
                "",
                "phase15-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py",
                "",
                "phase15-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig",
                "",
                "phase15: phase15-validate phase15-test",
                "",
            )
        ),
    )
    for rel in (
        DOCS_ALIGNMENT_CHECKER_REL,
        HANDOFF_CHECKER_REL,
        SHARED_SUMMARY_CHECKER_REL,
        VALIDATOR_REL,
    ):
        _write(root / rel, "# stub\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-scripts-readme-alignment-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_scripts_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        readme_path = root / README_REL
        baseline_readme = _read(readme_path)

        missing_guard = README_REQUIRED_MARKERS[1]
        _write(readme_path, baseline_readme.replace(missing_guard + "\n", "", 1))
        _assert_only(validate(root), [f"readme:missing:{missing_guard}"], "missing_shared_summary_guard")
        _write(readme_path, baseline_readme)
        case_count += 1

        old_route = "`make -C zigux phase15-validate` now reruns `validate-phase15.py`, `check-phase15-scripts-readme-alignment.py`, and `check-phase15-review-process-handoff.py` together so the shipped validator-first route covers both the broad readiness packet and the dedicated parity-scorecard reporting packet before `make -C zigux phase15-test` replays `zigux/tests/phase15_build.zig`."
        _write(readme_path, baseline_readme.replace(README_REQUIRED_MARKERS[3], old_route, 1))
        _assert_only(validate(root), [f"readme:missing:{README_REQUIRED_MARKERS[3]}"], "old_route_undercount")
        _write(readme_path, baseline_readme)
        case_count += 1

        duplicate_guard = baseline_readme + README_REQUIRED_MARKERS[1] + "\n"
        _write(readme_path, duplicate_guard)
        _assert_only(validate(root), [f"readme:count:2:{README_REQUIRED_MARKERS[1]}"], "duplicate_shared_summary_guard")
        _write(readme_path, baseline_readme)
        case_count += 1

        makefile_path = root / MAKEFILE_REL
        baseline_makefile = _read(makefile_path)
        _write(
            makefile_path,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py --self-test\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["makefile:missing:scripts/zigux/check-phase15-docs-readme-alignment.py --self-test"],
            "missing_docs_checker_self_test",
        )
        _write(makefile_path, baseline_makefile)
        case_count += 1

        _write(
            makefile_path,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py --self-test\n",
                "",
                1,
            ).replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "makefile:missing:scripts/zigux/check-phase15-shared-summary-gap.py --self-test",
                "makefile:missing:scripts/zigux/check-phase15-shared-summary-gap.py",
            ],
            "missing_shared_summary_checker",
        )
        _write(makefile_path, baseline_makefile)
        case_count += 1

        _write(makefile_path, baseline_makefile.replace("phase15: phase15-validate phase15-test", "phase15:", 1))
        _assert_only(
            validate(root),
            ["makefile:missing:phase15: phase15-validate phase15-test"],
            "missing_phase15_aggregate_route",
        )
        _write(makefile_path, baseline_makefile)
        case_count += 1

        (root / SHARED_SUMMARY_CHECKER_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{SHARED_SUMMARY_CHECKER_REL}"],
            "missing_shared_summary_checker_file",
        )
        _seed_fixture_tree(root)
        case_count += 1

    print("PHASE15_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the scripts-root Phase 15 governance packet aligned with the shipped phase15-validate route."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_SCRIPTS_README_ALIGNMENT=fail")
        print("PHASE15_SCRIPTS_README_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_SCRIPTS_README_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    print(
        "PHASE15_SCRIPTS_README_ALIGNMENT_MARKER_COUNT="
        f"{len(README_REQUIRED_MARKERS) + len(MAKEFILE_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
