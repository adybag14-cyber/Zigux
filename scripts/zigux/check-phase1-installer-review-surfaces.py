#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

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

CLOSURE_SHARED_REVIEW_PACKET_START = "## Shared Review Packet"
CLOSURE_SHARED_REVIEW_PACKET_END = "## Find Bit Review Rule"
CLOSURE_SHARED_REVIEW_PACKET_MARKERS = [
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
    (
        "phase1_closure_install_zig_selftest_route",
        "- `python3 scripts/zigux/install-zig.py --self-test`",
        1,
    ),
    (
        "phase1_closure_installer_companion_selftest_route",
        "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`",
        1,
    ),
    (
        "phase1_closure_installer_companion_live_route",
        "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py`",
        1,
    ),
]

CLOSURE_PRESENCE_MARKERS = [
    "- explicit opt-in to Node 24 action execution on GitHub-hosted runners",
    "- no known dependency on the deprecated Node 20 runtime",
    "- Zig installation through an in-repo official-download step instead of a Node 20-bound action",
]

WORKFLOW_MARKERS = [
    ("workflow_phase1_installer_selftest", "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test", 1),
    ("workflow_phase1_installer_check", "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py", 1),
    ("workflow_phase1_installer_companion_selftest", "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test", 1),
    ("workflow_phase1_installer_companion_check", "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py", 1),
]

MAKEFILE_MARKERS = [
    ("makefile_phase1_validate_target", "phase1-validate:", 1),
    ("makefile_phase1_installer_selftest", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test", 1),
    ("makefile_phase1_installer_check", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py", 1),
    ("makefile_phase1_installer_companion_selftest", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test", 1),
    ("makefile_phase1_installer_companion_check", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py", 1),
]

REVIEW_CHECKLIST_PACKET_MARKERS = [
    "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
]

REVIEW_CHECKLIST_PHASE1_BLOCK_START = "  * if the change touches the closed Phase 1 host-tools packet,"
REVIEW_CHECKLIST_PHASE1_BLOCK_END = "  * if the change touches the shared Phase 2 toolchain packet,"
REVIEW_CHECKLIST_PHASE1_ROUTE_MARKERS = [
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`",
    "`scripts/zigux/check-phase1-installer-companion-checks.py`",
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`",
    "`python3 scripts/zigux/check-phase1-installer-companion-checks.py`",
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
    counts: dict[str, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        counts[line] = counts.get(line, 0) + 1

    issues: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = counts.get(marker, 0)
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


def extract_bounded_block(text: str, label: str, start_marker: str, end_marker: str) -> tuple[str, list[str]]:
    start_index = text.find(start_marker)
    if start_index == -1:
        return "", [f"{label}:missing_start:{start_marker}"]
    end_index = text.find(end_marker, start_index + len(start_marker))
    if end_index == -1:
        return "", [f"{label}:missing_end:{end_marker}"]
    return text[start_index:end_index], []


def validate_root(root: Path) -> list[str]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return [f"missing_file:{item}" for item in missing_files]

    docs_root = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    phase1_closure = (root / "Documentation/zigux/phase1-closure.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")

    issues: list[str] = []
    issues.extend(collect_exact_count_markers(docs_root, DOCS_ROOT_MARKERS))
    issues.extend(collect_exact_count_markers(scripts_readme, SCRIPTS_README_MARKERS))
    issues.extend(collect_exact_count_markers(tests_readme, TESTS_README_MARKERS))
    issues.extend(collect_exact_line_count_markers(workflow, WORKFLOW_MARKERS))
    issues.extend(collect_exact_line_count_markers(makefile, MAKEFILE_MARKERS))
    issues.extend(collect_presence_markers(phase1_closure, "phase1_closure_installer_packet", CLOSURE_PRESENCE_MARKERS))
    issues.extend(
        collect_presence_markers(
            review_checklist,
            "review_checklist_phase1_installer_packet",
            REVIEW_CHECKLIST_PACKET_MARKERS,
        )
    )

    closure_packet, closure_errors = extract_bounded_block(
        phase1_closure,
        "phase1_closure_shared_review_packet",
        CLOSURE_SHARED_REVIEW_PACKET_START,
        CLOSURE_SHARED_REVIEW_PACKET_END,
    )
    issues.extend(closure_errors)
    if not closure_errors:
        issues.extend(collect_exact_count_markers(closure_packet, CLOSURE_SHARED_REVIEW_PACKET_MARKERS))

    review_phase1_block, block_errors = extract_bounded_block(
        review_checklist,
        "review_checklist_phase1_block",
        REVIEW_CHECKLIST_PHASE1_BLOCK_START,
        REVIEW_CHECKLIST_PHASE1_BLOCK_END,
    )
    issues.extend(block_errors)
    if not block_errors:
        route_markers = [
            ("review_checklist_phase1_route", marker, 1)
            for marker in REVIEW_CHECKLIST_PHASE1_ROUTE_MARKERS
        ]
        issues.extend(collect_exact_count_markers(review_phase1_block, route_markers))

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
        root / "Documentation/zigux/phase1-closure.md",
        "\n".join(
            [
                *CLOSURE_PRESENCE_MARKERS,
                CLOSURE_SHARED_REVIEW_PACKET_START,
                *(marker for _, marker, _ in CLOSURE_SHARED_REVIEW_PACKET_MARKERS),
                CLOSURE_SHARED_REVIEW_PACKET_END,
            ]
        )
        + "\n",
    )
    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(marker for _, marker, _ in WORKFLOW_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(marker for _, marker, _ in MAKEFILE_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(
            [
                *REVIEW_CHECKLIST_PACKET_MARKERS,
                REVIEW_CHECKLIST_PHASE1_BLOCK_START,
                *REVIEW_CHECKLIST_PHASE1_ROUTE_MARKERS,
                REVIEW_CHECKLIST_PHASE1_BLOCK_END,
            ]
        )
        + "\n",
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

        review_path = root / "Documentation/zigux/review-checklist.md"
        review_text = review_path.read_text(encoding="utf-8")
        write_text(
            review_path,
            review_text.replace("`python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`\n", "", 1),
        )
        expect(validate_root(root), "review_checklist_phase1_route:expected=1:actual=0")
        build_self_test_root(root)

        review_text = review_path.read_text(encoding="utf-8")
        write_text(
            review_path,
            review_text.replace("`python3 scripts/zigux/check-phase1-installer-companion-checks.py`\n", "", 1),
        )
        expect(validate_root(root), "review_checklist_phase1_route:expected=1:actual=0")
        build_self_test_root(root)

        write_text(root / "Documentation/zigux/review-checklist.md", "")
        issues = validate_root(root)
        expect(
            issues,
            "review_checklist_phase1_installer_packet:" + REVIEW_CHECKLIST_PACKET_MARKERS[0] + ":expected>=1:actual=0",
            "review_checklist_phase1_block:missing_start:" + REVIEW_CHECKLIST_PHASE1_BLOCK_START,
        )
        build_self_test_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")
        write_text(
            closure_path,
            closure_text.replace("- `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`\n", "", 1),
        )
        expect(validate_root(root), "phase1_closure_installer_companion_selftest_route:expected=1:actual=0")
        build_self_test_root(root)

        closure_text = closure_path.read_text(encoding="utf-8")
        write_text(
            closure_path,
            closure_text.replace(
                "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py`\n",
                "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py`\n- `python3 scripts/zigux/check-phase1-installer-companion-checks.py`\n",
                1,
            ),
        )
        expect(validate_root(root), "phase1_closure_installer_companion_live_route:expected=1:actual=2")
        build_self_test_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        write_text(
            workflow_path,
            workflow_text.replace("run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test\n", "", 1),
        )
        expect(validate_root(root), "workflow_phase1_installer_companion_selftest:expected=1:actual=0")
        build_self_test_root(root)

        makefile_path = root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8")
        write_text(
            makefile_path,
            makefile_text.replace("cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test\n", "", 1),
        )
        expect(validate_root(root), "makefile_phase1_installer_companion_selftest:expected=1:actual=0")
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
        f"{len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(CLOSURE_SHARED_REVIEW_PACKET_MARKERS) + len(CLOSURE_PRESENCE_MARKERS) + len(WORKFLOW_MARKERS) + len(MAKEFILE_MARKERS) + len(REVIEW_CHECKLIST_PACKET_MARKERS) + len(REVIEW_CHECKLIST_PHASE1_ROUTE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
