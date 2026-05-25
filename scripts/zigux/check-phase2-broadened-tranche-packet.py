#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_LEDGER = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_PATHS = (
    PHASE2_CLOSURE,
    ARTIFACT_DIFF_NOTE,
    SCRIPTS_README,
    BOOTSTRAP_LEDGER,
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/Makefile"),
)

PHASE2_CLOSURE_MARKERS = (
    "# Phase 2 Closure",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/artifact_diff.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-tools`",
    "artifact-support",
)

ARTIFACT_DIFF_MARKERS = (
    "# Zigux Artifact-Diff Notes",
    "## Current Phase 2 use",
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
    "## Phase 4 Tooling Review Note",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-tools`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
)

BOOTSTRAP_LEDGER_MARKERS = (
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/artifact-diff.md`",
    "- `scripts/zigux/README.md`",
    "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    "## Scope Note",
    "## Release-Planning Continuation",
)

EXACT_COUNT_MARKERS = {
    PHASE2_CLOSURE: (
        "- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
        "- `PHASE2_CURRENT_GAP_PACKET=`",
    ),
    ARTIFACT_DIFF_NOTE: (
        "## Current Phase 2 use",
        "## Phase 4 Tooling Review Note",
    ),
    BOOTSTRAP_LEDGER: (
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "## Release-Planning Continuation",
    ),
}

MARKER_TABLE = {
    PHASE2_CLOSURE: PHASE2_CLOSURE_MARKERS,
    ARTIFACT_DIFF_NOTE: ARTIFACT_DIFF_MARKERS,
    SCRIPTS_README: SCRIPTS_README_MARKERS,
    BOOTSTRAP_LEDGER: BOOTSTRAP_LEDGER_MARKERS,
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_marker_issues(path: Path, text: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in text:
            issues.append((f"MISSING::{path}", marker))
    return issues


def collect_exact_count_issues(path: Path, text: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((f"COUNT::{path}", f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    existing_paths: set[Path] = set()
    for rel_path in REQUIRED_PATHS:
        if not (root / rel_path).exists():
            issues.append(("MISSING_PATH", str(rel_path)))
        else:
            existing_paths.add(rel_path)

    for rel_path, markers in MARKER_TABLE.items():
        if rel_path not in existing_paths:
            continue
        text = read_text(root / rel_path)
        issues.extend(collect_marker_issues(rel_path, text, markers))

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        if rel_path not in existing_paths:
            continue
        text = read_text(root / rel_path)
        issues.extend(collect_exact_count_issues(rel_path, text, markers))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_BROADENED_TRANCHE_PACKET=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "`Documentation/zigux/phase2-closure.md`",
                "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
                "`scripts/zigux/artifact_diff.py`",
                "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`make -C zigux phase2-tools`",
                "artifact-support",
                "- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
                "- `PHASE2_CURRENT_GAP_PACKET=`",
                "",
            )
        ),
    )
    write_text(
        root / ARTIFACT_DIFF_NOTE,
        "\n".join(
            (
                "# Zigux Artifact-Diff Notes",
                "## Current Phase 2 use",
                "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
                "## Phase 4 Tooling Review Note",
                "",
            )
        ),
    )
    write_text(
        root / SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                "## Phase 2",
                "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
                "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
                "`scripts/zigux/check-phase2-tool-manifest.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`make -C zigux phase2-tools`",
                "`scripts/zigux/check-genksyms-bridge.py`",
                "`scripts/zigux/check-phase2-fixdep-gate.py`",
                "",
            )
        ),
    )
    write_text(
        root / BOOTSTRAP_LEDGER,
        "\n".join(
            (
                "# Zigux Alpha Bootstrap Commit Ledger",
                "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
                "- `Documentation/zigux/phase2-closure.md`",
                "- `Documentation/zigux/artifact-diff.md`",
                "- `scripts/zigux/README.md`",
                "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
                "## Scope Note",
                "## Release-Planning Continuation",
                "",
            )
        ),
    )
    for rel_path in REQUIRED_PATHS[4:]:
        write_text(root / rel_path, "present\n")


def run_self_test() -> int:
    expected_case_count = (
        1
        + sum(len(markers) for markers in MARKER_TABLE.values())
        + sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())
        + len(REQUIRED_PATHS)
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_broadened_tranche_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for rel_path, markers in MARKER_TABLE.items():
            for marker in markers:
                build_sample_root(root)
                path = root / rel_path
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (f"MISSING::{rel_path}", marker) in collect_issues(root)
                checks_run += 1

        for rel_path, markers in EXACT_COUNT_MARKERS.items():
            for marker in markers:
                build_sample_root(root)
                path = root / rel_path
                path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
                assert (f"COUNT::{rel_path}", f"2::{marker}") in collect_issues(root)
                checks_run += 1

        for rel_path in REQUIRED_PATHS:
            build_sample_root(root)
            (root / rel_path).unlink()
            assert ("MISSING_PATH", str(rel_path)) in collect_issues(root)
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_BROADENED_TRANCHE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BROADENED_TRANCHE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the broadened Phase 2 tranche packet aligned across the closure note, artifact-diff note, scripts README, and bootstrap ledger."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a synthetic current-like root for focused checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BROADENED_TRANCHE_PACKET=pass")
    print(f"PHASE2_BROADENED_TRANCHE_PACKET_FILE_COUNT={len(MARKER_TABLE)}")
    print(
        "PHASE2_BROADENED_TRANCHE_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKER_TABLE.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
