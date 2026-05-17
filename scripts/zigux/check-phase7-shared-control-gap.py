#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("scripts/zigux/README.md")
RBTREE_SLICE_PATH = Path("Documentation/zigux/phase7-rbtree-slice.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")

DIRECT_PACKET = [
    "scripts/zigux/README.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

README_REQUIRED_SNIPPETS = [
    "Phase 7 flow - the current shared-control packet is directly readable again on current `master`:",
    "`python3 scripts/zigux/validate-phase7.py --self-test`, `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`, `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`, `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`, `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`, and `make -C zigux phase7-validate` replay the shipped Phase 7 wrapper, survey, and parity guards",
    "current `master` still ships no `samples/zigux/*string*`, `*cmdline*`, `*argv*`, or `*rbtree*` Phase 5 reference sample",
]

RBTREE_SLICE_REQUIRED_SNIPPETS = [
    "Current repo reality at the shared bundle level is now route-present rather than blocked:",
    "direct current `master` reads returned this slice note together with `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`.",
    "* `python3 scripts/zigux/validate-phase7.py`",
    "* `python3 scripts/zigux/check-phase7-make-wrapper.py`",
    "* `python3 scripts/zigux/check-phase7-build-wiring.py`",
    "* `zigux/tests/phase7_build.zig`",
    "* `zigux/Makefile`",
    "* `.github/workflows/zigux-bootstrap.yml`",
]

VALIDATOR_REQUIRED_SNIPPETS = [
    '"zigux/tests/phase7_string_helpers_sample_boundary.zig": [',
    '"scripts/zigux/validate-phase7.py",',
    '"scripts/zigux/check-phase7-make-wrapper.py",',
    '"scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",',
    '"scripts/zigux/check-phase7-build-wiring.py",',
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


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / README_PATH, README_REQUIRED_SNIPPETS)
    require_snippets(repo_root / RBTREE_SLICE_PATH, RBTREE_SLICE_REQUIRED_SNIPPETS)
    require_snippets(repo_root / VALIDATOR_PATH, VALIDATOR_REQUIRED_SNIPPETS)
    require_repo_reality(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / README_PATH, "\n".join(README_REQUIRED_SNIPPETS) + "\n")
    write(root / RBTREE_SLICE_PATH, "\n".join(RBTREE_SLICE_REQUIRED_SNIPPETS) + "\n")
    write(root / VALIDATOR_PATH, "\n".join(VALIDATOR_REQUIRED_SNIPPETS) + "\n")
    for rel in DIRECT_PACKET[3:]:
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
            (root / README_PATH, README_REQUIRED_SNIPPETS[1]),
            (root / RBTREE_SLICE_PATH, RBTREE_SLICE_REQUIRED_SNIPPETS[0]),
            (root / VALIDATOR_PATH, VALIDATOR_REQUIRED_SNIPPETS[3]),
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
        (root / README_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing README to fail")

        scaffold_repo(root)
        (root / RBTREE_SLICE_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing rbtree slice to fail")

        scaffold_repo(root)
        (root / VALIDATOR_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected missing validator to fail")

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
