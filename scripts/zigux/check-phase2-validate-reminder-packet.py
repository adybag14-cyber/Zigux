#!/usr/bin/env python3
"""Guard the current Phase 2 validator reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
MAKEFILE = Path("zigux/Makefile")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    PHASE2_CLOSURE,
    PHASE2_NOTES,
    SCRIPTS_README,
    TESTS_README,
    VALIDATE_PHASE2,
    VALIDATE_PHASE2_CLOSURE,
    MAKEFILE,
    TOOL_MANIFEST,
)

PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

PHASE2_NOTES_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

VALIDATE_PHASE2_MARKERS = (
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)

VALIDATE_PHASE2_CLOSURE_MARKERS = (
    'Path("scripts/zigux/validate-phase2.py")',
    'Path("scripts/zigux/validate-phase2-closure.py")',
    'Path("zigux/Makefile")',
    'Path("zigux/tests/fixtures/phase2_tool_manifest.json")',
)

MAKEFILE_MARKERS = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

MANIFEST_MAKE_WRAPPERS = (
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


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def add_missing_markers(
    issues: list[tuple[str, str]],
    code: str,
    text: str,
    markers: tuple[str, ...],
) -> None:
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))


def require_manifest_list(
    issues: list[tuple[str, str]],
    manifest: dict[str, object],
    key: str,
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


def expect_markers_in_list(
    issues: list[tuple[str, str]],
    code: str,
    label: str,
    actual: list[str] | None,
    expected: tuple[str, ...],
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append((code, f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    closure_text = read_text(resolve(root, PHASE2_CLOSURE))
    notes_text = read_text(resolve(root, PHASE2_NOTES))
    scripts_readme_text = read_text(resolve(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve(root, TESTS_README))
    validate_text = read_text(resolve(root, VALIDATE_PHASE2))
    validate_closure_text = read_text(resolve(root, VALIDATE_PHASE2_CLOSURE))
    makefile_text = read_text(resolve(root, MAKEFILE))
    manifest = read_json(resolve(root, TOOL_MANIFEST))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    add_missing_markers(issues, "MISSING_PHASE2_CLOSURE_MARKER", closure_text, PHASE2_CLOSURE_MARKERS)
    add_missing_markers(issues, "MISSING_PHASE2_NOTES_MARKER", notes_text, PHASE2_NOTES_MARKERS)
    add_missing_markers(
        issues,
        "MISSING_SCRIPTS_README_MARKER",
        scripts_readme_text,
        SCRIPTS_README_MARKERS,
    )
    add_missing_markers(
        issues,
        "MISSING_TESTS_README_MARKER",
        tests_readme_text,
        TESTS_README_MARKERS,
    )
    add_missing_markers(
        issues,
        "MISSING_VALIDATE_PHASE2_MARKER",
        validate_text,
        VALIDATE_PHASE2_MARKERS,
    )
    add_missing_markers(
        issues,
        "MISSING_VALIDATE_PHASE2_CLOSURE_MARKER",
        validate_closure_text,
        VALIDATE_PHASE2_CLOSURE_MARKERS,
    )
    add_missing_markers(issues, "MISSING_MAKEFILE_MARKER", makefile_text, MAKEFILE_MARKERS)

    expect_markers_in_list(
        issues,
        "MISSING_MANIFEST_SURFACE",
        "validators",
        require_manifest_list(issues, manifest, "validators"),
        MANIFEST_VALIDATORS,
    )
    expect_markers_in_list(
        issues,
        "MISSING_MANIFEST_SURFACE",
        "make_wrappers",
        require_manifest_list(issues, manifest, "make_wrappers"),
        MANIFEST_MAKE_WRAPPERS,
    )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_VALIDATE_REMINDER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, PHASE2_CLOSURE), "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(resolve(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve(root, VALIDATE_PHASE2), "\n".join(VALIDATE_PHASE2_MARKERS) + "\n")
    write_text(
        resolve(root, VALIDATE_PHASE2_CLOSURE),
        "\n".join(VALIDATE_PHASE2_CLOSURE_MARKERS) + "\n",
    )
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(
            {
                "present_surfaces": {
                    "validators": list(MANIFEST_VALIDATORS),
                    "make_wrappers": list(MANIFEST_MAKE_WRAPPERS),
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_reminder_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = resolve(root, PHASE2_CLOSURE)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), PHASE2_CLOSURE_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_PHASE2_CLOSURE_MARKER", PHASE2_CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve(root, PHASE2_NOTES)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), PHASE2_NOTES_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_PHASE2_NOTES_MARKER", PHASE2_NOTES_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve(root, SCRIPTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), SCRIPTS_README_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve(root, TESTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), TESTS_README_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_TESTS_README_MARKER", TESTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve(root, VALIDATE_PHASE2)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), VALIDATE_PHASE2_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATE_PHASE2_MARKER", VALIDATE_PHASE2_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve(root, VALIDATE_PHASE2_CLOSURE)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), VALIDATE_PHASE2_CLOSURE_MARKERS[0]),
            encoding="utf-8",
        )
        assert (
            "MISSING_VALIDATE_PHASE2_CLOSURE_MARKER",
            VALIDATE_PHASE2_CLOSURE_MARKERS[0],
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve(root, MAKEFILE)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        del payload["present_surfaces"]["validators"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_SHAPE", "validators") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["make_wrappers"] = ["make -C zigux phase2-validate"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "make_wrappers:make -C zigux phase2",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve(root, PHASE2_CLOSURE).unlink()
        assert ("MISSING_REQUIRED_FILE", PHASE2_CLOSURE.as_posix()) in collect_issues(root)
        checks_run += 1

    print("PHASE2_VALIDATE_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_VALIDATE_REMINDER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_VALIDATE_REMINDER_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    manifest = read_json(resolve(root, TOOL_MANIFEST))
    assert isinstance(manifest, dict)
    present_surfaces = manifest["present_surfaces"]
    assert isinstance(present_surfaces, dict)
    validators = present_surfaces["validators"]
    make_wrappers = present_surfaces["make_wrappers"]
    assert isinstance(validators, list)
    assert isinstance(make_wrappers, list)

    print("PHASE2_VALIDATE_REMINDER_PACKET=pass")
    print(f"PHASE2_VALIDATE_REMINDER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_VALIDATE_REMINDER_PACKET_VALIDATOR_COUNT={len(validators)}")
    print(f"PHASE2_VALIDATE_REMINDER_PACKET_MAKE_WRAPPER_COUNT={len(make_wrappers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
