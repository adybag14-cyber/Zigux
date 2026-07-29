#!/usr/bin/env python3
"""Fast offline validation for the full Linux source-coverage infrastructure."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".github/scripts"
sys.path.insert(0, str(SCRIPTS))

from kernel_coverage import compact_log, create_object_map, safe_extract  # noqa: E402

EXPECTED_ARCHITECTURES = {
    "alpha", "arc", "arm", "arm64", "csky", "hexagon", "loongarch", "m68k",
    "microblaze", "mips", "nios2", "openrisc", "parisc", "powerpc", "riscv",
    "s390", "sh", "sparc", "um", "x86", "xtensa",
}
EXPECTED_LLVM = {"arm", "arm64", "hexagon", "loongarch", "mips", "powerpc", "riscv", "s390", "sparc", "um", "x86"}
EXPECTED_RUST = {"arm", "arm64", "loongarch", "riscv", "s390", "um", "x86"}
EXPECTED_FULL_COUNTS = {
    "architecture": 105,
    "llvm": 22,
    "rust": 7,
    "hardening": 13,
    "dtbs": 21,
    "auxiliary": 11,
}


def generate_plan(scope: str, output: Path) -> dict:
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "full_linux_matrix.py"),
            "--config", str(ROOT / ".github/config/full-linux-coverage.json"),
            "--scope", scope,
            "--rand-seeds", "0xC0FFEE,0x5EED",
            "--plan-output", str(output),
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(output.read_text(encoding="utf-8"))


def test_config_and_matrices(temp: Path) -> None:
    config = json.loads((ROOT / ".github/config/full-linux-coverage.json").read_text(encoding="utf-8"))
    architectures = config["architectures"]
    ids = {item["id"] for item in architectures}
    assert ids == EXPECTED_ARCHITECTURES, (ids - EXPECTED_ARCHITECTURES, EXPECTED_ARCHITECTURES - ids)
    assert len(ids) == len(architectures), "architecture IDs must be unique"
    assert {item["id"] for item in architectures if item["llvm_supported"]} == EXPECTED_LLVM
    assert {item["id"] for item in architectures if item["rust_supported"]} == EXPECTED_RUST
    assert len({item["id"] for item in config["hardening_profiles"]}) == 13
    assert len({item["id"] for item in config["auxiliary_tasks"]}) == 11
    assert config["rust_toolchain"]["rust_version"] == "1.96.1"
    assert config["rust_toolchain"]["bindgen_crate"] == "bindgen-cli"
    assert config["rust_toolchain"]["bindgen_version"] == "0.71.1"
    assert config["capstone_toolchain"]["tag"] == "5.0.6"
    assert config["capstone_toolchain"]["commit"] == "accf4df62f1fba6f92cae692985d27063552601c"

    full = generate_plan("full", temp / "full.json")
    assert full["counts"] == EXPECTED_FULL_COUNTS
    assert full["total_jobs"] == 179
    for row in full["groups"]["rust"]:
        assert "rustup" in row["extra_packages"]
        assert "bindgen-0.71" not in row["extra_packages"]
    for row in full["groups"]["auxiliary"]:
        if row.get("toolchain") == "rust":
            assert "rustup" in row["extra_packages"]
        assert "bindgen-0.71" not in row["extra_packages"]
    auxiliary_by_id = {row["id"]: row for row in full["groups"]["auxiliary"]}
    perf = auxiliary_by_id["perf"]
    assert {"libtraceevent-dev", "libtracefs-dev", "libpfm4-dev", "libbabeltrace2-dev"}.issubset(perf["extra_packages"])
    assert "libcapstone-dev" not in perf["extra_packages"]
    assert {"libasound2-dev", "libcap-ng-dev"}.issubset(auxiliary_by_id["selftests"]["extra_packages"])
    assert "llvm" in auxiliary_by_id["bpftool"]["extra_packages"]
    all_ids = [row["id"] for rows in full["groups"].values() for row in rows]
    assert len(all_ids) == len(set(all_ids))

    smoke = generate_plan("smoke", temp / "smoke.json")
    assert smoke["total_jobs"] == 10
    dtbs = generate_plan("dtbs", temp / "dtbs.json")
    assert dtbs["counts"]["dtbs"] == 21 and dtbs["counts"]["auxiliary"] == 0
    auxiliary = generate_plan("auxiliary", temp / "auxiliary.json")
    assert auxiliary["counts"]["auxiliary"] == 11 and auxiliary["counts"]["dtbs"] == 0
    auxiliary_source = (ROOT / ".github/scripts/auxiliary_coverage.py").read_text(encoding="utf-8")
    assert 'mapping_root.mkdir(parents=True, exist_ok=True)' in auxiliary_source
    assert '"--kunitconfig"' in auxiliary_source
    assert 'make_command(source_root, out_root, {"kbuild_arch": "x86"}, "headers")' in auxiliary_source
    assert 'f"O={out_root}"' in auxiliary_source
    assert 'FORCE_TARGETS=1' not in auxiliary_source
    assert 'capstone_commit != capstone_cfg["commit"]' in auxiliary_source
    assert '"pkg-config", "--modversion", "capstone"' in auxiliary_source
    kernel_source = (ROOT / ".github/scripts/kernel_coverage.py").read_text(encoding="utf-8")
    assert '"install",\n                bindgen_crate' in kernel_source
    assert 'f"={bindgen_version}"' in kernel_source


def test_object_mapping_and_log_compaction(temp: Path) -> None:
    source = temp / "source"
    output = temp / "output"
    record = temp / "record"
    (source / "drivers/demo").mkdir(parents=True)
    (output / "drivers/demo").mkdir(parents=True)
    record.mkdir()
    source_file = source / "drivers/demo/example.c"
    source_file.write_text("int example(void) { return 0; }\n", encoding="utf-8")
    (output / "drivers/demo/example.o").write_bytes(b"object")
    (output / "drivers/demo/.example.o.cmd").write_text(
        f"cmd_drivers/demo/example.o := gcc -c {source_file} -o drivers/demo/example.o\n",
        encoding="utf-8",
    )
    objects, sources = create_object_map(
        source,
        output,
        record,
        {"id": "test-row", "architecture": "x86", "profile": "defconfig", "toolchain": "native-gcc"},
    )
    assert objects == 1 and sources == 1
    mapped = subprocess.check_output(["zstd", "-q", "-dc", str(record / "object-source.tsv.zst")], text=True)
    assert "drivers/demo/example.c" in mapped

    log = record / "build.log"
    log.write_bytes(b"header\n" + b"x" * 3_000_000 + b"\ntail\n")
    compact_log(log, max_bytes=100_000)
    assert not log.exists()
    excerpt = (record / "build-log-excerpt.txt").read_bytes()
    assert b"bytes omitted" in excerpt and b"header" in excerpt and b"tail" in excerpt
    assert len(excerpt) < 101_000


def test_safe_archive_extraction(temp: Path) -> None:
    archive = temp / "unsafe.tar"
    info = tarfile.TarInfo("root/../../escape")
    payload = b"bad"
    info.size = len(payload)
    with tarfile.open(archive, "w") as tar:
        tar.addfile(info, io.BytesIO(payload))
    with tarfile.open(archive, "r") as tar:
        try:
            safe_extract(tar, temp / "extract", strip_first_component=True)
        except RuntimeError:
            pass
        else:
            raise AssertionError("path-traversal archive was not rejected")


def test_aggregate_report(temp: Path) -> None:
    source = temp / "aggregate-source"
    records = temp / "aggregate-records/records/test"
    report = temp / "aggregate-report"
    (source / "drivers").mkdir(parents=True)
    (source / "rust").mkdir(parents=True)
    (source / "drivers/a.c").write_text("int a;\n", encoding="utf-8")
    (source / "rust/b.rs").write_text("pub static B: i32 = 1;\n", encoding="utf-8")
    records.mkdir(parents=True)
    (records / "manifest.json").write_text(
        json.dumps({
            "build_id": "test", "kind": "architecture", "architecture": "x86",
            "profile": "defconfig", "toolchain": "native-gcc", "status": "success",
            "object_count": 1, "mapped_source_count": 1,
        }),
        encoding="utf-8",
    )
    mapping = records / "object-source.tsv"
    mapping.write_text(
        "build_id\tarchitecture\tprofile\ttoolchain\tobject\tsource\n"
        "test\tx86\tdefconfig\tnative-gcc\tdrivers/a.o\tdrivers/a.c\n",
        encoding="utf-8",
    )
    subprocess.run(["zstd", "-q", "-f", str(mapping), "-o", str(mapping) + ".zst"], check=True)
    mapping.unlink()
    subprocess.run(
        [
            sys.executable, str(SCRIPTS / "aggregate_linux_coverage.py"),
            "--records-root", str(temp / "aggregate-records"),
            "--repository", "example/example",
            "--source-sha", "0" * 40,
            "--source-root", str(source),
            "--output", str(report),
        ],
        check=True,
    )
    summary = json.loads((report / "summary.json").read_text(encoding="utf-8"))
    assert summary["source_file_count"] == 2
    assert summary["observed_compiled_source_count"] == 1
    assert summary["observed_source_coverage_percent"] == 50.0
    assert (report / "source-to-object.tsv.zst").is_file()
    assert (report / "source-coverage-summary.tsv.zst").is_file()
    assert (report / "uncompiled-sources.tsv.zst").is_file()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="full-linux-coverage-tests-") as directory:
        temp = Path(directory)
        test_config_and_matrices(temp)
        test_object_mapping_and_log_compaction(temp)
        test_safe_archive_extraction(temp)
        test_aggregate_report(temp)
    print("full Linux coverage infrastructure tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
