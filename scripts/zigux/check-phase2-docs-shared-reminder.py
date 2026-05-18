#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"

DOCS_README_MARKERS = (
    "Phase 2 notes",
    "- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/README.md`",
    "- `scripts/zigux/check-zig-toolchain.py`",
    "- `scripts/zigux/check-phase2-kbuild-routes.py`",
    "- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "- `scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "- `scripts/zigux/check-phase2-toolchain-pinning.py`",
    "- `scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "- `scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "- `scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "- `scripts/zigux/check-phase2-required-make-routes.py`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "- `scripts/zigux/kconfig/conf_bridge.zig`",
    "- `scripts/zigux/kconfig/confdata_bridge.zig`",
    "- `scripts/zigux/zig-toolchain-policy.json`",
    "- `zigux/Makefile`",
    "- `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "- `zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "current directly readable Phase 2 toolchain, kbuild, kconfig bridge, make-wrapper, and artifact-support packet",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "historical packet members until same-lane work rematerializes them on `master`",
    "keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the docs-shared-reminder checker, the required-make-route guard, the pinned Zig toolchain policy, the surviving kbuild and alignment guards, the live `conf_bridge` plus `confdata_bridge` helpers, `zigux/Makefile`, the current artifact-support manifest, the current kconfig fixture roster, and the current reminder routes `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "without reviving missing closure, cross-target, or installer proof text",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "current directly readable Phase 2 toolchain, kbuild, kconfig bridge, docs-shared-reminder, and required-make-route packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`zigux/Makefile`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2`",
    "historical packet members rather than shipped current-`master` evidence",
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, DOCS_README)),
            DOCS_README_MARKERS,
            "MISSING_DOCS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, REVIEW_CHECKLIST)),
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_SHARED_REMINDER=fail")
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
    write_text(resolve_path(root, DOCS_README), "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(DOCS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + 2
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_shared_reminder_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in DOCS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_DOCS_README_MARKERS", marker) in issues)
            checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues)
            checks_run += 1

        for rel_path in (DOCS_README, REVIEW_CHECKLIST):
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
    print("PHASE2_DOCS_SHARED_REMINDER_SELF_TEST=pass")
    print(f"PHASE2_DOCS_SHARED_REMINDER_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 docs-root and review-checklist reminder packet aligned to current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_SHARED_REMINDER=pass")
    print(
        "PHASE2_DOCS_SHARED_REMINDER_MARKER_COUNT="
        f"{len(DOCS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())