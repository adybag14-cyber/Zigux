#!/usr/bin/env python3
"""Check the bounded Phase 3 notifier-chain shared-subsystems packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SLICE_DOC_PATH = Path("Documentation/zigux/phase3-notifier-chain-slice.md")
CHECKER_PATH = Path("scripts/zigux/check-phase3-notifier-chain.py")
DUMP_PATH = Path("zigux/tests/phase3_notifier_chain_dump.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_notifier_chain/expected.json")
HARNESS_PATH = Path(
    "zigux/tests/fixtures/phase3_notifier_chain/phase3_notifier_chain_c_harness.c"
)
HELPER_PATH = Path("zigux/helpers/notifier_chain_view.zig")
BINDINGS_PATH = Path("zigux/bindings/notifier_abi.zig")

REQUIRED_FILES = (
    SLICE_DOC_PATH,
    CHECKER_PATH,
    DUMP_PATH,
    EXPECTED_PATH,
    HARNESS_PATH,
    HELPER_PATH,
    BINDINGS_PATH,
)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
    return issues


def resolve_zig_binary(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("missing Zig binary; pass --zig or add `zig` to PATH")


def run_c_harness(repo_root: Path) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_notifier_chain_c_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        output_path = tmp_path / "phase3_notifier_chain_c_harness"
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
    helper = (repo_root / HELPER_PATH).as_posix()
    bindings = (repo_root / BINDINGS_PATH).as_posix()
    return f"""const std = @import(\"std\");

pub fn build(b: *std.Build) void {{
    const target = b.standardTargetOptions(.{{}});
    const optimize = b.standardOptimizeOption(.{{}});

    const notifier_bindings = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = \"{bindings}\" }},
        .target = target,
        .optimize = optimize,
    }});
    const helper_module = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = \"{helper}\" }},
        .target = target,
        .optimize = optimize,
    }});
    helper_module.addImport(\"notifier_abi_bindings\", notifier_bindings);

    const root_module = b.createModule(.{{
        .root_source_file = .{{ .cwd_relative = \"{dump}\" }},
        .target = target,
        .optimize = optimize,
    }});
    root_module.addImport(\"notifier_abi_bindings\", notifier_bindings);
    root_module.addImport(\"notifier_chain_view\", helper_module);

    const exe = b.addExecutable(.{{
        .name = \"phase3-notifier-chain-dump\",
        .root_module = root_module,
    }});

    const run_artifact = b.addRunArtifact(exe);
    const run_step = b.step(\"run\", \"Run the Phase 3 notifier-chain dump\");
    run_step.dependOn(&run_artifact.step);
}}
"""


def run_zig_dump(repo_root: Path, zig_binary: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_notifier_chain_zig_") as tmp_dir:
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_notifier_chain_selftest_") as tmp:
        root = Path(tmp)
        for rel_path in REQUIRED_FILES:
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")
        assert validate_repo(root) == []

        missing = root / DUMP_PATH
        missing.unlink()
        assert validate_repo(root) == [f"missing repo file: {DUMP_PATH.as_posix()}"]

    print("PHASE3_NOTIFIER_CHAIN_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 3 notifier-chain shared-subsystems packet."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--zig")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = args.repo_root.resolve()
    issues = validate_repo(repo_root)
    if issues:
        print("PHASE3_NOTIFIER_CHAIN=fail")
        for issue in issues:
            print(issue)
        return 1

    expected = _read_json(repo_root / EXPECTED_PATH)
    c_actual = run_c_harness(repo_root)
    zig_actual = run_zig_dump(repo_root, resolve_zig_binary(args.zig))

    if c_actual != expected:
        print("PHASE3_NOTIFIER_CHAIN=fail")
        print("c harness drifted from committed expected.json")
        return 1
    if zig_actual != expected:
        print("PHASE3_NOTIFIER_CHAIN=fail")
        print("zig dump drifted from committed expected.json")
        return 1
    if c_actual != zig_actual:
        print("PHASE3_NOTIFIER_CHAIN=fail")
        print("c harness and zig dump disagree")
        return 1

    print("PHASE3_NOTIFIER_CHAIN=pass")
    print("PHASE3_NOTIFIER_CHAIN_CASES=empty,ordered,unordered,results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
