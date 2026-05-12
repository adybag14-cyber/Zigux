#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

REQUIRED_FILES = [
    "zigux/Makefile",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/README.md",
    "Documentation/zigux/review-checklist.md",
]

DOCS_ROOT_MARKERS = [
    "`scripts/zigux/check-phase1-installer-companion-checks.py` remains a focused companion check beside the counted docs-root packet instead of widening the exact marker line that `scripts/zigux/validate-phase1.py` enforces.",
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
    "keep `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
]

REVIEW_CHECKLIST_MARKERS = [
    "`scripts/zigux/check-phase1-installer-companion-checks.py`",
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`",
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py`",
]

MAKEFILE_MARKERS = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py",
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_stripped_line_markers(text: str, label: str, markers: list[str]) -> list[str]:
    lines = text.splitlines()
    missing: list[str] = []
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    makefile = (root / "zigux" / "Makefile").read_text(encoding="utf-8")
    docs_root = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    tests_readme = (root / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(
        encoding="utf-8"
    )

    missing: list[str] = []
    missing.extend(collect_stripped_line_markers(makefile, "makefile", MAKEFILE_MARKERS))
    missing.extend(collect_exact_count_markers(docs_root, "docs_root", DOCS_ROOT_MARKERS))
    missing.extend(collect_exact_count_markers(scripts_readme, "scripts_readme", SCRIPTS_README_MARKERS))
    missing.extend(collect_stripped_line_markers(workflow, "workflow", WORKFLOW_MARKERS))
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

    (root / "zigux" / "Makefile").write_text(
        "\n".join(MAKEFILE_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "Documentation" / "zigux" / "README.md").write_text(
        "\n".join(DOCS_ROOT_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "scripts" / "zigux" / "README.md").write_text(
        "\n".join(SCRIPTS_README_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / ".github" / "workflows" / "zigux-bootstrap.yml").write_text(
        "\n".join(
            [
                "      - name: Self-test Phase 1 installer companion checks",
                "        run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
                "      - name: Check Phase 1 installer companion checks",
                "        run: python3 scripts/zigux/check-phase1-installer-companion-checks.py",
            ]
        )
        + "\n",
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
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_installer_companion_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        docs_root_path = root / "Documentation/zigux/README.md"
        docs_root_path.unlink()
        assert collect_missing_files(root) == ["Documentation/zigux/README.md"]
        case_count += 1
        make_fixture_root(root)

        review_path = root / "Documentation/zigux/review-checklist.md"
        review_path.write_text(
            review_path.read_text(encoding="utf-8") + REVIEW_CHECKLIST_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist:`scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=2"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        (root / "Documentation/zigux/README.md").write_text("", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert (
            "docs_root:`scripts/zigux/check-phase1-installer-companion-checks.py` remains a focused companion check beside the counted docs-root packet instead of widening the exact marker line that `scripts/zigux/validate-phase1.py` enforces.:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        (root / "scripts/zigux/README.md").write_text("", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "scripts_readme:- `check-phase1-installer-companion-checks.py`:expected=1:actual=0" in missing
        case_count += 1
        make_fixture_root(root)

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "makefile:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "workflow:run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        (root / "zigux/tests/README.md").write_text("", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert (
            "tests_readme:keep `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                "`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist:`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase1-installer-companion-checks.py`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist:`scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                "`python3 scripts/zigux/check-phase1-installer-companion-checks.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist:`python3 scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=0"
            in missing
        )
        case_count += 1

    print("PHASE1_INSTALLER_COMPANION_CHECKS_SELF_TEST=pass")
    print(f"PHASE1_INSTALLER_COMPANION_CHECKS_SELF_TEST_CASE_COUNT={case_count}")


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
        f"{len(MAKEFILE_MARKERS) + len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(WORKFLOW_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
