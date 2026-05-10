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
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "survey_note": "Documentation/zigux/phase11-hvc-console-survey.md",
    "validation_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "slice_note": "Documentation/zigux/phase11-hvc-console-slice.md",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
}

REQUIRED_GAP_IDS = {
    "phase11-hvc-console-survey-gate",
    "phase11-hvc-console-survey-note",
    "phase11-hvc-console-driver-tests",
    "phase11-hvc-console-validation-matrix",
    "phase11-hvc-console-tty-and-teardown-parity",
    "phase11-hvc-console-header-parity",
    "phase11-hvc-console-hv-ops-signature-assert",
}

SURVEY_GATE_MARKERS = [
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "pub const SysrqHandoffRequest",
    "pub fn summarizeSysrqHandoff",
    "keeps_live_sysrq_execution_out_of_scope = true",
    'test "phase11 hvc console survey keeps bounded exported helper signature proofs"',
    "notifier_add_irq",
    "notifier_hangup_irq",
]

SURVEY_NOTE_MARKERS = [
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "bounded supporting helper",
    "exported-helper signature proof",
    "hvc_kick()",
    "notifier_add_irq()",
    "notifier_hangup_irq()",
]

VALIDATION_MATRIX_MARKERS = [
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "dedicated `make -C zigux phase11-hvc-survey` archival route fail-closed",
    "sysrq handoff",
    "notifier-facing handoff",
    "`hvc_cleanup()` tty-port release handoff",
]

SLICE_NOTE_MARKERS = [
    "tiny sysrq handoff summary",
    "notifier-facing handoff summary",
    "does not claim tty-driver registration, notifier callback execution, khvcd polling, live sysrq dispatch",
]

SYSRQ_HELPER_MARKERS = [
    "pub const SysrqHandoffRequest",
    "pub const SysrqHandoffSnapshot",
    "pub fn summarizeSysrqHandoff",
    "toggles_sysrq_mode",
    "invokes_sysrq_handler",
    "keeps_live_sysrq_execution_out_of_scope = true",
]

SELF_TEST_CASE_COUNT = 6


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

    if payload.get("phase") != "Phase 11":
        raise CheckError("phase11_hvc_console_manifest.json lost Phase 11 marker")
    if payload.get("anchor") != "drivers/tty/hvc/hvc_console.c":
        raise CheckError("phase11_hvc_console_manifest.json lost the hvc_console anchor")

    survey_summary = payload.get("survey_summary")
    if not isinstance(survey_summary, dict):
        raise CheckError("phase11_hvc_console_manifest.json is missing survey_summary")
    for field in (
        "hvc_console_sysrq_present",
        "hvc_console_survey_gate_present",
        "hvc_console_survey_note_present",
    ):
        if survey_summary.get(field) is not True:
            raise CheckError(
                f"phase11_hvc_console_manifest.json lost survey_summary.{field}"
            )

    gaps = payload.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("phase11_hvc_console_manifest.json is missing gaps list")

    seen_ids = {gap.get("id") for gap in gaps if isinstance(gap, dict)}
    missing = sorted(REQUIRED_GAP_IDS - seen_ids)
    if missing:
        raise CheckError(
            "phase11_hvc_console_manifest.json is missing required gap ids: "
            + ", ".join(missing)
        )


def run_check(root: Path) -> None:
    check_manifest(root)
    expect_markers(
        REQUIRED_FILES["survey_gate"],
        read_text(root, REQUIRED_FILES["survey_gate"]),
        SURVEY_GATE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["survey_note"],
        read_text(root, REQUIRED_FILES["survey_note"]),
        SURVEY_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["validation_matrix"],
        read_text(root, REQUIRED_FILES["validation_matrix"]),
        VALIDATION_MATRIX_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["slice_note"],
        read_text(root, REQUIRED_FILES["slice_note"]),
        SLICE_NOTE_MARKERS,
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
                "phase": "Phase 11",
                "anchor": "drivers/tty/hvc/hvc_console.c",
                "survey_summary": {
                    "hvc_console_sysrq_present": True,
                    "hvc_console_survey_gate_present": True,
                    "hvc_console_survey_note_present": True,
                },
                "gaps": [{"id": gap_id} for gap_id in sorted(REQUIRED_GAP_IDS)],
            },
            indent=2,
        )
        + "\n",
    )
    write(root / REQUIRED_FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write(
        root / REQUIRED_FILES["validation_matrix"],
        "\n".join(VALIDATION_MATRIX_MARKERS) + "\n",
    )
    write(root / REQUIRED_FILES["slice_note"], "\n".join(SLICE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["sysrq_helper"], "\n".join(SYSRQ_HELPER_MARKERS) + "\n")


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

        gate_missing = tmpdir / REQUIRED_FILES["survey_gate"]
        gate_missing.write_text(
            gate_missing.read_text(encoding="utf-8").replace(
                "notifier_hangup_irq\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "notifier_hangup_irq")

        build_self_test_fixture(tmpdir)
        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "exported-helper signature proof\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "exported-helper signature proof")

        build_self_test_fixture(tmpdir)
        manifest_missing = tmpdir / REQUIRED_FILES["manifest"]
        manifest = json.loads(manifest_missing.read_text(encoding="utf-8"))
        manifest["gaps"] = manifest["gaps"][:-1]
        manifest_missing.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmpdir, "phase11_hvc_console_manifest.json is missing required gap ids")

        build_self_test_fixture(tmpdir)
        helper_missing = tmpdir / REQUIRED_FILES["sysrq_helper"]
        helper_missing.write_text(
            helper_missing.read_text(encoding="utf-8").replace(
                "pub fn summarizeSysrqHandoff\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "pub fn summarizeSysrqHandoff")

        build_self_test_fixture(tmpdir)
        shutil.rmtree(tmpdir / "Documentation")
        expect_failure(tmpdir, REQUIRED_FILES["survey_note"])

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
