#!/usr/bin/env python3
"""Guard the Phase 1 string review packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

CLOSURE_ROUTE_MARKERS = [
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase1-string-review-packet.py`",
]

LANE_NOTE_MARKERS = [
    "`scripts/zigux/check-phase1-string-review-packet.py`",
]

MAKEFILE_ROUTE_MARKERS = {
    "self_test_route": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "live_route": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py",
}

LIST_FIELDS = (
    "memparse_review_anchors",
    "strscpy_review_anchors",
    "prefix_suffix_review_anchors",
    "sysfs_review_anchors",
    "lookup_review_anchors",
    "counted_search_review_anchors",
    "parity_fixture_keys",
)

SCALAR_FIELDS = (
    "basename_review_anchor",
    "trim_nul_review_anchor",
    "memchr_moving_dirty_anchor",
    "phase1_helper_replay_anchor",
)

EXPECTED_SELF_TEST_CASE_COUNT = 52


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in (CLOSURE_REL, LANE_NOTE_REL, MAKEFILE_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            missing.append(f"missing_file:{relative_path.as_posix()}")
    return missing


def require_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")
    return missing


def require_symbol_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(marker)}(?![A-Za-z0-9_])")
        if not pattern.search(text):
            missing.append(f"{label}:{marker}")
    return missing


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == line)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_manifest_string_list(value: Any, label: str) -> tuple[list[str], list[str]]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        return [], [f"string_manifest:{label}"]
    return value, []


def require_manifest_string(value: Any, label: str) -> tuple[str, list[str]]:
    if not isinstance(value, str) or not value:
        return "", [f"string_manifest:{label}"]
    return value, []


def collect_string_review_packet_failures(root: Path) -> list[str]:
    missing = collect_missing_files(root)
    if missing:
        return missing

    closure_text = load_text(root, CLOSURE_REL)
    lane_note_text = load_text(root, LANE_NOTE_REL)
    makefile_text = load_text(root, MAKEFILE_REL)
    manifest = load_json(root, MANIFEST_REL)

    if not isinstance(manifest, dict):
        return ["string_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["string_manifest:review_anchors"]

    string_anchors = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_anchors, dict):
        return ["string_manifest:tools/lib/string.zig"]

    missing.extend(require_markers(closure_text, "phase1_closure:shared_review_packet", CLOSURE_ROUTE_MARKERS))
    missing.extend(require_markers(lane_note_text, "lane_note:string_review_packet", LANE_NOTE_MARKERS))

    for label, marker in MAKEFILE_ROUTE_MARKERS.items():
        missing.extend(require_exact_line(makefile_text, f"makefile:{label}", marker))

    for field in LIST_FIELDS:
        markers, field_missing = require_manifest_string_list(string_anchors.get(field), field)
        missing.extend(field_missing)
        if not field_missing:
            if field == "parity_fixture_keys":
                missing.extend(require_symbol_markers(closure_text, f"phase1_closure:{field}", markers))
            else:
                missing.extend(require_markers(closure_text, f"phase1_closure:{field}", markers))

    for field in SCALAR_FIELDS:
        marker, field_missing = require_manifest_string(string_anchors.get(field), field)
        missing.extend(field_missing)
        if not field_missing and marker not in closure_text:
            missing.append(f"phase1_closure:{field}:{marker}")

    next_safe_step_note, field_missing = require_manifest_string(
        string_anchors.get("next_safe_step_note"),
        "next_safe_step_note",
    )
    missing.extend(field_missing)
    if not field_missing:
        missing.extend(
            require_exact_occurrence(
                lane_note_text,
                "lane_note:string_next_safe_step_note",
                next_safe_step_note,
            )
        )

    return missing


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_string_anchors() -> dict[str, Any]:
    return {
        "memparse_review_anchors": [
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "strscpy_review_anchors": [
            'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
            'test "strscpyPad zero-pads the tail after a short source"',
            'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
            'test "strscpyPad preserves strscpy truncation semantics"',
            'test "strscpy_pad mirrors strscpyPad padding semantics"',
        ],
        "prefix_suffix_review_anchors": [
            'test "strHasPrefix returns the matched prefix length with C-string semantics"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "sysfs_review_anchors": [
            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
        ],
        "lookup_review_anchors": [
            'test "matchString finds C-string matches and preserves first-match order"',
            'test "match_string mirrors matchString for empty and matched lists"',
        ],
        "counted_search_review_anchors": [
            'test "strnchr honors count and C-string boundaries"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        ],
        "parity_fixture_keys": [
            "strtobool_y",
            "strtobool_on",
            "strtobool_zero",
            "strtobool_off",
            "strtobool_invalid",
            "strlcpy_len",
            "strlcpy_buffer",
            "skip_spaces",
            "trim_spaces",
            "remove_spaces",
            "replace_char",
            "replace_char_end",
            "replace_char_cstr_end",
            "replace_char_cstr_bytes",
            "memchr_inv_index",
            "memchr_inv_none",
        ],
        "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
        "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
        "next_safe_step_note": "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and closure note unless current master later adds dedicated shared sysfs fixture keys; until then, newline-aware equality and lookup order remain owned by the direct string tests.",
    }


def sample_manifest() -> dict[str, Any]:
    return {
        "review_anchors": {
            "tools/lib/string.zig": sample_string_anchors(),
        }
    }


def sample_closure_text() -> str:
    anchors = sample_string_anchors()
    lines = [
        "# Phase 1 Closure",
        "",
        "## Shared Review Packet",
        *[f"- {marker}" for marker in CLOSURE_ROUTE_MARKERS],
        "",
        "## String Review Rule",
    ]

    for field in LIST_FIELDS:
        lines.append("")
        lines.append(f"### {field}")
        lines.extend(f"- {marker}" for marker in anchors[field])

    lines.append("")
    lines.append("### scalar_anchors")
    lines.extend(f"- {anchors[field]}" for field in SCALAR_FIELDS)
    return "\n".join(lines) + "\n"


def sample_lane_note_text() -> str:
    next_safe_step_note = sample_string_anchors()["next_safe_step_note"]
    return (
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        "The still-open string sysfs follow-through, if it reopens, should stay on one string-only "
        "shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, "
        "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/check-phase1-string-review-packet.py`, "
        "and `scripts/zigux/validate-phase1-closure.py`.\n\n"
        f"- {next_safe_step_note}\n"
    )


def sample_makefile_text() -> str:
    return (
        "phase1-validate:\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(root, CLOSURE_REL, sample_closure_text())
    write_file(root, LANE_NOTE_REL, sample_lane_note_text())
    write_file(root, MAKEFILE_REL, sample_makefile_text())
    write_file(root, MANIFEST_REL, json.dumps(sample_manifest(), indent=2) + "\n")


def build_self_test_cases() -> list[tuple[str, str | None, str | None, str]]:
    anchors = sample_string_anchors()
    cases: list[tuple[str, str | None, str | None, str]] = [("success", None, None, "none")]

    for index, marker in enumerate(CLOSURE_ROUTE_MARKERS, start=1):
        cases.append((f"missing_closure_route_{index}", CLOSURE_REL.as_posix(), f"- {marker}\n", "remove"))

    for label, marker in MAKEFILE_ROUTE_MARKERS.items():
        cases.append((f"missing_makefile_{label}", MAKEFILE_REL.as_posix(), marker + "\n", "remove"))

    for index, marker in enumerate(LANE_NOTE_MARKERS, start=1):
        cases.append((f"missing_lane_note_marker_{index}", LANE_NOTE_REL.as_posix(), marker, "remove"))

    for field in LIST_FIELDS:
        for index, marker in enumerate(anchors[field], start=1):
            cases.append((f"missing_{field}_{index}", CLOSURE_REL.as_posix(), f"- {marker}\n", "remove"))

    for field in SCALAR_FIELDS:
        cases.append((f"missing_{field}", CLOSURE_REL.as_posix(), f"- {anchors[field]}\n", "remove"))

    next_safe_step_note = anchors["next_safe_step_note"]
    cases.append(("missing_next_safe_step_note", LANE_NOTE_REL.as_posix(), next_safe_step_note, "remove"))
    cases.append(("duplicate_next_safe_step_note", LANE_NOTE_REL.as_posix(), next_safe_step_note, "duplicate"))

    return cases


def run_self_test() -> int:
    cases = build_self_test_cases()
    if len(cases) != EXPECTED_SELF_TEST_CASE_COUNT:
        print(
            "self-test:case-count-mismatch:"
            f"expected={EXPECTED_SELF_TEST_CASE_COUNT}:actual={len(cases)}"
        )
        return 1

    for name, relative_path, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-review-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if relative_path and needle:
                target = root / relative_path
                text = target.read_text(encoding="utf-8")
                if operation == "remove":
                    target.write_text(text.replace(needle, "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    target.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")

            missing = collect_string_review_packet_failures(root)
            if name == "success":
                if missing:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in missing:
                        print(item)
                    return 1
                continue

            if not missing:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_string_review_packet_failures(repo_root(args.root))
    if missing:
        for item in missing:
            print(item)
        return 1

    print("phase1-string-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
