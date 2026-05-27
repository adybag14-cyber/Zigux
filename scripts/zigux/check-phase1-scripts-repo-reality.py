#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_REL = Path("scripts/zigux/README.md")

REQUIRED_PRESENT_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase1-parity.py`",
    "`scripts/zigux/artifact_diff.py`",
    "`zigux/tests/fixtures/phase1_helpers.json`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`zigux/tests/fixtures/phase1_replay_blockers.json`",
)

REQUIRED_MISSING_MARKERS = (
    "`scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`scripts/zigux/check-phase1-installer-companion-checks.py`",
    "`scripts/zigux/validate-phase1.py`",
    "`zigux/tests/phase1_bench.zig`",
    "`zigux/tests/fixtures/phase1_bench_expectations.json`",
    "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
)

FORBIDDEN_MISSING_MARKERS = (
    "still return missing for `scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase1-parity.py` is missing",
    "still return missing for `scripts/zigux/check-phase1-parity.py`",
    "`scripts/zigux/artifact_diff.py` is missing",
    "still return missing for `scripts/zigux/artifact_diff.py`",
    "`zigux/tests/fixtures/phase1_helpers.json` is missing",
    "`zigux/tests/fixtures/phase1_helper_manifest.json` is missing",
    "`zigux/tests/fixtures/phase1_replay_blockers.json` is missing",
)

REQUIRED_SENTENCE_SNIPPETS = (
    "current `master` directly serves `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase1_helpers.json`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zigux/tests/fixtures/phase1_replay_blockers.json`",
    "keep the remaining Phase 1 scripts-root reminder follow-through focused on the older validator-first, bench-route, and replay routes",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    readme = root / README_REL
    ensure(readme.exists(), f"missing:{README_REL.as_posix()}", issues)
    if issues:
        return issues

    text = read_text(readme)

    for marker in REQUIRED_PRESENT_MARKERS:
        ensure(marker in text, f"missing_present_marker:{marker}", issues)
    for marker in REQUIRED_MISSING_MARKERS:
        ensure(marker in text, f"missing_gap_marker:{marker}", issues)
    for marker in FORBIDDEN_MISSING_MARKERS:
        ensure(marker not in text, f"stale_missing_marker:{marker}", issues)
    for marker in REQUIRED_SENTENCE_SNIPPETS:
        ensure(marker in text, f"missing_sentence_snippet:{marker}", issues)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_SCRIPTS_REPO_REALITY=fail")
        for issue in issues:
            print(f"PHASE1_SCRIPTS_REPO_REALITY_ISSUE={issue}")
        return 1

    print("PHASE1_SCRIPTS_REPO_REALITY=pass")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_PRESENT_COUNT={len(REQUIRED_PRESENT_MARKERS)}")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_MISSING_COUNT={len(REQUIRED_MISSING_MARKERS)}")
    print(
        "PHASE1_SCRIPTS_REPO_REALITY_PRESENT_MARKERS="
        + ",".join(marker.strip("`") for marker in REQUIRED_PRESENT_MARKERS)
    )
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_readme(*, stale_install_missing: bool = False, stale_parity_missing: bool = False) -> str:
    if stale_install_missing:
        opening = (
            "- repeated authenticated reads on current `master` still return missing for "
            "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, "
            "`scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, "
            "`zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and "
            "`zigux/tests/fixtures/phase1_helpers_c_harness.c`"
        )
        gaps = ""
    elif stale_parity_missing:
        opening = (
            "- repeated authenticated reads on current `master` still return missing for "
            "`scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, "
            "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, "
            "`zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and "
            "`zigux/tests/phase1_helpers_c_harness.c`"
        )
        gaps = ""
    else:
        opening = (
            "- current `master` directly serves `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-bench.py`, "
            "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/artifact_diff.py`, "
            "`zigux/tests/fixtures/phase1_helpers.json`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and "
            "`zigux/tests/fixtures/phase1_replay_blockers.json`, so keep the remaining Phase 1 scripts-root reminder "
            "follow-through focused on the older validator-first, bench-route, and replay routes that still stay absent "
            "instead of modeling those directly readable paths and the broader parity-fixture companion packet as repo-reality gaps"
        )
        gaps = (
            "- repeated authenticated reads on current `master` still return missing for "
            "`scripts/zigux/check-phase1-installer-review-surfaces.py`, "
            "`scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, "
            "`zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and "
            "`zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, "
            "bench, and replay routes as historical packet members that need fresh re-materialization before they are reused "
            "here as direct current-`master` reminder evidence"
        )
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            opening,
            gaps,
            "",
        )
    )


def build_sample_root(root: Path) -> None:
    write_text(root / README_REL, build_sample_readme())


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="phase1_scripts_repo_reality_") as tmp_dir:
        tmp = Path(tmp_dir)
        for name, mutate in (
            ("good", lambda root: None),
            ("missing_readme", lambda root: (root / README_REL).unlink()),
            ("stale_install_missing", lambda root: write_text(root / README_REL, build_sample_readme(stale_install_missing=True))),
            ("stale_parity_missing", lambda root: write_text(root / README_REL, build_sample_readme(stale_parity_missing=True))),
            ("missing_present_marker", lambda root: write_text(root / README_REL, build_sample_readme().replace("`scripts/zigux/install-zig.py`, ", "", 1))),
            ("missing_fixture_marker", lambda root: write_text(root / README_REL, build_sample_readme().replace("`zigux/tests/fixtures/phase1_replay_blockers.json`", "`zigux/tests/fixtures/phase1_replay_blockers_old.json`", 1))),
            ("missing_gap_marker", lambda root: write_text(root / README_REL, build_sample_readme().replace("`zigux/tests/fixtures/phase1_helpers_c_harness.c`", "`zigux/tests/phase1_harness_gone.c`", 1))),
            ("missing_sentence_snippet", lambda root: write_text(root / README_REL, build_sample_readme().replace("keep the remaining Phase 1 scripts-root reminder follow-through focused on the older validator-first, bench-route, and replay routes that still stay absent ", "", 1))),
        ):
            case_root = tmp / name
            build_sample_root(case_root)
            mutate(case_root)
            ok = run_check(case_root) == (0 if name == "good" else 1)
            cases.append((name, ok))

    failed = [name for name, ok in cases if not ok]
    if failed:
        print("PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST_CASE_COUNT={len(cases)}")
    print(
        "PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST_CASES="
        + ",".join(name for name, _ in cases)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 1 scripts-root repo-reality reminder."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
