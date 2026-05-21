#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

ARCHIVE_PACKET_SENTENCE = (
    "current `master` now directly materializes `third_party/README.md`, "
    "`.github/workflows/zigux-bootstrap.yml`, "
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`, and "
    "`scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned "
    "repo-local pinned-archive workflow, bootstrap guard, and archive README contract "
    "explicit here instead of leaving them outside the tests-root reminder"
)
ARCHIVE_REPLAY_SENTENCE = (
    "keep the local-first archive workflow replay surface explicit through "
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, "
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, "
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and "
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`."
)
TOOLCHAIN_REPLAY_SENTENCE = (
    "Keep the current toolchain self-check and replay surface explicit through "
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`, "
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`, "
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, "
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, "
    "`python3 scripts/zigux/install-zig.py --self-test`, and "
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`."
)
INSTALLER_CROSS_PACKET_SENTENCE = (
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, "
    "`python3 scripts/zigux/install-zig.py --self-test`, "
    "`scripts/zigux/check-phase2-cross.py`, "
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`, and "
    "`zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned "
    "installer, direct cross-route, and cross-target fixture packet explicit here "
    "instead of leaving it in the historical-gap bucket"
)
GENKSYMS_PACKET_SENTENCE = (
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, "
    "`scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the "
    "`zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, "
    "bridge helper, wrapper, and fixture roster explicit here instead of leaving it "
    "outside the tests-root reminder"
)
FIXDEP_PACKET_SENTENCE = (
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, "
    "`scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, "
    "`make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so "
    "keep that returned fixdep governance, parity, helper, wrapper, and fixture packet "
    "explicit here instead of leaving it outside the tests-root reminder"
)
LIVE_PACKET_SUMMARY = (
    "the current directly readable Phase 2 packet is the scripts-root kbuild, "
    "installer, direct cross-route, cross-selftest, docs-shared-reminder, "
    "tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, "
    "kconfig bridge checker, genksyms bridge, fixdep governance and parity set plus "
    "the live kconfig bridge helpers, the restored closure-side note, validator "
    "entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their "
    "fixture roster"
)

REQUIRED_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/install-zig.py",
    "third_party/README.md",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    ARCHIVE_PACKET_SENTENCE,
    ARCHIVE_REPLAY_SENTENCE,
    TOOLCHAIN_REPLAY_SENTENCE,
    INSTALLER_CROSS_PACKET_SENTENCE,
    GENKSYMS_PACKET_SENTENCE,
    FIXDEP_PACKET_SENTENCE,
    LIVE_PACKET_SUMMARY,
)

EXACT_COUNT_MARKERS = (
    ARCHIVE_PACKET_SENTENCE,
    ARCHIVE_REPLAY_SENTENCE,
    TOOLCHAIN_REPLAY_SENTENCE,
    INSTALLER_CROSS_PACKET_SENTENCE,
    GENKSYMS_PACKET_SENTENCE,
    FIXDEP_PACKET_SENTENCE,
    LIVE_PACKET_SUMMARY,
)

FORBIDDEN_README_MARKERS = (
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
)

REQUIRED_FILES = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "third_party/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/fixdep/cases.json",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path, readme_rel_path: str) -> list[str]:
    issues: list[str] = []
    readme_path = root / readme_rel_path
    if not readme_path.is_file():
        return [f"missing_file:{readme_rel_path}"]

    readme_text = read_text(readme_path)

    for rel_path in REQUIRED_FILES:
        candidate = root / rel_path
        if not candidate.exists():
            issues.append(f"missing_required_path:{rel_path}")
        elif not candidate.is_file():
            issues.append(f"required_path_not_file:{rel_path}")

    for marker in REQUIRED_README_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing_required_marker:{marker}")

    for marker in EXACT_COUNT_MARKERS:
        count = readme_text.count(marker)
        if count != 1:
            issues.append(f"required_marker_count:{marker}:count={count}:expected=1")

    for marker in FORBIDDEN_README_MARKERS:
        count = readme_text.count(marker)
        if count != 0:
            issues.append(f"forbidden_readme_marker:{marker}:count={count}:expected=0")

    return issues


def build_sample_root(root: Path, readme_rel_path: str) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "placeholder\n")
    write_text(root / readme_rel_path, "\n\n".join(REQUIRED_README_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    readme_rel_path = "zigux/tests/README.md"
    with tempfile.TemporaryDirectory(prefix="phase2_tests_readme_live_tooling_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root, readme_rel_path)
        assert collect_issues(root, readme_rel_path) == []
        case_count += 1

        build_sample_root(root, readme_rel_path)
        readme_path = root / readme_rel_path
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8").replace(REQUIRED_README_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root, readme_rel_path)
        assert f"missing_required_marker:{REQUIRED_README_MARKERS[0]}" in issues
        case_count += 1

        build_sample_root(root, readme_rel_path)
        readme_path = root / readme_rel_path
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8") + "\n" + EXACT_COUNT_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root, readme_rel_path)
        assert f"required_marker_count:{EXACT_COUNT_MARKERS[0]}:count=2:expected=1" in issues
        case_count += 1

        build_sample_root(root, readme_rel_path)
        readme_path = root / readme_rel_path
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8") + "\n" + FORBIDDEN_README_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root, readme_rel_path)
        assert (
            f"forbidden_readme_marker:{FORBIDDEN_README_MARKERS[0]}:count=1:expected=0"
            in issues
        )
        case_count += 1

        build_sample_root(root, readme_rel_path)
        (root / REQUIRED_FILES[0]).unlink()
        issues = collect_issues(root, readme_rel_path)
        assert f"missing_required_path:{REQUIRED_FILES[0]}" in issues
        case_count += 1

        build_sample_root(root, readme_rel_path)
        required_path = root / REQUIRED_FILES[1]
        required_path.unlink()
        required_path.mkdir(parents=True)
        issues = collect_issues(root, readme_rel_path)
        assert f"required_path_not_file:{REQUIRED_FILES[1]}" in issues
        case_count += 1

        issues = collect_issues(root, "missing.md")
        assert "missing_file:missing.md" in issues
        case_count += 1

    print("PHASE2_TESTS_README_LIVE_TOOLING_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_LIVE_TOOLING_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 2 tests-root reminder keeps the current live tooling "
            "packet explicit instead of drifting back toward the older missing-tool story."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--readme-rel-path",
        default="zigux/tests/README.md",
        help="Tests-root README path relative to --root",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root, args.readme_rel_path)
        print(f"PHASE2_TESTS_README_LIVE_TOOLING_SAMPLE_ROOT={args.write_sample_root}")
        print(f"PHASE2_TESTS_README_LIVE_TOOLING_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
        return 0

    issues = collect_issues(args.root, args.readme_rel_path)
    if issues:
        print("PHASE2_TESTS_README_LIVE_TOOLING=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_TESTS_README_LIVE_TOOLING=pass")
    print(f"PHASE2_TESTS_README_LIVE_TOOLING_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
    print(
        f"PHASE2_TESTS_README_LIVE_TOOLING_REQUIRED_MARKER_COUNT={len(REQUIRED_README_MARKERS)}"
    )
    print(f"PHASE2_TESTS_README_LIVE_TOOLING_EXACT_COUNT_CHECKS={len(EXACT_COUNT_MARKERS)}")
    print(
        f"PHASE2_TESTS_README_LIVE_TOOLING_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_README_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())