#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=docs_root_smoke_summary

Fail-closed checker for the docs-root summary of the shared Phase 14 smoke packet.
This companion checker keeps `Documentation/zigux/README.md` aligned with the
current study-only replay route and the shipped shared-smoke note surfaces.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=docs_root_smoke_summary"
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
REQUIRED_MARKERS = [
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge.zig",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_survey.zig",
    "zigux/tests/phase14_rcu_tree_survey.zig",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/Makefile",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    docs_root_path = root / DOCS_ROOT_PATH
    if not docs_root_path.exists():
        return [f"missing file: {DOCS_ROOT_PATH}"]

    text = read_text(docs_root_path)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing marker in {DOCS_ROOT_PATH}: {marker}")
    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        good_text = "\n".join(REQUIRED_MARKERS) + "\n"
        write_text(root / DOCS_ROOT_PATH, good_text)

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken_path = root / DOCS_ROOT_PATH
        broken_path.write_text(
            good_text.replace(
                "scripts/zigux/check-phase14-release-boundary-exact-counts.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/README.md: "
            "scripts/zigux/check-phase14-release-boundary-exact-counts.py" in error
            for error in errors
        ):
            print(
                "self-test expected failure when the release-boundary checker marker drifted",
                file=sys.stderr,
            )
            return 1

        broken_path.write_text(
            good_text.replace("make -C zigux phase14-smoke\n", "", 1),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/README.md: make -C zigux phase14-smoke"
            in error
            for error in errors
        ):
            print(
                "self-test expected failure when the focused smoke command marker drifted",
                file=sys.stderr,
            )
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase14 docs-root smoke summary validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
