#!/usr/bin/env python3
"""Guard the current Phase 2 validate-route packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3] if len(HERE.parents) >= 4 else HERE.parent

SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
VALIDATE = Path("scripts/zigux/validate-phase2.py")
VALIDATE_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")

REMINDER_SURFACES = (
    SCRIPTS_README,
    TESTS_README,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
)

VALIDATOR_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
)

ROUTE_MARKERS = (
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
)

MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

EXPECTED_MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_MAKE_WRAPPERS = (
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json_dict(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def manifest_list(issues: list[tuple[str, str]], manifest: dict, key: str) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in (*REMINDER_SURFACES, WORKFLOW, MAKEFILE, MANIFEST, VALIDATE, VALIDATE_CLOSURE):
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    for rel in REMINDER_SURFACES:
        text = read_text(resolve(root, rel))
        for marker in VALIDATOR_MARKERS:
            if marker not in text:
                issues.append(("MISSING_REMINDER_VALIDATOR_MARKER", f"{rel.as_posix()}:{marker}"))
        for marker in ROUTE_MARKERS:
            if marker not in text:
                issues.append(("MISSING_REMINDER_ROUTE_MARKER", f"{rel.as_posix()}:{marker}"))

    workflow_text = read_text(resolve(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    makefile_text = read_text(resolve(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    manifest = read_json_dict(resolve(root, MANIFEST))
    validators = manifest_list(issues, manifest, "validators")
    if validators is not None:
        for marker in EXPECTED_MANIFEST_VALIDATORS:
            if marker not in validators:
                issues.append(("MISSING_MANIFEST_VALIDATOR", marker))
        if validators != list(EXPECTED_MANIFEST_VALIDATORS):
            issues.append(("MANIFEST_VALIDATOR_ORDER_MISMATCH", "validators"))

    make_wrappers = manifest_list(issues, manifest, "make_wrappers")
    if make_wrappers is not None:
        for marker in EXPECTED_MANIFEST_MAKE_WRAPPERS:
            if marker not in make_wrappers:
                issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", marker))

    return issues


def build_sample_root(root: Path) -> None:
    reminder_text = "\n".join((*VALIDATOR_MARKERS, *ROUTE_MARKERS)) + "\n"
    for rel in REMINDER_SURFACES:
        write_text(resolve(root, rel), reminder_text)
    write_text(resolve(root, VALIDATE), "present\n")
    write_text(resolve(root, VALIDATE_CLOSURE), "present\n")
    write_text(resolve(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve(root, MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {
                    "validators": list(EXPECTED_MANIFEST_VALIDATORS),
                    "make_wrappers": list(EXPECTED_MANIFEST_MAKE_WRAPPERS),
                },
            },
            indent=2,
        )
        + "\n",
    )


def reset_root(root: Path) -> None:
    if root.exists():
        for child in root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        root.mkdir(parents=True)
    build_sample_root(root)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REMINDER_SURFACES) * len(VALIDATOR_MARKERS)
        + len(REMINDER_SURFACES) * len(ROUTE_MARKERS)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(EXPECTED_MANIFEST_VALIDATORS)
        + 1
        + len(EXPECTED_MANIFEST_MAKE_WRAPPERS)
        + 2
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_route_packet_") as tmp_dir:
        root = Path(tmp_dir)

        reset_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for rel in REMINDER_SURFACES:
            for marker in VALIDATOR_MARKERS:
                reset_root(root)
                path = resolve(root, rel)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert ("MISSING_REMINDER_VALIDATOR_MARKER", f"{rel.as_posix()}:{marker}") in collect_issues(root)
                checks_run += 1

        for rel in REMINDER_SURFACES:
            for marker in ROUTE_MARKERS:
                reset_root(root)
                path = resolve(root, rel)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert ("MISSING_REMINDER_ROUTE_MARKER", f"{rel.as_posix()}:{marker}") in collect_issues(root)
                checks_run += 1

        for marker in WORKFLOW_LINES:
            reset_root(root)
            path = resolve(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            reset_root(root)
            path = resolve(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in EXPECTED_MANIFEST_VALIDATORS:
            reset_root(root)
            path = resolve(root, MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["validators"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_VALIDATOR", marker) in collect_issues(root)
            checks_run += 1

        reset_root(root)
        path = resolve(root, MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"].reverse()
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MANIFEST_VALIDATOR_ORDER_MISMATCH", "validators") in collect_issues(root)
        checks_run += 1

        for marker in EXPECTED_MANIFEST_MAKE_WRAPPERS:
            reset_root(root)
            path = resolve(root, MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["make_wrappers"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_MAKE_WRAPPER", marker) in collect_issues(root)
            checks_run += 1

        for rel in (VALIDATE, VALIDATE_CLOSURE):
            reset_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_VALIDATE_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(path: Path) -> int:
    path.mkdir(parents=True, exist_ok=True)
    reset_root(path)
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_SAMPLE_ROOT={path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the current Phase 2 validate-route packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_VALIDATE_ROUTE_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_VALIDATE_ROUTE_PACKET=pass")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_REMINDER_SURFACE_COUNT={len(REMINDER_SURFACES)}")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_VALIDATOR_COUNT={len(EXPECTED_MANIFEST_VALIDATORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
