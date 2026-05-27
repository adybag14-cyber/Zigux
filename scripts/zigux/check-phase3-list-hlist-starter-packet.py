#!/usr/bin/env python3
"""Fail-close the bounded Phase 3 list/hlist starter packet inside the live starter-plus-dump slice."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase3-list-hlist-slice.md")
LIST_VIEW_PATH = Path("zigux/helpers/list_view.zig")
HLIST_VIEW_PATH = Path("zigux/helpers/hlist_view.zig")
TEST_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_list_hlist_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-list-hlist",
    "status": "starter_and_dump_packet_present",
    "scope": "helper-local list_head and hlist starter packet plus fixture-backed dump parity",
    "next_safe_step": (
        "keep any future same-lane follow-through narrowed to shared validator-entrypoint "
        "alignment or another explicitly bounded helper-local replay route after rereading current master"
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "zigux/tests/phase3_list_hlist_dump.zig",
    "zigux/tests/phase3_list_hlist_dump_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist.py",
    "zigux/Makefile",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "make -C zigux phase3-list-hlist-starter-packet",
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
    "make -C zigux phase3-list-hlist-dump",
)

REQUIRED_REPO_REALITY_GAPS: tuple[str, ...] = ()

REQUIRED_MARKERS = {
    DOC_PATH: (
        "This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.",
        "`zigux/helpers/list_view.zig`",
        "`zigux/helpers/hlist_view.zig`",
        "`zigux/tests/phase3_list_hlist_starter_packet.zig`",
        "`zigux/tests/phase3_list_hlist_starter_packet_build.zig`",
        "`zigux/tests/phase3_list_hlist_dump.zig`",
        "`zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`",
        "`zigux/tests/fixtures/phase3_list_hlist_manifest.json`",
        "`scripts/zigux/check-phase3-list-hlist-starter-packet.py`",
        "`scripts/zigux/check-phase3-list-hlist.py`",
        "`zigux/Makefile`",
        "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
        "make -C zigux phase3-list-hlist-starter-packet",
        "make -C zigux phase3-list-hlist-dump",
        "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc",
        "It does not claim exported ABI structs, intrusive container recovery helpers, list mutation semantics, or wider subsystem-specific list ownership behavior.",
    ),
    LIST_VIEW_PATH: (
        "pub const ListView = struct {",
        "pub fn first(self: ListView) ?*const ListHead {",
        "pub fn last(self: ListView) ?*const ListHead {",
        "pub fn hasConsistentBacklinks(self: ListView) bool {",
        "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {",
    ),
    HLIST_VIEW_PATH: (
        "pub const HListView = struct {",
        "pub fn first(self: HListView) ?*const HListNode {",
        "pub fn firstPprevMatchesHead(self: HListView) bool {",
        "pub fn hasConsistentPrevLinks(self: HListView) bool {",
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
    MAKEFILE_PATH: (
        "phase3-list-hlist-starter-packet:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
        "phase3-list-hlist-dump:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-list-hlist"',
        '"status": "starter_and_dump_packet_present"',
        '"zigux/tests/phase3_list_hlist_starter_packet.zig"',
        '"zigux/tests/phase3_list_hlist_dump.zig"',
        '"scripts/zigux/check-phase3-list-hlist-starter-packet.py"',
        '"scripts/zigux/check-phase3-list-hlist.py"',
        '"zigux/Makefile"',
        '"make -C zigux phase3-list-hlist-starter-packet"',
        '"make -C zigux phase3-list-hlist-dump"',
    ),
}

SELF_TEST_CASES = (
    (DOC_PATH, "`scripts/zigux/check-phase3-list-hlist.py`"),
    (LIST_VIEW_PATH, "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {"),
    (HLIST_VIEW_PATH, "pub fn tailNextIsNull(self: HListView) bool {"),
    (TEST_PATH, 'test "hlist starter packet reports the first broken prev-link witness" {'),
    (BUILD_PATH, '"phase3-list-hlist-starter-packet"'),
    (MAKEFILE_PATH, "phase3-list-hlist-starter-packet:"),
    (MANIFEST_PATH, '"status": "starter_and_dump_packet_present"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


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


def _run_zig_build(repo_root: Path, zig: str) -> None:
    result = _run(
        [
            zig,
            "build",
            "phase3-list-hlist-starter-packet",
            "--build-file",
            str(BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "zig starter packet build failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def validate_repo(repo_root: Path, zig: str, *, skip_exec: bool = False) -> list[str]:
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

    if repo_reality_gaps != list(REQUIRED_REPO_REALITY_GAPS):
        issues.append(
            "phase3_list_hlist_manifest.json repo_reality_gaps must stay empty after the dump packet lands"
        )

    if issues or skip_exec:
        return issues

    try:
        _run_zig_build(repo_root, zig)
    except Exception as exc:
        issues.append(str(exc))

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


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_list_hlist_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root, zig="zig", skip_exec=True)
        if issues:
            print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root, zig="zig", skip_exec=True)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].append(REQUIRED_PACKET_FILES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root, zig="zig", skip_exec=True)
        expected = "phase3_list_hlist_manifest.json packet_files duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
            print("expected duplicate packet_files entry was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root, zig="zig", skip_exec=True)
        expected = "phase3_list_hlist_manifest.json replay_routes duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
            print("expected duplicate replay_routes entry was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["stale-gap"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root, zig="zig", skip_exec=True)
        expected = (
            "phase3_list_hlist_manifest.json repo_reality_gaps must stay empty after the dump packet lands"
        )
        if expected not in issues:
            print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=fail")
            print("expected repo_reality_gaps drift was not reported")
            return 1

    print("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 3}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 3 list/hlist starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 list/hlist starter packet",
    )
    parser.add_argument("--zig", help="path to Zig toolchain")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = _resolve_tool(args.zig, "ZIG", "zig")
    issues = validate_repo(args.repo_root, zig, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_LIST_HLIST_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_LIST_HLIST_PACKET=pass")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
