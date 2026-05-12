#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

FILES = {
    "docs_root": "Documentation/zigux/README.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
    "scripts_root": "scripts/zigux/README.md",
    "tests_root": "zigux/tests/README.md",
    "tests_companion": "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
}

MARKERS = {
    "docs_root": [
        "Phase 11 flow -",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`zigux/tests/phase11_build.zig`",
        "`make -C zigux phase11`",
        "the landed HVC archival packet is the survey gate, modem-control split, poll-retry split, sysrq helper, teardown note, validation matrix, and dedicated `phase11-hvc-survey` route",
    ],
    "review_checklist": [
        "if the change touches the shared Phase 11 simple-driver packet",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`zigux/tests/phase11_build.zig`",
        "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
        "`make -C zigux phase11`",
        "five shipped Phase 11 checker scripts on current `master`",
    ],
    "scripts_root": [
        "Phase 11 flow -",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`zigux/tests/phase11_build.zig`",
        "`make -C zigux phase11`",
        "`make -C zigux phase11-hvc-survey`",
        "the landed HVC archival packet is the survey gate, modem-control split, poll-retry split, sysrq helper, teardown note, validation matrix, and dedicated `phase11-hvc-survey` route",
    ],
    "tests_root": [
        "keep the shared Phase 11 simple-driver packet explicit in the tests root too",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`zigux/tests/phase11_build.zig`",
        "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
        "`make -C zigux phase11`",
        "five shipped Phase 11 checker scripts on `master`",
        "the dedicated archival `hvc_console` teardown note plus manifest-backed survey gate, modem-control split, poll-retry split, and sysrq-helper boundary",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "`zigux/tests/phase11_hvc_console_manifest.json`",
        "`zigux/tests/phase11_hvc_console_survey.zig`",
        "`zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "`zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
        "`make -C zigux phase11-hvc-survey`",
    ],
    "tests_companion": [
        "# Phase 10, 11, and 13 Tests-Root Review Companion",
        "## Phase 11 tests-root packet",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "`zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
        "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
        "`hvc_cleanup()` teardown handoff, the dedicated archival `hvc_console` teardown note plus the validation matrix, manifest-backed survey gate, modem-control split, poll-retry split, and sysrq-helper boundary",
    ],
}

SELF_TEST_CASE_COUNT = 15


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_summary_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        cases = [
            (FILES["docs_root"], MARKERS["docs_root"][5]),
            (FILES["review_checklist"], MARKERS["review_checklist"][2]),
            (FILES["review_checklist"], MARKERS["review_checklist"][4]),
            (FILES["scripts_root"], MARKERS["scripts_root"][2]),
            (FILES["scripts_root"], MARKERS["scripts_root"][6]),
            (FILES["tests_root"], MARKERS["tests_root"][5]),
            (FILES["tests_root"], MARKERS["tests_root"][7]),
            (FILES["tests_root"], MARKERS["tests_root"][9]),
            (FILES["tests_root"], MARKERS["tests_root"][12]),
            (FILES["tests_root"], MARKERS["tests_root"][13]),
            (FILES["tests_root"], MARKERS["tests_root"][14]),
            (FILES["tests_companion"], MARKERS["tests_companion"][3]),
            (FILES["tests_companion"], MARKERS["tests_companion"][4]),
            (FILES["tests_companion"], MARKERS["tests_companion"][5]),
            (FILES["tests_companion"], MARKERS["tests_companion"][7]),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
        print(f"PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_SHARED_SUMMARY_SURFACES=fail: {exc}")
        return 1

    print("PHASE11_SHARED_SUMMARY_SURFACES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
