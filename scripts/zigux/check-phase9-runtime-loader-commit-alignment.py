#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
GAP_SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
SUBSTRATE_PLAN_PATH = "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"

REQUIRED_FILES = [
    MANIFEST_PATH,
    GAP_SURVEY_PATH,
    SUBSTRATE_PLAN_PATH,
]

PINNED_SENTENCE_PREFIX = "pinned to `master` commit `"
SURVEYED_COMMIT_RE = re.compile(r'"surveyed_commit"\s*:\s*"([0-9a-f]{40})"')
DOC_COMMIT_RE = re.compile(r"`PHASE9_SURVEYED_COMMIT=([0-9a-f]{40})`")


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def extract_manifest_commit(text: str) -> str | None:
    match = SURVEYED_COMMIT_RE.search(text)
    return match.group(1) if match else None


def extract_doc_commit(text: str) -> str | None:
    match = DOC_COMMIT_RE.search(text)
    return match.group(1) if match else None


def pinned_sentence(commit: str) -> str:
    return f"{PINNED_SENTENCE_PREFIX}{commit}`"


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    manifest_text = read_text(root, MANIFEST_PATH)
    gap_survey_text = read_text(root, GAP_SURVEY_PATH)
    substrate_plan_text = read_text(root, SUBSTRATE_PLAN_PATH)

    missing_markers: list[str] = []

    manifest_commit = extract_manifest_commit(manifest_text)
    if manifest_commit is None:
        missing_markers.append(f"{MANIFEST_PATH}:missing_or_invalid_surveyed_commit")
        return [], missing_markers

    gap_survey_commit = extract_doc_commit(gap_survey_text)
    if gap_survey_commit is None:
        missing_markers.append(f"{GAP_SURVEY_PATH}:missing_or_invalid_phase9_surveyed_commit")
    elif gap_survey_commit != manifest_commit:
        missing_markers.append(f"{GAP_SURVEY_PATH}:surveyed_commit_mismatch")

    substrate_plan_commit = extract_doc_commit(substrate_plan_text)
    if substrate_plan_commit is None:
        missing_markers.append(f"{SUBSTRATE_PLAN_PATH}:missing_or_invalid_phase9_surveyed_commit")
    elif substrate_plan_commit != manifest_commit:
        missing_markers.append(f"{SUBSTRATE_PLAN_PATH}:surveyed_commit_mismatch")

    expected_pinned_sentence = pinned_sentence(manifest_commit)
    if expected_pinned_sentence not in gap_survey_text:
        missing_markers.append(f"{GAP_SURVEY_PATH}:missing_pinned_commit_sentence")
    if expected_pinned_sentence not in substrate_plan_text:
        missing_markers.append(f"{SUBSTRATE_PLAN_PATH}:missing_pinned_commit_sentence")

    return [], missing_markers


def write_fixture_root(root: Path) -> None:
    commit = "1383062a0df7f7a360df54db685454b3e69798af"
    fixture_files = {
        MANIFEST_PATH: "{\n  \"surveyed_commit\": \"1383062a0df7f7a360df54db685454b3e69798af\"\n}\n",
        GAP_SURVEY_PATH: (
            "# Gap Survey\n\n"
            f"- `PHASE9_SURVEYED_COMMIT={commit}`\n\n"
            f"the current survey packet is pinned to `master` commit `{commit}`.\n"
        ),
        SUBSTRATE_PLAN_PATH: (
            "# Substrate Plan\n\n"
            f"- `PHASE9_SURVEYED_COMMIT={commit}`\n\n"
            f"The current substrate-plan packet is pinned to `master` commit `{commit}`.\n"
        ),
    }

    for rel_path, text in fixture_files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def expect_missing_marker(case: str, root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(root)
    assert missing_files == [], case
    assert expected in missing_markers, case


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_loader_commit_alignment_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        gap_survey_path = tmp_root / GAP_SURVEY_PATH
        original_gap_survey = gap_survey_path.read_text(encoding="utf-8")
        gap_survey_path.write_text(
            original_gap_survey.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                "6be8e2a2a4094a8fab9fc1dc62fd9b93f0b65e97",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "gap_surveyed_commit_mismatch",
            tmp_root,
            f"{GAP_SURVEY_PATH}:surveyed_commit_mismatch",
        )
        gap_survey_path.write_text(original_gap_survey, encoding="utf-8")
        case_count += 1

        substrate_plan_path = tmp_root / SUBSTRATE_PLAN_PATH
        original_substrate_plan = substrate_plan_path.read_text(encoding="utf-8")
        substrate_plan_path.write_text(
            original_substrate_plan.replace(PINNED_SENTENCE_PREFIX, "pinned to `master` revision `", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "substrate_plan_missing_pinned_sentence",
            tmp_root,
            f"{SUBSTRATE_PLAN_PATH}:missing_pinned_commit_sentence",
        )
        substrate_plan_path.write_text(original_substrate_plan, encoding="utf-8")
        case_count += 1

        manifest_path = tmp_root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text("{}\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_missing_commit",
            tmp_root,
            f"{MANIFEST_PATH}:missing_or_invalid_surveyed_commit",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")
        case_count += 1

    print("PHASE9_LOADER_COMMIT_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE9_LOADER_COMMIT_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the shared Phase 9 runtime-loader packet stays pinned to one surveyed commit."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in alignment drift checks without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE9_LOADER_COMMIT_ALIGNMENT=fail")
        print("MISSING_PHASE9_LOADER_COMMIT_ALIGNMENT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE9_LOADER_COMMIT_ALIGNMENT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE9_LOADER_COMMIT_ALIGNMENT=fail")
        print("MISSING_PHASE9_LOADER_COMMIT_ALIGNMENT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE9_LOADER_COMMIT_ALIGNMENT_MARKERS_END")
        return 1

    print("PHASE9_LOADER_COMMIT_ALIGNMENT=pass")
    print(f"PHASE9_LOADER_COMMIT_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
