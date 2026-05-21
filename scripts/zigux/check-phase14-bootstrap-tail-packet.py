#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
RELEASE_BOUNDARY_PATH = "Documentation/zigux/phase14-release-boundary-survey.md"
ATTACHED_TOOLCHAIN_GUIDANCE_PATH = "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SHARED_SMOKE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-shared-smoke-route.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase14.py"
TESTS_SUMMARY_CHECKER_PATH = "scripts/zigux/check-phase14-tests-readme-smoke-summary.py"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"

REQUIRED_PATHS = (
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SMOKE_SURVEY_PATH,
    RELEASE_BOUNDARY_PATH,
    ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SHARED_SMOKE_ROUTE_CHECKER_PATH,
    VALIDATOR_PATH,
    TESTS_SUMMARY_CHECKER_PATH,
    STUDY_ONLY_ACCOUNTING_PATH,
)

REQUIRED_WORKFLOW_STEPS = (
    "- name: Self-test current Phase 14 shared smoke route checker",
    "- name: Run current Phase 14 validate route",
    "- name: Run current Phase 12 throughput-parity anchor",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "run: make -C zigux phase14-validate",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
)

REQUIRED_MARKERS = {
    MAKEFILE_PATH: (
        "phase14-validate:",
        "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
        "scripts/zigux/check-phase14-shared-smoke-route.py",
        "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
        "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
        "scripts/zigux/validate-phase14.py --self-test",
        "scripts/zigux/validate-phase14.py",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    ),
    DOCS_README_PATH: (
        "while `zigux/Makefile` is current repo evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.",
        "Phase 14 notes",
        "scripts/zigux/validate-phase14.py",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 14 smoke packet",
        "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
        "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json`",
        "keep `make -C zigux phase14-validate` explicit as the current shared-smoke gate",
    ),
    SMOKE_SURVEY_PATH: (
        "`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
        "`scripts/zigux/validate-phase14.py` is directly readable again through the current contents path",
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again too",
        "`make -C zigux phase14-validate` as current rerun guidance",
    ),
    RELEASE_BOUNDARY_PATH: (
        "`scripts/zigux/check-phase14-shared-smoke-route.py` now also directly records that returned route in both the readable Makefile body and the readable bootstrap workflow.",
        "`PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
        "`PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
        "One current direct-readback rerun command is proven from this note: `make -C zigux phase14-validate`.",
    ),
    ATTACHED_TOOLCHAIN_GUIDANCE_PATH: (
        "`scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path",
        "`zigux/tests/README.md` is already aligned with the returned route split",
        "the readable `zigux/Makefile` now exposes `phase14-validate`",
    ),
    SCRIPTS_README_PATH: (
        "## Phase 14",
        "the current scripts-root shared smoke packet stays reviewable",
        "`scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/validate-phase14.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the recoverable shared-smoke layer visible",
        "current `master` does materialize `zigux/Makefile`, and its live body now exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with `phase14-validate`; `phase14-smoke`, `phase14-test`, and `phase14` still do not return",
    ),
    TESTS_README_PATH: (
        "## Phase 14 shared smoke packet",
        "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
        "`scripts/zigux/check-phase14-shared-smoke-route.py`",
        "`scripts/zigux/validate-phase14.py`",
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
        "Current `master` does materialize `zigux/Makefile`",
    ),
    SHARED_SMOKE_ROUTE_CHECKER_PATH: (
        "PHASE14_CHECK_PACKET=shared_smoke_route",
        "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass",
        "run: make -C zigux phase14-validate",
    ),
    VALIDATOR_PATH: (
        "PHASE14_VALIDATION=pass",
        "PHASE14_VALIDATOR_SELF_TEST=pass",
        "PHASE14_CHECK_PACKET=shared_smoke_route",
        "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass",
    ),
    TESTS_SUMMARY_CHECKER_PATH: (
        "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.",
        "PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass",
        "SURVEY_PATH = Path(\"Documentation/zigux/phase14-end-to-end-smoke-survey.md\")",
    ),
    STUDY_ONLY_ACCOUNTING_PATH: (
        "`kernel/workqueue.c` remains a boundary-study target first, not a rewrite target",
        "`kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target",
    ),
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: (
        "phase14-smoke:",
        "phase14-test:",
        "phase14: phase14-validate phase14-smoke phase14-test",
    ),
    WORKFLOW_PATH: (
        "run: make -C zigux phase14-smoke",
        "run: make -C zigux phase14-test",
        "run: make -C zigux phase14",
    ),
}


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_step_index(lines: list[str], marker: str) -> int:
    normalized = marker.strip()
    for index, line in enumerate(lines):
        if line.strip() == normalized:
            return index
    return -1


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    workflow = read_text(root, WORKFLOW_PATH)
    workflow_lines = workflow.splitlines()

    step_indexes: list[int] = []
    for marker in REQUIRED_WORKFLOW_STEPS:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP", f"{marker}:count={count}"))
            continue
        step_indexes.append(find_step_index(workflow_lines, marker))

    if len(step_indexes) == len(REQUIRED_WORKFLOW_STEPS) and step_indexes != sorted(step_indexes):
        issues.append(("MISORDERED_WORKFLOW_STEPS", "phase14 tail packet order changed"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if marker not in text:
                issues.append((f"MISSING_MARKER:{rel}", marker))

    for rel, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if count_exact_lines(text, marker) > 0:
                issues.append((f"FORBIDDEN_MARKER:{rel}", marker))

    return issues


def emit_issues(label: str, issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print(f"{label}=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def fixture_workflow() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 14 shared smoke route checker
        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
      - name: Run current Phase 14 validate route
        run: make -C zigux phase14-validate
      - name: Run current Phase 12 throughput-parity anchor
        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig
"""


def fixture_makefile() -> str:
    return """PYTHON ?= python3
ZIGUX_ROOT := ..

.PHONY: phase12-smoke phase12-test phase12 phase14-validate

phase12-smoke:
\tcd $(ZIGUX_ROOT) && zig build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
\tcd $(ZIGUX_ROOT) && zig build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-smoke phase12-test

phase14-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root, WORKFLOW_PATH, fixture_workflow())
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(
        root,
        DOCS_README_PATH,
        "# Zigux Documentation This directory is the product documentation root for Zigux.\n"
        "Phase 14 notes\n"
        "- scripts/zigux/validate-phase14.py\n"
        "- scripts/zigux/check-phase14-release-boundary-exact-counts.py\n"
        "while `zigux/Makefile` is current repo evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.\n",
    )
    write_text(
        root,
        REVIEW_CHECKLIST_PATH,
        "# Zigux Review Checklist\n"
        "if the change touches the shared Phase 14 smoke packet\n"
        "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`\n"
        "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json`\n"
        "keep `make -C zigux phase14-validate` explicit as the current shared-smoke gate\n",
    )
    write_text(
        root,
        SMOKE_SURVEY_PATH,
        "# Phase 14 End-to-End Smoke Survey\n"
        "`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`\n"
        "`scripts/zigux/validate-phase14.py` is directly readable again through the current contents path\n"
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again too\n"
        "`make -C zigux phase14-validate` as current rerun guidance\n",
    )
    write_text(
        root,
        RELEASE_BOUNDARY_PATH,
        "# Phase 14 Release Boundary Survey\n"
        "`scripts/zigux/check-phase14-shared-smoke-route.py` now also directly records that returned route in both the readable Makefile body and the readable bootstrap workflow.\n"
        "`PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n"
        "`PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`\n"
        "One current direct-readback rerun command is proven from this note: `make -C zigux phase14-validate`.\n",
    )
    write_text(
        root,
        ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
        "# Phase 14 Attached Toolchain Guidance Gap\n"
        "`scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path\n"
        "`zigux/tests/README.md` is already aligned with the returned route split\n"
        "the readable `zigux/Makefile` now exposes `phase14-validate`\n",
    )
    write_text(
        root,
        SCRIPTS_README_PATH,
        "# scripts/zigux\n"
        "## Phase 14\n"
        "the current scripts-root shared smoke packet stays reviewable\n"
        "`scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/validate-phase14.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the recoverable shared-smoke layer visible\n"
        "current `master` does materialize `zigux/Makefile`, and its live body now exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with `phase14-validate`; `phase14-smoke`, `phase14-test`, and `phase14` still do not return\n",
    )
    write_text(
        root,
        TESTS_README_PATH,
        "# zigux/tests\n"
        "## Phase 14 shared smoke packet\n"
        "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`\n"
        "`scripts/zigux/check-phase14-shared-smoke-route.py`\n"
        "`scripts/zigux/validate-phase14.py`\n"
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`\n"
        "Current `master` does materialize `zigux/Makefile`\n",
    )
    write_text(
        root,
        SHARED_SMOKE_ROUTE_CHECKER_PATH,
        "PHASE14_CHECK_PACKET=shared_smoke_route\n"
        "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass\n"
        "run: make -C zigux phase14-validate\n",
    )
    write_text(
        root,
        VALIDATOR_PATH,
        "PHASE14_VALIDATION=pass\n"
        "PHASE14_VALIDATOR_SELF_TEST=pass\n"
        "PHASE14_CHECK_PACKET=shared_smoke_route\n"
        "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass\n",
    )
    write_text(
        root,
        TESTS_SUMMARY_CHECKER_PATH,
        "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.\n"
        "PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass\n"
        "SURVEY_PATH = Path(\"Documentation/zigux/phase14-end-to-end-smoke-survey.md\")\n",
    )
    write_text(
        root,
        STUDY_ONLY_ACCOUNTING_PATH,
        "# Phase 15 Study-Only Anchor Accounting\n"
        "`kernel/workqueue.c` remains a boundary-study target first, not a rewrite target\n"
        "`kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    issues = collect_issues(root)
    if not any(expected_fragment in value or expected_fragment in code for code, value in issues):
        raise AssertionError(f"expected failure containing {expected_fragment!r}, got {issues!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-bootstrap-tail-packet-"))
    try:
        write_fixture_tree(base)
        issues = collect_issues(base)
        if issues:
            print("PHASE14_BOOTSTRAP_TAIL_PACKET_SELF_TEST=fail")
            for code, value in issues:
                print(f"{code}:{value}")
            return 1

        write_fixture_tree(base)
        workflow = read_text(base, WORKFLOW_PATH).replace(
            "- name: Run current Phase 14 validate route\n        run: make -C zigux phase14-validate\n",
            "",
            1,
        )
        write_text(base, WORKFLOW_PATH, workflow)
        expect_failure(base, "MISSING_WORKFLOW_STEP")

        write_fixture_tree(base)
        write_text(
            base,
            WORKFLOW_PATH,
            """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 14 shared smoke route checker
        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
      - name: Run current Phase 12 throughput-parity anchor
        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig
      - name: Run current Phase 14 validate route
        run: make -C zigux phase14-validate
""",
        )
        expect_failure(base, "MISORDERED_WORKFLOW_STEPS")

        write_fixture_tree(base)
        makefile = read_text(base, MAKEFILE_PATH) + "\nphase14-smoke:\n\t@true\n"
        write_text(base, MAKEFILE_PATH, makefile)
        expect_failure(base, "FORBIDDEN_MARKER:zigux/Makefile")

        write_fixture_tree(base)
        docs = read_text(base, DOCS_README_PATH).replace("Phase 14 notes\n", "", 1)
        write_text(base, DOCS_README_PATH, docs)
        expect_failure(base, "MISSING_MARKER:Documentation/zigux/README.md")

        print("PHASE14_BOOTSTRAP_TAIL_PACKET_SELF_TEST=pass")
        print("PHASE14_BOOTSTRAP_TAIL_PACKET_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_fixture_tree(args.write_sample_root)
        print(f"PHASE14_BOOTSTRAP_TAIL_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues("PHASE14_BOOTSTRAP_TAIL_PACKET", issues)

    print("PHASE14_BOOTSTRAP_TAIL_PACKET=pass")
    print(f"PHASE14_BOOTSTRAP_TAIL_PACKET_WORKFLOW_STEP_COUNT={len(REQUIRED_WORKFLOW_STEPS)}")
    print(f"PHASE14_BOOTSTRAP_TAIL_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(
        "PHASE14_BOOTSTRAP_TAIL_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values()) + len(REQUIRED_WORKFLOW_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
