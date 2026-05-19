#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTE = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"

BOOTSTRAP_NOTE_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.",
    "## Current direct packet",
    "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, and `scripts/zigux/check-phase2-cross-selftest-alignment.py` are the current shipped Phase 2 reminder and alignment guards visible on `master`.",
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, and `ZIGUX_ZIG_URL`",
    "`.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, and the `zigux/tests/fixtures/genksyms_bridge/` fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` now records the full sixteen-mode `conf_bridge` packet",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
    "## Current repo-reality gaps",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, and direct cross-route packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer or direct cross-route surfaces from the current packet.",
    "## Follow-through",
    "Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, kconfig bridge alignment, or fixture-backed artifact-diff support.",
    "Do not widen this note into fixdep semantics, genksyms parser behavior, conf or confdata bridge semantics, or deeper cross-target execution claims beyond the returned `phase2_cross_targets.json` packet unless current `master` materializes the companion wider surfaces and their reminder checks.",
)

FORBIDDEN_BOOTSTRAP_NOTE_MARKERS = (
    "Repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`.",
    "Treat the absent installer and direct cross-route names as historical packet members until same-lane work rematerializes them on `master`.",
    "Repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, BOOTSTRAP_NOTE))
    issues = [("MISSING_BOOTSTRAP_NOTE_MARKERS", marker) for marker in BOOTSTRAP_NOTE_MARKERS if marker not in text]
    issues.extend(
        ("FORBIDDEN_BOOTSTRAP_NOTE_MARKERS", marker)
        for marker in FORBIDDEN_BOOTSTRAP_NOTE_MARKERS
        if marker in text
    )
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, BOOTSTRAP_NOTE), "\n".join(BOOTSTRAP_NOTE_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(BOOTSTRAP_NOTE_MARKERS) + len(FORBIDDEN_BOOTSTRAP_NOTE_MARKERS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_note_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in BOOTSTRAP_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for marker in FORBIDDEN_BOOTSTRAP_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_BOOTSTRAP_NOTE_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, BOOTSTRAP_NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing file did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_NOTE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap note aligned to the current toolchain packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_BOOTSTRAP_NOTE_ALIGNMENT=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_BOOTSTRAP_NOTE_ALIGNMENT=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_MARKER_COUNT={len(BOOTSTRAP_NOTE_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_BOOTSTRAP_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
