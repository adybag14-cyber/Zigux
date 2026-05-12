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
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "zigux/Makefile",
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
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/Makefile",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test",
)
REQUIRED_REVIEW_BOUNDARY_MARKERS = (
    "Documentation/zigux/phase3-validator-support-surface.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "closed together when either note drifts",
)
REQUIRED_SHARED_REMINDER_MARKERS = (
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
    "make -C zigux phase3-selftest",
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
CURRENT_PACKET_MARKER_COUNTS = {
    marker: 1 for marker in REQUIRED_CURRENT_PACKET_MARKERS
}
REVIEW_BOUNDARY_MARKER_COUNTS = {
    marker: 1 for marker in REQUIRED_REVIEW_BOUNDARY_MARKERS
}
SHARED_REMINDER_MARKER_COUNTS = {
    marker: 1 for marker in REQUIRED_SHARED_REMINDER_MARKERS
}
BOUNDARY_NOTE_CURRENT_SURFACE_MARKER_COUNTS = {
    marker: 1 for marker in REQUIRED_BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS
}
BOUNDARY_NOTE_NEXT_STEP_MARKER_COUNTS = {
    marker: 1 for marker in REQUIRED_BOUNDARY_NOTE_NEXT_STEP_MARKERS
}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_section(text: str, heading: str, next_heading: str | None) -> str | None:
    if heading not in text:
        return None
    section = text.split(heading, 1)[1]
    if next_heading is not None and next_heading in section:
        section = section.split(next_heading, 1)[0]
    elif next_heading is None and "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def _check_section_marker_counts(
    section: str | None,
    marker_counts: dict[str, int],
    label: str,
    missing_section_message: str,
) -> list[str]:
    if section is None:
        return [missing_section_message]

    issues: list[str] = []
    for marker, expected_count in marker_counts.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"{label} marker count drift: {marker} "
                f"(expected {expected_count}, found {actual_count})"
            )
    return issues


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

    current_packet = _extract_section(
        text,
        "## Current packet",
        "## Review boundary",
    )
    review_boundary = _extract_section(
        text,
        "## Review boundary",
        "## Non-goals",
    )
    shared_reminder = _extract_section(
        text,
        "## Shared reminder",
        None,
    )

    missing.extend(
        _check_section_marker_counts(
            current_packet,
            CURRENT_PACKET_MARKER_COUNTS,
            "current packet",
            "missing current packet section",
        )
    )
    missing.extend(
        _check_section_marker_counts(
            review_boundary,
            REVIEW_BOUNDARY_MARKER_COUNTS,
            "review boundary",
            "missing review boundary section",
        )
    )
    missing.extend(
        _check_section_marker_counts(
            shared_reminder,
            SHARED_REMINDER_MARKER_COUNTS,
            "shared reminder",
            "missing shared reminder section",
        )
    )
    return missing


def validate_boundary_note_text(text: str) -> list[str]:
    issues: list[str] = []

    current_landed_surface = _extract_section(
        text,
        "## Current landed surface",
        "## Next bounded step",
    )
    issues.extend(
        _check_section_marker_counts(
            current_landed_surface,
            BOUNDARY_NOTE_CURRENT_SURFACE_MARKER_COUNTS,
            "boundary note current surface",
            "boundary note missing section: ## Current landed surface",
        )
    )

    next_bounded_step = _extract_section(
        text,
        "## Next bounded step",
        "## Non-goals",
    )
    issues.extend(
        _check_section_marker_counts(
            next_bounded_step,
            BOUNDARY_NOTE_NEXT_STEP_MARKER_COUNTS,
            "boundary note next-step",
            "boundary note missing section: ## Next bounded step",
        )
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
    sample += "\n".join(REQUIRED_BOUNDARY_NOTE_CURRENT_SURFACE_MARKER_COUNTS)
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
    expected = (
        "current packet marker count drift: "
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
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
    expected = (
        "current packet marker count drift: zigux/uapi/dev_t.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected current packet dev_t marker was not reported")
        return 1

    shared_reminder_next_step_marker = (
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md"
    )
    before, separator, after = sample.rpartition(shared_reminder_next_step_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "shared reminder marker count drift: "
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
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
        review_boundary_next_step_marker,
        "",
        1,
    )
    broken = validate_text(
        before + "## Review boundary\n" + review_boundary_broken + "\n## Non-goals\n" + tail
    )
    expected = (
        "review boundary marker count drift: "
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review boundary next-step marker was not reported")
        return 1

    review_boundary_closed_marker = "closed together when either note drifts"
    review_boundary_broken = review_boundary.replace(
        review_boundary_closed_marker,
        "",
        1,
    )
    broken = validate_text(
        before + "## Review boundary\n" + review_boundary_broken + "\n## Non-goals\n" + tail
    )
    expected = (
        "review boundary marker count drift: "
        "closed together when either note drifts "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review boundary fail-closed marker was not reported")
        return 1

    header_family_note_marker = "Documentation/zigux/phase3-abi-header-family-survey.md"
    before, separator, after = sample.rpartition(header_family_note_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "current packet marker count drift: "
        "Documentation/zigux/phase3-abi-header-family-survey.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected header-family current packet marker was not reported")
        return 1

    current_packet_bindings_marker = "zigux/bindings/abi.zig"
    broken = validate_text(sample.replace(current_packet_bindings_marker, "", 1))
    expected = (
        "current packet marker count drift: zigux/bindings/abi.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected bindings current packet marker was not reported")
        return 1

    current_packet_makefile_marker = "zigux/Makefile"
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
    current_packet_broken = current_packet.replace(current_packet_makefile_marker, "", 1)
    broken = validate_text(
        before + "## Current packet\n" + current_packet_broken + "\n## Review boundary\n" + tail
    )
    expected = (
        "current packet marker count drift: zigux/Makefile "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected makefile current packet marker was not reported")
        return 1

    shared_reminder_bindings_marker = "zigux/bindings/abi.zig"
    before, separator, after = sample.rpartition(shared_reminder_bindings_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "shared reminder marker count drift: zigux/bindings/abi.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected bindings shared reminder marker was not reported")
        return 1

    focused_replay_marker = "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"
    broken = validate_text(sample.replace(focused_replay_marker, ""))
    if not any(focused_replay_marker in entry for entry in broken):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected focused replay marker was not reported")
        return 1
    expected = (
        "current packet marker count drift: "
        "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected focused replay current packet marker was not reported")
        return 1

    mmio_consumer_marker = "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"
    broken = validate_text(sample.replace(mmio_consumer_marker, ""))
    if not any(mmio_consumer_marker in entry for entry in broken):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected mmio consumer marker was not reported")
        return 1
    expected = (
        "current packet marker count drift: "
        "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected mmio consumer current packet marker was not reported")
        return 1

    header_family_validator_marker = "scripts/zigux/validate-phase3-abi-header-family-survey.py"
    before, separator, after = sample.rpartition(header_family_validator_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "current packet marker count drift: "
        "scripts/zigux/validate-phase3-abi-header-family-survey.py "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected header-family validator current packet marker was not reported")
        return 1

    wrapper_selftest_marker = "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test"
    before, separator, after = sample.rpartition(wrapper_selftest_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "current packet marker count drift: "
        "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected wrapper self-test current packet marker was not reported")
        return 1

    shared_reminder_marker = "zigux/uapi/dev_t.zig"
    broken = validate_text(sample.rsplit(shared_reminder_marker, 1)[0])
    expected = (
        "shared reminder marker count drift: zigux/uapi/dev_t.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder marker was not reported")
        return 1

    shared_reminder_validator_marker = (
        "scripts/zigux/validate-phase3-validator-support-surface.py"
    )
    before, separator, after = sample.rpartition(shared_reminder_validator_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "shared reminder marker count drift: "
        "scripts/zigux/validate-phase3-validator-support-surface.py "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder validator marker was not reported")
        return 1

    shared_reminder_selftest_driver_marker = (
        "scripts/zigux/validate_phase3_selftest.py"
    )
    before, separator, after = sample.rpartition(shared_reminder_selftest_driver_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "shared reminder marker count drift: "
        "scripts/zigux/validate_phase3_selftest.py "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder selftest driver marker was not reported")
        return 1

    shared_reminder_selftest_route_marker = "make -C zigux phase3-selftest"
    before, separator, after = sample.rpartition(shared_reminder_selftest_route_marker)
    broken = validate_text(before + after if separator else sample)
    expected = (
        "shared reminder marker count drift: "
        "make -C zigux phase3-selftest "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder selftest route marker was not reported")
        return 1

    scripts_readme_marker = "scripts/zigux/README.md"
    broken = validate_text(sample.replace(scripts_readme_marker, "", 1))
    expected = (
        "shared reminder marker count drift: scripts/zigux/README.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected scripts README reminder marker was not reported")
        return 1

    shared_duplicate = sample.replace(
        "scripts/zigux/README.md",
        "scripts/zigux/README.md\nscripts/zigux/README.md",
        1,
    )
    broken = validate_text(shared_duplicate)
    expected = (
        "shared reminder marker count drift: scripts/zigux/README.md "
        "(expected 1, found 2)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder duplicate drift was not reported")
        return 1

    before, separator, after = sample.partition("\n## Shared reminder\n")
    if not separator:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder section separator was not found")
        return 1
    broken = validate_text(
        before
        + "\n## Shared reminder\n"
        + after.replace(
            "zigux/uapi/dev_t.zig",
            "## Future follow-through\nzigux/uapi/dev_t.zig",
            1,
        )
    )
    expected = (
        "shared reminder marker count drift: zigux/uapi/dev_t.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared reminder next-heading drift was not reported")
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
            "boundary note next-step marker count drift: "
            "and next-step notes while leaving the narrower `zigux/uapi/version.zig` "
            "(expected 1, found 0)"
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
            "boundary note current surface marker count drift: zigux/uapi/version.zig "
            "(expected 1, found 0)"
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
            "boundary note next-step marker count drift: "
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note section-scoped drift was not reported")
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
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py\n"
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
            1,
        )
        boundary_path.write_text(
            before
            + "## Next bounded step\n"
            + next_step
            + "\n## Non-goals\n"
            + tail,
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "boundary note next-step marker count drift: "
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py "
            "(expected 1, found 2)"
        )
        if expected not in issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected boundary-note duplicate drift was not reported")
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
