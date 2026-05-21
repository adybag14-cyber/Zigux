#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"

TESTS_MARKERS = (
    "- `scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet",
)

BOOTSTRAP_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits archive digests to `x86_64-linux`, and names `phase2-toolchain` plus `phase2-validate` as the required Linux-style make routes when those routes are rematerialized.",
    "- `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are the current shipped Phase 2 reminder, parity, and alignment guards visible on `master`.",
    "- `scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "- `.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, `python3 scripts/zigux/check-lane05-local-archive-readme.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pinning.py`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`, `python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test`, `python3 scripts/zigux/check-phase2-kbuild-routes.py`, `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`, `python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`, `python3 scripts/zigux/check-phase2-required-make-routes.py`, `python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`, `python3 scripts/zigux/check-phase2-docs-shared-reminder.py`, `python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`, `python3 scripts/zigux/check-phase2-tool-manifest.py`, `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`, `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`, `python3 scripts/zigux/check-genksyms-bridge.py --self-test`, `python3 scripts/zigux/check-genksyms-bridge.py`, `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/fixdep.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-fixdep`, and `make -C zigux phase2-validate`, so the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, local-first archive workflow, third_party README contract, installer, toolchain-pinning, pin-scope, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, genksyms bridge, kconfig bridge, fixdep governance and parity packet, and make-wrapper-backed toolchain, tools, and kconfig route replays instead of leaving the returned Phase 2 packet implicit beside the shipped CI path.",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/fixdep/cases.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, tool-manifest, fixture-backed artifact-support, fixdep, and bridge packet reviewable without widening back into older validator-first claims.",
    "- The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "- Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
)

TESTS_EXACT_COUNT_MARKERS = (
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
)

BOOTSTRAP_EXACT_COUNT_MARKERS = (
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

TESTS_FORBIDDEN_MARKERS = (
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as historical packet members rather than shipped current-`master` evidence",
)

BOOTSTRAP_FORBIDDEN_MARKERS = (
    "historical packet members until same-lane work rematerializes them on `master`",
    "Treat older validator-first-only Phase 2 names as current repo-reality gaps inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_text = read_text(resolve_path(root, TESTS_README))
    bootstrap_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(tests_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_forbidden_markers(tests_text, TESTS_FORBIDDEN_MARKERS, "FORBIDDEN_TESTS_MARKERS"))
    issues.extend(collect_exact_count_markers(tests_text, TESTS_EXACT_COUNT_MARKERS, "EXACT_COUNT_TESTS_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_text, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_forbidden_markers(bootstrap_text, BOOTSTRAP_FORBIDDEN_MARKERS, "FORBIDDEN_BOOTSTRAP_MARKERS"))
    issues.extend(collect_exact_count_markers(bootstrap_text, BOOTSTRAP_EXACT_COUNT_MARKERS, "EXACT_COUNT_BOOTSTRAP_MARKERS"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_MARKERS) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_MARKERS) + "\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(TESTS_MARKERS)
        + len(TESTS_FORBIDDEN_MARKERS)
        + len(TESTS_EXACT_COUNT_MARKERS)
        + len(BOOTSTRAP_MARKERS)
        + len(BOOTSTRAP_FORBIDDEN_MARKERS)
        + len(BOOTSTRAP_EXACT_COUNT_MARKERS)
        + 2
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_toolchain_pin_scope_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in TESTS_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_TESTS_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for marker in BOOTSTRAP_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_BOOTSTRAP_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_BOOTSTRAP_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for rel_path in (TESTS_README, BOOTSTRAP_NOTES):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, rel_path)) in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the tests-root Phase 2 toolchain pin-scope packet aligned with the current bootstrap note."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET=pass")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_MARKERS)}")
    print(
        "PHASE2_TESTS_README_TOOLCHAIN_PIN_SCOPE_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{len(TESTS_FORBIDDEN_MARKERS) + len(BOOTSTRAP_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
