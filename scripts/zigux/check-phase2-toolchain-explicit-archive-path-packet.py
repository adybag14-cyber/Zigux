#!/usr/bin/env python3
"""Validate the Phase 2 explicit Zig archive path contract."""

import argparse
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = Path("scripts/zigux/check-zig-toolchain.py")

REQUIRED_SOURCE_MARKERS = (
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    "describe_invalid_explicit_archive_path",
    "explicit archive path is a directory, expected a regular file",
    "explicit archive path does not exist",
    "archive target {target!r} is outside archive_target_scope",
    "archive target must be explicit when policy covers multiple archive targets",
    "archive_name_matches_policy(path.name, expected_filename)",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}",
)

REQUIRED_ORDERED_MARKERS = (
    ("resolve_policy_archive(args.archive, args.archive_target)", "describe_invalid_explicit_archive_path(archive_path)"),
    ("describe_invalid_explicit_archive_path(archive_path)", "if archive_path is None or not archive_path.is_file():"),
    ("validate_policy_archive(", "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")"),
)

SAMPLE_CHECKER = '''#!/usr/bin/env python3
import argparse
from pathlib import Path


def describe_invalid_explicit_archive_path(archive_path):
    if not archive_path.exists():
        return None
    if archive_path.is_dir():
        return f"explicit archive path is a directory, expected a regular file: {archive_path}"
    return None


def archive_name_matches_policy(path_name, expected_filename):
    return path_name == expected_filename


def resolve_policy_archive(explicit_archive, explicit_target):
    target = explicit_target
    if target == "outside":
        raise ValueError(f"archive target {target!r} is outside archive_target_scope in policy: x86_64-linux")
    if explicit_target is None and explicit_archive == "multi-target.tar.xz":
        raise ValueError("archive target must be explicit when policy covers multiple archive targets")
    return explicit_target, explicit_archive


def validate_policy_archive(path, archive_target):
    expected_filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
    if not archive_name_matches_policy(path.name, expected_filename):
        return "mismatch", "expected archive filename", "0" * 64, "1" * 64
    return "present", None, "0" * 64, "0" * 64


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-only", action="store_true")
    parser.add_argument("--archive")
    parser.add_argument("--archive-target")
    args = parser.parse_args()
    if args.archive_only:
        try:
            resolve_policy_archive(args.archive, args.archive_target)
        except ValueError:
            print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")
            return 1
        archive_path = Path(args.archive) if args.archive is not None else None
        if args.archive is not None and archive_path is not None:
            describe_invalid_explicit_archive_path(archive_path)
        if archive_path is None or not archive_path.is_file():
            print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")
            print("explicit archive path does not exist")
            return 1
        archive_status, note, expected_sha, actual_sha = validate_policy_archive(
            archive_path,
            args.archive_target or "unresolved",
        )
        print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")
        return 0 if note is None else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


@dataclass(frozen=True)
class PacketResult:
    marker_count: int
    ordered_pair_count: int


def read_checker(root: Path) -> str:
    checker = root / CHECKER_PATH
    if not checker.is_file():
        raise ValueError(f"missing required checker: {checker}")
    return checker.read_text(encoding="utf-8")


def validate_source(root: Path) -> PacketResult:
    source = read_checker(root)
    missing_markers = [marker for marker in REQUIRED_SOURCE_MARKERS if marker not in source]
    if missing_markers:
        raise ValueError(
            "phase2_toolchain_explicit_archive_path_packet:missing_markers:"
            + ",".join(missing_markers)
        )

    missing_order = []
    for before, after in REQUIRED_ORDERED_MARKERS:
        before_index = source.find(before)
        after_index = -1 if before_index == -1 else source.find(after, before_index + len(before))
        if before_index == -1 or after_index == -1:
            missing_order.append(f"{before} -> {after}")
    if missing_order:
        raise ValueError(
            "phase2_toolchain_explicit_archive_path_packet:missing_order:"
            + ",".join(missing_order)
        )

    return PacketResult(
        marker_count=len(REQUIRED_SOURCE_MARKERS),
        ordered_pair_count=len(REQUIRED_ORDERED_MARKERS),
    )


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    checker = root / CHECKER_PATH
    checker.parent.mkdir(parents=True, exist_ok=True)
    checker.write_text(SAMPLE_CHECKER, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_raises(fn, expected: str) -> None:
        nonlocal case_count
        try:
            fn()
        except ValueError as exc:
            assert expected in str(exc)
            case_count += 1
            return
        raise AssertionError("expected ValueError")

    with tempfile.TemporaryDirectory(prefix="zigux_explicit_archive_packet_") as tmp:
        root = Path(tmp) / "sample"
        write_sample_root(root)
        result = validate_source(root)
        assert result.marker_count == len(REQUIRED_SOURCE_MARKERS)
        assert result.ordered_pair_count == len(REQUIRED_ORDERED_MARKERS)
        case_count += 1

        checker = root / CHECKER_PATH
        original = checker.read_text(encoding="utf-8")
        checker.write_text(original.replace('parser.add_argument("--archive"', "parser.add_argument('--archive'"), encoding="utf-8")
        expect_raises(lambda: validate_source(root), "missing_markers")
        checker.write_text(
            original.replace(
                "            describe_invalid_explicit_archive_path(archive_path)",
                "            # directory guard removed",
                1,
            ),
            encoding="utf-8",
        )
        expect_raises(lambda: validate_source(root), "missing_order")
        checker.write_text(original.replace("archive target {target!r} is outside archive_target_scope", "archive target is invalid"), encoding="utf-8")
        expect_raises(lambda: validate_source(root), "missing_markers")

    print("PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run generated-sample checker tests.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample repository root for replay.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        result = validate_source(args.root)
    except ValueError as exc:
        print("PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET=fail")
        print(f"PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET_NOTE={exc}")
        return 1

    print("PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET_MARKER_COUNT={result.marker_count}")
    print(f"PHASE2_TOOLCHAIN_EXPLICIT_ARCHIVE_PATH_PACKET_ORDERED_PAIR_COUNT={result.ordered_pair_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
