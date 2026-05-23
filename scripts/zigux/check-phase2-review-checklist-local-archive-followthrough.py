#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
LOCAL_ARCHIVE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-local-archive-contract.md"
LOCAL_ARCHIVE_CONTRACT_CHECK = ROOT / "scripts" / "zigux" / "check-phase2-local-archive-contract.py"
BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET = ROOT / "scripts" / "zigux" / "check-phase2-bootstrap-note-local-archive-packet.py"

REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
)

PHASE2_NOTES_MARKERS = (
    "`Documentation/zigux/phase2-local-archive-contract.md` and `scripts/zigux/check-phase2-local-archive-contract.py` keep the still-missing repo-local archive payload wording fail-closed: `third_party/README.md` owns the exact archive-path replay, while the broader Phase 2 reminder packet keeps `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` explicit until current `master` actually materializes `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`.",
)

LOCAL_ARCHIVE_NOTE_MARKERS = (
    "# Phase 2 Local Archive Contract",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` remain the current direct-readback anchors for the pinned archive contract, the local-first `third_party`, mirror, then direct-download bootstrap order, and the shipped Lane 05 reminder guards.",
    "`scripts/zigux/check-phase2-local-archive-contract.py` keeps this focused Phase 2 note fail-closed against current repo reality: when `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` is still absent it requires the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay, and it only allows the exact archive-path replay back into this note after that pinned payload lands on current `master`.",
    "current `master` still does not materialize `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, so keep the repo-local archive wording tied to `third_party/README.md`, the two Lane 05 reminder guards, and the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay until that pinned payload actually lands.",
)

LOCAL_ARCHIVE_CONTRACT_CHECK_MARKERS = (
    'ARCHIVE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-local-archive-contract.md"',
    "PHASE2_LOCAL_ARCHIVE_CONTRACT=pass",
    LOCAL_ARCHIVE_NOTE_MARKERS[2],
)

BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKERS = (
    'LOCAL_ARCHIVE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-local-archive-contract.md"',
    "PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET=pass",
    PHASE2_NOTES_MARKERS[0],
    LOCAL_ARCHIVE_NOTE_MARKERS[2],
)

PHASE2_NOTES_EXACT_COUNT_MARKERS = (
    PHASE2_NOTES_MARKERS[0],
)

LOCAL_ARCHIVE_NOTE_EXACT_COUNT_MARKERS = (
    LOCAL_ARCHIVE_NOTE_MARKERS[2],
    LOCAL_ARCHIVE_NOTE_MARKERS[3],
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    review_checklist = read_text(resolve_path(root, REVIEW_CHECKLIST))
    phase2_notes = read_text(resolve_path(root, PHASE2_NOTES))
    local_archive_note = read_text(resolve_path(root, LOCAL_ARCHIVE_NOTE))
    local_archive_contract_check = read_text(resolve_path(root, LOCAL_ARCHIVE_CONTRACT_CHECK))
    bootstrap_note_local_archive_packet = read_text(resolve_path(root, BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET))

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing(review_checklist, REVIEW_CHECKLIST_MARKERS, "review-checklist"))
    issues.extend(collect_missing(phase2_notes, PHASE2_NOTES_MARKERS, "phase2-notes"))
    issues.extend(collect_exact_count(phase2_notes, PHASE2_NOTES_EXACT_COUNT_MARKERS, "phase2-notes-count"))
    issues.extend(collect_missing(local_archive_note, LOCAL_ARCHIVE_NOTE_MARKERS, "local-archive-note"))
    issues.extend(collect_exact_count(local_archive_note, LOCAL_ARCHIVE_NOTE_EXACT_COUNT_MARKERS, "local-archive-note-count"))
    issues.extend(
        collect_missing(
            local_archive_contract_check,
            LOCAL_ARCHIVE_CONTRACT_CHECK_MARKERS,
            "local-archive-contract-check",
        )
    )
    issues.extend(
        collect_missing(
            bootstrap_note_local_archive_packet,
            BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKERS,
            "bootstrap-note-local-archive-packet",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)
    print("PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_FOLLOWTHROUGH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, LOCAL_ARCHIVE_NOTE), "\n".join(LOCAL_ARCHIVE_NOTE_MARKERS) + "\n")
    write_text(
        resolve_path(root, LOCAL_ARCHIVE_CONTRACT_CHECK),
        "\n".join(LOCAL_ARCHIVE_CONTRACT_CHECK_MARKERS) + "\n",
    )
    write_text(
        resolve_path(root, BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET),
        "\n".join(BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKERS) + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 11

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_local_archive_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        review_path = resolve_path(root, REVIEW_CHECKLIST)
        review_path.write_text(
            replace_once(review_path.read_text(encoding="utf-8"), REVIEW_CHECKLIST_MARKERS[1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("review-checklist", REVIEW_CHECKLIST_MARKERS[1]) in issues
        checks_run += 1

        build_self_test_root(root)
        notes_path = resolve_path(root, PHASE2_NOTES)
        notes_path.write_text(
            notes_path.read_text(encoding="utf-8") + PHASE2_NOTES_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("phase2-notes-count", f"2::{PHASE2_NOTES_MARKERS[0]}") in issues
        checks_run += 1

        build_self_test_root(root)
        local_note_path = resolve_path(root, LOCAL_ARCHIVE_NOTE)
        local_note_path.write_text(
            replace_once(local_note_path.read_text(encoding="utf-8"), LOCAL_ARCHIVE_NOTE_MARKERS[3]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("local-archive-note", LOCAL_ARCHIVE_NOTE_MARKERS[3]) in issues
        checks_run += 1

        build_self_test_root(root)
        local_contract_check_path = resolve_path(root, LOCAL_ARCHIVE_CONTRACT_CHECK)
        local_contract_check_path.write_text(
            replace_once(
                local_contract_check_path.read_text(encoding="utf-8"),
                LOCAL_ARCHIVE_CONTRACT_CHECK_MARKERS[1],
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("local-archive-contract-check", LOCAL_ARCHIVE_CONTRACT_CHECK_MARKERS[1]) in issues
        checks_run += 1

        build_self_test_root(root)
        packet_path = resolve_path(root, BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET)
        packet_path.write_text(
            replace_once(
                packet_path.read_text(encoding="utf-8"),
                BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKERS[1],
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "bootstrap-note-local-archive-packet",
            BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKERS[1],
        ) in issues
        checks_run += 1

        for rel_path in (
            REVIEW_CHECKLIST,
            PHASE2_NOTES,
            LOCAL_ARCHIVE_NOTE,
            LOCAL_ARCHIVE_CONTRACT_CHECK,
            BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET,
        ):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_FOLLOWTHROUGH_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_FOLLOWTHROUGH_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 review-checklist packet aligned with the local-archive follow-through now carried by the lane review surface."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_FOLLOWTHROUGH=pass")
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_FOLLOWTHROUGH_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(LOCAL_ARCHIVE_NOTE_MARKERS) + len(LOCAL_ARCHIVE_CONTRACT_CHECK_MARKERS) + len(BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKERS)}"
    )
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_FOLLOWTHROUGH_EXACT_COUNT_MARKER_COUNT="
        f"{len(PHASE2_NOTES_EXACT_COUNT_MARKERS) + len(LOCAL_ARCHIVE_NOTE_EXACT_COUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
