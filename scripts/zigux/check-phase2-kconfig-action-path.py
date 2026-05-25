#!/usr/bin/env python3
"""Guard the current Phase 2 kconfig action path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
DOCS_README = Path("Documentation/zigux/README.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
CONF_MANIFEST = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")
CONFDATA_MANIFEST = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")
KCONFIG_CASES = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")

REQUIRED_FILES = (
    WORKFLOW,
    MAKEFILE,
    DOCS_README,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST,
    CONF_MANIFEST,
    CONFDATA_MANIFEST,
    KCONFIG_CASES,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "run: make -C zigux phase2-kconfig",
)

MAKEFILE_LINES = (
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
)

MARKER_GROUPS: dict[str, tuple[Path, tuple[str, ...]]] = {
    "docs": (
        DOCS_README,
        (
            "`scripts/zigux/check-kconfig-bridge.py`",
            "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
            "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
            "`scripts/zigux/kconfig/conf_bridge.zig`",
            "`scripts/zigux/kconfig/confdata_bridge.zig`",
            "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
            "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
            "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
            "`make -C zigux phase2-kconfig`",
        ),
    ),
    "closure": (
        PHASE2_CLOSURE,
        (
            "`scripts/zigux/check-kconfig-bridge.py`",
            "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
            "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
            "`zig test scripts/zigux/kconfig/conf_bridge.zig`",
            "`zig test scripts/zigux/kconfig/confdata_bridge.zig`",
            "`make -C zigux phase2-kconfig`",
        ),
    ),
    "review": (
        REVIEW_CHECKLIST,
        (
            "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
            "`scripts/zigux/kconfig/conf_bridge.zig`",
            "`scripts/zigux/kconfig/confdata_bridge.zig`",
            "`make -C zigux phase2-kconfig`",
        ),
    ),
    "scripts": (
        SCRIPTS_README,
        (
            "`scripts/zigux/check-kconfig-bridge.py`",
            "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
            "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
            "`scripts/zigux/kconfig/conf_bridge.zig`",
            "`scripts/zigux/kconfig/confdata_bridge.zig`",
            "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
            "`make -C zigux phase2-kconfig`",
        ),
    ),
    "tests": (
        TESTS_README,
        (
            "`scripts/zigux/check-kconfig-bridge.py`",
            "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
            "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
            "`scripts/zigux/kconfig/conf_bridge.zig`",
            "`scripts/zigux/kconfig/confdata_bridge.zig`",
            "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
            "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
            "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
            "`make -C zigux phase2-kconfig`",
        ),
    ),
}

EXPECT_MANIFEST = {
    "checkers": (
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    ),
    "bridge_helpers": (
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
    ),
    "fixture_roster": (
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    ),
    "make_wrappers": ("make -C zigux phase2-kconfig",),
    "review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
}


def path(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(root: Path, rel: Path) -> str:
    return path(root, rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: Path) -> object:
    return json.loads(read_text(root, rel))


def write(pathname: Path, content: str) -> None:
    pathname.parent.mkdir(parents=True, exist_ok=True)
    pathname.write_text(content, encoding="utf-8")


def add_line_issues(issues: list[tuple[str, str]], text: str, code: str, lines: tuple[str, ...]) -> None:
    for line in lines:
        count = sum(1 for entry in text.splitlines() if entry.strip() == line)
        if count == 0:
            issues.append((code, line))
        elif count > 1:
            issues.append((f"DUPLICATE_{code}", f"{line}:count={count}"))


def add_marker_issues(issues: list[tuple[str, str]], text: str, code: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not path(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    add_line_issues(issues, read_text(root, WORKFLOW), "WORKFLOW_LINE", WORKFLOW_LINES)
    add_line_issues(issues, read_text(root, MAKEFILE), "MAKEFILE_LINE", MAKEFILE_LINES)

    for code, (rel, markers) in MARKER_GROUPS.items():
        add_marker_issues(issues, read_text(root, rel), f"MISSING_{code.upper()}_MARKER", markers)

    tool_manifest = read_json(root, TOOL_MANIFEST)
    if not isinstance(tool_manifest, dict):
        return [("INVALID_TOOL_MANIFEST", type(tool_manifest).__name__)]
    surfaces = tool_manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return [("INVALID_TOOL_MANIFEST", "present_surfaces")]
    for key, expected in EXPECT_MANIFEST.items():
        actual = surfaces.get(key)
        if not isinstance(actual, list):
            issues.append(("INVALID_TOOL_MANIFEST_SURFACE", key))
            continue
        for item in expected:
            if item not in actual:
                issues.append(("MISSING_TOOL_MANIFEST_SURFACE", f"{key}:{item}"))

    conf_manifest = read_json(root, CONF_MANIFEST)
    confdata_manifest = read_json(root, CONFDATA_MANIFEST)
    cases = read_json(root, KCONFIG_CASES)
    if not isinstance(conf_manifest, dict):
        issues.append(("INVALID_CONF_MANIFEST", type(conf_manifest).__name__))
    if not isinstance(confdata_manifest, dict):
        issues.append(("INVALID_CONFDATA_MANIFEST", type(confdata_manifest).__name__))
    if not isinstance(cases, dict):
        issues.append(("INVALID_KCONFIG_CASES", type(cases).__name__))
        return issues

    if conf_manifest.get("tool") != "scripts/zigux/kconfig/conf_bridge.zig":
        issues.append(("CONF_MANIFEST_TOOL_MISMATCH", repr(conf_manifest.get("tool"))))
    if confdata_manifest.get("tool") != "scripts/zigux/kconfig/confdata_bridge.zig":
        issues.append(("CONFDATA_MANIFEST_TOOL_MISMATCH", repr(confdata_manifest.get("tool"))))
    if conf_manifest.get("fixture_case_source") != "zigux/tests/fixtures/kconfig_bridge/cases.json":
        issues.append(("CONF_MANIFEST_SOURCE_MISMATCH", repr(conf_manifest.get("fixture_case_source"))))
    if confdata_manifest.get("fixture_case_source") != "zigux/tests/fixtures/kconfig_bridge/cases.json":
        issues.append(("CONFDATA_MANIFEST_SOURCE_MISMATCH", repr(confdata_manifest.get("fixture_case_source"))))

    conf_cases = cases.get("conf_cases")
    confdata_cases = cases.get("confdata_cases")
    if not isinstance(conf_cases, list):
        issues.append(("INVALID_KCONFIG_CASES", "conf_cases"))
    elif conf_manifest.get("case_count") != len(conf_cases):
        issues.append(("CONF_CASE_COUNT_MISMATCH", f"actual={conf_manifest.get('case_count')!r}:expected={len(conf_cases)!r}"))
    if not isinstance(confdata_cases, list):
        issues.append(("INVALID_KCONFIG_CASES", "confdata_cases"))
    elif confdata_manifest.get("case_count") != len(confdata_cases):
        issues.append(("CONFDATA_CASE_COUNT_MISMATCH", f"actual={confdata_manifest.get('case_count')!r}:expected={len(confdata_cases)!r}"))

    return issues


def emit(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_sample_root(root: Path) -> None:
    write(path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write(path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    for rel, markers in MARKER_GROUPS.values():
        write(path(root, rel), "\n".join(markers) + "\n")
    write(
        path(root, TOOL_MANIFEST),
        json.dumps({"present_surfaces": {key: list(value) for key, value in EXPECT_MANIFEST.items()}}, indent=2) + "\n",
    )
    write(
        path(root, CONF_MANIFEST),
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/conf_bridge.zig",
                "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
                "case_count": 16,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        path(root, CONFDATA_MANIFEST),
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
                "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
                "case_count": 15,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        path(root, KCONFIG_CASES),
        json.dumps({"conf_cases": [{} for _ in range(16)], "confdata_cases": [{} for _ in range(15)]}, indent=2) + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_action_path_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        cases = [
            (WORKFLOW, WORKFLOW_LINES[0], "MISSING_WORKFLOW_LINE"),
            (MAKEFILE, MAKEFILE_LINES[0], "MISSING_MAKEFILE_LINE"),
            (DOCS_README, MARKER_GROUPS["docs"][1][0], "MISSING_DOCS_MARKER"),
            (PHASE2_CLOSURE, MARKER_GROUPS["closure"][1][0], "MISSING_CLOSURE_MARKER"),
            (REVIEW_CHECKLIST, MARKER_GROUPS["review"][1][0], "MISSING_REVIEW_MARKER"),
            (SCRIPTS_README, MARKER_GROUPS["scripts"][1][0], "MISSING_SCRIPTS_MARKER"),
            (TESTS_README, MARKER_GROUPS["tests"][1][0], "MISSING_TESTS_MARKER"),
        ]
        for rel, marker, code in cases:
            write_sample_root(root)
            target = path(root, rel)
            target.write_text(target.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert collect_issues(root)
            checks += 1

        write_sample_root(root)
        payload = json.loads(path(root, TOOL_MANIFEST).read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].pop()
        write(path(root, TOOL_MANIFEST), json.dumps(payload, indent=2) + "\n")
        assert any(entry[0] == "MISSING_TOOL_MANIFEST_SURFACE" for entry in collect_issues(root))
        checks += 1

        write_sample_root(root)
        payload = json.loads(path(root, CONF_MANIFEST).read_text(encoding="utf-8"))
        payload["tool"] = "drifted"
        write(path(root, CONF_MANIFEST), json.dumps(payload, indent=2) + "\n")
        assert ("CONF_MANIFEST_TOOL_MISMATCH", "'drifted'") in collect_issues(root)
        checks += 1

        write_sample_root(root)
        payload = json.loads(path(root, CONFDATA_MANIFEST).read_text(encoding="utf-8"))
        payload["case_count"] = 99
        write(path(root, CONFDATA_MANIFEST), json.dumps(payload, indent=2) + "\n")
        assert any(entry[0] == "CONFDATA_CASE_COUNT_MISMATCH" for entry in collect_issues(root))
        checks += 1

        write_sample_root(root)
        write(path(root, KCONFIG_CASES), json.dumps({"conf_cases": [], "confdata_cases": []}, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(entry[0] == "CONF_CASE_COUNT_MISMATCH" for entry in issues)
        assert any(entry[0] == "CONFDATA_CASE_COUNT_MISMATCH" for entry in issues)
        checks += 1

        write_sample_root(root)
        path(root, TOOL_MANIFEST).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except json.JSONDecodeError:
            checks += 1
        else:
            raise AssertionError("invalid manifest json did not fail")

    print("PHASE2_KCONFIG_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 2 kconfig action path stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print("PHASE2_KCONFIG_ACTION_PATH_SAMPLE_ROOT=written")
        print(f"PHASE2_KCONFIG_ACTION_PATH_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit(issues)
    print("PHASE2_KCONFIG_ACTION_PATH=pass")
    print(f"PHASE2_KCONFIG_ACTION_PATH_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ACTION_PATH_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ACTION_PATH_DOCS_MARKER_COUNT={len(MARKER_GROUPS['docs'][1])}")
    print(f"PHASE2_KCONFIG_ACTION_PATH_CLOSURE_MARKER_COUNT={len(MARKER_GROUPS['closure'][1])}")
    print(f"PHASE2_KCONFIG_ACTION_PATH_REVIEW_MARKER_COUNT={len(MARKER_GROUPS['review'][1])}")
    print(f"PHASE2_KCONFIG_ACTION_PATH_SCRIPTS_MARKER_COUNT={len(MARKER_GROUPS['scripts'][1])}")
    print(f"PHASE2_KCONFIG_ACTION_PATH_TESTS_MARKER_COUNT={len(MARKER_GROUPS['tests'][1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
