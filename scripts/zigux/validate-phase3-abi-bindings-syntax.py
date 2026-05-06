#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ABI_BINDINGS = ROOT / "zigux" / "bindings" / "abi.zig"
DEFAULT_DEV_T_BINDINGS = ROOT / "zigux" / "bindings" / "dev_t.zig"
DEFAULT_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi_manifest.json"
DEFAULT_DOC = ROOT / "Documentation" / "zigux" / "phase3-abi-slice.md"
FUSED_MARKER = ";pub const "
REQUIRED_MANIFEST_FILES = (
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
)
REQUIRED_DOC_MARKERS = (
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
)
REQUIRED_EXPORT_UAPI_DOC_MARKERS = (
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
    "PHASE3_ABI_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice",
)


def find_fused_pub_const_lines(source: str) -> list[int]:
    return [index for index, line in enumerate(source.splitlines(), start=1) if FUSED_MARKER in line]


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
    for marker in (*REQUIRED_DOC_MARKERS, *REQUIRED_EXPORT_UAPI_DOC_MARKERS):
        if marker not in doc_markers:
            issues.append(f"{doc_path}:missing_doc_marker:{marker}")
    return issues


def run_validation(abi_bindings_path: Path, dev_t_bindings_path: Path, manifest_path: Path, doc_path: Path) -> int:
    issues = validate_bindings(abi_bindings_path)
    issues.extend(validate_bindings(dev_t_bindings_path))
    issues.extend(validate_gate_contract(manifest_path, doc_path))
    if issues:
        print("PHASE3_ABI_BINDINGS_SYNTAX=fail")
        print("PHASE3_ABI_BINDINGS_SYNTAX_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_ABI_BINDINGS_SYNTAX_ISSUES_END")
        return 1
    print("PHASE3_ABI_BINDINGS_SYNTAX=pass")
    print(f"ABI_BINDINGS_PATH={abi_bindings_path.relative_to(ROOT).as_posix()}")
    print(f"DEV_T_BINDINGS_PATH={dev_t_bindings_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_MANIFEST={manifest_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_DOC={doc_path.relative_to(ROOT).as_posix()}")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_bindings_syntax_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        root = tmp_dir / "repo"
        abi_bindings = root / "zigux" / "bindings" / "abi.zig"
        dev_t_bindings = root / "zigux" / "bindings" / "dev_t.zig"
        manifest = root / "zigux" / "tests" / "fixtures" / "phase3_abi_manifest.json"
        doc = root / "Documentation" / "zigux" / "phase3-abi-slice.md"
        for path in (abi_bindings.parent, manifest.parent, doc.parent):
            path.mkdir(parents=True, exist_ok=True)

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
                    "- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`",
                    "- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`",
                    "- `PHASE3_ABI_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`",
                    "- `PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        assert validate_bindings(abi_bindings) == []
        assert validate_bindings(dev_t_bindings) == []
        assert validate_gate_contract(manifest, doc) == []

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
        assert fused_dev_t_issues == [f"{dev_t_bindings}:1:{FUSED_MARKER.strip()}"]

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
                *REQUIRED_EXPORT_UAPI_DOC_MARKERS,
            )
        ]

    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect fused top-level Phase 3 ABI binding declarations across the curated ABI and dev_t bindings and require the dedicated syntax gate contract."
    )
    parser.add_argument(
        "abi_path",
        nargs="?",
        type=Path,
        default=DEFAULT_ABI_BINDINGS,
        help="ABI bindings file to inspect.",
    )
    parser.add_argument(
        "--dev-t-path",
        type=Path,
        default=DEFAULT_DEV_T_BINDINGS,
        help="dev_t bindings file to inspect.",
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
    return run_validation(args.abi_path, args.dev_t_path, args.manifest, args.doc)


if __name__ == "__main__":
    raise SystemExit(main())
