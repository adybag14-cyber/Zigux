#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-direct-tool-manifest-workflow.py"
WORKFLOW_ALIGNMENT = (
    ROOT
    / "scripts"
    / "zigux"
    / "check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py"
)

REQUIRED_PATHS = (
    VALIDATE,
    WORKFLOW_CHECKER,
    WORKFLOW_ALIGNMENT,
)

REQUIRED_VALIDATE_MARKERS = (
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow.py",',
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py",',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    normalized_marker = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized_marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    validate_path = resolve_path(root, VALIDATE)
    if not validate_path.exists():
        return issues

    validate_text = read_text(validate_path)
    for marker in REQUIRED_VALIDATE_MARKERS:
        count = count_exact_lines(validate_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_MARKER", f"{marker}:count={count}"))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_REQUIRED_PATH_COUNT="
        f"{len(REQUIRED_PATHS)}"
    )
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_MARKER_COUNT="
        f"{len(REQUIRED_VALIDATE_MARKERS)}"
    )
    return 0


def build_sample_root(root: Path) -> None:
    validate_lines = ["CHECKS = ("]
    validate_lines.extend(REQUIRED_VALIDATE_MARKERS)
    validate_lines.append(")")
    write_text(resolve_path(root, VALIDATE), "\n".join(validate_lines) + "\n")
    write_text(resolve_path(root, WORKFLOW_CHECKER), "# present\n")
    write_text(resolve_path(root, WORKFLOW_ALIGNMENT), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_cross_direct_tool_manifest_validator_contract_"
    ) as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        write_text(resolve_path(root, VALIDATE), "CHECKS = ()\n")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        write_text(
            validate_path,
            "CHECKS = (\n"
            + "\n".join(REQUIRED_VALIDATE_MARKERS + (REQUIRED_VALIDATE_MARKERS[0],))
            + "\n)\n",
        )
        assert run_check(root) == 1
        checks += 1

        for path in REQUIRED_PATHS[1:]:
            build_sample_root(root)
            resolve_path(root, path).unlink()
            assert run_check(root) == 1
            checks += 1

        build_sample_root(root)
        resolve_path(root, VALIDATE).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_SELF_TEST=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_SELF_TEST_CASE_COUNT="
        f"{checks}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 validator packet aware of the direct tool-manifest "
            "workflow checker pair."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())