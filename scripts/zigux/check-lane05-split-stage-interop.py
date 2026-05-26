#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")

SPLIT_SHARED_MANIFEST_LINES = (
    '"encoding": "base64"',
    '"parts_glob": "part-*.b64"',
)
STAGE_SHARED_MANIFEST_LINES = (
    'if encoding != "base64":',
    'if parts_glob != "part-*.b64":',
)

SHARED_SHARD_PATTERN = 'part-{index:03d}.b64'

SPLIT_ONLY_MARKERS = (
    '(output_dir / f"part-{index:03d}.b64").write_text(',
    '"part_count": part_count,',
    'manifest_path = write_manifest(',
    'SPLIT_PINNED_ZIG_ARCHIVE=pass',
    'SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST=',
    'SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT=',
)

STAGE_ONLY_MARKERS = (
    'def reconstruct_archive_from_parts(',
    'manifest = load_shard_manifest(parts_dir)',
    'filename = require_manifest_string(manifest, "filename", manifest_path)',
    'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
    'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
    'size = require_manifest_int(manifest, "size", manifest_path)',
    'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
    'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
    'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
    'shard_path = parts_dir / f"part-{index:03d}.b64"',
    'base64.b64decode(encoded, validate=True)',
    '--parts-dir',
    'STAGE_PINNED_ZIG_ARCHIVE=pass',
    'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=parts_dir',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-stage interop missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 split-stage interop expected exactly {expected} {label} markers `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-stage interop missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"lane05 split-stage interop expected {label} `{earlier}` before `{later}`")


def check_split_helper(root: Path) -> int:
    split_text = read_text(root / SPLIT_HELPER_PATH)

    for marker in SPLIT_SHARED_MANIFEST_LINES:
        require_marker(split_text, marker, "split-helper shared manifest marker")
    for marker in SPLIT_ONLY_MARKERS:
        require_marker(split_text, marker, "split-helper marker")

    require_exact_count(split_text, SPLIT_SHARED_MANIFEST_LINES[0], 1, "split-helper encoding")
    require_exact_count(split_text, SPLIT_SHARED_MANIFEST_LINES[1], 1, "split-helper parts_glob")
    require_exact_count(split_text, SHARED_SHARD_PATTERN, 1, "split-helper shard pattern")

    require_order(
        split_text,
        '"chunk_bytes": chunk_bytes,',
        '"part_count": part_count,',
        "split manifest field order",
    )
    require_order(
        split_text,
        '"part_count": part_count,',
        '"parts_glob": "part-*.b64",',
        "split manifest field order",
    )
    require_order(
        split_text,
        "manifest_path = write_manifest(",
        "SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST=",
        "split manifest output order",
    )

    return len(SPLIT_SHARED_MANIFEST_LINES) + len(SPLIT_ONLY_MARKERS) + 1


def check_stage_helper(root: Path) -> int:
    stage_text = read_text(root / STAGE_HELPER_PATH)

    for marker in STAGE_SHARED_MANIFEST_LINES:
        require_marker(stage_text, marker, "stage-helper shared manifest marker")
    for marker in STAGE_ONLY_MARKERS:
        require_marker(stage_text, marker, "stage-helper marker")

    require_exact_count(stage_text, STAGE_SHARED_MANIFEST_LINES[0], 1, "stage-helper encoding")
    require_exact_count(stage_text, STAGE_SHARED_MANIFEST_LINES[1], 1, "stage-helper parts_glob")
    require_exact_count(stage_text, SHARED_SHARD_PATTERN, 1, "stage-helper shard pattern")
    require_exact_count(stage_text, "--parts-dir", 1, "stage-helper parts-dir flag")

    require_order(
        stage_text,
        'filename = require_manifest_string(manifest, "filename", manifest_path)',
        'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
        "stage manifest field order",
    )
    require_order(
        stage_text,
        'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
        'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
        "stage manifest field order",
    )
    require_order(
        stage_text,
        'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
        'size = require_manifest_int(manifest, "size", manifest_path)',
        "stage manifest field order",
    )
    require_order(
        stage_text,
        'size = require_manifest_int(manifest, "size", manifest_path)',
        'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
        "stage manifest field order",
    )
    require_order(
        stage_text,
        'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
        "stage manifest field order",
    )
    require_order(
        stage_text,
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
        'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
        "stage manifest field order",
    )

    return len(STAGE_SHARED_MANIFEST_LINES) + len(STAGE_ONLY_MARKERS) + 2


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)

    (root / SPLIT_HELPER_PATH).write_text(
        "\n".join(
            (
                'DEFAULT_CHUNK_BYTES = 786_432',
                "def write_manifest(output_dir):",
                "    return {",
                '        "encoding": "base64",',
                '        "chunk_bytes": chunk_bytes,',
                '        "part_count": part_count,',
                '        "parts_glob": "part-*.b64",',
                "    }",
                '    (output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
                "    manifest_path = write_manifest(output_dir)",
                '    print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )

    (root / STAGE_HELPER_PATH).write_text(
        "\n".join(
            (
                "import base64",
                "def reconstruct_archive_from_parts(parts_dir, destination):",
                '    manifest = load_shard_manifest(parts_dir)',
                '    filename = require_manifest_string(manifest, "filename", manifest_path)',
                '    encoding = require_manifest_string(manifest, "encoding", manifest_path)',
                '    sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
                '    size = require_manifest_int(manifest, "size", manifest_path)',
                '    part_count = require_manifest_int(manifest, "part_count", manifest_path)',
                '    require_manifest_int(manifest, "chunk_bytes", manifest_path)',
                '    parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
                '    if encoding != "base64":',
                '        raise ValueError("bad encoding")',
                '    if parts_glob != "part-*.b64":',
                '        raise ValueError("bad glob")',
                '    shard_path = parts_dir / f"part-{index:03d}.b64"',
                '    base64.b64decode(encoded, validate=True)',
                '    print("STAGE_PINNED_ZIG_ARCHIVE=pass")',
                '    print("STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=parts_dir")',
                '    parser.add_argument("--parts-dir")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_stage_interop_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        assert check_split_helper(root) == len(SPLIT_SHARED_MANIFEST_LINES) + len(SPLIT_ONLY_MARKERS) + 1
        assert check_stage_helper(root) == len(STAGE_SHARED_MANIFEST_LINES) + len(STAGE_ONLY_MARKERS) + 2
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_stage_interop_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                check_split_helper(root)
                check_stage_helper(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "split-helper shared manifest marker",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'if parts_glob != "part-*.b64":',
                'if parts_glob != "part-*.txt":',
                1,
            ),
            encoding="utf-8",
        ),
        'stage-helper shared manifest marker: if parts_glob != "part-*.b64":',
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'part_count = require_manifest_int(manifest, "part_count", manifest_path)\n'
                '    require_manifest_int(manifest, "chunk_bytes", manifest_path)\n',
                'require_manifest_int(manifest, "chunk_bytes", manifest_path)\n'
                '    part_count = require_manifest_int(manifest, "part_count", manifest_path)\n',
                1,
            ),
            encoding="utf-8",
        ),
        "stage manifest field order",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                '    (output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
                '    (output_dir / f"piece-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
                1,
            ),
            encoding="utf-8",
        ),
        'split-helper marker: (output_dir / f"part-{index:03d}.b64").write_text(',
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace("--parts-dir", "--archive-dir", 1),
            encoding="utf-8",
        ),
        "stage-helper marker: --parts-dir",
    )

    print("LANE05_SPLIT_STAGE_INTEROP_SELF_TEST=pass")
    print(f"LANE05_SPLIT_STAGE_INTEROP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper and staged-archive helper still agree on shard contract details."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        split_marker_count = check_split_helper(root)
        stage_marker_count = check_stage_helper(root)
    except ValueError as exc:
        print("LANE05_SPLIT_STAGE_INTEROP=fail")
        print(f"LANE05_SPLIT_STAGE_INTEROP_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_STAGE_INTEROP_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_STAGE_INTEROP=pass")
    print(f"LANE05_SPLIT_STAGE_INTEROP_ROOT={root}")
    print(f"LANE05_SPLIT_STAGE_INTEROP_SPLIT_MARKER_COUNT={split_marker_count}")
    print(f"LANE05_SPLIT_STAGE_INTEROP_STAGE_MARKER_COUNT={stage_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
