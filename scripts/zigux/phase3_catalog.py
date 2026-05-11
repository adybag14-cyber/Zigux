#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "Documentation" / "zigux"
SCRIPTS_DIR = ROOT / "scripts" / "zigux"
TESTS_DIR = ROOT / "zigux" / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
ARTIFACT_DIFF_PATH = DOCS_DIR / "artifact-diff.md"


@dataclass(frozen=True)
class Phase3Slice:
    slug: str
    description: str
    doc_path: Path
    check_script: Path
    dump_path: Path
    expected_path: Path
    harness_path: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "slug": self.slug,
            "description": self.description,
            "doc": self.doc_path.relative_to(ROOT).as_posix(),
            "check_script": self.check_script.relative_to(ROOT).as_posix(),
            "dump": self.dump_path.relative_to(ROOT).as_posix(),
            "expected": self.expected_path.relative_to(ROOT).as_posix(),
            "harness": self.harness_path.relative_to(ROOT).as_posix(),
        }


def discover_phase3_slices(root: Path = ROOT) -> list[Phase3Slice]:
    return [
        Phase3Slice(
            slug="abi",
            description="ABI layout",
            doc_path=root / "Documentation/zigux/phase3-abi-slice.md",
            check_script=root / "scripts/zigux/check-phase3-abi.py",
            dump_path=root / "zigux/tests/phase3_abi_dump.zig",
            expected_path=root / "zigux/tests/fixtures/phase3_abi/expected.json",
            harness_path=root / "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
        )
    ]


def audit_doc_sync(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    required = [
        root / "Documentation/zigux/phase3-abi-slice.md",
        root / "Documentation/zigux/artifact-diff.md",
        root / "scripts/zigux/run-phase3-checks.py",
        root / "scripts/zigux/phase3_check_lib.py",
        root / "scripts/zigux/generate-phase3-check-wrappers.py",
    ]
    for path in required:
        if not path.exists():
            issues.append(f"missing repo file: {path.relative_to(root).as_posix()}")

    artifact_diff = root / "Documentation/zigux/artifact-diff.md"
    if artifact_diff.exists():
        text = artifact_diff.read_text(encoding="utf-8")
        marker = "python3 scripts/zigux/run-phase3-checks.py --slug abi"
        if marker not in text:
            issues.append(f"missing artifact-diff marker: {marker}")
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests/fixtures/phase3_abi").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
        for rel in [
            "Documentation/zigux/phase3-abi-slice.md",
            "Documentation/zigux/artifact-diff.md",
            "scripts/zigux/run-phase3-checks.py",
            "scripts/zigux/phase3_check_lib.py",
            "scripts/zigux/generate-phase3-check-wrappers.py",
            "scripts/zigux/check-phase3-abi.py",
            "zigux/tests/phase3_abi_dump.zig",
            "zigux/tests/fixtures/phase3_abi/expected.json",
            "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
        ]:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("python3 scripts/zigux/run-phase3-checks.py --slug abi\n", encoding="utf-8")
        assert [entry.slug for entry in discover_phase3_slices(root)] == ["abi"]
        assert audit_doc_sync(root) == []
        (root / "Documentation/zigux/artifact-diff.md").write_text("stale\n", encoding="utf-8")
        assert audit_doc_sync(root) == ["missing artifact-diff marker: python3 scripts/zigux/run-phase3-checks.py --slug abi"]
    print("PHASE3_CATALOG_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Focused Phase 3 catalog helper.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--audit-doc-sync", action="store_true")
    parser.add_argument("--print-slices", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    entries = discover_phase3_slices()
    if args.print_slices:
        print(json.dumps([entry.to_dict() for entry in entries], indent=2, sort_keys=True))

    if args.audit_doc_sync:
        issues = audit_doc_sync()
        if issues:
            print("PHASE3_DOC_SYNC_AUDIT=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE3_DOC_SYNC_AUDIT=pass")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
