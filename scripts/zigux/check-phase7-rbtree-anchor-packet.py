#!/usr/bin/env python3
"""Guard the current Phase 7 rbtree anchor packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

TESTS_README_PATH = Path("zigux/tests/README.md")
SURVEY_PATH = Path("zigux/tests/phase7_rbtree_survey.zig")

DIRECT_PACKET = [
    "zigux/tests/README.md",
    "zigux/tests/phase7_rbtree_survey.zig",
    "scripts/zigux/check-phase7-rbtree-anchor-packet.py",
]

MISSING_BROADER_PACKET = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "zigux/tests/phase7_build.zig",
]

REQUIRED_TESTS_SNIPPETS = [
    "Phase 7 review packet",
    "* current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    "* repo-reality warning for the broader Phase 7 rbtree packet:",
    "* treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again",
    "* keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
]

REQUIRED_SURVEY_SNIPPETS = [
    "const active_lane_key = \"P7-L13\";",
    "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    "repo-reality warning for the broader Phase 7 rbtree packet:",
    "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
    "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree",
]

SELF_TEST_CASE_COUNT = 8


class ValidationError(RuntimeError):
    """Raised when a required shared-surface marker is missing."""


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
                f"missing expected Phase 7 shared-surface marker in {path.as_posix()}: {snippet}"
            )


def require_current_repo_reality(repo_root: Path) -> None:
    missing_direct = [rel for rel in DIRECT_PACKET if not (repo_root / rel).exists()]
    if missing_direct:
        raise ValidationError(
            "direct-readback packet no longer matches the current tree: "
            + ", ".join(missing_direct)
        )

    present_broader = [
        rel for rel in MISSING_BROADER_PACKET if (repo_root / rel).exists()
    ]
    if present_broader:
        raise ValidationError(
            "broader packet entries are now present and the shared warning must be narrowed: "
            + ", ".join(present_broader)
        )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / TESTS_README_PATH, REQUIRED_TESTS_SNIPPETS)
    require_snippets(repo_root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS)
    require_current_repo_reality(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / TESTS_README_PATH, "\n".join(REQUIRED_TESTS_SNIPPETS) + "\n")
    write(root / SURVEY_PATH, "\n".join(REQUIRED_SURVEY_SNIPPETS) + "\n")
    write(root / Path(DIRECT_PACKET[-1]), "# current checker under test\n")


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
    with tempfile.TemporaryDirectory(prefix="phase7-shared-surface-") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0
        for path, snippet in [
            (root / TESTS_README_PATH, REQUIRED_TESTS_SNIPPETS[1]),
            (root / TESTS_README_PATH, REQUIRED_TESTS_SNIPPETS[4]),
            (root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS[0]),
            (root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS[4]),
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
        write(root / Path(MISSING_BROADER_PACKET[0]), "# returned broader packet member\n")
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected present broader packet file to fail")

        scaffold_repo(root)
        (root / TESTS_README_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing tests README to fail")

        scaffold_repo(root)
        (root / SURVEY_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing survey to fail")

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE7_RBTREE_ANCHOR_PACKET_SELF_TEST=pass")
    print(f"PHASE7_RBTREE_ANCHOR_PACKET_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE7_RBTREE_ANCHOR_PACKET=fail: {exc}")
        return 1

    print("PHASE7_RBTREE_ANCHOR_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
