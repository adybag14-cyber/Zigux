#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

CHECKS = (
    ("include/zigux/abi.h", re.compile(r"^#define\s+(ZIGUX_[A-Z0-9_]+)\b"), "macro"),
    ("include/zigux/abi.h", re.compile(r"^struct\s+(zigux_[a-z0-9_]+)\s*\{"), "struct"),
    ("zigux/bindings/abi.zig", re.compile(r"^pub const\s+([A-Z0-9_]+)\s*:"), "binding-constant"),
    ("zigux/bindings/abi.zig", re.compile(r"^pub const\s+([A-Za-z0-9_]+)\s*=\s*extern struct\b"), "binding-extern-struct"),
)


def _scan_duplicates(path: Path, pattern: re.Pattern[str], kind: str) -> list[str]:
    declarations: dict[str, list[int]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = pattern.match(line)
        if match is None:
            continue
        declarations.setdefault(match.group(1), []).append(line_no)
    issues: list[str] = []
    for name, line_numbers in declarations.items():
        if len(line_numbers) > 1:
            rendered = ",".join(str(line_no) for line_no in line_numbers)
            issues.append(
                f"duplicate_abi_declaration:{kind}:{path.relative_to(path.parents[2]).as_posix()}:{rendered}:{name}"
            )
    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel, pattern, kind in CHECKS:
        path = root / rel
        if not path.exists():
            issues.append(f"missing_source_file:{rel}")
            continue
        issues.extend(_scan_duplicates(path, pattern, kind))
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_duplicate_decl_") as tmp_dir:
        root = Path(tmp_dir)
        (root / "include/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/bindings").mkdir(parents=True, exist_ok=True)

        (root / "include/zigux/abi.h").write_text(
            "#define ZIGUX_ABI_VERSION 1U\n"
            "#define ZIGUX_STATUS_FLAG_ERROR 1U\n"
            "struct zigux_boundary_header {\n\tunsigned size;\n};\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux/bindings/abi.zig").write_text(
            "pub const ABI_VERSION: u16 = 1;\n"
            "pub const STATUS_FLAG_ERROR: u16 = 1;\n"
            "pub const BoundaryHeader = extern struct {\n"
            "    size: u32,\n"
            "};\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == []

        (root / "include/zigux/abi.h").write_text(
            (root / "include/zigux/abi.h").read_text(encoding="utf-8") + "#define ZIGUX_STATUS_FLAG_ERROR 1U\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert issues == [
            "duplicate_abi_declaration:macro:include/zigux/abi.h:2,6:ZIGUX_STATUS_FLAG_ERROR"
        ], issues

        (root / "include/zigux/abi.h").write_text(
            "#define ZIGUX_ABI_VERSION 1U\n"
            "struct zigux_boundary_header {\n\tunsigned size;\n};\n"
            "struct zigux_boundary_header {\n\tunsigned size;\n};\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux/bindings/abi.zig").write_text(
            "pub const ABI_VERSION: u16 = 1;\n"
            "pub const ABI_VERSION: u16 = 1;\n"
            "pub const BoundaryHeader = extern struct {\n    size: u32,\n};\n"
            "pub const BoundaryHeader = extern struct {\n    size: u32,\n};\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert issues == [
            "duplicate_abi_declaration:struct:include/zigux/abi.h:2,5:zigux_boundary_header",
            "duplicate_abi_declaration:binding-constant:zigux/bindings/abi.zig:1,2:ABI_VERSION",
            "duplicate_abi_declaration:binding-extern-struct:zigux/bindings/abi.zig:3,6:BoundaryHeader",
        ], issues

    print("PHASE3_ABI_DUPLICATE_DECLARATIONS_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect duplicate ABI declarations in the Phase 3 shared header and Zig bindings.")
    parser.add_argument("--self-test", action="store_true", help="run isolated checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_ABI_DUPLICATE_DECLARATIONS=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_ABI_DUPLICATE_DECLARATIONS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
