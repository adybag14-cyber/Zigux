#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
STRING_HELPERS_SLICE_PATH = Path("Documentation/zigux/phase7-string-helpers-slice.md")
REVIEW_CHECKPOINT_PATH = Path("Documentation/zigux/phase7-shared-control-review-checkpoint.md")
BUILD_WIRING_CHECKER_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")
SHARED_SURFACE_VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")

DIRECT_PACKET = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-shared-control-review-checkpoint.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "samples/zigux/README.md",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-shared-control-gap.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/validate-phase7.py",
]

PARKED_SHARED_CONTROL_PATHS = [
    "scripts/zigux/check-phase7-make-wrapper.py",
]

READABLE_NON_OWNER_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase7_build.zig",
]

ABSENT_WORKFLOW_MARKERS = [
    "Validate Phase 7 runtime helper gates",
    "Run Phase 7 runtime helper tests",
    "make -C zigux phase7-validate",
    "make -C zigux phase7-test",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
]

ABSENT_MAKEFILE_MARKERS = [
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
]

REQUIRED_WORKFLOW_LINES = [
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
]

REQUIRED_SEQUENCING_SNIPPETS = [
    "- shared control-surface packet, lane `P7-Y05`:",
    "- string_helpers packet, helper-local lane family:",
    "keep helper-local `string_helpers` slice, helper, dedicated replay, survey, manifest, sample-boundary, and checker drift out of `P7-Y05`; only route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, or shared-build reminders back to the shared-control packet",
    "keep `Documentation/zigux/phase7-string-helpers-slice.md` with the string_helpers helper-local lane family instead of the shared-control packet while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay routed to `P7-Y05`.",
    "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "- `scripts/zigux/check-phase7-shared-control-gap.py`",
    "- `scripts/zigux/validate-phase7.py`",
    "the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` still exposes only the narrow `phase7-validate` foothold and still omits `phase7-test`, `phase7`, and the helper-local Phase 7 wrapper routes. Keep shared-control truthfulness anchored to that returned validator foothold, those returned checker hooks, the readable non-owner build shard, and the still-absent broader wrapper boundaries instead of claiming the older workflow-backed test routes have returned.",
]

REQUIRED_REVIEW_SNIPPETS = [
    "# Phase 7 Shared Control Review Checkpoint",
    "`scripts/zigux/validate-phase7.py`",
    "Keep `scripts/zigux/check-phase7-make-wrapper.py` framed as parked reminder vocabulary until a fresh current-`master` reread proves that path returned.",
    "Keep `zigux/tests/phase7_build.zig` framed as readable non-owner build evidence only; it does not by itself prove that `phase7-test`, `phase7`, or workflow-backed Phase 7 routes returned.",
    "Keep `phase7-test` and `phase7` framed as absent wrapper-route vocabulary",
    "`.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate` and `make -C zigux phase7-test` steps.",
]

REQUIRED_STRING_HELPERS_SNIPPETS = [
    "shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes",
    "Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up",
    "- do not count `scripts/zigux/validate-phase7.py`",
]

REQUIRED_MAKEFILE_LINES = [
    "phase7-validate:",
    "$(PYTHON) scripts/zigux/validate-phase7.py",
]

SELF_TEST_CASE_COUNT = 12


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected marker in {path.as_posix()}: {snippet}")


def require_exact_lines(path: Path, lines: list[str]) -> None:
    content_lines = {line.strip() for line in read_text(path).splitlines()}
    for line in lines:
        if line.strip() not in content_lines:
            raise ValidationError(f"missing expected line in {path.as_posix()}: {line}")


def require_absent_markers(path: Path, markers: list[str]) -> None:
    content = read_text(path)
    for marker in markers:
        if marker in content:
            raise ValidationError(f"unexpected stale marker in {path.as_posix()}: {marker}")


def require_repo_reality(repo_root: Path) -> None:
    missing_direct = [rel for rel in DIRECT_PACKET if not (repo_root / rel).exists()]
    if missing_direct:
        raise ValidationError("direct packet drift: " + ", ".join(missing_direct))

    returned_parked = [rel for rel in PARKED_SHARED_CONTROL_PATHS if (repo_root / rel).exists()]
    if returned_parked:
        raise ValidationError("parked shared-control paths unexpectedly returned: " + ", ".join(returned_parked))

    missing_non_owner = [rel for rel in READABLE_NON_OWNER_FILES if not (repo_root / rel).exists()]
    if missing_non_owner:
        raise ValidationError("missing non-owner shared-control files: " + ", ".join(missing_non_owner))

    require_absent_markers(repo_root / WORKFLOW_PATH, ABSENT_WORKFLOW_MARKERS)
    require_absent_markers(repo_root / MAKEFILE_PATH, ABSENT_MAKEFILE_MARKERS)
    require_exact_lines(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_LINES)


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SEQUENCING_NOTE_PATH, REQUIRED_SEQUENCING_SNIPPETS)
    require_snippets(repo_root / STRING_HELPERS_SLICE_PATH, REQUIRED_STRING_HELPERS_SNIPPETS)
    require_snippets(repo_root / REVIEW_CHECKPOINT_PATH, REQUIRED_REVIEW_SNIPPETS)
    require_snippets(repo_root / BUILD_WIRING_CHECKER_PATH, ["FORBIDDEN_MAKEFILE_MARKERS", '"phase7-test:"', '"phase7:"'])
    require_snippets(repo_root / SHARED_SURFACE_VALIDATOR_PATH, ["make -C zigux phase7-validate"])
    require_exact_lines(repo_root / WORKFLOW_PATH, REQUIRED_WORKFLOW_LINES)
    require_repo_reality(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SEQUENCING_NOTE_PATH, "\n".join(REQUIRED_SEQUENCING_SNIPPETS) + "\n")
    write(root / STRING_HELPERS_SLICE_PATH, "\n".join(REQUIRED_STRING_HELPERS_SNIPPETS) + "\n")
    write(root / REVIEW_CHECKPOINT_PATH, "\n".join(REQUIRED_REVIEW_SNIPPETS) + "\n")
    write(root / BUILD_WIRING_CHECKER_PATH, "\n".join(["FORBIDDEN_MAKEFILE_MARKERS", '"phase7-test:"', '"phase7:"']) + "\n")
    write(root / SHARED_SURFACE_VALIDATOR_PATH, "make -C zigux phase7-validate\n")
    for rel in DIRECT_PACKET[2:]:
        path = root / Path(rel)
        if path.exists():
            continue
        write(path, "# direct phase7 shared-control packet file\n")
    write(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write(root / MAKEFILE_PATH, "phase7-validate:\n\t$(PYTHON) scripts/zigux/validate-phase7.py\n")
    write(root / BUILD_PATH, "// readable non-owner build shard\n")


def expect_failure(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    original = read_text(path)
    if old:
        updated = original.replace(old, new, 1)
    else:
        updated = original + new
    write(path, updated)
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase7_shared_control_gap_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0
        cases = [
            (SEQUENCING_NOTE_PATH, REQUIRED_SEQUENCING_SNIPPETS[3], "returned narrow", ""),
            (REVIEW_CHECKPOINT_PATH, REQUIRED_REVIEW_SNIPPETS[2], "returned narrow", ""),
            (STRING_HELPERS_SLICE_PATH, REQUIRED_STRING_HELPERS_SNIPPETS[2], "- do not count `scripts/zigux/check-phase7-build-wiring.py`", ""),
            (WORKFLOW_PATH, REQUIRED_WORKFLOW_LINES[0], "run: true", ""),
            (WORKFLOW_PATH, "", "run: make -C zigux phase7-test\n", ""),
            (MAKEFILE_PATH, REQUIRED_MAKEFILE_LINES[0], "phase7:\n", ""),
            (MAKEFILE_PATH, "", "phase7-test:\n", ""),
            (SHARED_SURFACE_VALIDATOR_PATH, "make -C zigux phase7-validate", "make -C zigux phase7", ""),
        ]
        for rel, old, new, _ in cases:
            scaffold_repo(root)
            expect_failure(root, rel, old, new)
            cases_run += 1

        scaffold_repo(root)
        write(root / PARKED_SHARED_CONTROL_PATHS[0], "# unexpectedly returned parked path\n")
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected validation failure")

        scaffold_repo(root)
        (root / BUILD_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected validation failure")

        scaffold_repo(root)
        (root / SHARED_SURFACE_VALIDATOR_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected validation failure")

        scaffold_repo(root)
        (root / WORKFLOW_PATH).unlink()
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected validation failure")

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass")
    print(f"PHASE7_SHARED_CONTROL_GAP_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
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
    print(f"PHASE7_SHARED_CONTROL_GAP_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
