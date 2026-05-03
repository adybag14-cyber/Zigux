#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


SURVEYED_COMMIT_RE = re.compile(r"`PHASE9_SURVEYED_COMMIT=([0-9a-f]{40})`")

PINNED_COMMIT_TEMPLATE = "pinned to `master` commit `{commit}`"


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def extract_markdown_surveyed_commit(text: str, label: str) -> tuple[str | None, str | None]:
    match = SURVEYED_COMMIT_RE.search(text)
    if not match:
        return None, f"{label}:missing_or_invalid_surveyed_commit_marker"
    return match.group(1), None


def extract_manifest_surveyed_commit(text: str) -> tuple[str | None, str | None]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError:
        return None, "manifest:json_decode_failed"

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", surveyed_commit):
        return None, "manifest:missing_or_invalid_surveyed_commit"
    return surveyed_commit, None


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_text = read_text(root, "zigux/tests/runtime_loader_gap_manifest.json")
    survey_text = read_text(root, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")
    substrate_text = read_text(root, "Documentation/zigux/phase9-runtime-loader-substrate-plan.md")

    manifest_commit, manifest_error = extract_manifest_surveyed_commit(manifest_text)
    if manifest_error:
        return [manifest_error]

    assert manifest_commit is not None

    survey_commit, survey_error = extract_markdown_surveyed_commit(
        survey_text,
        "gap_survey",
    )
    if survey_error:
        errors.append(survey_error)
    elif survey_commit != manifest_commit:
        errors.append("gap_survey:surveyed_commit_mismatch")

    substrate_commit, substrate_error = extract_markdown_surveyed_commit(
        substrate_text,
        "substrate_plan",
    )
    if substrate_error:
        errors.append(substrate_error)
    elif substrate_commit != manifest_commit:
        errors.append("substrate_plan:surveyed_commit_mismatch")

    pinned_commit_sentence = PINNED_COMMIT_TEMPLATE.format(commit=manifest_commit)
    if pinned_commit_sentence not in survey_text:
        errors.append("gap_survey:missing_pinned_commit_sentence")
    if pinned_commit_sentence not in substrate_text:
        errors.append("substrate_plan:missing_pinned_commit_sentence")

    return errors


def run_self_test() -> int:
    baseline_manifest = """{
  \"surveyed_commit\": \"1383062a0df7f7a360df54db685454b3e69798af\"
}
"""
    baseline_survey = """# Gap Survey

- `PHASE9_SURVEYED_COMMIT=1383062a0df7f7a360df54db685454b3e69798af`

the current survey packet is pinned to `master` commit `1383062a0df7f7a360df54db685454b3e69798af`.
"""
    baseline_substrate = """# Substrate Plan

- `PHASE9_SURVEYED_COMMIT=1383062a0df7f7a360df54db685454b3e69798af`

The current substrate-plan packet is pinned to `master` commit `1383062a0df7f7a360df54db685454b3e69798af`.
"""

    with tempfile.TemporaryDirectory(prefix="phase9_loader_commit_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)

        manifest_path = root / "zigux/tests/runtime_loader_gap_manifest.json"
        survey_path = root / "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
        substrate_path = root / "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"

        manifest_path.write_text(baseline_manifest, encoding="utf-8")
        survey_path.write_text(baseline_survey, encoding="utf-8")
        substrate_path.write_text(baseline_substrate, encoding="utf-8")

        baseline_errors = validate(root)
        if baseline_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:baseline_failed:"
                + ",".join(baseline_errors)
            )

        substrate_path.write_text(
            baseline_substrate.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                "0000000000000000000000000000000000000000",
                1,
            ),
            encoding="utf-8",
        )
        substrate_errors = validate(root)
        if "substrate_plan:surveyed_commit_mismatch" not in substrate_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_substrate_commit_mismatch:"
                + ",".join(substrate_errors or ["none"])
            )
        substrate_path.write_text(baseline_substrate, encoding="utf-8")

        survey_path.write_text(
            baseline_survey.replace(
                PINNED_COMMIT_TEMPLATE.format(
                    commit="1383062a0df7f7a360df54db685454b3e69798af"
                ),
                "",
                1,
            ),
            encoding="utf-8",
        )
        survey_errors = validate(root)
        if "gap_survey:missing_pinned_commit_sentence" not in survey_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_gap_pinned_sentence_failure:"
                + ",".join(survey_errors or ["none"])
            )
        survey_path.write_text(baseline_survey, encoding="utf-8")

        substrate_path.write_text(
            baseline_substrate.replace(
                PINNED_COMMIT_TEMPLATE.format(
                    commit="1383062a0df7f7a360df54db685454b3e69798af"
                ),
                "",
                1,
            ),
            encoding="utf-8",
        )
        substrate_errors = validate(root)
        if "substrate_plan:missing_pinned_commit_sentence" not in substrate_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_substrate_pinned_sentence_failure:"
                + ",".join(substrate_errors or ["none"])
            )
        substrate_path.write_text(baseline_substrate, encoding="utf-8")

        manifest_path.write_text("{\n  \"surveyed_commit\": \"invalid\"\n}\n", encoding="utf-8")
        manifest_errors = validate(root)
        if "manifest:missing_or_invalid_surveyed_commit" not in manifest_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_manifest_commit_failure:"
                + ",".join(manifest_errors or ["none"])
            )

    print("PHASE9_LOADER_COMMIT_ALIGNMENT_SELF_TEST=pass")
    print("PHASE9_LOADER_COMMIT_ALIGNMENT_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate surveyed-commit alignment for the shared Phase 9 runtime-loader evidence packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root of the Zigux checkout to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in validator self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        print("PHASE9_LOADER_COMMIT_ALIGNMENT=fail")
        print("PHASE9_LOADER_COMMIT_ALIGNMENT_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE9_LOADER_COMMIT_ALIGNMENT_ERRORS_END")
        return 1

    print("PHASE9_LOADER_COMMIT_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
