#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SELF_CHECKER_REL = Path("scripts/zigux/check-phase1-bench-zig-not-found-packet.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    BENCH_CHECKER_REL,
    SELF_CHECKER_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = (
    'parser.add_argument("--zig", help="Path to Zig executable")',
    "def find_zig(explicit: str | None) -> str:",
    'zig = shutil.which("zig")',
    'raise SystemExit("zig not found; pass --zig or add zig to PATH")',
    'print("PHASE1_BENCH_CHECK=fail")',
    'print("PHASE1_BENCH_CHECK_REASON=zig_not_found")',
)

WORKFLOW_SECTIONS = (
    (
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "      - name: Self-test current Phase 1 bench zig-not-found packet checker",
        "        run: python3 scripts/zigux/check-phase1-bench-zig-not-found-packet.py --self-test",
    ),
    (
        "      - name: Check current Phase 1 bench zig-not-found packet",
        "        run: python3 scripts/zigux/check-phase1-bench-zig-not-found-packet.py",
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [str(rel) for rel in REQUIRED_FILES if not (root / rel).is_file()]


def collect_missing_markers(root: Path) -> list[str]:
    bench_text = read_text(root / BENCH_CHECKER_REL)
    workflow_text = read_text(root / WORKFLOW_REL)
    missing = [marker for marker in REQUIRED_MARKERS if marker not in bench_text]
    for workflow_section in WORKFLOW_SECTIONS:
        workflow_block = "\n".join(workflow_section)
        if workflow_block not in workflow_text:
            missing.extend(workflow_section)
    return missing


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(
        root / BENCH_CHECKER_REL,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "",
                "import argparse",
                "import shutil",
                "",
                'parser = argparse.ArgumentParser(description="fixture")',
                'parser.add_argument("--zig", help="Path to Zig executable")',
                "",
                "def find_zig(explicit: str | None) -> str:",
                "    if explicit:",
                "        return explicit",
                '    zig = shutil.which("zig")',
                "    if zig:",
                "        return zig",
                '    raise SystemExit("zig not found; pass --zig or add zig to PATH")',
                "",
                "def emit_zig_not_found_packet() -> None:",
                '    print("PHASE1_BENCH_CHECK=fail")',
                '    print("PHASE1_BENCH_CHECK_REASON=zig_not_found")',
                "",
            )
        )
        + "\n",
    )
    write_text(
        root / SELF_CHECKER_REL,
        "#!/usr/bin/env python3\nprint('fixture')\n",
    )
    write_text(
        root / WORKFLOW_REL,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "      - name: Self-test current Phase 1 bench zig-not-found packet checker",
                "        run: python3 scripts/zigux/check-phase1-bench-zig-not-found-packet.py --self-test",
                "      - name: Check current Phase 1 bench zig-not-found packet",
                "        run: python3 scripts/zigux/check-phase1-bench-zig-not-found-packet.py",
                "",
            )
        ),
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_zig_not_found_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        bench_checker = root / BENCH_CHECKER_REL
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                'print("PHASE1_BENCH_CHECK_REASON=zig_not_found")\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == ['print("PHASE1_BENCH_CHECK_REASON=zig_not_found")']
        case_count += 1

        write_sample_root(root)
        workflow = root / WORKFLOW_REL
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "      - name: Check current Phase 1 bench zig-not-found packet\n"
                "        run: python3 scripts/zigux/check-phase1-bench-zig-not-found-packet.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == [
            "      - name: Check current Phase 1 bench zig-not-found packet",
            "        run: python3 scripts/zigux/check-phase1-bench-zig-not-found-packet.py",
        ]
        case_count += 1

        write_sample_root(root)
        (root / SELF_CHECKER_REL).unlink()
        assert collect_missing_files(root) == [str(SELF_CHECKER_REL)]
        case_count += 1

        write_sample_root(root)
        (root / WORKFLOW_REL).unlink()
        assert collect_missing_files(root) == [str(WORKFLOW_REL)]
        case_count += 1

    print("PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 16 Zig-not-found bench packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--write-sample-root", help="Write a minimal passing sample root and exit.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(Path(args.write_sample_root))
        print(f"PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_SAMPLE_ROOT={Path(args.write_sample_root)}")
        return 0

    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_ZIG_NOT_FOUND_PACKET=fail")
        print("MISSING_PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BENCH_ZIG_NOT_FOUND_PACKET=fail")
        print("MISSING_PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_MARKERS_END")
        return 1

    print("PHASE1_BENCH_ZIG_NOT_FOUND_PACKET=pass")
    print(f"PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_ZIG_NOT_FOUND_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS) + sum(len(section) for section in WORKFLOW_SECTIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
