#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_PINNING = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"
TESTS_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`make -C zigux phase2-cross`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the fixture-backed tool-manifest, artifact-tools, cross-target, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

TOOLCHAIN_PINNING_MARKERS = (
    'ROOT / "scripts" / "zigux" / "install-zig.py",',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross.py",',
    'ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",',
    '"scripts/zigux/install-zig.py"',
    '"scripts/zigux/check-phase2-cross.py"',
    '"zigux/tests/fixtures/phase2_cross_targets.json"',
    '"repo_reality_gaps": [],',
)

TESTS_ALIGNMENT_MARKERS = (
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    '"keep the fixture-backed tool-manifest, artifact-tools, cross-target, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",',
)

EXPECTED_FIXTURE = {
    "phase": "Phase 2",
    "status": "active",
    "route": "make -C zigux phase2-cross",
    "archive_target_scope": ["x86_64-linux"],
    "cross_targets": {
        "x86_64-linux": "archive_required",
        "aarch64-linux": "route_contract_only",
    },
}


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def collect_fixture_issues(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_CROSS_TARGET_FIXTURE", type(payload).__name__)]
    if payload.get("phase") != EXPECTED_FIXTURE["phase"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_FIXTURE["status"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_FIXTURE["route"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != EXPECTED_FIXTURE["archive_target_scope"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or not target:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if route != EXPECTED_FIXTURE["route"]:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        actual_modes[target] = validation_mode

    if actual_modes != EXPECTED_FIXTURE["cross_targets"]:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_NOTES)),
            PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINES",
            "DUPLICATE_MAKEFILE_LINES",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TOOLCHAIN_PINNING)),
            TOOLCHAIN_PINNING_MARKERS,
            "MISSING_TOOLCHAIN_PINNING_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_ALIGNMENT)),
            TESTS_ALIGNMENT_MARKERS,
            "MISSING_TESTS_ALIGNMENT_MARKERS",
        )
    )
    issues.extend(collect_fixture_issues(read_json(resolve_path(root, CROSS_TARGETS))))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_PINNING), "\n".join(TOOLCHAIN_PINNING_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_ALIGNMENT), "\n".join(TESTS_ALIGNMENT_MARKERS) + "\n")
    write_text(
        resolve_path(root, CROSS_TARGETS),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": "make -C zigux phase2-cross",
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": "make -C zigux phase2-cross",
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": "make -C zigux phase2-cross",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


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


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(PHASE2_NOTES_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + len(TOOLCHAIN_PINNING_MARKERS)
        + len(TESTS_ALIGNMENT_MARKERS)
        + 4
        + 6
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_PHASE2_NOTES_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in TOOLCHAIN_PINNING_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TOOLCHAIN_PINNING)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TOOLCHAIN_PINNING_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_ALIGNMENT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_ALIGNMENT)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_ALIGNMENT_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase X"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "phase") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"].append(payload["cross_targets"][0].copy())
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in issues
        checks_run += 1

        for path in (
            PHASE2_NOTES,
            TESTS_README,
            MAKEFILE,
            TOOLCHAIN_PINNING,
            TESTS_ALIGNMENT,
            CROSS_TARGETS,
        ):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 returned direct cross-route packet aligned across the live reminder guards."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_ALIGNMENT=pass")
    print(
        "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT="
        f"{len(PHASE2_NOTES_MARKERS) + len(TESTS_README_MARKERS) + len(MAKEFILE_LINES) + len(TOOLCHAIN_PINNING_MARKERS) + len(TESTS_ALIGNMENT_MARKERS)}"
    )
    print("PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
