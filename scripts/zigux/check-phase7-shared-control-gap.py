#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
STRING_HELPERS_SLICE_PATH = Path("Documentation/zigux/phase7-string-helpers-slice.md")
CMDLINE_SLICE_PATH = Path("Documentation/zigux/phase7-cmdline-slice.md")
WORKSPACE_BOOTSTRAP_SURVEY_PATH = Path("Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md")
REVIEW_CHECKPOINT_PATH = Path("Documentation/zigux/phase7-shared-control-review-checkpoint.md")
BUILD_WIRING_CHECKER_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")
SHARED_SURFACE_VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")

DIRECT_PACKET = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md",
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
    "phase7-string-helpers-format-boundary:",
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
    "- cmdline packet, lane `P7-L08`:",
    "keep helper-local `string_helpers` slice, helper, dedicated replay, survey, manifest, sample-boundary, and checker drift out of `P7-Y05`; only route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, or shared-build reminders back to the shared-control packet",
    "scheduled anti-overlap note: recurring helper-local lane `P7-Y01` is same-family `string_helpers` follow-through, not a separate Phase 7 helper packet; keep it narrowed to `lib/string_helpers.zig` and its directly coupled slice, replay, survey, manifest, sample-boundary, or checker surfaces while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay with `P7-Y05`",
    "keep `Documentation/zigux/phase7-string-helpers-slice.md` with the string_helpers helper-local lane family instead of the shared-control packet while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay routed to `P7-Y05`.",
    "Current lane evidence also keeps `P7-Y01` inside this same helper-local family, while `P7-L04` remains the shared-control workspace-bootstrap follow-through for validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminder drift rather than a second helper-local string_helpers packet.",
    "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "- `scripts/zigux/check-phase7-shared-control-gap.py`",
    "- `scripts/zigux/validate-phase7.py`",
    "the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` still exposes only the narrow `phase7-validate` foothold and still omits `phase7-test`, `phase7`, and the helper-local Phase 7 wrapper routes. Keep shared-control truthfulness anchored to that returned validator foothold, those returned checker hooks, the readable non-owner build shard, and the still-absent broader wrapper boundaries instead of claiming the older workflow-backed test routes have returned.",
    "so `P7-L08` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.",
    "Treat recurring lane `P7-L04` as the shared-control workspace-bootstrap follow-through; keep it narrowed to `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`, `Documentation/zigux/phase7-shared-control-review-checkpoint.md`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-shared-control-gap.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the readable non-owner `zigux/tests/phase7_build.zig` instead of reassigning that lane to helper-local string_helpers ownership.",
    "treat recurring helper-local lane `P7-Y01` as same-family follow-through inside that one packet rather than as a separate helper family",
]

FORBIDDEN_SEQUENCING_SNIPPETS = [
    "- cmdline packet, lane `P7-L10`:",
    "so `P7-L10` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.",
    "scheduled anti-overlap note: recurring helper-local lanes `P7-L04` and `P7-Y01` are same-family `string_helpers` follow-through, not separate Phase 7 helper packets; keep both lanes narrowed to `lib/string_helpers.zig` and its directly coupled slice, replay, survey, manifest, sample-boundary, or checker surfaces",
    "Current lane evidence also keeps `P7-L04` and `P7-Y01` inside this same helper-local family rather than treating them as two separate helper packets.",
    "Treat recurring helper-local lanes `P7-L04` and `P7-Y01` as same-family string_helpers follow-through inside that one helper packet, not as separate Phase 7 helper lanes; keep `P7-L04` narrowed to string_helpers slice, survey, manifest, sample-boundary, or checker drift and keep `P7-Y01` narrowed to `lib/string_helpers.zig` ownership or directly coupled helper-local truthfulness while both lanes still route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build drift back to `P7-Y05`.",
    "treat recurring helper-local lanes `P7-L04` and `P7-Y01` as same-family sublanes of that one packet rather than as separate helper families",
]

REQUIRED_REVIEW_SNIPPETS = [
    "# Phase 7 Shared Control Review Checkpoint",
    "`scripts/zigux/validate-phase7.py`",
    "Keep `scripts/zigux/check-phase7-make-wrapper.py` framed as parked reminder vocabulary until a fresh current-`master` reread proves that path returned.",
    "Keep `zigux/tests/phase7_build.zig` framed as readable non-owner build evidence only; it does not by itself prove that `phase7-test`, `phase7`, or workflow-backed Phase 7 routes returned.",
    "Keep `phase7-test` and `phase7` framed as absent wrapper-route vocabulary",
    "`.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate` and `make -C zigux phase7-test` steps.",
    "`Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`",
    "Keep `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md` framed as the roadmap-vs-bootstrap gap note: it can claim the four roadmap-backed helper anchors and the narrow `phase7-validate` foothold, but it must not promote absent `phase7-test`, `phase7`, or workflow-backed Phase 7 test routes into current proof.",
]

REQUIRED_WORKSPACE_BOOTSTRAP_SURVEY_SNIPPETS = [
    "# Phase 7 Runtime Workspace Bootstrap Gap Survey",
    "`PHASE7_STATUS=shared_control_workspace_bootstrap_gap_survey`",
    "`PHASE7_LANE_KEY=P7-L01`",
    "survey focus: roadmap-backed runtime leaf-library anchors versus current workspace/bootstrap glue on `master`",
    "the Phase 7 roadmap anchors remain `lib/string_helpers.c`, `lib/cmdline.c`, `lib/argv_split.c`, and `lib/rbtree.c`",
    "`zigux/tests/phase7_build.zig` wires all four returned helpers into the shared Phase 7 build graph",
    "`scripts/zigux/validate-phase7.py` plus `make -C zigux phase7-validate` keep one returned shared validation foothold explicit on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` self-tests `scripts/zigux/check-phase7-shared-control-gap.py` and `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "the readable `zigux/Makefile` still exposes only `phase7-validate` for the shared Phase 7 packet",
    "current `master` still does not materialize `phase7-test` or `phase7` in `zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `zig build test --build-file zigux/tests/phase7_build.zig --summary all` steps",
    "the roadmap-backed helper anchors are present, but the shared workspace bootstrap glue remains a narrow validation foothold rather than a returned end-to-end Phase 7 workspace route",
    "treat that gap as shared-control reminder debt, not as missing helper-local proof for `string_helpers`, `cmdline`, `argv_split`, or `rbtree`",
]

REQUIRED_STRING_HELPERS_SNIPPETS = [
    "shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes",
    "Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up",
    "- do not count `scripts/zigux/validate-phase7.py`",
]

REQUIRED_CMDLINE_SLICE_SNIPPETS = [
    "PHASE7_LANE_KEY=P7-L08",
    "shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons",
]

REQUIRED_MAKEFILE_LINES = [
    "phase7-validate:",
    "$(PYTHON) scripts/zigux/validate-phase7.py",
]

SELF_TEST_CASE_COUNT = 23


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected marker in {path.as_posix()}: {snippet}")


def require_exact_lines(path: Path, lines: list[str]) -> None:
    content = read_text(path)
    for line in lines:
        count = count_exact_lines(content, line)
        if count == 0:
            raise ValidationError(f"missing expected line in {path.as_posix()}: {line}")
        if count != 1:
            raise ValidationError(f"duplicate expected line in {path.as_posix()}: {line}")


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
    require_absent_markers(repo_root / SEQUENCING_NOTE_PATH, FORBIDDEN_SEQUENCING_SNIPPETS)
    require_snippets(repo_root / WORKSPACE_BOOTSTRAP_SURVEY_PATH, REQUIRED_WORKSPACE_BOOTSTRAP_SURVEY_SNIPPETS)
    require_snippets(repo_root / STRING_HELPERS_SLICE_PATH, REQUIRED_STRING_HELPERS_SNIPPETS)
    require_snippets(repo_root / CMDLINE_SLICE_PATH, REQUIRED_CMDLINE_SLICE_SNIPPETS)
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
    write(root / WORKSPACE_BOOTSTRAP_SURVEY_PATH, "\n".join(REQUIRED_WORKSPACE_BOOTSTRAP_SURVEY_SNIPPETS) + "\n")
    write(root / STRING_HELPERS_SLICE_PATH, "\n".join(REQUIRED_STRING_HELPERS_SNIPPETS) + "\n")
    write(root / CMDLINE_SLICE_PATH, "\n".join(REQUIRED_CMDLINE_SLICE_SNIPPETS) + "\n")
    write(root / REVIEW_CHECKPOINT_PATH, "\n".join(REQUIRED_REVIEW_SNIPPETS) + "\n")
    write(root / BUILD_WIRING_CHECKER_PATH, "\n".join(["FORBIDDEN_MAKEFILE_MARKERS", '"phase7-test:"', '"phase7:"']) + "\n")
    write(root / SHARED_SURFACE_VALIDATOR_PATH, "make -C zigux phase7-validate\n")
    for rel in DIRECT_PACKET[3:]:
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
    updated = original.replace(old, new, 1) if old else original + new
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
            (SEQUENCING_NOTE_PATH, REQUIRED_SEQUENCING_SNIPPETS[4], "recurring helper-local lane `P7-Y99`"),
            (SEQUENCING_NOTE_PATH, REQUIRED_SEQUENCING_SNIPPETS[6], "Current lane evidence also keeps `P7-L04` and `P7-Y01` inside this same helper-local family rather than treating them as two separate helper packets."),
            (SEQUENCING_NOTE_PATH, REQUIRED_SEQUENCING_SNIPPETS[11], "Treat recurring lane `P7-L04` as helper-local drift."),
            (SEQUENCING_NOTE_PATH, REQUIRED_SEQUENCING_SNIPPETS[12], "treat recurring helper-local lanes `P7-L04` and `P7-Y01` as same-family sublanes of that one packet rather than as separate helper families"),
            (REVIEW_CHECKPOINT_PATH, REQUIRED_REVIEW_SNIPPETS[2], "returned narrow"),
            (STRING_HELPERS_SLICE_PATH, REQUIRED_STRING_HELPERS_SNIPPETS[2], "- do not count `scripts/zigux/check-phase7-build-wiring.py`"),
            (CMDLINE_SLICE_PATH, REQUIRED_CMDLINE_SLICE_SNIPPETS[0], "PHASE7_LANE_KEY=P7-L10"),
            (WORKFLOW_PATH, REQUIRED_WORKFLOW_LINES[0], "run: true"),
            (WORKFLOW_PATH, "", "run: make -C zigux phase7-test\n"),
            (MAKEFILE_PATH, REQUIRED_MAKEFILE_LINES[0], "phase7:\n"),
            (MAKEFILE_PATH, "", "phase7-test:\n"),
            (MAKEFILE_PATH, "", "phase7-string-helpers-format-boundary:\n"),
            (SHARED_SURFACE_VALIDATOR_PATH, "make -C zigux phase7-validate", "make -C zigux phase7"),
        ]
        for rel, old, new in cases:
            scaffold_repo(root)
            expect_failure(root, rel, old, new)
            cases_run += 1

        for forbidden in FORBIDDEN_SEQUENCING_SNIPPETS[:4]:
            scaffold_repo(root)
            write(root / SEQUENCING_NOTE_PATH, read_text(root / SEQUENCING_NOTE_PATH) + forbidden + "\n")
            try:
                validate(root)
            except ValidationError:
                cases_run += 1
            else:
                raise AssertionError("expected validation failure")

        scaffold_repo(root)
        write(root / WORKFLOW_PATH, read_text(root / WORKFLOW_PATH) + REQUIRED_WORKFLOW_LINES[0] + "\n")
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected validation failure")

        scaffold_repo(root)
        write(root / MAKEFILE_PATH, read_text(root / MAKEFILE_PATH) + "\t$(PYTHON) scripts/zigux/validate-phase7.py\n")
        try:
            validate(root)
        except ValidationError:
            cases_run += 1
        else:
            raise AssertionError("expected validation failure")

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
    print(f"PHASE7_SHARED_CONTROL_GAP_DIRECT_PACKET_COUNT={len(DIRECT_PACKET)}")
    print(f"PHASE7_SHARED_CONTROL_GAP_PARKED_PATH_COUNT={len(PARKED_SHARED_CONTROL_PATHS)}")
    print(f"PHASE7_SHARED_CONTROL_GAP_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
