#!/usr/bin/env python3
"""Check the bounded Phase 3 list/hlist starter packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SLICE_DOC_PATH = Path("Documentation/zigux/phase3-list-hlist-slice.md")
CHECKER_PATH = Path("scripts/zigux/check-phase3-list-hlist.py")
HEADER_PATH = Path("include/zigux/list_hlist.h")
UAPI_PATH = Path("zigux/uapi/list_hlist.zig")
BINDING_PATH = Path("zigux/bindings/list_hlist.zig")
LIST_HELPER_PATH = Path("zigux/helpers/list_view.zig")
HLIST_HELPER_PATH = Path("zigux/helpers/hlist_view.zig")
TEST_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_list_hlist_starter_packet_manifest.json")
DUMP_PATH = Path("zigux/tests/phase3_list_hlist_dump.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_list_hlist/expected.json")
HARNESS_PATH = Path(
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c"
)

REQUIRED_FILES = (
    SLICE_DOC_PATH,
    CHECKER_PATH,
    HEADER_PATH,
    UAPI_PATH,
    BINDING_PATH,
    LIST_HELPER_PATH,
    HLIST_HELPER_PATH,
    TEST_PATH,
    BUILD_PATH,
    MANIFEST_PATH,
    DUMP_PATH,
    EXPECTED_PATH,
    HARNESS_PATH,
)

REQUIRED_DOC_MARKERS = (
    "include/zigux/list_hlist.h",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "This is not the broader shared Phase 3 ABI substrate",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist.py",
)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    doc_path = repo_root / SLICE_DOC_PATH
    if doc_path.is_file():
        text = doc_path.read_text(encoding="utf-8")
        for marker in REQUIRED_DOC_MARKERS:
            if marker not in text:
                issues.append(f"missing {SLICE_DOC_PATH.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            if not isinstance(packet_files, list):
                issues.append(f"{MANIFEST_PATH.as_posix()} packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append(f"{MANIFEST_PATH.as_posix()} replay_routes is not a list")
            if isinstance(packet_files, list):
                for rel_path in REQUIRED_FILES:
                    if rel_path.as_posix() not in packet_files and rel_path != CHECKER_PATH:
                        issues.append(
                            f"{MANIFEST_PATH.as_posix()} missing packet_files entry: {rel_path.as_posix()}"
                        )
                if CHECKER_PATH.as_posix() not in packet_files:
                    issues.append(
                        f"{MANIFEST_PATH.as_posix()} missing packet_files entry: {CHECKER_PATH.as_posix()}"
                    )
            if isinstance(replay_routes, list):
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            f"{MANIFEST_PATH.as_posix()} missing replay route: {route}"
                        )
    return issues


def resolve_zig_binary(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("missing Zig binary; pass --zig or add `zig` to PATH")


def run_c_harness(repo_root: Path) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_list_hlist_c_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        output_path = tmp_path / "phase3_list_hlist_c_harness"
        subprocess.run(
            [
                "gcc",
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-o",
                str(output_path),
                str(repo_root / HARNESS_PATH),
            ],
            check=True,
            cwd=repo_root,
        )
        result = subprocess.run(
            [str(output_path)],
            check=True,
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    return json.loads(result.stdout)


def render_build_file(repo_root: Path) -> str:
    dump = (repo_root / DUMP_PATH).as_posix()
    helper_list = (repo_root / LIST_HELPER_PATH).as_posix()
    helper_hlist = (repo_root / HLIST_HELPER_PATH).as_posix()
    binding = (repo_root / BINDING_PATH).as_posix()
    uapi = (repo_root / UAPI_PATH).as_posix()
    return f"""const std = @import("std");

pub fn build(b: *std.Build) void {{
    const target = b.standardTargetOptions(.{{}});
    const optimize = b.standardOptimizeOption(.{{}});

    const uapi_list_hlist = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = "{uapi}" }},
        .target = target,
        .optimize = optimize,
    }});
    const list_hlist_binding = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = "{binding}" }},
        .target = target,
        .optimize = optimize,
    }});
    list_hlist_binding.addImport("uapi_list_hlist", uapi_list_hlist);

    const list_view = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = "{helper_list}" }},
        .target = target,
        .optimize = optimize,
    }});
    list_view.addImport("list_hlist_binding", list_hlist_binding);

    const hlist_view = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = "{helper_hlist}" }},
        .target = target,
        .optimize = optimize,
    }});
    hlist_view.addImport("list_hlist_binding", list_hlist_binding);

    const root_module = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = "{dump}" }},
        .target = target,
        .optimize = optimize,
    }});
    root_module.addImport("list_hlist_binding", list_hlist_binding);
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const exe = b.addExecutable(.{{
        .name = "phase3-list-hlist-dump",
        .root_module = root_module,
    }});

    const run_artifact = b.addRunArtifact(exe);
    const run_step = b.step("run", "Run the Phase 3 list/hlist dump");
    run_step.dependOn(&run_artifact.step);
}}
"""


def run_zig_dump(repo_root: Path, zig_binary: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_list_hlist_zig_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        build_path = tmp_path / "build.zig"
        cache_dir = tmp_path / "cache"
        global_cache_dir = tmp_path / "global-cache"
        build_path.write_text(render_build_file(repo_root), encoding="utf-8")
        result = subprocess.run(
            [
                zig_binary,
                "build",
                "run",
                "--build-file",
                str(build_path),
                "--cache-dir",
                str(cache_dir),
                "--global-cache-dir",
                str(global_cache_dir),
            ],
            check=True,
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
    return json.loads(result.stdout)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_list_hlist_selftest_") as tmp:
        root = Path(tmp)
        for rel_path in REQUIRED_FILES:
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel_path == MANIFEST_PATH:
                path.write_text(
                    json.dumps(
                        {
                            "packet_files": [p.as_posix() for p in REQUIRED_FILES],
                            "replay_routes": list(REQUIRED_REPLAY_ROUTES),
                        }
                    ),
                    encoding="utf-8",
                )
            elif rel_path == SLICE_DOC_PATH:
                path.write_text("\n".join(REQUIRED_DOC_MARKERS) + "\n", encoding="utf-8")
            elif rel_path == EXPECTED_PATH:
                path.writeText = None
                path.write_text("{}\n", encoding="utf-8")
            else:
                path.write_text("// placeholder\n", encoding="utf-8")
        assert validate_repo(root) == []

        missing = root / DUMP_PATH
        missing.unlink()
        assert validate_repo(root) == [f"missing repo file: {DUMP_PATH.as_posix()}"]

    print("PHASE3_LIST_HLIST_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 3 list/hlist starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (default: current repo root).",
    )
    parser.add_argument(
        "--zig",
        help="Path to the Zig binary for running the dump replay.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the lightweight checker self-test and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = args.repo_root.resolve()
    issues = validate_repo(repo_root)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    expected = _read_json(repo_root / EXPECTED_PATH)
    c_result = run_c_harness(repo_root)
    if c_result != expected:
        print("phase3 list/hlist C harness output mismatch")
        print(json.dumps(c_result, indent=2, sort_keys=True))
        return 1

    zig_result = run_zig_dump(repo_root, resolve_zig_binary(args.zig))
    if zig_result != expected:
        print("phase3 list/hlist Zig dump output mismatch")
        print(json.dumps(zig_result, indent=2, sort_keys=True))
        return 1

    print("PHASE3_LIST_HLIST_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
