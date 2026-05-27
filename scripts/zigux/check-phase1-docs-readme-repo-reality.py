#!/usr/bin/env python3
"""Guard the current Phase 1 docs-root repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
DOCS_README_REL = Path("Documentation/zigux/README.md")

REQUIRED_PRESENT_PATHS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
)

REQUIRED_MISSING_PATHS = (
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-installer-companion-checks.py",
    "scripts/zigux/validate-phase1.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

REQUIRED_MARKERS = (
    "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-string-review-packet.py` - `scripts/zigux/check-phase1-direct-owner-markers.py` - `scripts/zigux/check-phase1-shared-reminder-packet.py` - `scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "* `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase1_helpers.json`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zigux/tests/fixtures/phase1_replay_blockers.json` are directly readable on current `master` again, so keep the returned installer-viability, bench, parity-fixture, artifact-diff, fixture, manifest, and replay-blocker packet explicit from the docs root instead of leaving those surfaces in the older missing-route warning bucket.",
    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those older installer-review, validator-first, bench-route, and C-harness surfaces as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.",
    "* `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14, so keep that returned route inventory explicit here while the older Phase 1 wrapper names stay historical packet members rather than active docs-root proof.",
    "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
)

FORBIDDEN_FRAGMENTS = (
    "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `zigux/Makefile` - `zigux/tests/build.zig` - `zigux/tests/phase1_helpers.zig` - `zigux/tests/phase1_bench.zig` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/validate-phase1.py` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-parity.py` - `scripts/zigux/check-phase1-bench.py` - `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
    "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-phase1-installer-review-surfaces.py` - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
    "`python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`",
)

SAMPLE_DOCS_README = """# Zigux Documentation
This directory is the product documentation root for Zigux.
Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy
Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md`
Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-string-review-packet.py` - `scripts/zigux/check-phase1-direct-owner-markers.py` - `scripts/zigux/check-phase1-shared-reminder-packet.py` - `scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.
* `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase1_helpers.json`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zigux/tests/fixtures/phase1_replay_blockers.json` are directly readable on current `master` again, so keep the returned installer-viability, bench, parity-fixture, artifact-diff, fixture, manifest, and replay-blocker packet explicit from the docs root instead of leaving those surfaces in the older missing-route warning bucket.
* repeated authenticated reads on current `master` still return missing for `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those older installer-review, validator-first, bench-route, and C-harness surfaces as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.
* `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14, so keep that returned route inventory explicit here while the older Phase 1 wrapper names stay historical packet members rather than active docs-root proof.
* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.
"""


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in REQUIRED_PRESENT_PATHS:
        if not (root / relative_path).exists():
            missing.append(relative_path)
    return missing


def collect_unexpected_files(root: Path) -> list[str]:
    unexpected: list[str] = []
    for relative_path in REQUIRED_MISSING_PATHS:
        if (root / relative_path).exists():
            unexpected.append(relative_path)
    return unexpected


def collect_marker_issues(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(f"required:{count}:{marker}")
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"forbidden:{count}:{fragment}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_present:{path}" for path in collect_missing_files(root)]
    issues.extend(f"unexpected_missing:{path}" for path in collect_unexpected_files(root))
    docs_readme_path = root / DOCS_README_REL
    if not docs_readme_path.exists():
        issues.append(f"missing_docs_readme:{DOCS_README_REL}")
        return issues
    issues.extend(collect_marker_issues(read_text(docs_readme_path)))
    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE1_DOCS_README_REPO_REALITY=fail")
    for issue in issues:
        print(f"PHASE1_DOCS_README_REPO_REALITY_ISSUE={issue}")
    return 1


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / DOCS_README_REL, SAMPLE_DOCS_README)
    for relative_path in REQUIRED_PRESENT_PATHS:
        write_text(root / relative_path, "present\n")


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)
    print("PHASE1_DOCS_README_REPO_REALITY=pass")
    print(f"PHASE1_DOCS_README_REPO_REALITY_PRESENT_COUNT={len(REQUIRED_PRESENT_PATHS)}")
    print(f"PHASE1_DOCS_README_REPO_REALITY_MISSING_COUNT={len(REQUIRED_MISSING_PATHS)}")
    print(f"PHASE1_DOCS_README_REPO_REALITY_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE1_DOCS_README_REPO_REALITY_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_FRAGMENTS)}")
    return 0


def expect_exit(code: int, expected: int, label: str) -> None:
    if code != expected:
        raise SystemExit(f"{label}: expected exit {expected}, got {code}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_sample_root(root)
        expect_exit(run_check(root), 0, "sample_root")

        missing_present_root = root / "missing_present"
        write_sample_root(missing_present_root)
        (missing_present_root / "scripts/zigux/check-phase1-parity.py").unlink()
        expect_exit(run_check(missing_present_root), 1, "missing_present")

        missing_marker_root = root / "missing_marker"
        write_sample_root(missing_marker_root)
        docs_path = missing_marker_root / DOCS_README_REL
        docs_path.write_text(
            docs_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/artifact_diff.py`, ", "", 1
            ),
            encoding="utf-8",
        )
        expect_exit(run_check(missing_marker_root), 1, "missing_marker")

        forbidden_fragment_root = root / "forbidden_fragment"
        write_sample_root(forbidden_fragment_root)
        docs_path = forbidden_fragment_root / DOCS_README_REL
        docs_path.write_text(
            docs_path.read_text(encoding="utf-8")
            + "\n"
            + FORBIDDEN_FRAGMENTS[2]
            + "\n",
            encoding="utf-8",
        )
        expect_exit(run_check(forbidden_fragment_root), 1, "forbidden_fragment")

        unexpected_missing_root = root / "unexpected_missing"
        write_sample_root(unexpected_missing_root)
        write_text(
            unexpected_missing_root / "scripts/zigux/check-phase1-installer-review-surfaces.py",
            "unexpected\n",
        )
        expect_exit(run_check(unexpected_missing_root), 1, "unexpected_missing")

    print("PHASE1_DOCS_README_REPO_REALITY_SELF_TEST=pass")
    print("PHASE1_DOCS_README_REPO_REALITY_SELF_TEST_CASE_COUNT=5")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 docs-root repo-reality packet."
    )
    parser.add_argument("--root", help="Repository root to validate.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a sample passing root to the provided directory and exit.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0
    return run_check(repo_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
