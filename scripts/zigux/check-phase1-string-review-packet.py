#!/usr/bin/env python3
"""Guard the Phase 1 string review packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import json
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


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
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
        if marker not in makefile_text:
            missing.append(f"makefile:{label}")

    list_fields = (
        "memparse_review_anchors",
        "strscpy_review_anchors",
        "prefix_suffix_review_anchors",
        "sysfs_review_anchors",
        "lookup_review_anchors",
        "counted_search_review_anchors",
        "parity_fixture_keys",
    )
    for field in list_fields:
        markers, field_missing = require_manifest_string_list(string_anchors.get(field), field)
        missing.extend(field_missing)
        if not field_missing:
            missing.extend(require_markers(closure_text, f"phase1_closure:{field}", markers))

    scalar_fields = (
        "basename_review_anchor",
        "trim_nul_review_anchor",
        "memchr_moving_dirty_anchor",
        "phase1_helper_replay_anchor",
    )
    for field in scalar_fields:
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


def sample_manifest() -> dict[str, Any]:
    return {
        "review_anchors": {
            "tools/lib/string.zig": {
                "memparse_review_anchors": [
                    'test "memparse handles decimal hexadecimal octal and suffixes"',
                    'test "memparse keeps original rest when sign is not followed by digits"',
                ],
                "strscpy_review_anchors": [
                    'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
                    'test "strscpyPad zero-pads the tail after a short source"',
                ],
                "prefix_suffix_review_anchors": [
                    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
                    'test "strstarts mirrors the header-level prefix helper"',
                    'test "strEndsWith honors C-string boundaries"',
                ],
                "sysfs_review_anchors": [
                    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
                    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
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
                    "replace_char_cstr_bytes",
                    "memchr_inv_none",
                ],
                "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
                "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
                "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
                "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
                "next_safe_step_note": "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and closure note unless current master later adds dedicated shared sysfs fixture keys; until then, newline-aware equality and lookup order remain owned by the direct string tests.",
            }
        }
    }


def sample_closure_text() -> str:
    return """# Phase 1 Closure

## Shared Review Packet
- `scripts/zigux/check-phase1-string-review-packet.py`
- `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`
- `python3 scripts/zigux/check-phase1-string-review-packet.py`

## String Review Rule
That means `test "memparse handles decimal hexadecimal octal and suffixes"`, `test "memparse keeps original rest when sign is not followed by digits"`, `test "strscpy keeps NUL termination and reports truncation with -E2BIG"`, `test "strscpyPad zero-pads the tail after a short source"`, `test "strHasPrefix returns the matched prefix length with C-string semantics"`, `test "strstarts mirrors the header-level prefix helper"`, `test "strEndsWith honors C-string boundaries"`, `test "sysfsStreq treats trailing newline and NUL as equivalent"`, `test "sysfsMatchString finds newline-aware matches and preserves first-match order"`, `test "matchString finds C-string matches and preserves first-match order"`, `test "match_string mirrors matchString for empty and matched lists"`, `test "strnchr honors count and C-string boundaries"`, `test "strnchrNul returns the first match, NUL, or count boundary"`, `test "kbasename returns the final path component with C-string semantics"`, and `test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"` stay present and review-visible whenever the helper changes.
The shared replay must also keep `test "phase 1 string replaceChar stops at embedded NUL"` plus the `strtobool_y`, `replace_char_cstr_bytes`, and `memchr_inv_none` fixture fields explicit, while `test "memchrInv follows the earliest dirty byte as long buffers change"` remains a helper-local review anchor.
"""


def sample_lane_note_text() -> str:
    next_safe_step_note = sample_manifest()["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"]
    return f"""# Phase 1 Host-Helper Lane Sequencing

The still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/validate-phase1-closure.py`.

PHASE1_STRING_NEXT_SAFE_STEP={next_safe_step_note}
"""


def sample_makefile_text() -> str:
    return """phase1-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py
"""


def build_sample_repo(root: Path) -> None:
    write_file(root, CLOSURE_REL, sample_closure_text())
    write_file(root, LANE_NOTE_REL, sample_lane_note_text())
    write_file(root, MAKEFILE_REL, sample_makefile_text())
    write_file(root, MANIFEST_REL, json.dumps(sample_manifest(), indent=2) + "\n")


def run_self_test() -> int:
    next_safe_step_note = sample_manifest()["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"]
    cases: list[tuple[str, str | None, str | None, str]] = [
        ("success", None, None, "none"),
        (
            "missing_closure_route",
            CLOSURE_REL.as_posix(),
            "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`\n",
            "remove",
        ),
        (
            "missing_makefile_route",
            MAKEFILE_REL.as_posix(),
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-string-review-packet.py --self-test\n",
            "remove",
        ),
        (
            "missing_prefix_suffix_anchor",
            CLOSURE_REL.as_posix(),
            'test "strEndsWith honors C-string boundaries"',
            "remove",
        ),
        (
            "missing_basename_anchor",
            CLOSURE_REL.as_posix(),
            'test "kbasename returns the final path component with C-string semantics"',
            "remove",
        ),
        (
            "missing_sysfs_anchor",
            CLOSURE_REL.as_posix(),
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            "remove",
        ),
        (
            "missing_lane_note_marker",
            LANE_NOTE_REL.as_posix(),
            "`scripts/zigux/check-phase1-string-review-packet.py`",
            "remove",
        ),
        (
            "missing_next_safe_step_note",
            LANE_NOTE_REL.as_posix(),
            next_safe_step_note,
            "remove",
        ),
        (
            "duplicate_next_safe_step_note",
            LANE_NOTE_REL.as_posix(),
            next_safe_step_note,
            "duplicate",
        ),
    ]

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