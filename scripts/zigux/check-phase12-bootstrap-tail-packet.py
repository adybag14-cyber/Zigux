#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = "scripts/zigux/check-phase12-release-readiness-packet.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
RELEASE_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
TESTS_README_PATH = "zigux/tests/README.md"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    RELEASE_SURVEY_PATH,
    TESTS_README_PATH,
]

REQUIRED_WORKFLOW_SEQUENCE = [
    (
        "- name: Self-test current Phase 12 build-only surface checker",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    ),
    (
        "- name: Check current Phase 12 build-only surface",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py",
    ),
    (
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    ),
    (
        "- name: Check current Phase 12 release-readiness packet",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    ),
    (
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
    ),
    (
        "- name: Run current Phase 12 smoke packet",
        "run: make -C zigux phase12-smoke",
    ),
    (
        "- name: Run current Phase 12 shared test packet",
        "run: make -C zigux phase12-test",
    ),
    (
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
    ),
    (
        "- name: Run current Phase 12 throughput-parity anchor",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
    ),
]

REQUIRED_MARKERS = {
    BUILD_ONLY_CHECKER_PATH: [
        "PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass",
        "PHASE12_BUILD_ONLY_REQUIRED_FILE_COUNT=",
        "phase12: phase12-smoke phase12-test",
        "Run current Phase 12 aggregate route",
        "Run current Phase 12 throughput-parity anchor",
    ],
    RELEASE_READINESS_CHECKER_PATH: [
        "PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass",
        "PHASE12_RELEASE_READINESS_PACKET_REQUIRED_FILE_COUNT=",
        "run: make -C zigux phase12",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
    ],
    VALIDATOR_PATH: [
        "PHASE12_VALIDATION=pass",
        "PHASE12_REQUIRED_FILE_COUNT=",
        "scripts-side support packet",
        "make -C zigux phase12-validate",
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    RELEASE_SURVEY_PATH: [
        "the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`",
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
        "`.github/workflows/zigux-bootstrap.yml` still runs `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig` after the shared `phase12-smoke` and `phase12-test` reruns",
    ],
    TESTS_README_PATH: [
        "Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle",
        "Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
        "Keep `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` explicit as the current shared smoke-first build gate",
    ],
}


def normalized_lines(text: str) -> list[str]:
    return [line.lstrip() for line in text.splitlines()]


def count_exact_line(lines: list[str], marker: str) -> int:
    return sum(1 for line in lines if line == marker)


def find_exact_line(lines: list[str], marker: str) -> int:
    for index, line in enumerate(lines):
        if line == marker:
            return index
    return -1


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
    workflow_lines = normalized_lines(workflow_text)
    previous_run_index = -1
    for name_marker, run_marker in REQUIRED_WORKFLOW_SEQUENCE:
        name_count = count_exact_line(workflow_lines, name_marker)
        if name_count == 0:
            failures.append(f"missing_workflow_line:{name_marker}")
            continue
        if name_count != 1:
            failures.append(f"duplicate_workflow_line:{name_marker}:count={name_count}")
        run_count = count_exact_line(workflow_lines, run_marker)
        if run_count == 0:
            failures.append(f"missing_workflow_line:{run_marker}")
            continue
        if run_count != 1:
            failures.append(f"duplicate_workflow_line:{run_marker}:count={run_count}")
        name_index = find_exact_line(workflow_lines, name_marker)
        run_index = find_exact_line(workflow_lines, run_marker)
        if run_index <= name_index:
            failures.append(f"workflow_run_not_after_name:{name_marker}")
            continue
        if name_index <= previous_run_index:
            failures.append(f"workflow_step_out_of_order:{name_marker}")
            continue
        previous_run_index = run_index

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_fixture(rel_path: str) -> str:
    if rel_path == WORKFLOW_PATH:
        lines = ["name: zigux-bootstrap", ""]
        for name_marker, run_marker in REQUIRED_WORKFLOW_SEQUENCE:
            lines.append(f"      {name_marker}")
            lines.append(f"        {run_marker}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    if rel_path in REQUIRED_MARKERS:
        return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
    return "fixture\n"


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, sample_fixture(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_first(path: Path, needle: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(needle + "\n", "", 1)
    if updated == text:
        updated = text.replace(needle, "", 1)
    if updated == text:
        raise SystemExit(f"unable to remove marker: {needle}")
    path.write_text(updated, encoding="utf-8")


def duplicate_exact_line(path: Path, needle: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.lstrip() == needle:
            lines.insert(index + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise SystemExit(f"unable to duplicate marker: {needle}")


def replace_first(path: Path, needle: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(needle, replacement, 1)
    if updated == text:
        raise SystemExit(f"unable to replace marker: {needle}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase12_bootstrap_tail_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        if validate(root):
            raise SystemExit(f"sample root should pass but failed: {validate(root)!r}")

        checks = 0
        for rel_path in REQUIRED_FILES:
            write_sample_root(root)
            (root / rel_path).unlink()
            expect_failure(root, f"missing_file:{rel_path}")
            checks += 1

        write_sample_root(root)
        remove_first(root / WORKFLOW_PATH, REQUIRED_WORKFLOW_SEQUENCE[0][0])
        expect_failure(
            root,
            f"missing_workflow_line:{REQUIRED_WORKFLOW_SEQUENCE[0][0]}",
        )
        checks += 1

        write_sample_root(root)
        duplicate_exact_line(root / WORKFLOW_PATH, REQUIRED_WORKFLOW_SEQUENCE[4][1])
        expect_failure(
            root,
            f"duplicate_workflow_line:{REQUIRED_WORKFLOW_SEQUENCE[4][1]}:count=2",
        )
        checks += 1

        write_sample_root(root)
        workflow_path = root / WORKFLOW_PATH
        replace_first(
            workflow_path,
            REQUIRED_WORKFLOW_SEQUENCE[5][0],
            REQUIRED_WORKFLOW_SEQUENCE[6][0],
        )
        expect_failure(
            root,
            f"duplicate_workflow_line:{REQUIRED_WORKFLOW_SEQUENCE[6][0]}:count=2",
        )
        checks += 1

        write_sample_root(root)
        remove_first(
            root / RELEASE_SURVEY_PATH,
            REQUIRED_MARKERS[RELEASE_SURVEY_PATH][1],
        )
        expect_failure(
            root,
            f"missing_marker:{RELEASE_SURVEY_PATH}:{REQUIRED_MARKERS[RELEASE_SURVEY_PATH][1]}",
        )
        checks += 1

        write_sample_root(root)
        remove_first(root / MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][2])
        expect_failure(
            root,
            f"missing_marker:{MAKEFILE_PATH}:{REQUIRED_MARKERS[MAKEFILE_PATH][2]}",
        )
        checks += 1

        write_sample_root(root)
        remove_first(
            root / TESTS_README_PATH,
            REQUIRED_MARKERS[TESTS_README_PATH][2],
        )
        expect_failure(
            root,
            f"missing_marker:{TESTS_README_PATH}:{REQUIRED_MARKERS[TESTS_README_PATH][2]}",
        )
        checks += 1

    print("PHASE12_BOOTSTRAP_TAIL_PACKET_SELF_TEST=pass")
    print(f"PHASE12_BOOTSTRAP_TAIL_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 bootstrap tail packet around the shared "
            "support bundle, returned smoke-and-test wrappers, and throughput anchor."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in fixture-backed self-test.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample tree for replay validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE12_BOOTSTRAP_TAIL_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_BOOTSTRAP_TAIL_PACKET=fail:{failure}")
        return 1

    print("PHASE12_BOOTSTRAP_TAIL_PACKET=pass")
    print(f"PHASE12_BOOTSTRAP_TAIL_PACKET_WORKFLOW_STEP_COUNT={len(REQUIRED_WORKFLOW_SEQUENCE)}")
    print(
        "PHASE12_BOOTSTRAP_TAIL_PACKET_REQUIRED_FILE_COUNT="
        f"{len(REQUIRED_FILES)}"
    )
    print(
        "PHASE12_BOOTSTRAP_TAIL_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())