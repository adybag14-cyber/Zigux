#!/usr/bin/env python3
"""Guard the find_bit Phase 1 review-anchor addendum."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

HELPER_REL = Path("tools/lib/find_bit.zig")
ADDENDUM_REL = Path("zigux/tests/fixtures/phase1_find_bit_review_anchors.json")

EXPECTED_REQUIRED_HELPER_TESTS = [
    'test "Linux-style next-or aliases clamp tail words and past-end starts"',
    'test "Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes"',
]

EXPECTED_REQUIRED_ENTRYPOINTS = [
    "find_next_or_bit",
    "_find_next_or_bit",
    "find_first_clump8",
    "_find_first_clump8",
    "find_next_clump8",
    "_find_next_clump8",
]

EXPECTED_VALUES = {
    "phase": "Phase 1",
    "helper": HELPER_REL.as_posix(),
    "lane": "P1-L10",
    "status": "active_review_anchor_addendum",
    "required_helper_tests": EXPECTED_REQUIRED_HELPER_TESTS,
    "required_entrypoints": EXPECTED_REQUIRED_ENTRYPOINTS,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (HELPER_REL, ADDENDUM_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    try:
        addendum = load_json(root, ADDENDUM_REL)
    except json.JSONDecodeError as exc:
        return [f"{ADDENDUM_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    if not isinstance(addendum, dict):
        return [f"{ADDENDUM_REL.as_posix()}:expected=dict:actual={type(addendum).__name__}"]

    for key, expected in EXPECTED_VALUES.items():
        failures.extend(require_exact_value(f"{ADDENDUM_REL.as_posix()}:{key}", addendum.get(key), expected))

    helper = load_text(root, HELPER_REL)
    for test_name in EXPECTED_REQUIRED_HELPER_TESTS:
        failures.extend(require_once(helper, f"{HELPER_REL.as_posix()}:{test_name}", test_name + " {"))
    for entrypoint in EXPECTED_REQUIRED_ENTRYPOINTS:
        failures.extend(require_once(helper, f"{HELPER_REL.as_posix()}:{entrypoint}", "pub fn " + entrypoint))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        helper = "\n".join(
            [
                "pub fn find_next_or_bit() void {}",
                "pub fn _find_next_or_bit() void {}",
                "pub fn find_first_clump8() void {}",
                "pub fn _find_first_clump8() void {}",
                "pub fn find_next_clump8() void {}",
                "pub fn _find_next_clump8() void {}",
                'test "Linux-style next-or aliases clamp tail words and past-end starts" {',
                "}",
                'test "Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes" {',
                "}",
                "",
            ]
        )
        addendum = {
            "phase": "Phase 1",
            "helper": HELPER_REL.as_posix(),
            "lane": "P1-L10",
            "status": "active_review_anchor_addendum",
            "required_helper_tests": EXPECTED_REQUIRED_HELPER_TESTS,
            "required_entrypoints": EXPECTED_REQUIRED_ENTRYPOINTS,
        }
        write_file(root, HELPER_REL, helper)
        write_file(root, ADDENDUM_REL, json.dumps(addendum, indent=2) + "\n")
        failures = collect_failures(root)
        if failures:
            return ["self_test_valid_fixture_failed", *failures]

        addendum["required_entrypoints"] = EXPECTED_REQUIRED_ENTRYPOINTS[:-1]
        write_file(root, ADDENDUM_REL, json.dumps(addendum, indent=2) + "\n")
        failures = collect_failures(root)
        if not any("required_entrypoints" in failure for failure in failures):
            return ["self_test_invalid_fixture_did_not_fail"]

    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None, help="Repository root to validate. Defaults to the checkout containing this script.")
    parser.add_argument("--self-test", action="store_true", help="Run the checker self-test fixtures.")
    args = parser.parse_args()

    failures = run_self_test() if args.self_test else collect_failures(repo_root(args.root))
    if failures:
        print("phase1-find-bit-review-anchors: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("phase1-find-bit-review-anchors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
