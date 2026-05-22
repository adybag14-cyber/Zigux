#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")

EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
]

EXPECTED_TOOL_MANIFEST_NOTE_MARKERS = (
    "Keep the dedicated manifest guards, the primary artifact_diff helper, and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, scripts/zigux/artifact_diff.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option version-side-effect proof, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
)

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
        "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
    ],
}


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    tool_manifest_path = root / TOOL_MANIFEST
    artifact_manifest_path = root / ARTIFACT_MANIFEST

    try:
        tool_manifest = read_json(tool_manifest_path)
    except json.JSONDecodeError as exc:
        return [("INVALID_TOOL_MANIFEST_JSON", exc.msg)]
    if not isinstance(tool_manifest, dict):
        return [("INVALID_TOOL_MANIFEST_PAYLOAD", type(tool_manifest).__name__)]

    present_surfaces = tool_manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", repr(present_surfaces)))
    else:
        artifact_support = present_surfaces.get("artifact_support")
        if artifact_support != EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT:
            issues.append(
                (
                    "TOOL_MANIFEST_ARTIFACT_SUPPORT_MISMATCH",
                    f"actual={artifact_support!r}:expected={EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT!r}",
                )
            )

    notes = tool_manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_TOOL_MANIFEST_NOTES", repr(notes)))
    else:
        for marker in EXPECTED_TOOL_MANIFEST_NOTE_MARKERS:
            if marker not in notes:
                issues.append(("MISSING_TOOL_MANIFEST_NOTE_MARKER", marker))

    try:
        artifact_manifest = read_json(artifact_manifest_path)
    except json.JSONDecodeError as exc:
        return issues + [("INVALID_ARTIFACT_MANIFEST_JSON", exc.msg)]
    if not isinstance(artifact_manifest, dict):
        return issues + [("INVALID_ARTIFACT_MANIFEST_PAYLOAD", type(artifact_manifest).__name__)]

    for key in ("phase", "status", "scope"):
        if artifact_manifest.get(key) != EXPECTED_ARTIFACT_MANIFEST[key]:
            issues.append(
                (
                    "ARTIFACT_MANIFEST_FIELD_MISMATCH",
                    f"{key}:actual={artifact_manifest.get(key)!r}:expected={EXPECTED_ARTIFACT_MANIFEST[key]!r}",
                )
            )

    tooling = artifact_manifest.get("tooling")
    expected_tooling = EXPECTED_ARTIFACT_MANIFEST["tooling"]
    if not isinstance(tooling, dict):
        issues.append(("INVALID_ARTIFACT_MANIFEST_TOOLING", repr(tooling)))
    else:
        for key, expected in expected_tooling.items():
            if tooling.get(key) != expected:
                issues.append(
                    (
                        "ARTIFACT_MANIFEST_TOOLING_MISMATCH",
                        f"{key}:actual={tooling.get(key)!r}:expected={expected!r}",
                    )
                )

    artifact_notes = artifact_manifest.get("notes")
    expected_notes = EXPECTED_ARTIFACT_MANIFEST["notes"]
    if artifact_notes != expected_notes:
        issues.append(
            (
                "ARTIFACT_MANIFEST_NOTES_MISMATCH",
                f"actual={artifact_notes!r}:expected={expected_notes!r}",
            )
        )

    required_paths = {
        *EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT,
        *EXPECTED_ARTIFACT_MANIFEST["tooling"]["primary"],
        *EXPECTED_ARTIFACT_MANIFEST["tooling"]["consumers"],
        *EXPECTED_ARTIFACT_MANIFEST["tooling"]["checkers"],
    }
    for rel_path in sorted(required_paths):
        if not (root / rel_path).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel_path))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOL_MANIFEST_ARTIFACT_SUPPORT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    tool_manifest = {
        "present_surfaces": {
            "artifact_support": list(EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT),
        },
        "notes": list(EXPECTED_TOOL_MANIFEST_NOTE_MARKERS),
    }
    artifact_manifest = {
        "phase": EXPECTED_ARTIFACT_MANIFEST["phase"],
        "status": EXPECTED_ARTIFACT_MANIFEST["status"],
        "scope": EXPECTED_ARTIFACT_MANIFEST["scope"],
        "tooling": {
            key: list(value)
            for key, value in EXPECTED_ARTIFACT_MANIFEST["tooling"].items()
        },
        "notes": list(EXPECTED_ARTIFACT_MANIFEST["notes"]),
    }

    write_json(root / TOOL_MANIFEST, tool_manifest)
    write_json(root / ARTIFACT_MANIFEST, artifact_manifest)

    for rel_path in {
        *EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT,
        *EXPECTED_ARTIFACT_MANIFEST["tooling"]["primary"],
        *EXPECTED_ARTIFACT_MANIFEST["tooling"]["consumers"],
        *EXPECTED_ARTIFACT_MANIFEST["tooling"]["checkers"],
    }:
        if rel_path == ARTIFACT_MANIFEST.as_posix():
            continue
        write_text(root / rel_path, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 12

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_artifact_support_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads((root / TOOL_MANIFEST).read_text(encoding="utf-8"))
        payload["present_surfaces"]["artifact_support"] = payload["present_surfaces"]["artifact_support"][1:]
        write_json(root / TOOL_MANIFEST, payload)
        assert any(code == "TOOL_MANIFEST_ARTIFACT_SUPPORT_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads((root / TOOL_MANIFEST).read_text(encoding="utf-8"))
        payload["notes"] = payload["notes"][:-1]
        write_json(root / TOOL_MANIFEST, payload)
        assert any(code == "MISSING_TOOL_MANIFEST_NOTE_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads((root / ARTIFACT_MANIFEST).read_text(encoding="utf-8"))
        payload["tooling"]["primary"] = []
        write_json(root / ARTIFACT_MANIFEST, payload)
        assert any(code == "ARTIFACT_MANIFEST_TOOLING_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads((root / ARTIFACT_MANIFEST).read_text(encoding="utf-8"))
        payload["notes"] = payload["notes"][:-1]
        write_json(root / ARTIFACT_MANIFEST, payload)
        assert any(code == "ARTIFACT_MANIFEST_NOTES_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        (root / "scripts/zigux/artifact_diff.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/artifact_diff.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / TOOL_MANIFEST).write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_TOOL_MANIFEST_JSON", "Expecting property name enclosed in double quotes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / ARTIFACT_MANIFEST).write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_ARTIFACT_MANIFEST_JSON", "Expecting property name enclosed in double quotes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / TOOL_MANIFEST).write_text("[]\n", encoding="utf-8")
        assert ("INVALID_TOOL_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / ARTIFACT_MANIFEST).write_text("[]\n", encoding="utf-8")
        assert ("INVALID_ARTIFACT_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads((root / ARTIFACT_MANIFEST).read_text(encoding="utf-8"))
        payload["scope"] = "broken"
        write_json(root / ARTIFACT_MANIFEST, payload)
        assert any(code == "ARTIFACT_MANIFEST_FIELD_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads((root / TOOL_MANIFEST).read_text(encoding="utf-8"))
        payload["present_surfaces"] = []
        write_json(root / TOOL_MANIFEST, payload)
        assert any(code == "INVALID_TOOL_MANIFEST_PRESENT_SURFACES" for code, _ in collect_issues(root))
        checks_run += 1

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_TOOL_MANIFEST_ARTIFACT_SUPPORT_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_ARTIFACT_SUPPORT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 tool manifest keeps the current artifact-support packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST_ARTIFACT_SUPPORT=pass")
    print(
        "PHASE2_TOOL_MANIFEST_ARTIFACT_SUPPORT_REQUIRED_PATH_COUNT="
        f"{len(set(EXPECTED_TOOL_MANIFEST_ARTIFACT_SUPPORT + EXPECTED_ARTIFACT_MANIFEST['tooling']['primary'] + EXPECTED_ARTIFACT_MANIFEST['tooling']['consumers'] + EXPECTED_ARTIFACT_MANIFEST['tooling']['checkers']))}"
    )
    print(
        "PHASE2_TOOL_MANIFEST_ARTIFACT_SUPPORT_NOTE_COUNT="
        f"{len(EXPECTED_TOOL_MANIFEST_NOTE_MARKERS) + len(EXPECTED_ARTIFACT_MANIFEST['notes'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())