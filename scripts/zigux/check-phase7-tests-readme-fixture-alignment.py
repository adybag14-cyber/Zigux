#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TESTS_README = Path("zigux/tests/README.md")
ARGV_SPLIT_MANIFEST = Path("zigux/tests/phase7_argv_split_manifest.json")
RBTREE_MANIFEST = Path("zigux/tests/phase7_rbtree_manifest.json")

REQUIRED_TESTS_README_MARKERS = (
    "## Phase 7",
    "`zigux/tests/phase7_build.zig`",
    "`zigux/tests/phase7_string_helpers.zig`",
    "`zigux/tests/phase7_cmdline.zig`",
    "`zigux/tests/phase7_argv_split.zig`",
    "`zigux/tests/phase7_argv_split_survey.zig`",
    "`zigux/tests/phase7_argv_split_manifest.json`",
    "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
    "`zigux/tests/phase7_rbtree.zig`",
    "`zigux/tests/phase7_rbtree_survey.zig`",
    "`zigux/tests/phase7_rbtree_manifest.json`",
)

FORBIDDEN_TESTS_README_MARKERS = (
    "`zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`",
    "`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`",
    "`zigux/tests/fixtures/phase7_rbtree.json`",
    "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
)

REQUIRED_ARGV_SPLIT_SURFACES = (
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
)

REQUIRED_RBTREE_MISSING_PATHS = (
    "lib/rbtree.zig",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
)


def read_text(root: Path, rel_path: Path) -> str:
    path = root / rel_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(root: Path, rel_path: Path) -> object:
    path = root / rel_path
    try:
        return json.loads(read_text(root, rel_path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        found: set[str] = set()
        for item in value:
            found.update(collect_strings(item))
        return found
    if isinstance(value, dict):
        found: set[str] = set()
        for item in value.values():
            found.update(collect_strings(item))
        return found
    return set()


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    tests_readme_text = read_text(root, TESTS_README)
    argv_split_manifest = read_json(root, ARGV_SPLIT_MANIFEST)
    rbtree_manifest = read_json(root, RBTREE_MANIFEST)

    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            issues.append(("MISSING_TESTS_README_MARKERS", marker))

    for marker in FORBIDDEN_TESTS_README_MARKERS:
        if marker in tests_readme_text:
            issues.append(("FORBIDDEN_TESTS_README_MARKERS", marker))

    argv_split_strings = collect_strings(argv_split_manifest)
    for surface in REQUIRED_ARGV_SPLIT_SURFACES:
        if surface not in argv_split_strings:
            issues.append(("MISSING_ARGV_SPLIT_MANIFEST_SURFACES", surface))

    argv_split_missing = argv_split_manifest.get("missing_paths")
    if argv_split_missing != []:
        issues.append(("NONEMPTY_ARGV_SPLIT_MISSING_PATHS", json.dumps(argv_split_missing, sort_keys=True)))

    rbtree_missing = rbtree_manifest.get("missing_paths")
    if rbtree_missing != list(REQUIRED_RBTREE_MISSING_PATHS):
        issues.append(("RBTREE_MISSING_PATHS_DRIFT", json.dumps(rbtree_missing, sort_keys=True)))

    rbtree_strings = collect_strings(rbtree_manifest)
    for surface in ("zigux/tests/phase7_rbtree.zig", "zigux/tests/phase7_rbtree_survey.zig", "zigux/tests/phase7_rbtree_manifest.json"):
        if surface not in rbtree_strings:
            issues.append(("MISSING_RBTREE_MANIFEST_SURFACES", surface))

    for missing_path in REQUIRED_RBTREE_MISSING_PATHS[1:]:
        marker = f"`{missing_path}`"
        if marker in tests_readme_text:
            issues.append(("README_LISTS_RBTREE_MANIFEST_GAP", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE7_TESTS_README_FIXTURE_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(root: Path, rel_path: Path, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        TESTS_README,
        "\n".join(
            [
                "# zigux/tests",
                "",
                "## Phase 7",
                "- `zigux/tests/phase7_build.zig`",
                "- `zigux/tests/phase7_string_helpers.zig`",
                "- `zigux/tests/phase7_cmdline.zig`",
                "- `zigux/tests/phase7_argv_split.zig`",
                "- `zigux/tests/phase7_argv_split_survey.zig`",
                "- `zigux/tests/phase7_argv_split_manifest.json`",
                "- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
                "- `zigux/tests/phase7_rbtree.zig`",
                "- `zigux/tests/phase7_rbtree_survey.zig`",
                "- `zigux/tests/phase7_rbtree_manifest.json`",
            ]
        )
        + "\n",
    )
    write_text(
        root,
        ARGV_SPLIT_MANIFEST,
        json.dumps(
            {
                "lane_key": "P7-L09",
                "missing_paths": [],
                "review_surfaces": list(REQUIRED_ARGV_SPLIT_SURFACES),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_text(
        root,
        RBTREE_MANIFEST,
        json.dumps(
            {
                "lane_key": "P7-L13",
                "visible_paths": [
                    "zigux/tests/phase7_rbtree.zig",
                    "zigux/tests/phase7_rbtree_survey.zig",
                    "zigux/tests/phase7_rbtree_manifest.json",
                ],
                "missing_paths": list(REQUIRED_RBTREE_MISSING_PATHS),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
        + len(REQUIRED_ARGV_SPLIT_SURFACES)
        + 1
        + 1
        + 3
        + 2
        + 3
    )

    with tempfile.TemporaryDirectory(prefix="zigux_p7_tests_readme_fixture_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = root / TESTS_README
            path.write_text(remove_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_TESTS_README_MARKERS", marker)) in issues
            checks_run += 1

        for marker in FORBIDDEN_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = root / TESTS_README
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert (("FORBIDDEN_TESTS_README_MARKERS", marker)) in issues
            checks_run += 1

        for surface in REQUIRED_ARGV_SPLIT_SURFACES:
            build_self_test_root(root)
            path = root / ARGV_SPLIT_MANIFEST
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["review_surfaces"].remove(surface)
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_ARGV_SPLIT_MANIFEST_SURFACES", surface)) in issues
            checks_run += 1

        build_self_test_root(root)
        path = root / ARGV_SPLIT_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["missing_paths"] = ["legacy-gap"]
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (("NONEMPTY_ARGV_SPLIT_MISSING_PATHS", '["legacy-gap"]')) in issues
        checks_run += 1

        build_self_test_root(root)
        path = root / RBTREE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["missing_paths"] = ["zigux/tests/fixtures/phase7_rbtree.json"]
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (("RBTREE_MISSING_PATHS_DRIFT", '["zigux/tests/fixtures/phase7_rbtree.json"]')) in issues
        checks_run += 1

        for surface in (
            "zigux/tests/phase7_rbtree.zig",
            "zigux/tests/phase7_rbtree_survey.zig",
            "zigux/tests/phase7_rbtree_manifest.json",
        ):
            build_self_test_root(root)
            path = root / RBTREE_MANIFEST
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["visible_paths"].remove(surface)
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_RBTREE_MANIFEST_SURFACES", surface)) in issues
            checks_run += 1

        for marker in (
            "`zigux/tests/fixtures/phase7_rbtree.json`",
            "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        ):
            build_self_test_root(root)
            path = root / TESTS_README
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert (("README_LISTS_RBTREE_MANIFEST_GAP", marker)) in issues
            checks_run += 1

        for rel_path in (TESTS_README, ARGV_SPLIT_MANIFEST, RBTREE_MANIFEST):
            build_self_test_root(root)
            (root / rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE7_TESTS_README_FIXTURE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE7_TESTS_README_FIXTURE_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 7 tests-root reminder aligned with the current argv_split and rbtree fixture/manifest packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE7_TESTS_README_FIXTURE_ALIGNMENT=pass")
    print(f"PHASE7_TESTS_README_REQUIRED_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}")
    print(f"PHASE7_TESTS_README_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_TESTS_README_MARKERS)}")
    print(f"PHASE7_TESTS_README_ARGV_SPLIT_SURFACE_COUNT={len(REQUIRED_ARGV_SPLIT_SURFACES)}")
    print(f"PHASE7_TESTS_README_RBTREE_MISSING_PATH_COUNT={len(REQUIRED_RBTREE_MISSING_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
