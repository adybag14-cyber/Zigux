#!/usr/bin/env python3
"""Fail-close the current Phase 3 list/hlist starter-plus-dump packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-list-hlist-slice.md")
LIST_HELPER_PATH = Path("zigux/helpers/list_view.zig")
HLIST_HELPER_PATH = Path("zigux/helpers/hlist_view.zig")
STARTER_TEST_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet.zig")
STARTER_BUILD_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet_build.zig")
DUMP_PATH = Path("zigux/tests/phase3_list_hlist_dump.zig")
DUMP_BUILD_PATH = Path("zigux/tests/phase3_list_hlist_dump_build.zig")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_list_hlist/expected.json")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_list_hlist_manifest.json")

REQUIRED_MARKERS = {
    DOC_PATH: (
        "This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.",
        "`zigux/tests/phase3_list_hlist_dump.zig`",
        "`zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`",
        "`scripts/zigux/check-phase3-list-hlist.py`",
        "`zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig`",
    ),
    LIST_HELPER_PATH: (
        "pub const ListView = struct {",
        "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {",
    ),
    HLIST_HELPER_PATH: (
        "pub const HListView = struct {",
        "pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak {",
    ),
    STARTER_TEST_PATH: (
        'test "list starter packet keeps circular ordering and broken backlinks explicit" {',
        'test "hlist starter packet reports the first broken prev-link witness" {',
    ),
    STARTER_BUILD_PATH: (
        '"phase3-list-hlist-starter-packet"',
        'root_module.addImport("list_view", list_view);',
        'root_module.addImport("hlist_view", hlist_view);',
    ),
    DUMP_PATH: (
        'const list_view = @import("list_view");',
        'const hlist_view = @import("hlist_view");',
        'try writeListCase(writer, "broken_backlink", &list_broken_head, &list_broken_first, &list_broken_second, false);',
        'try writeHListCase(writer, "broken_prev_link", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);',
    ),
    DUMP_BUILD_PATH: (
        '.root_source_file = b.path("phase3_list_hlist_dump.zig"),',
        '"phase3-list-hlist-dump"',
    ),
    C_HARNESS_PATH: (
        'write_list_case("broken_backlink", &list_broken_head, &list_broken_first, &list_broken_second, false);',
        'write_hlist_case("broken_prev_link", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);',
        'if (raw == ptr_of(&head->first)) return "head.first";',
    ),
    EXPECTED_PATH: (
        '"word_bits": 64',
        '"name": "broken_backlink"',
        '"expected_prev_label": "node0"',
        '"name": "broken_prev_link"',
        '"expected_pprev_label": "node0.next"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-list-hlist"',
        '"status": "starter_and_dump_packet_present"',
        '"zigux/tests/phase3_list_hlist_dump.zig"',
        '"scripts/zigux/check-phase3-list-hlist.py"',
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
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _diff(label: str, expected: object, actual: object) -> str:
    expected_text = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    actual_text = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    diff = "".join(
        difflib.unified_diff(
            expected_text.splitlines(keepends=True),
            actual_text.splitlines(keepends=True),
            fromfile=f"{label}-expected",
            tofile=f"{label}-actual",
        )
    )
    return diff.strip() or f"{label} JSON differed without a textual diff"


def _load_json(path: Path) -> object:
    return json.loads(_read(path))


def _run_starter_build(repo_root: Path, zig: str) -> None:
    result = _run(
        [
            zig,
            "build",
            "phase3-list-hlist-starter-packet",
            "--build-file",
            str(repo_root / STARTER_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "starter build failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _run_zig_dump(repo_root: Path, zig: str) -> object:
    result = _run(
        [
            zig,
            "build",
            "phase3-list-hlist-dump",
            "--build-file",
            str(repo_root / DUMP_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "zig dump failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def _run_c_harness(repo_root: Path, cc: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_list_hlist_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_list_hlist_c_harness"
        compile_result = _run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-o",
                str(binary),
                str(repo_root / C_HARNESS_PATH),
            ],
            cwd=repo_root,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "c harness compile failed:\n"
                f"stdout:\n{compile_result.stdout}\n"
                f"stderr:\n{compile_result.stderr}"
            )
        run_result = _run([str(binary)], cwd=repo_root)
        if run_result.returncode != 0:
            raise RuntimeError(
                "c harness run failed:\n"
                f"stdout:\n{run_result.stdout}\n"
                f"stderr:\n{run_result.stderr}"
            )
        return json.loads(run_result.stdout)


def validate_repo(repo_root: Path, zig: str, cc: str, *, skip_exec: bool = False) -> list[str]:
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

    manifest_path = repo_root / MANIFEST_PATH
    try:
        manifest = _load_json(manifest_path)
    except FileNotFoundError:
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    if manifest.get("status") != "starter_and_dump_packet_present":
        issues.append("phase3_list_hlist_manifest.json wrong status")
    if manifest.get("slug") != "phase3-list-hlist":
        issues.append("phase3_list_hlist_manifest.json wrong slug")
    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    if not isinstance(packet_files, list):
        issues.append("phase3_list_hlist_manifest.json packet_files is not a list")
    else:
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_list_hlist_manifest.json missing packet_files entry: {entry}")
    if not isinstance(replay_routes, list):
        issues.append("phase3_list_hlist_manifest.json replay_routes is not a list")
    else:
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(f"phase3_list_hlist_manifest.json missing replay route: {entry}")
    if manifest.get("repo_reality_gaps") != []:
        issues.append("phase3_list_hlist_manifest.json repo_reality_gaps must be empty after the parity packet lands")

    if issues or skip_exec:
        return issues

    expected = _load_json(repo_root / EXPECTED_PATH)
    try:
        _run_starter_build(repo_root, zig)
        zig_actual = _run_zig_dump(repo_root, zig)
        c_actual = _run_c_harness(repo_root, cc)
    except Exception as exc:
        issues.append(str(exc))
        return issues

    if zig_actual != expected:
        issues.append(_diff("zig-dump", expected, zig_actual))
    if c_actual != expected:
        issues.append(_diff("c-harness", expected, c_actual))
    if zig_actual != c_actual:
        issues.append(_diff("zig-vs-c", zig_actual, c_actual))

    return issues


SELF_TEST_CASES = (
    (DOC_PATH, "This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`."),
    (DUMP_PATH, 'try writeListCase(writer, "broken_backlink", &list_broken_head, &list_broken_first, &list_broken_second, false);'),
    (C_HARNESS_PATH, 'write_hlist_case("broken_prev_link", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);'),
    (EXPECTED_PATH, '"expected_pprev_label": "node0.next"'),
    (MANIFEST_PATH, '"status": "starter_and_dump_packet_present"'),
)


def run_self_test() -> int:
    root = Path(__file__).resolve().parents[2]
    issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
    if issues:
        print("PHASE3_LIST_HLIST_SELF_TEST=fail")
        print("\n".join(issues))
        return 1

    for relative_path, marker in SELF_TEST_CASES:
        path = root / relative_path
        original = _read(path)
        path.write_text(original.replace(marker, "", 1), encoding="utf-8")
        try:
            issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LIST_HLIST_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1
        finally:
            path.write_text(original, encoding="utf-8")

    print("PHASE3_LIST_HLIST_SELF_TEST=pass")
    print(f"PHASE3_LIST_HLIST_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 list/hlist starter-plus-dump packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 list/hlist packet",
    )
    parser.add_argument("--zig", help="path to zig executable")
    parser.add_argument("--cc", help="path to C compiler")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = _resolve_tool(args.zig, "ZIG", "zig")
    cc = _resolve_tool(args.cc, "CC", "gcc")
    issues = validate_repo(args.repo_root, zig, cc, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_LIST_HLIST=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / C_HARNESS_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
