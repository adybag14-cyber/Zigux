#!/usr/bin/env python3
"""Validate the current bounded Phase 3 shared ABI binding surface."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")

REQUIRED_SOURCE_MARKERS = {
    ABI_HEADER_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_FACILITY_KERNEL 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_boundary_header {",
        "struct zigux_interop_policy {",
        "struct zigux_notifier_block {",
    ),
    ABI_BINDINGS_PATH: (
        "pub const ABI_VERSION: u16 = 1;",
        "pub const FACILITY_KERNEL: u16 = 1;",
        "pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;",
        "pub const BoundaryHeader = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub const NotifierBlock = notifier_abi.NotifierBlock;",
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _abi_header_constant_names(text: str) -> set[str]:
    return set(
        re.findall(r"^\s*#define\s+ZIGUX_([A-Z0-9_]+)\b", text, flags=re.MULTILINE)
    )


def _abi_binding_constant_names(text: str) -> set[str]:
    return set(
        re.findall(r"^\s*pub const\s+([A-Z0-9_]+)\s*:", text, flags=re.MULTILINE)
    )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}

    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        texts[rel_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    header_text = texts.get(ABI_HEADER_PATH)
    bindings_text = texts.get(ABI_BINDINGS_PATH)
    if header_text is not None and bindings_text is not None:
        missing_binding_constants = sorted(
            _abi_header_constant_names(header_text).difference(
                _abi_binding_constant_names(bindings_text)
            )
        )
        for name in missing_binding_constants:
            issues.append(
                "missing ABI binding constant for header define: "
                f"ZIGUX_{name} -> {name}"
            )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_") as tmp_dir:
        root = Path(tmp_dir)

        _write(
            root / ABI_HEADER_PATH,
            "\n".join(REQUIRED_SOURCE_MARKERS[ABI_HEADER_PATH]) + "\n",
        )
        _write(
            root / ABI_BINDINGS_PATH,
            "\n".join(REQUIRED_SOURCE_MARKERS[ABI_BINDINGS_PATH]) + "\n",
        )

        issues = validate_repo(root)
        if issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        _write(
            root / ABI_BINDINGS_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_SOURCE_MARKERS[ABI_BINDINGS_PATH]
                if marker != "pub const ABI_VERSION: u16 = 1;"
            )
            + "\n",
        )
        issues = validate_repo(root)
        expected = (
            "missing ABI binding constant for header define: "
            "ZIGUX_ABI_VERSION -> ABI_VERSION"
        )
        if expected not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected missing ABI binding constant was not reported")
            return 1

    print("PHASE3_VALIDATION_SELF_TEST=pass")
    print("PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 shared ABI binding surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains include/zigux/ and zigux/bindings/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_VALIDATION=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_VALIDATION=pass")
    print("PHASE3_SCOPE=shared-abi-binding-constants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
