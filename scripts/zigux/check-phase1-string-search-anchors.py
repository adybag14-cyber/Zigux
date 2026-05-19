#!/usr/bin/env python3
"""Guard the newer Phase 1 string search-and-length anchors against helper drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
STRING_HELPER_REL = Path("tools/lib/string.zig")

EXPECTED_SOURCE_SYMBOLS = [
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
    "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
]

EXPECTED_TEST_ANCHORS = [
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    helper_path = root / STRING_HELPER_REL
    if not helper_path.exists():
        return [f"missing_file:{STRING_HELPER_REL.as_posix()}"]

    helper_text = load_text(root, STRING_HELPER_REL)
    failures: list[str] = []

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol))

    for anchor in EXPECTED_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(EXPECTED_SOURCE_SYMBOLS + EXPECTED_TEST_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-string-search-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutation_specs = []
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.append(("missing_helper_file", None, "missing_file"))

    for name, target, kind in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-search-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            path = root / STRING_HELPER_REL
            if kind == "missing_file":
                path.unlink()
            else:
                assert target is not None
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_STRING_SEARCH_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_STRING_SEARCH_ANCHOR_SELF_TEST_CASE_COUNT={case_count}")
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

    print("phase1-string-search-anchors:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
