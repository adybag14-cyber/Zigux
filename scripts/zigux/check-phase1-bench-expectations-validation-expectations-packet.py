#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SELF_CHECKER_REL = Path(
    "scripts/zigux/check-phase1-bench-expectations-validation-expectations-packet.py"
)
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    SELF_CHECKER_REL,
    BENCH_CHECKER_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = (
    "kind, payload = load_runtime_expectations(EXPECTATIONS)",
    'if kind == "missing_expectations_file":',
    'if kind == "expectations_json_error":',
    'if kind != "pass":',
    'print("PHASE1_BENCH_CHECK=fail")',
    'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
    'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
    "print(payload)",
    "expectations = payload",
)

WORKFLOW_MARKERS = (
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
)


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [str(relative_path) for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_missing_markers(root: Path) -> list[str]:
    text = read_text(root, BENCH_CHECKER_REL)
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def collect_missing_workflow_markers(root: Path) -> list[str]:
    text = read_text(root, WORKFLOW_REL)
    return [marker for marker in WORKFLOW_MARKERS if marker not in text]


def validate_marker_order(root: Path) -> tuple[str, object]:
    text = read_text(root, BENCH_CHECKER_REL)
    positions = {marker: text.find(marker) for marker in REQUIRED_MARKERS}
    missing = [marker for marker, position in positions.items() if position < 0]
    if missing:
        return ("missing_markers", missing)
    ordered_positions = [positions[marker] for marker in REQUIRED_MARKERS]
    if ordered_positions != sorted(ordered_positions):
        return ("marker_order", list(REQUIRED_MARKERS))
    return ("pass", None)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path, include_expectations_marker: bool = True) -> None:
    write_text(root / SELF_CHECKER_REL, "#!/usr/bin/env python3\nprint('fixture')\n")
    lines = [
        "#!/usr/bin/env python3",
        "kind, payload = load_runtime_expectations(EXPECTATIONS)",
        'if kind == "missing_expectations_file":',
        "    return 1",
        'if kind == "expectations_json_error":',
        "    return 1",
        'if kind != "pass":',
        '    print("PHASE1_BENCH_CHECK=fail")',
        '    print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
    ]
    if include_expectations_marker:
        lines.append('    print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")')
    lines.extend(
        [
            "    print(payload)",
            "    return 1",
            "",
            "expectations = payload",
            "",
        ]
    )
    write_text(root / BENCH_CHECKER_REL, "\n".join(lines))
    workflow_lines = [
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ]
    write_text(root / WORKFLOW_REL, "\n".join(workflow_lines) + "\n")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase1_bench_expectations_validation_expectations_"
    ) as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        assert collect_missing_workflow_markers(root) == []
        assert validate_marker_order(root) == ("pass", None)
        case_count += 1

        write_sample_root(root, include_expectations_marker=False)
        expected_missing = ['print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")']
        assert collect_missing_markers(root) == expected_missing
        assert validate_marker_order(root) == ("missing_markers", expected_missing)
        case_count += 1

        write_sample_root(root)
        bench_checker = root / BENCH_CHECKER_REL
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                '    print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")\n'
                "    print(payload)\n",
                "    print(payload)\n"
                '    print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")\n',
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == []
        assert validate_marker_order(root) == ("marker_order", list(REQUIRED_MARKERS))
        case_count += 1

        write_sample_root(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text("jobs:\n  bootstrap:\n    steps:\n", encoding="utf-8")
        assert collect_missing_workflow_markers(root) == list(WORKFLOW_MARKERS)
        case_count += 1

        write_sample_root(root)
        (root / BENCH_CHECKER_REL).unlink()
        assert collect_missing_files(root) == [str(BENCH_CHECKER_REL)]
        case_count += 1

        write_sample_root(root)
        (root / WORKFLOW_REL).unlink()
        assert collect_missing_files(root) == [str(WORKFLOW_REL)]
        case_count += 1

    print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_SELF_TEST=pass")
    print(
        "PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_SELF_TEST_CASE_COUNT="
        f"{case_count}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the bounded Lane 16 expectations-validation expectations-path packet."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--write-sample-root", help="Write a minimal sample root and exit.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(Path(args.write_sample_root))
        print(
            "PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_SAMPLE_ROOT="
            f"{Path(args.write_sample_root)}"
        )
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET=fail")
        print("MISSING_PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET=fail")
        print("MISSING_PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_MARKERS_END")
        return 1

    missing_workflow_markers = collect_missing_workflow_markers(root)
    if missing_workflow_markers:
        print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET=fail")
        print("MISSING_PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_WORKFLOW_MARKERS_START")
        for item in missing_workflow_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_WORKFLOW_MARKERS_END")
        return 1

    order_kind, order_payload = validate_marker_order(root)
    if order_kind != "pass":
        print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET=fail")
        print(f"PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_REASON={order_kind}")
        if isinstance(order_payload, list):
            for item in order_payload:
                print(item)
        else:
            print(order_payload)
        return 1

    print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET=pass")
    print(
        "PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_REQUIRED_FILE_COUNT="
        f"{len(REQUIRED_FILES)}"
    )
    print(
        "PHASE1_BENCH_EXPECTATIONS_VALIDATION_EXPECTATIONS_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
