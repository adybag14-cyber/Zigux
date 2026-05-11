#!/usr/bin/env python3
"""Validate the dedicated Phase 3 validator-support surface note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
BOUNDARY_NOTE_PATH = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
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
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test",
)
REQUIRED_REVIEW_BOUNDARY_MARKERS = (
    "Documentation/zigux/phase3-validator-support-surface.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "closed together when either note drifts",
)
REQUIRED_SHARED_REMINDER_MARKERS = (
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
)
REQUIRED_BOUNDARY_NOTE_POLICY_MARKERS = (
    "keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey",
    "and next-step notes while leaving the narrower `zigux/uapi/version.zig`",
    "export/UAPI packet actually grows",
)
REQUIRED_BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS = (
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "make -C zigux phase3-validate",
)
REQUIRED_BOUNDARY_NOTE_NEXT_STEP_MARKERS = (
    *REQUIRED_BOUNDARY_NOTE_POLICY_MARKERS,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_section(text: str, heading: str, next_heading: str) -> str | None:
    if heading not in text:
        return None
    section = text.split(heading, 1)[1]
    if next_heading in section:
        section = section.split(next_heading, 1)[0]
    return section


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
    review_boundary = text.split("## Review boundary", 1)[1].split("## Non-goals", 1)[0]
    shared_reminder = text.split("## Shared reminder", 1)[1]

    missing.extend(
        f"current packet missing marker: {marker}"
        for marker in REQUIRED_CURRENT_PACKET_MARKERS
        if marker not in current_packet
    )
    missing.extend(
        f"review boundary missing marker: {marker}"
        for marker in REQUIRED_REVIEW_BOUNDARY_MARKERS
        if marker not in review_boundary
    )
    missing.extend(
        f"shared reminder missing marker: {marker}"
        for marker in REQUIRED_SHARED_REMINDER_MARKERS
        if marker not in shared_reminder
    )
    return missing


def validate_boundary_note_text(text: str) -> list[str]:
    issues: list[str] = []

    current_landed_surface = _extract_section(
        text,
        "## Current landed surface",
        "## Next bounded step",
    )
    if current_landed_surface is None:
        issues.append("boundary note missing section: ## Current landed surface")
    else:
        issues.extend(
            f"boundary note current surface missing marker: {marker}"
            for marker in REQUIRED_BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS
            if marker not in current_landed_surface
        )

    next_bounded_step = _extract_section(
        text,
        "## Next bounded step",
        "## Non-goals",
    )
    if next_bounded_step is None:
        issues.append("boundary note missing section: ## Next bounded step")
    else:
        issues.extend(
            f"boundary note next-step missing marker: {marker}"
            for marker in REQUIRED_BOUNDARY_NOTE_NEXT_STEP_MARKERS
            if marker not in next_bounded_step
        )

    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    note_path = repo_root / NOTE_PATH
    try:
        note_text = load_text(note_path)
    except FileNotFoundError:
        return [f"missing note: {note_path.as_posix()}"]
    issues.extend(validate_text(note_text))

    boundary_note_path = repo_root / BOUNDARY_NOTE_PATH
    try:
        boundary_note_text = load_text(boundary_note_path)
    except FileNotFoundError:
        issues.append(f"missing boundary note: {boundary_note_path.as_posix()}")
    else:
        issues.extend(validate_boundary_note_text(boundary_note_text))

    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_text() -> str:
    sample = "\n".join(REQUIRED_MARKERS)
    sample += "\n## Current packet\n" + "\n".join(REQUIRED_CURRENT_PACKET_MARKERS)
    sample += "\n## Review boundary\n" + "\n".join(REQUIRED_REVIEW_BOUNDARY_MARKERS)
    sample += "\n## Non-goals\n- stub\n"
    sample += "\n## Shared reminder\n" + "\n".join(REQUIRED_SHARED_REMINDER_MARKERS)
    return sample


def _boundary_note_sample_text() -> str:
    sample = "## Current landed surface\n"
    sample += "\n".join(REQUIRED_BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS)
    sample += "\n## Next bounded step\n"
    sample += "\n".join(REQUIRED_BOUNDARY_NOTE_NEXT_STEP_MARKERS)
    sample += "\n## Non-goals\n- stub\n"
    return sample


def run_self_test() -> int:
    sample = _sample_text()
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

    current_packet_dev_t_marker = "zigux/uapi/dev_t.zig"
    before, separator, after = sample.partition("## Current packet\n")
    if not separator:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected current packet section separator was not found")
        return 1
    current_packet, separator, tail = after.partition("\n## Review boundary\n")
    if not separator:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review boundary section separator was not found")
        return 1
    current_packet_broken = current_packet.replace(current_packet_dev_t_marker, "", 1)
    broken = validate_text(
        before + "## Current packet\n" + current_packet_broken + "\n## Review boundary\n" + tail
    )
    if f"current packet missing marker: {current_packet_dev_t_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected current packet dev_t marker was not reported")
        return 1

    shared_reminder_next_step_marker = (
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md"
    )
    before, separator, after = sample.rpartition(shared_reminder_next_step_marker)
    broken = validate_text(before + after if separator else sample)
    if f"shared reminder missing marker: {shared_reminder_next_step_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder next-step marker was not reported")
        return 1

    review_boundary_next_step_marker = (
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md"
    )
    before, separator, after = sample.partition("## Review boundary\n")
    if not separator:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review boundary section separator was not found")
        return 1
    review_boundary, separator, tail = after.partition("\n## Non-goals\n")
    if not separator:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected non-goals section separator was not found")
        return 1
    review_boundary_broken = review_boundary.replace(
        review_boundary_next_step_marker, "", 1
    )
    broken = validate_text(
        before + "## Review boundary\n" + review_boundary_broken + "\n## Non-goals\n" + tail
    )
    if (
        f"review boundary missing marker: {review_boundary_next_step_marker}"
        not in broken
    ):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review boundary next-step marker was not reported")
        return 1

    review_boundary_closed_marker = "closed together when either note drifts"
    review_boundary_broken = review_boundary.replace(
        review_boundary_closed_marker, "", 1
    )
    broken = validate_text(
        before + "## Review boundary\n" + review_boundary_broken + "\n## Non-goals\n" + tail
    )
    if (
        f"review boundary missing marker: {review_boundary_closed_marker}"
        not in broken
    ):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review boundary fail-closed marker was not reported")
        return 1

    header_family_note_marker = "Documentation/zigux/phase3-abi-header-family-survey.md"
    before, separator, after = sample.rpartition(header_family_note_marker)
    broken = validate_text(before + after if separator else sample)
    if f"current packet missing marker: {header_family_note_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected header-family current packet marker was not reported")
        return 1

    current_packet_bindings_marker = "zigux/bindings/abi.zig"
    broken = validate_text(sample.replace(current_packet_bindings_marker, "", 1))
    if f"current packet missing marker: {current_packet_bindings_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected bindings current packet marker was not reported")
        return 1

    shared_reminder_bindings_marker = "zigux/bindings/abi.zig"
    before, separator, after = sample.rpartition(shared_reminder_bindings_marker)
    broken = validate_text(before + after if separator else sample)
    if f"shared reminder missing marker: {shared_reminder_bindings_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected bindings shared reminder marker was not reported")
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

    header_family_validator_marker = "scripts/zigux/validate-phase3-abi-header-family-survey.py"
    before, separator, after = sample.rpartition(header_family_validator_marker)
    broken = validate_text(before + after if separator else sample)
    if f"current packet missing marker: {header_family_validator_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected header-family validator current packet marker was not reported")
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

    shared_reminder_validator_marker = (
        "scripts/zigux/validate-phase3-validator-support-surface.py"
    )
    before, separator, after = sample.rpartition(shared_reminder_validator_marker)
    broken = validate_text(before + after if separator else sample)
    if (
        f"shared reminder missing marker: {shared_reminder_validator_marker}"
        not in broken
    ):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder validator marker was not reported")
        return 1

    scripts_readme_marker = "scripts/zigux/README.md"
    broken = validate_text(sample.replace(scripts_readme_marker, "", 1))
    if f"shared reminder missing marker: {scripts_readme_marker}" not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected scripts README reminder marker was not reported")
        return 1

    boundary_sample = _boundary_note_sample_text()
    if validate_boundary_note_text(boundary_sample):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected boundary-note policy sample to validate")
        return 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_support_") as temp_dir:
        root = Path(temp_dir)
        _write(root / NOTE_PATH, sample)
        _write(root / BOUNDARY_NOTE_PATH, boundary_sample)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        boundary_path = root / BOUNDARY_NOTE_PATH
        boundary_path.write_text(
            boundary_sample.replace(
                "and next-step notes while leaving the narrower `zigux/uapi/version.zig`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "boundary note next-step missing marker: "
            "and next-step notes while leaving the narrower `zigux/uapi/version.zig`"
        )
        if expected not in issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note policy drift was not reported")
            return 1

        _write(root / BOUNDARY_NOTE_PATH, boundary_sample)
        boundary_path.write_text(
            boundary_sample.replace(
                "zigux/uapi/version.zig",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "boundary note current surface missing marker: zigux/uapi/version.zig"
        )
        if expected not in issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note current-surface drift was not reported")
            return 1

        _write(root / BOUNDARY_NOTE_PATH, boundary_sample)
        before, separator, after = boundary_sample.partition("## Next bounded step\n")
        if not separator:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note next-step section separator was not found")
            return 1
        next_step, separator, tail = after.partition("\n## Non-goals\n")
        if not separator:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note non-goals separator was not found")
            return 1
        next_step = next_step.replace(
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
            "",
            1,
        )
        boundary_path.write_text(
            before
            + "## Next bounded step\n"
            + next_step
            + "\n## Non-goals\n"
            + tail
            + "\nscripts/zigux/validate-phase3-abi-bindings-syntax.py",
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "boundary note next-step missing marker: scripts/zigux/validate-phase3-abi-bindings-syntax.py"
        )
        if expected not in issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note section-scoped drift was not reported")
            return 1

        boundary_path.unlink()
        issues = validate_repo(root)
        expected = f"missing boundary note: {(root / BOUNDARY_NOTE_PATH).as_posix()}"
        if expected not in issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing boundary note was not reported")
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

    issues = validate_repo(args.repo_root)
    if issues:
        for marker in issues:
            print(f"missing marker: {marker}", file=sys.stderr)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
