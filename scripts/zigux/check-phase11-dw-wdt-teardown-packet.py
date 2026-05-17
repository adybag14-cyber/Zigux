#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "matrix": Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md"),
    "teardown_note": Path("Documentation/zigux/phase11-dw-wdt-teardown-note.md"),
    "verify_file": Path("drivers/watchdog/dw_wdt_verify.zig"),
}

MATRIX_MARKERS = [
    "remove and teardown failure-mode split",
    "the reset-controlled remove, idle-remove, and IRQ-mode teardown-outcome replays in `drivers/watchdog/dw_wdt_verify.zig`",
    "keep this remove-and-teardown boundary stable while the lane stays host-free and registration-first",
]

TEARDOWN_NOTE_MARKERS = [
    "preserving continued-heartbeat semantics when the hardware is non-stoppable",
    "separating the idle no-op, reset-controlled stop, and continued-heartbeat outcomes",
    "whether hardware remains running after remove when reset control is unavailable",
]

VERIFY_FILE_MARKERS = [
    'test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit" {',
    'test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct" {',
    'test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit" {',
]

SELF_TEST_CASES = (
    ("matrix_marker_missing", "matrix", MATRIX_MARKERS[0]),
    ("teardown_note_marker_missing", "teardown_note", TEARDOWN_NOTE_MARKERS[1]),
    ("verify_marker_missing", "verify_file", VERIFY_FILE_MARKERS[2]),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_repo(root: Path) -> list[str]:
    missing: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        path = root / rel_path
        if not path.is_file():
            missing.append(f"missing_file:{rel_path.as_posix()}")
            continue
        text = read_text(path)
        markers = {
            "matrix": MATRIX_MARKERS,
            "teardown_note": TEARDOWN_NOTE_MARKERS,
            "verify_file": VERIFY_FILE_MARKERS,
        }[label]
        for marker in markers:
            if marker not in text:
                missing.append(f"missing_marker:{label}:{marker}")
    return missing


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    (root / REQUIRED_FILES["matrix"]).write_text(
        "\n".join(MATRIX_MARKERS),
        encoding="utf-8",
    )
    (root / REQUIRED_FILES["teardown_note"]).write_text(
        "\n".join(TEARDOWN_NOTE_MARKERS),
        encoding="utf-8",
    )
    (root / REQUIRED_FILES["verify_file"]).write_text(
        "\n".join(VERIFY_FILE_MARKERS),
        encoding="utf-8",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-teardown-") as tmpdir:
        root = Path(tmpdir)
        seed_fixture(root)

        baseline = check_repo(root)
        if baseline:
            raise SystemExit(
                "baseline self-test fixture failed: " + ", ".join(baseline)
            )

        case_count = 1
        for case_name, label, marker in SELF_TEST_CASES:
            case_root = root / case_name
            shutil.copytree(root, case_root)
            target = case_root / REQUIRED_FILES[label]
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            failures = check_repo(case_root)
            expected = f"missing_marker:{label}:{marker}"
            if expected not in failures:
                raise SystemExit(
                    f"self-test case {case_name} did not fail as expected: {failures}"
                )
            case_count += 1

        print("PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-close the Phase 11 DesignWare watchdog teardown packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in checker self-tests instead of inspecting a repo",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    failures = check_repo(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_DW_WDT_TEARDOWN_PACKET=pass")
    print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE11_DW_WDT_TEARDOWN_PACKET_MARKER_COUNT="
        f"{len(MATRIX_MARKERS) + len(TEARDOWN_NOTE_MARKERS) + len(VERIFY_FILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
