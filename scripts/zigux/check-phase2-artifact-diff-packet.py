#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 artifact-diff packet."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
ARTIFACT_DIFF = Path("scripts/zigux/artifact_diff.py")
ARTIFACT_MANIFEST_CHECKER = Path("scripts/zigux/check-phase2-artifact-tools-manifest.py")
KCONFIG_CONSUMER = Path("scripts/zigux/check-kconfig-bridge.py")
FIXDEP_CONSUMER = Path("scripts/zigux/check-fixdep-diff.py")
ARTIFACT_MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")

REQUIRED_PATHS = (
    BOOTSTRAP_NOTES,
    VALIDATE_PHASE2,
    ARTIFACT_DIFF,
    ARTIFACT_MANIFEST_CHECKER,
    KCONFIG_CONSUMER,
    FIXDEP_CONSUMER,
    ARTIFACT_MANIFEST,
)

BOOTSTRAP_NOTE_MARKERS = (
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts/zigux/artifact_diff.py` is directly readable on current `master`",
    "primary artifact-diff helper",
)

VALIDATE_PHASE2_MARKERS = (
    '"scripts/zigux/artifact_diff.py",',
    '"scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"zigux/tests/fixtures/phase2_artifact_tools_manifest.json",',
)

PRIMARY_TOOL_MARKERS = (
    'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    '    "legacy_sha256_alias",',
    "def normalize_mode(mode: str) -> str:",
    "    return LEGACY_MODE_ALIASES.get(mode, mode)",
)

EXPECTED_CONSUMER_MARKERS = {
    KCONFIG_CONSUMER: (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(actual)], cwd=str(ROOT))',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(actual), str(repeat)], cwd=str(ROOT))',
    ),
    FIXDEP_CONSUMER: (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "text", str(expected), str(actual)], cwd=str(ROOT))',
    ),
}

REQUIRED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "artifact-diff support for fixture-backed scripts/zigux validation",
}

REQUIRED_TOOLING = {
    "primary": [ARTIFACT_DIFF.as_posix()],
    "consumers": [KCONFIG_CONSUMER.as_posix(), FIXDEP_CONSUMER.as_posix()],
    "checkers": [ARTIFACT_MANIFEST_CHECKER.as_posix()],
    "supported_modes": ["text", "json", "bytes"],
}

REQUIRED_NOTE_MARKERS = (
    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_marker_count_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_occurrences(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def find_duplicate_strings(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


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


def read_manifest(path: Path) -> tuple[dict | None, tuple[str, str] | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError:
        return None, ("INVALID_MANIFEST_JSON", path.as_posix())


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
        if not resolve(root, Path(entry)).exists():
            issues.append(("MISSING_TOOL_PATH", f"{category}:{entry}"))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    manifest, manifest_issue = read_manifest(resolve(root, ARTIFACT_MANIFEST))
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
        primary_tool_path = resolve(root, ARTIFACT_DIFF)
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


def collect_consumer_marker_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for relative_path, markers in EXPECTED_CONSUMER_MARKERS.items():
        text = read_text(resolve(root, relative_path))
        issues.extend(
            collect_marker_count_issues(
                text,
                markers,
                "MISSING_CONSUMER_MARKER",
                "DUPLICATE_CONSUMER_MARKER",
            )
        )
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            raise SystemExit(f"required file missing: {resolve(root, rel)}")

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, BOOTSTRAP_NOTES)),
            BOOTSTRAP_NOTE_MARKERS,
            "MISSING_BOOTSTRAP_NOTE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, VALIDATE_PHASE2)),
            VALIDATE_PHASE2_MARKERS,
            "MISSING_VALIDATE_PHASE2_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            read_text(resolve(root, ARTIFACT_DIFF)),
            PRIMARY_TOOL_MARKERS,
            "MISSING_PRIMARY_TOOL_MARKER",
            "DUPLICATE_PRIMARY_TOOL_MARKER",
        )
    )
    issues.extend(collect_consumer_marker_issues(root))
    issues.extend(collect_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_DIFF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_manifest() -> dict:
    return {
        **REQUIRED_TOP_LEVEL,
        "tooling": {
            key: list(value) if isinstance(value, list) else value
            for key, value in REQUIRED_TOOLING.items()
        },
        "notes": list(REQUIRED_NOTE_MARKERS),
    }


def write_manifest(path: Path, manifest: dict) -> None:
    write_text(path, json.dumps(manifest, indent=2) + "\n")


def render_primary_tool_source() -> str:
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


def render_consumer_source(relative_path: Path) -> str:
    markers = EXPECTED_CONSUMER_MARKERS.get(relative_path)
    if markers is None:
        return "present\n"
    return "\n".join(markers) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_NOTE_MARKERS) + "\n")
    write_text(resolve(root, VALIDATE_PHASE2), "\n".join(VALIDATE_PHASE2_MARKERS) + "\n")
    write_text(resolve(root, ARTIFACT_DIFF), render_primary_tool_source())
    write_text(resolve(root, ARTIFACT_MANIFEST_CHECKER), "present\n")
    write_text(resolve(root, KCONFIG_CONSUMER), render_consumer_source(KCONFIG_CONSUMER))
    write_text(resolve(root, FIXDEP_CONSUMER), render_consumer_source(FIXDEP_CONSUMER))
    write_manifest(resolve(root, ARTIFACT_MANIFEST), build_self_test_manifest())


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    expected_case_count = (
        1
        + 1
        + len(BOOTSTRAP_NOTE_MARKERS)
        + len(VALIDATE_PHASE2_MARKERS)
        + len(PRIMARY_TOOL_MARKERS)
        + sum(len(markers) for markers in EXPECTED_CONSUMER_MARKERS.values())
        + len(REQUIRED_TOP_LEVEL)
        + len(REQUIRED_TOOLING)
        + 1
        + len(REQUIRED_NOTE_MARKERS)
        + 1
        + 1
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_diff_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        overlapping = "\n".join(
            (
                "`scripts/zigux/artifact_diff.py`",
                "`scripts/zigux/artifact_diff.py` is directly readable on current `master`",
                "",
            )
        )
        updated = replace_once(overlapping, "`scripts/zigux/artifact_diff.py`")
        assert updated.count("`scripts/zigux/artifact_diff.py`") == 1
        checks_run += 1

        for marker in BOOTSTRAP_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_NOTES)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_BOOTSTRAP_NOTE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_MARKERS:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_VALIDATE_PHASE2_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in PRIMARY_TOOL_MARKERS:
            build_self_test_root(root)
            path = resolve(root, ARTIFACT_DIFF)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_PRIMARY_TOOL_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for relative_path, markers in EXPECTED_CONSUMER_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                path = resolve(root, relative_path)
                write_text(path, replace_once(read_text(path), marker))
                assert ("MISSING_CONSUMER_MARKER", marker) in collect_issues(root)
                checks_run += 1

        for key in REQUIRED_TOP_LEVEL:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest[key] = "broken"
            write_manifest(resolve(root, ARTIFACT_MANIFEST), manifest)
            assert ("TOP_LEVEL_MISMATCH", key) in collect_issues(root)
            checks_run += 1

        for key in REQUIRED_TOOLING:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["tooling"][key] = []
            write_manifest(resolve(root, ARTIFACT_MANIFEST), manifest)
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
        manifest["notes"] = "broken"
        write_manifest(resolve(root, ARTIFACT_MANIFEST), manifest)
        assert ("MISSING_NOTES", "notes") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["notes"].remove(marker)
            write_manifest(resolve(root, ARTIFACT_MANIFEST), manifest)
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["notes"] = list(reversed(REQUIRED_NOTE_MARKERS))
        write_manifest(resolve(root, ARTIFACT_MANIFEST), manifest)
        assert ("NOTE_ORDER_MISMATCH", "notes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve(root, ARTIFACT_DIFF).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing artifact_diff.py did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_ARTIFACT_DIFF_PACKET=pass")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    print(
        "PHASE2_ARTIFACT_DIFF_PACKET_MARKER_COUNT="
        f"{len(BOOTSTRAP_NOTE_MARKERS) + len(VALIDATE_PHASE2_MARKERS) + len(PRIMARY_TOOL_MARKERS) + sum(len(markers) for markers in EXPECTED_CONSUMER_MARKERS.values()) + len(REQUIRED_NOTE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
