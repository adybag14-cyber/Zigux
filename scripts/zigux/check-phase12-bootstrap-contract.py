#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
NOTE_PATH = "Documentation/zigux/phase12-bootstrap-lane-contract.md"

NOTE_MARKERS = [
    "`PHASE12_BOOTSTRAP_LANE=active`",
    "lane owner: `Lane 05`",
    "workflow anchor: `.github/workflows/zigux-bootstrap.yml`",
    "checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`",
    "the current bootstrap workflow still begins with `Compile current scripts`",
    "the current Phase 12 slice sits after the current Zig toolchain, Phase 2, Phase 1, Phase 4, Phase 7, Phase 10, and Phase 11 packets",
    "the current Phase 12 bootstrap segment reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all` are current bootstrap-lane evidence on `master`",
    "the current bootstrap tail still ends with `make -C zigux phase8-validate`, `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, and `Check current docs-root sanity markers`",
    "the shipped docs guard is still the inline `Check current docs-root sanity markers` step from `.github/workflows/zigux-bootstrap.yml`",
    "`Check current Phase 12 build-only surface`, `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` belong to the active Lane 05 workflow review branch, not current `master`",
]

REQUIRED_STEP_ORDER = [
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy packet",
    "Check current pinned Zig archive packet",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 kconfig bridge packet",
    "Self-test current Phase 2 kbuild routes checker",
    "Check current Phase 2 kbuild packet",
    "Self-test current Phase 2 tests README checker",
    "Check current Phase 2 tests README packet",
    "Self-test current Phase 2 cross selftest alignment checker",
    "Check current Phase 2 cross alignment packet",
    "Self-test current Phase 2 toolchain pinning checker",
    "Check current Phase 2 toolchain pinning packet",
    "Self-test current Phase 2 toolchain pin-scope checker",
    "Check current Phase 2 toolchain pin-scope packet",
    "Self-test current Phase 2 required make-routes checker",
    "Check current Phase 2 required make routes",
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
    "Self-test current Phase 4 reversible-delivery pin checker",
    "Check current Phase 4 reversible-delivery pin packet",
    "Self-test current Phase 4 tests README checker",
    "Check current Phase 4 tests README packet",
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 shared-control gap packet",
    "Self-test current Phase 10 bootstrap route checker",
    "Check current Phase 10 bootstrap route",
    "Validate Phase 10 checker-backed review packet",
    "Run Phase 10 helper tests",
    "Self-test current Phase 11 HVC cleanup current-head checker",
    "Check current Phase 11 HVC cleanup current-head packet",
    "Self-test current Phase 11 build inventory checker",
    "Check current Phase 11 build inventory packet",
    "Self-test current Phase 11 matrix-gap survey checker",
    "Check current Phase 11 matrix-gap survey packet",
    "Self-test current Phase 12 build-only surface checker",
    "Check current Phase 12 build-only surface",
    "Self-test current Phase 12 release-readiness packet checker",
    "Validate Phase 12 degraded-workflow bundle",
    "Check current Phase 12 release-readiness packet",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
    "Validate Phase 8 tooling gates",
    "Run focused Phase 8 libbpf segment survey tests",
    "Check current docs-root sanity markers",
]

WORKFLOW_REQUIRED_MARKERS = [
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "make -C zigux phase12-validate",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "make -C zigux phase12-smoke",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase8-validate",
    "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "scripts/zigux/check-phase12-bootstrap-lane-shape.py",
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / WORKFLOW_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.exists():
        raise FileNotFoundError(rel_path)
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [WORKFLOW_PATH, NOTE_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    note_text = read_text(root, NOTE_PATH)
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"note:{marker}")

    workflow_text = read_text(root, WORKFLOW_PATH)
    last_index = -1
    for step in REQUIRED_STEP_ORDER:
        current_index = workflow_text.find(step)
        if current_index == -1:
            failures.append(f"workflow_missing:{step}")
            continue
        if current_index <= last_index:
            failures.append(f"workflow_order:{step}")
        last_index = current_index

    for marker in WORKFLOW_REQUIRED_MARKERS:
        if marker not in workflow_text:
            failures.append(f"workflow_required:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_note() -> str:
    return """# Phase 12 Bootstrap Lane Contract

This note records the current Phase 12 portion of the bootstrap workflow without
rewriting the broader reminder packet or reopening the live workflow file in this
lane.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current bootstrap workflow still begins with `Compile current scripts`
- the current Phase 12 slice sits after the current Zig toolchain, Phase 2, Phase 1, Phase 4, Phase 7, Phase 10, and Phase 11 packets
- the current Phase 12 bootstrap segment reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all` are current bootstrap-lane evidence on `master`
- the current bootstrap tail still ends with `make -C zigux phase8-validate`, `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, and `Check current docs-root sanity markers`
- the shipped docs guard is still the inline `Check current docs-root sanity markers` step from `.github/workflows/zigux-bootstrap.yml`
- `Check current Phase 12 build-only surface`, `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` belong to the active Lane 05 workflow review branch, not current `master`
- until the workflow changes again, Lane 05 should keep this contract companion aligned to the broader current-`master` bootstrap segment instead of the older smaller-tail packet or the active branch-only checker pair
"""


def fixture_workflow() -> str:
    command_by_step = {
        "Self-test current Phase 12 build-only surface checker": "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "Check current Phase 12 build-only surface": "python3 scripts/zigux/check-build-only-phase12-surface.py",
        "Self-test current Phase 12 release-readiness packet checker": "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "Validate Phase 12 degraded-workflow bundle": "make -C zigux phase12-validate",
        "Check current Phase 12 release-readiness packet": "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
        "Run focused Phase 12 smoke shard": "make -C zigux phase12-smoke",
        "Run Phase 12 complex driver tests": "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
        "Validate Phase 8 tooling gates": "make -C zigux phase8-validate",
        "Run focused Phase 8 libbpf segment survey tests": "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    }
    rendered_steps = []
    for index, step in enumerate(REQUIRED_STEP_ORDER, start=1):
        command = command_by_step.get(step, f"echo {index}")
        rendered_steps.append(f"      - name: {step}\n        run: {command}")
    steps = "\n\n".join(rendered_steps)
    return (
        "name: zigux-bootstrap\n\n"
        "jobs:\n"
        "  bootstrap:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        f"{steps}\n"
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-contract-"))
    try:
        write_text(base / NOTE_PATH, fixture_note())
        write_text(base / WORKFLOW_PATH, fixture_workflow())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_text(
            base / NOTE_PATH,
            fixture_note().replace("- lane owner: `Lane 05`\n", "", 1),
        )
        expect_failure(base, "note:lane owner: `Lane 05`")

        write_text(base / NOTE_PATH, fixture_note())
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "      - name: Validate Phase 12 degraded-workflow bundle\n        run: make -C zigux phase12-validate\n",
                "",
                1,
            ),
        )
        expect_failure(
            base,
            "workflow_missing:Validate Phase 12 degraded-workflow bundle",
        )

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "      - name: Validate Phase 10 checker-backed review packet\n        run: echo 36\n\n"
                "      - name: Run Phase 10 helper tests\n        run: echo 37\n",
                "      - name: Run Phase 10 helper tests\n        run: echo 37\n\n"
                "      - name: Validate Phase 10 checker-backed review packet\n        run: echo 36\n",
                1,
            ),
        )
        expect_failure(base, "workflow_order:Run Phase 10 helper tests")

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow()
            + "\n      - name: Self-test current Phase 12 bootstrap lane checker\n        run: echo stale\n",
        )
        expect_failure(
            base,
            "workflow_forbidden:Self-test current Phase 12 bootstrap lane checker",
        )

        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 12 bootstrap contract companion."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_BOOTSTRAP_CONTRACT=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_BOOTSTRAP_CONTRACT=pass")
    print(f"PHASE12_BOOTSTRAP_CONTRACT_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE12_BOOTSTRAP_CONTRACT_STEP_COUNT={len(REQUIRED_STEP_ORDER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
