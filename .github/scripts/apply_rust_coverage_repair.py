#!/usr/bin/env python3
"""Apply the reviewed Rust coverage repair to production files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".github/config/full-linux-coverage.json"
SCRIPT_PATH = ROOT / ".github/scripts/kernel_coverage.py"
TEST_PATH = ROOT / ".github/scripts/test_full_linux_coverage.py"
DOCS_PATH = ROOT / "docs/FULL-LINUX-COVERAGE.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["rust_llvm_toolchain"] = {
        "version": "20.1.8",
        "archive": "llvm-20.1.8-x86_64.tar.xz",
        "base_url": "https://www.kernel.org/pub/tools/llvm/files",
    }
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    text = SCRIPT_PATH.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    def add_llvm() -> Path:\n        cfg = config["llvm_toolchain"]\n',
        '    def add_llvm(toolchain_key: str = "llvm_toolchain") -> Path:\n        cfg = config[toolchain_key]\n',
        "add_llvm definition",
    )
    text = replace_once(
        text,
        '    elif toolchain == "rust":\n        add_llvm()\n',
        '    elif toolchain == "rust":\n        add_llvm("rust_llvm_toolchain")\n',
        "Rust LLVM selection",
    )

    marker = '''def config_y(config_path: Path, symbol: str) -> bool:
    wanted = f"CONFIG_{symbol}=y"
    return wanted in config_path.read_text(encoding="utf-8", errors="replace").splitlines()


'''
    helpers = marker + '''RUST_KCONFIG_SYMBOLS = (
    "HAVE_RUST",
    "RUST_IS_AVAILABLE",
    "RUST",
    "MODVERSIONS",
    "GENDWARFKSYMS",
    "GCC_PLUGINS",
    "GCC_PLUGIN_RANDSTRUCT",
    "RANDSTRUCT",
    "RANDSTRUCT_FULL",
    "RANDSTRUCT_PERFORMANCE",
    "DEBUG_INFO_BTF",
    "PAHOLE_HAS_LANG_EXCLUDE",
    "LTO",
    "LTO_CLANG",
    "LTO_CLANG_THIN",
    "LTO_CLANG_FULL",
    "CFI",
    "HAVE_CFI_ICALL_NORMALIZE_INTEGERS_RUSTC",
    "KASAN",
    "CC_IS_CLANG",
    "KASAN_SW_TAGS",
    "EXPOLINE",
    "WERROR",
)


def config_state(config_path: Path, symbol: str) -> str:
    if not config_path.is_file():
        return "missing-config"
    enabled = f"CONFIG_{symbol}="
    disabled = f"# CONFIG_{symbol} is not set"
    for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(enabled):
            return line.split("=", 1)[1]
        if line == disabled:
            return "n"
    return "absent"


def write_rust_kconfig_diagnostics(config_path: Path, record_dir: Path, phase: str) -> dict[str, str]:
    states = {symbol: config_state(config_path, symbol) for symbol in RUST_KCONFIG_SYMBOLS}
    payload = {"phase": phase, "symbols": states}
    (record_dir / f"rust-kconfig-{phase}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
    )
    return states


'''
    text = replace_once(text, marker, helpers, "Rust Kconfig diagnostics helpers")

    old_rust = '''        if row["kind"] == "rust":
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
'''
    new_rust = '''        rust_sample_symbols: list[str] = []
        if row["kind"] == "rust":
            # Settle blockers before requesting RUST. A single Kconfig pass may
            # otherwise discard RUST before architecture-derived HAVE_RUST updates.
            rust_blockers = [
                "WERROR",
                "MODVERSIONS",
                "GCC_PLUGINS",
                "GCC_PLUGIN_RANDSTRUCT",
                "RANDSTRUCT_FULL",
                "RANDSTRUCT_PERFORMANCE",
                "DEBUG_INFO_BTF",
                "LTO",
                "LTO_CLANG",
                "LTO_CLANG_THIN",
                "LTO_CLANG_FULL",
                "CFI",
                "KASAN",
                "KASAN_SW_TAGS",
            ]
            for symbol in dict.fromkeys([*rust_blockers, *row.get("disable", [])]):
                scripts_config(source_root, out_root, "--disable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=n")

            runner.run(make_command(source_root, out_root, row, "olddefconfig"), env=env, check=True)
            runner.run(make_command(source_root, out_root, row, "rustavailable"), env=env, check=True)
            runner.run(make_command(source_root, out_root, row, "olddefconfig"), env=env, check=True)

            config_path = out_root / ".config"
            before = write_rust_kconfig_diagnostics(config_path, record_dir, "before-enable")
            manifest["rust_kconfig_before_enable"] = before
            missing_prerequisites = [
                symbol for symbol in ("HAVE_RUST", "RUST_IS_AVAILABLE") if before.get(symbol) != "y"
            ]
            if missing_prerequisites:
                raise RuntimeError(
                    "Rust architecture prerequisites unavailable after Kconfig reconciliation: "
                    + ", ".join(
                        f"CONFIG_{symbol}={before.get(symbol)}" for symbol in missing_prerequisites
                    )
                )

            for symbol in row.get("enable", ["RUST", "MODULES"]):
                scripts_config(source_root, out_root, "--enable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=y")
            runner.run(make_command(source_root, out_root, row, "olddefconfig"), env=env, check=True)

            enabled = write_rust_kconfig_diagnostics(config_path, record_dir, "after-enable")
            manifest["rust_kconfig_after_enable"] = enabled
            if enabled.get("RUST") != "y":
                raise RuntimeError(
                    "CONFIG_RUST=y was rejected after two-phase Kconfig reconciliation; "
                    f"diagnostic symbols: {json.dumps(enabled, sort_keys=True)}"
                )

            rust_sample_symbols = extract_rust_sample_symbols(source_root)
            manifest["rust_sample_symbols_requested"] = rust_sample_symbols
            for symbol in rust_sample_symbols:
                scripts_config(source_root, out_root, "--enable", symbol, runner, env)
                adjustments.append(f"CONFIG_{symbol}=y(requested)")
'''
    text = replace_once(text, old_rust, new_rust, "two-phase Rust Kconfig block")

    text = replace_once(
        text,
        '''        if row["kind"] == "rust" and not config_y(config_path, "RUST"):
            raise RuntimeError("CONFIG_RUST=y was requested but Kconfig did not enable it")
''',
        '''        if row["kind"] == "rust":
            final_rust_state = write_rust_kconfig_diagnostics(config_path, record_dir, "final")
            manifest["rust_kconfig_final"] = final_rust_state
            manifest["rust_sample_symbols_enabled"] = [
                symbol for symbol in rust_sample_symbols if config_y(config_path, symbol)
            ]
            if final_rust_state.get("RUST") != "y":
                raise RuntimeError(
                    "CONFIG_RUST=y was lost during final Kconfig reconciliation; "
                    f"see {record_dir / 'rust-kconfig-final.json'}"
                )
''',
        "final Rust validation",
    )

    text = replace_once(
        text,
        '''    finally:
        manifest["elapsed_seconds"] = round(time.time() - started, 3)
        manifest["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        compact_log(log_path)
''',
        '''    finally:
        config_path = out_root / ".config"
        if config_path.is_file():
            shutil.copy2(config_path, record_dir / "kernel.config")
            if row["kind"] == "rust":
                manifest.setdefault(
                    "rust_kconfig_final",
                    write_rust_kconfig_diagnostics(config_path, record_dir, "failure-or-final"),
                )
        if row["kind"] == "rust":
            generated_bindings = out_root / "rust/bindings/bindings_generated.rs"
            if generated_bindings.is_file():
                bindings_copy = record_dir / "bindings-generated.rs"
                shutil.copy2(generated_bindings, bindings_copy)
                subprocess.run(
                    ["zstd", "-q", "-f", "-10", str(bindings_copy), "-o", str(bindings_copy) + ".zst"],
                    check=False,
                )
                if Path(str(bindings_copy) + ".zst").is_file():
                    bindings_copy.unlink(missing_ok=True)
        manifest["elapsed_seconds"] = round(time.time() - started, 3)
        manifest["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        compact_log(log_path)
''',
        "failure preservation",
    )
    SCRIPT_PATH.write_text(text, encoding="utf-8")

    tests = TEST_PATH.read_text(encoding="utf-8")
    tests = replace_once(
        tests,
        '    assert config["rust_toolchain"]["bindgen_version"] == "0.71.1"\n',
        '    assert config["rust_toolchain"]["bindgen_version"] == "0.71.1"\n'
        '    assert config["rust_llvm_toolchain"]["version"] == "20.1.8"\n'
        '    assert config["rust_llvm_toolchain"]["archive"] == "llvm-20.1.8-x86_64.tar.xz"\n',
        "Rust LLVM assertions",
    )
    tests = replace_once(
        tests,
        '    assert \'f"={bindgen_version}"\' in kernel_source\n',
        '    assert \'f"={bindgen_version}"\' in kernel_source\n'
        '    assert \'add_llvm("rust_llvm_toolchain")\' in kernel_source\n'
        '    assert \'rust-kconfig-{phase}.json\' in kernel_source\n'
        '    assert \'Rust architecture prerequisites unavailable after Kconfig reconciliation\' in kernel_source\n'
        '    assert \'bindings-generated.rs\' in kernel_source\n',
        "Rust script assertions",
    )
    TEST_PATH.write_text(tests, encoding="utf-8")

    docs = DOCS_PATH.read_text(encoding="utf-8")
    section = '''
## Rust coverage reliability

Rust coverage uses a dedicated pinned LLVM/libclang toolchain rather than the newest LLVM compatibility matrix. Each row settles architecture and hardening Kconfig prerequisites before requesting `CONFIG_RUST=y`, records dependency states, preserves the final `.config`, and archives generated bindings on failure. All seven supported Rust architecture rows are live-tested before changes are merged.
'''
    if "## Rust coverage reliability" not in docs:
        DOCS_PATH.write_text(docs + section, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
