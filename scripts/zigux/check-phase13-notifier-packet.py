#!/usr/bin/env python3
"""Guard the adjacent Phase 13 notifier/list packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": (
        "`scripts/zigux/check-phase13-notifier-packet.py`",
        "`zigux/tests/phase13_notifier_list_manifest.json`",
        "`zigux/tests/phase13_notifier_list_reviewability.zig`",
        "`zigux/helpers/notifier_chain_view.zig`",
        "`make -C zigux phase13-validate`",
        "focused checker",
    ),
    "Documentation/zigux/phase13-notifier-summary-gap.md": (
        "`scripts/zigux/check-phase13-notifier-packet.py`",
        "`zigux/tests/phase13_notifier_list_manifest.json`",
        "`zigux/tests/phase13_notifier_list_reviewability.zig`",
        "`zigux/helpers/notifier_chain_view.zig`",
        "`make -C zigux phase13-validate`",
    ),
    "zigux/tests/phase13_notifier_list_manifest.json": (
        "\"lane_key\": \"P13-L18\"",
        "\"anchor\": \"drivers/tty/hvc/hvc_console.h\"",
        "\"current_notifier_packet_checker_present\": true",
        "\"current_phase13_notifier_list_manifest_present\": true",
        "\"current_phase13_notifier_list_reviewability_present\": true",
        "\"id\": \"phase13-notifier-focused-packet-checker\"",
        "\"id\": \"phase13-notifier-chain-helper-gap\"",
        "\"id\": \"phase13-build-route-gap\"",
    ),
    "zigux/tests/phase13_notifier_list_reviewability.zig": (
        'const manifest_text = @embedFile("phase13_notifier_list_manifest.json");',
        'readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-notifier-list-survey.md")',
        'readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-notifier-packet.py")',
        '"phase13-notifier-focused-packet-checker"',
        '"PHASE13_NOTIFIER_PACKET=pass"',
    ),
    "zigux/bindings/notifier_abi.zig": (
        "pub const NotifierBlock = extern struct",
        "pub fn chainHasNonincreasingPriority",
        "pub fn listHasConsistentBacklinks",
        "pub fn hlistHasConsistentPrevLinks",
    ),
    "zigux/helpers/list_view.zig": (
        "pub const ListView = struct",
        "pub fn hasConsistentBacklinks(self: ListView) bool",
        "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak",
    ),
    "zigux/helpers/hlist_view.zig": (
        "pub const HListView = struct",
        "pub fn hasConsistentPrevLinks(self: HListView) bool",
        "pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak",
    ),
    "include/zigux/abi.h": (
        "struct zigux_notifier_block {",
        "struct zigux_list_head {",
        "struct zigux_hlist_head {",
        "zigux_notifier_first_chain_priority_increase",
        "zigux_list_has_consistent_backlinks",
        "zigux_hlist_has_consistent_prev_links",
    ),
    "drivers/tty/hvc/hvc_console.h": (
        "int notifier_add_irq(struct hvc_struct *hp, int irq);",
        "void notifier_del_irq(struct hvc_struct *hp, int irq);",
        "void notifier_hangup_irq(struct hvc_struct *hp, int irq);",
    ),
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": (
        "`zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`",
    ),
}


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relpath, markers in REQUIRED_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")
    for relpath, markers in FORBIDDEN_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue
        for marker in markers:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")
    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_NOTIFIER_PACKET=fail")
    print("PHASE13_NOTIFIER_PACKET_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_NOTIFIER_PACKET_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    write_text(
        root,
        "Documentation/zigux/phase13-notifier-list-survey.md",
        "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-notifier-list-survey.md"]) + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase13-notifier-summary-gap.md",
        "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-notifier-summary-gap.md"]) + "\n",
    )
    for relpath, markers in REQUIRED_MARKERS.items():
        if relpath.startswith("Documentation/zigux/phase13-notifier-"):
            continue
        write_text(root, relpath, "\n".join(markers) + "\n")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-notifier-packet-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        survey_path = tempdir / "Documentation/zigux/phase13-notifier-list-survey.md"
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase13-notifier-packet.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-notifier-list-survey.md:`scripts/zigux/check-phase13-notifier-packet.py`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        manifest_path = tempdir / "zigux/tests/phase13_notifier_list_manifest.json"
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8").replace(
                '"id": "phase13-notifier-focused-packet-checker"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            'missing_marker:zigux/tests/phase13_notifier_list_manifest.json:"id": "phase13-notifier-focused-packet-checker"'
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        checker_input = tempdir / "zigux/helpers/list_view.zig"
        checker_input.write_text(
            checker_input.read_text(encoding="utf-8").replace(
                "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:zigux/helpers/list_view.zig:pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        reviewability_path = tempdir / "zigux/tests/phase13_notifier_list_reviewability.zig"
        reviewability_path.write_text(
            reviewability_path.read_text(encoding="utf-8").replace(
                '"PHASE13_NOTIFIER_PACKET=pass"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            'missing_marker:zigux/tests/phase13_notifier_list_reviewability.zig:"PHASE13_NOTIFIER_PACKET=pass"'
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        abi_path = tempdir / "include/zigux/abi.h"
        abi_path.unlink()
        issues = collect_issues(tempdir)
        assert "required file missing: include/zigux/abi.h" in issues
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_NOTIFIER_PACKET=pass")
    print(f"PHASE13_NOTIFIER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE13_NOTIFIER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
