#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DOCS_README = Path("Documentation/zigux/README.md")
TOOLCHAIN_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")

ARCHIVE_PATH = "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`"
ARCHIVE_COMMAND = (
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz "
    "--archive-target x86_64-linux`"
)
LOCAL_FIRST_ORDER = "local-first `third_party`, mirror, then direct-download bootstrap order"

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    DOCS_README: (
        "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again",
        ARCHIVE_COMMAND,
        LOCAL_FIRST_ORDER,
    ),
    TOOLCHAIN_NOTES: (
        "`third_party/README.md` is directly readable on current `master`",
        ARCHIVE_COMMAND,
        "`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py`",
        "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
    ),
    REVIEW_CHECKLIST: (
        "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `third_party/README.md`",
        "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
        "`scripts/zigux/check-lane05-local-archive-readme.py`",
        ARCHIVE_COMMAND,
    ),
    TESTS_README: (
        "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`",
        ARCHIVE_PATH,
        ARCHIVE_COMMAND,
        LOCAL_FIRST_ORDER,
    ),
    THIRD_PARTY_README: (
        ARCHIVE_PATH,
        ARCHIVE_COMMAND,
        "`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
    ),
}


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(root: Path) -> list[tuple[str, str, str]]:
    issues: list[tuple[str, str, str]] = []
    for rel_path, markers in FILE_MARKERS.items():
        text = read_text(resolve(root, rel_path))
        for marker in markers:
            if marker not in text:
                issues.append((str(rel_path), "missing_marker", marker))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(resolve(root, rel_path), "\n".join(markers) + "\n")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    case_count = 0
    expected_case_count = 1 + sum(len(markers) for markers in FILE_MARKERS.values()) + len(FILE_MARKERS)

    with tempfile.TemporaryDirectory(prefix="lane25_shared_local_archive_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                write_sample_root(root)
                path = resolve(root, rel_path)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (str(rel_path), "missing_marker", marker) in issues
                case_count += 1

        for rel_path in FILE_MARKERS:
            write_sample_root(root)
            resolve(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                case_count += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert case_count == expected_case_count
    print("PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def emit_issues(root: Path, issues: list[tuple[str, str, str]]) -> int:
    print("PHASE2_SHARED_LOCAL_ARCHIVE_PACKET=fail")
    print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_ROOT={root}")
    for rel_path, code, marker in issues:
        print(f"{code}:{rel_path}:{marker}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 2 repo-local archive reminder packet drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(root, issues)

    print("PHASE2_SHARED_LOCAL_ARCHIVE_PACKET=pass")
    print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_ROOT={root}")
    print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_REQUIRED_PATH_COUNT={len(FILE_MARKERS)}")
    print(f"PHASE2_SHARED_LOCAL_ARCHIVE_PACKET_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
