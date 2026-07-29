#!/usr/bin/env python3
"""Build Linux tools, tests, samples, documentation, and Rust developer targets."""

from __future__ import annotations

import argparse
import json
import os
import shutil
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
            mapping_root = source_root
            rc = runner.run(["make", "-C", str(source_root / "tools/testing/selftests"), "-k", f"-j{jobs}", "FORCE_TARGETS=1"], cwd=source_root, env=env)
        elif task == "kunit":
            mapping_root = out_root / "kunit"
            rc = runner.run([sys.executable, str(source_root / "tools/testing/kunit/kunit.py"), "build", "--build_dir", str(mapping_root), "--jobs", jobs], cwd=source_root, env=env)
        elif task == "perf":
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
