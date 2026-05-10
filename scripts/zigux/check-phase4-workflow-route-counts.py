#!/usr/bin/env python3
"""Validate the shipped Phase 4 wrapper-route inventory.

The checker stays intentionally narrow: it makes sure the current Linux-style
Makefile routes and the bootstrap workflow still expose the bounded Phase 4
validation and replay paths that the validation lane documents.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


EXPECTED_MAKE_TARGETS = [
    "phase4-validate",
    "phase4-test",
    "phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-survey",
    "phase4-perf-baseline-survey",
    "phase4-bitmap-diff",
    "phase4-bitmap-diff-survey",
    "phase4-bitmap-live-helper-replay",
    "phase4-test-fsmount-survey",
    "phase4-kprobe-example-survey",
    "phase4",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test "
    "phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey "
    "phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey "
    "phase4-bitmap-live-helper-replay phase4-test-fsmount-survey "
    "phase4-kprobe-example-survey phase4",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "phase4-test:",
    "$(ZIG) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "$(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "$(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "$(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "$(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "$(ZIG) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "$(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-test-fsmount-survey:",
    "$(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "$(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4: phase4-validate phase4-test",
]

REQUIRED_WORKFLOW_MARKERS = [
    "- name: Validate Phase 4 diff gates",
    "run: make -C zigux phase4-validate",
    "- name: Self-test Phase 4 validator directly",
    "run: python3 scripts/zigux/validate-phase4.py --self-test",
    "- name: Validate Phase 4 diff packet directly",
    "run: python3 scripts/zigux/validate-phase4.py",
    "- name: Run Phase 4 diff tests directly",
    "run: zig build test --build-file zigux/tests/phase4_build.zig",
]

SELFTEST_MAKEFILE = """PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4

phase4-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py

phase4-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-live-helper-replay:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig

phase4-test-fsmount-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig

phase4-kprobe-example-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig

phase4: phase4-validate phase4-test
"""

SELFTEST_WORKFLOW = """jobs:
  bootstrap:
    steps:
      - name: Validate Phase 4 diff gates
        run: make -C zigux phase4-validate
      - name: Self-test Phase 4 validator directly
        run: python3 scripts/zigux/validate-phase4.py --self-test
      - name: Validate Phase 4 diff packet directly
        run: python3 scripts/zigux/validate-phase4.py
      - name: Run Phase 4 diff tests directly
        run: zig build test --build-file zigux/tests/phase4_build.zig
"""


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parents[2]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def ensure_markers(label: str, text: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        joined = "\n".join(f"  - {marker}" for marker in missing)
        raise SystemExit(f"{label} is missing required Phase 4 markers:\n{joined}")


def declared_targets(makefile_text: str) -> set[str]:
    targets: set[str] = set()
    for line in makefile_text.splitlines():
        if not line or line.startswith(("\t", "#", "PHONY", ".")):
            continue
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9_-]*):", line)
        if match:
            targets.add(match.group(1))
    return targets


def ensure_expected_targets(makefile_text: str) -> None:
    targets = declared_targets(makefile_text)
    missing = [target for target in EXPECTED_MAKE_TARGETS if target not in targets]
    if missing:
        joined = "\n".join(f"  - {target}" for target in missing)
        raise SystemExit(f"zigux/Makefile is missing expected Phase 4 targets:\n{joined}")


def check(makefile_path: Path, workflow_path: Path) -> None:
    makefile_text = read_text(makefile_path)
    workflow_text = read_text(workflow_path)
    ensure_expected_targets(makefile_text)
    ensure_markers("zigux/Makefile", makefile_text, REQUIRED_MAKE_MARKERS)
    ensure_markers(".github/workflows/zigux-bootstrap.yml", workflow_text, REQUIRED_WORKFLOW_MARKERS)


def run_selftest() -> None:
    with TemporaryDirectory() as tempdir:
        root = Path(tempdir)
        makefile = root / "zigux/Makefile"
        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        makefile.parent.mkdir(parents=True, exist_ok=True)
        workflow.parent.mkdir(parents=True, exist_ok=True)
        makefile.write_text(SELFTEST_MAKEFILE, encoding="utf-8")
        workflow.write_text(SELFTEST_WORKFLOW, encoding="utf-8")
        check(makefile, workflow)
    print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNT={len(EXPECTED_MAKE_TARGETS)}")
    print(f"PHASE4_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS)}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        run_selftest()
        return 0

    root = repo_root_from_script(Path(__file__))
    check(root / "zigux/Makefile", root / ".github/workflows/zigux-bootstrap.yml")
    print("PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK=pass")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNT={len(EXPECTED_MAKE_TARGETS)}")
    print(f"PHASE4_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
