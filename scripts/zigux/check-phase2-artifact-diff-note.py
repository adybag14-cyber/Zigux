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

PRESENT_REPO_PATHS = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/validate-phase4.py",
)

NOTE_MARKERS = (
    "# Artifact Diff Policy",
    "## Rules",
    "## Current Direct-Readback Packet",
    "`scripts/zigux/artifact_diff.py` is directly readable on current `master`",
    "`python3 scripts/zigux/artifact_diff.py --self-test` is the shipped helper replay for that contract today",
    "`scripts/zigux/check-artifact-diff-contract.py` is directly readable on current `master`",
    "`python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the shipped contract-checker replay for that helper packet today",
    "`scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable on current `master`",
    "`python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the shipped determinism replay for that helper packet today",
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py` is directly readable on current `master`",
    "`scripts/zigux/validate-phase4.py` is directly readable on current `master`",
    "## Current Reminder Surface",
    "current shared Phase 4 reminder surfaces still keep this docs-side note framed as a broader companion while the returned helper, contract checker, determinism checker, validator-replay checker, validator entrypoint, and direct local-only perf packet carry the direct current-head handoff",
    "broader build and bitmap replay companions still rely on split readback: authenticated contents reads can still flap for `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`, even though public raw fallback rereads return them on current `master`",
    "## Current Uses",
    "current Phase 4 reminder surfaces keep the helper, contract checker, determinism checker, validator-replay checker, returned validator entrypoint, repo-reality warning, direct local-only perf packet, and roadmap-backed `atomic64_diff` pair explicit while broader build and bitmap replay companions still wait on steadier authenticated blob-pin refresh",
    "## Next Honest Follow-Through",
    "refresh exact authenticated blob pins for `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` together once the split-readback path steadies",
)

FILE_MARKERS = {
    PHASE4_NOTE: (
        "In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
    ),
    REVIEW_CHECKLIST: (
        "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
        "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    ),
    SCRIPTS_README: (
        "the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair",
        "current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket: `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap in authenticated contents reads in this runtime, but public raw fallback rereads return those files on current `master`",
    ),
}

NOTE_TEMPLATE = """# Artifact Diff Policy

Zigux keeps host-side artifact snapshots only when they anchor a bounded parity or reminder claim that reviewers can replay honestly.

## Rules

- prefer text, JSON, or stable digest output over opaque binary blobs whenever the same review goal is possible
- keep artifact scope small enough that one lane can regenerate, compare, and review it without widening into unrelated closure work
- update an artifact in the same bounded change that changed the source behavior or reminder contract it documents
- keep helper, contract-checker, determinism, validator, and reminder-surface truthfulness explicit when broader build and bitmap replay companions still rely on split readback

## Current Direct-Readback Packet

- `scripts/zigux/artifact_diff.py` is directly readable on current `master`
- `python3 scripts/zigux/artifact_diff.py --self-test` is the shipped helper replay for that contract today
- `scripts/zigux/check-artifact-diff-contract.py` is directly readable on current `master`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the shipped contract-checker replay for that helper packet today
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable on current `master`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the shipped determinism replay for that helper packet today
- `scripts/zigux/check-phase4-artifact-diff-validator-replays.py` is directly readable on current `master`
- `scripts/zigux/validate-phase4.py` is directly readable on current `master`
- the directly readable helper-and-checker packet currently keeps the bounded `text`, `json`, and `bytes` comparison modes, the legacy `sha256 -> bytes` alias, the current helper self-test catalog, the current contract replay packet, the determinism self-test, and the validator replay surface explicit from the scripts root

## Current Reminder Surface

- keep this note aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md`
- current shared Phase 4 reminder surfaces still keep this docs-side note framed as a broader companion while the returned helper, contract checker, determinism checker, validator-replay checker, validator entrypoint, and direct local-only perf packet carry the direct current-head handoff
- broader build and bitmap replay companions still rely on split readback: authenticated contents reads can still flap for `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`, even though public raw fallback rereads return them on current `master`
- keep the host-side artifact-diff contract explicit here without claiming that the broader build, bitmap replay, or shared-CI perf-promotion packet is fully refreshed through exact authenticated blob capture

## Current Uses

- the helper and contract checker remain the shared comparison layer for bounded artifact-backed parity work under `scripts/zigux/`
- the determinism checker and validator-replay checker keep the helper summaries, contract catalogs, and validator packet fail-closed beside the direct helper replay
- current Phase 2 reminder surfaces already rely on the host-side artifact-diff contract indirectly for bounded fixture-backed parity lanes instead of reopening older missing-route closure wording
- current Phase 4 reminder surfaces keep the helper, contract checker, determinism checker, validator-replay checker, returned validator entrypoint, repo-reality warning, direct local-only perf packet, and roadmap-backed `atomic64_diff` pair explicit while broader build and bitmap replay companions still wait on steadier authenticated blob-pin refresh

## Next Honest Follow-Through

- narrow shared reminder surfaces only when direct current-head rereads prove they still overstate or understate the returned helper-and-checker packet
- refresh exact authenticated blob pins for `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` together once the split-readback path steadies
- repair `scripts/zigux/check-artifact-diff-contract.py` before treating the broader contract summary as fully synchronized with the current helper packet if the contract checker drifts on current-head reread
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


def build_sample_root(root: Path) -> None:
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
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="lane25_artifact_diff_note_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in NOTE_MARKERS:
            build_sample_root(root)
            path = resolve(root, NOTE)
            write_text(path, remove_marker(read_text(path), marker))
            assert ("MISSING_NOTE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for path, markers in FILE_MARKERS.items():
            for marker in markers:
                build_sample_root(root)
                file_path = resolve(root, path)
                write_text(file_path, remove_marker(read_text(file_path), marker))
                key = f"{path.relative_to(ROOT)}::{marker}"
                assert ("MISSING_ALIGNMENT_MARKERS", key) in collect_issues(root)
                checks += 1

        for rel in PRESENT_REPO_PATHS:
            build_sample_root(root)
            resolve(root, Path(rel)).unlink()
            assert ("MISSING_PRESENT_REPO_PATHS", rel) in collect_issues(root)
            checks += 1

        build_sample_root(root)
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
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root rooted in exact current marker expectations",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        sample_root = args.write_sample_root.resolve()
        build_sample_root(sample_root)
        print(f"PHASE2_ARTIFACT_DIFF_NOTE_SAMPLE_ROOT={sample_root}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARTIFACT_DIFF_NOTE=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_ALIGNMENT_MARKER_COUNT={sum(len(values) for values in FILE_MARKERS.values())}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_PRESENT_PATH_COUNT={len(PRESENT_REPO_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
