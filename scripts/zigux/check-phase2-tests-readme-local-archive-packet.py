#!/usr/bin/env python3
"""Guard the Lane 25 tests-root local-first archive packet."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")

ARCHIVE_REPLAY = (
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`"
)

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "third_party/README.md",
)

REVIEW_MARKERS = (
    "`third_party/README.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    ARCHIVE_REPLAY,
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
)

TESTS_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
)

THIRD_PARTY_MARKERS = (
    "# Zigux third-party archives",
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    f"- {ARCHIVE_REPLAY}",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
    "- Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
    "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
    "- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
)

def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 tests-readme local-archive checker missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"phase2 tests-readme local-archive checker unreadable file {path}: {exc}") from exc


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"phase2 tests-readme local-archive checker missing required path: {path}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase2 tests-readme local-archive checker missing {label} marker: {marker}"
            )


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, REVIEW_CHECKLIST), REVIEW_MARKERS, "review checklist")
    require_markers(read_text(root, TESTS_README), TESTS_MARKERS, "tests README")
    require_markers(read_text(root, THIRD_PARTY_README), THIRD_PARTY_MARKERS, "third_party README")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST, "\n".join(REVIEW_MARKERS) + "\n")
    write_text(root / TESTS_README, "\n".join(TESTS_MARKERS) + "\n")
    write_text(root / THIRD_PARTY_README, "\n".join(THIRD_PARTY_MARKERS) + "\n")
    for rel in REQUIRED_PATHS:
        path = root / rel
        if rel == THIRD_PARTY_README.as_posix():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("# placeholder\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_tests_readme_local_archive_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        check_root(root)
        case_count += 1

        broken_review = root / REVIEW_CHECKLIST
        broken_review.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "review checklist marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing review checklist marker failure")
        write_sample_root(root)

        broken_tests = root / TESTS_README
        broken_tests.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "tests README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing tests README marker failure")
        write_sample_root(root)

        broken_third_party = root / THIRD_PARTY_README
        broken_third_party.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "third_party README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing third_party README marker failure")
        write_sample_root(root)

        missing_required = root / "scripts/zigux/check-lane05-local-first-archive-workflow.py"
        missing_required.unlink()
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")
        write_sample_root(root)

        missing_workflow = root / ".github/workflows/zigux-bootstrap.yml"
        missing_workflow.unlink()
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing workflow path failure")

    print("PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 25 Phase 2 tests-root local-first archive packet."
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

    root = args.root.resolve()
    check_root(root)
    print("PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET=pass")
    print(f"PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_ROOT={root}")
    print(f"PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(
        "PHASE2_TESTS_README_LOCAL_ARCHIVE_PACKET_THIRD_PARTY_MARKER_COUNT="
        f"{len(THIRD_PARTY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
