#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("scripts/zigux/README.md")
STRING_HELPERS_SLICE_PATH = Path("Documentation/zigux/phase7-string-helpers-slice.md")

DIRECT_PACKET = [
    "scripts/zigux/README.md",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "lib/string_helpers.zig",
    "samples/zigux/README.md",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
]

PARKED_SHARED_CONTROL_PATHS = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/validate-phase7.py",
    "zigux/tests/phase7_build.zig",
]

README_REQUIRED_SNIPPETS = [
    "Phase 7 flow - the current scripts-root Phase 7 reminder is intentionally narrow:",
    "helper-local string evidence now lives directly in `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, and `zigux/tests/phase7_string_helpers_sample_boundary.zig`, while the surviving broader shared-helper anchor is the directly readable `zigux/tests/phase7_rbtree_survey.zig`",
    "authenticated contents reads on current `master` now return missing for the older shared-control wrapper packet members `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `zigux/tests/phase7_build.zig`, `Documentation/zigux/phase7-argv-split-slice.md`, and `Documentation/zigux/phase7-rbtree-slice.md`",
    "leave broader shared-control validator or make-wrapper follow-up parked until those missing wrapper files rematerialize on current `master`",
]

STRING_HELPERS_SLICE_REQUIRED_SNIPPETS = [
    "lane-key note: `helper-local` keeps the expanded string-helpers starter packet separate from the Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes",
    "Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up and should not be counted here as direct helper-local proof unless a fresh reread materializes them again on current `master`.",
    "- do not count `scripts/zigux/validate-phase7.py`",
    "unless a fresh same-family reread proves those broader shared-control reminders are directly readable again on current `master`.",
]

SELF_TEST_CASE_COUNT = 8


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


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / README_PATH, README_REQUIRED_SNIPPETS)
    require_snippets(repo_root / STRING_HELPERS_SLICE_PATH, STRING_HELPERS_SLICE_REQUIRED_SNIPPETS)
    require_repo_reality(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / README_PATH, "\n".join(README_REQUIRED_SNIPPETS) + "\n")
    write(root / STRING_HELPERS_SLICE_PATH, "\n".join(STRING_HELPERS_SLICE_REQUIRED_SNIPPETS) + "\n")
    for rel in DIRECT_PACKET[2:]:
        write(root / Path(rel), "# direct phase7 shared-control packet file\n")


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
            (root / README_PATH, README_REQUIRED_SNIPPETS[0]),
            (root / README_PATH, README_REQUIRED_SNIPPETS[2]),
            (root / STRING_HELPERS_SLICE_PATH, STRING_HELPERS_SLICE_REQUIRED_SNIPPETS[0]),
            (root / STRING_HELPERS_SLICE_PATH, STRING_HELPERS_SLICE_REQUIRED_SNIPPETS[2]),
        ]:
            expect_failure(root, path, snippet)
            cases_run += 1

        write(root / Path(PARKED_SHARED_CONTROL_PATHS[0]), "# stale shared-control path returned\n")
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected rematerialized parked path to fail")
        (root / Path(PARKED_SHARED_CONTROL_PATHS[0])).unlink()

        (root / Path(DIRECT_PACKET[-1])).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing direct packet file to fail")

        scaffold_repo(root)
        (root / README_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing README to fail")

        scaffold_repo(root)
        (root / STRING_HELPERS_SLICE_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing string-helpers slice to fail")

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
