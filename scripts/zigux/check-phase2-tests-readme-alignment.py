#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REQUIRED_TESTS_README_MARKERS = (
    "Phase 2 review packet",
    "current direct-readback Phase 2 kconfig and genksyms bridge packet:",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/Makefile`",
    "current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, toolchain reminder, and genksyms bridge set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest, artifact-tools, cross-target, kconfig bridge, and genksyms bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)
FORBIDDEN_TESTS_README_MARKERS = (
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "keep the fixture-backed tool-manifest and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)
REQUIRED_DOCS_ROOT_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "now keep the current directly readable Phase 2 toolchain, installer, closure-side, kbuild, kconfig bridge, make-wrapper, and artifact-support packet visible from the docs root instead of rebuilding the older direct cross-route stack from missing current-`master` paths.",
    "keep the docs-root Phase 2 summary aligned to the shipped installer helper, the shipped toolchain checker, the docs-shared-reminder checker, the required-make-route guard, the pinned Zig toolchain policy, the surviving kbuild and alignment guards, the live `conf_bridge` plus `confdata_bridge` helpers, `zigux/Makefile`, the current artifact-support manifest, the current kconfig fixture roster, and the current reminder routes `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    docs_root_text = read_text(resolve_path(root, DOCS_ROOT_README))
    issues = collect_missing_markers(
        tests_readme_text,
        REQUIRED_TESTS_README_MARKERS,
        "MISSING_TESTS_README_MARKERS",
    )
    issues.extend(
        collect_forbidden_markers(
            tests_readme_text,
            FORBIDDEN_TESTS_README_MARKERS,
            "FORBIDDEN_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            docs_root_text,
            REQUIRED_DOCS_ROOT_MARKERS,
            "MISSING_DOCS_ROOT_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TESTS_README_ALIGNMENT=fail")
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
    write_text(resolve_path(root, TESTS_README), "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
        + len(REQUIRED_DOCS_ROOT_MARKERS)
        + 2
    )
    with tempfile.TemporaryDirectory(prefix="zigux_p2_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        for marker in REQUIRED_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1
        for marker in FORBIDDEN_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_README_MARKERS", marker) in issues
            checks_run += 1
        for marker in REQUIRED_DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_MARKERS", marker) in issues
            checks_run += 1
        for path in (TESTS_README, DOCS_ROOT_README):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")
    assert checks_run == expected_case_count
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current directly readable Phase 2 tests-root and docs-root reminder packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_ALIGNMENT_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_ALIGNMENT_DOCS_ROOT_MARKER_COUNT={len(REQUIRED_DOCS_ROOT_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
