#!/usr/bin/env python3
"""Check the current Phase 1 Makefile route packet against repo-reality expectations."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_TARGETS = {
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-validate",
    "phase2",
    "phase3-validate",
    "phase3",
    "phase8-validate",
    "phase8-exec-cmd-test",
    "phase8-test",
    "phase8",
    "phase10-validate",
    "phase10-test",
    "phase10",
    "phase12-smoke",
    "phase12-test",
    "phase12",
}

FORBIDDEN_TARGETS = {
    "phase1-validate",
    "phase1-test",
    "phase1-bench",
    "phase1",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_makefile(root: Path) -> str:
    return (root / MAKEFILE_REL).read_text(encoding="utf-8")


def parse_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("."):
            continue
        if raw_line.startswith(("\t", " ")) or ":" not in stripped:
            continue
        head = stripped.split(":", 1)[0].strip()
        if head:
            targets.add(head)
    return targets


def parse_phony_targets(text: str) -> set[str]:
    phony: set[str] = set()
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, _, tail = stripped.partition(":")
        for token in tail.split():
            if token:
                phony.add(token)
    return phony


def collect_failures(root: Path) -> list[str]:
    makefile_path = root / MAKEFILE_REL
    if not makefile_path.exists():
        return [f"missing_file:{MAKEFILE_REL.as_posix()}"]

    text = load_makefile(root)
    targets = parse_targets(text)
    phony_targets = parse_phony_targets(text)

    failures: list[str] = []

    missing_targets = sorted(REQUIRED_TARGETS - targets)
    if missing_targets:
        failures.append(f"missing_targets:{missing_targets!r}")

    missing_phony = sorted(REQUIRED_TARGETS - phony_targets)
    if missing_phony:
        failures.append(f"missing_phony:{missing_phony!r}")

    unexpected_targets = sorted(FORBIDDEN_TARGETS & targets)
    if unexpected_targets:
        failures.append(f"unexpected_targets:{unexpected_targets!r}")

    unexpected_phony = sorted(FORBIDDEN_TARGETS & phony_targets)
    if unexpected_phony:
        failures.append(f"unexpected_phony:{unexpected_phony!r}")

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


SAMPLE_MAKEFILE = """PYTHON ?= python3
ZIG ?= zig
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
PHASE8_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase8-validate phase8-exec-cmd-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12

phase2-toolchain:
	true
phase2-tools:
	true
phase2-kconfig:
	true
phase2-cross:
	true
phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross
	true
phase2: phase2-validate
	true
phase3-validate:
	true
phase3: phase3-validate
	true
phase8-validate:
	true
phase8-exec-cmd-test:
	true
phase8-test:
	true
phase8:
	true
phase10-validate:
	true
phase10-test:
	true
phase10: phase10-validate phase10-test
	true
phase12-smoke:
	true
phase12-test:
	true
phase12: phase12-smoke phase12-test
	true
"""


def run_self_test() -> int:
    cases: list[tuple[str, str, bool]] = [
        ("baseline", SAMPLE_MAKEFILE, True),
        ("missing_phase12_test_from_phony", SAMPLE_MAKEFILE.replace(" phase12-test", "", 1), False),
        ("missing_phase8_rule", SAMPLE_MAKEFILE.replace("\nphase8:\n\ttrue\n", "\n", 1), False),
        ("unexpected_phase1_target", SAMPLE_MAKEFILE + "\nphase1-validate:\n\ttrue\n", False),
        (
            "unexpected_phase1_phony",
            SAMPLE_MAKEFILE.replace("phase12", "phase12 phase1", 1),
            False,
        ),
    ]

    for name, text, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-makefile-route-{name}-") as tmpdir:
            root = Path(tmpdir)
            write_text(root / MAKEFILE_REL, text)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"self-test:{name}:unexpected={failures}")
                return 1

    print("phase1-makefile-route-readback:self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-makefile-route-readback:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
