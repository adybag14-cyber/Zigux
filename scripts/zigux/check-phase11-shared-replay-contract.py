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
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-dw-wdt-teardown-note.md",
    "scripts/zigux/check-phase11-dw-wdt-packet.py",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "zigux/tests/phase11_dw_wdt_survey.zig",
    "scripts/zigux/check-phase11-shared-summary-surfaces.py",
    "Documentation/zigux/phase11-hvc-console-slice.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "scripts/zigux/check-phase11-header-boundary-packet.py",
    "zigux/tests/phase11_uapi_header_parity_manifest.json",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
]

MARKERS = {
    "note": [
        "# Phase 11 Shared Replay Contract",
        "* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
        "* `scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "* no shared `validate-phase11.py`",
        "* `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "* `Documentation/zigux/phase11-dw-wdt-survey.md`",
        "* `Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
        "* `drivers/watchdog/dw_wdt_verify.zig`",
        "* `zigux/tests/phase11_dw_wdt.zig`",
        "* `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "* `zigux/tests/phase11_hvc_console.zig`",
        "* `zigux/tests/phase11_hvc_cleanup.zig`",
        "* `drivers/tty/hvc/hvc_console_verify.zig`",
        "Treat `Documentation/zigux/phase11-hvc-console-teardown-note.md` together with `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "* DesignWare watchdog continuity now stays with `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and `zigux/tests/phase11_dw_wdt_survey.zig`",
        "* HVC archival continuity stays with `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "- DesignWare lane `P11-L10` currently owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and `zigux/tests/phase11_dw_wdt_survey.zig`",
        "- HVC archival packet lane `P11-L16` owns `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`",
        "7. Keep the DesignWare lane honest: on current `master` the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and `zigux/tests/phase11_dw_wdt_survey.zig`",
        "8. Keep the HVC split honest: on current `master` the landed HVC archival packet is the teardown note, validation matrix, survey note, direct `zigux/tests/phase11_hvc_console.zig` plus `zigux/tests/phase11_hvc_cleanup.zig` replays",
    ],
}

FORBIDDEN_MARKERS = {
    "note": [
        "the older manifest, survey, validation-matrix, and teardown reminder surfaces stay removed rather than being silently reintroduced as shared evidence",
        "stay recorded as the remaining repo-reality gaps rather than shared proof",
    ],
    "closure_note": [
        "the older manifest, survey, validation-matrix, and teardown reminder surfaces remain removed on current `master`",
        "stay framed as the remaining repo-reality gaps rather than shared closure evidence",
    ],
    "lane_note": [
        "instead of a shipped `drivers/watchdog/dw_wdt_verify.zig` helper",
        "Do not reopen the archival survey gate, modem-control split, poll-retry split, sysrq helper, or shared reminder packet from that driver-only lane unless those exact packet surfaces are the thing moving.",
    ],
}

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


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, MARKERS[label])
        expect_forbidden_markers_absent(label, text)
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
            (FILES["note"], MARKERS["note"][4]),
            (FILES["note"], MARKERS["note"][10]),
            (FILES["closure_note"], MARKERS["closure_note"][2]),
            (FILES["closure_note"], MARKERS["closure_note"][3]),
            (FILES["lane_note"], MARKERS["lane_note"][1]),
            (FILES["lane_note"], MARKERS["lane_note"][3]),
            ("drivers/watchdog/dw_wdt_verify.zig", "drivers/watchdog/dw_wdt_verify.zig"),
            ("zigux/tests/phase11_hvc_cleanup.zig", "zigux/tests/phase11_hvc_cleanup.zig"),
            ("drivers/tty/hvc/hvc_console_verify.zig", "drivers/tty/hvc/hvc_console_verify.zig"),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            if relative_path in FILES.values():
                path.write_text(
                    path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                    encoding="utf-8",
                )
                expect_failure(case_root, marker)
            else:
                path.unlink()
                expect_failure(case_root, relative_path)

        forbidden_cases = [
            ("note", FORBIDDEN_MARKERS["note"][0]),
            ("closure_note", FORBIDDEN_MARKERS["closure_note"][1]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][0]),
        ]

        for label, marker in forbidden_cases:
            case_root = tmpdir / f"forbidden_{label}_{abs(hash(marker))}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT=12")
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
