#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-shared-replay-contract.py"

FILES = {
    "note": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
}

NOTE_EXISTENCE_FILES = [
    "Documentation/zigux/phase11-hvc-console-slice.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_survey.zig",
]

MARKERS = {
    "note": [
        "# Phase 11 Shared Replay Contract",
        "* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
        "* `zigux/tests/phase11_build.zig`",
        "* `make -C zigux phase11`",
        "* no shared `validate-phase11.py`",
        "* no shared `make -C zigux phase11-validate` target on `master`",
        "The dedicated archival HVC evidence still stays explicit beside that shared route:",
        "* `Documentation/zigux/phase11-hvc-console-slice.md`",
        "* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "* `Documentation/zigux/phase11-hvc-console-survey.md`",
        "* `Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "* `zigux/tests/phase11_hvc_cleanup.zig`",
        "* `zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "* `drivers/tty/hvc/hvc_console_verify.zig`",
        "* `drivers/tty/hvc/hvc_console_sysrq.zig`",
        "* `scripts/zigux/check-phase11-hvc-survey-packet.py`",
        "* `zigux/tests/phase11_hvc_console_manifest.json`",
        "* `zigux/tests/phase11_hvc_console_survey.zig`",
        "* `make -C zigux phase11-hvc-survey`",
        "Treat `Documentation/zigux/phase11-hvc-console-teardown-note.md` together with `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey` as the landed dedicated HVC archival evidence on current `master`, while direct `zigux/tests/phase11_hvc_console.zig` stays recorded as the remaining repo-reality gap rather than shared proof.",
        "The dedicated DesignWare watchdog evidence also stays explicit beside that shared route:",
        "* `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "* `Documentation/zigux/phase11-dw-wdt-survey.md`",
        "* `Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
        "* `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "* `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`",
        "* `python3 scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "* `zigux/tests/phase11_dw_wdt_manifest.json`",
        "* `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "* `zigux/tests/phase11_dw_wdt_survey.zig`",
        "* `drivers/watchdog/dw_wdt_verify.zig`",
        "* `scripts/zigux/check-phase11-header-boundary-packet.py`",
        "* `zigux/tests/phase11_uapi_header_parity_survey.zig`",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "* `zigux/tests/phase11_build.zig`",
        "* `make -C zigux phase11`",
        "* there is no shared `validate-phase11.py`",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
        "* DesignWare watchdog continuity stays with `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_survey.zig`",
        "* HVC archival continuity stays with `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, and `make -C zigux phase11-hvc-survey`, while direct `zigux/tests/phase11_hvc_console.zig` stays framed as the remaining repo-reality gap rather than shared closure evidence",
        "* shared header boundary continuity stays with `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_survey.zig`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "- DesignWare lane `P11-L05` owns `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "- HVC delivery-gate lane `P11-L16` owns `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey`",
        "The shared packet surfaces still living together on current `master` are `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, and `make -C zigux phase11`.",
        "Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the shared notes, the shared contract checker, the shared `phase11_build.zig` route, and `make -C zigux phase11`, while `scripts/zigux/check-phase11-shared-summary-surfaces.py` remains the focused direct audit for the docs-root, scripts-root, tests-root, and checklist summaries when reminder wording moves.",
        "Keep the current validator posture explicit: there is a shared `zigux/tests/phase11_build.zig` route and a shared `make -C zigux phase11` wrapper on current `master`, but there is no shared `validate-phase11.py`, no shared `zigux/tests/fixtures/phase11_build_inventory.json`, and no shared `make -C zigux phase11-validate` target, so reminder-surface edits should stay aligned with the surviving build-backed packet instead of reviving the older inventory-driven validator story.",
        "Keep the DesignWare lane honest: on current `master` the landed DesignWare packet is the validation matrix, survey note, teardown note, registration-scaffold replay, verify helper, dedicated packet checker, and shared Phase 11 replay route rather than a docs-only planning placeholder.",
        "Keep the HVC delivery-gate lane honest: on current `master` the landed HVC archival packet is the teardown-note cleanup handoff through `zigux/tests/phase11_hvc_cleanup.zig`, the direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, the manifest-backed survey gate, modem-control split, poll-retry split, sysrq helper, validation matrix, and dedicated `phase11-hvc-survey` route rather than a missing or purely reminder-only packet.",
    ],
}

SELF_TEST_CASE_COUNT = 22


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        expect_markers(label, read_text(root, relative_path), MARKERS[label])
    for relative_path in NOTE_EXISTENCE_FILES:
        read_text(root, relative_path)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    for label, relative_path in FILES.items():
        write(root / relative_path, "\n".join(MARKERS[label]) + "\n")
    for relative_path in NOTE_EXISTENCE_FILES:
        write(root / relative_path, f"{relative_path}\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_contract_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        cases = [
            (FILES["note"], "* `zigux/tests/phase11_build.zig`"),
            (FILES["note"], "* no shared `make -C zigux phase11-validate` target on `master`"),
            (FILES["note"], "* `Documentation/zigux/phase11-hvc-console-slice.md`"),
            (FILES["note"], "* `Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (FILES["note"], "* `zigux/tests/phase11_hvc_cleanup.zig`"),
            (FILES["note"], "* `drivers/tty/hvc/hvc_console_verify.zig`"),
            (FILES["note"], "* `drivers/tty/hvc/hvc_console_sysrq.zig`"),
            (FILES["note"], "Treat `Documentation/zigux/phase11-hvc-console-teardown-note.md` together with `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey` as the landed dedicated HVC archival evidence on current `master`, while direct `zigux/tests/phase11_hvc_console.zig` stays recorded as the remaining repo-reality gap rather than shared proof."),
            (FILES["note"], "* `drivers/watchdog/dw_wdt_verify.zig`"),
            (FILES["closure_note"], "* `zigux/tests/phase11_build.zig`"),
            (FILES["closure_note"], "* DesignWare watchdog continuity stays with `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_survey.zig`"),
            (FILES["closure_note"], "* HVC archival continuity stays with `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, and `make -C zigux phase11-hvc-survey`, while direct `zigux/tests/phase11_hvc_console.zig` stays framed as the remaining repo-reality gap rather than shared closure evidence"),
            (FILES["lane_note"], "# Phase 11 Driver Lane Sequencing"),
            (FILES["lane_note"], "- HVC delivery-gate lane `P11-L16` owns `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey`"),
            (FILES["lane_note"], "The shared packet surfaces still living together on current `master` are `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, and `make -C zigux phase11`."),
            (FILES["lane_note"], "Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the shared notes, the shared contract checker, the shared `phase11_build.zig` route, and `make -C zigux phase11`, while `scripts/zigux/check-phase11-shared-summary-surfaces.py` remains the focused direct audit for the docs-root, scripts-root, tests-root, and checklist summaries when reminder wording moves."),
            (FILES["lane_note"], "Keep the DesignWare lane honest: on current `master` the landed DesignWare packet is the validation matrix, survey note, teardown note, registration-scaffold replay, verify helper, dedicated packet checker, and shared Phase 11 replay route rather than a docs-only planning placeholder."),
            (FILES["lane_note"], "Keep the HVC delivery-gate lane honest: on current `master` the landed HVC archival packet is the teardown-note cleanup handoff through `zigux/tests/phase11_hvc_cleanup.zig`, the direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, the manifest-backed survey gate, modem-control split, poll-retry split, sysrq helper, validation matrix, and dedicated `phase11-hvc-survey` route rather than a missing or purely reminder-only packet."),
            ("Documentation/zigux/phase11-hvc-console-teardown-note.md", "Documentation/zigux/phase11-hvc-console-teardown-note.md"),
            ("zigux/tests/phase11_hvc_cleanup.zig", "zigux/tests/phase11_hvc_cleanup.zig"),
            ("zigux/tests/phase11_hvc_console_modem_control_split.zig", "zigux/tests/phase11_hvc_console_modem_control_split.zig"),
            ("zigux/tests/phase11_hvc_console_survey.zig", "zigux/tests/phase11_hvc_console_survey.zig"),
            ("drivers/tty/hvc/hvc_console_verify.zig", "drivers/tty/hvc/hvc_console_verify.zig"),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            if relative_path in FILES.values():
                path.write_text(path.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
                expect_failure(case_root, marker)
            else:
                path.unlink()
                expect_failure(case_root, relative_path)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_SHARED_REPLAY_CONTRACT=fail: {exc}")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
