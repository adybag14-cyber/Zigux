#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ABI_HEADER = ROOT / "include" / "zigux" / "abi.h"
DEFAULT_ABI_BINDINGS = ROOT / "zigux" / "bindings" / "abi.zig"
DEFAULT_DEV_T_BINDINGS = ROOT / "zigux" / "bindings" / "dev_t.zig"
DEFAULT_NOTIFIER_BINDINGS = ROOT / "zigux" / "bindings" / "notifier_abi.zig"
DEFAULT_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi_manifest.json"
DEFAULT_DOC = ROOT / "Documentation" / "zigux" / "phase3-abi-slice.md"
FUSED_MARKER = ";pub const "
HEADER_FUSED_MARKERS = (
    "};#define ",
    "};struct ",
    "};typedef ",
    ";#define ",
)
REQUIRED_MANIFEST_FILES = (
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
)
REQUIRED_DOC_MARKERS = (
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
    "python3 scripts/zigux/survey-phase3-abi-constant-parity.py",
    "python3 scripts/zigux/survey-phase3-abi-constant-parity.py --self-test",
)
REQUIRED_BINDINGS_DOC_MARKERS = (
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
)
REQUIRED_EXPORT_UAPI_DOC_MARKERS = (
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
    "PHASE3_ABI_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof",
)


def find_fused_pub_const_lines(source: str) -> list[int]:
    return [index for index, line in enumerate(source.splitlines(), start=1) if FUSED_MARKER in line]


def find_fused_header_lines(source: str) -> list[tuple[int, str]]:
    issues: list[tuple[int, str]] = []
    for index, line in enumerate(source.splitlines(), start=1):
        for marker in HEADER_FUSED_MARKERS:
            if marker in line:
                issues.append((index, marker.strip()))
                break
    return issues


def validate_header(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    return [f"{path}:{line}:{marker}" for line, marker in find_fused_header_lines(source)]


def validate_bindings(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    return [f"{path}:{line}:{FUSED_MARKER.strip()}" for line in find_fused_pub_const_lines(source)]


def _load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_doc_lines(source: str) -> set[str]:
    markers: set[str] = set()
    for line in source.splitlines():
        normalized = line.strip()
        if normalized.startswith("- "):
            normalized = normalized[2:].lstrip()
        if normalized.startswith("* "):
            normalized = normalized[2:].lstrip()
        if normalized.startswith("`") and normalized.endswith("`") and len(normalized) >= 2:
            normalized = normalized[1:-1]
        markers.add(normalized)
    return markers


def validate_gate_contract(manifest_path: Path, doc_path: Path) -> list[str]:
    issues: list[str] = []
    manifest = _load_manifest(manifest_path)
    files = manifest.get("files")
    if not isinstance(files, list):
        issues.append(f"{manifest_path}:missing_manifest_files")
    else:
        for required_file in REQUIRED_MANIFEST_FILES:
            if required_file not in files:
                issues.append(f"{manifest_path}:missing_manifest_file:{required_file}")

    doc_markers = _normalize_doc_lines(doc_path.read_text(encoding="utf-8"))
    for marker in (*REQUIRED_DOC_MARKERS, *REQUIRED_BINDINGS_DOC_MARKERS, *REQUIRED_EXPORT_UAPI_DOC_MARKERS):
        if marker not in doc_markers:
            issues.append(f"{doc_path}:missing_doc_marker:{marker}")
    return issues


def run_validation(
    abi_header_path: Path,
    abi_bindings_path: Path,
    dev_t_bindings_path: Path,
    notifier_bindings_path: Path,
    manifest_path: Path,
    doc_path: Path,
) -> int:
    issues = validate_header(abi_header_path)
    issues.extend(validate_bindings(abi_bindings_path))
    issues.extend(validate_bindings(dev_t_bindings_path))
    issues.extend(validate_bindings(notifier_bindings_path))
    issues.extend(validate_gate_contract(manifest_path, doc_path))
    if issues:
        print("PHASE3_ABI_BINDINGS_SYNTAX=fail")
        print("PHASE3_ABI_BINDINGS_SYNTAX_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_ABI_BINDINGS_SYNTAX_ISSUES_END")
        return 1
    print("PHASE3_ABI_BINDINGS_SYNTAX=pass")
    print(f"ABI_HEADER_PATH={abi_header_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_PATH={abi_bindings_path.relative_to(ROOT).as_posix()}")
    print(f"DEV_T_BINDINGS_PATH={dev_t_bindings_path.relative_to(ROOT).as_posix()}")
    print(f"NOTIFIER_BINDINGS_PATH={notifier_bindings_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_MANIFEST={manifest_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_DOC={doc_path.relative_to(ROOT).as_posix()}")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_bindings_syntax_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        root = tmp_dir / "repo"
        abi_header = root / "include" / "zigux" / "abi.h"
        abi_bindings = root / "zigux" / "bindings" / "abi.zig"
        dev_t_bindings = root / "zigux" / "bindings" / "dev_t.zig"
        notifier_bindings = root / "zigux" / "bindings" / "notifier_abi.zig"
        manifest = root / "zigux" / "tests" / "fixtures" / "phase3_abi_manifest.json"
        doc = root / "Documentation" / "zigux" / "phase3-abi-slice.md"
        for path in (abi_header.parent, abi_bindings.parent, manifest.parent, doc.parent):
            path.mkdir(parents=True, exist_ok=True)

        abi_header.write_text(
            "\n".join(
                [
                    "#ifndef _ZIGUX_ABI_H",
                    "#define _ZIGUX_ABI_H",
                    "struct zigux_boundary_header {",
                    "    unsigned int size;",
                    "};",
                    "#define ZIGUX_ABI_VERSION 1U",
                    "#endif",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        abi_bindings.write_text(
            "\n".join(
                [
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        dev_t_bindings.write_text(
            "\n".join(
                [
                    "pub const minor_bits: u5 = 20;",
                    "pub const minor_mask: u32 = (1 << minor_bits) - 1;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        notifier_bindings.write_text(
            "\n".join(
                [
                    "pub const NOTIFIER_CHAIN_FLAG_EMPTY: u32 = 1;",
                    "pub const NOTIFIER_CHAIN_FLAG_TERMINATED: u32 = 2;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        manifest.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(REQUIRED_MANIFEST_FILES),
                    "file_count": len(REQUIRED_MANIFEST_FILES),
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        doc.write_text(
            "\n".join(
                [
                    "- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py`",
                    "- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test`",
                    "- `python3 scripts/zigux/survey-phase3-abi-constant-parity.py`",
                    "- `python3 scripts/zigux/survey-phase3-abi-constant-parity.py --self-test`",
                    "- `include/zigux/dev_t.h`",
                    "- `include/linux/zigux.h`",
                    "- `zigux/bindings/abi.zig`",
                    "- `zigux/bindings/dev_t.zig`",
                    "- `zigux/bindings/notifier_abi.zig`",
                    "- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`",
                    "- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`",
                    "- `PHASE3_ABI_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`",
                    "- `PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        assert validate_header(abi_header) == []
        assert validate_bindings(abi_bindings) == []
        assert validate_bindings(dev_t_bindings) == []
        assert validate_bindings(notifier_bindings) == []
        assert validate_gate_contract(manifest, doc) == []

        abi_header.write_text(
            "struct zigux_boundary_header { unsigned int size; };#define ZIGUX_ABI_VERSION 1U\n",
            encoding="utf-8",
            newline="\n",
        )
        fused_header_issues = validate_header(abi_header)
        assert fused_header_issues == [f"{abi_header}:1:{HEADER_FUSED_MARKERS[0].strip()}"]

        abi_header.write_text(
            "\n".join(
                [
                    "#ifndef _ZIGUX_ABI_H",
                    "#define _ZIGUX_ABI_H",
                    "struct zigux_boundary_header {",
                    "    unsigned int size;",
                    "};",
                    "#define ZIGUX_ABI_VERSION 1U",
                    "#endif",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        abi_bindings.write_text(
            "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;\n",
            encoding="utf-8",
            newline="\n",
        )
        fused_abi_issues = validate_bindings(abi_bindings)
        assert fused_abi_issues == [f"{abi_bindings}:1:{FUSED_MARKER.strip()}"]

        abi_bindings.write_text(
            "\n".join(
                [
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        dev_t_bindings.write_text(
            "pub const minor_bits: u5 = 20;pub const minor_mask: u32 = (1 << minor_bits) - 1;\n",
            encoding="utf-8",
            newline="\n",
        )
        fused_dev_t_issues = validate_bindings(dev_t_bindings)
        assert fused_dev_t_issues == [f"{dev_t_bindings}:1:{FUSED_MARKER.strip()}]

        dev_t_bindings.write_text(
            "\n".join(
                [
                    "pub const minor_bits: u5 = 20;",
                    "pub const minor_mask: u32 = (1 << minor_bits) - 1;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        notifier_bindings.write_text(
            "pub const NOTIFIER_CHAIN_FLAG_EMPTY: u32 = 1;pub const NOTIFIER_CHAIN_FLAG_TERMINATED: u32 = 2;\n",
            encoding="utf-8",
            newline="\n",
        )
        fused_notifier_issues = validate_bindings(notifier_bindings)
        assert fused_notifier_issues == [f"{notifier_bindings}:1:{FUSED_MARKER.strip()}]

        notifier_bindings.write_text(
            "\n".join(
                [
                    "pub const NOTIFIER_CHAIN_FLAG_EMPTY: u32 = 1;",
                    "pub const NOTIFIER_CHAIN_FLAG_TERMINATED: u32 = 2;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        manifest.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": [],
                    "file_count": 0,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        manifest_issues = validate_gate_contract(manifest, doc)
        assert manifest_issues == [
            f"{manifest}:missing_manifest_file:{required_file}" for required_file in REQUIRED_MANIFEST_FILES
        ]

        manifest.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(REQUIRED_MANIFEST_FILES),
                    "file_count": len(REQUIRED_MANIFEST_FILES),
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        doc.write_text(
            "- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py`\n",
            encoding="utf-8",
            newline="\n",
        )
        doc_issues = validate_gate_contract(manifest, doc)
        assert doc_issues == [
            f"{doc}:missing_doc_marker:{marker}"
            for marker in (
                "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
                "python3 scripts/zigux/survey-phase3-abi-constant-parity.py",
                "python3 scripts/zigux/survey-phase3-abi-constant-parity.py --self-test",
                *REQUIRED_BINDINGS_DOC_MARKERS,
                *REQUIRED_EXPORT_UAPI_DOC_MARKERS,
            )
        ]

    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect fused top-level declarations across the authoritative Phase 3 ABI header and the curated ABI, dev_t, and notifier bindings, and require the dedicated syntax gate contract."
    )
    parser.add_argument(
        "abi_path",
        nargs="?",
        type=Path,
        default=DEFAULT_ABI_BINDINGS,
        help="ABI bindings file to inspect.",
    )
    parser.add_argument(
        "--header-path",
        type=Path,
        default=DEFAULT_ABI_HEADER,
        help="Authoritative ABI header to inspect.",
    )
    parser.add_argument(
        "--dev-t-path",
        type=Path,
        default=DEFAULT_DEV_T_BINDINGS,
        help="dev_t bindings file to inspect.",
    )
    parser.add_argument(
        "--notifier-path",
        type=Path,
        default=DEFAULT_NOTIFIER_BINDINGS,
        help="notifier starter bindings file to inspect.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Phase 3 ABI manifest to verify.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_DOC,
        help="Phase 3 ABI slice note to verify.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated syntax-guard coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_validation(args.header_path, args.abi_path, args.dev_t_path, args.notifier_path, args.manifest, args.doc)


if __name__ == "__main__":
    raise SystemExit(main())
