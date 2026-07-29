#!/usr/bin/env python3
"""Generate bounded GitHub Actions matrices for the full Linux coverage campaign."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def slug(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value).strip("-")


def matrix(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        raise ValueError(f"duplicate matrix ids: {duplicates}")
    return {"include": rows}


def emit(name: str, value: Any, output_path: Path | None) -> None:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
    if output_path:
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={encoded}\n")
    else:
        print(f"{name}={encoded}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--scope",
        choices=["full", "smoke", "architecture", "llvm", "rust", "hardening", "dtbs", "auxiliary"],
        default="full",
    )
    parser.add_argument("--rand-seeds", default="0xC0FFEE,0x5EED")
    parser.add_argument("--plan-output")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    arch_by_id = {item["id"]: item for item in config["architectures"]}
    seeds = [seed.strip() for seed in args.rand_seeds.split(",") if seed.strip()]
    if not seeds:
        raise ValueError("at least one deterministic randconfig seed is required")
    for seed in seeds:
        int(seed, 0)

    architecture_rows: list[dict[str, Any]] = []
    architecture_profiles = ["defconfig", "allmodconfig", "allyesconfig"]
    architecture_profiles.extend(f"randconfig-{seed}" for seed in seeds)
    for arch in config["architectures"]:
        for profile in architecture_profiles:
            if profile == "defconfig":
                config_target = arch["config_target"]
                seed = ""
            elif profile.startswith("randconfig-"):
                config_target = "randconfig"
                seed = profile.split("-", 1)[1]
            else:
                config_target = profile
                seed = ""
            architecture_rows.append(
                {
                    "id": f"arch-{arch['id']}-{slug(profile)}",
                    "kind": "architecture",
                    "architecture": arch["id"],
                    "label": arch["label"],
                    "kbuild_arch": arch["kbuild_arch"],
                    "profile": profile,
                    "config_target": config_target,
                    "toolchain": arch["preferred_toolchain"],
                    "gcc_triple": arch.get("gcc_triple", ""),
                    "llvm_ias": arch.get("llvm_ias", True),
                    "seed": seed,
                    "targets": ["all", "modules"],
                    "extra_packages": [],
                }
            )

    llvm_rows: list[dict[str, Any]] = []
    for arch in config["architectures"]:
        if not arch.get("llvm_supported"):
            continue
        for profile in ("defconfig", "allmodconfig"):
            llvm_rows.append(
                {
                    "id": f"llvm-{arch['id']}-{profile}",
                    "kind": "llvm",
                    "architecture": arch["id"],
                    "label": arch["label"],
                    "kbuild_arch": arch["kbuild_arch"],
                    "profile": profile,
                    "config_target": arch["config_target"] if profile == "defconfig" else "allmodconfig",
                    "toolchain": "llvm",
                    "gcc_triple": arch.get("gcc_triple", ""),
                    "llvm_ias": arch.get("llvm_ias", True),
                    "seed": "",
                    "targets": ["all", "modules"],
                    "extra_packages": [],
                }
            )

    rust_rows: list[dict[str, Any]] = []
    for arch in config["architectures"]:
        if not arch.get("rust_supported"):
            continue
        rust_rows.append(
            {
                "id": f"rust-{arch['id']}",
                "kind": "rust",
                "architecture": arch["id"],
                "label": arch["label"],
                "kbuild_arch": arch["kbuild_arch"],
                "profile": "rust-enabled",
                "config_target": arch["config_target"],
                "toolchain": "rust",
                "gcc_triple": arch.get("gcc_triple", ""),
                "llvm_ias": arch.get("llvm_ias", True),
                "seed": "",
                "targets": ["all", "modules"],
                "enable": ["RUST", "MODULES"],
                "disable": arch.get("rust_disable", []),
                "extra_packages": ["bindgen-0.71", "rustup"],
            }
        )

    hardening_rows: list[dict[str, Any]] = []
    for profile in config["hardening_profiles"]:
        arch = arch_by_id[profile["architecture"]]
        row = dict(profile)
        row.update(
            {
                "kind": "hardening",
                "profile": profile["id"],
                "kbuild_arch": arch["kbuild_arch"],
                "gcc_triple": arch.get("gcc_triple", ""),
                "llvm_ias": arch.get("llvm_ias", True),
                "seed": "",
                "targets": ["all", "modules"],
            }
        )
        hardening_rows.append(row)

    dtbs_rows: list[dict[str, Any]] = []
    for arch in config["architectures"]:
        dtbs_rows.append(
            {
                "id": f"dtbs-{arch['id']}",
                "kind": "dtbs",
                "architecture": arch["id"],
                "label": f"{arch['label']} device trees",
                "kbuild_arch": arch["kbuild_arch"],
                "profile": "dtbs",
                "config_target": arch["config_target"],
                "toolchain": arch["preferred_toolchain"],
                "gcc_triple": arch.get("gcc_triple", ""),
                "llvm_ias": arch.get("llvm_ias", True),
                "seed": "",
                "targets": ["dtbs"],
                "allow_not_applicable": True,
                "extra_packages": ["u-boot-tools"],
            }
        )

    auxiliary_rows = []
    for task in config["auxiliary_tasks"]:
        row = dict(task)
        row.update({"kind": "auxiliary", "profile": task["task"]})
        auxiliary_rows.append(row)

    if args.scope == "smoke":
        architecture_rows = [
            row for row in architecture_rows
            if row["architecture"] in {"x86", "arm64", "riscv"} and row["profile"] == "defconfig"
        ]
        llvm_rows = [row for row in llvm_rows if row["architecture"] == "x86" and row["profile"] == "defconfig"]
        rust_rows = [row for row in rust_rows if row["architecture"] == "x86"]
        hardening_rows = [row for row in hardening_rows if row["id"] == "gcc-randstruct"]
        dtbs_rows = [row for row in dtbs_rows if row["architecture"] in {"arm64", "riscv"}]
        auxiliary_rows = [row for row in auxiliary_rows if row["id"] in {"headers", "objtool"}]
    elif args.scope != "full":
        architecture_rows = architecture_rows if args.scope == "architecture" else []
        llvm_rows = llvm_rows if args.scope == "llvm" else []
        rust_rows = rust_rows if args.scope == "rust" else []
        hardening_rows = hardening_rows if args.scope == "hardening" else []
        dtbs_rows = dtbs_rows if args.scope == "dtbs" else []
        auxiliary_rows = auxiliary_rows if args.scope == "auxiliary" else []

    groups = {
        "architecture": architecture_rows,
        "llvm": llvm_rows,
        "rust": rust_rows,
        "hardening": hardening_rows,
        "dtbs": dtbs_rows,
        "auxiliary": auxiliary_rows,
    }
    output_path = Path(os.environ["GITHUB_OUTPUT"]) if os.environ.get("GITHUB_OUTPUT") else None
    for name, rows in groups.items():
        emit(f"{name}_matrix", matrix(rows), output_path)
        emit(f"{name}_count", len(rows), output_path)

    plan = {
        "schema": 1,
        "scope": args.scope,
        "rand_seeds": seeds,
        "groups": groups,
        "counts": {name: len(rows) for name, rows in groups.items()},
        "total_jobs": sum(len(rows) for rows in groups.values()),
    }
    if args.plan_output:
        Path(args.plan_output).write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(plan["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
