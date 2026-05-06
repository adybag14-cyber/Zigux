#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BINDINGS = ROOT / "zigux" / "bindings" / "abi.zig"
DEFAULT_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi_manifest.json"
DEFAULT_DOC = ROOT / "Documentation" / "zigux" / "phase3-abi-slice.md"
FUSED_MARKER = ";pub const "
REQUIRED_MANIFEST_FILE = "scripts/zigux/validate-phase3-abi-bindings-syntax.py"
REQUIRED_DOC_MARKERS = (
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
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
    if not isinstance(files, list) or REQUIRED_MANIFEST_FILE not in files:
        issues.append(f"{manifest_path}:missing_manifest_file:{REQUIRED_MANIFEST_FILE}")

    doc_markers = _normalize_doc_lines(doc_path.read_text(encoding="utf-8"))
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_markers:
            issues.append(f"{doc_path}:missing_doc_marker:{marker}")
    return issues


def run_validation(bindings_path: Path, manifest_path: Path, doc_path: Path) -> int:
    issues = validate_bindings(bindings_path)
    issues.extend(validate_gate_contract(manifest_path, doc_path))
    if issues:
        print("PHASE3_ABI_BINDINGS_SYNTAX=fail")
        print("PHASE3_ABI_BINDINGS_SYNTAX_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_ABI_BINDINGS_SYNTAX_ISSUES_END")
        return 1
    print("PHASE3_ABI_BINDINGS_SYNTAX=pass")
    print(f"ABI_BINDINGS_PATH={bindings_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_MANIFEST={manifest_path.relative_to(ROOT).as_posix()}")
    print(f"ABI_BINDINGS_DOC={doc_path.relative_to(ROOT).as_posix()}")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_bindings_syntax_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        root = tmp_dir / "repo"
        bindings = root / "zigux" / "bindings" / "abi.zig"
        manifest = root / "zigux" / "tests" / "fixtures" / "phase3_abi_manifest.json"
        doc = root / "Documentation" / "zigux" / "phase3-abi-slice.md"
        for path in (bindings.parent, manifest.parent, doc.parent):
            path.mkdir(parents=True, exist_ok=True)

        bindings.write_text(
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
        manifest.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": [REQUIRED_MANIFEST_FILE],
                    "file_count": 1,
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
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        assert validate_bindings(bindings) == []
        assert validate_gate_contract(manifest, doc) == []

        bindings.write_text(
            "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;\n",
            encoding="utf-8",
            newline="\n",
        )
        fused_issues = validate_bindings(bindings)
        assert fused_issues == [f"{bindings}:1:{FUSED_MARKER.strip()}"]

        bindings.write_text(
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
        assert manifest_issues == [f"{manifest}:missing_manifest_file:{REQUIRED_MANIFEST_FILE}"]

        manifest.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": [REQUIRED_MANIFEST_FILE],
                    "file_count": 1,
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
            f"{doc}:missing_doc_marker:python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test"
        ]

    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect fused top-level Phase 3 ABI binding declarations and require the dedicated syntax gate contract."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=DEFAULT_BINDINGS,
        help="Bindings file to inspect.",
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
    return run_validation(args.path, args.manifest, args.doc)


if __name__ == "__main__":
    raise SystemExit(main())
