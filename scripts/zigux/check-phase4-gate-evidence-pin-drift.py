#!/usr/bin/env python3
"""Fail closed when the broader Phase 4 gate-evidence note pins stale blob SHAs."""

from __future__ import annotations

import argparse
import hashlib
import re
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-gate-evidence.md")
PINNED_FILES = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": Path("Documentation/zigux/phase4-validation-matrix.md"),
    "PHASE4_VALIDATOR_BLOB_SHA": Path("scripts/zigux/validate-phase4.py"),
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA": Path("scripts/zigux/check-phase4-workflow-route-counts.py"),
    "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA": Path("Documentation/zigux/artifact-diff.md"),
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA": Path("scripts/zigux/check-artifact-diff-contract.py"),
    "PHASE4_BUILD_BLOB_SHA": Path("zigux/tests/phase4_build.zig"),
    "PHASE4_MAKEFILE_BLOB_SHA": Path("zigux/Makefile"),
    "PHASE4_WORKFLOW_BLOB_SHA": Path(".github/workflows/zigux-bootstrap.yml"),
    "PHASE4_DOC_README_BLOB_SHA": Path("Documentation/zigux/README.md"),
    "PHASE4_SCRIPT_README_BLOB_SHA": Path("scripts/zigux/README.md"),
    "PHASE4_TESTS_README_BLOB_SHA": Path("zigux/tests/README.md"),
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA": Path("zigux/tests/atomic64_diff.zig"),
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA": Path("zigux/tests/runtime_atomic64_diff.zig"),
    "PHASE4_BITMAP_DIFF_BLOB_SHA": Path("zigux/tests/bitmap_diff.zig"),
    "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA": Path("zigux/tests/phase4_bitmap_live_helper_replay.zig"),
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json"),
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": Path("zigux/tests/phase4_runtime_atomic64_diff_survey.zig"),
    "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA": Path("Documentation/zigux/review-checklist.md"),
}
SHA_MARKER_RE = re.compile(r"`(?P<name>[A-Z0-9_]+)=(?P<sha>[0-9a-f]{40})`")
EXPECTED_SELF_TEST_CASES = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def read_pins(note_text: str) -> dict[str, str]:
    return {match.group("name"): match.group("sha") for match in SHA_MARKER_RE.finditer(note_text)}


def collect_issues(root: Path, note_path: Path = NOTE, pinned_files: dict[str, Path] = PINNED_FILES) -> list[str]:
    note_file = root / note_path
    if not note_file.is_file():
        return [f"missing_note:{note_path.as_posix()}"]

    issues: list[str] = []
    observed = read_pins(note_file.read_text(encoding="utf-8"))
    for marker, rel_path in pinned_files.items():
        expected = observed.get(marker)
        if expected is None:
            issues.append(f"missing_marker:{marker}")
            continue

        target = root / rel_path
        if not target.is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")
            continue

        actual = git_blob_sha(target.read_bytes())
        if actual != expected:
            issues.append(
                f"sha_drift:{marker}:expected={expected}:actual={actual}:path={rel_path.as_posix()}"
            )

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture(root: Path) -> dict[str, Path]:
    fixture_files = {
        "PHASE4_VALIDATOR_BLOB_SHA": Path("scripts/zigux/validate-phase4.py"),
        "PHASE4_WORKFLOW_BLOB_SHA": Path(".github/workflows/zigux-bootstrap.yml"),
    }
    file_contents = {
        fixture_files["PHASE4_VALIDATOR_BLOB_SHA"]: "print('phase4 validator')\n",
        fixture_files["PHASE4_WORKFLOW_BLOB_SHA"]: "name: phase4-pin-drift-test\n",
    }
    for rel_path, content in file_contents.items():
        write_text(root / rel_path, content)

    note_lines = ["# fixture", ""]
    for marker, rel_path in fixture_files.items():
        blob_sha = git_blob_sha((root / rel_path).read_bytes())
        note_lines.append(f"`{marker}={blob_sha}`")
    write_text(root / NOTE, "\n".join(note_lines) + "\n")
    return fixture_files


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-pin-drift-") as tmp:
        root = Path(tmp)
        fixture_files = build_fixture(root)
        if collect_issues(root, pinned_files=fixture_files):
            raise AssertionError("baseline fixture failed")
        cases += 1

        note_path = root / NOTE
        note_path.write_text(note_path.read_text(encoding="utf-8").replace(
            "PHASE4_VALIDATOR_BLOB_SHA", "PHASE4_VALIDATOR_BLOB"
        ), encoding="utf-8")
        issues = collect_issues(root, pinned_files=fixture_files)
        if "missing_marker:PHASE4_VALIDATOR_BLOB_SHA" not in issues:
            raise AssertionError("missing marker mutation did not fail closed")
        cases += 1

        fixture_files = build_fixture(root)
        write_text(root / fixture_files["PHASE4_VALIDATOR_BLOB_SHA"], "print('drift')\n")
        issues = collect_issues(root, pinned_files=fixture_files)
        if not any(issue.startswith("sha_drift:PHASE4_VALIDATOR_BLOB_SHA:") for issue in issues):
            raise AssertionError("sha drift mutation did not fail closed")
        cases += 1

        fixture_files = build_fixture(root)
        (root / fixture_files["PHASE4_WORKFLOW_BLOB_SHA"]).unlink()
        issues = collect_issues(root, pinned_files=fixture_files)
        if "missing_file:.github/workflows/zigux-bootstrap.yml" not in issues:
            raise AssertionError("missing file mutation did not fail closed")
        cases += 1

        missing_note_root = root / "missing-note"
        missing_note_root.mkdir(parents=True, exist_ok=True)
        issues = collect_issues(missing_note_root, pinned_files=fixture_files)
        if issues != ["missing_note:Documentation/zigux/phase4-gate-evidence.md"]:
            raise AssertionError("missing note mutation did not fail closed")
        cases += 1

    if cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}"
        )

    print("PHASE4_GATE_EVIDENCE_PIN_DRIFT_SELF_TEST=pass")
    print(f"PHASE4_GATE_EVIDENCE_PIN_DRIFT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(root)
    if issues:
        print("PHASE4_GATE_EVIDENCE_PIN_DRIFT=fail")
        print("PHASE4_GATE_EVIDENCE_PIN_DRIFT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE4_GATE_EVIDENCE_PIN_DRIFT_ISSUES_END")
        return 1

    print("PHASE4_GATE_EVIDENCE_PIN_DRIFT=pass")
    print(f"PHASE4_GATE_EVIDENCE_PIN_DRIFT_TARGET_COUNT={len(PINNED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
