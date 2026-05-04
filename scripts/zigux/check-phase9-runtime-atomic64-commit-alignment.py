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

PINNED_SURVEY_TEMPLATE = "the current survey packet is pinned to `master` commit `{commit}`"
PINNED_MODULE_TEMPLATE = "the current module-slice packet is pinned to `master` commit `{commit}`"

PIN_CARRIER_PATHS = {
    "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    "zigux/tests/runtime_atomic64_manifest.json",
}
REQUIRED_PACKET_PATHS = {
    "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "zigux/tests/runtime_atomic64_manifest.json",
    "zigux/tests/runtime_atomic64_survey.zig",
    "zigux/tests/phase9_build.zig",
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


def validate_required_packet_paths(packet_paths: list[str]) -> list[str]:
    seen_paths = set(packet_paths)
    missing_paths = sorted(REQUIRED_PACKET_PATHS - seen_paths)
    return [f"runtime_atomic64_packet:missing_required_path:{path}" for path in missing_paths]


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_text = read_text(root, "zigux/tests/runtime_atomic64_manifest.json")
    survey_text = read_text(root, "Documentation/zigux/phase9-runtime-atomic64-survey.md")
    module_text = read_text(root, "Documentation/zigux/phase9-runtime-atomic64-module-slice.md")

    manifest_commit, packet_paths, manifest_error = extract_manifest_surveyed_commit_and_paths(manifest_text)
    if manifest_error:
        return [manifest_error]

    assert manifest_commit is not None
    assert packet_paths is not None

    errors.extend(validate_required_packet_paths(packet_paths))

    survey_commit, survey_error = extract_markdown_surveyed_commit(
        survey_text,
        "atomic64_survey",
    )
    if survey_error:
        errors.append(survey_error)
    elif survey_commit != manifest_commit:
        errors.append("atomic64_survey:surveyed_commit_mismatch")

    module_commit, module_error = extract_markdown_surveyed_commit(
        module_text,
        "atomic64_module_slice",
    )
    if module_error:
        errors.append(module_error)
    elif module_commit != manifest_commit:
        errors.append("atomic64_module_slice:surveyed_commit_mismatch")

    if PINNED_SURVEY_TEMPLATE.format(commit=manifest_commit) not in survey_text:
        errors.append("atomic64_survey:missing_pinned_commit_sentence")
    if PINNED_MODULE_TEMPLATE.format(commit=manifest_commit) not in module_text:
        errors.append("atomic64_module_slice:missing_pinned_commit_sentence")

    changed_paths, git_error = git_changed_packet_paths(root, manifest_commit, packet_paths)
    if git_error is not None:
        errors.append(git_error)
    elif changed_paths:
        errors.append("runtime_atomic64_packet:surveyed_commit_stale")
        errors.extend(
            f"runtime_atomic64_packet:changed_since_surveyed_commit:{path}" for path in changed_paths
        )

    return errors


def run_self_test() -> int:
    baseline_manifest = """{
  \"surveyed_commit\": \"1383062a0df7f7a360df54db685454b3e69798af\",
  \"delivery_evidence_catalog\": [
    {
      \"id\": \"runtime-atomic64-survey-note\",
      \"kind\": \"documentation\",
      \"path\": \"Documentation/zigux/phase9-runtime-atomic64-survey.md\",
      \"role\": \"records the bounded survey note\"
    },
    {
      \"id\": \"runtime-atomic64-module-slice\",
      \"kind\": \"documentation\",
      \"path\": \"Documentation/zigux/phase9-runtime-atomic64-module-slice.md\",
      \"role\": \"records the bounded module-slice note\"
    },
    {
      \"id\": \"runtime-atomic64-freeze-map\",
      \"kind\": \"governance\",
      \"path\": \"Documentation/zigux/freeze-map.md\",
      \"role\": \"records the study-only workqueue boundary\"
    },
    {
      \"id\": \"runtime-loader-gap-note\",
      \"kind\": \"documentation\",
      \"path\": \"Documentation/zigux/phase9-runtime-loader-gap-survey.md\",
      \"role\": \"records the shared loader blocker note\"
    },
    {
      \"id\": \"runtime-atomic64-manifest\",
      \"kind\": \"manifest\",
      \"path\": \"zigux/tests/runtime_atomic64_manifest.json\",
      \"role\": \"records the manifest-backed catalog\"
    },
    {
      \"id\": \"runtime-atomic64-survey-gate\",
      \"kind\": \"validation\",
      \"path\": \"zigux/tests/runtime_atomic64_survey.zig\",
      \"role\": \"records the dedicated survey gate\"
    },
    {
      \"id\": \"phase9-atomic64-build-gate\",
      \"kind\": \"validation\",
      \"path\": \"zigux/tests/phase9_build.zig\",
      \"role\": \"records the shared build entrypoint\"
    }
  ]
}
"""
    baseline_survey = """# Atomic64 Survey

- `PHASE9_SURVEYED_COMMIT=1383062a0df7f7a360df54db685454b3e69798af`

the current survey packet is pinned to `master` commit `1383062a0df7f7a360df54db685454b3e69798af`.
"""
    baseline_module = """# Atomic64 Module Slice

- `PHASE9_SURVEYED_COMMIT=1383062a0df7f7a360df54db685454b3e69798af`

the current module-slice packet is pinned to `master` commit `1383062a0df7f7a360df54db685454b3e69798af`.
"""

    with tempfile.TemporaryDirectory(prefix="phase9_atomic64_commit_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)

        manifest_path = root / "zigux/tests/runtime_atomic64_manifest.json"
        survey_path = root / "Documentation/zigux/phase9-runtime-atomic64-survey.md"
        module_path = root / "Documentation/zigux/phase9-runtime-atomic64-module-slice.md"
        freeze_map_path = root / "Documentation/zigux/freeze-map.md"
        loader_gap_path = root / "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
        survey_gate_path = root / "zigux/tests/runtime_atomic64_survey.zig"
        build_gate_path = root / "zigux/tests/phase9_build.zig"

        manifest_path.write_text(baseline_manifest, encoding="utf-8")
        survey_path.write_text(baseline_survey, encoding="utf-8")
        module_path.write_text(baseline_module, encoding="utf-8")
        freeze_map_path.write_text("# freeze map baseline\n", encoding="utf-8")
        loader_gap_path.write_text("# loader gap baseline\n", encoding="utf-8")
        survey_gate_path.write_text("// survey gate baseline\n", encoding="utf-8")
        build_gate_path.write_text("// phase9 build baseline\n", encoding="utf-8")

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
        module_path.write_text(
            baseline_module.replace(
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
                "phase9-atomic64-commit-alignment:self-test:baseline_failed:"
                + ",".join(baseline_errors)
            )

        missing_path_manifest = json.loads(
            baseline_manifest.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            )
        )
        missing_path_manifest["delivery_evidence_catalog"] = [
            entry
            for entry in missing_path_manifest["delivery_evidence_catalog"]
            if entry.get("path") != "Documentation/zigux/freeze-map.md"
        ]
        manifest_path.write_text(
            json.dumps(missing_path_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        missing_path_errors = validate(root)
        if "runtime_atomic64_packet:missing_required_path:Documentation/zigux/freeze-map.md" not in missing_path_errors:
            raise SystemExit(
                "phase9-atomic64-commit-alignment:self-test:expected_required_path_failure:"
                + ",".join(missing_path_errors or ["none"])
            )
        manifest_path.write_text(
            baseline_manifest.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        module_path.write_text(
            baseline_module.replace(
                "the current module-slice packet is pinned to `master` commit `"
                f"{baseline_commit}`.",
                "",
                1,
            ),
            encoding="utf-8",
        )
        module_errors = validate(root)
        if "atomic64_module_slice:missing_pinned_commit_sentence" not in module_errors:
            raise SystemExit(
                "phase9-atomic64-commit-alignment:self-test:expected_module_pinned_sentence_failure:"
                + ",".join(module_errors or ["none"])
            )
        module_path.write_text(
            baseline_module.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        survey_path.write_text(
            baseline_survey.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                "0000000000000000000000000000000000000000",
                1,
            ),
            encoding="utf-8",
        )
        survey_errors = validate(root)
        if "atomic64_survey:surveyed_commit_mismatch" not in survey_errors:
            raise SystemExit(
                "phase9-atomic64-commit-alignment:self-test:expected_survey_commit_mismatch:"
                + ",".join(survey_errors or ["none"])
            )
        survey_path.write_text(
            baseline_survey.replace(
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
                "phase9-atomic64-commit-alignment:self-test:expected_manifest_commit_failure:"
                + ",".join(manifest_errors or ["none"])
            )
        manifest_path.write_text(
            baseline_manifest.replace(
                "1383062a0df7f7a360df54db685454b3e69798af",
                baseline_commit,
            ),
            encoding="utf-8",
        )

        build_gate_path.write_text("// phase9 build changed after pin\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "change build gate after pin"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        stale_errors = validate(root)
        if "runtime_atomic64_packet:surveyed_commit_stale" not in stale_errors:
            raise SystemExit(
                "phase9-atomic64-commit-alignment:self-test:expected_stale_packet_failure:"
                + ",".join(stale_errors or ["none"])
            )
        if "runtime_atomic64_packet:changed_since_surveyed_commit:zigux/tests/phase9_build.zig" not in stale_errors:
            raise SystemExit(
                "phase9-atomic64-commit-alignment:self-test:expected_changed_path_marker:"
                + ",".join(stale_errors)
            )

    print("PHASE9_ATOMIC64_COMMIT_ALIGNMENT_SELF_TEST=pass")
    print("PHASE9_ATOMIC64_COMMIT_ALIGNMENT_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate surveyed-commit alignment for the Phase 9 runtime atomic64 evidence packet."
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
        print("PHASE9_ATOMIC64_COMMIT_ALIGNMENT=fail")
        print("PHASE9_ATOMIC64_COMMIT_ALIGNMENT_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE9_ATOMIC64_COMMIT_ALIGNMENT_ERRORS_END")
        return 1

    print("PHASE9_ATOMIC64_COMMIT_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
