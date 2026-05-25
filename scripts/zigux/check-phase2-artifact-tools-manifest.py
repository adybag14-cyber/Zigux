#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
PRIMARY_TOOL = Path("scripts/zigux/artifact_diff.py")

REQUIRED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "artifact-diff support for fixture-backed scripts/zigux validation",
}

REQUIRED_TOOLING = {
    "primary": [PRIMARY_TOOL.as_posix()],
    "consumers": [
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-fixdep-diff.py",
    ],
    "checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],
    "supported_modes": ["text", "json", "bytes"],
}

PRIMARY_TOOL_MARKERS = (
    'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    '    "legacy_sha256_alias",',
    "def normalize_mode(mode: str) -> str:",
    "    return LEGACY_MODE_ALIASES.get(mode, mode)",
)

EXPECTED_CONSUMER_MARKERS = {
    "scripts/zigux/check-kconfig-bridge.py": (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(actual)], cwd=str(ROOT))',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(actual), str(repeat)], cwd=str(ROOT))',
    ),
    "scripts/zigux/check-fixdep-diff.py": (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "text", str(expected), str(actual)], cwd=str(ROOT))',
    ),
}

REQUIRED_NOTE_MARKERS = (
    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
)


def read_manifest(path: Path) -> tuple[dict | None, tuple[str, str] | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError:
        return None, ("INVALID_MANIFEST_JSON", path.as_posix())


def find_duplicate_strings(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def resolve_manifest_path(root: Path, relative_path: str) -> Path:
    return root / Path(relative_path)


def collect_tooling_entry_issues(root: Path, category: str, actual: object, expected: list[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(actual, list):
        return [("MISSING_TOOLING", category)]

    non_string_entries = [repr(entry) for entry in actual if not isinstance(entry, str)]
    for entry in non_string_entries:
        issues.append(("INVALID_TOOLING_ENTRY", f"{category}:{entry}"))

    string_entries = [entry for entry in actual if isinstance(entry, str)]
    expected_set = set(expected)
    for entry in find_duplicate_strings(string_entries):
        issues.append(("DUPLICATE_TOOLING_ENTRY", f"{category}:{entry}"))
    for entry in expected:
        if entry not in string_entries:
            issues.append(("TOOLING_MISMATCH", f"{category}:{entry}"))
    for entry in string_entries:
        if entry not in expected_set:
            issues.append(("UNEXPECTED_TOOLING_ENTRY", f"{category}:{entry}"))
        if not resolve_manifest_path(root, entry).exists():
            issues.append(("MISSING_TOOL_PATH", f"{category}:{entry}"))
    return issues


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_primary_tool_marker_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    path = resolve_manifest_path(root, PRIMARY_TOOL.as_posix())
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return issues
    for marker in PRIMARY_TOOL_MARKERS:
        count = count_exact_occurrences(text, marker)
        if count == 0:
            issues.append(("MISSING_PRIMARY_TOOL_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_PRIMARY_TOOL_MARKER", f"{marker}:count={count}"))
    return issues


def collect_consumer_marker_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for relative_path, markers in EXPECTED_CONSUMER_MARKERS.items():
        path = resolve_manifest_path(root, relative_path)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        for marker in markers:
            count = count_exact_occurrences(text, marker)
            key = f"{relative_path}:{marker}"
            if count == 0:
                issues.append(("MISSING_CONSUMER_MARKER", key))
            elif count != 1:
                issues.append(("DUPLICATE_CONSUMER_MARKER", f"{key}:count={count}"))
    return issues


def parse_string_sequence(node: ast.AST, path: Path, field_name: str) -> list[str]:
    if not isinstance(node, (ast.Tuple, ast.List)):
        raise ValueError(f"{path}:{field_name}:expected_string_sequence")

    values: list[str] = []
    for element in node.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            raise ValueError(f"{path}:{field_name}:expected_string_literals")
        values.append(element.value)
    return values


def load_primary_tool_supported_modes(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"{path}:missing_primary_tool") from exc

    try:
        module = ast.parse(source, filename=path.as_posix())
    except SyntaxError as exc:
        raise ValueError(f"{path}:invalid_python:{exc.lineno}:{exc.offset}") from exc

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "MODE_CHOICES":
                return parse_string_sequence(node.value, path, "MODE_CHOICES")
    raise ValueError(f"{path}:missing_MODE_CHOICES")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest, manifest_issue = read_manifest(root / MANIFEST)
    issues: list[tuple[str, str]] = []
    if manifest_issue is not None:
        issues.append(manifest_issue)
        return issues
    assert manifest is not None

    for key, expected in REQUIRED_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            issues.append(("TOP_LEVEL_MISMATCH", key))

    tooling = manifest.get("tooling")
    if not isinstance(tooling, dict):
        issues.append(("MISSING_TOOLING", "tooling"))
    else:
        for key, expected in REQUIRED_TOOLING.items():
            actual = tooling.get(key)
            if key == "supported_modes":
                if actual != expected:
                    issues.append(("TOOLING_MISMATCH", key))
                continue
            issues.extend(collect_tooling_entry_issues(root, key, actual, expected))

        primary_tool_path = resolve_manifest_path(root, PRIMARY_TOOL.as_posix())
        if primary_tool_path.exists():
            try:
                actual_modes = load_primary_tool_supported_modes(primary_tool_path)
            except ValueError as exc:
                issues.append(("INVALID_PRIMARY_TOOL_SOURCE", str(exc)))
            else:
                if actual_modes != REQUIRED_TOOLING["supported_modes"]:
                    issues.append(
                        (
                            "PRIMARY_TOOL_SUPPORTED_MODES_MISMATCH",
                            f"actual={actual_modes!r}:expected={REQUIRED_TOOLING['supported_modes']!r}",
                        )
                    )
            issues.extend(collect_primary_tool_marker_issues(root))
        issues.extend(collect_consumer_marker_issues(root))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_NOTES", "notes"))
    else:
        non_string_notes = [repr(note) for note in notes if not isinstance(note, str)]
        for note in non_string_notes:
            issues.append(("INVALID_NOTE_ENTRY", note))
        string_notes = [note for note in notes if isinstance(note, str)]
        for note in find_duplicate_strings(string_notes):
            issues.append(("DUPLICATE_NOTE_ENTRY", note))
        for marker in REQUIRED_NOTE_MARKERS:
            if marker not in string_notes:
                issues.append(("MISSING_NOTE_MARKER", marker))
        if string_notes != list(REQUIRED_NOTE_MARKERS):
            issues.append(("NOTE_ORDER_MISMATCH", "notes"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_TOOLS_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_manifest() -> dict:
    return {
        **REQUIRED_TOP_LEVEL,
        "tooling": {
            key: list(value) if isinstance(value, list) else value
            for key, value in REQUIRED_TOOLING.items()
        },
        "notes": list(REQUIRED_NOTE_MARKERS),
    }


def render_primary_tool_self_test_source() -> str:
    return "\n".join(
        (
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            "SELF_TEST_CASES = [",
            '    "legacy_sha256_alias",',
            "]",
            "",
            "def normalize_mode(mode: str) -> str:",
            "    return LEGACY_MODE_ALIASES.get(mode, mode)",
            "",
        )
    )


def render_consumer_self_test_source(relative_path: str) -> str:
    markers = EXPECTED_CONSUMER_MARKERS.get(relative_path)
    if markers is None:
        return "present\n"
    return "\n".join(markers) + "\n"


def build_self_test_root(root: Path) -> None:
    manifest_path = root / MANIFEST
    write_manifest(manifest_path, build_self_test_manifest())
    write_text(root / PRIMARY_TOOL, render_primary_tool_self_test_source())
    for relative_path in (
        *REQUIRED_TOOLING["consumers"],
        *REQUIRED_TOOLING["checkers"],
    ):
        write_text(root / relative_path, render_consumer_self_test_source(relative_path))


def run_self_test() -> int:
    expected_case_count = 50
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_tools_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        manifest_path = root / MANIFEST

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for key in REQUIRED_TOP_LEVEL:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest[key] = "broken"
            write_manifest(manifest_path, manifest)
            assert ("TOP_LEVEL_MISMATCH", key) in collect_issues(root)
            checks_run += 1

        for key in REQUIRED_TOOLING:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["tooling"][key] = []
            write_manifest(manifest_path, manifest)
            issues = collect_issues(root)
            if key == "supported_modes":
                assert ("TOOLING_MISMATCH", key) in issues
            else:
                assert any(
                    issue[0] in {"MISSING_TOOLING", "TOOLING_MISMATCH"} and issue[1].startswith(f"{key}:")
                    for issue in issues
                )
            checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["tooling"] = "broken"
        write_manifest(manifest_path, manifest)
        assert ("MISSING_TOOLING", "tooling") in collect_issues(root)
        checks_run += 1

        for key in ("primary", "consumers", "checkers"):
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["tooling"][key] = "broken"
            write_manifest(manifest_path, manifest)
            assert ("MISSING_TOOLING", key) in collect_issues(root)
            checks_run += 1

        for category, entry in (
            ("primary", REQUIRED_TOOLING["primary"][0]),
            ("consumers", REQUIRED_TOOLING["consumers"][0]),
            ("checkers", REQUIRED_TOOLING["checkers"][0]),
        ):
            build_self_test_root(root)
            (root / entry).unlink()
            assert ("MISSING_TOOL_PATH", f"{category}:{entry}") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["notes"] = "broken"
        write_manifest(manifest_path, manifest)
        assert ("MISSING_NOTES", "notes")) in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["notes"].remove(marker)
            write_manifest(manifest_path, manifest)
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["notes"] = list(reversed(REQUIRED_NOTE_MARKERS))
        write_manifest(manifest_path, manifest)
        assert ("NOTE_ORDER_MISMATCH", "notes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["notes"].append(REQUIRED_NOTE_MARKERS[0])
        write_manifest(manifest_path, manifest)
        assert ("DUPLICATE_NOTE_ENTRY", REQUIRED_NOTE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["notes"].append(123)
        write_manifest(manifest_path, manifest)
        assert ("INVALID_NOTE_ENTRY", "123") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["tooling"]["primary"].append(REQUIRED_TOOLING["primary"][0])
        write_manifest(manifest_path, manifest)
        assert ("DUPLICATE_TOOLING_ENTRY", f"primary:{REQUIRED_TOOLING['primary'][0]}") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["tooling"]["consumers"].append(123)
        write_manifest(manifest_path, manifest)
        assert ("INVALID_TOOLING_ENTRY", "consumers:123") in collect_issues(root)
        checks_run += 1

        for category, entry in (
            ("primary", "scripts/zigux/unexpected-primary-tool.py"),
            ("consumers", "scripts/zigux/unexpected-consumer.py"),
            ("checkers", "scripts/zigux/unexpected-checker.py"),
        ):
            build_self_test_root(root)
            write_text(root / entry, "present\n")
            manifest = build_self_test_manifest()
            manifest["tooling"][category].append(entry)
            write_manifest(manifest_path, manifest)
            assert ("UNEXPECTED_TOOLING_ENTRY", f"{category}:{entry}") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(root / PRIMARY_TOOL, 'MODE_CHOICES = ("json", "text", "bytes")\n')
        assert (
            "PRIMARY_TOOL_SUPPORTED_MODES_MISMATCH",
            "actual=['json', 'text', 'bytes']:expected=['text', 'json', 'bytes']",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root / PRIMARY_TOOL, 'MODE_CHOICES = "text"\n')
        assert (
            "INVALID_PRIMARY_TOOL_SOURCE",
            f"{(root / PRIMARY_TOOL).as_posix()}:MODE_CHOICES:expected_string_sequence",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(manifest_path, "{broken\n")
        assert ("INVALID_MANIFEST_JSON", manifest_path.as_posix()) in collect_issues(root)
        checks_run += 1

        for marker in PRIMARY_TOOL_MARKERS:
            build_self_test_root(root)
            path = root / PRIMARY_TOOL
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_PRIMARY_TOOL_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in PRIMARY_TOOL_MARKERS:
            build_self_test_root(root)
            path = root / PRIMARY_TOOL
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker, f"{marker}\n{marker}", 1),
                encoding="utf-8",
            )
            assert ("DUPLICATE_PRIMARY_TOOL_MARKER", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for relative_path, markers in EXPECTED_CONSUMER_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                path = root / relative_path
                path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
                assert ("MISSING_CONSUMER_MARKER", f"{relative_path}:{marker}") in collect_issues(root)
                checks_run += 1

        for relative_path, markers in EXPECTED_CONSUMER_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                path = root / relative_path
                path.write_text(
                    path.read_text(encoding="utf-8").replace(marker, f"{marker}\n{marker}", 1),
                    encoding="utf-8",
                )
                assert (
                    "DUPLICATE_CONSUMER_MARKER",
                    f"{relative_path}:{marker}:count=2",
                ) in collect_issues(root)
                checks_run += 1

        manifest_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 artifact-tools manifest aligned with the current artifact-diff packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_ARTIFACT_TOOLS_MANIFEST=pass")
    print(f"PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_NOTE_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    print(
        "PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_TOOL_PATH_COUNT="
        f"{len(REQUIRED_TOOLING['primary']) + len(REQUIRED_TOOLING['consumers']) + len(REQUIRED_TOOLING['checkers'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
