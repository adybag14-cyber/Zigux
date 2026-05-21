#!/usr/bin/env python3
"""Validate the dedicated Phase 3 include/linux/zigux.h governance note."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys

HEADER_PATH = Path("include/linux/zigux.h")
NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")

ROLE_MARKER = (
    "PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for "
    "already-landed ABI, boundary-header, and starter dev_t review surfaces only"
)
REQUIRED_SCOPE_MARKERS = {
    "PHASE3_ZIGUX_H_PATH=include/linux/zigux.h": 1,
    "PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only": 1,
    "PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md": 1,
    "PHASE3_ZIGUX_H_EXPORT_UAPI_SURVEY=Documentation/zigux/phase3-export-uapi-boundary-survey.md": 1,
    "PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json": 1,
    ROLE_MARKER: 1,
}
REQUIRED_NOTE_MARKERS = {
    "`include/linux/zigux.h` remains the Linux-facing relay and aggregation header for already-landed ABI, boundary-header, and starter `dev_t` review surfaces only": 1,
    "new top-level helper families should not land in `include/linux/zigux.h` by themselves": 1,
    "growth in this header is only reviewable when the same bounded change keeps the canonical owner headers, the shared Phase 3 packet notes, and the manifest-backed inventory aligned": 1,
    "helper naming churn, alias-only growth, or relay-only expansion without packet-local proof should be treated as reviewability risk rather than Phase 3 closure": 1,
    "if a new boundary family needs its own ownership note, that note should land before or with the new header surface instead of being implied by aggregation here": 1,
    "keep them as thin named relays over the canonical ABI header and the shipped starter UAPI companions rather than moving semantic ownership here": 1,
}
HEADER_INCLUDE_MARKERS = (
    "#include <zigux/abi.h>",
    "#include <zigux/dev_t.h>",
)
HEADER_HELPERS = (
    "zigux_uapi_version_current",
    "zigux_uapi_version_has_current_abi_major",
    "zigux_uapi_version_has_current_abi_minor",
    "zigux_uapi_version_has_current_header_family_revision",
    "zigux_uapi_version_matches_current",
    "zigux_uapi_boundary_header_current",
    "zigux_uapi_boundary_header_compatible",
    "zigux_uapi_boundary_header_has_current_abi_version",
    "zigux_uapi_boundary_header_is_canonical",
    "zigux_uapi_boundary_header_is_compatible",
    "zigux_uapi_boundary_header_extends_boundary",
    "zigux_uapi_boundary_header_requested_extra_bytes",
    "zigux_uapi_boundary_header_canonicalize",
    "zigux_uapi_validate_boundary_header",
    "zigux_boundary_header_make",
    "zigux_boundary_header_make_compatible",
    "zigux_boundary_header_is_current_abi_version",
    "zigux_boundary_header_is_compatible_size",
    "zigux_boundary_header_is_canonical_size",
    "zigux_boundary_header_is_compatible",
    "zigux_boundary_header_is_canonical",
    "zigux_boundary_header_extends_boundary",
    "zigux_boundary_header_requested_extra_bytes",
    "zigux_boundary_header_canonicalize",
    "zigux_validate_boundary_header",
    "zigux_uapi_dev_t_fields_is_valid",
    "zigux_uapi_dev_t_fields_range_is_valid",
)
NOTE_HELPERS = (
    "`zigux_uapi_version_current()`",
    "`zigux_uapi_version_has_current_*()`",
    "`zigux_uapi_version_matches_current()`",
    "`zigux_uapi_boundary_header_current()`",
    "`zigux_uapi_boundary_header_compatible()`",
    "`zigux_uapi_boundary_header_is_canonical()`",
    "`zigux_uapi_boundary_header_is_compatible()`",
    "`zigux_uapi_boundary_header_extends_boundary()`",
    "`zigux_uapi_boundary_header_requested_extra_bytes()`",
    "`zigux_uapi_boundary_header_canonicalize()`",
    "`zigux_boundary_header_make()`",
    "`zigux_boundary_header_make_compatible()`",
    "`zigux_boundary_header_is_current_abi_version()`",
    "`zigux_boundary_header_is_compatible_size()`",
    "`zigux_boundary_header_is_canonical_size()`",
    "`zigux_boundary_header_is_compatible()`",
    "`zigux_boundary_header_is_canonical()`",
    "`zigux_boundary_header_extends_boundary()`",
    "`zigux_boundary_header_requested_extra_bytes()`",
    "`zigux_boundary_header_canonicalize()`",
    "`zigux_uapi_dev_t_fields_is_valid()`",
    "`zigux_uapi_dev_t_fields_range_is_valid()`",
)


def _git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def load_text(path: Path, what: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing {what}: {path}") from exc


def validate_text(note_text: str, header_text: str) -> list[str]:
    issues: list[str] = []

    for marker, expected_count in REQUIRED_SCOPE_MARKERS.items():
        actual_count = note_text.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"scope marker count drift: {marker} (expected {expected_count}, found {actual_count})"
            )

    expected_blob_marker = f"PHASE3_ZIGUX_H_BLOB_SHA={_git_blob_sha(header_text)}"
    actual_blob_count = note_text.count(expected_blob_marker)
    if actual_blob_count != 1:
        issues.append(
            f"blob marker drift: {expected_blob_marker} (expected 1, found {actual_blob_count})"
        )

    for marker, expected_count in REQUIRED_NOTE_MARKERS.items():
        actual_count = note_text.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"note marker count drift: {marker} (expected {expected_count}, found {actual_count})"
            )

    for include_marker in HEADER_INCLUDE_MARKERS:
        actual_count = header_text.count(include_marker)
        if actual_count != 1:
            issues.append(
                f"header include count drift: {include_marker} (expected 1, found {actual_count})"
            )

    for helper in HEADER_HELPERS:
        if not re.search(rf"static inline[^\n]*\b{re.escape(helper)}\s*\(", header_text):
            issues.append(f"header helper missing: {helper}")

    for helper in NOTE_HELPERS:
        if helper not in note_text:
            issues.append(f"governance note helper marker missing: {helper}")

    return issues


def run_self_test() -> int:
    sample_header = """#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include <zigux/abi.h>
#include <zigux/dev_t.h>

static inline int zigux_uapi_version_current(void) { return 0; }
static inline int zigux_uapi_version_has_current_abi_major(void) { return 0; }
static inline int zigux_uapi_version_has_current_abi_minor(void) { return 0; }
static inline int zigux_uapi_version_has_current_header_family_revision(void) { return 0; }
static inline int zigux_uapi_version_matches_current(void) { return 0; }
static inline int zigux_uapi_boundary_header_current(void) { return 0; }
static inline int zigux_uapi_boundary_header_compatible(void) { return 0; }
static inline int zigux_uapi_boundary_header_has_current_abi_version(void) { return 0; }
static inline int zigux_uapi_boundary_header_is_canonical(void) { return 0; }
static inline int zigux_uapi_boundary_header_is_compatible(void) { return 0; }
static inline int zigux_uapi_boundary_header_extends_boundary(void) { return 0; }
static inline int zigux_uapi_boundary_header_requested_extra_bytes(void) { return 0; }
static inline int zigux_uapi_boundary_header_canonicalize(void) { return 0; }
static inline int zigux_uapi_validate_boundary_header(void) { return 0; }
static inline int zigux_boundary_header_make(void) { return 0; }
static inline int zigux_boundary_header_make_compatible(void) { return 0; }
static inline int zigux_boundary_header_is_current_abi_version(void) { return 0; }
static inline int zigux_boundary_header_is_compatible_size(void) { return 0; }
static inline int zigux_boundary_header_is_canonical_size(void) { return 0; }
static inline int zigux_boundary_header_is_compatible(void) { return 0; }
static inline int zigux_boundary_header_is_canonical(void) { return 0; }
static inline int zigux_boundary_header_extends_boundary(void) { return 0; }
static inline int zigux_boundary_header_requested_extra_bytes(void) { return 0; }
static inline int zigux_boundary_header_canonicalize(void) { return 0; }
static inline int zigux_validate_boundary_header(void) { return 0; }
static inline int zigux_uapi_dev_t_fields_is_valid(void) { return 0; }
static inline int zigux_uapi_dev_t_fields_range_is_valid(void) { return 0; }

#endif
"""
    sample_blob = _git_blob_sha(sample_header)
    sample_note = f"""# Phase 3 Linux `zigux.h` Header Governance

- PHASE3_ZIGUX_H_PATH=include/linux/zigux.h
- PHASE3_ZIGUX_H_BLOB_SHA={sample_blob}
- PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only
- PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md
- PHASE3_ZIGUX_H_EXPORT_UAPI_SURVEY=Documentation/zigux/phase3-export-uapi-boundary-survey.md
- PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json
- {ROLE_MARKER}

`include/linux/zigux.h` remains the Linux-facing relay and aggregation header for already-landed ABI, boundary-header, and starter `dev_t` review surfaces only
new top-level helper families should not land in `include/linux/zigux.h` by themselves
growth in this header is only reviewable when the same bounded change keeps the canonical owner headers, the shared Phase 3 packet notes, and the manifest-backed inventory aligned
helper naming churn, alias-only growth, or relay-only expansion without packet-local proof should be treated as reviewability risk rather than Phase 3 closure
if a new boundary family needs its own ownership note, that note should land before or with the new header surface instead of being implied by aggregation here
keep them as thin named relays over the canonical ABI header and the shipped starter UAPI companions rather than moving semantic ownership here

`zigux_uapi_version_current()`
`zigux_uapi_version_has_current_*()`
`zigux_uapi_version_matches_current()`
`zigux_uapi_boundary_header_current()`
`zigux_uapi_boundary_header_compatible()`
`zigux_uapi_boundary_header_is_canonical()`
`zigux_uapi_boundary_header_is_compatible()`
`zigux_uapi_boundary_header_extends_boundary()`
`zigux_uapi_boundary_header_requested_extra_bytes()`
`zigux_uapi_boundary_header_canonicalize()`
`zigux_boundary_header_make()`
`zigux_boundary_header_make_compatible()`
`zigux_boundary_header_is_current_abi_version()`
`zigux_boundary_header_is_compatible_size()`
`zigux_boundary_header_is_canonical_size()`
`zigux_boundary_header_is_compatible()`
`zigux_boundary_header_is_canonical()`
`zigux_boundary_header_extends_boundary()`
`zigux_boundary_header_requested_extra_bytes()`
`zigux_boundary_header_canonicalize()`
`zigux_uapi_dev_t_fields_is_valid()`
`zigux_uapi_dev_t_fields_range_is_valid()`
"""
    issues = validate_text(sample_note, sample_header)
    if issues:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("\n".join(issues))
        return 1

    broken = validate_text(sample_note.replace(ROLE_MARKER, "", 1), sample_header)
    expected = f"scope marker count drift: {ROLE_MARKER} (expected 1, found 0)"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected role-marker drift was not reported")
        return 1

    broken = validate_text(
        sample_note.replace("`zigux_boundary_header_requested_extra_bytes()`", "", 1),
        sample_header,
    )
    expected = "governance note helper marker missing: `zigux_boundary_header_requested_extra_bytes()`"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected helper-marker drift was not reported")
        return 1

    broken = validate_text(sample_note, sample_header.replace("#include <zigux/dev_t.h>\n", "", 1))
    expected = "header include count drift: #include <zigux/dev_t.h> (expected 1, found 0)"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected include drift was not reported")
        return 1

    broken = validate_text(sample_note, sample_header.replace(
        "static inline int zigux_boundary_header_is_current_abi_version(void) { return 0; }\n",
        "",
        1,
    ))
    expected = "header helper missing: zigux_boundary_header_is_current_abi_version"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected header-helper drift was not reported")
        return 1

    broken = validate_text(sample_note.replace(sample_blob, "deadbeef", 1), sample_header)
    expected = f"blob marker drift: PHASE3_ZIGUX_H_BLOB_SHA={sample_blob} (expected 1, found 0)"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected blob drift was not reported")
        return 1

    print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    note_text = load_text(args.repo_root / NOTE_PATH, "governance note")
    header_text = load_text(args.repo_root / HEADER_PATH, "Linux-facing header")
    issues = validate_text(note_text, header_text)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())