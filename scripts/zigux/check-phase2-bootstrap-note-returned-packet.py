#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"

MARKERS = (
    "`scripts/zigux/artifact_diff.py` is directly readable on current `master` and keeps the shipped `text`, `json`, `bytes`, and legacy `sha256`-alias comparison surfaces explicit beneath the fixture-backed artifact-support packet already consumed by the current kconfig and fixdep checks.",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`, `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`, `python3 scripts/zigux/check-genksyms-bridge.py --self-test`, `python3 scripts/zigux/check-genksyms-bridge.py`, `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/fixdep.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, and `make -C zigux phase2-validate`, so the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, local-first archive workflow, third_party README contract, installer, toolchain-pinning, pin-scope, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, primary artifact-diff helper, dedicated genksyms selftest-alignment guard, genksyms bridge, kconfig bridge, fixdep governance and parity packet, and make-wrapper-backed `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` route replays instead of leaving the returned Phase 2 packet implicit beside the shipped CI path.",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` plus restored `zigux/tests/fixtures/genksyms_bridge/` manifest and process-output roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, tool-manifest, fixture-backed artifact-support, primary artifact-diff helper, genksyms, fixdep, and bridge packet reviewable without widening back into older validator-first claims.",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
)

FORBIDDEN_MARKERS: tuple[str, ...] = ()


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


def collect_missing_markers(text: str) -> list[tuple[str, str]]:
    return [("MISSING_MARKERS", marker) for marker in MARKERS if marker not in text]


def collect_forbidden_markers(text: str) -> list[tuple[str, str]]:
    return [("FORBIDDEN_MARKERS", marker) for marker in FORBIDDEN_MARKERS if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, PHASE2_NOTES))
    return collect_missing_markers(text) + collect_forbidden_markers(text)


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(MARKERS) + len(FORBIDDEN_MARKERS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_note_returned_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MARKERS", marker) in issues
            checks_run += 1

        for marker in FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_MARKERS", marker) in issues
            checks_run += 1

        build_sample_root(root)
        resolve_path(root, PHASE2_NOTES).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing file did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the returned artifact-diff and genksyms packet explicit in the Phase 2 bootstrap note."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a synthetic passing tree for focused local replay",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET_MARKER_COUNT={len(MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTE_RETURNED_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
