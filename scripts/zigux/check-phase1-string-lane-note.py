#!/usr/bin/env python3
"""Guard the narrow Phase 1 string lane-note review rules against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

EXPECTED_HELPER_LINES = {
    "sysfs_streq": 'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    "sysfs_match": 'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    "strspn": 'test "strspn counts the accepted prefix with C-string semantics"',
    "strnchrnul": 'test "strnchrNul returns the first match, NUL, or count boundary"',
}

EXPECTED_LANE_LINES = {
    "direct_owner": "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    "counted_search_boundary": "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.",
    "strspn_note": "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`.",
    "sysfs_review_rule": "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; the restored `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift.",
    "next_safe_step": "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
}

EXPECTED_MANIFEST_VALUES = {
    ("review_anchors", "tools/lib/string.zig", "sysfs_review_anchors"): [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    ("review_anchors", "tools/lib/string.zig", "counted_search_review_anchors"): [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strpbrk finds the first accepted byte with C-string semantics"',
        'test "strspn counts the accepted prefix with C-string semantics"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    ("review_anchors", "tools/lib/string.zig", "strnchrnul_review_anchor"): 'test "strnchrNul returns the first match, NUL, or count boundary"',
    ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"): "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == line.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (STRING_HELPER_REL, STRING_MANIFEST_REL, STRING_LANE_NOTE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    lane_text = load_text(root, STRING_LANE_NOTE_REL)
    manifest = load_json(root, STRING_MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    for label, line in EXPECTED_HELPER_LINES.items():
        failures.extend(require_exact_line(helper_text, f"helper:{label}", line))
    for label, line in EXPECTED_LANE_LINES.items():
        failures.extend(require_exact_line(lane_text, f"lane:{label}", line))
    for path, expected in EXPECTED_MANIFEST_VALUES.items():
        failures.extend(
            require_exact_value(
                f"manifest:{'.'.join(path)}",
                nested_value(manifest, path),
                expected,
            )
        )
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, "\n".join(EXPECTED_HELPER_LINES.values()) + "\n")
    write_file(root, STRING_LANE_NOTE_REL, "\n".join(EXPECTED_LANE_LINES.values()) + "\n")
    manifest = {"review_anchors": {"tools/lib/string.zig": {}}}
    for path, value in EXPECTED_MANIFEST_VALUES.items():
        current = manifest
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value
    write_file(root, STRING_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")


def mutate_remove_line(root: Path, relative_path: Path, line: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(line + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_line(root: Path, relative_path: Path, line: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(line + "\n", line + "\n" + line + "\n", 1), encoding="utf-8")


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / STRING_MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-string-lane-note-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

    for label, line in EXPECTED_HELPER_LINES.items():
        for operation in ("remove", "duplicate"):
            with tempfile.TemporaryDirectory(prefix=f"phase1-string-lane-note-helper-{label}-{operation}-") as tmpdir:
                root = Path(tmpdir)
                build_sample_repo(root)
                if operation == "remove":
                    mutate_remove_line(root, STRING_HELPER_REL, line)
                else:
                    mutate_duplicate_line(root, STRING_HELPER_REL, line)
                if not collect_failures(root):
                    print(f"self-test:helper:{label}:{operation}:expected_failure")
                    return 1
                case_count += 1

    for label, line in EXPECTED_LANE_LINES.items():
        for operation in ("remove", "duplicate"):
            with tempfile.TemporaryDirectory(prefix=f"phase1-string-lane-note-lane-{label}-{operation}-") as tmpdir:
                root = Path(tmpdir)
                build_sample_repo(root)
                if operation == "remove":
                    mutate_remove_line(root, STRING_LANE_NOTE_REL, line)
                else:
                    mutate_duplicate_line(root, STRING_LANE_NOTE_REL, line)
                if not collect_failures(root):
                    print(f"self-test:lane:{label}:{operation}:expected_failure")
                    return 1
                case_count += 1

    for path in EXPECTED_MANIFEST_VALUES:
        with tempfile.TemporaryDirectory(prefix="phase1-string-lane-note-manifest-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            mutate_manifest(root, path)
            if not collect_failures(root):
                print(f"self-test:manifest:{'.'.join(path)}:expected_failure")
                return 1
            case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-string-lane-note-missing-file-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        (root / STRING_LANE_NOTE_REL).unlink()
        if not collect_failures(root):
            print("self-test:missing_file:expected_failure")
            return 1
        case_count += 1

    print("PHASE1_STRING_LANE_NOTE_SELF_TEST=pass")
    print(f"PHASE1_STRING_LANE_NOTE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-string-lane-note:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
