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
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/run-phase3-checks.py",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-abi-bindings-survey.md",
    "Documentation/zigux/phase3-bindings-governance.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
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

CURRENT_PACKET_MARKERS = {
    "Documentation/zigux/phase3-kernel-export-shim-governance.md": 1,
    "Documentation/zigux/phase3-abi-bindings-survey.md": 1,
    "Documentation/zigux/phase3-bindings-governance.md": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py": 1,
    "zigux/uapi/dev_t.zig": 1,
    "zigux/bindings/abi.zig": 1,
    "zigux/Makefile": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py": 1,
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py": 1,
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test": 1,
}

REVIEW_BOUNDARY_MARKERS = {
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "scripts/zigux/validate-phase3-validator-support-surface.py": 1,
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py": 1,
    "Documentation/zigux/phase3-abi-bindings-survey.md": 1,
    "Documentation/zigux/phase3-bindings-governance.md": 1,
    "Documentation/zigux/phase3-kernel-export-shim-governance.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "closed together when either note drifts": 1,
}

SHARED_REMINDER_MARKERS = {
    "scripts/zigux/README.md": 1,
    "zigux/tests/README.md": 1,
    "scripts/zigux/validate_phase3_selftest.py": 1,
    "scripts/zigux/validate-phase3-validator-support-surface.py": 1,
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py": 1,
    "Documentation/zigux/phase3-abi-bindings-survey.md": 1,
    "Documentation/zigux/phase3-bindings-governance.md": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/review-checklist.md": 1,
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md": 1,
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py": 1,
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py": 1,
    "zigux/uapi/dev_t.zig": 1,
    "zigux/bindings/abi.zig": 1,
    "make -C zigux phase3-selftest": 1,
}

BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS = {
    "include/zigux/dev_t.h": 1,
    "zigux/uapi/version.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
    "scripts/zigux/check-phase3-abi.py": 1,
    "scripts/zigux/validate-phase3-export-uapi-survey.py": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py": 1,
    "make -C zigux phase3-validate": 1,
}

BOUNDARY_NOTE_NEXT_STEP_MARKERS = {
    "keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey": 1,
    "and next-step notes while leaving the narrower `zigux/uapi/version.zig`": 1,
    "export/UAPI packet actually grows": 1,
    "include/zigux/dev_t.h": 1,
    "zigux/uapi/version.zig": 1,
    "scripts/zigux/check-phase3-abi.py": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py": 1,
}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(text: str, heading: str, next_heading: str | None) -> str | None:
    if heading not in text:
        return None
    section = text.split(heading, 1)[1]
    if next_heading is not None and next_heading in section:
        section = section.split(next_heading, 1)[0]
    elif next_heading is None and "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def replace_in_section(
    text: str,
    heading: str,
    next_heading: str | None,
    old: str,
    new: str = "",
) -> str:
    prefix, marker, suffix = text.partition(heading)
    if not marker:
        return text
    if next_heading is None:
        section, next_marker, tail = suffix, "", ""
    else:
        section, next_marker, tail = suffix.partition(next_heading)
    return prefix + marker + section.replace(old, new, 1) + next_marker + tail


def check_marker_counts(
    section: str | None,
    marker_counts: dict[str, int],
    label: str,
    missing_message: str,
) -> list[str]:
    if section is None:
        return [missing_message]
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
    issues = [f"missing marker: {marker}" for marker in REQUIRED_MARKERS if marker not in text]
    issues.extend(
        check_marker_counts(
            extract_section(text, "## Current packet", "## Review boundary"),
            CURRENT_PACKET_MARKERS,
            "current packet",
            "missing current packet section",
        )
    )
    issues.extend(
        check_marker_counts(
            extract_section(text, "## Review boundary", "## Non-goals"),
            REVIEW_BOUNDARY_MARKERS,
            "review boundary",
            "missing review boundary section",
        )
    )
    issues.extend(
        check_marker_counts(
            extract_section(text, "## Shared reminder", None),
            SHARED_REMINDER_MARKERS,
            "shared reminder",
            "missing shared reminder section",
        )
    )
    return issues


def validate_boundary_note_text(text: str) -> list[str]:
    issues: list[str] = []
    issues.extend(
        check_marker_counts(
            extract_section(text, "## Current landed surface", "## Next bounded step"),
            BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS,
            "boundary note current surface",
            "boundary note missing section: ## Current landed surface",
        )
    )
    issues.extend(
        check_marker_counts(
            extract_section(text, "## Next bounded step", "## Non-goals"),
            BOUNDARY_NOTE_NEXT_STEP_MARKERS,
            "boundary note next-step",
            "boundary note missing section: ## Next bounded step",
        )
    )
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    note_path = repo_root / NOTE_PATH
    if not note_path.is_file():
        return [f"missing note: {note_path.as_posix()}"]

    issues = validate_text(load_text(note_path))

    boundary_note_path = repo_root / BOUNDARY_NOTE_PATH
    if not boundary_note_path.is_file():
        issues.append(f"missing boundary note: {boundary_note_path.as_posix()}")
    else:
        issues.extend(validate_boundary_note_text(load_text(boundary_note_path)))

    return issues


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_note_text() -> str:
    sample = "\n".join(REQUIRED_MARKERS)
    sample += "\n## Current packet\n" + "\n".join(CURRENT_PACKET_MARKERS)
    sample += "\n## Review boundary\n" + "\n".join(REVIEW_BOUNDARY_MARKERS)
    sample += "\n## Non-goals\n- stub\n"
    sample += "\n## Shared reminder\n" + "\n".join(SHARED_REMINDER_MARKERS)
    return sample


def sample_boundary_note_text() -> str:
    next_step_markers = [
        marker
        for marker in BOUNDARY_NOTE_NEXT_STEP_MARKERS
        if marker != "zigux/uapi/version.zig"
    ]
    sample = "## Current landed surface\n" + "\n".join(
        BOUNDARY_NOTE_CURRENT_SURFACE_MARKERS
    )
    sample += "\n## Next bounded step\n" + "\n".join(next_step_markers)
    sample += "\n## Non-goals\n- stub\n"
    return sample


def run_self_test() -> int:
    note_sample = sample_note_text()
    boundary_sample = sample_boundary_note_text()

    if validate_text(note_sample):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected note sample to validate")
        return 1

    if validate_boundary_note_text(boundary_sample):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected boundary-note sample to validate")
        return 1

    issues = validate_text(
        replace_in_section(
            note_sample,
            "## Current packet",
            "## Review boundary",
            "Documentation/zigux/phase3-bindings-governance.md",
        )
    )
    if not any(
        "Documentation/zigux/phase3-bindings-governance.md" in issue
        for issue in issues
    ):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected current-packet bindings-governance drift was not reported")
        return 1

    issues = validate_text(
        replace_in_section(
            note_sample,
            "## Review boundary",
            "## Non-goals",
            "Documentation/zigux/phase3-abi-bindings-survey.md",
        )
    )
    if not any(
        "Documentation/zigux/phase3-abi-bindings-survey.md" in issue
        for issue in issues
    ):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected review-boundary bindings-survey drift was not reported")
        return 1

    issues = validate_text(
        replace_in_section(
            note_sample,
            "## Shared reminder",
            None,
            "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
        )
    )
    if not any(
        "scripts/zigux/validate-phase3-linux-zigux-header-governance.py" in issue
        for issue in issues
    ):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected shared-reminder governance-validator drift was not reported")
        return 1

    issues = validate_boundary_note_text(
        boundary_sample.replace("include/zigux/dev_t.h", "", 1)
    )
    if not any("include/zigux/dev_t.h" in issue for issue in issues):
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("expected boundary-note current-surface drift was not reported")
        return 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_support_") as temp_dir:
        root = Path(temp_dir)
        write_text(root / NOTE_PATH, note_sample)
        write_text(root / BOUNDARY_NOTE_PATH, boundary_sample)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        (root / BOUNDARY_NOTE_PATH).unlink()
        expected = f"missing boundary note: {(root / BOUNDARY_NOTE_PATH).as_posix()}"
        if expected not in validate_repo(root):
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
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
