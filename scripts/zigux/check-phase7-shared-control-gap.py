#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
STRING_HELPERS_SLICE_PATH = Path("Documentation/zigux/phase7-string-helpers-slice.md")
BUILD_WIRING_CHECKER_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

DIRECT_PACKET = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "samples/zigux/README.md",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "lib/string_helpers.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
]

PARKED_SHARED_CONTROL_PATHS = [
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/validate-phase7.py",
    "zigux/tests/phase7_build.zig",
]

READABLE_NON_OWNER_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
]

ABSENT_SHARED_CONTROL_ROUTE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-validate",
        "make -C zigux phase7-test",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "phase7-test:",
        "phase7:",
        "phase7-string-helpers-test:",
        "phase7-string-helpers-survey:",
        "phase7-string-helpers-sample-boundary:",
        "phase7-cmdline-test:",
        "phase7-cmdline-survey:",
        "phase7-argv-split-test:",
        "phase7-argv-split-survey:",
        "phase7-rbtree-test:",
        "phase7-rbtree-survey:",
    ],
}

REQUIRED_WORKFLOW_LINES = [
    "- name: Self-test current Phase 7 shared-control gap checker",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "- name: Check current Phase 7 shared-control gap packet",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
]

SEQUENCING_REQUIRED_SNIPPETS = [
    "- shared control-surface packet, lane `P7-Y05`:",
    "- the shared control packet is also only partly recoverable in this slot. `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain directly readable, but fresh authenticated contents reads still returned missing for `scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`, so `P7-Y05` should treat the shared wrapper stack as parked reminder vocabulary until those files rematerialize.",
    "- If the drift is the shared tests-root or scripts-root Phase 7 tranche summary, route it to `P7-Y05` and keep the change inside `zigux/tests/README.md` or `scripts/zigux/README.md` only.",
]

STRING_HELPERS_SLICE_REQUIRED_SNIPPETS = [
    "lane-key note: `helper-local` keeps the expanded string-helpers starter packet separate from the Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes",
    "Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up and should not be counted here as direct helper-local proof unless a fresh reread materializes them again on current `master`.",
    "- do not count `scripts/zigux/validate-phase7.py`",
    "unless a fresh same-family reread proves those broader shared-control reminders are directly readable again on current `master`.",
]

BUILD_WIRING_REQUIRED_SNIPPETS = [
    "FORBIDDEN_MAKEFILE_MARKERS = [",
    '    "phase7-validate",',
    '    "phase7-test",',
    '    "phase7:",',
    '            "Check that the shipped Phase 7 shared control packet stays parked on "',
    '            "current repo reality until Phase 7 build routes rematerialize."',
]

SELF_TEST_CASE_COUNT = (
    len(SEQUENCING_REQUIRED_SNIPPETS)
    + len(STRING_HELPERS_SLICE_REQUIRED_SNIPPETS)
    + len(BUILD_WIRING_REQUIRED_SNIPPETS)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(PARKED_SHARED_CONTROL_PATHS)
    + len(DIRECT_PACKET[2:])
    + len(READABLE_NON_OWNER_FILES)
    + sum(len(markers) for markers in ABSENT_SHARED_CONTROL_ROUTE_MARKERS.values())
    + 2
)


class ValidationError(RuntimeError):
    """Raised when the current Phase 7 shared-control packet drifts."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 7 shared-control marker in {path.as_posix()}: {snippet}"
            )


def require_exact_lines(path: Path, required_lines: list[str]) -> None:
    content_lines = {line.strip() for line in read_text(path).splitlines()}
    for required_line in required_lines:
        if required_line.strip() not in content_lines:
            raise ValidationError(
                f"missing expected Phase 7 shared-control line in {path.as_posix()}: {required_line}"
            )


def require_absent_markers(repo_root: Path) -> None:
    for rel, markers in ABSENT_SHARED_CONTROL_ROUTE_MARKERS.items():
        content = read_text(repo_root / rel)
        for marker in markers:
            if marker in content:
                raise ValidationError(
                    f"unexpected Phase 7 shared-control wrapper marker in {rel}: {marker}"
                )


def require_repo_reality(repo_root: Path) -> None:
    missing_direct = [rel for rel in DIRECT_PACKET if not (repo_root / rel).exists()]
    if missing_direct:
        raise ValidationError(
            "direct Phase 7 shared-control packet no longer matches current tree: "
            + ", ".join(missing_direct)
        )

    rematerialized_paths = [rel for rel in PARKED_SHARED_CONTROL_PATHS if (repo_root / rel).exists()]
    if rematerialized_paths:
        raise ValidationError(
            "parked Phase 7 shared-control paths unexpectedly rematerialized: "
            + ", ".join(rematerialized_paths)
        )

    missing_non_owner = [rel for rel in READABLE_NON_OWNER_FILES if not (repo_root / rel).exists()]
    if missing_non_owner:
        raise ValidationError(
            "required readable non-owner Phase 7 shared-control files disappeared: "
            + ", ".join(missing_non_owner)
        )

    require_absent_markers(repo_root)


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SEQUENCING_NOTE_PATH, SEQUENCING_REQUIRED_SNIPPETS)
    require_snippets(repo_root / STRING_HELPERS_SLICE_PATH, STRING_HELPERS_SLICE_REQUIRED_SNIPPETS)
    require_snippets(repo_root / BUILD_WIRING_CHECKER_PATH, BUILD_WIRING_REQUIRED_SNIPPETS)
    require_exact_lines(repo_root / WORKFLOW_PATH, REQUIRED_WORKFLOW_LINES)
    require_repo_reality(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SEQUENCING_NOTE_PATH, "\n".join(SEQUENCING_REQUIRED_SNIPPETS) + "\n")
    write(root / STRING_HELPERS_SLICE_PATH, "\n".join(STRING_HELPERS_SLICE_REQUIRED_SNIPPETS) + "\n")
    write(root / BUILD_WIRING_CHECKER_PATH, "\n".join(BUILD_WIRING_REQUIRED_SNIPPETS) + "\n")
    for rel in DIRECT_PACKET[2:]:
        if rel == BUILD_WIRING_CHECKER_PATH.as_posix():
            continue
        write(root / Path(rel), "# direct phase7 shared-control packet file\n")
    write(root / WORKFLOW_PATH, "\n".join(["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]) + "\n")
    write(
        root / Path("zigux/Makefile"),
        "phase2-validate:\n\tpython3 scripts/zigux/validate-phase2.py\n",
    )


def expect_validation_error(root: Path, expected_fragment: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected {expected_fragment!r} in validation error, got {str(exc)!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")


def expect_failure(root: Path, path: Path, snippet: str) -> None:
    original = read_text(path)
    write(path, original.replace(snippet + "\n", "", 1))
    try:
        expect_validation_error(root, snippet)
    finally:
        write(path, original)


def expect_unexpected_marker(root: Path, path: Path, marker: str) -> None:
    original = read_text(path)
    write(path, original + marker + "\n")
    try:
        expect_validation_error(root, marker)
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase7_shared_control_gap_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0
        for path, snippets in (
            (root / SEQUENCING_NOTE_PATH, SEQUENCING_REQUIRED_SNIPPETS),
            (root / STRING_HELPERS_SLICE_PATH, STRING_HELPERS_SLICE_REQUIRED_SNIPPETS),
            (root / BUILD_WIRING_CHECKER_PATH, BUILD_WIRING_REQUIRED_SNIPPETS),
            (root / WORKFLOW_PATH, REQUIRED_WORKFLOW_LINES),
        ):
            for snippet in snippets:
                expect_failure(root, path, snippet)
                cases_run += 1

        for rel in PARKED_SHARED_CONTROL_PATHS:
            parked_path = root / Path(rel)
            write(parked_path, "# stale shared-control path returned\n")
            try:
                expect_validation_error(root, rel)
            finally:
                parked_path.unlink()
            cases_run += 1

        for rel in DIRECT_PACKET[2:]:
            direct_path = root / Path(rel)
            direct_path.unlink()
            try:
                expect_validation_error(root, rel)
            finally:
                if rel == BUILD_WIRING_CHECKER_PATH.as_posix():
                    write(direct_path, "\n".join(BUILD_WIRING_REQUIRED_SNIPPETS) + "\n")
                else:
                    write(direct_path, "# direct phase7 shared-control packet file\n")
            cases_run += 1

        for rel in READABLE_NON_OWNER_FILES:
            non_owner_path = root / Path(rel)
            original = read_text(non_owner_path)
            non_owner_path.unlink()
            try:
                expect_validation_error(root, rel)
            finally:
                write(non_owner_path, original)
            cases_run += 1

        for rel, markers in ABSENT_SHARED_CONTROL_ROUTE_MARKERS.items():
            path = root / Path(rel)
            for marker in markers:
                expect_unexpected_marker(root, path, marker)
                cases_run += 1

        scaffold_repo(root)
        (root / SEQUENCING_NOTE_PATH).unlink()
        expect_validation_error(root, str(SEQUENCING_NOTE_PATH))
        cases_run += 1

        scaffold_repo(root)
        (root / STRING_HELPERS_SLICE_PATH).unlink()
        expect_validation_error(root, str(STRING_HELPERS_SLICE_PATH))
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass")
    print(f"PHASE7_SHARED_CONTROL_GAP_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_SHARED_CONTROL_GAP=fail: {exc}")
        return 1

    print("PHASE7_SHARED_CONTROL_GAP=pass")
    print(f"PHASE7_SHARED_CONTROL_GAP_DIRECT_FILE_COUNT={len(DIRECT_PACKET)}")
    print(f"PHASE7_SHARED_CONTROL_GAP_PARKED_FILE_COUNT={len(PARKED_SHARED_CONTROL_PATHS)}")
    print(f"PHASE7_SHARED_CONTROL_GAP_NON_OWNER_FILE_COUNT={len(READABLE_NON_OWNER_FILES)}")
    print(f"PHASE7_SHARED_CONTROL_GAP_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
