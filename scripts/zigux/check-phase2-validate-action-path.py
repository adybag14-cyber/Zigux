#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 validator action path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TESTS_README = Path("zigux/tests/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")

REQUIRED_FILES = (
    WORKFLOW,
    MAKEFILE,
    PHASE2_CLOSURE,
    BOOTSTRAP_NOTES,
    TESTS_README,
    TOOL_MANIFEST,
    VALIDATE_PHASE2,
    VALIDATE_PHASE2_CLOSURE,
)

REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase2-closure.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_CLOSURE_MARKERS = (
    "`python3 scripts/zigux/validate-phase2.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_TESTS_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

EXPECTED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_MAKE_WRAPPERS = (
    "zigux/Makefile",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
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


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE))
    bootstrap_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    tests_text = read_text(resolve(root, TESTS_README))
    manifest = read_json(resolve(root, TOOL_MANIFEST))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    workflow_indices: list[int] = []
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        workflow_indices.append(exact_line_index(workflow_text, marker) or 0)
    if len(workflow_indices) == len(REQUIRED_WORKFLOW_LINES) and workflow_indices != sorted(
        workflow_indices
    ):
        issues.append(("WORKFLOW_ORDER_MISMATCH", "phase2-validator-route-order"))

    makefile_indices: list[int] = []
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
            continue
        makefile_indices.append(exact_line_index(makefile_text, marker) or 0)
    if len(makefile_indices) == len(REQUIRED_MAKEFILE_LINES) and makefile_indices != sorted(
        makefile_indices
    ):
        issues.append(("MAKEFILE_ORDER_MISMATCH", "phase2-validator-make-order"))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_BOOTSTRAP_MARKERS:
        if marker not in bootstrap_text:
            issues.append(("MISSING_BOOTSTRAP_MARKER", marker))

    for marker in REQUIRED_TESTS_MARKERS:
        if marker not in tests_text:
            issues.append(("MISSING_TESTS_MARKER", marker))

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    expect_subset(
        issues,
        "validators",
        require_manifest_list(issues, manifest, "validators"),
        EXPECTED_VALIDATORS,
    )
    expect_subset(
        issues,
        "make_wrappers",
        require_manifest_list(issues, manifest, "make_wrappers"),
        EXPECTED_MAKE_WRAPPERS,
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_VALIDATE_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, WORKFLOW), "name: zigux-bootstrap\n" + "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(
        resolve(root, MAKEFILE),
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                *REQUIRED_MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(resolve(root, PHASE2_CLOSURE), "# closure\n" + "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(
        resolve(root, BOOTSTRAP_NOTES),
        "# bootstrap\n" + "\n".join(REQUIRED_BOOTSTRAP_MARKERS) + "\n",
    )
    write_text(resolve(root, TESTS_README), "# tests\n" + "\n".join(REQUIRED_TESTS_MARKERS) + "\n")
    write_text(resolve(root, VALIDATE_PHASE2), "present\n")
    write_text(resolve(root, VALIDATE_PHASE2_CLOSURE), "present\n")
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(
            {
                "repo_reality_gaps": [],
                "present_surfaces": {
                    "validators": list(EXPECTED_VALIDATORS),
                    "make_wrappers": list(EXPECTED_MAKE_WRAPPERS),
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + 1
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + 1
        + len(REQUIRED_CLOSURE_MARKERS)
        + len(REQUIRED_BOOTSTRAP_MARKERS)
        + len(REQUIRED_TESTS_MARKERS)
        + 3
        + len(REQUIRED_FILES)
        + 1
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker, "run: echo missing"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            "name: zigux-bootstrap\n" + "\n".join(reversed(REQUIRED_WORKFLOW_LINES)) + "\n",
            encoding="utf-8",
        )
        assert ("WORKFLOW_ORDER_MISMATCH", "phase2-validator-route-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE)
        makefile_path.write_text(
            "\n".join(
                (
                    "PYTHON ?= python3",
                    "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                    "",
                    *reversed(REQUIRED_MAKEFILE_LINES),
                )
            )
            + "\n",
            encoding="utf-8",
        )
        assert ("MAKEFILE_ORDER_MISMATCH", "phase2-validator-make-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_CLOSURE_MARKERS:
            build_sample_root(root)
            path = resolve(root, PHASE2_CLOSURE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_BOOTSTRAP_MARKERS:
            build_sample_root(root)
            path = resolve(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_TESTS_MARKERS:
            build_sample_root(root)
            path = resolve(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_MARKER", marker) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"].remove(EXPECTED_VALIDATORS[0])
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", f"validators:{EXPECTED_VALIDATORS[0]}") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["make_wrappers"].remove(EXPECTED_MAKE_WRAPPERS[1])
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", f"make_wrappers:{EXPECTED_MAKE_WRAPPERS[1]}") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["repo_reality_gaps"] = ["unexpected"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "UNEXPECTED_MANIFEST_GAPS" for code, _ in collect_issues(root))
        checks += 1

        for rel in REQUIRED_FILES:
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        manifest_path.write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid manifest JSON did not abort")

    assert checks == expected_case_count
    print("PHASE2_VALIDATE_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_VALIDATE_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current Phase 2 validator action path stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_VALIDATE_ACTION_PATH_SAMPLE_ROOT=written")
        print(f"PHASE2_VALIDATE_ACTION_PATH_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATE_ACTION_PATH=pass")
    print(f"PHASE2_VALIDATE_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATE_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_VALIDATE_ACTION_PATH_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE2_VALIDATE_ACTION_PATH_BOOTSTRAP_MARKER_COUNT={len(REQUIRED_BOOTSTRAP_MARKERS)}")
    print(f"PHASE2_VALIDATE_ACTION_PATH_TESTS_MARKER_COUNT={len(REQUIRED_TESTS_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
