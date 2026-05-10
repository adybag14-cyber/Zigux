#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC survey packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_hvc_console_manifest.json",
    "survey_note": "Documentation/zigux/phase11-hvc-console-survey.md",
    "teardown_note": "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "validation_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
}

NOTE_MARKERS = [
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "exported hvc helper signature proof",
    "default `notifier_*_irq()` export-signature parity",
    "live sysrq execution",
]

TEARDOWN_NOTE_MARKERS = [
    "summarizeCleanupHandoff()",
    "tty_port_put()",
    "host-backed teardown",
    "summarizeRemoveHandoff()",
]

VALIDATION_MATRIX_MARKERS = [
    "sysrq dispatch boundary `summarizeSysrqHandoff()`",
    "targetless-dispatch and no-dispatch notifier-deferral replays in `drivers/tty/hvc/hvc_console_verify.zig`",
    "make -C zigux phase11-hvc-survey",
]

SURVEY_GATE_MARKERS = [
    "phase11-hvc-console-survey-gate",
    "sysrq handoff helper",
    "notifier handoff helper",
    "struct hv_ops",
    "Documentation/zigux/phase11-hvc-console-survey.md",
]

SYSRQ_HELPER_MARKERS = [
    "pub fn summarizeSysrqHandoff(",
    ".keeps_live_sysrq_execution_out_of_scope = true,",
    ".keeps_tty_registration_out_of_scope = true,",
]

SELF_TEST_CASE_COUNT = 10


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {relative_path}: {marker}")


def check_manifest(root: Path) -> None:
    manifest_path = REQUIRED_FILES["manifest"]
    manifest_text = read_text(root, manifest_path)
    try:
        payload = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid json in {manifest_path}: {exc}") from exc

    if payload.get("lane") != "P11-L16":
        raise CheckError("phase11_hvc_console_manifest.json lost lane P11-L16")

    if payload.get("status") != "starter_landed":
        raise CheckError("phase11_hvc_console_manifest.json lost starter_landed status")

    gaps = payload.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("phase11_hvc_console_manifest.json is missing gaps list")

    required_gap_ids = {
        "phase11-hvc-console-survey-gate",
        "phase11-hvc-console-survey-note",
        "phase11-hvc-console-sysrq-handoff",
    }
    seen_ids = {gap.get("id") for gap in gaps if isinstance(gap, dict)}
    missing = sorted(required_gap_ids - seen_ids)
    if missing:
        raise CheckError(
            "phase11_hvc_console_manifest.json is missing required gap ids: "
            + ", ".join(missing)
        )


def run_check(root: Path) -> None:
    check_manifest(root)
    expect_markers(
        REQUIRED_FILES["survey_note"],
        read_text(root, REQUIRED_FILES["survey_note"]),
        NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["teardown_note"],
        read_text(root, REQUIRED_FILES["teardown_note"]),
        TEARDOWN_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["validation_matrix"],
        read_text(root, REQUIRED_FILES["validation_matrix"]),
        VALIDATION_MATRIX_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["survey_gate"],
        read_text(root, REQUIRED_FILES["survey_gate"]),
        SURVEY_GATE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["sysrq_helper"],
        read_text(root, REQUIRED_FILES["sysrq_helper"]),
        SYSRQ_HELPER_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(
        root / REQUIRED_FILES["manifest"],
        json.dumps(
            {
                "lane": "P11-L16",
                "status": "starter_landed",
                "gaps": [
                    {"id": "phase11-hvc-console-survey-gate"},
                    {"id": "phase11-hvc-console-survey-note"},
                    {"id": "phase11-hvc-console-sysrq-handoff"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / REQUIRED_FILES["survey_note"],
        "\n".join(
            [
                "drivers/tty/hvc/hvc_console_sysrq.zig",
                "exported hvc helper signature proof",
                "default `notifier_*_irq()` export-signature parity",
                "live sysrq execution",
            ]
        )
        + "\n",
    )
    write(
        root / REQUIRED_FILES["teardown_note"],
        "\n".join(TEARDOWN_NOTE_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["validation_matrix"],
        "\n".join(VALIDATION_MATRIX_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["survey_gate"],
        "\n".join(SURVEY_GATE_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["sysrq_helper"],
        "\n".join(SYSRQ_HELPER_MARKERS) + "\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_survey_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "exported hvc helper signature proof\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "exported hvc helper signature proof")
        build_self_test_fixture(tmpdir)

        teardown_missing = tmpdir / REQUIRED_FILES["teardown_note"]
        teardown_missing.write_text(
            teardown_missing.read_text(encoding="utf-8").replace(
                "tty_port_put()\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "tty_port_put()")
        build_self_test_fixture(tmpdir)

        matrix_missing = tmpdir / REQUIRED_FILES["validation_matrix"]
        matrix_missing.write_text(
            matrix_missing.read_text(encoding="utf-8").replace(
                "make -C zigux phase11-hvc-survey\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "make -C zigux phase11-hvc-survey")
        build_self_test_fixture(tmpdir)

        helper_missing = tmpdir / REQUIRED_FILES["sysrq_helper"]
        helper_missing.write_text(
            helper_missing.read_text(encoding="utf-8").replace(
                ".keeps_live_sysrq_execution_out_of_scope = true,\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, ".keeps_live_sysrq_execution_out_of_scope = true,")
        build_self_test_fixture(tmpdir)

        manifest_missing = tmpdir / REQUIRED_FILES["manifest"]
        manifest = json.loads(manifest_missing.read_text(encoding="utf-8"))
        manifest["gaps"] = manifest["gaps"][:-1]
        manifest_missing.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmpdir, "phase11-hvc-console-sysrq-handoff")
        build_self_test_fixture(tmpdir)

        shutil.rmtree(tmpdir / "zigux" / "tests")
        expect_failure(tmpdir, REQUIRED_FILES["manifest"])

        print("PHASE11_HVC_SURVEY_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_HVC_SURVEY_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_SURVEY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
