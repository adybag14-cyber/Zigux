#!/usr/bin/env python3
"""Guard the Phase 2 kconfig allconfig helper action path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
PHASE2_VALIDATE = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE = Path("scripts/zigux/validate-phase2-closure.py")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
HELPER_PACKET = Path("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py")

REQUIRED_FILES = (
    WORKFLOW,
    MAKEFILE,
    PHASE2_VALIDATE,
    PHASE2_CLOSURE_VALIDATE,
    PHASE2_TOOL_MANIFEST,
    HELPER_PACKET,
)

REQUIRED_VALIDATE_LINES = (
    f"\"{HELPER_PACKET.as_posix()}\",",
    f"\"run: python3 {HELPER_PACKET.as_posix()} --self-test\",",
    f"\"run: python3 {HELPER_PACKET.as_posix()}\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py\",",
)

REQUIRED_CLOSURE_LINES = (
    f"\"`{HELPER_PACKET.as_posix()}`\",",
    f"KCONFIG_ALLCONFIG_HELPER_PACKET_REL = Path(\"{HELPER_PACKET.as_posix()}\")",
)

REQUIRED_WORKFLOW_LINES = (
    f"run: python3 {HELPER_PACKET.as_posix()} --self-test",
    f"run: python3 {HELPER_PACKET.as_posix()}",
)

REQUIRED_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
)

EXPECTED_MANIFEST_CHECKERS = (HELPER_PACKET.as_posix(),)
EXPECTED_MANIFEST_VALIDATORS = (
    PHASE2_VALIDATE.as_posix(),
    PHASE2_CLOSURE_VALIDATE.as_posix(),
)
EXPECTED_MANIFEST_MAKE_WRAPPERS = (
    MAKEFILE.as_posix(),
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-validate",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def exact_line_index(text: str, marker: str) -> int | None:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return None


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


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError("swap markers not found")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_subset(
    issues: list[tuple[str, str]], label: str, actual: list[str] | None, expected: tuple[str, ...]
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_exact_line_issues(
    issues: list[tuple[str, str]], text: str, code_prefix: str, markers: tuple[str, ...], order_label: str
) -> None:
    indices: list[int] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((f"MISSING_{code_prefix}", marker))
            continue
        if count != 1:
            issues.append((f"DUPLICATE_{code_prefix}", f"{marker}:count={count}"))
            continue
        indices.append(exact_line_index(text, marker) or 0)
    if len(indices) == len(markers) and indices != sorted(indices):
        issues.append((f"{code_prefix}_ORDER_MISMATCH", order_label))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    validate_text = read_text(resolve(root, PHASE2_VALIDATE))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_VALIDATE))
    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    manifest = read_json(resolve(root, PHASE2_TOOL_MANIFEST))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    collect_exact_line_issues(
        issues,
        validate_text,
        "VALIDATE_MARKER",
        REQUIRED_VALIDATE_LINES,
        "phase2-kconfig-allconfig-validate-order",
    )
    collect_exact_line_issues(
        issues,
        closure_text,
        "CLOSURE_VALIDATE_MARKER",
        REQUIRED_CLOSURE_LINES,
        "phase2-kconfig-allconfig-closure-order",
    )
    collect_exact_line_issues(
        issues,
        workflow_text,
        "WORKFLOW_LINE",
        REQUIRED_WORKFLOW_LINES,
        "phase2-kconfig-allconfig-workflow-order",
    )
    collect_exact_line_issues(
        issues,
        makefile_text,
        "MAKEFILE_LINE",
        REQUIRED_MAKEFILE_LINES,
        "phase2-kconfig-allconfig-makefile-order",
    )

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    expect_subset(
        issues,
        "checkers",
        require_manifest_list(issues, manifest, "checkers"),
        EXPECTED_MANIFEST_CHECKERS,
    )
    expect_subset(
        issues,
        "validators",
        require_manifest_list(issues, manifest, "validators"),
        EXPECTED_MANIFEST_VALIDATORS,
    )
    expect_subset(
        issues,
        "make_wrappers",
        require_manifest_list(issues, manifest, "make_wrappers"),
        EXPECTED_MANIFEST_MAKE_WRAPPERS,
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, HELPER_PACKET), "# helper present\n")
    write_text(resolve(root, PHASE2_VALIDATE), "\n".join(REQUIRED_VALIDATE_LINES) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE_VALIDATE), "\n".join(REQUIRED_CLOSURE_LINES) + "\n")
    write_text(resolve(root, WORKFLOW), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(
        resolve(root, PHASE2_TOOL_MANIFEST),
        json.dumps(
            {
                "repo_reality_gaps": [],
                "present_surfaces": {
                    "checkers": [HELPER_PACKET.as_posix()],
                    "validators": [
                        PHASE2_VALIDATE.as_posix(),
                        PHASE2_CLOSURE_VALIDATE.as_posix(),
                    ],
                    "make_wrappers": [
                        MAKEFILE.as_posix(),
                        "make -C zigux phase2-kconfig",
                        "make -C zigux phase2-validate",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    expected_case_count = 11
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_allconfig_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        (resolve(root, HELPER_PACKET)).unlink()
        expect_issue(root, ("MISSING_REQUIRED_FILE", HELPER_PACKET.as_posix()))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, PHASE2_VALIDATE),
            replace_exact_line(read_text(resolve(root, PHASE2_VALIDATE)), REQUIRED_VALIDATE_LINES[0], "\"placeholder\","),
        )
        expect_issue(root, ("MISSING_VALIDATE_MARKER", REQUIRED_VALIDATE_LINES[0]))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, PHASE2_VALIDATE),
            duplicate_exact_line(read_text(resolve(root, PHASE2_VALIDATE)), REQUIRED_VALIDATE_LINES[0]),
        )
        expect_issue(
            root,
            ("DUPLICATE_VALIDATE_MARKER", f"{REQUIRED_VALIDATE_LINES[0]}:count=2"),
        )
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, PHASE2_VALIDATE),
            swap_exact_lines(
                read_text(resolve(root, PHASE2_VALIDATE)),
                REQUIRED_VALIDATE_LINES[0],
                REQUIRED_VALIDATE_LINES[1],
            ),
        )
        expect_issue(root, ("VALIDATE_MARKER_ORDER_MISMATCH", "phase2-kconfig-allconfig-validate-order"))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, PHASE2_CLOSURE_VALIDATE),
            replace_exact_line(read_text(resolve(root, PHASE2_CLOSURE_VALIDATE)), REQUIRED_CLOSURE_LINES[0], "placeholder"),
        )
        expect_issue(root, ("MISSING_CLOSURE_VALIDATE_MARKER", REQUIRED_CLOSURE_LINES[0]))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, WORKFLOW),
            duplicate_exact_line(read_text(resolve(root, WORKFLOW)), REQUIRED_WORKFLOW_LINES[0]),
        )
        expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[0]}:count=2"))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, WORKFLOW),
            swap_exact_lines(read_text(resolve(root, WORKFLOW)), REQUIRED_WORKFLOW_LINES[0], REQUIRED_WORKFLOW_LINES[1]),
        )
        expect_issue(root, ("WORKFLOW_LINE_ORDER_MISMATCH", "phase2-kconfig-allconfig-workflow-order"))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, MAKEFILE),
            duplicate_exact_line(read_text(resolve(root, MAKEFILE)), REQUIRED_MAKEFILE_LINES[0]),
        )
        expect_issue(root, ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[0]}:count=2"))
        checks += 1

        build_sample_root(root)
        write_text(
            resolve(root, MAKEFILE),
            swap_exact_lines(read_text(resolve(root, MAKEFILE)), REQUIRED_MAKEFILE_LINES[0], REQUIRED_MAKEFILE_LINES[1]),
        )
        expect_issue(root, ("MAKEFILE_LINE_ORDER_MISMATCH", "phase2-kconfig-allconfig-makefile-order"))
        checks += 1

        build_sample_root(root)
        manifest = json.loads(read_text(resolve(root, PHASE2_TOOL_MANIFEST)))
        manifest["present_surfaces"]["checkers"] = []
        write_text(resolve(root, PHASE2_TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")
        expect_issue(root, ("MISSING_MANIFEST_SURFACE", f"checkers:{HELPER_PACKET.as_posix()}"))
        checks += 1

    assert checks == expected_case_count
    print("PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 2 kconfig allconfig helper packet stays wired through "
            "the shared validators, workflow, Makefile, and tool manifest."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH=pass")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_VALIDATE_MARKER_COUNT={len(REQUIRED_VALIDATE_LINES)}")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_LINES)}")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_MAKEFILE_MARKER_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
