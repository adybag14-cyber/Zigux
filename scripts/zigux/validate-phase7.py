#!/usr/bin/env python3
"""Validate the bounded Phase 7 leaf-library evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
CHECKER_PATH = Path("scripts/zigux/check-phase7-shared-surface.py")
ARGV_SPLIT_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")
MAKE_WRAPPER_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

EXPECTED_PACKET = "phase7-leaf-library-evidence"
EXPECTED_PHASE = "Phase 7"
EXPECTED_SCOPE = "shared leaf-library evidence rows and validation foothold only"
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]
REQUIRED_FILES = [
    CATALOG_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    CHECKER_PATH,
    ARGV_SPLIT_CHECKER_PATH,
    MAKE_WRAPPER_ALIGNMENT_CHECKER_PATH,
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    Path("lib/string_helpers.zig"),
    Path("lib/string_helpers_parse_int_array.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
]
SELF_TEST_CASE_COUNT = 8

class ValidationError(RuntimeError):
    pass

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc

def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))

def run_checker(root: Path, checker_path: Path, root_flag: str = "--repo-root") -> None:
    result = subprocess.run(
        [sys.executable, str(root / checker_path), root_flag, str(root)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker_path.as_posix()} failed: {detail}")

def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    manifest = read_json(root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase7 packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase7 phase drift")
    if manifest.get("lane_scope") != EXPECTED_SCOPE:
        raise ValidationError("phase7 scope drift")
    if manifest.get("current_replay_inventory") != EXPECTED_REPLAYS:
        raise ValidationError("phase7 replay inventory drift")

    makefile = read_text(root / MAKEFILE_PATH)
    if "phase7-validate:" not in makefile or "$(PYTHON) scripts/zigux/validate-phase7.py" not in makefile:
        raise ValidationError("phase7 make route missing")

    run_checker(root, CHECKER_PATH)
    run_checker(root, MAKE_WRAPPER_ALIGNMENT_CHECKER_PATH, "--root")
    run_checker(root, ARGV_SPLIT_CHECKER_PATH)

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def scaffold_repo(root: Path) -> None:
    source_root = Path(__file__).resolve().parent
    write(root / CATALOG_PATH, "\n".join([
        "- packet: `phase7-leaf-library-evidence`",
        "- phase: `Phase 7`",
        "- lane scope: shared leaf-library evidence rows and validation foothold only",
        "",
        "## Current direct-readback companions",
        "- `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
        "- `Documentation/zigux/README.md`",
        "- `scripts/zigux/check-phase7-shared-surface.py`",
        "- `scripts/zigux/validate-phase7.py`",
        "- `scripts/zigux/README.md`",
        "- `zigux/tests/README.md`",
        "- `zigux/tests/phase7_leaf_library_evidence_manifest.json`",
        "- `zigux/Makefile`",
        "- `lib/string_helpers.zig`",
        "- `lib/string_helpers_parse_int_array.zig`",
        "- `lib/cmdline.zig`",
        "- `lib/argv_split.zig`",
        "",
        "## Current replay inventory",
        "- `make -C zigux phase7-validate`",
        "",
        "## Current repo-reality gaps",
        "- `lib/rbtree.zig`",
        "",
        "`kstrdupQuotable()`",
        "`kstrdupQuotableCmdline()`",
    ]) + "\n")
    write(root / MAKEFILE_PATH, "phase7-validate:\n\t$(PYTHON) scripts/zigux/validate-phase7.py\n")
    write(root / MANIFEST_PATH, json.dumps({
        "packet": EXPECTED_PACKET,
        "phase": EXPECTED_PHASE,
        "lane_scope": EXPECTED_SCOPE,
        "current_direct_readback_companions": [
            "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
            "Documentation/zigux/README.md",
            "scripts/zigux/check-phase7-shared-surface.py",
            "scripts/zigux/validate-phase7.py",
            "scripts/zigux/README.md",
            "zigux/tests/README.md",
            "zigux/tests/phase7_leaf_library_evidence_manifest.json",
            "zigux/Makefile",
            "lib/string_helpers.zig",
            "lib/string_helpers_parse_int_array.zig",
            "lib/cmdline.zig",
            "lib/argv_split.zig",
        ],
        "roadmap_anchors": [
            "lib/string_helpers.c",
            "lib/cmdline.c",
            "lib/argv_split.c",
            "lib/rbtree.c",
        ],
        "current_direct_helper_evidence": [
            {"key": "string_helpers", "zig_helper": "lib/string_helpers.zig", "expected_markers": ["pub const STRING_UNITS_10", "pub const KasprintfStrarrayResult", "pub fn kstrdupQuotable", "pub fn kstrdupQuotableCmdline"]},
            {"key": "string_helpers_parse_int_array", "zig_helper": "lib/string_helpers_parse_int_array.zig", "expected_markers": ["pub const ParseIntArrayResult", "pub fn parseIntArray"]},
            {"key": "cmdline", "zig_helper": "lib/cmdline.zig", "expected_markers": ["pub fn parseOptionStr", "pub fn getOption"]},
            {"key": "argv_split", "zig_helper": "lib/argv_split.zig", "expected_markers": ["pub const ArgvSplitResult", "pub fn argvSplit"]},
        ],
        "current_replay_inventory": EXPECTED_REPLAYS,
        "current_repo_reality_gaps": ["lib/rbtree.zig", "zigux/tests/phase7_build.zig"],
    }, indent=2) + "\n")
    write(root / DOCS_README_PATH, "# Zigux Documentation\nPhase 7 notes\n")
    write(root / SCRIPTS_README_PATH, "# scripts/zigux\n\n## Phase 7\n")
    write(root / TESTS_README_PATH, "# zigux/tests\n\n## Phase 7\n")
    for rel_path, content in [
        (Path("lib/string_helpers.zig"), "pub const STRING_UNITS_10 = 0;\npub const KasprintfStrarrayResult = struct {};\npub fn kstrdupQuotable() void {}\npub fn kstrdupQuotableCmdline() void {}\n"),
        (Path("lib/string_helpers_parse_int_array.zig"), "pub const ParseIntArrayResult = struct {};\npub fn parseIntArray() void {}\n"),
        (Path("lib/cmdline.zig"), "pub fn parseOptionStr() void {}\npub fn getOption() void {}\n"),
        (Path("lib/argv_split.zig"), "pub const ArgvSplitResult = struct {};\npub fn argvSplit() void {}\n"),
    ]:
        write(root / rel_path, content)
    checker_text = (source_root / "check-phase7-shared-surface.py").read_text(encoding="utf-8")
    write(root / CHECKER_PATH, checker_text)
    argv_split_checker_text = (source_root / "check-phase7-argv-split-packet.py").read_text(encoding="utf-8")
    write(root / ARGV_SPLIT_CHECKER_PATH, argv_split_checker_text)
    alignment_checker_text = (source_root / "check-phase7-make-wrapper-selftest-alignment.py").read_text(encoding="utf-8")
    write(root / MAKE_WRAPPER_ALIGNMENT_CHECKER_PATH, alignment_checker_text)

def expect_failure(root: Path, rel_path: Path, transform: str) -> None:
    if transform == "delete":
        (root / rel_path).unlink()
    else:
        original = read_text(root / rel_path)
        write(root / rel_path, original.replace(transform, "", 1))
    try:
        validate(root)
    except (ValidationError, json.JSONDecodeError):
        return
    raise AssertionError("expected validation failure")

def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        for rel_path, transform in [
            (MANIFEST_PATH, '"make -C zigux phase7-validate"'),
            (MAKEFILE_PATH, "phase7-validate:"),
            (Path("lib/string_helpers.zig"), "pub fn kstrdupQuotableCmdline"),
            (Path("lib/argv_split.zig"), "pub fn argvSplit"),
            (CHECKER_PATH, "delete"),
            (ARGV_SPLIT_CHECKER_PATH, "delete"),
            (MAKE_WRAPPER_ALIGNMENT_CHECKER_PATH, "delete"),
            (DOCS_README_PATH, "delete"),
        ]:
            case_root = Path(tempfile.mkdtemp(prefix="zigux_phase7_validate_case_"))
            try:
                scaffold_repo(case_root)
                expect_failure(case_root, rel_path, transform)
                cases_run += 1
            finally:
                for child in sorted(case_root.rglob("*"), reverse=True):
                    if child.is_file():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                case_root.rmdir()
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE7_VALIDATE_SELF_TEST=pass")
    print(f"PHASE7_VALIDATE_SELF_TEST_CASE_COUNT={cases_run}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_VALIDATE=fail: {exc}")
        return 1
    print("PHASE7_VALIDATE=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
