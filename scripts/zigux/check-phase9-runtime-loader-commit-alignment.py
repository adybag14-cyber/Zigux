#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


SURVEYED_COMMIT_RE = re.compile(r"`PHASE9_SURVEYED_COMMIT=([0-9a-f]{40})`")

PINNED_COMMIT_TEMPLATE = "pinned to `master` commit `{commit}`"
PIN_CARRIER_PATHS = {
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def extract_markdown_surveyed_commit(text: str, label: str) -> tuple[str | None, str | None]:
    match = SURVEYED_COMMIT_RE.search(text)
    if not match:
        return None, f"{label}:missing_or_invalid_surveyed_commit_marker"
    return match.group(1), None


def extract_manifest_surveyed_commit_and_paths(
    text: str,
) -> tuple[str | None, list[str] | None, str | None]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError:
        return None, None, "manifest:json_decode_failed"

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", surveyed_commit):
        return None, None, "manifest:missing_or_invalid_surveyed_commit"

    delivery_catalog = manifest.get("delivery_evidence_catalog")
    if not isinstance(delivery_catalog, list) or not delivery_catalog:
        return None, None, "manifest:missing_delivery_evidence_catalog"

    packet_paths: list[str] = []
    seen_paths: set[str] = set()
    for entry in delivery_catalog:
        if not isinstance(entry, dict):
            return None, None, "manifest:invalid_delivery_evidence_entry"
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            return None, None, "manifest:invalid_delivery_evidence_path"
        if path not in seen_paths:
            packet_paths.append(path)
            seen_paths.add(path)

    return surveyed_commit, packet_paths, None


def git_changed_packet_paths(root: Path, base_commit: str, packet_paths: list[str]) -> tuple[list[str] | None, str | None]:
    try:
        rev_parse = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None, "git:unavailable_or_not_repo"

    if rev_parse.stdout.strip() != "true":
        return None, "git:unavailable_or_not_repo"

    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{base_commit}^{{commit}}"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None, "git:missing_surveyed_commit"

    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base_commit}..HEAD", "--", *packet_paths],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    changed_paths = [
        line.strip()
        for line in diff.stdout.splitlines()
        if line.strip() and line.strip() not in PIN_CARRIER_PATHS
    ]
    return changed_paths, None


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_text = read_text(root, "zigux/tests/runtime_loader_gap_manifest.json")
    survey_text = read_text(root, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")
    substrate_text = read_text(root, "Documentation/zigux/phase9-runtime-loader-substrate-plan.md")

    manifest_commit, packet_paths, manifest_error = extract_manifest_surveyed_commit_and_paths(manifest_text)
    if manifest_error:
        return [manifest_error]

    assert manifest_commit is not None
    assert packet_paths is not None

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

    changed_paths, git_error = git_changed_packet_paths(root, manifest_commit, packet_paths)
    if git_error is not None:
        errors.append(git_error)
    elif changed_paths:
        errors.append("runtime_loader_packet:surveyed_commit_stale")
        errors.extend(
            f"runtime_loader_packet:changed_since_surveyed_commit:{path}" for path in changed_paths
        )

    return errors


def run_self_test() -> int:
    baseline_manifest = """{
  \"surveyed_commit\": \"1383062a0df7f7a360df54db685454b3e69798af\",
  \"delivery_evidence_catalog\": [
    {
      \"id\": \"runtime-loader-gap-note\",
      \"kind\": \"documentation\",
      \"path\": \"Documentation/zigux/phase9-runtime-loader-gap-survey.md\",
      \"role\": \"records the shared runtime loader gap note\"
    },
    {
      \"id\": \"runtime-loader-substrate-plan\",
      \"kind\": \"documentation\",
      \"path\": \"Documentation/zigux/phase9-runtime-loader-substrate-plan.md\",
      \"role\": \"records the shared runtime loader substrate plan\"
    },
    {
      \"id\": \"runtime-loader-gap-manifest\",
      \"kind\": \"manifest\",
      \"path\": \"zigux/tests/runtime_loader_gap_manifest.json\",
      \"role\": \"records the manifest-backed catalog\"
    },
    {
      \"id\": \"runtime-loader-contract\",
      \"kind\": \"runtime_substrate\",
      \"path\": \"zigux/kernel/runtime_loader.zig\",
      \"role\": \"records the shared request contract\"
    }
  ]
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
        (root / "zigux/kernel").mkdir(parents=True, exist_ok=True)

        manifest_path = root / "zigux/tests/runtime_loader_gap_manifest.json"
        survey_path = root / "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
        substrate_path = root / "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"
        runtime_loader_path = root / "zigux/kernel/runtime_loader.zig"

        manifest_path.write_text(baseline_manifest, encoding="utf-8")
        survey_path.write_text(baseline_survey, encoding="utf-8")
        substrate_path.write_text(baseline_substrate, encoding="utf-8")
        runtime_loader_path.write_text("// runtime loader baseline\n", encoding="utf-8")

        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Codex"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "codex@example.com"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "baseline"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        baseline_commit = (
            subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
        )

        manifest_path.write_text(
            baseline_manifest.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )
        survey_path.write_text(
            baseline_survey.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )
        substrate_path.write_text(
            baseline_substrate.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "pin surveyed commit"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )

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
        substrate_path.write_text(
            baseline_substrate.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        survey_path.write_text(
            baseline_survey.replace(
                PINNED_COMMIT_TEMPLATE.format(commit=baseline_commit),
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
        survey_path.write_text(
            baseline_survey.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        substrate_path.write_text(
            baseline_substrate.replace(
                PINNED_COMMIT_TEMPLATE.format(commit=baseline_commit),
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
        substrate_path.write_text(
            baseline_substrate.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        manifest_path.write_text(
            """{
  \"surveyed_commit\": \"invalid\",
  \"delivery_evidence_catalog\": []
}
""",
            encoding="utf-8",
        )
        manifest_errors = validate(root)
        if "manifest:missing_or_invalid_surveyed_commit" not in manifest_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_manifest_commit_failure:"
                + ",".join(manifest_errors or ["none"])
            )
        manifest_path.write_text(
            baseline_manifest.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        runtime_loader_path.write_text("// runtime loader changed after pin\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "change runtime loader after pin"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        stale_errors = validate(root)
        if "runtime_loader_packet:surveyed_commit_stale" not in stale_errors:
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_stale_packet_failure:"
                + ",".join(stale_errors or ["none"])
            )
        if (
            "runtime_loader_packet:changed_since_surveyed_commit:zigux/kernel/runtime_loader.zig"
            not in stale_errors
        ):
            raise SystemExit(
                "phase9-loader-commit-alignment:self-test:expected_changed_path_marker:"
                + ",".join(stale_errors)
            )

    print("PHASE9_LOADER_COMMIT_ALIGNMENT_SELF_TEST=pass")
    print("PHASE9_LOADER_COMMIT_ALIGNMENT_SELF_TEST_CASE_COUNT=5")
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
