#!/usr/bin/env python3
"""Guard the current Lane 16 bench packet across closure, scripts, workflow, and checker surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ),
    SCRIPTS_README_REL: (
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def run_self_test() -> None:",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    ),
}

FORBIDDEN_FRAGMENTS = {
    SCRIPTS_README_REL: (
        "treating the bench checker itself as a missing tests-root route",
    ),
    WORKFLOW_REL: (
        "run: zig build bench --build-file zigux/tests/build.zig",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == WORKFLOW_REL:
            lines = text.splitlines()
            for marker in markers:
                count = sum(1 for line in lines if line.strip() == marker)
                if count != 1:
                    issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")
        else:
            for marker in markers:
                count = text.count(marker)
                if count != 1:
                    issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(fragment)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "\n".join(MARKERS[relative_path]) + "\n")


def mutate_remove(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1

    cases: list[tuple[str, str | None, str | None, str | None]] = []
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", relative_path, None, "unlink"))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}", relative_path, marker, "remove"))
            cases.append((f"duplicate:{relative_path}", relative_path, marker, "duplicate"))
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append((f"forbidden:{relative_path}", relative_path, fragment, "append"))

    for _, relative_path, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            assert relative_path is not None
            target = root / relative_path
            if operation == "unlink":
                target.unlink()
            elif operation == "remove":
                assert needle is not None
                mutate_remove(root, relative_path, needle)
            elif operation == "duplicate":
                assert needle is not None
                mutate_duplicate(root, relative_path, needle)
            elif operation == "append":
                assert needle is not None
                target.write_text(target.read_text(encoding="utf-8") + needle + "\n", encoding="utf-8")
            issues = collect_issues(root)
            if not issues:
                print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
                print(f"expected failure for {operation}:{relative_path}")
                return 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_CURRENT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_CURRENT_PACKET=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_CURRENT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
