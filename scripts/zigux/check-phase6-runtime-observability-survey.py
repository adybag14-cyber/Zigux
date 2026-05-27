#!/usr/bin/env python3
"""Fail closed when the shared Phase 6 survey packet drops runtime-output diagnostics evidence."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
RUNTIME_OUTPUT_CHECKER = "scripts/zigux/check-phase6-runtime-output-markers.py"

REQUIRED_SURVEY_SNIPPETS = [
    "the four dedicated perf-marker guards",
    RUNTIME_OUTPUT_CHECKER,
]

SELF_TEST_CASE_COUNT = 2


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
            raise ValidationError(f"missing Phase 6 runtime observability marker in {path.as_posix()}: {snippet}")


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 6 Perf Gate Survey",
                "",
                f"- evidence note: the four dedicated perf-marker guards now include `{RUNTIME_OUTPUT_CHECKER}` beside the existing shared validator packet.",
            ]
        )
        + "\n",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase6_runtime_observability_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        def expect_failure(mutator) -> None:
            nonlocal cases_run
            scaffold_repo(root)
            mutator()
            try:
                validate(root)
            except ValidationError:
                cases_run += 1
                return
            raise AssertionError("expected validation failure")

        expect_failure(lambda: write(root / SURVEY_PATH, read_text(root / SURVEY_PATH).replace("four dedicated perf-marker guards", "three dedicated perf-marker guards", 1)))
        expect_failure(lambda: write(root / SURVEY_PATH, read_text(root / SURVEY_PATH).replace(RUNTIME_OUTPUT_CHECKER, "scripts/zigux/check-phase6-runtime-marker-summary.py", 1)))

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_RUNTIME_OBSERVABILITY_SURVEY_SELF_TEST=pass")
    print(f"PHASE6_RUNTIME_OBSERVABILITY_SURVEY_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE6_RUNTIME_OBSERVABILITY_SURVEY=fail: {exc}")
        return 1
    print("PHASE6_RUNTIME_OBSERVABILITY_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
