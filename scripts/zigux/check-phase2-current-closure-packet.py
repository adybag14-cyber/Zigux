#!/usr/bin/env python3
"""Check that the exact Phase 2 closure packet sentinel stays aligned."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
SENTINEL_PREFIX = "PHASE2_CURRENT_CLOSURE_PACKET="

EXPECTED_PACKET = (
    Path("Documentation/zigux/phase2-closure.md"),
    Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"),
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-lane05-install-zig-archive-verification.py"),
    Path("scripts/zigux/stage-pinned-zig-archive.py"),
    Path("scripts/zigux/check-lane05-stage-helper-contract.py"),
    Path("scripts/zigux/check-lane05-stage-helper-selftest.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/zig-toolchain-policy.json"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"),
    Path("scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"),
    Path("scripts/zigux/fixdep.zig"),
    Path("third_party/README.md"),
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/manifest.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/help_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/minimal_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/long_options_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"),
)

REQUIRED_NOTE_MARKERS = (
    "`PHASE2_STATUS=parked`",
    "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
    "PHASE2_NEXT_SAFE_STEP=",
    "archive-verification",
    "staged repo-local archive helper",
    "helper-local kconfig allconfig guard",
    "bounded genksyms bridge",
    "fixdep",
    "make-wrapper",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_closure_note_text(packet: tuple[Path, ...] = EXPECTED_PACKET) -> str:
    bullet_lines = "\n".join(f"- `{path.as_posix()}`" for path in packet)
    packet_csv = ",".join(path.as_posix() for path in packet)
    return (
        "# Phase 2 Closure\n\n"
        "## Status\n\n"
        "- `PHASE2_STATUS=parked`\n"
        "- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`\n"
        "- current authority: the archive-verification, staged repo-local archive helper, "
        "helper-local kconfig allconfig guard, bounded genksyms bridge, fixdep, and "
        "make-wrapper packet remain authoritative\n\n"
        "## Current Closure Packet\n\n"
        f"{bullet_lines}\n\n"
        f"- `{SENTINEL_PREFIX}{packet_csv}`\n"
        "- `PHASE2_CURRENT_GAP_PACKET=`\n"
        "- `PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again`\n"
    )


def parse_sentinel_packet(text: str) -> list[str] | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if SENTINEL_PREFIX not in line:
            continue
        start = line.index(SENTINEL_PREFIX) + len(SENTINEL_PREFIX)
        remainder = line[start:]
        if remainder.endswith("`"):
            remainder = remainder[:-1]
        if remainder.startswith("`"):
            remainder = remainder[1:]
        return [entry for entry in remainder.split(",") if entry]
    return None


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    closure_note_path = root / CLOSURE_NOTE_REL
    if not closure_note_path.is_file():
        return [f"missing_file:{CLOSURE_NOTE_REL.as_posix()}"]

    closure_note_text = closure_note_path.read_text(encoding="utf-8")
    actual_packet = parse_sentinel_packet(closure_note_text)
    expected_packet = [path.as_posix() for path in EXPECTED_PACKET]

    if actual_packet is None:
        issues.append(f"missing_closure_packet_sentinel:{SENTINEL_PREFIX}")
    else:
        if actual_packet != expected_packet:
            expected_set = set(expected_packet)
            actual_set = set(actual_packet)
            for entry in expected_packet:
                if entry not in actual_set:
                    issues.append(f"missing_closure_packet_entry:{entry}")
            for entry in actual_packet:
                if entry not in expected_set:
                    issues.append(f"unexpected_closure_packet_entry:{entry}")
            limit = min(len(expected_packet), len(actual_packet))
            for index in range(limit):
                if expected_packet[index] != actual_packet[index]:
                    issues.append(
                        "closure_packet_order_mismatch:"
                        f"index={index}:expected={expected_packet[index]}:actual={actual_packet[index]}"
                    )
                    break
            if len(actual_packet) != len(expected_packet):
                issues.append(
                    "closure_packet_count_mismatch:"
                    f"expected={len(expected_packet)}:actual={len(actual_packet)}"
                )

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in closure_note_text:
            issues.append(f"missing_note_marker:{marker}")

    for rel_path in EXPECTED_PACKET:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    return issues


def build_good_tree(root: Path, packet: tuple[Path, ...] = EXPECTED_PACKET) -> None:
    write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(packet))
    for rel_path in packet:
        if rel_path == CLOSURE_NOTE_REL:
            continue
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_current_closure_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-current-closure-packet:self-test:good_tree")
        case_count += 1

        build_good_tree(root)
        write_text(root / CLOSURE_NOTE_REL, "# Phase 2 Closure\n")
        issues = collect_issues(root)
        if f"missing_closure_packet_sentinel:{SENTINEL_PREFIX}" not in issues:
            raise SystemExit("phase2-current-closure-packet:self-test:missing_sentinel")
        case_count += 1

        build_good_tree(root)
        packet = list(EXPECTED_PACKET)
        packet.pop(3)
        write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(tuple(packet)))
        issues = collect_issues(root)
        if "missing_closure_packet_entry:Documentation/zigux/README.md" not in issues:
            raise SystemExit("phase2-current-closure-packet:self-test:missing_entry")
        case_count += 1

        build_good_tree(root)
        packet = list(EXPECTED_PACKET)
        packet.insert(1, Path("scripts/zigux/check-phase2-current-closure-packet.py"))
        write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(tuple(packet)))
        issues = collect_issues(root)
        if (
            "unexpected_closure_packet_entry:scripts/zigux/check-phase2-current-closure-packet.py"
            not in issues
        ):
            raise SystemExit("phase2-current-closure-packet:self-test:unexpected_entry")
        case_count += 1

        build_good_tree(root)
        packet = list(EXPECTED_PACKET)
        packet[0], packet[1] = packet[1], packet[0]
        write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(tuple(packet)))
        issues = collect_issues(root)
        expected_issue = (
            "closure_packet_order_mismatch:index=0:"
            "expected=Documentation/zigux/phase2-closure.md:"
            "actual=Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"
        )
        if expected_issue not in issues:
            raise SystemExit("phase2-current-closure-packet:self-test:order_mismatch")
        case_count += 1

        build_good_tree(root)
        write_text(
            root / CLOSURE_NOTE_REL,
            build_closure_note_text().replace("staged repo-local archive helper", "stage helper"),
        )
        issues = collect_issues(root)
        if "missing_note_marker:staged repo-local archive helper" not in issues:
            raise SystemExit("phase2-current-closure-packet:self-test:missing_note_marker")
        case_count += 1

    print("PHASE2_CURRENT_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CURRENT_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> int:
    build_good_tree(root)
    print(f"PHASE2_CURRENT_CLOSURE_PACKET_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the exact Phase 2 closure packet sentinel stays aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for replay coverage",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_CURRENT_CLOSURE_PACKET=fail")
        print("PHASE2_CURRENT_CLOSURE_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CURRENT_CLOSURE_PACKET_ISSUES_END")
        return 1

    print("PHASE2_CURRENT_CLOSURE_PACKET=pass")
    print(f"PHASE2_CURRENT_CLOSURE_PACKET_FILE_COUNT={len(EXPECTED_PACKET)}")
    print(f"PHASE2_CURRENT_CLOSURE_PACKET_MARKER_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
