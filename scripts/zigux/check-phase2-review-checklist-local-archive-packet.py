#!/usr/bin/env python3
"""Guard the Lane 25 review-checklist local-first archive packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")

REQUIRED_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "third_party/README.md",
)

REVIEW_MARKERS = (
    "`third_party/README.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
)

TESTS_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
)

THIRD_PARTY_MARKERS = (
    "# Zigux third-party archives",
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards",
)

SAMPLE_REVIEW = """# Zigux Review Checklist
* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `third_party/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/zig-toolchain-policy.json`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/cases.json`, and `zigux/tests/fixtures/fixdep/cases.json` still agree on the current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet, while `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, `python3 scripts/zigux/check-lane05-local-archive-readme.py`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay explicit as the current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet?
"""

SAMPLE_TESTS = """# zigux/tests
current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder
keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers
keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.
"""

SAMPLE_THIRD_PARTY = """# Zigux third-party archives

## Current pinned Zig archive contract

- target: `x86_64-linux`
- channel: `0.17.0-dev.87+9b177a7d2`
- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`
- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`
- size: `58159088` bytes

## Validation

- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`

## Bootstrap order

- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.
- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.
"""


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"phase2 review-checklist local-archive checker missing file: {path}"
        ) from exc
    except OSError as exc:
        raise SystemExit(
            f"phase2 review-checklist local-archive checker unreadable file {path}: {exc}"
        ) from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase2 review-checklist local-archive checker missing {label} marker: {marker}"
            )


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(
                f"phase2 review-checklist local-archive checker missing required path: {path}"
            )


def check_root(root: Path) -> None:
    require_paths(root)
    review_text = read_text(root, REVIEW_CHECKLIST)
    tests_text = read_text(root, TESTS_README)
    third_party_text = read_text(root, THIRD_PARTY_README)
    require_markers(review_text, REVIEW_MARKERS, "review checklist")
    require_markers(tests_text, TESTS_MARKERS, "tests README")
    require_markers(third_party_text, THIRD_PARTY_MARKERS, "third_party README")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST, SAMPLE_REVIEW)
    write_text(root / TESTS_README, SAMPLE_TESTS)
    write_text(root / THIRD_PARTY_README, SAMPLE_THIRD_PARTY)
    for rel in REQUIRED_PATHS[:-1]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# placeholder\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_review_checklist_local_archive_") as tmp:
        sample_root = Path(tmp)
        write_sample_root(sample_root)
        check_root(sample_root)
        case_count += 1

        broken_review = sample_root / REVIEW_CHECKLIST
        broken_review.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "review checklist marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing review marker failure")
        write_sample_root(sample_root)

        broken_tests = sample_root / TESTS_README
        broken_tests.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "tests README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing tests marker failure")
        write_sample_root(sample_root)

        broken_third_party = sample_root / THIRD_PARTY_README
        broken_third_party.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "third_party README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing third_party marker failure")
        write_sample_root(sample_root)

        missing_required = sample_root / "scripts/zigux/check-lane05-local-first-archive-workflow.py"
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_SELF_TEST=pass")
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT="
        f"{case_count}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 25 Phase 2 review-checklist local-first archive packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    check_root(args.root.resolve())
    print("PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_ROOT={args.root.resolve()}")
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_REQUIRED_PATH_COUNT="
        f"{len(REQUIRED_PATHS)}"
    )
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_REVIEW_MARKER_COUNT="
        f"{len(REVIEW_MARKERS)}"
    )
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_TESTS_MARKER_COUNT="
        f"{len(TESTS_MARKERS)}"
    )
    print(
        "PHASE2_REVIEW_CHECKLIST_LOCAL_ARCHIVE_PACKET_THIRD_PARTY_MARKER_COUNT="
        f"{len(THIRD_PARTY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
