#!/usr/bin/env python3
"""Validate the dedicated Phase 3 validator-support surface note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
REQUIRED_MARKERS = (
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/run-phase3-checks.py",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/phase3_check_lib.py --self-test",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --check",
    "python3 scripts/zigux/run-phase3-checks.py --self-test",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3-selftest",
    "make -C zigux phase3",
    "shipped helper entrypoints on current `master`",
)
REQUIRED_CURRENT_PACKET_MARKERS = (
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test",
)
REQUIRED_SHARED_REMINDER_MARKERS = (
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing note: {path}") from exc


def validate_text(text: str) -> list[str]:
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if "## Current packet" not in text:
        missing.append("missing current packet section")
        return missing
    if "## Review boundary" not in text:
        missing.append("missing review boundary section")
        return missing
    if "## Shared reminder" not in text:
        missing.append("missing shared reminder section")
        return missing

    current_packet = text.split("## Current packet", 1)[1].split("## Review boundary", 1)[0]
    shared_reminder = text.split("## Shared reminder", 1)[1]

    missing.extend(
        f"current packet missing marker: {marker}"
        for marker in REQUIRED_CURRENT_PACKET_MARKERS
        if marker not in current_packet
    )
    missing.extend(
        f"shared reminder missing marker: {marker}"
        for marker in REQUIRED_SHARED_REMINDER_MARKERS
        if marker not in shared_reminder
    )
    return missing


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    sample += "\n## Current packet\n" + "\n".join(REQUIRED_CURRENT_PACKET_MARKERS)
    sample += "\n## Review boundary\nshipped helper entrypoints on current `master`\n"
    sample += "\n## Shared reminder\n" + "\n".join(REQUIRED_SHARED_REMINDER_MARKERS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    unique_marker = "scripts/zigux/validate-phase3-validator-support-surface.py"
    broken = validate_text(sample.replace(unique_marker, ""))
    if not any(unique_marker in entry for entry in broken):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected missing marker was not reported")
        return 1

    current_packet_marker = "Documentation/zigux/phase3-abi-h-boundary-next-step.md"
    broken = validate_text(sample.replace(current_packet_marker, "", 1))
    if f"current packet missing marker: {current_packet_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected current packet marker was not reported")
        return 1

    focused_replay_marker = "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"
    broken = validate_text(sample.replace(focused_replay_marker, ""))
    if not any(focused_replay_marker in entry for entry in broken):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected focused replay marker was not reported")
        return 1
    if f"current packet missing marker: {focused_replay_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected focused replay current packet marker was not reported")
        return 1

    mmio_consumer_marker = "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"
    broken = validate_text(sample.replace(mmio_consumer_marker, ""))
    if not any(mmio_consumer_marker in entry for entry in broken):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected mmio consumer marker was not reported")
        return 1
    if f"current packet missing marker: {mmio_consumer_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected mmio consumer current packet marker was not reported")
        return 1

    wrapper_selftest_marker = "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test"
    before, separator, after = sample.rpartition(wrapper_selftest_marker)
    broken = validate_text(before + after if separator else sample)
    if f"current packet missing marker: {wrapper_selftest_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected wrapper self-test current packet marker was not reported")
        return 1

    shared_reminder_marker = "zigux/uapi/dev_t.zig"
    broken = validate_text(sample.rsplit(shared_reminder_marker, 1)[0])
    if f"shared reminder missing marker: {shared_reminder_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder marker was not reported")
        return 1

    scripts_readme_marker = "scripts/zigux/README.md"
    broken = validate_text(sample.replace(scripts_readme_marker, "", 1))
    if f"shared reminder missing marker: {scripts_readme_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected scripts README reminder marker was not reported")
        return 1

    print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains Documentation/zigux/",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator coverage without reading repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    note_path = args.repo_root / NOTE_PATH
    text = load_text(note_path)
    missing = validate_text(text)
    if missing:
        for marker in missing:
            print(f"missing marker: {marker}", file=sys.stderr)
        return 1

    print(f"validated {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
