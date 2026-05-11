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
    "docs_readme": "Documentation/zigux/README.md",
    "scripts_readme": "scripts/zigux/README.md",
    "tests_readme": "zigux/tests/README.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
}

MARKERS = {
    "note": [
        "# Phase 11 Shared Replay Contract",
        "* `scripts/zigux/check-phase11-shared-replay-contract.py`",
        "The live DesignWare watchdog follow-through inside that shared route stays explicit through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`.",
        "* DesignWare watchdog planning lane: `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "The dedicated archival HVC evidence on current `master` is also kept explicit beside that shared route through the bounded survey, teardown, and failure-mode packet:",
        "* `Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "* `zigux/tests/phase11_hvc_console_manifest.json`",
        "* `zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "* `zigux/tests/phase11_hvc_console_survey.zig`",
        "* `drivers/tty/hvc/hvc_console_sysrq.zig`",
        "* `make -C zigux phase11-hvc-survey`",
        "without promoting missing driver-root starter, cleanup replay, or compile-local verify-helper files into the current shared contract.",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_parked`",
        "* `Documentation/zigux/phase11-shared-replay-contract.md`",
        "* `Documentation/zigux/phase11-driver-lane-sequencing.md`",
        "* `Documentation/zigux/phase11-uapi-header-parity-survey.md`",
        "* DesignWare watchdog planning lane: `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "* HVC archival packet: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "* `make -C zigux phase11-hvc-survey`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "Keep the current lane split explicit:",
        "- bcm2835 lane `P11-L03` owns",
        "- gpio lane `P11-L06` owns",
        "- DesignWare lane `P11-L11` is currently a docs-only planning lane on `master`",
        "- HVC lane `P11-L16` owns",
        "- header-boundary lane `P11-L18` owns",
        "rather than missing `hvc_console` starter, cleanup, manifest, or verify-helper files.",
    ],
    "docs_readme": [
        "Phase 11 notes - `Documentation/zigux/phase11-bcm2835-wdt-slice.md`",
        "`Documentation/zigux/phase11-shared-replay-contract.md` now records that same shared contributor packet",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    ],
    "scripts_readme": [
        "Phase 11 flow - `Documentation/zigux/README.md`",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig` helper path",
    ],
    "tests_readme": [
        "keep the shared Phase 11 simple-driver packet explicit in the tests root too:",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
        "`zigux/tests/phase11_hvc_console_manifest.json`",
        "`make -C zigux phase11-hvc-survey`",
    ],
    "review_checklist": [
        "if the change touches the shared Phase 11 simple-driver packet",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`Documentation/zigux/phase11-closure-note.md`",
        "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md`",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
    ],
}

SELF_TEST_CASE_COUNT = 8


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


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    for label, relative_path in FILES.items():
        write(root / relative_path, "\n".join(MARKERS[label]) + "\n")


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
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        cases = [
            (FILES["note"], MARKERS["note"][2]),
            (FILES["note"], MARKERS["note"][12]),
            (FILES["closure_note"], MARKERS["closure_note"][5]),
            (FILES["lane_note"], MARKERS["lane_note"][4]),
            (FILES["docs_readme"], MARKERS["docs_readme"][1]),
            (FILES["tests_readme"], MARKERS["tests_readme"][4]),
            (FILES["review_checklist"], MARKERS["review_checklist"][4]),
            (FILES["review_checklist"], MARKERS["review_checklist"][6]),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(tmpdir, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(path.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
            expect_failure(case_root, marker)

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
