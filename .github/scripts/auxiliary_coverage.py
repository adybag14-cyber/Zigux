#!/usr/bin/env python3
"""Build Linux tools, tests, samples, documentation, and Rust developer targets."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from kernel_coverage import (
    LoggedRunner,
    compact_log,
    create_object_map,
    make_command,
    prepare_source,
    scripts_config,
    setup_toolchain,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-json", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--record-root", required=True)
    args = parser.parse_args()

    row: dict[str, Any] = json.loads(args.row_json)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    record_dir = Path(args.record_root) / "records" / f"aux-{row['id']}"
    record_dir.mkdir(parents=True, exist_ok=True)
    runner = LoggedRunner(record_dir / "build.log")

    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd()))
    temp_root = Path(os.environ.get("RUNNER_TEMP", workspace / ".tmp")) / f"full-linux-aux-{row['id']}"
    source_root = temp_root / "source"
    tool_root = temp_root / "toolchains"
    out_root = workspace / "out-full-linux" / f"aux-{row['id']}"
    shutil.rmtree(temp_root, ignore_errors=True)
    shutil.rmtree(out_root, ignore_errors=True)
    source_root.mkdir(parents=True, exist_ok=True)
    tool_root.mkdir(parents=True, exist_ok=True)
    out_root.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "schema": 1,
        "build_id": f"aux-{row['id']}",
        "kind": "auxiliary",
        "task": row["task"],
        "profile": row["task"],
        "architecture": "x86",
        "toolchain": row.get("toolchain", "native-gcc"),
        "source_sha": args.source_sha,
        "status": "infrastructure_error",
    }
    started = time.time()
    exit_code = 1

    try:
        prepare_source(args.repository, args.source_sha, source_root, temp_root)
        env = os.environ.copy()
        env.update({
            "ARCH": "x86",
            "KBUILD_BUILD_USER": "github-actions",
            "KBUILD_BUILD_HOST": "zigux-full-coverage",
            "KBUILD_BUILD_VERSION": "1",
            "KBUILD_BUILD_TIMESTAMP": "Thu Jan 1 00:00:00 UTC 1970",
            "CCACHE_DISABLE": "1",
        })
        task = row["task"]
        jobs = str(os.cpu_count() or 2)

        if row.get("toolchain") == "rust":
            tool_row = {"id": f"aux-{row['id']}", "toolchain": "rust", "gcc_triple": "x86_64-linux", "llvm_ias": True}
            manifest["toolchain_metadata"] = setup_toolchain(tool_row, config, tool_root, env)
        else:
            manifest["toolchain_metadata"] = {"kind": "native-gcc", "gcc": shutil.which("gcc") or "gcc"}

        rc = 0
        mapping_root = out_root

        if task == "headers":
            rc = runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "headers_install", f"INSTALL_HDR_PATH={out_root / 'headers'}"), env=env)
        elif task == "samples":
            runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "x86_64_defconfig"), env=env, check=True)
            scripts_config(source_root, out_root, "--enable", "SAMPLES", runner, env)
            for symbol in ("WERROR", "RUST", "GCC_PLUGINS", "DEBUG_INFO"):
                scripts_config(source_root, out_root, "--disable", symbol, runner, env)
            runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "olddefconfig"), env=env, check=True)
            rc = runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "-k", f"-j{jobs}", "samples"), env=env)
        elif task == "selftests":
            mapping_root = out_root / "kselftest"
            runner.run(
                make_command(source_root, out_root, {"kbuild_arch": "x86"}, "headers"),
                env=env,
                check=True,
            )
            rc = runner.run(
                [
                    "make",
                    "-C",
                    str(source_root / "tools/testing/selftests"),
                    "-k",
                    f"-j{jobs}",
                    f"O={out_root}",
                    "FORCE_TARGETS=1",
                ],
                cwd=source_root,
                env=env,
            )
        elif task == "kunit":
            mapping_root = out_root / "kunit"
            mapping_root.mkdir(parents=True, exist_ok=True)
            kunit_config = source_root / "tools/testing/kunit/configs/default.config"
            if not kunit_config.is_file():
                raise FileNotFoundError(f"KUnit default configuration was not found: {kunit_config}")
            rc = runner.run(
                [
                    sys.executable,
                    str(source_root / "tools/testing/kunit/kunit.py"),
                    "build",
                    "--build_dir",
                    str(mapping_root),
                    "--kunitconfig",
                    str(kunit_config),
                    "--jobs",
                    jobs,
                ],
                cwd=source_root,
                env=env,
            )
        elif task == "perf":
            capstone_cfg = config["capstone_toolchain"]
            capstone_root = temp_root / "capstone"
            capstone_prefix = tool_root / "capstone-prefix"
            runner.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    capstone_cfg["tag"],
                    capstone_cfg["repository"],
                    str(capstone_root),
                ],
                check=True,
            )
            capstone_commit = subprocess.check_output(
                ["git", "-C", str(capstone_root), "rev-parse", "HEAD"],
                text=True,
            ).strip()
            if capstone_commit != capstone_cfg["commit"]:
                raise RuntimeError(
                    f"Capstone tag {capstone_cfg['tag']} resolved to {capstone_commit}, "
                    f"expected {capstone_cfg['commit']}"
                )
            capstone_args = [
                f"CAPSTONE_ARCHS={capstone_cfg['architectures']}",
                "CAPSTONE_STATIC=yes",
                "CAPSTONE_SHARED=yes",
                f"PREFIX={capstone_prefix}",
            ]
            runner.run(
                ["make", "-C", str(capstone_root), f"-j{jobs}", *capstone_args],
                env=env,
                check=True,
            )
            runner.run(
                ["make", "-C", str(capstone_root), "install", *capstone_args],
                env=env,
                check=True,
            )
            pkgconfig = capstone_prefix / "lib/pkgconfig"
            env["PKG_CONFIG_PATH"] = str(pkgconfig) + os.pathsep + env.get("PKG_CONFIG_PATH", "")
            env["CPATH"] = str(capstone_prefix / "include") + os.pathsep + env.get("CPATH", "")
            env["LIBRARY_PATH"] = str(capstone_prefix / "lib") + os.pathsep + env.get("LIBRARY_PATH", "")
            env["LD_LIBRARY_PATH"] = str(capstone_prefix / "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
            manifest["capstone"] = {
                "tag": capstone_cfg["tag"],
                "commit": capstone_commit,
                "pkg_config_version": subprocess.check_output(
                    ["pkg-config", "--modversion", "capstone"],
                    env=env,
                    text=True,
                ).strip(),
            }
            mapping_root = source_root / "tools/perf"
            rc = runner.run(["make", "-C", str(mapping_root), "-k", f"-j{jobs}"], cwd=source_root, env=env)
        elif task == "bpftool":
            mapping_root = source_root / "tools/bpf/bpftool"
            rc = runner.run(["make", "-C", str(mapping_root), "-k", f"-j{jobs}"], cwd=source_root, env=env)
        elif task == "objtool":
            mapping_root = source_root / "tools/objtool"
            rc = runner.run(["make", "-C", str(mapping_root), "-k", f"-j{jobs}"], cwd=source_root, env=env)
        elif task == "docs-html":
            rc = runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "-k", f"-j{jobs}", "htmldocs"), env=env)
            manifest["html_file_count"] = sum(1 for _ in out_root.rglob("*.html"))
        elif task in {"rusttest", "rustdoc", "rust-analyzer"}:
            runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "x86_64_defconfig"), env=env, check=True)
            runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "rustavailable"), env=env, check=True)
            for symbol in ("WERROR", "GCC_PLUGINS"):
                scripts_config(source_root, out_root, "--disable", symbol, runner, env)
            for symbol in ("RUST", "MODULES"):
                scripts_config(source_root, out_root, "--enable", symbol, runner, env)
            runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "olddefconfig"), env=env, check=True)
            if "CONFIG_RUST=y" not in (out_root / ".config").read_text(encoding="utf-8", errors="replace").splitlines():
                raise RuntimeError("CONFIG_RUST=y was not enabled for the Rust auxiliary target")
            rc = runner.run(make_command(source_root, out_root, {"kbuild_arch": "x86"}, "-k", f"-j{jobs}", task), env=env)
        else:
            raise ValueError(f"unsupported auxiliary task: {task}")

        manifest["build_exit_code"] = rc
        manifest["status"] = "success" if rc == 0 else "build_failed"
        exit_code = rc

        if mapping_root.exists():
            object_count, mapped_sources = create_object_map(source_root, mapping_root, record_dir, {
                "id": f"aux-{row['id']}", "architecture": "x86", "profile": task, "toolchain": row.get("toolchain", "native-gcc")
            })
        else:
            object_count, mapped_sources = 0, 0
        manifest["object_count"] = object_count
        manifest["mapped_source_count"] = mapped_sources

        outputs = []
        for root in (out_root, mapping_root):
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix in {".html", ".json", ".a", ".so", ".ko"}:
                    try:
                        outputs.append(path.relative_to(source_root).as_posix())
                    except ValueError:
                        try:
                            outputs.append(path.relative_to(workspace).as_posix())
                        except ValueError:
                            outputs.append(str(path))
        (record_dir / "selected-outputs.txt").write_text("\n".join(sorted(set(outputs))) + ("\n" if outputs else ""), encoding="utf-8")
    except Exception as exc:
        manifest["status"] = "infrastructure_error"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        with (record_dir / "build.log").open("a", encoding="utf-8") as log:
            log.write(f"\nFATAL: {manifest['error']}\n")
        print(f"::error::aux-{row['id']}: {manifest['error']}", file=sys.stderr)
        exit_code = 1
    finally:
        manifest["elapsed_seconds"] = round(time.time() - started, 3)
        manifest["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        compact_log(record_dir / "build.log")
        (record_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (record_dir / "row.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({key: manifest.get(key) for key in ("build_id", "status", "object_count", "mapped_source_count")}, sort_keys=True))

    return int(exit_code != 0)


if __name__ == "__main__":
    raise SystemExit(main())
