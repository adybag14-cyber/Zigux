#!/usr/bin/env python3
"""Guard the Phase 1 string copy-fill review packet against helper, manifest, and lane-note drift."""

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


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn strtomem(dest: []u8, src: []const u8) void {",
    "pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {",
    "pub fn memtostr(dest: []u8, src: []const u8) void {",
    "pub fn memtostrPad(dest: []u8, src: []const u8) void {",
    "pub fn memtostr_pad(dest: []u8, src: []const u8) void {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
]

EXPECTED_MANIFEST_REVIEW_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
]

EXPECTED_MANIFEST_REVIEW_SUMMARY = (
    "helper-local raw-copy and pad anchors stay explicit through the direct string tests because "
    "the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), strtomem(), or "
    "strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, and caller-selected pad behavior "
    "remain review-visible at the helper surface"
)

EXPECTED_LANE_MARKER = (
    "- the same string-local packet also keeps helper-local byte-copy and pad coverage explicit "
    "through `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, `strtomem_pad()`, `memtostr()`, "
    "`memtostrPad()`, and `memtostr_pad()`, with direct tests for requested-prefix copying, first-"
    "NUL truncation, terminator insertion, and destination-tail padding, so future string-only "
    "rereads should keep those anchors in the same helper-local packet until dedicated shared "
    "fixture keys land."
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(root: Path, relative_path: Path) -> object:
    return load_json_with_duplicate_tracking(load_text(root, relative_path))


def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


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
    try:
        manifest = load_json(root, STRING_MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("manifest", exc)]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_manifest_paths]

    for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor))

    failures.extend(
        require_exact_occurrence(
            lane_text,
            "string_lane:copy_fill_packet",
            EXPECTED_LANE_MARKER,
        )
    )

    failures.extend(
        require_exact_value(
            "string_manifest:review_anchors.tools/lib/string.zig.copy_fill_review_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "copy_fill_review_anchors")),
            EXPECTED_MANIFEST_REVIEW_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "string_manifest:review_anchors.tools/lib/string.zig.copy_fill_review_summary",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "copy_fill_review_summary")),
            EXPECTED_MANIFEST_REVIEW_SUMMARY,
        )
    )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_helper_text() -> str:
    return "\n".join(EXPECTED_STRING_SOURCE_SYMBOLS + EXPECTED_HELPER_TEST_ANCHORS) + "\n"


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": {
                        "copy_fill_review_anchors": EXPECTED_MANIFEST_REVIEW_ANCHORS,
                        "copy_fill_review_summary": EXPECTED_MANIFEST_REVIEW_SUMMARY,
                    }
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_lane_note() -> str:
    return EXPECTED_LANE_MARKER + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, sample_helper_text())
    write_file(root, STRING_MANIFEST_REL, sample_manifest())
    write_file(root, STRING_LANE_NOTE_REL, sample_lane_note())


def mutate_json_path(root: Path, relative_path: Path, path: tuple[str, ...]) -> None:
    json_path = root / relative_path
    data = json.loads(json_path.read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    else:
        current[final_key] = f"{value} drift"
    json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_json_line(root: Path, needle: str, duplicate_line: str) -> None:
    json_path = root / STRING_MANIFEST_REL
    text = json_path.read_text(encoding="utf-8")
    json_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-string-copy-fill-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutation_specs: list[tuple[str, tuple[str, object], str]] = []
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_STRING_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"lane_marker_{kind}", ("lane_marker", EXPECTED_LANE_MARKER), kind)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"manifest_{key}",
            ("manifest", ("review_anchors", "tools/lib/string.zig", key)),
            "manifest",
        )
        for key in ("copy_fill_review_anchors", "copy_fill_review_summary")
    )
    mutation_specs.append(
        (
            "manifest_duplicate_copy_fill_summary",
            (
                "duplicate_json_text",
                '      "copy_fill_review_summary": "helper-local raw-copy and pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), strtomem(), or strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, and caller-selected pad behavior remain review-visible at the helper surface"',
                '      "copy_fill_review_summary": "drifted duplicate summary",',
            ),
            "duplicate_json_text",
        )
    )
    mutation_specs.append(("manifest_missing_file", ("missing_file", STRING_MANIFEST_REL), "missing_file"))
    mutation_specs.append(("lane_note_missing_file", ("missing_file", STRING_LANE_NOTE_REL), "missing_file"))
    mutation_specs.append(("manifest_invalid_json", ("invalid_json", STRING_MANIFEST_REL), "invalid_json"))

    for name, target, kind in mutation_specs:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-copy-fill-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if target[0] == "source_symbol":
                path = root / STRING_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(f"{marker}\n", "", 1)
                else:
                    text = text.replace(f"{marker}\n", f"{marker}\n{marker}\n", 1)
                path.write_text(text, encoding="utf-8")
            elif target[0] == "helper_anchor":
                path = root / STRING_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(f"{marker}\n", "", 1)
                else:
                    text = text.replace(f"{marker}\n", f"{marker}\n{marker}\n", 1)
                path.write_text(text, encoding="utf-8")
            elif target[0] == "lane_marker":
                path = root / STRING_LANE_NOTE_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(f"{marker}\n", "", 1)
                else:
                    text = text.replace(f"{marker}\n", f"{marker}\n{marker}\n", 1)
                path.write_text(text, encoding="utf-8")
            elif target[0] == "manifest":
                mutate_json_path(root, STRING_MANIFEST_REL, target[1])
            elif target[0] == "duplicate_json_text":
                insert_duplicate_json_line(root, target[1], target[2])
            elif target[0] == "invalid_json":
                (root / target[1]).write_text("{\n", encoding="utf-8")
            else:
                (root / target[1]).unlink()

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_STRING_COPY_FILL_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_COPY_FILL_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-copy-fill-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
