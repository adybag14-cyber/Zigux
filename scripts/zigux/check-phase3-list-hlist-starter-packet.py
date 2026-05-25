#!/usr/bin/env python3
"""Validate the bounded Phase 3 list/hlist starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase3-list-hlist-slice.md")
LIST_PATH = Path("zigux/helpers/list_view.zig")
HLIST_PATH = Path("zigux/helpers/hlist_view.zig")
TEST_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_list_hlist_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-list-hlist-starter-packet",
    "status": "helper_local_list_hlist_slice_present",
    "scope": "helper-local list_head and hlist sentinel, ordering, and backlink replay",
    "next_safe_step": (
        "if this slice needs parity expansion later, add the narrow C harness and "
        "expected fixture without widening beyond helper-local list_head and hlist semantics"
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
)

REQUIRED_REPO_REALITY_GAPS = (
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
)

REQUIRED_MARKERS = {
    DOC_PATH: (
        "This note records one bounded shared-helper starter packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.",
        "`zigux/tests/fixtures/phase3_list_hlist_manifest.json`",
        "`scripts/zigux/check-phase3-list-hlist-starter-packet.py`",
        "`python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test`",
        "`python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py`",
        "`zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`",
        "`zigux/tests/fixtures/phase3_list_hlist/expected.json`",
    ),
    LIST_PATH: (
        "pub const ListView = struct {",
        "pub fn isEmpty(self: ListView) bool {",
        "pub fn first(self: ListView) ?*const ListHead {",
        "pub fn last(self: ListView) ?*const ListHead {",
        "pub fn len(self: ListView) usize {",
        "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {",
    ),
    HLIST_PATH: (
        "pub const HListView = struct {",
        "pub fn isEmpty(self: HListView) bool {",
        "pub fn first(self: HListView) ?*const HListNode {",
        "pub fn len(self: HListView) usize {",
        "pub fn firstPprevMatchesHead(self: HListView) bool {",
        "pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak {",
        "pub fn tailNextIsNull(self: HListView) bool {",
    ),
    TEST_PATH: (
        'test "list starter packet keeps a sentinel-only list empty and reviewable" {',
        'test "list starter packet keeps circular ordering and broken backlinks explicit" {',
        'test "hlist starter packet keeps empty heads and bounded chains explicit" {',
        'test "hlist starter packet reports the first broken prev-link witness" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/list_view.zig"),',
        '.root_source_file = b.path("../helpers/hlist_view.zig"),',
        '.root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),',
        'root_module.addImport("list_view", list_view);',
        'root_module.addImport("hlist_view", hlist_view);',
        '"phase3-list-hlist-starter-packet"',
        '"Run the shared Phase 3 list/hlist starter packet"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-list-hlist-starter-packet"',
        '"status": "helper_local_list_hlist_slice_present"',
        '"zigux/helpers/list_view.zig"',
        '"zigux/helpers/hlist_view.zig"',
        '"scripts/zigux/check-phase3-list-hlist-starter-packet.py"',
        '"python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test"',
        '"zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig"',
        '"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c"',
        '"zigux/tests/fixtures/phase3_list_hlist/expected.json"',
    ),
}

SELF_TEST_CASES = (
    (DOC_PATH, "`zigux/tests/fixtures/phase3_list_hlist_manifest.json`"),
    (DOC_PATH, "`python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test`"),
    (LIST_PATH, "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {"),
    (HLIST_PATH, "pub fn tailNextIsNull(self: HListView) bool {"),
    (TEST_PATH, 'test "hlist starter packet reports the first broken prev-link witness" {'),
    (BUILD_PATH, '"phase3-list-hlist-starter-packet"'),
    (MANIFEST_PATH, '"scripts/zigux/check-phase3-list-hlist-starter-packet.py"'),
)

SELF_TEST_FIELD_CASES = (
    ("phase", "Phase 4"),
    ("lane", "helper-runtime"),
    ("slug", "phase3-list-hlist-mislabel"),
    ("status", "helper_local_list_hlist_slice_missing"),
    ("scope", "scope drift"),
    ("next_safe_step", "outdated next step"),
)

SELF_TEST_REPLAY_ROUTE_CASES = REQUIRED_REPLAY_ROUTES

SELF_TEST_REPO_REALITY_GAP_CASES = REQUIRED_REPO_REALITY_GAPS


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    try:
        manifest = json.loads(_read(repo_root / MANIFEST_PATH))
    except FileNotFoundError:
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in EXPECTED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                f"phase3_list_hlist_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_list_hlist_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_list_hlist_manifest.json packet_files",
            packet_files,
            issues,
        )
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(
                    f"phase3_list_hlist_manifest.json missing packet_files entry: {entry}"
                )

    if not isinstance(replay_routes, list):
        issues.append("phase3_list_hlist_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_list_hlist_manifest.json replay_routes",
            replay_routes,
            issues,
        )
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(
                    f"phase3_list_hlist_manifest.json missing replay route: {entry}"
                )

    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_list_hlist_manifest.json repo_reality_gaps is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_list_hlist_manifest.json repo_reality_gaps",
            repo_reality_gaps,
            issues,
        )
        for entry in REQUIRED_REPO_REALITY_GAPS:
            if entry not in repo_reality_gaps:
                issues.append(
                    f"phase3_list_hlist_manifest.json missing repo_reality_gaps entry: {entry}"
                )
        for entry in repo_reality_gaps:
            if (repo_root / entry).exists():
                issues.append(
                    "phase3_list_hlist_manifest.json repo_reality_gaps entry is present on disk: "
                    f"{entry}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")

    manifest = {
        **EXPECTED_MANIFEST_FIELDS,
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        "repo_reality_gaps": list(REQUIRED_REPO_REALITY_GAPS),
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def _remove_marker(repo_root: Path, relative_path: Path, marker: str) -> None:
    path = repo_root / relative_path
    text = _read(path)
    _write(path, text.replace(marker, "", 1))


def _load_manifest(repo_root: Path) -> dict[str, object]:
    return json.loads(_read(repo_root / MANIFEST_PATH))


def _write_manifest(repo_root: Path, manifest: dict[str, object]) -> None:
    _write(repo_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_list_hlist_packet_") as temp_dir:
        repo_root = Path(temp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(repo_root)
            _remove_marker(repo_root, relative_path, marker)
            issues = validate_repo(repo_root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        for field, bad_value in SELF_TEST_FIELD_CASES:
            _populate_repo(repo_root)
            manifest = _load_manifest(repo_root)
            manifest[field] = bad_value
            _write_manifest(repo_root, manifest)
            issues = validate_repo(repo_root)
            expected = (
                f"phase3_list_hlist_manifest.json wrong {field}: "
                f"{bad_value!r} != {EXPECTED_MANIFEST_FIELDS[field]!r}"
            )
            if expected not in issues:
                print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected manifest field drift was not reported: {expected}")
                return 1

        for route in SELF_TEST_REPLAY_ROUTE_CASES:
            _populate_repo(repo_root)
            manifest = _load_manifest(repo_root)
            replay_routes = manifest["replay_routes"]
            assert isinstance(replay_routes, list)
            replay_routes.remove(route)
            _write_manifest(repo_root, manifest)
            issues = validate_repo(repo_root)
            expected = f"phase3_list_hlist_manifest.json missing replay route: {route}"
            if expected not in issues:
                print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected replay-route drift was not reported: {expected}")
                return 1

        for gap in SELF_TEST_REPO_REALITY_GAP_CASES:
            _populate_repo(repo_root)
            manifest = _load_manifest(repo_root)
            repo_reality_gaps = manifest["repo_reality_gaps"]
            assert isinstance(repo_reality_gaps, list)
            repo_reality_gaps.remove(gap)
            _write_manifest(repo_root, manifest)
            issues = validate_repo(repo_root)
            expected = f"phase3_list_hlist_manifest.json missing repo_reality_gaps entry: {gap}"
            if expected not in issues:
                print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected repo-reality-gap drift was not reported: {expected}")
                return 1

        _populate_repo(repo_root)
        present_gap = REQUIRED_REPO_REALITY_GAPS[0]
        _write(repo_root / present_gap, "// unexpected gap file\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_list_hlist_manifest.json repo_reality_gaps entry is present on disk: "
            f"{present_gap}"
        )
        if expected not in issues:
            print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected present-on-disk repo gap issue was not reported: {expected}")
            return 1

    print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass")
    print(
        "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT="
        f"{1 + len(SELF_TEST_CASES) + len(SELF_TEST_FIELD_CASES) + len(SELF_TEST_REPLAY_ROUTE_CASES) + len(SELF_TEST_REPO_REALITY_GAP_CASES) + 1}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 list/hlist starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the list/hlist starter packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in coverage without reading repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LIST_HLIST_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / LIST_PATH}")
    print(f"validated {args.repo_root / HLIST_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
