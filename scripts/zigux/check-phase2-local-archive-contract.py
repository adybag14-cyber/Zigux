#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
ARCHIVE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-local-archive-contract.md"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
ARCHIVE_PATH = ROOT / "third_party" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"

COMMON_NOTE_MARKERS = (
    "# Phase 2 Local Archive Contract",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` remain the current direct-readback anchors for the pinned archive contract, the local-first `third_party`, mirror, then direct-download bootstrap order, and the shipped Lane 05 reminder guards.",
    "`scripts/zigux/check-phase2-local-archive-contract.py` keeps this focused Phase 2 note fail-closed against current repo reality: when `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` is still absent it requires the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay, and it only allows the exact archive-path replay back into this note after that pinned payload lands on current `master`.",
)

ABSENT_ARCHIVE_NOTE_MARKERS = (
    "current `master` still does not materialize `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, so keep the repo-local archive wording tied to `third_party/README.md`, the two Lane 05 reminder guards, and the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay until that pinned payload actually lands.",
)

PRESENT_ARCHIVE_NOTE_MARKERS = (
    "current `master` does materialize `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, so keep the exact repo-local archive replay `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` explicit beside the README contract and the two Lane 05 reminder guards.",
)

ABSENT_ARCHIVE_FORBIDDEN_MARKERS = PRESENT_ARCHIVE_NOTE_MARKERS
PRESENT_ARCHIVE_FORBIDDEN_MARKERS = ABSENT_ARCHIVE_NOTE_MARKERS

THIRD_PARTY_README_MARKERS = (
    "# Zigux third-party archives",
    "## Current pinned Zig archive contract",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    archive_note = read_text(resolve_path(root, ARCHIVE_NOTE))
    third_party_readme = read_text(resolve_path(root, THIRD_PARTY_README))
    archive_exists = resolve_path(root, ARCHIVE_PATH).is_file()

    required_note_markers = COMMON_NOTE_MARKERS + (
        PRESENT_ARCHIVE_NOTE_MARKERS if archive_exists else ABSENT_ARCHIVE_NOTE_MARKERS
    )
    forbidden_docs_markers = PRESENT_ARCHIVE_FORBIDDEN_MARKERS if archive_exists else ABSENT_ARCHIVE_FORBIDDEN_MARKERS

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(archive_note, required_note_markers, "MISSING_ARCHIVE_NOTE_MARKERS"))
    issues.extend(collect_forbidden_markers(archive_note, forbidden_docs_markers, "FORBIDDEN_ARCHIVE_NOTE_MARKERS"))
    issues.extend(
        collect_missing_markers(
            third_party_readme,
            THIRD_PARTY_README_MARKERS,
            "MISSING_THIRD_PARTY_README_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_LOCAL_ARCHIVE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_root(root: Path, *, archive_exists: bool) -> None:
    docs_lines = list(COMMON_NOTE_MARKERS)
    docs_lines.extend(PRESENT_ARCHIVE_NOTE_MARKERS if archive_exists else ABSENT_ARCHIVE_NOTE_MARKERS)
    write_text(resolve_path(root, ARCHIVE_NOTE), "\n".join(docs_lines) + "\n")
    write_text(resolve_path(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_README_MARKERS) + "\n")
    archive_path = resolve_path(root, ARCHIVE_PATH)
    if archive_exists:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_bytes(b"archive-present")
    elif archive_path.exists():
        archive_path.unlink()


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        2
        + len(COMMON_NOTE_MARKERS)
        + len(ABSENT_ARCHIVE_NOTE_MARKERS)
        + len(PRESENT_ARCHIVE_NOTE_MARKERS)
        + len(THIRD_PARTY_README_MARKERS)
        + 6
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_local_archive_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_root(root, archive_exists=False)
        assert collect_issues(root) == []
        checks_run += 1

        build_root(root, archive_exists=True)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in COMMON_NOTE_MARKERS:
            build_root(root, archive_exists=False)
            path = resolve_path(root, ARCHIVE_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_ARCHIVE_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for marker in ABSENT_ARCHIVE_NOTE_MARKERS:
            build_root(root, archive_exists=False)
            path = resolve_path(root, ARCHIVE_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_ARCHIVE_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for marker in PRESENT_ARCHIVE_NOTE_MARKERS:
            build_root(root, archive_exists=True)
            path = resolve_path(root, ARCHIVE_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_ARCHIVE_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for marker in THIRD_PARTY_README_MARKERS:
            build_root(root, archive_exists=False)
            path = resolve_path(root, THIRD_PARTY_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_THIRD_PARTY_README_MARKERS", marker) in issues
            checks_run += 1

        build_root(root, archive_exists=False)
        absent_docs = resolve_path(root, ARCHIVE_NOTE)
        absent_docs.write_text(absent_docs.read_text(encoding="utf-8") + PRESENT_ARCHIVE_NOTE_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("FORBIDDEN_ARCHIVE_NOTE_MARKERS", PRESENT_ARCHIVE_NOTE_MARKERS[0]) in issues
        checks_run += 1

        build_root(root, archive_exists=True)
        present_docs = resolve_path(root, ARCHIVE_NOTE)
        present_docs.write_text(present_docs.read_text(encoding="utf-8") + ABSENT_ARCHIVE_NOTE_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("FORBIDDEN_ARCHIVE_NOTE_MARKERS", ABSENT_ARCHIVE_NOTE_MARKERS[0]) in issues
        checks_run += 1

        for rel_path in (ARCHIVE_NOTE, THIRD_PARTY_README):
            build_root(root, archive_exists=False)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

        build_root(root, archive_exists=False)
        absent_docs = resolve_path(root, ARCHIVE_NOTE)
        absent_text = absent_docs.read_text(encoding="utf-8")
        absent_text = absent_text.replace(ABSENT_ARCHIVE_NOTE_MARKERS[0], PRESENT_ARCHIVE_NOTE_MARKERS[0])
        absent_docs.write_text(absent_text, encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_ARCHIVE_NOTE_MARKERS", ABSENT_ARCHIVE_NOTE_MARKERS[0]) in issues
        assert ("FORBIDDEN_ARCHIVE_NOTE_MARKERS", PRESENT_ARCHIVE_NOTE_MARKERS[0]) in issues
        checks_run += 1

        build_root(root, archive_exists=True)
        present_docs = resolve_path(root, ARCHIVE_NOTE)
        present_text = present_docs.read_text(encoding="utf-8")
        present_text = present_text.replace(PRESENT_ARCHIVE_NOTE_MARKERS[0], ABSENT_ARCHIVE_NOTE_MARKERS[0])
        present_docs.write_text(present_text, encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_ARCHIVE_NOTE_MARKERS", PRESENT_ARCHIVE_NOTE_MARKERS[0]) in issues
        assert ("FORBIDDEN_ARCHIVE_NOTE_MARKERS", ABSENT_ARCHIVE_NOTE_MARKERS[0]) in issues
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_LOCAL_ARCHIVE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_LOCAL_ARCHIVE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 docs-root archive contract aligned with the actual repo-local pinned archive payload state."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    archive_exists = resolve_path(args.root.resolve(), ARCHIVE_PATH).is_file()
    print("PHASE2_LOCAL_ARCHIVE_CONTRACT=pass")
    print(f"PHASE2_LOCAL_ARCHIVE_CONTRACT_ARCHIVE_STATUS={'present' if archive_exists else 'missing'}")
    print(
        "PHASE2_LOCAL_ARCHIVE_CONTRACT_MARKER_COUNT="
        f"{len(COMMON_NOTE_MARKERS) + len(THIRD_PARTY_README_MARKERS) + (len(PRESENT_ARCHIVE_NOTE_MARKERS) if archive_exists else len(ABSENT_ARCHIVE_NOTE_MARKERS))}"
    )
    print(
        "PHASE2_LOCAL_ARCHIVE_CONTRACT_FORBIDDEN_MARKER_COUNT="
        f"{len(PRESENT_ARCHIVE_FORBIDDEN_MARKERS) if archive_exists else len(ABSENT_ARCHIVE_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
