#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

GUIDE = Path("Documentation/zigux/phase13-contributor-workflow-guide.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")

REQUIRED_MARKERS = {
    GUIDE: (
        "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "2. `scripts/zigux/README.md`",
        "3. `zigux/tests/README.md`",
        "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
        "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
        "Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`.",
    ),
    SCRIPTS_README: (
        "- Phase 13 flow - the current scripts-root shared-helper packet stays reviewable through the stable contributor-facing handle",
        "- `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared-summary and tests-root alignment packet explicit from the scripts root.",
        "- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    ),
    TESTS_README: (
        "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "Keep `scripts/zigux/check-phase13-tests-readme-alignment.py` explicit as the shipped tests-root alignment companion for that stable handle rather than as a new replay route or a Makefile-backed entrypoint.",
        "Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
        "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    ),
}

FORBIDDEN_MARKERS = {
    GUIDE: (
        "stable shared-summary guard: `make -C zigux phase13-validate`",
        "tests-root alignment companion: `make -C zigux phase13`",
    ),
    SCRIPTS_README: (
        "`zigux/Makefile` is present on current `master`, and it now exposes `make -C zigux phase13-validate`",
        "keep `make -C zigux phase13` explicit as a shipped shared build handle",
    ),
    TESTS_README: (
        "Current `master` still does not materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
        "- `zigux/helpers/notifier_chain_view.zig`",
        "- `include/zigux/notifier_abi.h`",
    ),
}


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath.as_posix()}")
    return path.read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relpath, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relpath)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath.as_posix()}:{marker}")
        for marker in FORBIDDEN_MARKERS[relpath]:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath.as_posix()}:{marker}")
    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE=fail")
    print("PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE_ISSUES_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for relpath, markers in REQUIRED_MARKERS.items():
        body = "\n".join(markers) + "\n"
        write_text(root / relpath, body)


def expect_issue(issues: list[str], expected: str) -> None:
    assert expected in issues, f"missing expected issue: {expected}"


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase13-contributor-workflow-handle-") as tmp:
        root = Path(tmp)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        guide = root / GUIDE
        guide.write_text(
            guide.read_text(encoding="utf-8").replace(
                "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        )
        checks_run += 1

        build_self_test_root(root)
        scripts_readme = root / SCRIPTS_README
        scripts_readme.write_text(
            scripts_readme.read_text(encoding="utf-8").replace(
                "- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:scripts/zigux/README.md:- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
        )
        checks_run += 1

        build_self_test_root(root)
        tests_readme = root / TESTS_README
        tests_readme.write_text(
            tests_readme.read_text(encoding="utf-8").replace(
                "Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:zigux/tests/README.md:Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
        )
        checks_run += 1

        build_self_test_root(root)
        tests_readme = root / TESTS_README
        tests_readme.write_text(
            tests_readme.read_text(encoding="utf-8")
            + "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`\n",
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "forbidden_marker:zigux/tests/README.md:Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
        )
        checks_run += 1

        build_self_test_root(root)
        guide = root / GUIDE
        guide.write_text(
            guide.read_text(encoding="utf-8")
            + "stable shared-summary guard: `make -C zigux phase13-validate`\n",
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "forbidden_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:stable shared-summary guard: `make -C zigux phase13-validate`",
        )
        checks_run += 1

        build_self_test_root(root)
        (root / TESTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing tests readme did not abort")

    print("PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE_SELF_TEST=pass")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 13 contributor-workflow handle aligned across shared reminder surfaces."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE=pass")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE_FILE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
