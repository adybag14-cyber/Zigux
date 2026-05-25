#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

REQUIRED_DOCS_ROOT_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
    "keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

EXACT_COUNT_DOCS_ROOT_MARKERS = (
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_TESTS_README_MARKERS = (
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)

EXACT_COUNT_TESTS_README_MARKERS = (
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)

FORBIDDEN_TESTS_README_MARKERS = (
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, and genksyms bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder\n\nkeep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
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


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    docs_root_text = read_text(resolve_path(root, DOCS_ROOT_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    issues = collect_missing_markers(
        docs_root_text, REQUIRED_DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKER"
    )
    issues.extend(
        collect_exact_count_markers(
            docs_root_text, EXACT_COUNT_DOCS_ROOT_MARKERS, "DOCS_ROOT_EXACT_COUNT_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text, REQUIRED_TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"
        )
    )
    issues.extend(
        collect_exact_count_markers(
            tests_readme_text, EXACT_COUNT_TESTS_README_MARKERS, "TESTS_README_EXACT_COUNT_MARKER"
        )
    )
    issues.extend(
        collect_forbidden_markers(
            tests_readme_text, FORBIDDEN_TESTS_README_MARKERS, "FORBIDDEN_TESTS_README_MARKER"
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_README_FIXDEP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    write_text(
        resolve_path(root, TESTS_README),
        "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n",
    )


def write_sample_root(root: Path) -> None:
    build_self_test_root(root)


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_DOCS_ROOT_MARKERS)
        + len(EXACT_COUNT_DOCS_ROOT_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(EXACT_COUNT_TESTS_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
        + 2
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_fixdep_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_MARKER", marker) in issues
            checks_run += 1

        for marker in EXACT_COUNT_DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("DOCS_ROOT_EXACT_COUNT_MARKER", f"2::{marker}") in issues
            checks_run += 1

        for marker in REQUIRED_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKER", marker) in issues
            checks_run += 1

        for marker in EXACT_COUNT_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("TESTS_README_EXACT_COUNT_MARKER", f"2::{marker}") in issues
            checks_run += 1

        for marker in FORBIDDEN_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_README_MARKER", marker) in issues
            checks_run += 1

        for path in (DOCS_ROOT_README, TESTS_README):
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
    print("PHASE2_DOCS_README_FIXDEP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_DOCS_README_FIXDEP_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the docs-root Phase 2 fixdep reminder packet aligned with tests-root evidence."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--self-test", action="store_true", help="Run built-in contract checks"
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal current-like sample root for replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print("PHASE2_DOCS_README_FIXDEP_PACKET_SAMPLE_ROOT=written")
        print(f"PHASE2_DOCS_README_FIXDEP_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_README_FIXDEP_PACKET=pass")
    print(f"PHASE2_DOCS_README_FIXDEP_PACKET_DOCS_MARKER_COUNT={len(REQUIRED_DOCS_ROOT_MARKERS)}")
    print(
        f"PHASE2_DOCS_README_FIXDEP_PACKET_TESTS_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}"
    )
    print(
        f"PHASE2_DOCS_README_FIXDEP_PACKET_TESTS_EXACT_COUNT_MARKER_COUNT={len(EXACT_COUNT_TESTS_README_MARKERS)}"
    )
    print(
        f"PHASE2_DOCS_README_FIXDEP_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_TESTS_README_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
