#!/usr/bin/env python3
"""Validate the dedicated Phase 3 ABI header-family survey note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
REQUIRED_MARKERS = (
    "include/linux/zigux.h",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "zigux/Makefile",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)
REQUIRED_CURRENT_PACKET_LINE_MARKERS = {
    marker: f"- `{marker}`" for marker in REQUIRED_MARKERS
}
FORBIDDEN_CURRENT_PACKET_MARKERS = (
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
)
REQUIRED_REVIEW_BOUNDARY_MARKER_COUNTS = {
    "include/linux/zigux.h": 1,
    "include/zigux/abi.h": 1,
    "include/zigux/dev_t.h": 1,
    "zigux/bindings/abi.zig": 1,
    "zigux/kernel/export_shim.zig": 1,
    "zigux/uapi/version.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
    "starter UAPI surface remains a bounded version-plus-dev_t pair": 1,
}
REQUIRED_NON_GOALS_MARKER_COUNTS = {
    "no new exported header family claims": 1,
    "no runtime-loader or helper-lane expansion": 1,
    "no deep-core header migration beyond the shipped export and UAPI surface": 1,
}
REQUIRED_SHARED_REMINDER_MARKER_COUNTS = {
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md": 1,
    "Documentation/zigux/phase3-linux-zigux-header-governance.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/README.md": 1,
    "Documentation/zigux/review-checklist.md": 1,
    "scripts/zigux/README.md": 1,
    "zigux/tests/README.md": 1,
    "zigux/uapi/dev_t.zig": 1,
    "zigux/bindings/abi.zig": 1,
    "zigux/bindings/dev_t.zig": 1,
    "zigux/tests/phase3_abi_dump.zig": 1,
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c": 1,
    "zigux/tests/fixtures/phase3_abi/expected.json": 1,
    "scripts/zigux/validate-phase3-export-uapi-survey.py": 1,
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py": 1,
    "scripts/zigux/survey-phase3-abi-constant-parity.py": 1,
    "`include/zigux/dev_t.h` plus `zigux/uapi/version.zig` starter-companion detail": 1,
    "should stay anchored in this dedicated survey and the paired next-step note": 1,
}
REVIEW_BOUNDARY_PREFIX = "## Review boundary"
NON_GOALS_PREFIX = "## Non-goals"
SHARED_REMINDER_PREFIX = "## Shared reminder"


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing survey note: {path}") from exc


def _extract_section(text: str, start_prefix: str, next_prefix: str | None) -> str | None:
    if start_prefix not in text:
        return None
    section = text.split(start_prefix, 1)[1]
    if next_prefix is not None and next_prefix in section:
        section = section.split(next_prefix, 1)[0]
    elif next_prefix is None and "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def validate_text(text: str) -> list[str]:
    if "## Current packet" not in text:
        return ["missing current packet section"]
    if REVIEW_BOUNDARY_PREFIX not in text:
        return ["missing review boundary section"]

    current_packet = text.split("## Current packet", 1)[1].split(
        REVIEW_BOUNDARY_PREFIX, 1
    )[0]
    issues: list[str] = []
    for marker, line_marker in REQUIRED_CURRENT_PACKET_LINE_MARKERS.items():
        expected_count = 1
        actual_count = current_packet.count(line_marker)
        if actual_count != expected_count:
            issues.append(
                "current packet marker count drift: "
                f"{marker} (expected {expected_count}, found {actual_count})"
            )
    issues.extend(
        f"current packet still claims removed replay marker: {marker}"
        for marker in FORBIDDEN_CURRENT_PACKET_MARKERS
        if marker in current_packet
    )

    review_boundary = _extract_section(text, REVIEW_BOUNDARY_PREFIX, NON_GOALS_PREFIX)
    if review_boundary is None:
        issues.append("missing review boundary section")
        return issues

    for marker, expected_count in REQUIRED_REVIEW_BOUNDARY_MARKER_COUNTS.items():
        actual_count = review_boundary.count(marker)
        if actual_count != expected_count:
            issues.append(
                "review boundary marker count drift: "
                f"{marker} (expected {expected_count}, found {actual_count})"
            )

    non_goals = _extract_section(text, NON_GOALS_PREFIX, SHARED_REMINDER_PREFIX)
    if non_goals is None:
        issues.append("missing non-goals section")
        return issues

    for marker, expected_count in REQUIRED_NON_GOALS_MARKER_COUNTS.items():
        actual_count = non_goals.count(marker)
        if actual_count != expected_count:
            issues.append(
                "non-goals marker count drift: "
                f"{marker} (expected {expected_count}, found {actual_count})"
            )

    shared_reminder = _extract_section(text, SHARED_REMINDER_PREFIX, None)
    if shared_reminder is None:
        issues.append("missing shared reminder section")
        return issues

    for marker, expected_count in REQUIRED_SHARED_REMINDER_MARKER_COUNTS.items():
        actual_count = shared_reminder.count(marker)
        if actual_count != expected_count:
            issues.append(
                "shared reminder marker count drift: "
                f"{marker} (expected {expected_count}, found {actual_count})"
            )
    return issues


def run_self_test() -> int:
    sample = (
        "## Current packet\n"
        + "\n".join(REQUIRED_CURRENT_PACKET_LINE_MARKERS.values())
        + "\n## Review boundary\n"
        + "\n".join(REQUIRED_REVIEW_BOUNDARY_MARKER_COUNTS.keys())
        + "\n## Non-goals\n"
        + "\n".join(REQUIRED_NON_GOALS_MARKER_COUNTS.keys())
        + "\n## Shared reminder\n"
        + "\n".join(REQUIRED_SHARED_REMINDER_MARKER_COUNTS.keys())
        + "\n## Future follow-through\n"
        + "future marker\n"
    )
    issues = validate_text(sample)
    if issues:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("\n".join(issues))
        return 1

    broken = validate_text(sample.replace("include/zigux/abi.h", "", 1))
    expected = (
        "current packet marker count drift: include/zigux/abi.h "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected missing current-packet marker was not reported")
        return 1

    broken = validate_text(sample.replace("zigux/bindings/abi.zig", "", 1))
    expected = (
        "current packet marker count drift: zigux/bindings/abi.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected current-packet bindings marker was not reported")
        return 1

    broken = validate_text(sample.replace("zigux/bindings/dev_t.zig", "", 1))
    expected = (
        "current packet marker count drift: zigux/bindings/dev_t.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected current-packet dev_t binding marker was not reported")
        return 1

    broken = validate_text(sample.replace("zigux/tests/phase3_abi_dump.zig", "", 1))
    expected = (
        "current packet marker count drift: zigux/tests/phase3_abi_dump.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected current-packet dump marker was not reported")
        return 1

    duplicate = sample.replace(
        "- `zigux/uapi/dev_t.zig`\n",
        "- `zigux/uapi/dev_t.zig`\n- `zigux/uapi/dev_t.zig`\n",
        1,
    )
    broken = validate_text(duplicate)
    expected = (
        "current packet marker count drift: zigux/uapi/dev_t.zig "
        "(expected 1, found 2)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected duplicate current-packet marker drift was not reported")
        return 1

    broken = validate_text(
        sample.replace(
            "## Review boundary",
            "zigux/tests/phase3_export_uapi.zig\n## Review boundary",
            1,
        )
    )
    forbidden = (
        "current packet still claims removed replay marker: "
        "zigux/tests/phase3_export_uapi.zig"
    )
    if forbidden not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected removed replay marker was not reported")
        return 1

    before, separator, after = sample.partition("## Review boundary\n")
    if not separator:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected review boundary section separator was not found")
        return 1
    review_boundary, separator, tail = after.partition("\n## Non-goals\n")
    if not separator:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected non-goals section separator was not found")
        return 1

    review_boundary_broken = review_boundary.replace("include/zigux/dev_t.h", "", 1)
    broken = validate_text(
        before + "## Review boundary\n" + review_boundary_broken + "\n## Non-goals\n" + tail
    )
    expected = (
        "review boundary marker count drift: include/zigux/dev_t.h "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected review-boundary dev_t marker was not reported")
        return 1

    review_boundary_broken = review_boundary.replace("zigux/uapi/version.zig", "", 1)
    broken = validate_text(
        before
        + "## Review boundary\n"
        + review_boundary_broken
        + "\n## Non-goals\n"
        + tail
        + "\nzigux/uapi/version.zig\n"
    )
    expected = (
        "review boundary marker count drift: zigux/uapi/version.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected section-scoped version companion drift was not reported")
        return 1

    review_boundary_moved = review_boundary.replace(
        "starter UAPI surface remains a bounded version-plus-dev_t pair",
        "",
        1,
    )
    broken = validate_text(
        before
        + "## Review boundary\n"
        + review_boundary_moved
        + "\n## Non-goals\n"
        + tail
        + "\nstarter UAPI surface remains a bounded version-plus-dev_t pair\n"
    )
    expected = (
        "review boundary marker count drift: "
        "starter UAPI surface remains a bounded version-plus-dev_t pair "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected section-scoped review-boundary drift was not reported")
        return 1

    before, separator, after = sample.partition("## Non-goals\n")
    if not separator:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected non-goals section separator was not found")
        return 1
    non_goals, separator, tail = after.partition("\n## Shared reminder\n")
    if not separator:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected shared reminder section separator was not found")
        return 1

    broken_non_goals = non_goals.replace(
        "no runtime-loader or helper-lane expansion",
        "",
        1,
    )
    broken = validate_text(
        before
        + "## Non-goals\n"
        + broken_non_goals
        + "\n## Shared reminder\n"
        + tail
    )
    expected = (
        "non-goals marker count drift: no runtime-loader or helper-lane expansion "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected non-goals marker drift was not reported")
        return 1

    broken_non_goals = non_goals.replace(
        "no deep-core header migration beyond the shipped export and UAPI surface",
        "",
        1,
    )
    broken = validate_text(
        before
        + "## Non-goals\n"
        + broken_non_goals
        + "\n## Shared reminder\n"
        + tail
        + "\nno deep-core header migration beyond the shipped export and UAPI surface\n"
    )
    expected = (
        "non-goals marker count drift: "
        "no deep-core header migration beyond the shipped export and UAPI surface "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected section-scoped non-goals drift was not reported")
        return 1

    broken = validate_text(sample.replace("Documentation/zigux/README.md", "", 1))
    expected = (
        "shared reminder marker count drift: Documentation/zigux/README.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected docs README shared-reminder drift was not reported")
        return 1

    moved = sample.replace(
        "Documentation/zigux/phase3-export-uapi-boundary-survey.md\n",
        "",
        1,
    ).replace(
        "## Future follow-through\n",
        "## Future follow-through\n"
        "Documentation/zigux/phase3-export-uapi-boundary-survey.md\n",
        1,
    )
    broken = validate_text(moved)
    expected = (
        "shared reminder marker count drift: "
        "Documentation/zigux/phase3-export-uapi-boundary-survey.md "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected section-scoped shared-reminder drift was not reported")
        return 1

    duplicate = sample.replace(
        "scripts/zigux/README.md\n",
        "scripts/zigux/README.md\nscripts/zigux/README.md\n",
        1,
    )
    broken = validate_text(duplicate)
    expected = (
        "shared reminder marker count drift: scripts/zigux/README.md "
        "(expected 1, found 2)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected duplicate shared-reminder marker drift was not reported")
        return 1

    survey_text = sample
    before, separator, after = survey_text.partition("## Shared reminder\n")
    survey_text = before + separator + after.replace("zigux/bindings/dev_t.zig", "", 1)
    broken = validate_text(survey_text)
    expected = (
        "shared reminder marker count drift: zigux/bindings/dev_t.zig "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected bindings/dev_t shared reminder drift was not reported")
        return 1

    print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")
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

    survey_path = args.repo_root / SURVEY_PATH
    text = load_text(survey_path)
    issues = validate_text(text)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1

    print(f"validated {survey_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())