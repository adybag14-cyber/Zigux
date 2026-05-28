#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF = Path(__file__).resolve()
ROOT = SELF.parents[2] if len(SELF.parents) >= 3 else Path.cwd()

TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
PARITY_CHECKER = Path("scripts/zigux/check-phase1-parity.py")
HELPER_REPLAY = Path("zigux/tests/phase1_helpers.zig")
HELPER_BUILD = Path("zigux/tests/phase1_helpers_build.zig")

REQUIRED_FILES = (
    TESTS_README,
    SCRIPTS_README,
    WORKFLOW,
    PARITY_CHECKER,
    HELPER_REPLAY,
    HELPER_BUILD,
)

TESTS_README_MARKERS = (
    "  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
    "  * keep `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
)

SCRIPTS_README_MARKERS = (
    "- `check-phase1-parity.py` compares the bounded helper outputs against the committed Phase 1 fixture corpus so `bitmap`, `find_bit`, `string`, `rbtree`, and the rest of the closed helper set stay pinned to the current C behavior. - `check-phase1-bench.py` verifies the benchmark smoke outputs recorded in `zigux/tests/fixtures/phase1_bench_expectations.json` so the helper hot loops keep their checksum-backed replay contract.",
    "- `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` keep a focused fixture-backed helper parity replay anchor on current `master` without widening back into the older validator-first, bench, or installer-backed closure stack",
)

WORKFLOW_MARKERS = (
    "      - name: Check Phase 1 helper parity",
    "        run: python3 scripts/zigux/check-phase1-parity.py",
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_count_issues(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    issues: list[str] = []
    for marker in markers:
        count = lines.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing:{rel.as_posix()}")
    if issues:
        return issues

    issues.extend(
        collect_count_issues(read_text(root / TESTS_README), "tests_readme", TESTS_README_MARKERS)
    )
    issues.extend(
        collect_count_issues(read_text(root / SCRIPTS_README), "scripts_readme", SCRIPTS_README_MARKERS)
    )
    issues.extend(
        collect_count_issues(read_text(root / WORKFLOW), "workflow", WORKFLOW_MARKERS)
    )
    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_TESTS_README_PARITY_PACKET=fail")
        for issue in issues:
            print(f"PHASE1_TESTS_README_PARITY_PACKET_ISSUE={issue}")
        return 1

    print("PHASE1_TESTS_README_PARITY_PACKET=pass")
    print(f"PHASE1_TESTS_README_PARITY_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_TESTS_README_PARITY_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE1_TESTS_README_PARITY_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE1_TESTS_README_PARITY_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print("PHASE1_TESTS_README_PARITY_PACKET_ROUTE=zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(root / TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / SCRIPTS_README, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / WORKFLOW, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / PARITY_CHECKER, "# sample parity checker\n")
    write_text(root / HELPER_REPLAY, "// sample helper replay\n")
    write_text(root / HELPER_BUILD, "// sample helper build\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1_tests_readme_parity_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        write_text(root / WORKFLOW, "      - name: Check Phase 1 helper parity\n")
        issues = collect_issues(root)
        assert any(issue.startswith("workflow:") for issue in issues)
        case_count += 1

        build_sample_root(root)
        write_text(root / SCRIPTS_README, "\n".join(SCRIPTS_README_MARKERS[:-1]) + "\n")
        issues = collect_issues(root)
        assert any(issue.startswith("scripts_readme:") for issue in issues)
        case_count += 1

        build_sample_root(root)
        (root / HELPER_BUILD).unlink()
        issues = collect_issues(root)
        assert f"missing:{HELPER_BUILD.as_posix()}" in issues
        case_count += 1

    print("PHASE1_TESTS_README_PARITY_PACKET_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_PARITY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="repository root to validate")
    parser.add_argument("--write-sample-root", help="write a focused current-like sample root")
    parser.add_argument("--self-test", action="store_true", help="run focused checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    return run_check(repo_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
