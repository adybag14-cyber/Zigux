#!/usr/bin/env python3

"""Fail-closed checker for the bounded Phase 11 HVC teardown/failure packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_hvc_console_manifest.json",
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "validation_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "cleanup_replay": "zigux/tests/phase11_hvc_cleanup.zig",
}

SURVEY_GATE_MARKERS = [
    "phase11-hvc-console-survey-gate",
    "cleanup handoff",
    "tty-registration handoff helper",
    "sysrq handoff helper",
    "notifier handoff helper",
    "targetless no-unregister edge",
    "struct hv_ops",
    "Documentation/zigux/phase11-hvc-console-survey.md",
]

VALIDATION_MATRIX_MARKERS = [
    "shared Phase 11 test gate",
    "cleanup replay",
    "tty-registration handoff",
    "sysrq handoff",
    "notifier-facing",
    "targetless notifier no-unregister edge",
]

REQUIRED_GAP_IDS = {
    "phase11-hvc-console-survey-gate",
    "phase11-hvc-console-survey-note",
    "phase11-hvc-console-cleanup-handoff",
    "phase11-hvc-console-remove-handoff",
    "phase11-hvc-console-driver-tests",
    "phase11-hvc-console-validation-matrix",
    "phase11-hvc-console-tty-and-teardown-parity",
    "phase11-hvc-console-sysrq-handoff",
    "phase11-hvc-console-notifier-handoff",
}

CHECKUP_REPLAY_MARKERS = [
    'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable"',
    "tty_port_put_requested",
    "CleanupRequiresTtyPortReference",
    'test "phase11 hvc console keeps write-teardown hangup buffering split reviewable"',
    "targetless no-unregister edge",
]

SELF_TEST_CASE_COUNT = 11


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

    if payload.get("lane_key") != "P11-L16":
        raise CheckError("phase11_hvc_console_manifest.json lost lane_key P11-L16")
    if payload.get("phase") != "Phase 11":
        raise CheckError("phase11_hvc_console_manifest.json lost Phase 11 marker")

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
        REQUIRED_FILES["validation_matrix"],
        read_text(root, REQUIRED_FILES["validation_matrix"]),
        VALIDATION_MATRIX_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["cleanup_replay"],
        read_text(root, REQUIRED_FILES["cleanup_replay"]),
        CHECKUP_REPLAY_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(
        root / REQUIRED_FILES["manifest"],
        json.dumps(
            {
                "lane_key": "P11-L16",
                "phase": "Phase 11",
                "gaps": [{"id": gap_id} for gap_id in sorted(REQUIRED_GAP_IDS)],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / REQUIRED_FILES["survey_gate"],
        "\n".join(SURVEY_GATE_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["validation_matrix"],
        "\n".join(VALIDATION_MATRIX_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["cleanup_replay"],
        "\n".join(CHECKUP_REPLAY_MARKERS) + "\n",
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

        gate_missing = tmpdir / REQUIRED_FILES["survey_gate"]
        gate_missing.write_text(
            gate_missing.read_text(encoding="utf-8").replace(
                "targetless no-unregister edge\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "targetless no-unregister edge")

        build_self_test_fixture(tmpdir)
        matrix_missing = tmpdir / REQUIRED_FILES["validation_matrix"]
        matrix_missing.write_text(
            matrix_missing.read_text(encoding="utf-8").replace(
                "targetless notifier no-unregister edge\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "targetless notifier no-unregister edge")

        build_self_test_fixture(tmpdir)
        cleanup_missing = tmpdir / REQUIRED_FILES["cleanup_replay"]
        cleanup_missing.write_text(
            cleanup_missing.read_text(encoding="utf-8").replace(
                "CleanupRequiresTtyPortReference\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "CleanupRequiresTtyPortReference")

        build_self_test_fixture(tmpdir)
        manifest_missing = tmpdir / REQUIRED_FILES["manifest"]
        manifest = json.loads(manifest_missing.read_text(encoding="utf-8"))
        manifest["gaps"] = manifest["gaps"][:-1]
        manifest_missing.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmpdir, "phase11-hvc-console-")

        build_self_test_fixture(tmpdir)
        shutil.rmtree(tmpdir / "zigux" / "tests")
        expect_failure(tmpdir, REQUIRED_FILES["manifest"])

        print("PHASE11_HVC_TEARDOWN_FAILURE_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_TEARDOWN_FAILURE_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_HVC_TEARDOWN_FAILURE_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_TEARDOWN_FAILURE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
