#!/usr/bin/env python3
"""Guard the current Phase 6 surveyed-head truthfulness gap note."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NOTE_PATH = Path("Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md")
EVIDENCE_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

EXPECTED_OLD_HEAD = "current-master-readback-2026-05-22"
EXPECTED_NEW_PERF_DATE = "2026-05-27"

REQUIRED_NOTE_SNIPPETS = (
    "`Documentation/zigux/phase6-helper-evidence-catalog.md` still advertises `surveyed head: current-master-readback-2026-05-22`",
    "`Documentation/zigux/phase6-helper-parity-catalog.md` still advertises `surveyed head: current-master-readback-2026-05-22`",
    "`zigux/tests/phase6_helper_evidence_manifest.json` still pins `surveyed_head` to `current-master-readback-2026-05-22`",
    "`zigux/tests/phase6_helper_parity_manifest.json` still pins `surveyed_head` to `current-master-readback-2026-05-22`",
    "`Documentation/zigux/phase6-perf-gate-survey.md` now says the shared perf packet was re-read from current `master` on `2026-05-27`",
    "Do not retag only one or two of those files. The honest fix is a one-pass refresh of the whole shared packet.",
)

REQUIRED_EVIDENCE_CATALOG_SNIPPET = "- surveyed head: `current-master-readback-2026-05-22`"
REQUIRED_PARITY_CATALOG_SNIPPET = "- surveyed head: `current-master-readback-2026-05-22`"
REQUIRED_PERF_SURVEY_SNIPPET = "the exact posture below was re-read from current `master` on `2026-05-27`"

SELF_TEST_CASE_COUNT = 7


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        parsed = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return parsed


def require_snippets(path: Path, snippets: tuple[str, ...]) -> None:
    text = read_text(path)
    for snippet in snippets:
        if snippet not in text:
            raise ValidationError(f"missing expected marker in {path.as_posix()}: {snippet}")


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / NOTE_PATH, REQUIRED_NOTE_SNIPPETS)
    require_snippets(repo_root / EVIDENCE_CATALOG_PATH, (REQUIRED_EVIDENCE_CATALOG_SNIPPET,))
    require_snippets(repo_root / PARITY_CATALOG_PATH, (REQUIRED_PARITY_CATALOG_SNIPPET,))
    require_snippets(repo_root / PERF_SURVEY_PATH, (REQUIRED_PERF_SURVEY_SNIPPET,))

    evidence_manifest = read_json(repo_root / EVIDENCE_MANIFEST_PATH)
    parity_manifest = read_json(repo_root / PARITY_MANIFEST_PATH)

    if evidence_manifest.get("surveyed_head") != EXPECTED_OLD_HEAD:
        raise ValidationError("phase6 helper evidence surveyed_head drifted")
    if parity_manifest.get("surveyed_head") != EXPECTED_OLD_HEAD:
        raise ValidationError("phase6 helper parity surveyed_head drifted")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / NOTE_PATH, "\n".join(REQUIRED_NOTE_SNIPPETS) + "\n")
    write(root / EVIDENCE_CATALOG_PATH, REQUIRED_EVIDENCE_CATALOG_SNIPPET + "\n")
    write(root / PARITY_CATALOG_PATH, REQUIRED_PARITY_CATALOG_SNIPPET + "\n")
    write(root / PERF_SURVEY_PATH, REQUIRED_PERF_SURVEY_SNIPPET + "\n")
    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps({"surveyed_head": EXPECTED_OLD_HEAD}, indent=2) + "\n",
    )
    write(
        root / PARITY_MANIFEST_PATH,
        json.dumps({"surveyed_head": EXPECTED_OLD_HEAD}, indent=2) + "\n",
    )


def expect_failure(root: Path, path: Path, mutate) -> None:
    original = read_text(path)
    mutate(path)
    try:
        validate(root)
    except ValidationError:
        pass
    else:
        raise AssertionError("expected validation failure")
    finally:
        write(path, original)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_truthfulness_") as tmp_dir:
        root = Path(tmp_dir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        expect_failure(
            root,
            root / NOTE_PATH,
            lambda path: write(path, read_text(path).replace(REQUIRED_NOTE_SNIPPETS[0], "", 1)),
        )
        cases_run += 1

        expect_failure(
            root,
            root / EVIDENCE_CATALOG_PATH,
            lambda path: write(path, ""),
        )
        cases_run += 1

        expect_failure(
            root,
            root / PARITY_CATALOG_PATH,
            lambda path: write(path, ""),
        )
        cases_run += 1

        expect_failure(
            root,
            root / PERF_SURVEY_PATH,
            lambda path: write(path, read_text(path).replace(EXPECTED_NEW_PERF_DATE, "2026-05-26")),
        )
        cases_run += 1

        expect_failure(
            root,
            root / EVIDENCE_MANIFEST_PATH,
            lambda path: write(path, json.dumps({"surveyed_head": "current-master-readback-2026-05-27"}, indent=2) + "\n"),
        )
        cases_run += 1

        expect_failure(
            root,
            root / PARITY_MANIFEST_PATH,
            lambda path: write(path, json.dumps({"surveyed_head": "current-master-readback-2026-05-27"}, indent=2) + "\n"),
        )
        cases_run += 1

        try:
            (root / PERF_SURVEY_PATH).unlink()
            validate(root)
        except ValidationError:
            pass
        else:
            raise AssertionError("expected missing file failure")
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_SURVEYED_HEAD_TRUTHFULNESS_SELF_TEST=pass")
    print(f"PHASE6_SURVEYED_HEAD_TRUTHFULNESS_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    validate(args.repo_root.resolve())
    print("PHASE6_SURVEYED_HEAD_TRUTHFULNESS=pass")
    print(f"PHASE6_SURVEYED_HEAD_TRUTHFULNESS_NOTE={(args.repo_root.resolve() / NOTE_PATH).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
