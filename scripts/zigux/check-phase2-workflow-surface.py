#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
EXPECTED_WORKFLOW = WORKFLOW.as_posix()
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)


def read_manifest(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def find_first_index(lines: list[str], marker: str) -> int | None:
    for index, line in enumerate(lines):
        if line.strip() == marker:
            return index
    return None


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_manifest(root / MANIFEST)
    workflow_text = read_text(root / WORKFLOW)
    issues: list[tuple[str, str]] = []

    workflow_field = manifest.get("workflow")
    if workflow_field != EXPECTED_WORKFLOW:
        issues.append(("WORKFLOW_FIELD_MISMATCH", repr(workflow_field)))

    workflow_lines = workflow_text.splitlines()
    last_index = -1
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        current_index = find_first_index(workflow_lines, marker)
        if current_index is None:
            raise AssertionError(f"counted marker missing from line scan: {marker}")
        if current_index <= last_index:
            issues.append(("WORKFLOW_ORDER_MISMATCH", marker))
            break
        last_index = current_index

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_WORKFLOW_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    write_text(
        root / MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
                "workflow": EXPECTED_WORKFLOW,
                "present_surfaces": {},
                "repo_reality_gaps": [],
                "notes": [],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                *REQUIRED_WORKFLOW_LINES,
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    expected_case_count = 1 + 1 + len(REQUIRED_WORKFLOW_LINES) + len(REQUIRED_WORKFLOW_LINES) + 1
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_workflow_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        manifest = read_manifest(root / MANIFEST)
        manifest["workflow"] = "broken.yml"
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("WORKFLOW_FIELD_MISMATCH", "'broken.yml'") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            write_text(root / WORKFLOW, replace_exact_line(read_text(root / WORKFLOW), marker, "run: python3 other.py"))
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            write_text(root / WORKFLOW, duplicate_exact_line(read_text(root / WORKFLOW), marker))
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        workflow_text = read_text(root / WORKFLOW)
        lines = workflow_text.splitlines()
        first_index = lines.index(REQUIRED_WORKFLOW_LINES[0])
        last_index = lines.index(REQUIRED_WORKFLOW_LINES[-1])
        lines[first_index], lines[last_index] = lines[last_index], lines[first_index]
        write_text(root / WORKFLOW, "\n".join(lines) + "\n")
        assert ("WORKFLOW_ORDER_MISMATCH", REQUIRED_WORKFLOW_LINES[1]) in collect_issues(root)
        checks += 1

    assert checks == expected_case_count
    print("PHASE2_WORKFLOW_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_WORKFLOW_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 tool-manifest workflow surface aligned with the shipped bootstrap workflow packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against synthetic fixtures")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing synthetic sample root for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        args.write_sample_root.mkdir(parents=True, exist_ok=True)
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_WORKFLOW_SURFACE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_WORKFLOW_SURFACE=pass")
    print(f"PHASE2_WORKFLOW_SURFACE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
