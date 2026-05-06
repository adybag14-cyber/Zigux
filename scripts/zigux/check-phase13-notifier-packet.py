#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/notifier_chain_view.zig",
    "include/zigux/abi.h",
    "include/zigux/notifier_abi.h",
    "zigux/tests/phase13_build.zig",
]

SURVEY_MARKERS = [
    "lane key: `P13-L18`",
    "`include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence",
    "`zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers",
    "`scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet",
    "shared Phase 13 build intentionally omits this packet",
]

BINDING_MARKERS = [
    "pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
    "pub const NotifierBlockRef",
    "pub const RawNotifierHeadRef",
    "pub const NotifierChainView",
    "pub const NotifierChainSummary",
]

HELPER_MARKERS = [
    "pub fn viewFromHead",
    "pub fn summarize",
    "pub fn hasNonincreasingPriorityOrder",
    "summarize keeps ordered terminated chains marked as nonincreasing priority",
    "summarize clears the priority-order flag when priorities rise",
]

HEADER_MARKERS = [
    "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
    "struct zigux_notifier_chain_view",
    "struct zigux_notifier_chain_summary",
    "zigux_notifier_chain_view_from_head",
    "zigux_notifier_chain_summarize",
    "zigux_notifier_chain_has_nonincreasing_priority_order",
]

REVIEWABILITY_MARKERS = [
    'try std.testing.expectEqualStrings("P13-L18", manifest.lane_key);',
    'const packet_checker_text = try readRepoFile(allocator, "scripts/zigux/check-phase13-notifier-packet.py");',
    'try expectContains(notifier_helper_text, "pub fn hasNonincreasingPriorityOrder");',
    'try expectContains(packet_checker_text, "PHASE13_NOTIFIER_PACKET=pass");',
    'try expectContains(packet_checker_text, "\\"phase13-notifier-focused-packet-checker\\"");',
    'try expectContains(exported_notifier_abi_text, "zigux_notifier");',
    'try expectContains(survey_note, "`scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet");',
    'if (std.mem.eql(u8, gap.id, "phase13-notifier-focused-packet-checker")) {',
    'try std.testing.expectEqualStrings("scripts/zigux/check-phase13-notifier-packet.py", gap.zigux_destination);',
]

MANIFEST_SUMMARY_KEYS = [
    "preexisting_phase13_build_present",
    "preexisting_notifier_binding_present",
    "preexisting_list_view_present",
    "preexisting_hlist_view_present",
    "preexisting_exported_list_abi_present",
    "preexisting_notifier_helper_present",
    "preexisting_exported_notifier_abi_present",
    "preexisting_phase13_notifier_reviewability_present",
    "preexisting_phase13_notifier_survey_note_present",
]

REQUIRED_GAPS = {
    "phase13-notifier-helper-surface": "zigux/helpers/notifier_chain_view.zig",
    "phase13-exported-notifier-c-header-surface": "include/zigux/notifier_abi.h",
    "phase13-notifier-focused-packet-checker": "scripts/zigux/check-phase13-notifier-packet.py",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_manifest(text: str) -> list[str]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"phase13-notifier-manifest:json:{exc.msg}"]

    issues: list[str] = []
    if manifest.get("lane_key") != "P13-L18":
        issues.append("phase13-notifier-manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        issues.append("phase13-notifier-manifest:phase")

    summary = manifest.get("survey_summary", {})
    for key in MANIFEST_SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase13-notifier-manifest-summary:{key}")

    gaps = {
        gap.get("id"): gap
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_destination in REQUIRED_GAPS.items():
        gap = gaps.get(gap_id)
        if gap is None:
            issues.append(f"phase13-notifier-manifest-gap:{gap_id}")
            continue
        if gap.get("status") != "starter_landed":
            issues.append(f"phase13-notifier-manifest-gap-status:{gap_id}")
        if gap.get("zigux_destination") != expected_destination:
            issues.append(f"phase13-notifier-manifest-gap-destination:{gap_id}")
    return issues


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    survey_text = read_text(root / "Documentation/zigux/phase13-notifier-list-survey.md")
    manifest_text = read_text(root / "zigux/tests/phase13_notifier_list_manifest.json")
    reviewability_text = read_text(root / "zigux/tests/phase13_notifier_list_reviewability.zig")
    binding_text = read_text(root / "zigux/bindings/notifier_abi.zig")
    helper_text = read_text(root / "zigux/helpers/notifier_chain_view.zig")
    header_text = read_text(root / "include/zigux/notifier_abi.h")
    build_text = read_text(root / "zigux/tests/phase13_build.zig")

    issues.extend(collect_missing(survey_text, SURVEY_MARKERS, "phase13-notifier-survey"))
    issues.extend(collect_missing(binding_text, BINDING_MARKERS, "phase13-notifier-binding"))
    issues.extend(collect_missing(helper_text, HELPER_MARKERS, "phase13-notifier-helper"))
    issues.extend(collect_missing(header_text, HEADER_MARKERS, "phase13-notifier-header"))
    issues.extend(collect_missing(reviewability_text, REVIEWABILITY_MARKERS, "phase13-notifier-reviewability"))
    issues.extend(validate_manifest(manifest_text))

    if "phase13_notifier" in build_text:
        issues.append("phase13-build:unexpected_notifier_replay_step")

    return issues


def seed_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "// stub\n")

    write_text(root / "Documentation/zigux/phase13-notifier-list-survey.md", "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / "zigux/bindings/notifier_abi.zig", "\n".join(BINDING_MARKERS) + "\n")
    write_text(root / "zigux/helpers/notifier_chain_view.zig", "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / "include/zigux/notifier_abi.h", "\n".join(HEADER_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase13_notifier_list_reviewability.zig", "\n".join(REVIEWABILITY_MARKERS) + "\n")
    write_text(
        root / "scripts/zigux/check-phase13-notifier-packet.py",
        'print("PHASE13_NOTIFIER_PACKET=pass")\n'
        'print("\\"phase13-notifier-focused-packet-checker\\"")\n',
    )
    write_text(root / "include/zigux/abi.h", "struct zigux_list_view {}\n")
    write_text(root / "zigux/tests/phase13_build.zig", 'const phase13_devres_tests = b.addTest(.{});\n')
    write_text(
        root / "zigux/tests/phase13_notifier_list_manifest.json",
        json.dumps(
            {
                "lane_key": "P13-L18",
                "phase": "Phase 13",
                "survey_summary": {key: True for key in MANIFEST_SUMMARY_KEYS},
                "gaps": [
                    {
                        "id": gap_id,
                        "status": "starter_landed",
                        "zigux_destination": destination,
                    }
                    for gap_id, destination in REQUIRED_GAPS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    )


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise SystemExit(f"phase13-notifier-packet-self-test:{label}:got={got_text}:want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_notifier_packet_") as temp_dir:
        root = Path(temp_dir)
        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-notifier-list-survey.md", "lane key: `P13-L18`\n")
        assert_only(
            validate(root),
            [
                "phase13-notifier-survey:`include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence",
                "phase13-notifier-survey:`zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers",
                "phase13-notifier-survey:`scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet",
                "phase13-notifier-survey:shared Phase 13 build intentionally omits this packet",
            ],
            "survey_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/bindings/notifier_abi.zig", "pub const NotifierBlockRef = extern struct {};\n")
        assert_only(
            validate(root),
            [
                "phase13-notifier-binding:pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
                "phase13-notifier-binding:pub const RawNotifierHeadRef",
                "phase13-notifier-binding:pub const NotifierChainView",
                "phase13-notifier-binding:pub const NotifierChainSummary",
            ],
            "binding_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/helpers/notifier_chain_view.zig", "pub fn summarize() void {}\n")
        assert_only(
            validate(root),
            [
                "phase13-notifier-helper:pub fn viewFromHead",
                "phase13-notifier-helper:pub fn hasNonincreasingPriorityOrder",
                "phase13-notifier-helper:summarize keeps ordered terminated chains marked as nonincreasing priority",
                "phase13-notifier-helper:summarize clears the priority-order flag when priorities rise",
            ],
            "helper_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "include/zigux/notifier_abi.h", "zigux_notifier_chain_view_from_head\n")
        assert_only(
            validate(root),
            [
                "phase13-notifier-header:ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
                "phase13-notifier-header:struct zigux_notifier_chain_view",
                "phase13-notifier-header:struct zigux_notifier_chain_summary",
                "phase13-notifier-header:zigux_notifier_chain_summarize",
                "phase13-notifier-header:zigux_notifier_chain_has_nonincreasing_priority_order",
            ],
            "header_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_notifier_list_reviewability.zig", 'try std.testing.expectEqualStrings("P13-L18", manifest.lane_key);\n')
        assert_only(
            validate(root),
            [
                'phase13-notifier-reviewability:const packet_checker_text = try readRepoFile(allocator, "scripts/zigux/check-phase13-notifier-packet.py");',
                'phase13-notifier-reviewability:try expectContains(notifier_helper_text, "pub fn hasNonincreasingPriorityOrder");',
                'phase13-notifier-reviewability:try expectContains(packet_checker_text, "PHASE13_NOTIFIER_PACKET=pass");',
                'phase13-notifier-reviewability:try expectContains(packet_checker_text, "\\"phase13-notifier-focused-packet-checker\\"");',
                'phase13-notifier-reviewability:try expectContains(exported_notifier_abi_text, "zigux_notifier");',
                'phase13-notifier-reviewability:try expectContains(survey_note, "`scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet");',
                'phase13-notifier-reviewability:if (std.mem.eql(u8, gap.id, "phase13-notifier-focused-packet-checker")) {',
                'phase13-notifier-reviewability:try std.testing.expectEqualStrings("scripts/zigux/check-phase13-notifier-packet.py", gap.zigux_destination);',
            ],
            "reviewability_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_notifier_list_manifest.json",
            json.dumps({"lane_key": "P13-L18", "phase": "Phase 13", "survey_summary": {}}, indent=2) + "\n",
        )
        assert_only(
            validate(root),
            [
                "phase13-notifier-manifest-summary:preexisting_phase13_build_present",
                "phase13-notifier-manifest-summary:preexisting_notifier_binding_present",
                "phase13-notifier-manifest-summary:preexisting_list_view_present",
                "phase13-notifier-manifest-summary:preexisting_hlist_view_present",
                "phase13-notifier-manifest-summary:preexisting_exported_list_abi_present",
                "phase13-notifier-manifest-summary:preexisting_notifier_helper_present",
                "phase13-notifier-manifest-summary:preexisting_exported_notifier_abi_present",
                "phase13-notifier-manifest-summary:preexisting_phase13_notifier_reviewability_present",
                "phase13-notifier-manifest-summary:preexisting_phase13_notifier_survey_note_present",
                "phase13-notifier-manifest-gap:phase13-notifier-helper-surface",
                "phase13-notifier-manifest-gap:phase13-exported-notifier-c-header-surface",
                "phase13-notifier-manifest-gap:phase13-notifier-focused-packet-checker",
            ],
            "manifest_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_build.zig", "const phase13_notifier_tests = b.addTest(.{});\n")
        assert_only(
            validate(root),
            ["phase13-build:unexpected_notifier_replay_step"],
            "build_adjacent_guard_failed",
        )
        case_count += 1

        (root / "include/zigux/notifier_abi.h").unlink()
        assert_only(
            validate(root),
            ["missing_file:include/zigux/notifier_abi.h"],
            "required_file_guard_failed",
        )
        case_count += 1

    print("PHASE13_NOTIFIER_PACKET=pass")
    print(f"PHASE13_NOTIFIER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shipped Phase 13 notifier/list packet surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(f"PHASE13_NOTIFIER_PACKET_ISSUE={issue}")
        return 1

    print("PHASE13_NOTIFIER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
