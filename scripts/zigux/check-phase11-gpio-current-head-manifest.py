#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 gpio_wdt current-head manifest packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/phase11_gpio_wdt_current_head_manifest.json"
SURVEY_PATH = "Documentation/zigux/phase11-gpio-wdt-survey.md"
MATRIX_PATH = "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md"
BUILD_PATH = "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig"

EXPECTED_CURRENT_HEAD_SURFACES = [
    "drivers/watchdog/gpio_wdt.zig",
    "drivers/watchdog/gpio_wdt_verify.zig",
    "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_registration_intent_review.zig",
    "zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest.json",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
]

EXPECTED_GAP_SUMMARY = [
    ("phase11-gpio-wdt-driver-starter", "starter_landed"),
    ("phase11-gpio-wdt-verify-helper", "starter_landed"),
    ("phase11-gpio-wdt-preflight-proof", "starter_landed"),
    ("phase11-gpio-wdt-registration-intent-proof", "starter_landed"),
    ("phase11-gpio-wdt-register-device-glue-proof", "starter_landed"),
    ("phase11-gpio-wdt-nowayout-proof", "starter_landed"),
    ("phase11-gpio-wdt-remove-handoff-proof", "starter_landed"),
    ("phase11-gpio-wdt-current-head-manifest", "starter_landed"),
    ("phase11-gpio-wdt-current-head-manifest-survey", "starter_landed"),
    ("phase11-gpio-wdt-shared-build-route", "shared_gap_current_head"),
    ("phase11-gpio-wdt-older-manifest-return", "shared_gap_current_head"),
    ("phase11-gpio-wdt-live-platform-validation", "ready_next"),
]

SURVEY_MARKERS = (
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
    "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py`",
    "registration-intent route",
    "dedicated build route",
)

MATRIX_MARKERS = (
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
    "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py`",
    "focused registration-intent proof",
    "packet aligned through",
)

BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_gpio_wdt_current_head_manifest_survey.zig")',
    '.name = "phase11-gpio-wdt-current-head-manifest-survey-tests"',
    "Run the focused Phase 11 gpio watchdog current-head manifest survey",
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
    expect_string("lane_key", manifest.get("lane_key"), "P11-L04")
    expect_string("phase", manifest.get("phase"), "Phase 11")
    expect_string(
        "packet_kind",
        manifest.get("packet_kind"),
        "current_head_driver_docs_and_proof_packet",
    )
    expect_string_list(
        "current_head_surfaces",
        manifest.get("current_head_surfaces"),
        EXPECTED_CURRENT_HEAD_SURFACES,
    )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("gaps must be a list")
    gap_summary: list[tuple[str, str]] = []
    for gap in gaps:
        if not isinstance(gap, dict):
            raise CheckError("each gap must be an object")
        gap_id = gap.get("id")
        status = gap.get("status")
        if not isinstance(gap_id, str) or not isinstance(status, str):
            raise CheckError("each gap must have string id and status")
        gap_summary.append((gap_id, status))
    if gap_summary != EXPECTED_GAP_SUMMARY:
        raise CheckError(
            f"gap summary mismatch: expected {EXPECTED_GAP_SUMMARY!r}, found {gap_summary!r}"
        )

    require_markers(root, SURVEY_PATH, SURVEY_MARKERS)
    require_markers(root, MATRIX_PATH, MATRIX_MARKERS)
    require_markers(root, BUILD_PATH, BUILD_MARKERS)


def build_fixture(root: Path) -> None:
    manifest = {
        "lane_key": "P11-L04",
        "phase": "Phase 11",
        "anchor": "drivers/watchdog/gpio_wdt.c",
        "packet_kind": "current_head_driver_docs_and_proof_packet",
        "current_head_surfaces": EXPECTED_CURRENT_HEAD_SURFACES,
        "gaps": [
            {"id": gap_id, "status": status}
            for gap_id, status in EXPECTED_GAP_SUMMARY
        ],
    }
    write_text(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root,
        SURVEY_PATH,
        "\n".join(
            [
                "# survey",
                "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`",
                "`zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`",
                "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
                "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
                "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
                "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`",
                "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py`",
                "registration-intent route with a dedicated build route",
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
                "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`",
                "`zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`",
                "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
                "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
                "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
                "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`",
                "`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py`",
                "focused registration-intent proof",
                "packet aligned through",
            ]
        )
        + "\n",
    )
    write_text(
        root,
        BUILD_PATH,
        "\n".join(
            [
                'const survey_module = b.createModule(.{ .root_source_file = b.path("phase11_gpio_wdt_current_head_manifest_survey.zig"), });',
                'const survey_tests = b.addTest(.{ .name = "phase11-gpio-wdt-current-head-manifest-survey-tests", .root_module = survey_module, });',
                'const test_step = b.step("test", "Run the focused Phase 11 gpio watchdog current-head manifest survey");',
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
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-gpio-current-head-manifest-"))
    cases = 0
    try:
        fixture = temp_dir / "fixture"
        build_fixture(fixture)
        validate(fixture)
        cases += 1

        mutations = (
            (MANIFEST_PATH, '"lane_key": "P11-L04"', '"lane_key": "P11-L99"', "lane_key mismatch"),
            (MANIFEST_PATH, '"packet_kind": "current_head_driver_docs_and_proof_packet"', '"packet_kind": "drifted_packet"', "packet_kind mismatch"),
            (SURVEY_PATH, "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`", "", SURVEY_PATH),
            (MATRIX_PATH, "focused registration-intent proof", "", MATRIX_PATH),
            (BUILD_PATH, 'Run the focused Phase 11 gpio watchdog current-head manifest survey', 'Run a different survey', BUILD_PATH),
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

    print("PHASE11_GPIO_CURRENT_HEAD_MANIFEST_SELF_TEST=pass")
    print(f"PHASE11_GPIO_CURRENT_HEAD_MANIFEST_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 gpio watchdog current-head manifest packet for drift."
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
        print(f"PHASE11_GPIO_CURRENT_HEAD_MANIFEST_SAMPLE_ROOT={sample_root}")
        return 0

    try:
        validate(Path(args.repo_root).resolve())
    except CheckError as exc:
        print(f"PHASE11_GPIO_CURRENT_HEAD_MANIFEST=fail: {exc}")
        return 1

    print("PHASE11_GPIO_CURRENT_HEAD_MANIFEST=pass")
    print(
        f"PHASE11_GPIO_CURRENT_HEAD_MANIFEST_SURFACE_COUNT={len(EXPECTED_CURRENT_HEAD_SURFACES)}"
    )
    print(f"PHASE11_GPIO_CURRENT_HEAD_MANIFEST_GAP_COUNT={len(EXPECTED_GAP_SUMMARY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
