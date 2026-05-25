#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"

REQUIRED_MARKERS = (
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/Makefile`",
    "keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "the current docs-root Phase 2 reminder packet should stay parked on `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`, with `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, the current kconfig bridge manifests, and the current genksyms bridge fixture roster keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

EXACT_COUNT_MARKERS = (
    "Phase 2 notes",
    "keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "the current docs-root Phase 2 reminder packet should stay parked on `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`, with `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, the current kconfig bridge manifests, and the current genksyms bridge fixture roster keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, DOCS_README))
    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_DOCS_ROOT_SUMMARY_MARKERS", marker))
    for marker in EXACT_COUNT_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_DOCS_ROOT_SUMMARY_MARKERS", f"{count}::{marker}"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_ROOT_SUMMARY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_README), "\n".join(REQUIRED_MARKERS) + "\n")


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_MARKERS) + len(EXACT_COUNT_MARKERS)
    with tempfile.TemporaryDirectory(prefix="zigux_p2_docs_root_summary_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        readme_path = resolve_path(root, DOCS_README)
        text = read_text(readme_path)

        for marker in REQUIRED_MARKERS:
            write_text(readme_path, remove_all(text, marker))
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_SUMMARY_MARKERS", marker) in issues, (marker, issues)
            build_sample_root(root)
            text = read_text(readme_path)
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            write_text(readme_path, text + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_DOCS_ROOT_SUMMARY_MARKERS", f"2::{marker}") in issues, (marker, issues)
            build_sample_root(root)
            text = read_text(readme_path)
            checks_run += 1

        if checks_run != expected_case_count:
            raise AssertionError(
                f"self-test count drift: expected {expected_case_count}, got {checks_run}"
            )

    print("PHASE2_DOCS_ROOT_SUMMARY=self-test-pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in regression checks instead of repo validation.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root and exit.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (defaults to current repo root).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_DOCS_ROOT_SUMMARY_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_ROOT_SUMMARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
