#!/usr/bin/env python3
"""Fail-closed survey for the Phase 11 golden-output tooling gap."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

GAP = "zigux/tests/phase11_golden_output_tooling_gap.json"
MANIFEST = "zigux/tests/phase11_gpio_wdt_current_head_manifest.json"
SURVEY = "Documentation/zigux/phase11-gpio-wdt-survey.md"
MATRIX = "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md"

REQUIREMENTS = [
    "deterministic artifact generation where applicable",
    "fixture or known-vector parity",
    "hardware validation matrix",
    "teardown and failure-mode parity",
]
ROUTES = [
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig",
]
BLOCKED = {
    "zigux/tests/phase11_gpio_wdt_manifest.json": "older wider manifest has not returned on current master",
    "zigux/tests/phase11_gpio_wdt_survey.zig": "older wider survey gate has not returned on current master",
    "zigux/tests/phase11_gpio_wdt.zig": "wider replay remains outside the current-head packet",
    "zigux/tests/phase11_gpio_wdt_platform_drvdata.zig": "live drvdata replay remains outside the current-head packet",
    "zigux/tests/phase11_build.zig": "shared Phase 11 build route has not returned on current master",
}
STATUSES = ["starter_landed", "shared_gap_current_head", "ready_next"]
DOC_MARKERS = {
    SURVEY: [
        "older wider replay and manifest route surfaces such as",
        "`zigux/tests/phase11_gpio_wdt_manifest.json`",
        "`zigux/tests/phase11_build.zig`",
        "hardware-backed validation",
        "current-head manifest",
    ],
    MATRIX: [
        "The older wider replay and route surfaces",
        "`zigux/tests/phase11_gpio_wdt_manifest.json`",
        "`zigux/tests/phase11_build.zig`",
        "hardware-backed validation",
        "machine-readable current-head manifest",
    ],
}


class CheckError(RuntimeError):
    pass


def text(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckError(f"missing required path: {rel}") from exc


def obj(root: Path, rel: str) -> object:
    try:
        return json.loads(text(root, rel))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {rel}: {exc}") from exc


def same(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise CheckError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_gap(root: Path) -> dict:
    gap = obj(root, GAP)
    if not isinstance(gap, dict):
        raise CheckError(f"{GAP} must contain an object")
    same(gap.get("lane_key"), "P11-L07", "lane_key")
    same(gap.get("phase"), "Phase 11", "phase")
    same(gap.get("survey_kind"), "fixture_refresh_and_golden_output_tooling_gap", "survey_kind")
    same(gap.get("current_packet_anchor"), MANIFEST, "current_packet_anchor")
    same(gap.get("roadmap_requirements"), REQUIREMENTS, "roadmap_requirements")
    same(gap.get("current_packet_statuses"), STATUSES, "current_packet_statuses")
    same(gap.get("returned_current_head_routes"), ROUTES, "returned_current_head_routes")
    blocked = gap.get("blocked_golden_output_surfaces")
    if not isinstance(blocked, list):
        raise CheckError("blocked_golden_output_surfaces must be a list")
    actual = {}
    for row in blocked:
        if not isinstance(row, dict):
            raise CheckError("blocked_golden_output_surfaces entries must be objects")
        actual[row.get("path")] = row.get("reason")
    same(actual, BLOCKED, "blocked_golden_output_surfaces")
    next_step = gap.get("next_step")
    if not isinstance(next_step, str) or "wider gpio watchdog fixture/manifest pair" not in next_step:
        raise CheckError("next_step must keep the wider fixture/manifest pair as the bounded follow-up")
    return gap


def validate_manifest(root: Path, gap: dict) -> None:
    manifest = obj(root, MANIFEST)
    if not isinstance(manifest, dict):
        raise CheckError(f"{MANIFEST} must contain an object")
    same(manifest.get("lane_key"), "P11-L04", "current-head lane_key")
    same(manifest.get("phase"), "Phase 11", "current-head phase")
    same(manifest.get("packet_kind"), "current_head_driver_docs_and_proof_packet", "current-head packet_kind")
    statuses = {row.get("status") for row in manifest.get("gaps", []) if isinstance(row, dict)}
    for status in gap["current_packet_statuses"]:
        if status not in statuses:
            raise CheckError(f"current-head manifest missing status {status!r}")
    surfaces = manifest.get("current_head_surfaces", [])
    for route in ROUTES:
        if route not in surfaces:
            raise CheckError(f"current_head_surfaces missing {route!r}")
    for blocked_path in BLOCKED:
        if blocked_path in surfaces:
            raise CheckError(f"blocked golden-output surface is present in current-head packet: {blocked_path}")


def validate_docs(root: Path) -> None:
    for rel, markers in DOC_MARKERS.items():
        body = text(root, rel)
        for marker in markers:
            if marker not in body:
                raise CheckError(f"{rel} missing marker {marker!r}")


def validate(root: Path) -> None:
    gap = validate_gap(root)
    validate_manifest(root, gap)
    validate_docs(root)


def write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_json(root: Path, rel: str, data: object) -> None:
    write(root, rel, json.dumps(data, indent=2) + "\n")


def build_fixture(root: Path) -> None:
    write_json(root, GAP, {
        "lane_key": "P11-L07",
        "phase": "Phase 11",
        "survey_kind": "fixture_refresh_and_golden_output_tooling_gap",
        "roadmap_requirements": REQUIREMENTS,
        "current_packet_anchor": MANIFEST,
        "current_packet_statuses": STATUSES,
        "returned_current_head_routes": ROUTES,
        "blocked_golden_output_surfaces": [{"path": p, "reason": r} for p, r in BLOCKED.items()],
        "next_step": "refresh the older wider gpio watchdog fixture/manifest pair only after a fresh repo readback proves the wider replay or shared route has returned",
    })
    write_json(root, MANIFEST, {
        "lane_key": "P11-L04",
        "phase": "Phase 11",
        "packet_kind": "current_head_driver_docs_and_proof_packet",
        "current_head_surfaces": ROUTES + [MANIFEST],
        "gaps": [{"status": status} for status in STATUSES],
    })
    write(root, SURVEY, "\n".join(DOC_MARKERS[SURVEY]) + "\n")
    write(root, MATRIX, "\n".join(DOC_MARKERS[MATRIX]) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        validate(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def self_test() -> int:
    temp = Path(tempfile.mkdtemp(prefix="phase11-golden-output-tooling-gap-"))
    cases = 0
    try:
        fixture = temp / "fixture"
        build_fixture(fixture)
        validate(fixture)
        cases += 1

        for name, edit, fragment in (
            ("lane", lambda gap: gap.__setitem__("lane_key", "P11-L99"), "lane_key mismatch"),
            ("requirement", lambda gap: gap["roadmap_requirements"].pop(), "roadmap_requirements mismatch"),
            ("blocked", lambda gap: gap["blocked_golden_output_surfaces"].pop(), "blocked_golden_output_surfaces mismatch"),
            ("route", lambda gap: gap["returned_current_head_routes"].pop(), "returned_current_head_routes mismatch"),
        ):
            broken = temp / name
            shutil.copytree(fixture, broken)
            gap = obj(broken, GAP)
            edit(gap)
            write_json(broken, GAP, gap)
            expect_failure(broken, fragment)
            cases += 1

        broken = temp / "missing_status"
        shutil.copytree(fixture, broken)
        manifest = obj(broken, MANIFEST)
        manifest["gaps"].pop()
        write_json(broken, MANIFEST, manifest)
        expect_failure(broken, "current-head manifest missing status")
        cases += 1

        broken = temp / "promoted_blocked"
        shutil.copytree(fixture, broken)
        manifest = obj(broken, MANIFEST)
        manifest["current_head_surfaces"].append("zigux/tests/phase11_gpio_wdt_manifest.json")
        write_json(broken, MANIFEST, manifest)
        expect_failure(broken, "blocked golden-output surface is present")
        cases += 1

        broken = temp / "missing_doc_marker"
        shutil.copytree(fixture, broken)
        write(broken, MATRIX, text(broken, MATRIX).replace("hardware-backed validation", "", 1))
        expect_failure(broken, MATRIX)
        cases += 1
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    print("PHASE11_GOLDEN_OUTPUT_TOOLING_GAP_SELF_TEST=pass")
    print(f"PHASE11_GOLDEN_OUTPUT_TOOLING_GAP_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Phase 11 fixture/golden-output tooling gap survey.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        validate(Path(args.repo_root).resolve())
    except CheckError as exc:
        print(f"PHASE11_GOLDEN_OUTPUT_TOOLING_GAP=fail: {exc}")
        return 1
    print("PHASE11_GOLDEN_OUTPUT_TOOLING_GAP=pass")
    print(f"PHASE11_GOLDEN_OUTPUT_TOOLING_GAP_BLOCKED_SURFACE_COUNT={len(BLOCKED)}")
    print(f"PHASE11_GOLDEN_OUTPUT_TOOLING_GAP_RETURNED_ROUTE_COUNT={len(ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
