#!/usr/bin/env python3
"""Check the current Phase 6 bootstrap helper packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase6.py")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")

PREV_STEP = "Check current Phase 4 artifact-diff validator replay packet"
VALIDATE_STEP = "Validate current Phase 6 helper packet"
TEST_STEP = "Run current Phase 6 leaf helper tests"
PERF_STEP = "Run current Phase 6 shared perf route"
NEXT_STEP = "Validate Phase 8 tooling routes"

VALIDATE_CMD = "make -C zigux phase6-validate"
TEST_CMD = "zig build test --build-file zigux/tests/phase6_build.zig --summary all"
PERF_CMD = "make -C zigux phase6-perf"

WORKFLOW_MARKERS = (
    PREV_STEP,
    VALIDATE_STEP,
    TEST_STEP,
    PERF_STEP,
    NEXT_STEP,
    VALIDATE_CMD,
    TEST_CMD,
    PERF_CMD,
)

VALIDATOR_MARKERS = (
    'HELPER_EVIDENCE_CATALOG = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")',
    'PHASE6_BUILD = Path("zigux/tests/phase6_build.zig")',
    'MAKEFILE = Path("zigux/Makefile")',
    'HEXDUMP_ROUTE_CHECKER = Path("scripts/zigux/check-phase6-hexdump-route.py")',
    '(HEXDUMP_ROUTE_CHECKER, "--root"),',
    'EXPECTED_SHARED_PERF_WRAPPER = "make -C zigux phase6-perf"',
    '"make -C zigux phase6-perf",',
    'print("PHASE6_VALIDATION=pass")',
)

MAKEFILE_MARKERS = (
    "phase6-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase6.py",
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
)

BUILD_MARKERS = (
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    'const test_step = b.step("test", "Run Phase 6 helper tests");',
)

DOCS_README_MARKERS = (
    "Phase 6 notes - `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "`scripts/zigux/check-phase6-shared-surface.py`",
    "`zigux/tests/phase6_build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase6-validate`",
    "`make -C zigux phase6`",
)

SCRIPTS_README_MARKERS = (
    "- Phase 6 flow - the current shared helper-evidence packet keeps the bounded base64, bsearch, checksum, and hexdump lane truthful from the scripts root without widening into new helper semantics",
    "`python3 scripts/zigux/check-phase6-shared-surface.py --self-test`",
    "`python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test`",
    "`make -C zigux phase6-perf`",
)

TESTS_README_MARKERS = (
    "## Phase 6 leaf-helper packet",
    "`scripts/zigux/check-phase6-shared-surface.py`",
    "`zigux/tests/phase6_build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase6-validate`",
    "`make -C zigux phase6`",
)

CATALOG_MARKERS = (
    "- shared Makefile wrapper surface: `zigux/Makefile`",
    "- `make -C zigux phase6-perf`",
    "- `make -C zigux phase6-hexdump-review`",
    "- `make -C zigux phase6-hexdump-perf`",
    "- `validate-phase6.py`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase6 bootstrap helper packet checker missing required file: {path.as_posix()}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_marker(text: str, marker: str, label: str, path: Path) -> None:
    if marker not in text:
        raise SystemExit(
            f"phase6 bootstrap helper packet checker missing {label} in {path.as_posix()}: {marker}"
        )


def require_exact_count(text: str, marker: str, expected: int, label: str, path: Path) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "phase6 bootstrap helper packet checker expected exactly "
            f"{expected} occurrences of {label} in {path.as_posix()}: {marker}; found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str, path: Path) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"phase6 bootstrap helper packet checker missing ordered {label} markers in {path.as_posix()}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "phase6 bootstrap helper packet checker expected "
            f"{label} order in {path.as_posix()}: `{earlier}` before `{later}`"
        )


def section_between(text: str, start: str, end: str, path: Path) -> str:
    start_index = text.find(start)
    if start_index == -1:
        raise SystemExit(
            f"phase6 bootstrap helper packet checker missing workflow boundary start in {path.as_posix()}: {start}"
        )
    end_index = text.find(end, start_index)
    if end_index == -1:
        raise SystemExit(
            f"phase6 bootstrap helper packet checker missing workflow boundary end in {path.as_posix()}: {end}"
        )
    return text[start_index:end_index]


def check_workflow(path: Path, text: str) -> None:
    for marker in WORKFLOW_MARKERS:
        require_marker(text, marker, "workflow marker", path)

    for marker in (VALIDATE_STEP, TEST_STEP, PERF_STEP, VALIDATE_CMD, TEST_CMD, PERF_CMD):
        require_exact_count(text, marker, 1, "workflow packet marker", path)

    require_order(text, PREV_STEP, VALIDATE_STEP, "workflow packet", path)
    require_order(text, VALIDATE_STEP, TEST_STEP, "workflow packet", path)
    require_order(text, TEST_STEP, PERF_STEP, "workflow packet", path)
    require_order(text, PERF_STEP, NEXT_STEP, "workflow packet", path)
    require_order(text, VALIDATE_CMD, TEST_CMD, "workflow packet command", path)
    require_order(text, TEST_CMD, PERF_CMD, "workflow packet command", path)

    packet = section_between(text, PREV_STEP, NEXT_STEP, path)
    for marker in (VALIDATE_STEP, TEST_STEP, PERF_STEP, VALIDATE_CMD, TEST_CMD, PERF_CMD):
        require_marker(packet, marker, "workflow packet member", path)


def check_markers(path: Path, markers: tuple[str, ...], label: str) -> None:
    text = read_text(path)
    for marker in markers:
        require_marker(text, marker, label, path)


def check_repo(root: Path) -> None:
    workflow_path = root / WORKFLOW_PATH
    check_workflow(workflow_path, read_text(workflow_path))
    check_markers(root / VALIDATOR_PATH, VALIDATOR_MARKERS, "validator marker")
    check_markers(root / MAKEFILE_PATH, MAKEFILE_MARKERS, "Makefile marker")
    check_markers(root / BUILD_PATH, BUILD_MARKERS, "build marker")
    check_markers(root / DOCS_README_PATH, DOCS_README_MARKERS, "docs README marker")
    check_markers(root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README marker")
    check_markers(root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README marker")
    check_markers(root / CATALOG_PATH, CATALOG_MARKERS, "helper-evidence catalog marker")


def scaffold_current_like_root(root: Path) -> None:
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                f"      - name: {PREV_STEP}",
                "        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
                f"      - name: {VALIDATE_STEP}",
                f"        run: {VALIDATE_CMD}",
                f"      - name: {TEST_STEP}",
                f"        run: {TEST_CMD}",
                f"      - name: {PERF_STEP}",
                f"        run: {PERF_CMD}",
                f"      - name: {NEXT_STEP}",
                "        run: make -C zigux phase8-validate",
                "",
            )
        ),
    )
    write_text(root / VALIDATOR_PATH, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / BUILD_PATH, "\n".join(BUILD_MARKERS) + "\n")
    write_text(root / DOCS_README_PATH, "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(
        root / TESTS_README_PATH,
        "\n".join(
            (
                "# zigux/tests",
                *TESTS_README_MARKERS,
                "",
            )
        ),
    )
    write_text(root / CATALOG_PATH, "\n".join(CATALOG_MARKERS) + "\n")


def expect_failure(root: Path, path: Path, marker: str) -> None:
    original = read_text(path)
    if marker not in original:
        raise AssertionError(f"self-test marker not found: {marker}")
    write_text(path, original.replace(marker, "", 1))
    try:
        check_repo(root)
    except SystemExit as exc:
        if marker not in str(exc):
            raise AssertionError(f"expected marker {marker!r} in failure, got {exc!s}") from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        write_text(path, original)


def run_self_test() -> int:
    import tempfile

    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_bootstrap_helper_packet_") as tmp_dir:
        root = Path(tmp_dir)
        scaffold_current_like_root(root)
        check_repo(root)

        for path, marker in (
            (root / WORKFLOW_PATH, VALIDATE_STEP),
            (root / WORKFLOW_PATH, TEST_CMD),
            (root / WORKFLOW_PATH, NEXT_STEP),
            (root / VALIDATOR_PATH, VALIDATOR_MARKERS[6]),
            (root / MAKEFILE_PATH, MAKEFILE_MARKERS[7]),
            (root / BUILD_PATH, BUILD_MARKERS[4]),
            (root / DOCS_README_PATH, DOCS_README_MARKERS[4]),
            (root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS[3]),
            (root / TESTS_README_PATH, TESTS_README_MARKERS[5]),
            (root / CATALOG_PATH, CATALOG_MARKERS[1]),
        ):
            expect_failure(root, path, marker)
            cases_run += 1

        workflow_path = root / WORKFLOW_PATH
        original = read_text(workflow_path)
        reordered = original.replace(
            f"      - name: {VALIDATE_STEP}\n        run: {VALIDATE_CMD}\n"
            f"      - name: {TEST_STEP}\n        run: {TEST_CMD}\n",
            f"      - name: {TEST_STEP}\n        run: {TEST_CMD}\n"
            f"      - name: {VALIDATE_STEP}\n        run: {VALIDATE_CMD}\n",
            1,
        )
        write_text(workflow_path, reordered)
        try:
            check_repo(root)
        except SystemExit as exc:
            if "workflow packet" not in str(exc) and "workflow packet command" not in str(exc):
                raise AssertionError(f"expected packet-order failure, got {exc!s}") from exc
        else:
            raise AssertionError("expected reordered workflow failure")
        finally:
            write_text(workflow_path, original)
        cases_run += 1

    print("PHASE6_BOOTSTRAP_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE6_BOOTSTRAP_HELPER_PACKET_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="write a current-like sample root to this path and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        scaffold_current_like_root(args.write_sample_root)
        return 0

    check_repo(args.root.resolve())
    print("PHASE6_BOOTSTRAP_HELPER_PACKET=pass")
    print("PHASE6_BOOTSTRAP_HELPER_PACKET_WORKFLOW_STEP_COUNT=3")
    print("PHASE6_BOOTSTRAP_HELPER_PACKET_REQUIRED_PATH_COUNT=7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
