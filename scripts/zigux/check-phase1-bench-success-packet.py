#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = [
    str(CHECKER_REL),
    str(WORKFLOW_REL),
]

CHECKER_MARKERS = [
    'print("PHASE1_BENCH_CHECK=pass")',
    'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
    'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
    'print(f"PHASE1_BENCH_ZIG={zig}")',
]

WORKFLOW_MARKERS = [
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
]

UNEXPECTED_LEGACY_MARKERS = [
    "PHASE1_BENCH_EXPECTATION_COUNT=",
]


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []

    checker = read_text(root, str(CHECKER_REL))
    workflow = read_text(root, str(WORKFLOW_REL))

    for marker in CHECKER_MARKERS:
        if marker not in checker:
            missing.append(f"{CHECKER_REL}:missing={marker}")

    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            missing.append(f"{WORKFLOW_REL}:missing={marker}")

    for marker in UNEXPECTED_LEGACY_MARKERS:
        if marker in checker:
            missing.append(f"{CHECKER_REL}:unexpected={marker}")

    return missing


def write_sample_root(root: Path) -> None:
    checker_path = root / CHECKER_REL
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    checker_path.write_text(
        "\n".join(
            [
                'print("PHASE1_BENCH_CHECK=pass")',
                'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
                'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
                'print(f"PHASE1_BENCH_ZIG={zig}")',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    workflow_path = root / WORKFLOW_REL
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_success_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        checker_path = root / CHECKER_REL
        checker_path.write_text(
            checker_path.read_text(encoding="utf-8").replace(
                'print(f"PHASE1_BENCH_ZIG={zig}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == [
            f"{CHECKER_REL}:missing=print(f\"PHASE1_BENCH_ZIG={{zig}}\")"
        ]
        case_count += 1
        write_sample_root(root)

        checker_path.write_text(
            checker_path.read_text(encoding="utf-8")
            + 'print("PHASE1_BENCH_EXPECTATION_COUNT=12")\n',
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == [
            f"{CHECKER_REL}:unexpected=PHASE1_BENCH_EXPECTATION_COUNT="
        ]
        case_count += 1
        write_sample_root(root)

        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text("jobs:\n  bootstrap:\n    steps:\n", encoding="utf-8")
        assert collect_missing_markers(root) == [
            f"{WORKFLOW_REL}:missing=run: python3 scripts/zigux/check-phase1-bench.py --self-test"
        ]
        case_count += 1
        write_sample_root(root)

        checker_path.unlink()
        assert collect_missing_files(root) == [str(CHECKER_REL)]
        case_count += 1
        write_sample_root(root)

        workflow_path.unlink()
        assert collect_missing_files(root) == [str(WORKFLOW_REL)]
        case_count += 1

    print("PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 bench success packet and its workflow self-test hook."
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a minimal passing sample tree to the provided directory.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        write_sample_root(root)
        print(f"PHASE1_BENCH_SUCCESS_PACKET_SAMPLE_ROOT={root}")
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_SUCCESS_PACKET=fail")
        print("MISSING_PHASE1_BENCH_SUCCESS_PACKET_FILES_START")
        for rel in missing_files:
            print(rel)
        print("MISSING_PHASE1_BENCH_SUCCESS_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BENCH_SUCCESS_PACKET=fail")
        print("MISSING_PHASE1_BENCH_SUCCESS_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_SUCCESS_PACKET_MARKERS_END")
        return 1

    print("PHASE1_BENCH_SUCCESS_PACKET=pass")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_SUCCESS_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(CHECKER_MARKERS) + len(WORKFLOW_MARKERS) + len(UNEXPECTED_LEGACY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
