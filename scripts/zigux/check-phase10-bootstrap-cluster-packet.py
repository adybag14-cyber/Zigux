#!/usr/bin/env python3
"""Guard the live Phase 10 bootstrap cluster and its shared reminder surfaces."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
CLOSURE_NOTE_PATH = Path("Documentation/zigux/phase10-closure-evidence.md")
ROUTE_CHECKER_PATH = Path("scripts/zigux/check-phase10-bootstrap-route.py")
VALIDATE_PATH = Path("scripts/zigux/validate-phase10.py")
CLOSURE_VALIDATOR_PATH = Path("scripts/zigux/validate-phase10-closure.py")

WORKFLOW_BEFORE_STEP = "Run Phase 8 tooling tests"
WORKFLOW_AFTER_STEP = "Validate current Phase 11 support bundle"
SELF_TEST_STEP = "Self-test current Phase 10 bootstrap route checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test"
CHECK_STEP = "Check current Phase 10 bootstrap route"
CHECK_CMD = "python3 scripts/zigux/check-phase10-bootstrap-route.py"
VALIDATE_STEP = "Validate Phase 10 checker-backed review packet"
VALIDATE_CMD = "make -C zigux phase10-validate"
TEST_STEP = "Run Phase 10 helper tests"
TEST_CMD = "make -C zigux phase10-test"
AGGREGATE_ROUTE = "make -C zigux phase10"
SELF_TEST_RUN_LINE = f"run: {SELF_TEST_CMD}\n"
CHECK_RUN_LINE = f"run: {CHECK_CMD}\n"
VALIDATE_RUN_LINE = f"run: {VALIDATE_CMD}\n"
TEST_RUN_LINE = f"run: {TEST_CMD}\n"

REQUIRED_PATHS = (
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    CLOSURE_NOTE_PATH,
    ROUTE_CHECKER_PATH,
    VALIDATE_PATH,
    CLOSURE_VALIDATOR_PATH,
)

SCRIPTS_README_MARKERS = (
    "## Phase 10",
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/Makefile",
)

TESTS_README_MARKERS = (
    "## Phase 10 shared virtio closure packet",
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
)

CLOSURE_NOTE_MARKERS = (
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "The shared bootstrap-route guard now stays explicit",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
)

MAKEFILE_MARKERS = (
    "phase10-validate:\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-bootstrap-route.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py\n",
    "phase10-test:\n",
    "phase10: phase10-validate phase10-test\n",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"phase10 bootstrap cluster packet missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "phase10 bootstrap cluster packet expected exactly "
            f"{expected} occurrences of {label} {marker!r}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"phase10 bootstrap cluster packet missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "phase10 bootstrap cluster packet expected "
            f"{label} {earlier!r} before {later!r}"
        )


def section_between(text: str, start: str, end: str, label: str) -> str:
    start_index = text.find(start)
    if start_index == -1:
        raise SystemExit(f"phase10 bootstrap cluster packet missing {label} start: {start}")
    end_index = text.find(end, start_index)
    if end_index == -1:
        raise SystemExit(f"phase10 bootstrap cluster packet missing {label} end: {end}")
    return text[start_index:end_index]


def check_workflow(text: str) -> None:
    cluster = section_between(
        text,
        f"- name: {WORKFLOW_BEFORE_STEP}",
        f"- name: {WORKFLOW_AFTER_STEP}",
        "workflow cluster",
    )

    for marker in (SELF_TEST_STEP, CHECK_STEP, VALIDATE_STEP, TEST_STEP):
        require_marker(cluster, marker, "workflow step marker")
        require_exact_count(cluster, marker, 1, "workflow step marker")

    for marker in (SELF_TEST_RUN_LINE, CHECK_RUN_LINE, VALIDATE_RUN_LINE, TEST_RUN_LINE):
        require_marker(cluster, marker, "workflow run line")
        require_exact_count(cluster, marker, 1, "workflow run line")

    require_order(cluster, SELF_TEST_STEP, CHECK_STEP, "workflow step order")
    require_order(cluster, CHECK_STEP, VALIDATE_STEP, "workflow step order")
    require_order(cluster, VALIDATE_STEP, TEST_STEP, "workflow step order")
    require_order(cluster, SELF_TEST_RUN_LINE, CHECK_RUN_LINE, "workflow command order")
    require_order(cluster, CHECK_RUN_LINE, VALIDATE_RUN_LINE, "workflow command order")
    require_order(cluster, VALIDATE_RUN_LINE, TEST_RUN_LINE, "workflow command order")


def check_makefile(text: str) -> None:
    for marker in MAKEFILE_MARKERS:
        require_marker(text, marker, "Makefile marker")
    require_order(text, MAKEFILE_MARKERS[0], MAKEFILE_MARKERS[5], "Makefile target order")
    require_order(text, MAKEFILE_MARKERS[5], MAKEFILE_MARKERS[6], "Makefile target order")
    require_order(text, MAKEFILE_MARKERS[1], MAKEFILE_MARKERS[3], "Makefile command order")
    require_order(text, MAKEFILE_MARKERS[3], MAKEFILE_MARKERS[4], "Makefile command order")


def check_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        require_marker(text, marker, label)


def check_root(root: Path) -> None:
    missing = [str(path) for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        raise SystemExit(
            "phase10 bootstrap cluster packet missing required paths: "
            + ", ".join(missing)
        )

    check_workflow(read_text(root / WORKFLOW_PATH))
    check_makefile(read_text(root / MAKEFILE_PATH))
    check_markers(read_text(root / SCRIPTS_README_PATH), SCRIPTS_README_MARKERS, "scripts README marker")
    check_markers(read_text(root / TESTS_README_PATH), TESTS_README_MARKERS, "tests README marker")
    check_markers(read_text(root / CLOSURE_NOTE_PATH), CLOSURE_NOTE_MARKERS, "closure note marker")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            [
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                f"      - name: {WORKFLOW_BEFORE_STEP}",
                "        run: make -C zigux phase8-test",
                f"      - name: {SELF_TEST_STEP}",
                f"        run: {SELF_TEST_CMD}",
                f"      - name: {CHECK_STEP}",
                f"        run: {CHECK_CMD}",
                f"      - name: {VALIDATE_STEP}",
                f"        run: {VALIDATE_CMD}",
                f"      - name: {TEST_STEP}",
                f"        run: {TEST_CMD}",
                f"      - name: {WORKFLOW_AFTER_STEP}",
                "        run: make -C zigux phase11-validate",
            ]
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE_PATH,
        "".join(MAKEFILE_MARKERS[:-1]) + MAKEFILE_MARKERS[-1],
    )
    write_text(
        root / SCRIPTS_README_PATH,
        "\n".join(
            [
                "# scripts/zigux",
                "## Phase 10",
                *SCRIPTS_README_MARKERS[1:],
                AGGREGATE_ROUTE,
            ]
        )
        + "\n",
    )
    write_text(
        root / TESTS_README_PATH,
        "\n".join(
            [
                "# zigux/tests",
                "## Phase 10 shared virtio closure packet",
                *TESTS_README_MARKERS[1:],
            ]
        )
        + "\n",
    )
    write_text(
        root / CLOSURE_NOTE_PATH,
        "\n".join(
            [
                "# Phase 10 Closure Evidence",
                *CLOSURE_NOTE_MARKERS,
            ]
        )
        + "\n",
    )
    write_text(root / ROUTE_CHECKER_PATH, "print('route checker fixture')\n")
    write_text(root / VALIDATE_PATH, "print('validate fixture')\n")
    write_text(root / CLOSURE_VALIDATOR_PATH, "print('closure validator fixture')\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_bootstrap_cluster_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        check_root(root)

        bad_workflow = read_text(root / WORKFLOW_PATH).replace(
            f"      - name: {CHECK_STEP}\n        run: {CHECK_CMD}\n"
            f"      - name: {VALIDATE_STEP}\n        run: {VALIDATE_CMD}\n",
            f"      - name: {VALIDATE_STEP}\n        run: {VALIDATE_CMD}\n"
            f"      - name: {CHECK_STEP}\n        run: {CHECK_CMD}\n",
            1,
        )
        write_text(root / WORKFLOW_PATH, bad_workflow)
        try:
            check_root(root)
        except SystemExit as exc:
            assert "workflow step order" in str(exc) or "workflow command order" in str(exc)
        else:
            raise AssertionError("expected workflow reorder failure")

        write_sample_root(root)
        bad_makefile = read_text(root / MAKEFILE_PATH).replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py\n",
            "",
            1,
        )
        write_text(root / MAKEFILE_PATH, bad_makefile)
        try:
            check_root(root)
        except SystemExit as exc:
            assert "Makefile marker" in str(exc)
        else:
            raise AssertionError("expected missing Makefile marker failure")

        write_sample_root(root)
        bad_scripts = read_text(root / SCRIPTS_README_PATH).replace(
            "scripts/zigux/validate-phase10.py",
            "scripts/zigux/validate-phase10-missing.py",
            1,
        )
        write_text(root / SCRIPTS_README_PATH, bad_scripts)
        try:
            check_root(root)
        except SystemExit as exc:
            assert "scripts README marker" in str(exc)
        else:
            raise AssertionError("expected scripts README marker failure")

        write_sample_root(root)
        bad_tests = read_text(root / TESTS_README_PATH).replace(
            "make -C zigux phase10-test",
            "make -C zigux phase10-run",
            1,
        )
        write_text(root / TESTS_README_PATH, bad_tests)
        try:
            check_root(root)
        except SystemExit as exc:
            assert "tests README marker" in str(exc)
        else:
            raise AssertionError("expected tests README marker failure")

        write_sample_root(root)
        (root / CLOSURE_VALIDATOR_PATH).unlink()
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing required paths" in str(exc)
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE10_BOOTSTRAP_CLUSTER_PACKET_SELF_TEST=pass")
    print("PHASE10_BOOTSTRAP_CLUSTER_PACKET_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE10_BOOTSTRAP_CLUSTER_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    check_root(root)
    print("PHASE10_BOOTSTRAP_CLUSTER_PACKET=pass")
    print("PHASE10_BOOTSTRAP_CLUSTER_PACKET_WORKFLOW_STEP_COUNT=4")
    print(f"PHASE10_BOOTSTRAP_CLUSTER_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(
        "PHASE10_BOOTSTRAP_CLUSTER_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
