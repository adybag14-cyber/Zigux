#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-installer-companion-checks.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

DOCS_ROOT_MARKERS = [
    (
        "docs_root_phase1_installer_packet",
        "- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
        1,
    ),
]

SCRIPTS_README_MARKERS = [
    (
        "scripts_readme_phase1_installer_packet",
        "- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the shared owner-map note, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the dedicated installer-companion checker packet, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.",
        1,
    ),
]

TESTS_README_MARKERS = [
    (
        "tests_readme_phase1_installer_packet",
        "  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
        1,
    ),
    (
        "tests_readme_phase1_installer_companion_checks",
        "  * keep `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
        1,
    ),
]

REVIEW_CHECKLIST_MARKERS = [
    "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
]

CLOSURE_MARKERS = [
    "- `scripts/zigux/install-zig.py`",
    "- `python3 scripts/zigux/install-zig.py --self-test`",
    "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`",
    "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py`",
    "- explicit opt-in to Node 24 action execution on GitHub-hosted runners",
    "- no known dependency on the deprecated Node 20 runtime",
    "- Zig installation through an in-repo official-download step instead of a Node 20-bound action",
]

CLOSURE_EXACT_MARKERS = [
    (
        "phase1_closure_installer_checker_anchor",
        "- `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        1,
    ),
    (
        "phase1_closure_installer_companion_checker_anchor",
        "- `scripts/zigux/check-phase1-installer-companion-checks.py`",
        1,
    ),
]

WORKFLOW_MARKERS = [
    (
        "workflow_phase1_installer_selftest",
        "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
        1,
    ),
    (
        "workflow_phase1_installer_check",
        "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py",
        1,
    ),
]

MAKEFILE_MARKERS = [
    ("makefile_phase1_validate_target", "phase1-validate:", 1),
    (
        "makefile_phase1_installer_selftest",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
        1,
    ),
    (
        "makefile_phase1_installer_check",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py",
        1,
    ),
]


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    issues: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            issues.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return issues


def collect_exact_line_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    actual_counts: dict[str, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        actual_counts[line] = actual_counts.get(line, 0) + 1

    issues: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = actual_counts.get(marker, 0)
        if actual_count != expected_count:
            issues.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return issues


def collect_presence_markers(text: str, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        actual_count = text.count(marker)
        if actual_count < 1:
            issues.append(f"{label}:{marker}:expected>=1:actual={actual_count}")
    return issues


def validate_root(root: Path) -> list[str]:
    issues = collect_missing_files(root)
    if issues:
        return [f"missing_file:{item}" for item in issues]

    docs_root = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    phase1_closure = (root / "Documentation/zigux/phase1-closure.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")

    issues = []
    issues.extend(collect_exact_count_markers(docs_root, DOCS_ROOT_MARKERS))
    issues.extend(collect_exact_count_markers(scripts_readme, SCRIPTS_README_MARKERS))
    issues.extend(collect_exact_count_markers(tests_readme, TESTS_README_MARKERS))
    issues.extend(collect_exact_count_markers(phase1_closure, CLOSURE_EXACT_MARKERS))
    issues.extend(collect_exact_line_count_markers(workflow, WORKFLOW_MARKERS))
    issues.extend(collect_exact_line_count_markers(makefile, MAKEFILE_MARKERS))
    issues.extend(
        collect_presence_markers(
            review_checklist,
            "review_checklist_phase1_installer_packet",
            REVIEW_CHECKLIST_MARKERS,
        )
    )
    issues.extend(
        collect_presence_markers(
            phase1_closure,
            "phase1_closure_installer_packet",
            CLOSURE_MARKERS,
        )
    )
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "// fixture\n")

    write_text(
        root / "Documentation/zigux/README.md",
        "\n".join(marker for _, marker, _ in DOCS_ROOT_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/README.md",
        "\n".join(marker for _, marker, _ in SCRIPTS_README_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/tests/README.md",
        "\n".join(marker for _, marker, _ in TESTS_README_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase1-closure.md",
        "\n".join([marker for _, marker, _ in CLOSURE_EXACT_MARKERS] + CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(marker for _, marker, _ in WORKFLOW_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(marker for _, marker, _ in MAKEFILE_MARKERS) + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    def expect(issues: list[str], *expected: str) -> None:
        nonlocal case_count
        for item in expected:
            assert item in issues
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1_installer_review_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        write_text(root / "Documentation/zigux/README.md", "")
        expect(validate_root(root), "docs_root_phase1_installer_packet:expected=1:actual=0")
        build_self_test_root(root)

        write_text(root / "scripts/zigux/README.md", "")
        expect(validate_root(root), "scripts_readme_phase1_installer_packet:expected=1:actual=0")
        build_self_test_root(root)

        write_text(root / "zigux/tests/README.md", "")
        expect(
            validate_root(root),
            "tests_readme_phase1_installer_packet:expected=1:actual=0",
            "tests_readme_phase1_installer_companion_checks:expected=1:actual=0",
        )
        build_self_test_root(root)

        write_text(root / "Documentation/zigux/review-checklist.md", "")
        expect(
            validate_root(root),
            "review_checklist_phase1_installer_packet:" + REVIEW_CHECKLIST_MARKERS[0] + ":expected>=1:actual=0",
        )
        build_self_test_root(root)

        write_text(root / "Documentation/zigux/phase1-closure.md", "")
        expect(
            validate_root(root),
            "phase1_closure_installer_checker_anchor:expected=1:actual=0",
            "phase1_closure_installer_companion_checker_anchor:expected=1:actual=0",
            "phase1_closure_installer_packet:- `scripts/zigux/install-zig.py`:expected>=1:actual=0",
        )
        build_self_test_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")
        write_text(
            closure_path,
            closure_text.replace("- `scripts/zigux/check-phase1-installer-companion-checks.py`\n", "", 1),
        )
        expect(
            validate_root(root),
            "phase1_closure_installer_companion_checker_anchor:expected=1:actual=0",
        )
        build_self_test_root(root)

        closure_text = closure_path.read_text(encoding="utf-8")
        write_text(
            closure_path,
            closure_text.replace(
                "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`\n",
                "",
                1,
            ),
        )
        expect(
            validate_root(root),
            "phase1_closure_installer_packet:- `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`:expected>=1:actual=0",
        )
        build_self_test_root(root)

        write_text(root / ".github/workflows/zigux-bootstrap.yml", "")
        expect(
            validate_root(root),
            "workflow_phase1_installer_selftest:expected=1:actual=0",
            "workflow_phase1_installer_check:expected=1:actual=0",
        )
        build_self_test_root(root)

        write_text(root / "zigux/Makefile", "")
        expect(
            validate_root(root),
            "makefile_phase1_validate_target:expected=1:actual=0",
            "makefile_phase1_installer_selftest:expected=1:actual=0",
            "makefile_phase1_installer_check:expected=1:actual=0",
        )
        build_self_test_root(root)

        (root / "Documentation/zigux/review-checklist.md").unlink()
        expect(validate_root(root), "missing_file:Documentation/zigux/review-checklist.md")
        build_self_test_root(root)

        (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").unlink()
        expect(validate_root(root), "missing_file:Documentation/zigux/phase1-host-helper-lane-sequencing.md")
        build_self_test_root(root)

        (root / "scripts/zigux/check-phase1-installer-companion-checks.py").unlink()
        expect(validate_root(root), "missing_file:scripts/zigux/check-phase1-installer-companion-checks.py")

    print("PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass")
    print(f"PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 1 installer-backed review surfaces stay aligned."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in alignment coverage without a repo checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE1_INSTALLER_REVIEW_SURFACES=fail")
        print("PHASE1_INSTALLER_REVIEW_SURFACES_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_INSTALLER_REVIEW_SURFACES_ISSUES_END")
        return 1

    print("PHASE1_INSTALLER_REVIEW_SURFACES=pass")
    print(
        "PHASE1_INSTALLER_REVIEW_SURFACES_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(CLOSURE_MARKERS) + len(CLOSURE_EXACT_MARKERS) + len(WORKFLOW_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
