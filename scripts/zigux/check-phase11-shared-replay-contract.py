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
    "scripts/zigux/check-phase11-dw-wdt-packet.py",
    "scripts/zigux/check-phase11-shared-summary-surfaces.py",
    "Documentation/zigux/phase11-hvc-console-slice.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
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
        "* `Documentation/zigux/phase11-shared-replay-contract.md`",
        "* `Documentation/zigux/phase11-closure-note.md`",
        "* `Documentation/zigux/phase11-driver-lane-sequencing.md`",
        "* `scripts/zigux/check-phase11-shared-replay-contract.py`",
        "* `scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "* `zigux/tests/phase11_build.zig`",
        "* `make -C zigux phase11`",
        "* no shared `validate-phase11.py`",
        "* no shared `make -C zigux phase11-validate` target on `master`",
        "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "The DesignWare watchdog lane now keeps its surviving bounded reminder packet explicit beside that shared route:",
        "* `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "* `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "Treat `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` together with `scripts/zigux/check-phase11-dw-wdt-packet.py` as the current DesignWare continuity packet on `master`: they keep the next bounded step pinned to platform-backed registration scaffolding while the older manifest, survey, validation-matrix, and teardown reminder surfaces stay removed rather than being silently reintroduced as shared evidence.",
        "The dedicated archival HVC evidence still stays explicit beside that shared route:",
        "* `Documentation/zigux/phase11-hvc-console-slice.md`",
        "* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "* `Documentation/zigux/phase11-hvc-console-survey.md`",
        "* `Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "* `zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "* `drivers/tty/hvc/hvc_console_sysrq.zig`",
        "* `scripts/zigux/check-phase11-hvc-survey-packet.py`",
        "* `zigux/tests/phase11_hvc_console_manifest.json`",
        "* `zigux/tests/phase11_hvc_console_survey.zig`",
        "* `make -C zigux phase11-hvc-survey`",
        "Treat `Documentation/zigux/phase11-hvc-console-teardown-note.md` together with `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey` as the landed dedicated HVC archival evidence on current `master`, while direct `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` stay recorded as the remaining repo-reality gaps rather than shared proof.",
        "The shared header-boundary evidence also stays explicit beside that shared route:",
        "* `Documentation/zigux/phase11-uapi-header-parity-survey.md`",
        "* `scripts/zigux/check-phase11-header-boundary-packet.py`",
        "* `zigux/tests/phase11_uapi_header_parity_manifest.json`",
        "* `zigux/tests/phase11_uapi_header_parity_survey.zig`",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "* `zigux/tests/phase11_build.zig`",
        "* DesignWare watchdog continuity now stays with `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` and `scripts/zigux/check-phase11-dw-wdt-packet.py`, which keep the surviving bounded DesignWare packet and the next platform-registration scaffold explicit while the older manifest, survey, validation-matrix, and teardown reminder surfaces remain removed on current `master`",
        "* HVC archival continuity stays with `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, and `make -C zigux phase11-hvc-survey`, while direct `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` stay framed as the remaining repo-reality gaps rather than shared closure evidence",
        "* shared header boundary continuity stays with `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_survey.zig`",
        "* there is no shared `validate-phase11.py`",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
        "* there is no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "- DesignWare lane `P11-L10` currently owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig` as the surviving bounded DesignWare packet; the next same-lane follow-through is platform-backed registration scaffolding rather than reviving removed manifest, survey, validation-matrix, or teardown reminder surfaces without new evidence",
        "The shared packet surfaces still living together on current `master` are `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, and `make -C zigux phase11`.",
        "Keep the current validator posture explicit: there is a shared `zigux/tests/phase11_build.zig` route and a shared `make -C zigux phase11` wrapper on current `master`, but there is no shared `validate-phase11.py`, no shared `zigux/tests/fixtures/phase11_build_inventory.json`, and no shared `make -C zigux phase11-validate` target, so reminder-surface edits should stay aligned with the surviving build-backed packet instead of reviving the older inventory-driven validator story.",
        "7. Keep the DesignWare lane honest: on current `master` the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`, pinned to `P11-L10`, and the next bounded step is platform-backed registration scaffolding rather than pretending removed manifest-backed reminder surfaces are still shipped.",
        "8. Keep the HVC split honest: on current `master` the landed HVC archival packet is the teardown note, validation matrix, survey note, manifest-backed survey gate, modem-control split, poll-retry split, sysrq helper, and dedicated `phase11-hvc-survey` route, while direct driver-file follow-through now stays on `P11-Y04` inside `drivers/tty/hvc/hvc_console.zig` plus at most one directly coupled teardown-note wording repair. Do not reopen the archival survey gate, modem-control split, poll-retry split, sysrq helper, or shared reminder packet from that driver-only lane unless those exact packet surfaces are the thing moving.",
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
            (FILES["note"], "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`"),
            (FILES["note"], "* `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`"),
            (FILES["note"], "Treat `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` together with `scripts/zigux/check-phase11-dw-wdt-packet.py` as the current DesignWare continuity packet on `master`: they keep the next bounded step pinned to platform-backed registration scaffolding while the older manifest, survey, validation-matrix, and teardown reminder surfaces stay removed rather than being silently reintroduced as shared evidence."),
            (FILES["note"], "* `zigux/tests/phase11_hvc_console_manifest.json`"),
            (FILES["note"], "* `drivers/tty/hvc/hvc_console_sysrq.zig`"),
            (FILES["closure_note"], "* DesignWare watchdog continuity now stays with `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` and `scripts/zigux/check-phase11-dw-wdt-packet.py`, which keep the surviving bounded DesignWare packet and the next platform-registration scaffold explicit while the older manifest, survey, validation-matrix, and teardown reminder surfaces remain removed on current `master`"),
            (FILES["closure_note"], "* there is no shared `make -C zigux phase11-validate` target on `master`"),
            (FILES["lane_note"], "- DesignWare lane `P11-L10` currently owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig` as the surviving bounded DesignWare packet; the next same-lane follow-through is platform-backed registration scaffolding rather than reviving removed manifest, survey, validation-matrix, or teardown reminder surfaces without new evidence"),
            (FILES["lane_note"], "7. Keep the DesignWare lane honest: on current `master` the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`, pinned to `P11-L10`, and the next bounded step is platform-backed registration scaffolding rather than pretending removed manifest-backed reminder surfaces are still shipped."),
            ("Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md", "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"),
            ("scripts/zigux/check-phase11-dw-wdt-packet.py", "scripts/zigux/check-phase11-dw-wdt-packet.py"),
            ("Documentation/zigux/phase11-hvc-console-teardown-note.md", "Documentation/zigux/phase11-hvc-console-teardown-note.md"),
            ("zigux/tests/phase11_hvc_console_manifest.json", "zigux/tests/phase11_hvc_console_manifest.json"),
            ("drivers/tty/hvc/hvc_console_sysrq.zig", "drivers/tty/hvc/hvc_console_sysrq.zig"),
            ("Documentation/zigux/phase11-uapi-header-parity-survey.md", "Documentation/zigux/phase11-uapi-header-parity-survey.md"),
            ("zigux/tests/phase11_uapi_header_parity_manifest.json", "zigux/tests/phase11_uapi_header_parity_manifest.json"),
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
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={len(cases)}")
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
