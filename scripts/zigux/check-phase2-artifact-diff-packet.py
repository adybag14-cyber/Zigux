#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
DOCS_README = Path("Documentation/zigux/README.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
ARTIFACT_DIFF = Path("scripts/zigux/artifact_diff.py")
ARTIFACT_TOOLS_CHECKER = Path("scripts/zigux/check-phase2-artifact-tools-manifest.py")
KCONFIG_CHECKER = Path("scripts/zigux/check-kconfig-bridge.py")
FIXDEP_CHECKER = Path("scripts/zigux/check-fixdep-diff.py")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_TOOLS_MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")

REQUIRED_PATHS = (
    BOOTSTRAP_NOTES,
    DOCS_README,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    ARTIFACT_DIFF,
    ARTIFACT_TOOLS_CHECKER,
    KCONFIG_CHECKER,
    FIXDEP_CHECKER,
    TOOL_MANIFEST,
    ARTIFACT_TOOLS_MANIFEST,
)

TEXT_MARKERS = {
    BOOTSTRAP_NOTES: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
        "`scripts/zigux/artifact_diff.py` is directly readable on current `master` and keeps the shipped `text`, `json`, `bytes`, and legacy `sha256`-alias comparison surfaces explicit beneath the fixture-backed artifact-support packet already consumed by the current kconfig and fixdep checks.",
    ),
    DOCS_README: (
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    ),
    PHASE2_CLOSURE: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "fixture-backed artifact-support packet",
    ),
    REVIEW_CHECKLIST: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    ),
    SCRIPTS_README: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "artifact-support and fixdep packet explicit from the scripts root",
    ),
}

EXPECTED_TOOL_MANIFEST_CHECKERS = [
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
]

EXPECTED_ARTIFACT_MANIFEST = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "artifact-diff support for fixture-backed scripts/zigux validation",
    "tooling": {
        "primary": ["scripts/zigux/artifact_diff.py"],
        "consumers": [
            "scripts/zigux/check-kconfig-bridge.py",
            "scripts/zigux/check-fixdep-diff.py",
        ],
        "checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],
        "supported_modes": ["text", "json", "bytes"],
    },
    "notes": [
        "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
        "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
        "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    ],
}

EXPECTED_MODE_CHOICES = ["text", "json", "bytes"]
EXPECTED_LEGACY_MODE_ALIASES = {"sha256": "bytes"}
EXPECTED_CONSUMER_MARKERS = {
    KCONFIG_CHECKER: (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(actual)], cwd=str(ROOT))',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(actual), str(repeat)], cwd=str(ROOT))',
    ),
    FIXDEP_CHECKER: (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "text", str(expected), str(actual)], cwd=str(ROOT))',
    ),
}


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}:{exc.lineno}:{exc.colno}: {exc.msg}") from exc


def parse_string_list(node: ast.AST, *, label: str) -> list[str]:
    if not isinstance(node, (ast.List, ast.Tuple)):
        raise ValueError(f"{label}:expected_string_sequence")
    values: list[str] = []
    for item in node.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            raise ValueError(f"{label}:expected_string_literals")
        values.append(item.value)
    return values


def parse_string_dict(node: ast.AST, *, label: str) -> dict[str, str]:
    if not isinstance(node, ast.Dict):
        raise ValueError(f"{label}:expected_string_dict")
    values: dict[str, str] = {}
    for key_node, value_node in zip(node.keys, node.values):
        if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
            raise ValueError(f"{label}:expected_string_keys")
        if not isinstance(value_node, ast.Constant) or not isinstance(value_node.value, str):
            raise ValueError(f"{label}:expected_string_values")
        values[key_node.value] = value_node.value
    return values


def load_artifact_diff_contract(path: Path) -> tuple[list[str], dict[str, str]]:
    source = read_text(path)
    module = ast.parse(source, filename=path.as_posix())
    mode_choices: list[str] | None = None
    legacy_aliases: dict[str, str] | None = None
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "MODE_CHOICES":
                mode_choices = parse_string_list(node.value, label="MODE_CHOICES")
            if isinstance(target, ast.Name) and target.id == "LEGACY_MODE_ALIASES":
                legacy_aliases = parse_string_dict(node.value, label="LEGACY_MODE_ALIASES")
    if mode_choices is None:
        raise ValueError(f"{path}:missing_MODE_CHOICES")
    if legacy_aliases is None:
        raise ValueError(f"{path}:missing_LEGACY_MODE_ALIASES")
    return mode_choices, legacy_aliases


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).exists():
            issues.append(("MISSING_REQUIRED_PATH", relative_path.as_posix()))

    for relative_path, markers in TEXT_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = read_text(path)
        for marker in markers:
            count = count_exact_occurrences(text, marker)
            key = f"{relative_path.as_posix()}::{marker}"
            if count == 0:
                issues.append(("MISSING_TEXT_MARKER", key))
            elif count != 1:
                issues.append(("DUPLICATE_TEXT_MARKER", f"{key}:count={count}"))

    tool_manifest_path = root / TOOL_MANIFEST
    if tool_manifest_path.exists():
        manifest = read_json(tool_manifest_path)
        if not isinstance(manifest, dict):
            issues.append(("INVALID_TOOL_MANIFEST", TOOL_MANIFEST.as_posix()))
        else:
            present_surfaces = manifest.get("present_surfaces")
            if not isinstance(present_surfaces, dict):
                issues.append(("MISSING_TOOL_MANIFEST_FIELD", "present_surfaces"))
            else:
                checkers = present_surfaces.get("checkers")
                if not isinstance(checkers, list):
                    issues.append(("MISSING_TOOL_MANIFEST_FIELD", "present_surfaces.checkers"))
                else:
                    for checker in EXPECTED_TOOL_MANIFEST_CHECKERS:
                        if checker not in checkers:
                            issues.append(("MISSING_TOOL_MANIFEST_CHECKER", checker))

    artifact_manifest_path = root / ARTIFACT_TOOLS_MANIFEST
    if artifact_manifest_path.exists():
        manifest = read_json(artifact_manifest_path)
        if not isinstance(manifest, dict):
            issues.append(("INVALID_ARTIFACT_MANIFEST", ARTIFACT_TOOLS_MANIFEST.as_posix()))
        else:
            for field_name in ("phase", "status", "scope"):
                if manifest.get(field_name) != EXPECTED_ARTIFACT_MANIFEST[field_name]:
                    issues.append(("ARTIFACT_MANIFEST_FIELD_MISMATCH", field_name))
            tooling = manifest.get("tooling")
            if not isinstance(tooling, dict):
                issues.append(("MISSING_ARTIFACT_MANIFEST_FIELD", "tooling"))
            else:
                for field_name, expected_value in EXPECTED_ARTIFACT_MANIFEST["tooling"].items():
                    if tooling.get(field_name) != expected_value:
                        issues.append(("ARTIFACT_MANIFEST_TOOLING_MISMATCH", field_name))
            notes = manifest.get("notes")
            if not isinstance(notes, list):
                issues.append(("MISSING_ARTIFACT_MANIFEST_FIELD", "notes"))
            else:
                for marker in EXPECTED_ARTIFACT_MANIFEST["notes"]:
                    if marker not in notes:
                        issues.append(("MISSING_ARTIFACT_NOTE", marker))

    artifact_diff_path = root / ARTIFACT_DIFF
    if artifact_diff_path.exists():
        try:
            mode_choices, legacy_aliases = load_artifact_diff_contract(artifact_diff_path)
        except ValueError as exc:
            issues.append(("INVALID_ARTIFACT_DIFF_SOURCE", str(exc)))
        else:
            if mode_choices != EXPECTED_MODE_CHOICES:
                issues.append(("ARTIFACT_DIFF_MODE_CHOICES_MISMATCH", repr(mode_choices)))
            if legacy_aliases != EXPECTED_LEGACY_MODE_ALIASES:
                issues.append(("ARTIFACT_DIFF_LEGACY_ALIAS_MISMATCH", repr(legacy_aliases)))

    for relative_path, markers in EXPECTED_CONSUMER_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = read_text(path)
        for marker in markers:
            count = count_exact_occurrences(text, marker)
            key = f"{relative_path.as_posix()}::{marker}"
            if count == 0:
                issues.append(("MISSING_CONSUMER_MARKER", key))
            elif count != 1:
                issues.append(("DUPLICATE_CONSUMER_MARKER", f"{key}:count={count}"))

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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def build_sample_root(root: Path) -> None:
    for relative_path, markers in TEXT_MARKERS.items():
        write_text(root / relative_path, "\n".join(markers) + "\n")

    tool_manifest = {
        "present_surfaces": {
            "checkers": [
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                "scripts/zigux/check-phase2-tool-manifest.py",
            ]
        }
    }
    write_json(root / TOOL_MANIFEST, tool_manifest)
    write_json(root / ARTIFACT_TOOLS_MANIFEST, EXPECTED_ARTIFACT_MANIFEST)
    write_text(
        root / ARTIFACT_DIFF,
        'MODE_CHOICES = ("text", "json", "bytes")\nLEGACY_MODE_ALIASES = {"sha256": "bytes"}\n',
    )
    write_text(
        root / KCONFIG_CHECKER,
        "\n".join(EXPECTED_CONSUMER_MARKERS[KCONFIG_CHECKER]) + "\n",
    )
    write_text(
        root / FIXDEP_CHECKER,
        "\n".join(EXPECTED_CONSUMER_MARKERS[FIXDEP_CHECKER]) + "\n",
    )
    write_text(root / ARTIFACT_TOOLS_CHECKER, "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_diff_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        notes_path = root / BOOTSTRAP_NOTES
        notes_path.write_text(notes_path.read_text(encoding="utf-8").replace(TEXT_MARKERS[BOOTSTRAP_NOTES][1], "", 1), encoding="utf-8")
        assert any(code == "MISSING_TEXT_MARKER" and value.startswith(f"{BOOTSTRAP_NOTES.as_posix()}::") for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        docs_path = root / DOCS_README
        docs_path.write_text(docs_path.read_text(encoding="utf-8") + TEXT_MARKERS[DOCS_README][0] + "\n", encoding="utf-8")
        assert any(code == "DUPLICATE_TEXT_MARKER" and value.startswith(f"{DOCS_README.as_posix()}::") for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        tool_manifest = read_json(root / TOOL_MANIFEST)
        assert isinstance(tool_manifest, dict)
        tool_manifest["present_surfaces"]["checkers"] = ["scripts/zigux/check-phase2-tool-manifest.py"]
        write_json(root / TOOL_MANIFEST, tool_manifest)
        assert ("MISSING_TOOL_MANIFEST_CHECKER", "scripts/zigux/check-phase2-artifact-tools-manifest.py") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        artifact_manifest = read_json(root / ARTIFACT_TOOLS_MANIFEST)
        assert isinstance(artifact_manifest, dict)
        artifact_manifest["tooling"]["supported_modes"] = ["json", "text", "bytes"]
        write_json(root / ARTIFACT_TOOLS_MANIFEST, artifact_manifest)
        assert ("ARTIFACT_MANIFEST_TOOLING_MISMATCH", "supported_modes") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        artifact_manifest = read_json(root / ARTIFACT_TOOLS_MANIFEST)
        assert isinstance(artifact_manifest, dict)
        artifact_manifest["notes"].pop()
        write_json(root / ARTIFACT_TOOLS_MANIFEST, artifact_manifest)
        assert any(code == "MISSING_ARTIFACT_NOTE" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root / ARTIFACT_DIFF, 'MODE_CHOICES = ("json", "text", "bytes")\nLEGACY_MODE_ALIASES = {"sha256": "bytes"}\n')
        assert any(code == "ARTIFACT_DIFF_MODE_CHOICES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root / ARTIFACT_DIFF, 'MODE_CHOICES = ("text", "json", "bytes")\n')
        assert any(code == "INVALID_ARTIFACT_DIFF_SOURCE" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        kconfig_path = root / KCONFIG_CHECKER
        kconfig_path.write_text(kconfig_path.read_text(encoding="utf-8").replace(EXPECTED_CONSUMER_MARKERS[KCONFIG_CHECKER][1], "", 1), encoding="utf-8")
        assert any(code == "MISSING_CONSUMER_MARKER" and value.startswith(f"{KCONFIG_CHECKER.as_posix()}::") for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        fixdep_path = root / FIXDEP_CHECKER
        fixdep_path.write_text(
            fixdep_path.read_text(encoding="utf-8").replace(
                EXPECTED_CONSUMER_MARKERS[FIXDEP_CHECKER][1],
                EXPECTED_CONSUMER_MARKERS[FIXDEP_CHECKER][1] + "\n" + EXPECTED_CONSUMER_MARKERS[FIXDEP_CHECKER][1],
                1,
            ),
            encoding="utf-8",
        )
        assert any(code == "DUPLICATE_CONSUMER_MARKER" and value.startswith(f"{FIXDEP_CHECKER.as_posix()}::") for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        (root / REVIEW_CHECKLIST).unlink()
        assert ("MISSING_REQUIRED_PATH", REVIEW_CHECKLIST.as_posix()) in collect_issues(root)
        checks += 1

    print("PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 artifact-diff support packet aligned across docs, manifests, and helper consumers."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root for focused packet replays")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_ARTIFACT_DIFF_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARTIFACT_DIFF_PACKET=pass")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_TEXT_SURFACE_COUNT={len(TEXT_MARKERS)}")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_CONSUMER_COUNT={len(EXPECTED_CONSUMER_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
