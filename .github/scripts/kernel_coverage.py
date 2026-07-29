#!/usr/bin/env python3
"""Run one cold Linux kernel source-coverage build and emit a compact record."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path
from typing import Any, Iterable


SOURCE_SUFFIXES = (".c", ".S", ".s", ".rs")


class LoggedRunner:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        command: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        check: bool = False,
    ) -> int:
        printable = " ".join(subprocess.list2cmdline([item]) for item in command)
        with self.log_path.open("a", encoding="utf-8", errors="replace") as log:
            log.write(f"\n$ {printable}\n")
            log.flush()
            process = subprocess.Popen(
                command,
                cwd=str(cwd) if cwd else None,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="replace",
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                sys.stdout.write(line)
                log.write(line)
            rc = process.wait()
            log.write(f"[exit {rc}]\n")
        if check and rc:
            raise subprocess.CalledProcessError(rc, command)
        return rc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Zigux-full-linux-coverage/1"})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out)


def safe_extract(tar: tarfile.TarFile, destination: Path, *, strip_first_component: bool = False) -> None:
    """Extract a trusted archive while rejecting path traversal and special files."""
    root = destination.resolve()
    members: list[tarfile.TarInfo] = []
    for original in tar.getmembers():
        member = original.replace()
        name = member.name
        if strip_first_component:
            parts = name.split("/", 1)
            if len(parts) != 2 or not parts[1]:
                continue
            name = parts[1]
            member.name = name
        target = (destination / name).resolve()
        if target != root and root not in target.parents:
            raise RuntimeError(f"archive member escapes extraction root: {original.name}")
        if member.ischr() or member.isblk() or member.isfifo():
            raise RuntimeError(f"unsupported special archive member: {original.name}")
        members.append(member)
    tar.extractall(destination, members=members, filter="data")


def compact_log(log_path: Path, *, max_bytes: int = 2_000_000) -> None:
    """Keep a bounded diagnostic excerpt; the full stream remains in Actions logs."""
    if not log_path.is_file():
        return
    data = log_path.read_bytes()
    excerpt_path = log_path.with_name("build-log-excerpt.txt")
    if len(data) <= max_bytes:
        excerpt_path.write_bytes(data)
    else:
        head_size = min(128_000, max_bytes // 4)
        tail_size = max_bytes - head_size
        marker = (
            f"\n\n--- {len(data) - head_size - tail_size:,} bytes omitted; "
            "consult the GitHub Actions job log for the complete stream ---\n\n"
        ).encode()
        excerpt_path.write_bytes(data[:head_size] + marker + data[-tail_size:])
    log_path.unlink(missing_ok=True)


def verified_download(base_url: str, archive: str, destination: Path) -> None:
    checksum_file = destination.parent / "sha256sums.asc"
    download(f"{base_url.rstrip('/')}/sha256sums.asc", checksum_file)
    text = checksum_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"^([0-9a-fA-F]{{64}})\s+\*?{re.escape(archive)}$", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"checksum for {archive} was not found in {base_url}/sha256sums.asc")
    expected = match.group(1).lower()
    download(f"{base_url.rstrip('/')}/{archive}", destination)
    actual = sha256_file(destination)
    if actual != expected:
        raise RuntimeError(f"SHA-256 mismatch for {archive}: expected {expected}, got {actual}")


def extract_archive(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, mode="r:xz") as tar:
        safe_extract(tar, destination)


def find_executable(root: Path, name: str) -> Path:
    matches = [path for path in root.rglob(name) if path.is_file() and os.access(path, os.X_OK)]
    if not matches:
        raise FileNotFoundError(f"{name} was not found below {root}")
    matches.sort(key=lambda path: (len(path.parts), str(path)))
    return matches[0]


def prepare_source(repository: str, source_sha: str, source_root: Path, temp_root: Path) -> None:
    archive = temp_root / f"source-{source_sha[:12]}.tar.gz"
    download(f"https://codeload.github.com/{repository}/tar.gz/{source_sha}", archive)
    source_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, mode="r:gz") as tar:
        safe_extract(tar, source_root, strip_first_component=True)
    if not (source_root / "Makefile").is_file():
        raise RuntimeError("downloaded source snapshot does not contain a kernel Makefile")


def setup_toolchain(
    row: dict[str, Any],
    config: dict[str, Any],
    tool_root: Path,
    env: dict[str, str],
) -> dict[str, str]:
    toolchain = row["toolchain"]
    metadata: dict[str, str] = {"kind": toolchain}
    path_parts: list[str] = []

    def add_gcc(triple: str) -> str:
        gcc_cfg = config["gcc_toolchain"]
        archive = f"x86_64-gcc-{gcc_cfg['version']}-nolibc-{triple}.tar.xz"
        archive_path = tool_root / archive
        extract_root = tool_root / f"gcc-{triple}"
        verified_download(gcc_cfg["base_url"], archive, archive_path)
        extract_archive(archive_path, extract_root)
        gcc = find_executable(extract_root, f"{triple}-gcc")
        path_parts.append(str(gcc.parent))
        metadata["gcc"] = str(gcc)
        metadata["gcc_archive"] = archive
        return str(gcc.with_name(f"{triple}-"))

    def add_llvm() -> Path:
        cfg = config["llvm_toolchain"]
        archive = cfg["archive"]
        archive_path = tool_root / archive
        extract_root = tool_root / "llvm"
        verified_download(cfg["base_url"], archive, archive_path)
        extract_archive(archive_path, extract_root)
        clang = find_executable(extract_root, "clang")
        path_parts.append(str(clang.parent))
        metadata["clang"] = str(clang)
        metadata["llvm_archive"] = archive
        libclang_candidates = sorted(
            (path for path in extract_root.rglob("libclang.so*") if path.is_file()),
            key=lambda path: (path.name != "libclang.so", len(path.parts), str(path)),
        )
        if libclang_candidates:
            env["LIBCLANG_PATH"] = str(libclang_candidates[0].parent)
            metadata["libclang"] = str(libclang_candidates[0])
        return extract_root

    if toolchain == "gcc":
        triple = row.get("gcc_triple", "")
        if not triple:
            raise ValueError(f"GCC row {row['id']} is missing gcc_triple")
        env["CROSS_COMPILE"] = add_gcc(triple)
    elif toolchain == "native-gcc":
        env.pop("CROSS_COMPILE", None)
        metadata["gcc"] = shutil.which("gcc") or "gcc"
    elif toolchain == "llvm":
        add_llvm()
        env["LLVM"] = "1"
        if not row.get("llvm_ias", True):
            triple = row.get("gcc_triple", "")
            if not triple:
                raise ValueError(f"LLVM_IAS=0 row {row['id']} is missing gcc_triple")
            env["LLVM_IAS"] = "0"
            env["CROSS_COMPILE"] = add_gcc(triple)
    elif toolchain == "rust":
        add_llvm()
        rust_cfg = config["rust_toolchain"]
        rust_version = rust_cfg["rust_version"]
        rustup = shutil.which("rustup")
        if not rustup:
            raise FileNotFoundError("rustup was not found; install the rustup package for Rust rows")
        rustup_home = tool_root / "rustup-home"
        cargo_home = tool_root / "cargo-home"
        rust_env = env.copy()
        rust_env.update({"RUSTUP_HOME": str(rustup_home), "CARGO_HOME": str(cargo_home)})
        subprocess.run(
            [
                rustup, "toolchain", "install", rust_version,
                "--profile", "minimal",
                "--component", "rust-src",
                "--component", "rustfmt",
                "--component", "clippy",
            ],
            env=rust_env,
            check=True,
        )
        rustc = find_executable(rustup_home / "toolchains", "rustc")
        rustdoc = find_executable(rustup_home / "toolchains", "rustdoc")
        rustfmt = find_executable(rustup_home / "toolchains", "rustfmt")
        clippy = find_executable(rustup_home / "toolchains", "clippy-driver")
        bindgen_name = rust_cfg.get("bindgen_binary", "bindgen-0.71")
        bindgen_text = shutil.which(bindgen_name)
        if not bindgen_text:
            raise FileNotFoundError(f"{bindgen_name} was not found; install the pinned bindgen package")
        bindgen = Path(bindgen_text)
        rust_sources = sorted(rustup_home.rglob("lib/rustlib/src/rust/library"))
        if not rust_sources:
            raise FileNotFoundError("RUST_LIB_SRC was not installed by rustup")
        path_parts.extend([str(rustc.parent), str(bindgen.parent)])
        env.update(
            {
                "LLVM": "1",
                "RUSTUP_HOME": str(rustup_home),
                "CARGO_HOME": str(cargo_home),
                "RUSTUP_TOOLCHAIN": rust_version,
                "RUSTC": str(rustc),
                "RUSTDOC": str(rustdoc),
                "RUSTFMT": str(rustfmt),
                "CLIPPY_DRIVER": str(clippy),
                "BINDGEN": str(bindgen),
                "RUST_LIB_SRC": str(rust_sources[0]),
            }
        )
        metadata.update(
            {
                "rustup": rustup,
                "rust_version": rust_version,
                "rustc": str(rustc),
                "rustc_version": subprocess.check_output([str(rustc), "--version"], text=True).strip(),
                "bindgen": str(bindgen),
                "bindgen_version": subprocess.check_output([str(bindgen), "--version"], text=True).strip(),
            }
        )
        if not row.get("llvm_ias", True) and row.get("gcc_triple"):
            env["LLVM_IAS"] = "0"
            env["CROSS_COMPILE"] = add_gcc(row["gcc_triple"])
    else:
        raise ValueError(f"unsupported toolchain kind: {toolchain}")

    if path_parts:
        env["PATH"] = os.pathsep.join(dict.fromkeys(path_parts)) + os.pathsep + env["PATH"]
    return metadata


def make_command(source_root: Path, out_root: Path, row: dict[str, Any], *targets: str) -> list[str]:
    command = [
        "make",
        "-C",
        str(source_root),
        f"O={out_root}",
        f"ARCH={row['kbuild_arch']}",
    ]
    command.extend(targets)
    return command


def scripts_config(source_root: Path, out_root: Path, action: str, symbol: str, runner: LoggedRunner, env: dict[str, str]) -> int:
    return runner.run(
        [str(source_root / "scripts/config"), "--file", str(out_root / ".config"), action, symbol],
        env=env,
    )


def config_enabled(config_path: Path, symbol: str) -> bool:
    pattern = re.compile(rf"^CONFIG_{re.escape(symbol)}=(?:y|m)$")
    return any(pattern.match(line) for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines())


def config_y(config_path: Path, symbol: str) -> bool:
    wanted = f"CONFIG_{symbol}=y"
    return wanted in config_path.read_text(encoding="utf-8", errors="replace").splitlines()


def extract_rust_sample_symbols(source_root: Path) -> list[str]:
    symbols: set[str] = set()
    for path in (source_root / "samples/rust").rglob("Kconfig*") if (source_root / "samples/rust").exists() else []:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"\s*(?:menu)?config\s+([A-Z0-9_]+)", line)
            if match:
                symbols.add(match.group(1))
    return sorted(symbols)


def normalize_source(candidate: str, source_root: Path, out_root: Path) -> str | None:
    candidate = candidate.strip("'\"")
    candidate = candidate.replace("\\ ", " ")
    path = Path(candidate)
    possible: list[Path] = []
    if path.is_absolute():
        possible.append(path)
    else:
        possible.extend([source_root / path, out_root / path])
    for item in possible:
        try:
            resolved = item.resolve()
        except OSError:
            continue
        if resolved.is_file() and resolved.suffix in SOURCE_SUFFIXES:
            try:
                return resolved.relative_to(source_root.resolve()).as_posix()
            except ValueError:
                return f"[generated]/{resolved.name}"
    return None


def create_object_map(source_root: Path, out_root: Path, record_dir: Path, row: dict[str, Any]) -> tuple[int, int]:
    mappings: set[tuple[str, str]] = set()
    source_pattern = re.compile(r"(?<![\w./-])([^\s'\";|&()]+\.(?:c|S|s|rs))(?![\w./-])")

    for cmd_path in out_root.rglob("*.cmd"):
        try:
            text = cmd_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        object_candidates = re.findall(r"(?:^|\s)([^\s:=]+\.o)(?:\s|$)", text)
        object_path = object_candidates[0] if object_candidates else cmd_path.stem.lstrip(".")
        for candidate in source_pattern.findall(text):
            normalized = normalize_source(candidate, source_root, out_root)
            if normalized:
                mappings.add((object_path, normalized))

    for obj in out_root.rglob("*.o"):
        rel_obj = obj.relative_to(out_root).as_posix()
        stem = obj.relative_to(out_root).with_suffix("")
        for suffix in SOURCE_SUFFIXES:
            candidate = source_root / (str(stem) + suffix)
            if candidate.is_file():
                mappings.add((rel_obj, candidate.relative_to(source_root).as_posix()))
                break

    tsv = record_dir / "object-source.tsv"
    with tsv.open("w", encoding="utf-8") as handle:
        handle.write("build_id\tarchitecture\tprofile\ttoolchain\tobject\tsource\n")
        for object_path, source_path in sorted(mappings):
            handle.write(
                f"{row['id']}\t{row.get('architecture','')}\t{row['profile']}\t"
                f"{row['toolchain']}\t{object_path}\t{source_path}\n"
            )
    compressed = Path(str(tsv) + ".zst")
    subprocess.run(["zstd", "-q", "-f", "-10", str(tsv), "-o", str(compressed)], check=False)
    if compressed.is_file():
        tsv.unlink(missing_ok=True)
    object_count = sum(1 for _ in out_root.rglob("*.o"))
    return object_count, len({source for _, source in mappings})


def source_inventory(source_root: Path, record_dir: Path) -> int:
    paths = []
    for suffix in SOURCE_SUFFIXES:
        paths.extend(path.relative_to(source_root).as_posix() for path in source_root.rglob(f"*{suffix}") if path.is_file())
    paths = sorted(set(paths))
    inventory = record_dir / "source-inventory.txt"
    inventory.write_text("\n".join(paths) + ("\n" if paths else ""), encoding="utf-8")
    subprocess.run(["zstd", "-q", "-f", "-10", str(inventory), "-o", str(inventory) + ".zst"], check=False)
    return len(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-json", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--record-root", required=True)
    args = parser.parse_args()

    row = json.loads(args.row_json)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    record_dir = Path(args.record_root) / "records" / row["id"]
    record_dir.mkdir(parents=True, exist_ok=True)
    log_path = record_dir / "build.log"
    runner = LoggedRunner(log_path)

    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd()))
    temp_root = Path(os.environ.get("RUNNER_TEMP", workspace / ".tmp")) / f"full-linux-{row['id']}"
    source_root = temp_root / "source"
    tool_root = temp_root / "toolchains"
    out_root = workspace / "out-full-linux" / row["id"]
    shutil.rmtree(temp_root, ignore_errors=True)
    shutil.rmtree(out_root, ignore_errors=True)
    source_root.mkdir(parents=True, exist_ok=True)
    out_root.mkdir(parents=True, exist_ok=True)
    tool_root.mkdir(parents=True, exist_ok=True)

    started = time.time()
    manifest: dict[str, Any] = {
        "schema": 1,
        "build_id": row["id"],
        "kind": row["kind"],
        "architecture": row.get("architecture"),
        "profile": row["profile"],
        "toolchain": row["toolchain"],
        "source_sha": args.source_sha,
        "status": "infrastructure_error",
        "config_target": row["config_target"],
        "targets": row.get("targets", ["all", "modules"]),
        "seed": row.get("seed", ""),
        "adjustments": [],
    }
    exit_code = 1

    try:
        prepare_source(args.repository, args.source_sha, source_root, temp_root)
        env = os.environ.copy()
        env.update(
            {
                "ARCH": row["kbuild_arch"],
                "KBUILD_BUILD_USER": "github-actions",
                "KBUILD_BUILD_HOST": "zigux-full-coverage",
                "KBUILD_BUILD_VERSION": "1",
                "KBUILD_BUILD_TIMESTAMP": "Thu Jan 1 00:00:00 UTC 1970",
                "CCACHE_DISABLE": "1",
            }
        )
        env.pop("CCACHE_DIR", None)
        toolchain_metadata = setup_toolchain(row, config, tool_root, env)
        manifest["toolchain_metadata"] = toolchain_metadata

        runner.run(make_command(source_root, out_root, row, "mrproper"), env=env, check=True)
        config_env = env.copy()
        if row.get("seed"):
            config_env["KCONFIG_SEED"] = str(row["seed"])
            config_env["KCONFIG_PROBABILITY"] = "12"
        runner.run(make_command(source_root, out_root, row, row["config_target"]), env=config_env, check=True)

        adjustments: list[str] = []
        broad_profile = row["profile"] in {"allmodconfig", "allyesconfig"} or row["profile"].startswith("randconfig-")
        if row["kind"] in {"architecture", "llvm"} and broad_profile:
            for symbol in config["baseline_disable"]:
                scripts_config(source_root, out_root, "--disable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=n")

        if row["kind"] == "rust":
            runner.run(make_command(source_root, out_root, row, "rustavailable"), env=env, check=True)
            for symbol in row.get("disable", []):
                scripts_config(source_root, out_root, "--disable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=n")
            for symbol in row.get("enable", ["RUST", "MODULES"]):
                scripts_config(source_root, out_root, "--enable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=y")
            for symbol in extract_rust_sample_symbols(source_root):
                scripts_config(source_root, out_root, "--enable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=y(requested)")

        if row["kind"] == "hardening":
            for symbol in row.get("disable", []):
                scripts_config(source_root, out_root, "--disable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=n")
            for symbol in row.get("enable", []):
                scripts_config(source_root, out_root, "--enable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=y(requested)")

        runner.run(make_command(source_root, out_root, row, "olddefconfig"), env=env, check=True)
        config_path = out_root / ".config"
        if not config_path.is_file():
            raise RuntimeError("Kconfig did not produce .config")

        if row["kind"] == "rust" and not config_y(config_path, "RUST"):
            raise RuntimeError("CONFIG_RUST=y was requested but Kconfig did not enable it")
        if row["kind"] == "hardening":
            unavailable = [symbol for symbol in row.get("enable", []) if not config_enabled(config_path, symbol)]
            if unavailable:
                raise RuntimeError(f"requested hardening symbols were not enabled: {', '.join(unavailable)}")

        shutil.copy2(config_path, record_dir / "kernel.config")
        manifest["adjustments"] = adjustments
        manifest["config_sha256"] = sha256_file(config_path)
        manifest["configured_module_symbols"] = sum(
            1 for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.endswith("=m")
        )

        targets = list(row.get("targets", ["all", "modules"]))
        if row["kind"] == "dtbs":
            dry_rc = runner.run(make_command(source_root, out_root, row, "-n", "dtbs"), env=env)
            if dry_rc != 0 and row.get("allow_not_applicable"):
                manifest["status"] = "not_applicable"
                manifest["reason"] = "architecture does not expose a usable dtbs target for this configuration"
                exit_code = 0
            else:
                build_rc = runner.run(
                    make_command(source_root, out_root, row, "-k", f"-j{os.cpu_count() or 2}", *targets),
                    env=env,
                )
                manifest["build_exit_code"] = build_rc
                manifest["status"] = "success" if build_rc == 0 else "build_failed"
                exit_code = build_rc
        else:
            build_rc = runner.run(
                make_command(source_root, out_root, row, "-k", f"-j{os.cpu_count() or 2}", *targets),
                env=env,
            )
            manifest["build_exit_code"] = build_rc
            manifest["status"] = "success" if build_rc == 0 else "build_failed"
            exit_code = build_rc

        object_count, mapped_sources = create_object_map(source_root, out_root, record_dir, row)
        manifest["object_count"] = object_count
        manifest["mapped_source_count"] = mapped_sources
        manifest["module_count"] = sum(1 for _ in out_root.rglob("*.ko"))
        manifest["device_tree_blob_count"] = sum(1 for _ in out_root.rglob("*.dtb"))
        output_files = sorted(
            path.relative_to(out_root).as_posix()
            for path in out_root.rglob("*")
            if path.is_file() and path.suffix in {".ko", ".dtb", ".dtbo"}
        )
        (record_dir / "selected-outputs.txt").write_text(
            "\n".join(output_files) + ("\n" if output_files else ""), encoding="utf-8"
        )
    except Exception as exc:
        manifest["status"] = "infrastructure_error"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\nFATAL: {manifest['error']}\n")
        print(f"::error::{row['id']}: {manifest['error']}", file=sys.stderr)
        exit_code = 1
    finally:
        manifest["elapsed_seconds"] = round(time.time() - started, 3)
        manifest["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        compact_log(log_path)
        (record_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (record_dir / "row.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({key: manifest.get(key) for key in ("build_id", "status", "object_count", "mapped_source_count")}, sort_keys=True))

    return int(exit_code != 0)


if __name__ == "__main__":
    raise SystemExit(main())
