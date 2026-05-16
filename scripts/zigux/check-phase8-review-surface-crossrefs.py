#!/usr/bin/env python3
"""Fail closed on the core Phase 8 exec-cmd and libbpf review surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


TESTS_README_PATH = Path("zigux/tests/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

SHARED_MARKERS = (
    "scripts/zigux/validate-phase8.py",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "make -C zigux phase8-validate",
    "make -C zigux phase8-exec-cmd-test",
    "make -C zigux phase8-libbpf-segments-test",
)

TESTS_README_MARKERS = (
    "Phase 8 review packet",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "make -C zigux phase8-test",
    "keep the shared Phase 8 tooling packet explicit here too",
)

REVIEW_CHECKLIST_MARKERS = (
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "tools/lib/subcmd/exec-cmd.zig",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    "scripts/zigux/check-phase8-libbpf-shard-routes.py",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
)


def _missing_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def check_phase8_review_surfaces(root: Path) -> list[str]:
    failures: list[str] = []

    tests_readme_path = root / TESTS_README_PATH
    if not tests_readme_path.is_file():
        failures.append(f"missing file:{TESTS_README_PATH.as_posix()}")
    else:
        tests_readme = tests_readme_path.read_text(encoding="utf-8")
        for marker in _missing_markers(tests_readme, SHARED_MARKERS):
            failures.append(f"tests_readme:{marker}")
        for marker in _missing_markers(tests_readme, TESTS_README_MARKERS):
            failures.append(f"tests_readme:{marker}")

    review_checklist_path = root / REVIEW_CHECKLIST_PATH
    if not review_checklist_path.is_file():
        failures.append(f"missing file:{REVIEW_CHECKLIST_PATH.as_posix()}")
    else:
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        for marker in _missing_markers(review_checklist, SHARED_MARKERS):
            failures.append(f"review_checklist:{marker}")
        for marker in _missing_markers(review_checklist, REVIEW_CHECKLIST_MARKERS):
            failures.append(f"review_checklist:{marker}")

    return failures


def _expect_missing(case_name: str, root: Path, expected: str) -> None:
    failures = check_phase8_review_surfaces(root)
    if failures != [expected]:
        raise AssertionError(f"{case_name}: expected {[expected]}, got {failures}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-review-surface-crossrefs-") as tmp:
        root = Path(tmp)
        tests_readme_path = root / TESTS_README_PATH
        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        tests_readme_path.parent.mkdir(parents=True, exist_ok=True)
        review_checklist_path.parent.mkdir(parents=True, exist_ok=True)

        tests_readme = "\n".join(
            (
                "# zigux/tests",
                "",
                "Phase 8 review packet",
                "Documentation/zigux/phase8-tooling-lane-sequencing.md",
                "zigux/tests/phase8_exec_cmd.zig",
                "zigux/tests/phase8_exec_cmd_only_build.zig",
                "zigux/tests/phase8_libbpf_segments.zig",
                "zigux/tests/phase8_libbpf_segments_only_build.zig",
                "scripts/zigux/validate-phase8.py",
                "make -C zigux phase8-validate",
                "make -C zigux phase8-exec-cmd-test",
                "make -C zigux phase8-libbpf-segments-test",
                "make -C zigux phase8-test",
                "keep the shared Phase 8 tooling packet explicit here too",
                "",
            )
        )
        review_checklist = "\n".join(
            (
                "# Zigux Review Checklist",
                "",
                "Documentation/zigux/phase8-exec-cmd-slice.md",
                "tools/lib/subcmd/exec-cmd.zig",
                "Documentation/zigux/phase8-libbpf-segment-survey.md",
                "scripts/zigux/validate-phase8.py",
                "scripts/zigux/check-phase8-libbpf-segment-gate.py",
                "scripts/zigux/check-phase8-libbpf-shard-routes.py",
                "tools/lib/bpf/zigux_segments/manifest.json",
                "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
                "zigux/tests/phase8_exec_cmd_only_build.zig",
                "zigux/tests/phase8_libbpf_segments.zig",
                "make -C zigux phase8-validate",
                "make -C zigux phase8-exec-cmd-test",
                "make -C zigux phase8-libbpf-segments-test",
                "",
            )
        )

        tests_readme_path.write_text(tests_readme, encoding="utf-8")
        review_checklist_path.write_text(review_checklist, encoding="utf-8")

        failures = check_phase8_review_surfaces(root)
        if failures:
            raise AssertionError(f"expected clean self-test, got {failures}")

        tests_readme_path.write_text(
            tests_readme.replace("make -C zigux phase8-libbpf-segments-test\n", "", 1),
            encoding="utf-8",
        )
        _expect_missing(
            "tests_readme_shared_marker",
            root,
            "tests_readme:make -C zigux phase8-libbpf-segments-test",
        )

        tests_readme_path.write_text(tests_readme, encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist.replace("tools/lib/subcmd/exec-cmd.zig\n", "", 1),
            encoding="utf-8",
        )
        _expect_missing(
            "review_checklist_exec_cmd_marker",
            root,
            "review_checklist:tools/lib/subcmd/exec-cmd.zig",
        )

        review_checklist_path.write_text(review_checklist, encoding="utf-8")
        tests_readme_path.unlink()
        _expect_missing(
            "missing_tests_readme",
            root,
            "missing file:zigux/tests/README.md",
        )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the core Phase 8 exec-cmd and segmented-libbpf review surfaces."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root containing zigux/tests and Documentation/zigux",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in self-tests instead of checking a repository root",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = check_phase8_review_surfaces(args.root.resolve())
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase8 review surfaces aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
