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
REQUIRED_SCOPE_MARKERS = {
    "PHASE3_ZIGUX_H_PATH=include/linux/zigux.h": 1,
    "PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only": 1,
    "PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md": 1,
    "PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json": 1,
    "PHASE3_ZIGUX_H_VALIDATOR_PATH=scripts/zigux/validate-phase3-linux-zigux-header-governance.py": 1,
    "PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed helper views, summaries, and narrow boundary adapters only": 1,
}
REQUIRED_GROWTH_RULE = (
    "PHASE3_ZIGUX_H_GROWTH_RULE=new top-level helper families may land in include/linux/zigux.h, "
    "and already-landed top-level review surfaces may be rehomed there, only when the same bounded "
    "change also lands packet-local proof and updates this note."
)
REQUIRED_PACKET_MARKERS = {
    "zigux/bindings/abi.zig": 2,
    "zigux/bindings/dev_t.zig": 2,
    "zigux/bindings/notifier_abi.zig": 2,
    "zigux/uapi/version.zig": 1,
}
REQUIRED_STARTER_PACKET_MARKERS = {
    "live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`": 1,
}
HEADER_INCLUDE_MARKERS = (
    '#include "../zigux/abi.h"',
    '#include "../zigux/dev_t.h"',
)
HEADER_HELPERS = (
    "zigux_export_status_ok",
    "zigux_boundary_header_make",
    "zigux_boundary_header_make_compatible",
)
REQUIRED_BOUNDARY_MARKERS = {
    "keep canonical and future-compatible constructors as thin named relays over the canonical header and starter UAPI ownership": 1,
    "aggregate `include/zigux/dev_t.h` rather than restating `ZIGUX_DEV_MINOR_BITS` or `ZIGUX_DEV_MINOR_MASK` locally": 1,
}


def _git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def _note_helper_count(note_text: str, helper: str) -> int:
    return len(re.findall(rf"`{re.escape(helper)}\(\)`", note_text))


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
            "blob marker drift: "
            f"{expected_blob_marker} (expected 1, found {actual_blob_count})"
        )

    growth_rule_count = note_text.count(REQUIRED_GROWTH_RULE)
    if growth_rule_count != 1:
        issues.append(
            "growth-rule marker count drift: "
            f"(expected 1, found {growth_rule_count})"
        )

    for marker, expected_count in REQUIRED_PACKET_MARKERS.items():
        actual_count = note_text.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"packet marker count drift: {marker} (expected {expected_count}, found {actual_count})"
            )

    for marker, expected_count in REQUIRED_STARTER_PACKET_MARKERS.items():
        actual_count = note_text.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"starter packet marker count drift: {marker} (expected {expected_count}, found {actual_count})"
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
        actual_count = _note_helper_count(note_text, helper)
        if actual_count < 1:
            issues.append(f"governance note helper marker missing: {helper}()")

    for marker, expected_count in REQUIRED_BOUNDARY_MARKERS.items():
        actual_count = note_text.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"boundary marker count drift: {marker} (expected {expected_count}, found {actual_count})"
            )

    return issues


def run_self_test() -> int:
    sample_header = (
        '#ifndef _LINUX_ZIGUX_H\n'
        '#define _LINUX_ZIGUX_H\n\n'
        '#include "../zigux/abi.h"\n'
        '#include "../zigux/dev_t.h"\n\n'
        'static inline int zigux_export_status_ok(struct zigux_export_status status)\n{\n    return status.code;\n}\n\n'
        'static inline struct zigux_boundary_header zigux_boundary_header_make(uint16_t flags)\n{\n    return zigux_default_header(flags);\n}\n\n'
        'static inline struct zigux_boundary_header zigux_boundary_header_make_compatible(uint32_t size, uint16_t flags)\n{\n    struct zigux_boundary_header header = zigux_default_header(flags);\n    header.size = size;\n    return header;\n}\n\n'
        '#endif\n'
    )
    sample_blob = _git_blob_sha(sample_header)
    sample_note = f"""## Scope
PHASE3_ZIGUX_H_PATH=include/linux/zigux.h
PHASE3_ZIGUX_H_BLOB_SHA={sample_blob}
PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only
PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md
PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json
PHASE3_ZIGUX_H_VALIDATOR_PATH=scripts/zigux/validate-phase3-linux-zigux-header-governance.py
PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed helper views, summaries, and narrow boundary adapters only

PHASE3_ZIGUX_H_GROWTH_RULE=new top-level helper families may land in include/linux/zigux.h, and already-landed top-level review surfaces may be rehomed there, only when the same bounded change also lands packet-local proof and updates this note.

zigux/bindings/abi.zig
zigux/bindings/dev_t.zig
zigux/bindings/notifier_abi.zig
zigux/uapi/version.zig
zigux/bindings/abi.zig
zigux/bindings/dev_t.zig
zigux/bindings/notifier_abi.zig
live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`

`zigux_export_status_ok()`
`zigux_boundary_header_make()`
`zigux_boundary_header_make_compatible()`
keep canonical and future-compatible constructors as thin named relays over the canonical header and starter UAPI ownership
aggregate `include/zigux/dev_t.h` rather than restating `ZIGUX_DEV_MINOR_BITS` or `ZIGUX_DEV_MINOR_MASK` locally
"""
    issues = validate_text(sample_note, sample_header)
    if issues:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("\n".join(issues))
        return 1

    broken = validate_text(
        sample_note.replace(
            "PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed helper views, summaries, and narrow boundary adapters only\n",
            "",
            1,
        ),
        sample_header,
    )
    expected = (
        "scope marker count drift: "
        "PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed helper views, summaries, and narrow boundary adapters only "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected role-marker drift was not reported")
        return 1

    broken = validate_text(sample_note.replace("zigux/uapi/version.zig\n", "", 1), sample_header)
    expected = "packet marker count drift: zigux/uapi/version.zig (expected 1, found 0)"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected starter-uapi marker drift was not reported")
        return 1

    broken = validate_text(
        sample_note.replace(
            "live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`\n",
            "",
            1,
        ),
        sample_header,
    )
    expected = (
        "starter packet marker count drift: "
        "live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig` "
        "(expected 1, found 0)"
    )
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected starter-pair marker drift was not reported")
        return 1

    broken = validate_text(sample_note.replace("zigux/bindings/notifier_abi.zig\n", "", 1), sample_header)
    expected = "packet marker count drift: zigux/bindings/notifier_abi.zig (expected 2, found 1)"
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected bindings marker drift was not reported")
        return 1

    broken = validate_text(sample_note.replace('`zigux_boundary_header_make_compatible()`', '', 1), sample_header)
    expected = 'governance note helper marker missing: zigux_boundary_header_make_compatible()'
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected governance-note helper drift was not reported")
        return 1

    broken = validate_text(sample_note.replace(sample_blob, 'deadbeef', 1), sample_header)
    expected = f'blob marker drift: PHASE3_ZIGUX_H_BLOB_SHA={sample_blob} (expected 1, found 0)'
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected blob drift was not reported")
        return 1

    broken = validate_text(sample_note, sample_header.replace('#include "../zigux/dev_t.h"\n', '', 1))
    expected = 'header include count drift: #include "../zigux/dev_t.h" (expected 1, found 0)'
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected include drift was not reported")
        return 1

    broken = validate_text(sample_note, sample_header.replace('zigux_export_status_ok', 'zigux_export_status_nope', 1))
    expected = 'header helper missing: zigux_export_status_ok'
    if expected not in broken:
        print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=fail")
        print("expected header helper drift was not reported")
        return 1

    print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    note_text = load_text(args.repo_root / NOTE_PATH, 'governance note')
    header_text = load_text(args.repo_root / HEADER_PATH, 'Linux-facing header')
    issues = validate_text(note_text, header_text)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1

    print(f'validated {args.repo_root / NOTE_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
