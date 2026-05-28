#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

LANE_NOTE = Path("Documentation/zigux/phase2-toolchain-lane-sequencing.md")
DOCS_README = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")

LANE_NOTE_MARKERS = (
    "shared backlog truthfulness lane `P2-Y12` owns turning current cross-family backlog evidence into one bounded next-safe-step correction",
    "shared backlog truthfulness under `P2-Y12` owns only the next-safe-step correction when the shared packet names wider direct replay coverage than the live Makefile and closure note actually ship; keep that lane parked unless a shared reminder, README, validator, or checker surface starts pointing at the wrong same-tranche follow-through, not at tool-local behavior inside `fixdep.zig`, `genksyms.zig`, `conf_bridge.zig`, `confdata_bridge.zig`, or `mk_elfconfig.zig`",
    "The remaining shared anti-overlap risk is narrower:",
    "- the remaining shared correction path is therefore narrower than a fresh sequencing-note rewrite: reopen `P2-Y10` only for multi-family route, manifest, validator, or reminder-surface drift, and reopen `P2-Y12` only when a shared backlog note points at the wrong next safe Phase 2 follow-through",
    "3. Reopen `P2-Y12` only when current `master` evidence shows a shared backlog or review surface pointing at the wrong next step; keep that lane limited to the smallest owner-map, README, or checker truthfulness repair that turns the backlog into one bounded follow-through.",
)

DOCS_README_MARKERS = (
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

BOOTSTRAP_NOTE_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, bootstrap workflow-route truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
)

BOOTSTRAP_NOTE_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "historical packet members until same-lane work rematerializes them on `master`",
)

REVIEW_CHECKLIST_MARKERS = (
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
)

REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
)

TESTS_README_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(root: Path, rel_path: Path) -> str:
    path = root / rel_path
    if not path.is_file():
        raise SystemExit(f"required file missing: {rel_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def collect_missing(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    lane_note_text = read_text(root, LANE_NOTE)
    docs_readme_text = read_text(root, DOCS_README)
    bootstrap_note_text = read_text(root, BOOTSTRAP_NOTE)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    tests_readme_text = read_text(root, TESTS_README)

    issues.extend(collect_missing(lane_note_text, LANE_NOTE_MARKERS, "MISSING_LANE_NOTE_MARKER"))
    issues.extend(collect_missing(docs_readme_text, DOCS_README_MARKERS, "MISSING_DOCS_README_MARKER"))
    issues.extend(collect_missing(bootstrap_note_text, BOOTSTRAP_NOTE_MARKERS, "MISSING_BOOTSTRAP_NOTE_MARKER"))
    issues.extend(collect_forbidden(bootstrap_note_text, BOOTSTRAP_NOTE_FORBIDDEN_MARKERS, "FORBIDDEN_BOOTSTRAP_NOTE_MARKER"))
    issues.extend(collect_missing(review_checklist_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKER"))
    issues.extend(collect_forbidden(review_checklist_text, REVIEW_CHECKLIST_FORBIDDEN_MARKERS, "FORBIDDEN_REVIEW_CHECKLIST_MARKER"))
    issues.extend(collect_missing(tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_good_tree(root: Path) -> None:
    write_text(root / LANE_NOTE, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root / DOCS_README, "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(root / BOOTSTRAP_NOTE, "\n".join(BOOTSTRAP_NOTE_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")


def run_self_test() -> int:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_backlog_truthfulness_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:good_tree")
        cases_run += 1

        build_good_tree(root)
        path = root / LANE_NOTE
        path.write_text(path.read_text(encoding="utf-8").replace(LANE_NOTE_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_LANE_NOTE_MARKER", LANE_NOTE_MARKERS[0]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:lane_note")
        cases_run += 1

        build_good_tree(root)
        path = root / DOCS_README
        path.write_text(path.read_text(encoding="utf-8").replace(DOCS_README_MARKERS[1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_DOCS_README_MARKER", DOCS_README_MARKERS[1]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:docs_readme")
        cases_run += 1

        build_good_tree(root)
        path = root / BOOTSTRAP_NOTE
        path.write_text(path.read_text(encoding="utf-8").replace(BOOTSTRAP_NOTE_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_BOOTSTRAP_NOTE_MARKER", BOOTSTRAP_NOTE_MARKERS[0]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:bootstrap_note")
        cases_run += 1

        build_good_tree(root)
        path = root / BOOTSTRAP_NOTE
        path.write_text(path.read_text(encoding="utf-8") + BOOTSTRAP_NOTE_FORBIDDEN_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        if ("FORBIDDEN_BOOTSTRAP_NOTE_MARKER", BOOTSTRAP_NOTE_FORBIDDEN_MARKERS[0]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:bootstrap_forbidden")
        cases_run += 1

        build_good_tree(root)
        path = root / REVIEW_CHECKLIST
        path.write_text(path.read_text(encoding="utf-8").replace(REVIEW_CHECKLIST_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_REVIEW_CHECKLIST_MARKER", REVIEW_CHECKLIST_MARKERS[0]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:review_checklist")
        cases_run += 1

        build_good_tree(root)
        path = root / REVIEW_CHECKLIST
        path.write_text(path.read_text(encoding="utf-8") + REVIEW_CHECKLIST_FORBIDDEN_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        if ("FORBIDDEN_REVIEW_CHECKLIST_MARKER", REVIEW_CHECKLIST_FORBIDDEN_MARKERS[0]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:review_forbidden")
        cases_run += 1

        build_good_tree(root)
        path = root / TESTS_README
        path.write_text(path.read_text(encoding="utf-8").replace(TESTS_README_MARKERS[1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_TESTS_README_MARKER", TESTS_README_MARKERS[1]) not in issues:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:tests_readme")
        cases_run += 1

        build_good_tree(root)
        (root / LANE_NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise
        else:
            raise SystemExit("phase2-toolchain-backlog-truthfulness:self-test:missing_file")
        cases_run += 1

    print("PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 backlog-truthfulness guidance aligned with the live toolchain packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact passing sample tree to the given directory",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_good_tree(args.write_sample_root)
        print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS=pass")
    print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_LANE_MARKER_COUNT={len(LANE_NOTE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_DOCS_MARKER_COUNT={len(DOCS_README_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_NOTE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_BACKLOG_TRUTHFULNESS_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
