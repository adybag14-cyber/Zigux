#!/usr/bin/env python3
"""Guard the Phase 1 string copy-fill and substring packet against helper and manifest drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_SOURCE_SYMBOLS = [
    "pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn strtomem(dest: []u8, src: []const u8) void {",
    "pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {",
    "pub fn memtostr(dest: []u8, src: []const u8) void {",
    "pub fn memtostrPad(dest: []u8, src: []const u8) void {",
    "pub fn memtostr_pad(dest: []u8, src: []const u8) void {",
    "pub fn strstr(buf: []const u8, needle: []const u8) ?usize {",
    "pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {",
]

EXPECTED_HELPER_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
    'test "strstr mirrors full-length C-string substring searches"',
    'test "strnstr honors count and C-string boundaries"',
]

EXPECTED_PACKET = {
    "copy_fill_review_anchors": [
        'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
        'test "strtomem copies a C-string prefix without adding a terminator or padding"',
        'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    ],
    "copy_fill_review_summary": (
        "helper-local raw-copy and pad anchors stay explicit through the direct string tests because "
        "the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), strtomem(), or "
        "strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, and caller-selected pad "
        "behavior remain review-visible at the helper surface"
    ),
    "substring_search_review_anchors": [
        'test "strstr mirrors full-length C-string substring searches"',
        'test "strnstr honors count and C-string boundaries"',
    ],
    "substring_search_review_summary": (
        "helper-local substring-search anchors stay explicit through the direct string tests because "
        "the shared Phase 1 replay still does not carry dedicated strstr() or strnstr() fixture "
        "keys, so full-length and count-clamped substring boundaries remain review-visible at the "
        "helper surface"
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


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
    for relative_path in (STRING_HELPER_REL, STRING_MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    try:
        manifest = load_json_with_duplicate_tracking(load_text(root, STRING_MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_paths]

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol))
    for anchor in EXPECTED_HELPER_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor))
    for key, expected in EXPECTED_PACKET.items():
        failures.extend(
            require_exact_value(
                f"string_manifest:review_anchors.tools/lib/string.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/string.zig", key)),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return json.dumps({"review_anchors": {"tools/lib/string.zig": EXPECTED_PACKET}}, indent=2) + "\n"


def sample_helper() -> str:
    return "\n".join(EXPECTED_SOURCE_SYMBOLS + EXPECTED_HELPER_ANCHORS) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, sample_helper())
    write_file(root, STRING_MANIFEST_REL, sample_manifest())


def mutate_json_path(root: Path, path: tuple[str, ...]) -> None:
    json_path = root / STRING_MANIFEST_REL
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
    with tempfile.TemporaryDirectory(prefix="phase1-string-copy-fill-substring-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

    mutation_specs: list[tuple[str, str, object]] = []
    mutation_specs.extend((f"source_remove_{idx}", "source_remove", symbol) for idx, symbol in enumerate(EXPECTED_SOURCE_SYMBOLS))
    mutation_specs.extend((f"anchor_remove_{idx}", "anchor_remove", anchor) for idx, anchor in enumerate(EXPECTED_HELPER_ANCHORS))
    mutation_specs.extend((f"manifest_{key}", "manifest", ("review_anchors", "tools/lib/string.zig", key)) for key in EXPECTED_PACKET)
    mutation_specs.append(("manifest_duplicate_copy_fill", "duplicate_json", (
        '      "copy_fill_review_anchors": [',
        '      "copy_fill_review_anchors": [],',
    )))
    mutation_specs.append(("manifest_missing_file", "missing_file", STRING_MANIFEST_REL))
    mutation_specs.append(("helper_missing_file", "missing_file", STRING_HELPER_REL))
    mutation_specs.append(("manifest_invalid_json", "invalid_json", STRING_MANIFEST_REL))

    for name, kind, payload in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-copy-fill-substring-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if kind == "source_remove":
                path = root / STRING_HELPER_REL
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(str(payload) + "\n", "", 1), encoding="utf-8")
            elif kind == "anchor_remove":
                path = root / STRING_HELPER_REL
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(str(payload) + "\n", "", 1), encoding="utf-8")
            elif kind == "manifest":
                mutate_json_path(root, payload)
            elif kind == "duplicate_json":
                insert_duplicate_json_line(root, payload[0], payload[1])
            elif kind == "missing_file":
                (root / payload).unlink()
            elif kind == "invalid_json":
                (root / payload).write_text("{\n", encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_STRING_COPY_FILL_SUBSTRING_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_COPY_FILL_SUBSTRING_PACKET_SELF_TEST_CASE_COUNT={case_count}")
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
        print("PHASE1_STRING_COPY_FILL_SUBSTRING_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_STRING_COPY_FILL_SUBSTRING_PACKET=pass")
    print(f"PHASE1_STRING_COPY_FILL_SUBSTRING_PACKET_SOURCE_SYMBOL_COUNT={len(EXPECTED_SOURCE_SYMBOLS)}")
    print(f"PHASE1_STRING_COPY_FILL_SUBSTRING_PACKET_HELPER_ANCHOR_COUNT={len(EXPECTED_HELPER_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
