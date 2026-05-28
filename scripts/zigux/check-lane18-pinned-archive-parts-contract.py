#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "scripts/zigux/zig-toolchain-policy.json").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SPLIT_HELPER_PATH = "scripts/zigux/split-pinned-zig-archive.py"
STAGE_HELPER_PATH = "scripts/zigux/stage-pinned-zig-archive.py"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
POLICY_PATH = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_FILES = [
    SPLIT_HELPER_PATH,
    STAGE_HELPER_PATH,
    WORKFLOW_PATH,
    POLICY_PATH,
]

REQUIRED_MARKERS = {
    SPLIT_HELPER_PATH: [
        "DEFAULT_CHUNK_BYTES = 786_432",
        '"encoding": "base64"',
        '"parts_glob": "part-*.b64"',
        'f"part-{index:03d}.b64"',
        "base64.b64encode(chunk).decode(\"ascii\")",
        "base64.b64decode(encoded, validate=True)",
        "SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT",
    ],
    STAGE_HELPER_PATH: [
        "def reconstruct_archive_from_parts(",
        'if encoding != "base64":',
        'if parts_glob != "part-*.b64":',
        'shard_path = parts_dir / f"part-{index:03d}.b64"',
        "base64.b64decode(encoded, validate=True)",
        'parser.add_argument(\n        "--parts-dir"',
        "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE",
    ],
    WORKFLOW_PATH: [
        'repo_archive_parts_dir="${repo_archive_path}.parts"',
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        '--parts-dir "$repo_archive_parts_dir"',
        "third_party/**",
    ],
    POLICY_PATH: [
        '"channel": "0.17.0-dev.87+9b177a7d2"',
        '"x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"',
        '"archive_target_scope": [',
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(rel_path: str) -> str:
    markers = REQUIRED_MARKERS[rel_path]
    return f"# fixture for {rel_path}\n" + "\n".join(markers) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "__REMOVED_LANE18_ARCHIVE_PARTS_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate fixture marker: {marker}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="lane18-archive-parts-contract-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        case_count = len(REQUIRED_FILES) + len(marker_cases)
        print("LANE18_PINNED_ARCHIVE_PARTS_CONTRACT_SELF_TEST=pass")
        print(f"LANE18_PINNED_ARCHIVE_PARTS_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def write_sample_root(root: Path) -> None:
    write_fixture_tree(root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the pinned Zig archive parts contract stays aligned "
            "across the split helper, staging helper, bootstrap workflow, and "
            "toolchain policy."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture-backed checker coverage.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing fixture root for action-path validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"LANE18_PINNED_ARCHIVE_PARTS_CONTRACT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"LANE18_PINNED_ARCHIVE_PARTS_CONTRACT=fail:{failure}", file=sys.stderr)
        return 1

    print("LANE18_PINNED_ARCHIVE_PARTS_CONTRACT=pass")
    print(f"LANE18_PINNED_ARCHIVE_PARTS_CONTRACT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "LANE18_PINNED_ARCHIVE_PARTS_CONTRACT_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
