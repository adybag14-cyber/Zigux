#!/usr/bin/env python3
"""Guard the current scripts-root Phase 2 toolchain reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"

SURFACE_PATHS = (
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
    ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md",
    ROOT / "Documentation" / "zigux" / "phase2-closure.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
)

REQUIRED_MARKERS = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "- `scripts/zigux/kconfig/conf_bridge.zig` keeps the shipped sixteen-mode request-plan bridge explicit from the scripts root, including the `helpnewconfig` `silent` option handling and the same `randconfig`, `defconfig`, `savedefconfig`, and `syncconfig` argument surfaces that the Phase 2 wrapper-first roadmap tranche expects",
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "- keep those installer, tool-manifest, direct cross-route, and genksyms bridge surfaces explicit beside the shipped toolchain and kbuild reminder packet",
    "- if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence",
)

FORBIDDEN_MARKERS = (
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(REQUIRED_MARKERS)
    + len(REQUIRED_MARKERS)
    + len(FORBIDDEN_MARKERS)
    + len(SURFACE_PATHS)
    + 1
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def remove_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def build_self_test_root(root: Path) -> None:
    readme_lines = ["# scripts/zigux", "", "## Phase 2", "", *REQUIRED_MARKERS]
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(readme_lines) + "\n")
    for path in SURFACE_PATHS:
        if path == SCRIPTS_README:
            continue
        write_text(resolve_path(root, path), "present\n")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    readme_text = read_text(resolve_path(root, SCRIPTS_README))

    for marker in REQUIRED_MARKERS:
        count = count_exact_lines(readme_text, marker)
        if count == 0:
            issues.append(("MISSING_SCRIPTS_README_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SCRIPTS_README_MARKERS", f"{marker}:count={count}"))

    for marker in FORBIDDEN_MARKERS:
        if marker in readme_text:
            issues.append(("FORBIDDEN_SCRIPTS_README_MARKERS", marker))

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_readme_toolchain_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(remove_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SCRIPTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(duplicate_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_SCRIPTS_README_MARKERS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_SCRIPTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for path in SURFACE_PATHS:
            if path == SCRIPTS_README:
                continue
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, SCRIPTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing scripts README did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current scripts-root Phase 2 toolchain reminder packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
