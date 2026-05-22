#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
CHECK_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
CHECK_CROSS = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CHECK_CROSS_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
CHECK_TOOLCHAIN_PINNING = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"

EXPECTED_PATH = "workflow_action_path"
EXPECTED_WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
EXPECTED_ACTION_PATH = (
    ".github/workflows/zigux-bootstrap.yml",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py",
)
EXPECTED_WORKFLOW_LINES = tuple(f"run: {entry}" for entry in EXPECTED_ACTION_PATH[1:])
REQUIRED_PATHS = (
    WORKFLOW,
    MANIFEST,
    CHECK_TOOLCHAIN,
    INSTALL_ZIG,
    CHECK_CROSS,
    CHECK_CROSS_ALIGNMENT,
    CHECK_TOOLCHAIN_PINNING,
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_duplicate_entries(entries: tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in REQUIRED_PATHS:
        if not resolve_path(root, path).is_file():
            issues.append(("MISSING_REQUIRED_FILE", str(path.relative_to(ROOT))))

    manifest_payload = read_json(resolve_path(root, MANIFEST))
    if not isinstance(manifest_payload, dict):
        return [("INVALID_MANIFEST_ROOT", type(manifest_payload).__name__)]

    if manifest_payload.get("workflow") != EXPECTED_WORKFLOW:
        issues.append(("INVALID_WORKFLOW_FIELD", str(manifest_payload.get("workflow"))))

    present_surfaces = manifest_payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_PRESENT_SURFACES", type(present_surfaces).__name__)]

    workflow_action_path = present_surfaces.get(EXPECTED_PATH)
    if not isinstance(workflow_action_path, list):
        return issues + [("INVALID_WORKFLOW_ACTION_PATH", type(workflow_action_path).__name__)]
    if not all(isinstance(entry, str) for entry in workflow_action_path):
        return issues + [("NON_STRING_WORKFLOW_ACTION_ENTRY", repr(workflow_action_path))]

    actual_entries = tuple(workflow_action_path)
    duplicates = find_duplicate_entries(actual_entries)
    for entry in duplicates:
        issues.append(("DUPLICATE_WORKFLOW_ACTION_ENTRY", entry))

    if actual_entries != EXPECTED_ACTION_PATH:
        missing = [entry for entry in EXPECTED_ACTION_PATH if entry not in actual_entries]
        unexpected = [entry for entry in actual_entries if entry not in EXPECTED_ACTION_PATH]
        if missing:
            issues.extend(("MISSING_WORKFLOW_ACTION_ENTRY", entry) for entry in missing)
        if unexpected:
            issues.extend(("UNEXPECTED_WORKFLOW_ACTION_ENTRY", entry) for entry in unexpected)
        if not missing and not unexpected:
            issues.append(("WORKFLOW_ACTION_ORDER_MISMATCH", json.dumps(actual_entries)))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for line in EXPECTED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{line}:count={count}"))

    exact_lines = [line.strip() for line in workflow_text.splitlines()]
    last_index = -1
    for line in EXPECTED_WORKFLOW_LINES:
        try:
            index = exact_lines.index(line)
        except ValueError:
            continue
        if index <= last_index:
            issues.append(("WORKFLOW_LINE_ORDER_MISMATCH", line))
            break
        last_index = index

    return issues


def format_issue(code: str, detail: str) -> str:
    return f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_NOTE={code}:{detail}"


def run_checker(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(format_issue(code, detail))
        print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION=fail")
        return 1
    print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION=pass")
    print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_ENTRY_COUNT={len(EXPECTED_ACTION_PATH)}")
    print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_WORKFLOW_LINE_COUNT={len(EXPECTED_WORKFLOW_LINES)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(destination: Path) -> None:
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "workflow": EXPECTED_WORKFLOW,
        "present_surfaces": {
            EXPECTED_PATH: list(EXPECTED_ACTION_PATH),
        },
    }
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
    ]
    for line in EXPECTED_WORKFLOW_LINES:
        workflow_lines.append("      - name: sample")
        workflow_lines.append(f"        {line}")

    write_text(destination / ".github" / "workflows" / "zigux-bootstrap.yml", "\n".join(workflow_lines) + "\n")
    write_text(destination / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json", json.dumps(manifest, indent=2) + "\n")
    write_text(destination / "scripts" / "zigux" / "check-zig-toolchain.py", "# sample\n")
    write_text(destination / "scripts" / "zigux" / "install-zig.py", "# sample\n")
    write_text(destination / "scripts" / "zigux" / "check-phase2-cross.py", "# sample\n")
    write_text(destination / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py", "# sample\n")
    write_text(destination / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py", "# sample\n")


def run_self_test() -> int:
    cases_run = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_sample_root(root)

        if run_checker(root) != 0:
            print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST=fail")
            print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST_CASE_COUNT={cases_run}")
            return 1
        cases_run += 1

        manifest_path = root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"].pop(EXPECTED_PATH)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if run_checker(root) == 0:
            print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST=fail")
            print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST_CASE_COUNT={cases_run}")
            return 1
        cases_run += 1

        write_sample_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"][EXPECTED_PATH][2] = "python3 scripts/zigux/install-zig.py"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if run_checker(root) == 0:
            print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST=fail")
            print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST_CASE_COUNT={cases_run}")
            return 1
        cases_run += 1

        write_sample_root(root)
        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace(
            "run: python3 scripts/zigux/check-phase2-cross.py\n",
            "",
        ), encoding="utf-8")
        if run_checker(root) == 0:
            print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST=fail")
            print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST_CASE_COUNT={cases_run}")
            return 1
        cases_run += 1

        write_sample_root(root)
        (root / "scripts" / "zigux" / "check-phase2-cross.py").unlink()
        if run_checker(root) == 0:
            print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST=fail")
            print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST_CASE_COUNT={cases_run}")
            return 1
        cases_run += 1

    print("PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_WORKFLOW_ACTION_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing minimal sample root and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0
    if args.self_test:
        return run_self_test()
    return run_checker(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
