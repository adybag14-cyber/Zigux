#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
README_PATH = ROOT / "scripts/zigux/README.md"
MAKEFILE_PATH = ROOT / "zigux/Makefile"
WORKFLOW_PATH = ROOT / ".github/workflows/zigux-bootstrap.yml"
BUILD_PATH = ROOT / "zigux/tests/phase11_build.zig"
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase11_build_inventory.json"

README_MARKERS = [
    "Phase 11 flow",
    "`make -C zigux phase11-validate` is the validator-first entrypoint for the active simple-driver tranche.",
    "`check-phase11-build-inventory.py`, `check-phase11-layout-assert-surface.py`, `check-phase11-hvc-validation-flow.py`, and `check-phase11-hvc-cleanup-alignment.py` keep the build snapshot, the Phase 11 layout-assert survey surface, the shared-versus-dedicated hvc replay contract, and the current hvc cleanup packet explicit before the broader Phase 11 validator runs.",
    "`validate-phase11.py` keeps those pre-replay gates plus `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` aligned with `zigux/tests/phase11_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the dedicated hvc_console survey note and validation matrix.",
    "`make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.",
]
MAKEFILE_MARKERS = [
    "phase11-validate:",
    "scripts/zigux/check-phase11-build-inventory.py --self-test",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
    "scripts/zigux/check-phase11-layout-assert-surface.py",
    "scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
    "scripts/zigux/check-phase11-hvc-validation-flow.py",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
    "scripts/zigux/validate-phase11.py --self-test",
    "scripts/zigux/validate-phase11.py",
    "phase11-hvc-survey:",
    "$(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
]
WORKFLOW_MARKERS = [
    "Self-test Phase 11 simple-driver validator",
    "Self-test Phase 11 build inventory checker",
    "Self-test Phase 11 hvc validation flow checker",
    "Self-test Phase 11 hvc cleanup alignment checker",
    "Self-test Phase 11 layout assert surface checker",
    "Validate Phase 11 simple-driver bundle",
    "Run Phase 11 watchdog and console tests",
    "Run dedicated Phase 11 hvc survey replay",
]
BUILD_MARKERS = [
    '    .name = "phase11-dw-wdt-suspend-resume-tests",',
    '    .name = "phase11-dw-wdt-remove-idle-split-tests",',
    '    .name = "phase11-hvc-console-modem-control-split-tests",',
    '    .name = "phase11-hvc-console-poll-retry-split-tests",',
    "    test_step.dependOn(&run_phase11_dw_wdt_suspend_resume_tests.step);",
    "    test_step.dependOn(&run_phase11_dw_wdt_remove_idle_split_tests.step);",
    "    test_step.dependOn(&run_phase11_hvc_console_modem_control_split_tests.step);",
    "    test_step.dependOn(&run_phase11_hvc_console_poll_retry_split_tests.step);",
]
FORBIDDEN_BUILD_MARKERS = [
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
EXPECTED_SHARED_SPLIT_REPLAYS = [
    {
        "test": "phase11-dw-wdt-remove-idle-split-tests",
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
    },
    {
        "test": "phase11-hvc-console-modem-control-split-tests",
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    },
    {
        "test": "phase11-hvc-console-poll-retry-split-tests",
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    },
]
EXPECTED_SHARED_REPLAY_MARKERS = [
    {
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        "marker": "    try std.testing.expect(summary.resume_preserves_timeout_programming);",
    },
    {
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        "marker": "    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        "marker": "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        "marker": "    try std.testing.expect(dispatch.invokes_sysrq_handler);",
    },
]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_fixture(path: Path) -> dict[str, object]:
    return json.loads(text(path))


def validate_contract(root: Path) -> int:
    missing: list[str] = []
    for label, path, markers in [
        ("readme", root / README_PATH, README_MARKERS),
        ("makefile", root / MAKEFILE_PATH, MAKEFILE_MARKERS),
        ("workflow", root / WORKFLOW_PATH, WORKFLOW_MARKERS),
        ("build", root / BUILD_PATH, BUILD_MARKERS),
    ]:
        source = text(path)
        for marker in markers:
            if marker not in source:
                missing.append(f"{label}:{marker}")

    build_text = text(root / BUILD_PATH)
    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in build_text:
            missing.append(f"build:forbidden:{marker}")

    fixture = load_fixture(root / FIXTURE_PATH)
    if fixture.get("shared_split_replays") != EXPECTED_SHARED_SPLIT_REPLAYS:
        missing.append("fixture:shared_split_replays")
    if fixture.get("shared_replay_markers") != EXPECTED_SHARED_REPLAY_MARKERS:
        missing.append("fixture:shared_replay_markers")

    if missing:
        print("PHASE11_SHARED_REPLAY_CONTRACT=fail")
        print("PHASE11_SHARED_REPLAY_CONTRACT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_SHARED_REPLAY_CONTRACT_MISSING_END")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    print(f"PHASE11_SHARED_REPLAY_MARKER_COUNT={len(EXPECTED_SHARED_REPLAY_MARKERS)}")
    print(f"PHASE11_SHARED_SPLIT_REPLAY_COUNT={len(EXPECTED_SHARED_SPLIT_REPLAYS)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-shared-replay-contract.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, result: subprocess.CompletedProcess[str], marker: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-shared-replay-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-shared-replay-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture_tree(root: Path) -> None:
    write_text(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    build_body = "\n".join(
        BUILD_MARKERS
        + [
            '    const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console survey replay");'
        ]
    )
    write_text(root / "zigux/tests/phase11_build.zig", build_body + "\n")
    write_text(
        root / "zigux/tests/fixtures/phase11_build_inventory.json",
        json.dumps(
            {
                "shared_split_replays": EXPECTED_SHARED_SPLIT_REPLAYS,
                "shared_replay_markers": EXPECTED_SHARED_REPLAY_MARKERS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "scripts/zigux/check-phase11-shared-replay-contract.py",
        Path(__file__).read_text(encoding="utf-8"),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_shared_replay_contract_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-shared-replay-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        readme_path = tmp_root / "scripts/zigux/README.md"
        readme_backup = text(readme_path)
        write_text(readme_path, readme_backup.replace("Phase 11 flow\n", "", 1))
        expect_missing("missing_readme_section", run_checker(tmp_root), "readme:Phase 11 flow")
        write_text(readme_path, readme_backup)

        build_path = tmp_root / "zigux/tests/phase11_build.zig"
        build_backup = text(build_path)
        write_text(
            build_path,
            build_backup + "\n" + FORBIDDEN_BUILD_MARKERS[0] + "\n",
        )
        expect_missing(
            "forbidden_hvc_survey_dep",
            run_checker(tmp_root),
            f"build:forbidden:{FORBIDDEN_BUILD_MARKERS[0]}",
        )
        write_text(build_path, build_backup)

        fixture_path = tmp_root / "zigux/tests/fixtures/phase11_build_inventory.json"
        fixture_backup = text(fixture_path)
        fixture = json.loads(fixture_backup)
        fixture["shared_replay_markers"] = fixture["shared_replay_markers"][:-1]
        write_text(fixture_path, json.dumps(fixture, indent=2) + "\n")
        expect_missing(
            "shared_replay_fixture_drift",
            run_checker(tmp_root),
            "fixture:shared_replay_markers",
        )
        write_text(fixture_path, fixture_backup)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_backup = text(makefile_path)
        write_text(
            makefile_path,
            makefile_backup.replace(
                "scripts/zigux/check-phase11-build-inventory.py --self-test\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_makefile_self_test",
            run_checker(tmp_root),
            "makefile:scripts/zigux/check-phase11-build-inventory.py --self-test",
        )

    print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
    print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT=4")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_contract(ROOT))
