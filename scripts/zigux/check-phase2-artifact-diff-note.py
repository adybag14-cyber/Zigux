#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
NOTE = ROOT / "Documentation" / "zigux" / "artifact-diff.md"

REQUIRED_PATHS = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
)

REQUIRED_MARKERS = (
    "## Current Phase 2 use",
    "Phase 2 keeps the shared helper explicit through the current direct-readback host-tool packets instead of leaving this note at a generic family summary.",
    "- `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep `scripts/zigux/artifact_diff.py` on the current `fixdep` parity path.",
    "- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, and `zigux/tests/fixtures/genksyms_bridge/manifest.json` keep the same helper explicit on the current `genksyms` bridge packet.",
    "- `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the same helper explicit on the current kconfig bridge packet.",
    "Keep broader Phase 2 closure-side, make-wrapper, and shared reminder claims routed through `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, and `scripts/zigux/README.md` so this note stays bounded to the helper contract and the current direct-readback consumer packet.",
)

FORBIDDEN_MARKERS = (
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
)

EXACT_COUNT_MARKERS = (
    "## Current Phase 2 use",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(root / NOTE.relative_to(ROOT))

    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    for marker in REQUIRED_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_MARKER", marker))

    for marker in FORBIDDEN_MARKERS:
        if marker in note_text:
            issues.append(("FORBIDDEN_MARKER", marker))

    for marker in EXACT_COUNT_MARKERS:
        count = note_text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_MARKER", f"{count}::{marker}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_DIFF_NOTE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(root / NOTE.relative_to(ROOT), "\n".join(REQUIRED_MARKERS) + "\n")
    for rel in REQUIRED_PATHS:
        write_text(resolve(root, rel), "placeholder\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_diff_note_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(note_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in FORBIDDEN_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(note_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(note_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("EXACT_COUNT_MARKER", f"2::{marker}") in collect_issues(root)
            checks += 1

        for rel in REQUIRED_PATHS:
            build_self_test_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_PATH", rel) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        (root / NOTE.relative_to(ROOT)).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing note did not abort")

    print("PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the Phase 2 artifact-diff note aligned to the current direct-readback consumer packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARTIFACT_DIFF_NOTE=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
