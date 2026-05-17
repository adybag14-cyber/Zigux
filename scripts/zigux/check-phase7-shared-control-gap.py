#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("scripts/zigux/README.md")
RBTREE_SURVEY_PATH = Path("zigux/tests/phase7_rbtree_survey.zig")
STRING_SLICE_PATH = Path("Documentation/zigux/phase7-string-helpers-slice.md")

DIRECT_PACKET = [
    "scripts/zigux/README.md",
    "zigux/tests/phase7_rbtree_survey.zig",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "lib/string_helpers.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
]

MISSING_SHARED_CONTROL_PACKET = [
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "zigux/tests/phase7_build.zig",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
]

README_REQUIRED_SNIPPETS = [
    "Phase 7 flow - the current scripts-root Phase 7 reminder is intentionally narrow:",
    "helper-local string evidence now lives directly in `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, and `zigux/tests/phase7_string_helpers_sample_boundary.zig`, while the surviving broader shared-helper anchor is the directly readable `zigux/tests/phase7_rbtree_survey.zig`",
    "authenticated contents reads on current `master` now return missing for the older shared-control wrapper packet members `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `zigux/tests/phase7_build.zig`, `Documentation/zigux/phase7-argv-split-slice.md`, and `Documentation/zigux/phase7-rbtree-slice.md`",
    "leave broader shared-control validator or make-wrapper follow-up parked until those missing wrapper files rematerialize on current `master`",
]

RBTREE_SURVEY_REQUIRED_SNIPPETS = [
    'const active_lane_key = "P7-L13";',
    "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    "repo-reality warning for the broader Phase 7 rbtree packet:",
]

STRING_SLICE_REQUIRED_SNIPPETS = [
    "`PHASE7_STATUS=starter_landed`",
    "Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up",
    "do not count `scripts/zigux/validate-phase7.py`",
    "do not count `scripts/zigux/check-phase7-make-wrapper.py`",
    "do not count `scripts/zigux/check-phase7-build-wiring.py`",
    "do not count `zigux/tests/phase7_build.zig`",
]

SELF_TEST_CASE_COUNT = 8


class ValidationError(RuntimeError):
    """Raised when the current Phase 7 repo-reality packet drifts."""


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


def require_repo_reality(repo_root: Path) -> None:
    missing_direct = [rel for rel in DIRECT_PACKET if not (repo_root / rel).exists()]
    if missing_direct:
        raise ValidationError(
            "direct Phase 7 packet no longer matches current tree: "
            + ", ".join(missing_direct)
        )

    returned_shared_control = [
        rel for rel in MISSING_SHARED_CONTROL_PACKET if (repo_root / rel).exists()
    ]
    if returned_shared_control:
        raise ValidationError(
            "shared-control repo-reality gap narrowed and the warning must be refreshed: "
            + ", ".join(returned_shared_control)
        )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / README_PATH, README_REQUIRED_SNIPPETS)
    require_snippets(repo_root / RBTREE_SURVEY_PATH, RBTREE_SURVEY_REQUIRED_SNIPPETS)
    require_snippets(repo_root / STRING_SLICE_PATH, STRING_SLICE_REQUIRED_SNIPPETS)
    require_repo_reality(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / README_PATH, "\n".join(README_REQUIRED_SNIPPETS) + "\n")
    write(root / RBTREE_SURVEY_PATH, "\n".join(RBTREE_SURVEY_REQUIRED_SNIPPETS) + "\n")
    write(root / STRING_SLICE_PATH, "\n".join(STRING_SLICE_REQUIRED_SNIPPETS) + "\n")
    for rel in DIRECT_PACKET[3:]:
        write(root / Path(rel), "# direct phase7 packet file\n")


def expect_failure(root: Path, path: Path, snippet: str) -> None:
    original = read_text(path)
    write(path, original.replace(snippet + "\n", "", 1))
    try:
        validate(root)
    except ValidationError as exc:
        if snippet not in str(exc):
            raise AssertionError(
                f"expected {snippet!r} in validation error, got {str(exc)!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase7_shared_control_gap_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0
        for path, snippet in [
            (root / README_PATH, README_REQUIRED_SNIPPETS[2]),
            (root / README_PATH, README_REQUIRED_SNIPPETS[3]),
            (root / RBTREE_SURVEY_PATH, RBTREE_SURVEY_REQUIRED_SNIPPETS[0]),
            (root / STRING_SLICE_PATH, STRING_SLICE_REQUIRED_SNIPPETS[3]),
        ]:
            expect_failure(root, path, snippet)
            cases_run += 1

        (root / Path(DIRECT_PACKET[-1])).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing direct packet file to fail")

        scaffold_repo(root)
        write(root / Path(MISSING_SHARED_CONTROL_PACKET[0]), "# returned wrapper\n")
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected returned shared-control file to fail")

        scaffold_repo(root)
        (root / README_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing README to fail")

        scaffold_repo(root)
        (root / STRING_SLICE_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing string slice to fail")

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
    print(
        "PHASE7_SHARED_CONTROL_GAP_MISSING_SHARED_CONTROL_FILE_COUNT="
        f"{len(MISSING_SHARED_CONTROL_PACKET)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
