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
    "- `scripts/zigux/install-zig.py`",
    "- `scripts/zigux/check-phase2-cross.py`",
    "- `python3 scripts/zigux/install-zig.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "- `scripts/zigux/check-kconfig-bridge.py`",
    "- `scripts/zigux/check-genksyms-bridge.py`",
    "- `scripts/zigux/genksyms.zig`",
    "- `zigux/tests/fixtures/phase2_cross_targets.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "current directly readable Phase 2 toolchain, installer, closure-side, kbuild, kconfig bridge, direct cross-route, make-wrapper, and artifact-support packet",
    "direct current-tree readback plus `zigux/tests/README.md` are the source of truth for the returned installer, direct cross-route, and cross-target fixture packet on current `master`.",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md` and `scripts/zigux/README.md` still carry older repo-reality-gap wording for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the returned installer helper, the docs-shared-reminder checker, the required-make-route guard, the shipped `check-kconfig-bridge.py` surface, the bounded `genksyms` helper and bridge checker packet",
    "`make -C zigux phase2-genksyms`",
    "keep the pinned policy-only, installer self-test, direct cross self-test, and archive-integrity replays explicit without widening beyond the current directly readable Phase 2 packet.",
)
DOCS_README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "historical packet members until same-lane work rematerializes them on `master`",
)
REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "current directly readable Phase 2 toolchain, installer, kbuild, kconfig bridge, direct cross-route, docs-shared-reminder, and required-make-route packet",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-genksyms`",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, installer-selftest, direct-cross-selftest, artifact-support, toolchain self-check, and make-wrapper packet?",
    "direct current-tree readback plus `zigux/tests/README.md` outrank the lagging repo-reality-gap wording still present in `Documentation/zigux/phase2-toolchain-bootstrap-notes.md` and `scripts/zigux/README.md` for the returned installer, direct cross-route, and cross-target fixture packet, while direct current-tree readback plus `zigux/tests/fixtures/phase2_tool_manifest.json` outrank the still-lagging reminder wording for the shipped `check-kconfig-bridge.py` surface and bounded `genksyms` helper/checker packet.",
)
REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
    "current directly readable Phase 2 toolchain, kbuild, kconfig bridge, docs-shared-reminder, and required-make-route packet",
)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError as exc:
        raise SystemExit(f'required file missing: {path}') from exc

def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path

def collect_missing_markers(text: str, markers: tuple[str, ...], code: str):
    return [(code, marker) for marker in markers if marker not in text]

def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str):
    return [(code, marker) for marker in markers if marker in text]

def collect_issues(root: Path):
    issues = []
    docs_readme_text = read_text(resolve_path(root, DOCS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    issues.extend(collect_missing_markers(docs_readme_text, DOCS_README_MARKERS, 'MISSING_DOCS_README_MARKERS'))
    issues.extend(collect_forbidden_markers(docs_readme_text, DOCS_README_FORBIDDEN_MARKERS, 'FORBIDDEN_DOCS_README_MARKERS'))
    issues.extend(collect_missing_markers(review_checklist_text, REVIEW_CHECKLIST_MARKERS, 'MISSING_REVIEW_CHECKLIST_MARKERS'))
    issues.extend(collect_forbidden_markers(review_checklist_text, REVIEW_CHECKLIST_FORBIDDEN_MARKERS, 'FORBIDDEN_REVIEW_CHECKLIST_MARKERS'))
    return issues

def emit_issues(issues):
    grouped = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print('PHASE2_DOCS_SHARED_REMINDER=fail')
    for code, values in grouped.items():
        print(f'{code}_START')
        for value in values:
            print(value)
        print(f'{code}_END')
    return 1

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_README), '\n'.join(DOCS_README_MARKERS) + '\n')
    write_text(resolve_path(root, REVIEW_CHECKLIST), '\n'.join(REVIEW_CHECKLIST_MARKERS) + '\n')

def replace_once(text: str, marker: str, replacement: str = '') -> str:
    if marker not in text:
        raise AssertionError(f'marker not found: {marker}')
    return text.replace(marker, replacement, 1)

def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(DOCS_README_MARKERS) + len(DOCS_README_FORBIDDEN_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS) + 2
    with tempfile.TemporaryDirectory(prefix='zigux_phase2_docs_shared_reminder_') as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        for marker in DOCS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding='utf-8'), marker), encoding='utf-8')
            issues = collect_issues(root)
            assert ('MISSING_DOCS_README_MARKERS', marker) in issues
            checks_run += 1
        for marker in DOCS_README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(path.read_text(encoding='utf-8') + marker + '\n', encoding='utf-8')
            issues = collect_issues(root)
            assert ('FORBIDDEN_DOCS_README_MARKERS', marker) in issues
            checks_run += 1
        for marker in REVIEW_CHECKLIST_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding='utf-8'), marker), encoding='utf-8')
            issues = collect_issues(root)
            assert ('MISSING_REVIEW_CHECKLIST_MARKERS', marker) in issues
            checks_run += 1
        for marker in REVIEW_CHECKLIST_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(path.read_text(encoding='utf-8') + marker + '\n', encoding='utf-8')
            issues = collect_issues(root)
            assert ('FORBIDDEN_REVIEW_CHECKLIST_MARKERS', marker) in issues
            checks_run += 1
        for rel_path in (DOCS_README, REVIEW_CHECKLIST):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert 'required file missing' in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f'missing file did not abort: {rel_path}')
    assert checks_run == expected_case_count
    print('PHASE2_DOCS_SHARED_REMINDER_SELF_TEST=pass')
    print(f'PHASE2_DOCS_SHARED_REMINDER_SELF_TEST_CASE_COUNT={checks_run}')
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description='Keep the shared Phase 2 docs-root reminder packet aligned to current repo reality.')
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root to inspect')
    parser.add_argument('--self-test', action='store_true', help='Run the built-in contract self-test')
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print('PHASE2_DOCS_SHARED_REMINDER=pass')
    print(f'PHASE2_DOCS_SHARED_REMINDER_MARKER_COUNT={len(DOCS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS)}')
    print(f'PHASE2_DOCS_SHARED_REMINDER_FORBIDDEN_MARKER_COUNT={len(DOCS_README_FORBIDDEN_MARKERS) + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
