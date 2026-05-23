#!/usr/bin/env python3
"""Keep the current Phase 2 cross packet explicit through closure-side surfaces."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
MAKEFILE = ROOT / "zigux" / "Makefile"

CHECKER_PATH = "scripts/zigux/check-phase2-cross-closure-packet.py"
FIXTURE_PATH = "zigux/tests/fixtures/phase2_cross_targets.json"
DIRECT_CHECKER_PATH = "scripts/zigux/check-phase2-cross.py"
ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase2-cross-selftest-alignment.py"
VALIDATE_PATH = "scripts/zigux/validate-phase2.py"
VALIDATE_CLOSURE_PATH = "scripts/zigux/validate-phase2-closure.py"
PHASE2_CROSS_ROUTE = "make -C zigux phase2-cross"
PHASE2_VALIDATE_ROUTE = "make -C zigux phase2-validate"
PHASE2_ROUTE = "make -C zigux phase2"

CLOSURE_MARKERS = (
    f"`{DIRECT_CHECKER_PATH}`",
    f"`{ALIGNMENT_CHECKER_PATH}`",
    f"`{FIXTURE_PATH}`",
    f"`{PHASE2_CROSS_ROUTE}`",
    f"`{PHASE2_VALIDATE_ROUTE}`",
    f"`{PHASE2_ROUTE}`",
)

VALIDATE_MARKERS = (
    f"\"{DIRECT_CHECKER_PATH}\",",
    f"\"{ALIGNMENT_CHECKER_PATH}\",",
    f"\"{FIXTURE_PATH}\",",
    f"\"{VALIDATE_CLOSURE_PATH}\",",
    "\"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\",",
)

CLOSURE_VALIDATE_MARKERS = (
    f"\"`{DIRECT_CHECKER_PATH}`\",",
    f"\"`{ALIGNMENT_CHECKER_PATH}`\",",
    f"\"`{FIXTURE_PATH}`\",",
    f"\"`{PHASE2_CROSS_ROUTE}`\",",
    f"\"`{PHASE2_VALIDATE_ROUTE}`\",",
    f"\"run: python3 {DIRECT_CHECKER_PATH} --self-test\",",
    f"\"run: python3 {DIRECT_CHECKER_PATH}\",",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(DIRECT_CHECKER_PATH).name} --self-test",
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(DIRECT_CHECKER_PATH).name}",
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(ALIGNMENT_CHECKER_PATH).name} --self-test",
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(ALIGNMENT_CHECKER_PATH).name}",
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(CHECKER_PATH).name} --self-test",
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(CHECKER_PATH).name}",
)

EXPECTED_SELF_TEST_CASE_COUNT = 11


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, PHASE2_MANIFEST))
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_SHAPE", "root")]

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return [("INVALID_MANIFEST_SHAPE", "present_surfaces")]

    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list) or not all(isinstance(item, str) for item in checkers):
        issues.append(("INVALID_MANIFEST_SHAPE", "checkers"))
    else:
        for marker in (DIRECT_CHECKER_PATH, ALIGNMENT_CHECKER_PATH):
            if marker not in checkers:
                issues.append(("MISSING_MANIFEST_CHECKER", marker))

    cross_support = present_surfaces.get("cross_route_support")
    if not isinstance(cross_support, list) or not all(isinstance(item, str) for item in cross_support):
        issues.append(("INVALID_MANIFEST_SHAPE", "cross_route_support"))
    else:
        for marker in (DIRECT_CHECKER_PATH, FIXTURE_PATH):
            if marker not in cross_support:
                issues.append(("MISSING_MANIFEST_CROSS_SUPPORT", marker))

    make_wrappers = present_surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list) or not all(isinstance(item, str) for item in make_wrappers):
        issues.append(("INVALID_MANIFEST_SHAPE", "make_wrappers"))
    else:
        for marker in ("zigux/Makefile", PHASE2_CROSS_ROUTE, PHASE2_VALIDATE_ROUTE, PHASE2_ROUTE):
            if marker not in make_wrappers:
                issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", marker))

    validators = present_surfaces.get("validators")
    if not isinstance(validators, list) or not all(isinstance(item, str) for item in validators):
        issues.append(("INVALID_MANIFEST_SHAPE", "validators"))
    else:
        for marker in (VALIDATE_PATH, VALIDATE_CLOSURE_PATH):
            if marker not in validators:
                issues.append(("MISSING_MANIFEST_VALIDATOR", marker))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_CLOSURE)),
            CLOSURE_MARKERS,
            "MISSING_CLOSURE_MARKER",
        )
    )
    issues.extend(collect_manifest_issues(root))
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_VALIDATE)),
            VALIDATE_MARKERS,
            "MISSING_VALIDATE_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_CLOSURE_VALIDATE)),
            CLOSURE_VALIDATE_MARKERS,
            "MISSING_CLOSURE_VALIDATE_MARKER",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_CLOSURE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_VALIDATE), "\n".join(VALIDATE_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE_VALIDATE), "\n".join(CLOSURE_VALIDATE_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, PHASE2_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "present_surfaces": {
                    "checkers": [DIRECT_CHECKER_PATH, ALIGNMENT_CHECKER_PATH],
                    "cross_route_support": [DIRECT_CHECKER_PATH, FIXTURE_PATH],
                    "make_wrappers": ["zigux/Makefile", PHASE2_CROSS_ROUTE, PHASE2_VALIDATE_ROUTE, PHASE2_ROUTE],
                    "validators": [VALIDATE_PATH, VALIDATE_CLOSURE_PATH],
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_closure_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_CLOSURE)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), CLOSURE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_VALIDATE)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), VALIDATE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_VALIDATE_MARKER", VALIDATE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_CLOSURE_VALIDATE)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), CLOSURE_VALIDATE_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_VALIDATE_MARKER", CLOSURE_VALIDATE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[-1]), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[-1]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[-1]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].remove(DIRECT_CHECKER_PATH)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_CHECKER", DIRECT_CHECKER_PATH) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["cross_route_support"].remove(FIXTURE_PATH)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_CROSS_SUPPORT", FIXTURE_PATH) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["make_wrappers"].remove(PHASE2_CROSS_ROUTE)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_MAKE_WRAPPER", PHASE2_CROSS_ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"].remove(VALIDATE_CLOSURE_PATH)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_VALIDATOR", VALIDATE_CLOSURE_PATH) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, PHASE2_MANIFEST).write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid manifest json did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CROSS_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 cross packet stays explicit through closure-side surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_CLOSURE_PACKET=pass")
    print(f"PHASE2_CROSS_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print("PHASE2_CROSS_CLOSURE_MANIFEST_KEYS=checkers,cross_route_support,make_wrappers,validators")
    print(f"PHASE2_CROSS_CLOSURE_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
