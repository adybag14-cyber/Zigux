#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC current-head manifest packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/phase11_hvc_current_head_manifest.json"
SURVEY_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
COMPANION_PATH = "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"

EXPECTED_PACKET_FILES = [
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "drivers/tty/hvc/hvc_console.h",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-validate-manifest-roster.py",
    "scripts/zigux/check-phase11-validate-check-roster.py",
    "scripts/zigux/check-phase11-validate-route-alignment.py",
    "scripts/zigux/check-phase11-focused-direct-build-replays.py",
    "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py",
    "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
    "scripts/zigux/check-phase11-hvc-current-head-manifest.py",
    "scripts/zigux/validate-phase11.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    MANIFEST_PATH,
]

EXPECTED_CHECKS = [
    "python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py",
    "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-validate-manifest-roster.py --self-test",
    "python3 scripts/zigux/check-phase11-validate-manifest-roster.py",
    "python3 scripts/zigux/check-phase11-validate-check-roster.py --self-test",
    "python3 scripts/zigux/check-phase11-validate-check-roster.py",
    "python3 scripts/zigux/check-phase11-validate-route-alignment.py --self-test",
    "python3 scripts/zigux/check-phase11-validate-route-alignment.py",
    "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test",
    "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py",
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
    "python3 scripts/zigux/validate-phase11.py --self-test",
    "python3 scripts/zigux/validate-phase11.py",
    "make -C zigux phase11-validate",
    "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
]

EXPECTED_GAPS = [
    "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "make -C zigux phase11-hvc-survey",
]

SURVEY_MARKERS = (
    "`zigux/tests/phase11_hvc_current_head_manifest.json`",
    "machine-readable current-head manifest packet",
    "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
)

MATRIX_MARKERS = (
    "`zigux/tests/phase11_hvc_current_head_manifest.json`",
    "machine-readable current-head manifest packet",
    "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
)

COMPANION_MARKERS = (
    "`zigux/tests/phase11_hvc_current_head_manifest.json`",
    "machine-readable current-head manifest packet",
    "`scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckError(f"missing required file: {relative_path}") from exc


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_manifest(root: Path) -> dict[str, object]:
    path = root / MANIFEST_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CheckError(f"missing required file: {MANIFEST_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {MANIFEST_PATH}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"{MANIFEST_PATH} must contain a JSON object")
    return payload


def expect_string(label: str, value: object, expected: str) -> None:
    if value != expected:
        raise CheckError(f"{label} mismatch: expected {expected!r}, found {value!r}")


def expect_string_list(label: str, value: object, expected: list[str]) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"{label} must be a string list")
    if value != expected:
        raise CheckError(f"{label} mismatch: expected {expected!r}, found {value!r}")


def require_markers(root: Path, relative_path: str, markers: tuple[str, ...]) -> None:
    text = read_text(root, relative_path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{relative_path} is missing required marker: {marker!r}")


def validate(root: Path) -> None:
    manifest = read_manifest(root)
    expect_string("lane_key", manifest.get("lane_key"), "P11-L16")
    expect_string("phase", manifest.get("phase"), "Phase 11")
    expect_string(
        "packet_status",
        manifest.get("packet_status"),
        "current_head_companion_packet_truthful",
    )
    expect_string(
        "validate_route",
        manifest.get("validate_route"),
        "make -C zigux phase11-validate",
    )
    expect_string_list("packet_files", manifest.get("packet_files"), EXPECTED_PACKET_FILES)
    expect_string_list("exact_current_checks", manifest.get("exact_current_checks"), EXPECTED_CHECKS)
    expect_string_list("repo_reality_gaps", manifest.get("repo_reality_gaps"), EXPECTED_GAPS)

    require_markers(root, SURVEY_PATH, SURVEY_MARKERS)
    require_markers(root, MATRIX_PATH, MATRIX_MARKERS)
    require_markers(root, COMPANION_PATH, COMPANION_MARKERS)


def build_fixture(root: Path) -> None:
    manifest = {
        "lane_key": "P11-L16",
        "phase": "Phase 11",
        "packet_status": "current_head_companion_packet_truthful",
        "scope": "fixture scope",
        "validate_route": "make -C zigux phase11-validate",
        "packet_files": EXPECTED_PACKET_FILES,
        "exact_current_checks": EXPECTED_CHECKS,
        "repo_reality_gaps": EXPECTED_GAPS,
    }
    write_text(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root,
        SURVEY_PATH,
        "\n".join(
            [
                "# survey",
                "machine-readable current-head manifest packet",
                "`zigux/tests/phase11_hvc_current_head_manifest.json`",
                "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py --self-test`",
                "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
            ]
        )
        + "\n",
    )
    write_text(
        root,
        MATRIX_PATH,
        "\n".join(
            [
                "# matrix",
                "machine-readable current-head manifest packet",
                "`zigux/tests/phase11_hvc_current_head_manifest.json`",
                "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py --self-test`",
                "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
            ]
        )
        + "\n",
    )
    write_text(
        root,
        COMPANION_PATH,
        "\n".join(
            [
                "# companion",
                "machine-readable current-head manifest packet",
                "`zigux/tests/phase11_hvc_current_head_manifest.json`",
                "`scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
            ]
        )
        + "\n",
    )


def expect_failure(root: Path, mutate, fragment: str) -> None:
    mutate(root)
    try:
        validate(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-current-head-manifest-"))
    cases = 0
    try:
        fixture = temp_dir / "fixture"
        build_fixture(fixture)
        validate(fixture)
        cases += 1

        mutations = (
            (
                MANIFEST_PATH,
                '"lane_key": "P11-L16"',
                '"lane_key": "P11-L99"',
                "lane_key mismatch",
            ),
            (
                MANIFEST_PATH,
                '"phase": "Phase 11"',
                '"phase": "Phase 12"',
                "phase mismatch",
            ),
            (
                MANIFEST_PATH,
                '"make -C zigux phase11-validate"',
                '"make -C zigux phase11"',
                "validate_route mismatch",
            ),
            (
                SURVEY_PATH,
                "`zigux/tests/phase11_hvc_current_head_manifest.json`",
                "",
                SURVEY_PATH,
            ),
            (
                MATRIX_PATH,
                "`python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
                "",
                MATRIX_PATH,
            ),
            (
                COMPANION_PATH,
                "machine-readable current-head manifest packet",
                "",
                COMPANION_PATH,
            ),
        )

        for index, (relative_path, old, new, fragment) in enumerate(mutations, start=1):
            broken = temp_dir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(
                broken,
                lambda root, rel=relative_path, before=old, after=new: write_text(
                    root,
                    rel,
                    read_text(root, rel).replace(before, after, 1),
                ),
                fragment,
            )
            cases += 1

        missing = temp_dir / "missing"
        shutil.copytree(fixture, missing, dirs_exist_ok=True)
        expect_failure(
            missing,
            lambda root: (root / MANIFEST_PATH).unlink(),
            MANIFEST_PATH,
        )
        cases += 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PHASE11_HVC_CURRENT_HEAD_MANIFEST_SELF_TEST=pass")
    print(f"PHASE11_HVC_CURRENT_HEAD_MANIFEST_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 HVC current-head manifest packet for drift."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--write-sample-root",
        default="",
        help="Optional directory to populate with a passing sample packet tree.",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        if sample_root.exists():
            shutil.rmtree(sample_root)
        build_fixture(sample_root)
        print(f"PHASE11_HVC_CURRENT_HEAD_MANIFEST_SAMPLE_ROOT={sample_root}")
        return 0

    try:
        validate(Path(args.repo_root).resolve())
    except CheckError as exc:
        print(f"PHASE11_HVC_CURRENT_HEAD_MANIFEST=fail: {exc}")
        return 1

    print("PHASE11_HVC_CURRENT_HEAD_MANIFEST=pass")
    print(f"PHASE11_HVC_CURRENT_HEAD_MANIFEST_PACKET_FILE_COUNT={len(EXPECTED_PACKET_FILES)}")
    print(f"PHASE11_HVC_CURRENT_HEAD_MANIFEST_EXACT_CHECK_COUNT={len(EXPECTED_CHECKS)}")
    print(f"PHASE11_HVC_CURRENT_HEAD_MANIFEST_GAP_COUNT={len(EXPECTED_GAPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
