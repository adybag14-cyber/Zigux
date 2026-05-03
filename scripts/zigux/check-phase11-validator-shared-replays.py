#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/zigux/validate-phase11.py"

REQUIRED_VALIDATOR_MARKERS = [
    "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "phase11_dw_wdt_suspend_resume_tests:    try std.testing.expect(summary.resume_preserves_timeout_programming);",
    "phase11_hvc_console_modem_control_split_tests:    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
]


def validate_validator_markers() -> int:
    if not VALIDATOR_PATH.exists():
        print("PHASE11_VALIDATOR_SHARED_REPLAYS=fail")
        print(f"MISSING_VALIDATOR_FILE={VALIDATOR_PATH.relative_to(ROOT).as_posix()}")
        return 1

    validator_text = VALIDATOR_PATH.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_VALIDATOR_MARKERS if marker not in validator_text]
    if missing:
        print("PHASE11_VALIDATOR_SHARED_REPLAYS=fail")
        print("PHASE11_VALIDATOR_SHARED_REPLAYS_MISSING_START")
        for marker in missing:
            print(marker)
        print("PHASE11_VALIDATOR_SHARED_REPLAYS_MISSING_END")
        return 1

    print("PHASE11_VALIDATOR_SHARED_REPLAYS=pass")
    print(f"PHASE11_VALIDATOR_SHARED_REPLAYS_MARKER_COUNT={len(REQUIRED_VALIDATOR_MARKERS)}")
    return 0


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-validator-shared-replays.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, result: subprocess.CompletedProcess[str], expected_marker: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-validator-shared-replays-self-test:{label}:unexpected_pass")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-validator-shared-replays-self-test:{label}:expected:{expected_marker}:actual:{actual}"
        )


def write_self_test_fixture(root: Path) -> None:
    target = root / "scripts/zigux"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(__file__, target / "check-phase11-validator-shared-replays.py")
    (target / "validate-phase11.py").write_text(
        "#!/usr/bin/env python3\n"
        "FILES = [\n"
        '    "zigux/tests/phase11_dw_wdt_suspend_resume.zig",\n'
        '    "zigux/tests/phase11_hvc_console_modem_control_split.zig",\n'
        "]\n"
        "missing = [\n"
        '    "phase11_dw_wdt_suspend_resume_tests:    try std.testing.expect(summary.resume_preserves_timeout_programming);",\n'
        '    "phase11_hvc_console_modem_control_split_tests:    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",\n'
        "]\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_validator_shared_replays_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_self_test_fixture(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-validator-shared-replays-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        validator_path = tmp_root / "scripts/zigux/validate-phase11.py"
        original_text = validator_path.read_text(encoding="utf-8")

        validator_path.write_text(
            original_text.replace('    "zigux/tests/phase11_dw_wdt_suspend_resume.zig",\n', "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "missing_dw_suspend_resume_file_marker",
            run_checker(tmp_root),
            "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        )
        validator_path.write_text(original_text, encoding="utf-8")

        validator_path.write_text(
            original_text.replace(
                '    "phase11_hvc_console_modem_control_split_tests:    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "missing_hvc_modem_marker",
            run_checker(tmp_root),
            "phase11_hvc_console_modem_control_split_tests:    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
        )
        validator_path.write_text(original_text, encoding="utf-8")

    print("PHASE11_VALIDATOR_SHARED_REPLAYS_SELF_TEST=pass")
    print("PHASE11_VALIDATOR_SHARED_REPLAYS_SELF_TEST_CASE_COUNT=2")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_validator_markers())
