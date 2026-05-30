#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-genksyms-selftest-alignment.py"

VERSION_PROOF = "VERSION_SIDE_EFFECT_TEST"
AMBIGUOUS_VERSION_PROOF = "AMBIGUOUS_VERSION_SIDE_EFFECT_TEST"
PROOF_CONSTANTS = (VERSION_PROOF, AMBIGUOUS_VERSION_PROOF)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def assignment_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
    return names


def function_text(source: str, tree: ast.Module, function_name: str) -> str:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(source, node) or ""
    return ""


def count_token(text: str, token: str) -> int:
    return sum(1 for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Name) and node.id == token)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    checker_path = root / ALIGNMENT_CHECKER.relative_to(ROOT)
    source = read_text(checker_path)
    try:
        tree = ast.parse(source, filename=checker_path.as_posix())
    except SyntaxError as exc:
        return [("INVALID_ALIGNMENT_CHECKER", f"{exc.lineno}:{exc.offset}")]

    issues: list[tuple[str, str]] = []
    names = assignment_names(tree)
    for constant in PROOF_CONSTANTS:
        if constant not in names:
            issues.append(("MISSING_STANDALONE_PROOF_CONSTANT", constant))

    manifest_builder = function_text(source, tree, "build_expected_manifest")
    if not manifest_builder:
        issues.append(("MISSING_ALIGNMENT_FUNCTION", "build_expected_manifest"))
    else:
        for constant in PROOF_CONSTANTS:
            if count_token(manifest_builder, constant) != 1:
                issues.append(("STANDALONE_PROOF_MANIFEST_PACKET_MISMATCH", constant))

    collector = function_text(source, tree, "collect_issues")
    if not collector:
        issues.append(("MISSING_ALIGNMENT_FUNCTION", "collect_issues"))
    else:
        for constant in PROOF_CONSTANTS:
            if count_token(collector, constant) < 1:
                issues.append(("STANDALONE_PROOF_REQUIRED_PATH_MISMATCH", constant))

    self_test = function_text(source, tree, "run_self_test")
    if not self_test:
        issues.append(("MISSING_ALIGNMENT_FUNCTION", "run_self_test"))
    else:
        for constant in PROOF_CONSTANTS:
            if count_token(self_test, constant) < 2:
                issues.append(("STANDALONE_PROOF_SELF_TEST_MISMATCH", constant))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_alignment_stub(root: Path) -> Path:
    path = root / ALIGNMENT_CHECKER.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "from pathlib import Path\n"
        "ROOT = Path.cwd()\n"
        "VERSION_SIDE_EFFECT_TEST = ROOT / 'scripts/zigux/genksyms_version_before_invalid_long_option_test.zig'\n"
        "AMBIGUOUS_VERSION_SIDE_EFFECT_TEST = ROOT / 'scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig'\n"
        "def build_expected_manifest():\n"
        "    return {'standalone_proof_packet': [\n"
        "        VERSION_SIDE_EFFECT_TEST.relative_to(ROOT).as_posix(),\n"
        "        AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT).as_posix(),\n"
        "    ]}\n"
        "def collect_issues(root):\n"
        "    early_required_paths = (\n"
        "        root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT),\n"
        "        root / AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT),\n"
        "    )\n"
        "    return list(early_required_paths)\n"
        "def run_self_test():\n"
        "    for missing_path in (VERSION_SIDE_EFFECT_TEST, AMBIGUOUS_VERSION_SIDE_EFFECT_TEST):\n"
        "        missing_path_in_root = Path('/tmp') / missing_path.relative_to(ROOT)\n"
        "        assert missing_path.relative_to(ROOT).as_posix() in str(missing_path_in_root)\n"
        "    VERSION_SIDE_EFFECT_TEST.relative_to(ROOT)\n"
        "    AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT)\n"
        "\n",
        encoding="utf-8",
    )
    return path


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_proof_packet_") as tmp_dir:
        root = Path(tmp_dir)
        path = write_alignment_stub(root)
        assert collect_issues(root) == []
        checks_run += 1

        path.write_text(read_text(path).replace("VERSION_SIDE_EFFECT_TEST = ", "MISSING_VERSION_SIDE_EFFECT_TEST = ", 1), encoding="utf-8")
        assert ("MISSING_STANDALONE_PROOF_CONSTANT", VERSION_PROOF) in collect_issues(root)
        checks_run += 1

        write_alignment_stub(root)
        path.write_text(read_text(path).replace("        VERSION_SIDE_EFFECT_TEST.relative_to(ROOT).as_posix(),\n", "", 1), encoding="utf-8")
        assert ("STANDALONE_PROOF_MANIFEST_PACKET_MISMATCH", VERSION_PROOF) in collect_issues(root)
        checks_run += 1

        write_alignment_stub(root)
        path.write_text(read_text(path).replace("        root / AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT),\n", "", 1), encoding="utf-8")
        assert ("STANDALONE_PROOF_REQUIRED_PATH_MISMATCH", AMBIGUOUS_VERSION_PROOF) in collect_issues(root)
        checks_run += 1

        write_alignment_stub(root)
        path.write_text(read_text(path).replace("    AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT)\n", "", 1), encoding="utf-8")
        assert ("STANDALONE_PROOF_SELF_TEST_MISMATCH", AMBIGUOUS_VERSION_PROOF) in collect_issues(root)
        checks_run += 1

    print("PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Phase 2 genksyms standalone proof packet alignment.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET=pass")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET_PROOF_COUNT={len(PROOF_CONSTANTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
