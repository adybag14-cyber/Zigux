#!/usr/bin/env python3
"""Guard the Lane 25 docs-root local-first archive packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

DOCS_README = Path("Documentation/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")

REQUIRED_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "third_party/README.md",
)

DOCS_MARKERS = (
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again",
    "keep the repo-local pinned archive contract",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "the local-first `third_party`, mirror, then direct-download bootstrap order",
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
    "Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards",
)

FORBIDDEN_DOCS_MARKERS = (
    "repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet",
)

FORBIDDEN_TESTS_MARKERS = (
    "the pinned `x86_64-linux` archive note and repo-local `.zig-toolchain` fallback tied to the shipped toolchain checker",
)

SAMPLE_DOCS = """# Zigux Documentation
Phase 2 notes
- `third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.
"""

SAMPLE_TESTS = """# zigux/tests
current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder
keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers
keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.
"""

SAMPLE_THIRD_PARTY = """# Zigux third-party archives

Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.
If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.
`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.
"""


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 docs-readme local-archive checker missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"phase2 docs-readme local-archive checker unreadable file {path}: {exc}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase2 docs-readme local-archive checker missing {label} marker: {marker}"
            )


def forbid_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise SystemExit(
                f"phase2 docs-readme local-archive checker found forbidden {label} marker: {marker}"
            )


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(
                f"phase2 docs-readme local-archive checker missing required path: {path}"
            )


def check_root(root: Path) -> None:
    require_paths(root)
    docs_text = read_text(root, DOCS_README)
    tests_text = read_text(root, TESTS_README)
    third_party_text = read_text(root, THIRD_PARTY_README)
    require_markers(docs_text, DOCS_MARKERS, "docs README")
    require_markers(tests_text, TESTS_MARKERS, "tests README")
    require_markers(third_party_text, THIRD_PARTY_MARKERS, "third_party README")
    forbid_markers(docs_text, FORBIDDEN_DOCS_MARKERS, "docs README")
    forbid_markers(tests_text, FORBIDDEN_TESTS_MARKERS, "tests README")


def write_sample_root(root: Path) -> None:
    (root / DOCS_README).parent.mkdir(parents=True, exist_ok=True)
    (root / TESTS_README).parent.mkdir(parents=True, exist_ok=True)
    (root / THIRD_PARTY_README).parent.mkdir(parents=True, exist_ok=True)
    (root / DOCS_README).write_text(SAMPLE_DOCS, encoding="utf-8")
    (root / TESTS_README).write_text(SAMPLE_TESTS, encoding="utf-8")
    (root / THIRD_PARTY_README).write_text(SAMPLE_THIRD_PARTY, encoding="utf-8")
    for rel in REQUIRED_PATHS[:-1]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# placeholder\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_local_archive_sample_") as tmp:
        sample_root = Path(tmp)
        write_sample_root(sample_root)
        check_root(sample_root)
        case_count += 1

        missing_docs = sample_root / DOCS_README
        missing_docs.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "docs README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing docs marker failure")
        write_sample_root(sample_root)

        forbidden_docs = sample_root / DOCS_README
        forbidden_docs.write_text(
            SAMPLE_DOCS + FORBIDDEN_DOCS_MARKERS[0] + "\n", encoding="utf-8"
        )
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "forbidden docs README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected forbidden docs marker failure")
        write_sample_root(sample_root)

        missing_required = sample_root / "scripts/zigux/check-lane05-local-archive-readme.py"
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")
        write_sample_root(sample_root)

        forbidden_tests = sample_root / TESTS_README
        forbidden_tests.write_text(
            SAMPLE_TESTS + FORBIDDEN_TESTS_MARKERS[0] + "\n", encoding="utf-8"
        )
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "forbidden tests README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected forbidden tests marker failure")

    print("PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_SELF_TEST=pass")
    print(
        "PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT="
        f"{case_count}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 25 Phase 2 docs-root local-first archive packet."
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
    print("PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET=pass")
    print(f"PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_ROOT={args.root.resolve()}")
    print(
        "PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_REQUIRED_PATH_COUNT="
        f"{len(REQUIRED_PATHS)}"
    )
    print(
        "PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_DOCS_MARKER_COUNT="
        f"{len(DOCS_MARKERS)}"
    )
    print(
        "PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_TESTS_MARKER_COUNT="
        f"{len(TESTS_MARKERS)}"
    )
    print(
        "PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_THIRD_PARTY_MARKER_COUNT="
        f"{len(THIRD_PARTY_MARKERS)}"
    )
    print(
        "PHASE2_DOCS_README_LOCAL_ARCHIVE_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{len(FORBIDDEN_DOCS_MARKERS) + len(FORBIDDEN_TESTS_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
