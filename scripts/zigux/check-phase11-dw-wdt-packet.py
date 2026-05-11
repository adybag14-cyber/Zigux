#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 DesignWare watchdog packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "survey_note": "Documentation/zigux/phase11-dw-wdt-survey.md",
    "validation_matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "teardown_note": "Documentation/zigux/phase11-dw-wdt-teardown-note.md",
    "shared_contract": "Documentation/zigux/phase11-shared-replay-contract.md",
    "scripts_readme": "scripts/zigux/README.md",
    "docs_readme": "Documentation/zigux/README.md",
    "registration_scaffold": "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "verify_replay": "drivers/watchdog/dw_wdt_verify.zig",
}

SURVEY_NOTE_MARKERS = [
    "phase11-dw-wdt-registration-scaffold-tests",
    "drivers/watchdog/dw_wdt_verify.zig",
    "hardware validation matrix",
    "platform_set_drvdata",
    "watchdog_register_device",
]

VALIDATION_MATRIX_MARKERS = [
    "PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed",
    "phase11-dw-wdt-registration-scaffold-tests",
    "phase11-dw-wdt-verify-tests",
    "platform_set_drvdata",
    "watchdog_register_device",
    "drivers/watchdog/dw_wdt_verify.zig",
]

TEARDOWN_NOTE_MARKERS = [
    "continued-heartbeat semantics",
    "teardownSummary()",
    "removeSummary()",
    "drivers/watchdog/dw_wdt_verify.zig",
]

SHARED_CONTRACT_MARKERS = [
    "python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test",
    "python3 scripts/zigux/check-phase11-dw-wdt-packet.py",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
]

SCRIPTS_README_MARKERS = [
    "`scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
]

DOCS_README_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
]

EXPECTED_GAP_STATUSES = {
    "phase11-build-gate": "starter_landed",
    "phase11-dw-wdt-survey-gate": "starter_landed",
    "phase11-dw-wdt-survey-note": "starter_landed",
    "phase11-dw-wdt-driver-starter": "starter_landed",
    "phase11-dw-wdt-driver-tests": "starter_landed",
    "phase11-dw-wdt-registration-order-scaffold": "starter_landed",
    "phase11-dw-wdt-teardown-parity": "starter_landed",
    "phase11-dw-wdt-platform-registration-scaffold": "ready_next",
    "phase11-dw-wdt-live-platform-pm": "blocked_on_driver_scaffold",
}

SELF_TEST_CASE_COUNT = 8


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
    manifest_text = read_text(root, REQUIRED_FILES["manifest"])
    try:
        payload = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid json in {REQUIRED_FILES['manifest']}: {exc}") from exc

    if payload.get("lane_key") != "P11-L05":
        raise CheckError("phase11_dw_wdt_manifest.json lost lane_key P11-L05")
    if payload.get("phase") != "Phase 11":
        raise CheckError("phase11_dw_wdt_manifest.json lost Phase 11 tag")
    if payload.get("anchor") != "drivers/watchdog/dw_wdt.c":
        raise CheckError("phase11_dw_wdt_manifest.json lost drivers/watchdog/dw_wdt.c anchor")

    survey_summary = payload.get("survey_summary")
    if not isinstance(survey_summary, dict):
        raise CheckError("phase11_dw_wdt_manifest.json is missing survey_summary")

    required_summary_flags = (
        "dw_wdt_registration_scaffold_present",
        "dw_wdt_registration_order_present",
        "dw_wdt_survey_gate_present",
        "dw_wdt_survey_note_present",
    )
    for flag in required_summary_flags:
        if survey_summary.get(flag) is not True:
            raise CheckError(f"phase11_dw_wdt_manifest.json lost summary flag {flag}")

    gaps = payload.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("phase11_dw_wdt_manifest.json is missing gaps list")

    statuses_by_id: dict[str, str] = {}
    for gap in gaps:
        if not isinstance(gap, dict):
            raise CheckError("phase11_dw_wdt_manifest.json has non-object gap entry")
        gap_id = gap.get("id")
        gap_status = gap.get("status")
        if not isinstance(gap_id, str) or not gap_id:
            raise CheckError("phase11_dw_wdt_manifest.json has gap without id")
        if gap_id in statuses_by_id:
            raise CheckError(f"phase11_dw_wdt_manifest.json duplicated gap id {gap_id}")
        statuses_by_id[gap_id] = gap_status

    for gap_id, expected_status in EXPECTED_GAP_STATUSES.items():
        actual = statuses_by_id.get(gap_id)
        if actual != expected_status:
            raise CheckError(
                "phase11_dw_wdt_manifest.json lost expected status "
                f"{expected_status} for {gap_id}"
            )


def run_check(root: Path) -> None:
    check_manifest(root)
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
        REQUIRED_FILES["teardown_note"],
        read_text(root, REQUIRED_FILES["teardown_note"]),
        TEARDOWN_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["shared_contract"],
        read_text(root, REQUIRED_FILES["shared_contract"]),
        SHARED_CONTRACT_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["scripts_readme"],
        read_text(root, REQUIRED_FILES["scripts_readme"]),
        SCRIPTS_README_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["docs_readme"],
        read_text(root, REQUIRED_FILES["docs_readme"]),
        DOCS_README_MARKERS,
    )
    # Existence checks for the executable artifacts that the packet names directly.
    read_text(root, REQUIRED_FILES["registration_scaffold"])
    read_text(root, REQUIRED_FILES["verify_replay"])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(
        root / REQUIRED_FILES["manifest"],
        json.dumps(
            {
                "lane_key": "P11-L05",
                "phase": "Phase 11",
                "surveyed_commit": "75f8336c4305beed127d7abfae37d3999b7cc57c",
                "anchor": "drivers/watchdog/dw_wdt.c",
                "roadmap_destinations": [
                    "drivers/watchdog/*.zig",
                    "zigux/tests/",
                    "Documentation/zigux/",
                ],
                "survey_summary": {
                    "dw_wdt_registration_scaffold_present": True,
                    "dw_wdt_registration_order_present": True,
                    "dw_wdt_survey_gate_present": True,
                    "dw_wdt_survey_note_present": True,
                },
                "gaps": [
                    {"id": gap_id, "status": status}
                    for gap_id, status in EXPECTED_GAP_STATUSES.items()
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / REQUIRED_FILES["survey_note"],
        "\n".join(SURVEY_NOTE_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["validation_matrix"],
        "\n".join(VALIDATION_MATRIX_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["teardown_note"],
        "\n".join(TEARDOWN_NOTE_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["shared_contract"],
        "\n".join(SHARED_CONTRACT_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["scripts_readme"],
        "\n".join(SCRIPTS_README_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["docs_readme"],
        "\n".join(DOCS_README_MARKERS) + "\n",
    )
    write(root / REQUIRED_FILES["registration_scaffold"], "platform_set_drvdata\n")
    write(root / REQUIRED_FILES["verify_replay"], "missing-drvdata-platform-handoff\n")


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        manifest_path = tmpdir / REQUIRED_FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"] = [
            gap for gap in manifest["gaps"] if gap["id"] != "phase11-dw-wdt-teardown-parity"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmpdir, "phase11-dw-wdt-teardown-parity")

        build_self_test_fixture(tmpdir)
        survey_path = tmpdir / REQUIRED_FILES["survey_note"]
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "phase11-dw-wdt-registration-scaffold-tests\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase11-dw-wdt-registration-scaffold-tests")

        build_self_test_fixture(tmpdir)
        matrix_path = tmpdir / REQUIRED_FILES["validation_matrix"]
        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8").replace("watchdog_register_device\n", ""),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "watchdog_register_device")

        build_self_test_fixture(tmpdir)
        teardown_path = tmpdir / REQUIRED_FILES["teardown_note"]
        teardown_path.write_text(
            teardown_path.read_text(encoding="utf-8").replace("removeSummary()\n", ""),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "removeSummary()")

        build_self_test_fixture(tmpdir)
        contract_path = tmpdir / REQUIRED_FILES["shared_contract"]
        contract_path.write_text(
            contract_path.read_text(encoding="utf-8").replace(
                "python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "check-phase11-dw-wdt-packet.py --self-test")

        build_self_test_fixture(tmpdir)
        readme_path = tmpdir / REQUIRED_FILES["scripts_readme"]
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8").replace(
                "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase11_dw_wdt_registration_scaffold.zig")

        build_self_test_fixture(tmpdir)
        docs_readme_path = tmpdir / REQUIRED_FILES["docs_readme"]
        docs_readme_path.write_text(
            docs_readme_path.read_text(encoding="utf-8").replace(
                "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase11-dw-wdt-validation-matrix.md")

        build_self_test_fixture(tmpdir)
        shutil.rmtree(tmpdir / "drivers", ignore_errors=True)
        expect_failure(tmpdir, REQUIRED_FILES["verify_replay"])

        print("PHASE11_DW_WDT_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_DW_WDT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
