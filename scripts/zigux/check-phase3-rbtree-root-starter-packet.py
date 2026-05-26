#!/usr/bin/env python3
"""Fail-close the bounded Phase 3 rbtree root starter packet."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase3-rbtree-root-slice.md")
BINDING_PATH = Path("zigux/bindings/rbtree_root.zig")
HELPER_PATH = Path("zigux/helpers/rbtree_root_view.zig")
TEST_PATH = Path("zigux/tests/phase3_rbtree_root_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_rbtree_root_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_rbtree_root_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-rbtree-root-starter-packet",
    "status": "helper_local_rbtree_root_slice_present",
    "scope": "helper-local rbtree root cached-leftmost and canonicalization replay",
    "next_safe_step": (
        "if this slice needs parity expansion later, add the narrow C harness and "
        "expected fixture without widening beyond helper-local root view layout and cached-leftmost semantics"
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-rbtree-root-slice.md",
    "zigux/bindings/rbtree_root.zig",
    "zigux/helpers/rbtree_root_view.zig",
    "zigux/tests/phase3_rbtree_root_starter_packet.zig",
    "zigux/tests/phase3_rbtree_root_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_rbtree_root_manifest.json",
    "scripts/zigux/check-phase3-rbtree-root-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-rbtree-root-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-rbtree-root-starter-packet.py",
    "zig build phase3-rbtree-root-starter-packet --build-file zigux/tests/phase3_rbtree_root_starter_packet_build.zig",
)

REQUIRED_REPO_REALITY_GAPS = (
    "zigux/tests/fixtures/phase3_rbtree_root/phase3_rbtree_root_c_harness.c",
    "zigux/tests/fixtures/phase3_rbtree_root/expected.json",
)

REQUIRED_MARKERS = {
    DOC_PATH: (
        "# Phase 3 rbtree root Slice",
        "`zigux/bindings/rbtree_root.zig`",
        "`zigux/helpers/rbtree_root_view.zig`",
        "`zigux/tests/phase3_rbtree_root_starter_packet.zig`",
        "`zigux/tests/phase3_rbtree_root_starter_packet_build.zig`",
        "`zigux/tests/fixtures/phase3_rbtree_root_manifest.json`",
        "`scripts/zigux/check-phase3-rbtree-root-starter-packet.py`",
        "zig build phase3-rbtree-root-starter-packet --build-file zigux/tests/phase3_rbtree_root_starter_packet_build.zig",
    ),
    BINDING_PATH: (
        'const abi = @import("abi_bindings");',
        "pub const RootView = abi.RbtreeRootView;",
        "pub fn empty() RootView {",
        "pub fn cached(root: usize, cached_leftmost: usize) RootView {",
        "pub fn canonicalize(view: RootView) ?RootView {",
    ),
    HELPER_PATH: (
        'const rbtree = @import("rbtree_bindings");',
        "pub const RootView = rbtree.RootView;",
        "pub fn cached(root: usize, cached_leftmost: usize) RootView {",
        "pub fn canonicalize(view: RootView) ?RootView {",
        'test "phase3 rbtree root view helper rejects unknown flags and rootless payloads" {',
    ),
    TEST_PATH: (
        'test "rbtree root starter packet keeps the empty helper lane explicit" {',
        'test "rbtree root starter packet keeps uncached rooted views canonical" {',
        'test "rbtree root starter packet keeps cached leftmost relays explicit" {',
        'test "rbtree root starter packet keeps cached flag drift narrow" {',
        'test "rbtree root starter packet rejects unknown flags and rootless payloads" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../bindings/rbtree_root.zig"),',
        '.root_source_file = b.path("../helpers/rbtree_root_view.zig"),',
        '.root_source_file = b.path("phase3_rbtree_root_starter_packet.zig"),',
        'root_module.addImport("rbtree_bindings", rbtree_bindings);',
        '"phase3-rbtree-root-starter-packet"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-rbtree-root-starter-packet"',
        '"status": "helper_local_rbtree_root_slice_present"',
        '"scripts/zigux/check-phase3-rbtree-root-starter-packet.py"',
        '"zigux/tests/fixtures/phase3_rbtree_root/phase3_rbtree_root_c_harness.c"',
        '"zigux/tests/fixtures/phase3_rbtree_root/expected.json"',
    ),
}

SELF_TEST_CASES = (
    (DOC_PATH, "`zigux/bindings/rbtree_root.zig`"),
    (BINDING_PATH, "pub fn canonicalize(view: RootView) ?RootView {"),
    (HELPER_PATH, "pub fn canonicalize(view: RootView) ?RootView {"),
    (TEST_PATH, 'test "rbtree root starter packet keeps cached flag drift narrow" {'),
    (BUILD_PATH, '"phase3-rbtree-root-starter-packet"'),
    (MANIFEST_PATH, '"status": "helper_local_rbtree_root_slice_present"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


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
        issues.append(f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})")


def _run_zig_build(repo_root: Path, zig: str) -> None:
    result = _run(
        [
            zig,
            "build",
            "phase3-rbtree-root-starter-packet",
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
                f"phase3_rbtree_root_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_rbtree_root_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_rbtree_root_manifest.json packet_files", packet_files, issues
        )
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(
                    f"phase3_rbtree_root_manifest.json missing packet_files entry: {entry}"
                )

    if not isinstance(replay_routes, list):
        issues.append("phase3_rbtree_root_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_rbtree_root_manifest.json replay_routes", replay_routes, issues
        )
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(
                    f"phase3_rbtree_root_manifest.json missing replay route: {entry}"
                )

    if repo_reality_gaps != list(REQUIRED_REPO_REALITY_GAPS):
        issues.append(
            "phase3_rbtree_root_manifest.json repo_reality_gaps must stay aligned with the documented absent C parity companions"
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_root_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root, zig="zig", skip_exec=True)
        if issues:
            print("PHASE3_RBTREE_ROOT_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root, zig="zig", skip_exec=True)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_RBTREE_ROOT_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_RBTREE_ROOT_PACKET_SELF_TEST=pass")
    print(f"PHASE3_RBTREE_ROOT_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 3 rbtree root starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 rbtree root starter packet",
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
        print("PHASE3_RBTREE_ROOT_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_RBTREE_ROOT_PACKET=pass")
    print(f"validated {args.repo_root / HELPER_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
