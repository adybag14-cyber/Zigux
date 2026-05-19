#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "Documentation" / "zigux" / "artifact-diff.md"
PHASE4_NOTE = ROOT / "Documentation" / "zigux" / "phase4-reversible-delivery-evidence.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

PRESENT_REPO_PATHS = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
)

GAP_REPO_PATHS = (
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/validate-phase4.py",
)

NOTE_MARKERS = (
    "# Artifact Diff Policy",
    "## Rules",
    "## Current Direct-Readback Helper",
    "`scripts/zigux/artifact_diff.py` is directly readable on current `master`",
    "`python3 scripts/zigux/artifact_diff.py --self-test` is the shipped direct replay for the helper contract today",
    "## Current Reminder Surface",
    "keep this note aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
    "authenticated contents reads on current `master` still return missing for `scripts/zigux/check-artifact-diff-contract.py` and `scripts/zigux/validate-phase4.py`",
    "`scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable again on current `master`",
    "## Current Uses",
    "current Phase 2 reminder surfaces already rely on the helper contract indirectly for bounded fixture-backed parity lanes instead of reopening the older broader closure stack from missing paths",
    "## Next Honest Follow-Through",
    "rematerialize `scripts/zigux/check-artifact-diff-contract.py` before treating the docs-side artifact-diff packet as a fully returned validator-first surface",
)

FILE_MARKERS = {
    PHASE4_NOTE: (
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here.",
    ),
    REVIEW_CHECKLIST: (
        "keep the host-side artifact-diff contract plus `scripts/zigux/check-phase4-remaining-gap-matrix.py` remaining-gap wording truthful",
    ),
    SCRIPTS_README: (
        "historical broader packet references still include `scripts/zigux/artifact_diff.py` and `scripts/zigux/check-artifact-diff-contract.py`, so keep the host-side artifact-diff contract explicit here while the broader validator-first packet stays in repo-reality-gap wording",
    ),
    TESTS_README: (
        "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    ),
}

NOTE_TEMPLATE = """# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity or reminder claim.

## Rules

- prefer text, JSON, or stable hashes over opaque binary blobs whenever the same review goal is possible
- keep artifact scope small enough that one lane can regenerate, compare, and review it honestly
- update an artifact in the same bounded change that changed the source behavior it documents
- keep helper contracts explicit in docs when the executable checker packet is still only partially rematerialized on current `master`

## Current Direct-Readback Helper

- `scripts/zigux/artifact_diff.py` is directly readable on current `master`
- `python3 scripts/zigux/artifact_diff.py --self-test` is the shipped direct replay for the helper contract today
- the helper exposes bounded `text`, `json`, and `sha256` comparison modes plus the outward markers `ARTIFACT_DIFF=...`, `MODE=...`, `EXPECTED=...`, `ACTUAL=...`, `EXPECTED_EXISTS=...`, `ACTUAL_EXISTS=...`, `EXPECTED_JSON_ERROR=...`, `ACTUAL_JSON_ERROR=...`, `SHA256=...`, `EXPECTED_SHA256=...`, and `ACTUAL_SHA256=...`

## Current Reminder Surface

- keep this note aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- that current direct-readback packet keeps the helper itself explicit while the broader validator-first and contract-checker packet is still only partially present on current `master`
- authenticated contents reads on current `master` still return missing for `scripts/zigux/check-artifact-diff-contract.py` and `scripts/zigux/validate-phase4.py`, so treat those as historical or adjacent packet members until a same-family lane rematerializes them directly
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable again on current `master`, so follow-up work here should stay bounded to note and reminder truthfulness unless the missing checker or validator packet returns too

## Current Uses

- the helper remains the shared comparison layer for bounded artifact-backed parity work under `scripts/zigux/`
- current Phase 2 reminder surfaces already rely on the helper contract indirectly for bounded fixture-backed parity lanes instead of reopening the older broader closure stack from missing paths
- current Phase 4 reminder surfaces keep the host-side helper explicit as a reviewable contract anchor while the broader rollback-readiness packet continues to distinguish direct current-head proof from historical packet members

## Next Honest Follow-Through

- narrow shared reminder surfaces only when direct current-head rereads prove they still overstate the broader artifact-diff packet
- rematerialize `scripts/zigux/check-artifact-diff-contract.py` before treating the docs-side artifact-diff packet as a fully returned validator-first surface
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(resolve(root, NOTE))
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKERS", marker))

    for path, markers in FILE_MARKERS.items():
        text = read_text(resolve(root, path))
        for marker in markers:
            if marker not in text:
                issues.append(("MISSING_ALIGNMENT_MARKERS", f"{path.relative_to(ROOT)}::{marker}"))

    for rel in PRESENT_REPO_PATHS:
        if not resolve(root, Path(rel)).exists():
            issues.append(("MISSING_PRESENT_REPO_PATHS", rel))

    for rel in GAP_REPO_PATHS:
        if resolve(root, Path(rel)).exists():
            issues.append(("UNEXPECTED_PRESENT_GAP_PATHS", rel))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_DIFF_NOTE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, NOTE), NOTE_TEMPLATE)
    for path, markers in FILE_MARKERS.items():
        write_text(resolve(root, path), "\n".join(markers) + "\n")
    for rel in PRESENT_REPO_PATHS:
        write_text(resolve(root, Path(rel)), "present\n")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(marker)
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks = 0
    expected = (
        1
        + len(NOTE_MARKERS)
        + sum(len(values) for values in FILE_MARKERS.values())
        + len(PRESENT_REPO_PATHS)
        + len(GAP_REPO_PATHS)
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="lane25_artifact_diff_note_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE)
            write_text(path, remove_marker(read_text(path), marker))
            assert ("MISSING_NOTE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for path, markers in FILE_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                file_path = resolve(root, path)
                write_text(file_path, remove_marker(read_text(file_path), marker))
                key = f"{path.relative_to(ROOT)}::{marker}"
                assert ("MISSING_ALIGNMENT_MARKERS", key) in collect_issues(root)
                checks += 1

        for rel in PRESENT_REPO_PATHS:
            build_self_test_root(root)
            resolve(root, Path(rel)).unlink()
            assert ("MISSING_PRESENT_REPO_PATHS", rel) in collect_issues(root)
            checks += 1

        for rel in GAP_REPO_PATHS:
            build_self_test_root(root)
            write_text(resolve(root, Path(rel)), "should stay missing\n")
            assert ("UNEXPECTED_PRESENT_GAP_PATHS", rel) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        resolve(root, NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing note did not abort")

    assert checks == expected, (checks, expected)
    print("PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 25 artifact-diff note aligned to the current direct-readback helper packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARTIFACT_DIFF_NOTE=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_ALIGNMENT_MARKER_COUNT={sum(len(values) for values in FILE_MARKERS.values())}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_PRESENT_PATH_COUNT={len(PRESENT_REPO_PATHS)}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_GAP_PATH_COUNT={len(GAP_REPO_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
