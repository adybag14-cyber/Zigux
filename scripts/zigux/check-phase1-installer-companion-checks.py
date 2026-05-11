#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/README.md",
]

SCRIPTS_README_MARKERS = [
    "- `check-phase1-installer-companion-checks.py`",
]

WORKFLOW_MARKERS = [
    "- name: Self-test Phase 1 installer companion checks",
    "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
    "- name: Check Phase 1 installer companion checks",
    "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py",
]

TESTS_README_MARKERS = [
    "keep `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
]

REVIEW_CHECKLIST_MARKERS = [
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`",
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return ROOT


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_exact_line_markers(text: str, label: str, markers: list[str]) -> list[str]:
    lines = text.splitlines()
    missing: list[str] = []
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    scripts_readme = (root / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    tests_readme = (root / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(
        encoding="utf-8"
    )

    missing: list[str] = []
    missing.extend(collect_exact_count_markers(scripts_readme, "scripts_readme", SCRIPTS_README_MARKERS))
    missing.extend(collect_exact_line_markers(workflow, "workflow", WORKFLOW_MARKERS))
    missing.extend(collect_exact_count_markers(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(
        collect_exact_count_markers(
            review_checklist,
            "review_checklist",
            REVIEW_CHECKLIST_MARKERS,
        )
    )
    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    (root / "scripts" / "zigux" / "README.md").write_text(
        "\n".join(SCRIPTS_README_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / ".github" / "workflows" / "zigux-bootstrap.yml").write_text(
        "\n".join(WORKFLOW_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "zigux" / "tests" / "README.md").write_text(
        "\n".join(TESTS_README_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "Documentation" / "zigux" / "review-checklist.md").write_text(
        "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    self_test_case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_installer_companion_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)
        assert collect_missing_files(tmp_root) == []
        assert collect_missing_markers(tmp_root) == []

        scripts_readme_path = tmp_root / "scripts" / "zigux" / "README.md"
        scripts_readme_text = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text("", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert (
            "scripts_readme:- `check-phase1-installer-companion-checks.py`:expected=1:actual=0"
            in missing
        )
        self_test_case_count += 1
        scripts_readme_path.write_text(scripts_readme_text, encoding="utf-8")

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text.replace(
                "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(tmp_root)
        assert (
            "workflow:run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test:expected=1:actual=0"
            in missing
        )
        self_test_case_count += 1
        workflow_path.write_text(workflow_text, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux" / "tests" / "README.md"
        tests_readme_path.write_text("", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert (
            "tests_readme:keep `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces:expected=1:actual=0"
            in missing
        )
        self_test_case_count += 1
        tests_readme_path.write_text("\n".join(TESTS_README_MARKERS) + "\n", encoding="utf-8")

        review_checklist_path = tmp_root / "Documentation" / "zigux" / "review-checklist.md"
        review_checklist_text = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist_text.replace("`python3 scripts/zigux/install-zig.py --self-test`\n", ""),
            encoding="utf-8",
        )
        missing = collect_missing_markers(tmp_root)
        assert "review_checklist:`python3 scripts/zigux/install-zig.py --self-test`:expected=1:actual=0" in missing
        self_test_case_count += 1
        review_checklist_path.write_text(review_checklist_text, encoding="utf-8")

    print("PHASE1_INSTALLER_COMPANION_CHECKS_SELF_TEST=pass")
    print(f"PHASE1_INSTALLER_COMPANION_CHECKS_SELF_TEST_CASE_COUNT={self_test_case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 1 installer companion review surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_INSTALLER_COMPANION_CHECKS=fail")
        print("MISSING_PHASE1_INSTALLER_COMPANION_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_INSTALLER_COMPANION_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_INSTALLER_COMPANION_CHECKS=fail")
        print("MISSING_PHASE1_INSTALLER_COMPANION_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_INSTALLER_COMPANION_MARKERS_END")
        return 1

    print("PHASE1_INSTALLER_COMPANION_CHECKS=pass")
    print(f"PHASE1_INSTALLER_COMPANION_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_INSTALLER_COMPANION_REQUIRED_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS) + len(WORKFLOW_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
