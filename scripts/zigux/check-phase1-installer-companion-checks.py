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
    "while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
    "`scripts/zigux/check-phase1-installer-companion-checks.py` remains a focused companion check beside the counted docs-root packet instead of widening the exact marker line that `scripts/zigux/validate-phase1.py` enforces.",
]

DOCS_ROOT_ROUTE_SPLIT_MARKERS = [
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` keep the docs-root companion note split explicit too: the self-test replays the bounded checker logic, while the live route guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line that `scripts/zigux/validate-phase1.py` enforces.",
]

SCRIPTS_README_MARKERS = [
    "- `check-phase1-installer-companion-checks.py`",
]

SCRIPTS_PHASE1_FLOW_MARKERS = [
    "- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the shared owner-map note, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the dedicated installer-companion checker packet, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.",
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

REVIEW_CHECKLIST_PHASE1_BLOCK_START = (
    "  * if the change touches the closed Phase 1 host-tools packet,"
)
REVIEW_CHECKLIST_PHASE1_BLOCK_END = (
    "  * if the change touches the shared Phase 2 toolchain packet,"
)
REVIEW_CHECKLIST_MARKERS = [
    "`scripts/zigux/check-phase1-installer-companion-checks.py`",
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`",
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py`",
]
REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS = [
    "`scripts/zigux/check-phase1-installer-companion-checks.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py`",
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


def extract_bounded_block(text: str, label: str, start_marker: str, end_marker: str) -> tuple[str, list[str]]:
    start_index = text.find(start_marker)
    if start_index == -1:
        return "", [f"{label}:missing_start:{start_marker}"]

    end_index = text.find(end_marker, start_index + len(start_marker))
    if end_index == -1:
        return "", [f"{label}:missing_end:{end_marker}"]

    return text[start_index:end_index], []


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
    missing.extend(
        collect_exact_count_markers(
            docs_root,
            "docs_root_route_split",
            DOCS_ROOT_ROUTE_SPLIT_MARKERS,
        )
    )
    missing.extend(collect_exact_count_markers(scripts_readme, "scripts_readme", SCRIPTS_README_MARKERS))
    missing.extend(
        collect_exact_count_markers(
            scripts_readme,
            "scripts_phase1_flow",
            SCRIPTS_PHASE1_FLOW_MARKERS,
        )
    )
    missing.extend(collect_stripped_line_markers(workflow, "workflow", WORKFLOW_MARKERS))
    missing.extend(collect_exact_count_markers(tests_readme, "tests_readme", TESTS_README_MARKERS))

    review_phase1_block, block_errors = extract_bounded_block(
        review_checklist,
        "review_checklist_phase1_block",
        REVIEW_CHECKLIST_PHASE1_BLOCK_START,
        REVIEW_CHECKLIST_PHASE1_BLOCK_END,
    )
    missing.extend(block_errors)
    if not block_errors:
        missing.extend(
            collect_exact_count_markers(
                review_phase1_block,
                "review_checklist_phase1_block",
                REVIEW_CHECKLIST_MARKERS,
            )
        )
        missing.extend(
            collect_exact_count_markers(
                review_phase1_block,
                "review_checklist_phase1_route_split",
                REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS,
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
        "\n".join(DOCS_ROOT_MARKERS + DOCS_ROOT_ROUTE_SPLIT_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "scripts" / "zigux" / "README.md").write_text(
        "\n".join(SCRIPTS_README_MARKERS + SCRIPTS_PHASE1_FLOW_MARKERS) + "\n",
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
        "\n".join(
            [
                REVIEW_CHECKLIST_PHASE1_BLOCK_START + " " + REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS[0],
                REVIEW_CHECKLIST_PHASE1_BLOCK_END,
            ]
        )
        + "\n",
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
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[0],
                "",
                1,
            )
            + REVIEW_CHECKLIST_MARKERS[0]
            + "\n",
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist_phase1_block:`scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[0],
                REVIEW_CHECKLIST_MARKERS[0] + ", " + REVIEW_CHECKLIST_MARKERS[0],
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist_phase1_block:`scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=2"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_PHASE1_BLOCK_START,
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"review_checklist_phase1_block:missing_start:{REVIEW_CHECKLIST_PHASE1_BLOCK_START}"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_PHASE1_BLOCK_END,
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"review_checklist_phase1_block:missing_end:{REVIEW_CHECKLIST_PHASE1_BLOCK_END}"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS[0],
                REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS[0] + " " + REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS[0],
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"review_checklist_phase1_route_split:{REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS[0]}:expected=1:actual=2"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        (root / "Documentation/zigux/README.md").write_text("", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert (
            "docs_root:while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.:expected=1:actual=0"
            in missing
        )
        assert (
            "docs_root:`scripts/zigux/check-phase1-installer-companion-checks.py` remains a focused companion check beside the counted docs-root packet instead of widening the exact marker line that `scripts/zigux/validate-phase1.py` enforces.:expected=1:actual=0"
            in missing
        )
        assert (
            "docs_root_route_split:`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` keep the docs-root companion note split explicit too: the self-test replays the bounded checker logic, while the live route guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line that `scripts/zigux/validate-phase1.py` enforces.:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(DOCS_ROOT_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "docs_root:while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                DOCS_ROOT_ROUTE_SPLIT_MARKERS[0],
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "docs_root_route_split:`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` keep the docs-root companion note split explicit too: the self-test replays the bounded checker logic, while the live route guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line that `scripts/zigux/validate-phase1.py` enforces.:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        (root / "scripts/zigux/README.md").write_text("", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "scripts_readme:- `check-phase1-installer-companion-checks.py`:expected=1:actual=0" in missing
        assert (
            "scripts_phase1_flow:- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the shared owner-map note, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the dedicated installer-companion checker packet, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                SCRIPTS_PHASE1_FLOW_MARKERS[0] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "scripts_phase1_flow:- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the shared owner-map note, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the dedicated installer-companion checker packet, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.:expected=1:actual=0"
            in missing
        )
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

        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
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
                REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS[0],
                "`scripts/zigux/check-phase1-installer-companion-checks.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist_phase1_route_split:`scripts/zigux/check-phase1-installer-companion-checks.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[1],
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist_phase1_block:`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[0],
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist_phase1_block:`scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=0"
            in missing
        )
        case_count += 1
        make_fixture_root(root)

        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[2],
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            "review_checklist_phase1_block:`python3 scripts/zigux/check-phase1-installer-companion-checks.py`:expected=1:actual=0"
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
        f"{len(MAKEFILE_MARKERS) + len(DOCS_ROOT_MARKERS) + len(DOCS_ROOT_ROUTE_SPLIT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(SCRIPTS_PHASE1_FLOW_MARKERS) + len(WORKFLOW_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_CHECKLIST_ROUTE_SPLIT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
