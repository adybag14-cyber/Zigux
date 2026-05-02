#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
MAKEFILE_PATH = "zigux/Makefile"
SURVEY_TEST_PATH = "zigux/tests/runtime_loader_non_owner_boundary_survey.zig"
TARGET_NAME = "phase9-non-owner-boundary-survey"
TARGET_COMMAND = "$(ZIG) test zigux/tests/runtime_loader_non_owner_boundary_survey.zig"

SURFACES = [
    {
        "surface": "scripts/zigux/kconfig/conf_bridge.zig",
        "owning_phase": "Phase 2",
        "boundary_kind": "config_surface_bridge",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
    {
        "surface": "scripts/zigux/kconfig/confdata_bridge.zig",
        "owning_phase": "Phase 2",
        "boundary_kind": "config_surface_bridge",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
    {
        "surface": "rust/exports.c",
        "owning_phase": "Phase 3",
        "boundary_kind": "export_boundary",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
    {
        "surface": "zigux/kernel/export_shim.zig",
        "owning_phase": "Phase 3",
        "boundary_kind": "export_boundary",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
]

REVIEW_CHECKLIST_LINE = (
    "if the change touches the shared Phase 9 runtime-loader evidence packet, do "
    "`scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, "
    "`rust/exports.c`, and `zigux/kernel/export_shim.zig` still stay explicit as "
    "Phase 2 or Phase 3 non-owner references instead of being silently counted as "
    "Phase 9 runtime evidence?"
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    survey_text = read_text(root, SURVEY_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    manifest = json.loads(read_text(root, MANIFEST_PATH))

    if not (root / SURVEY_TEST_PATH).exists():
        failures.append("survey_test:missing_file")

    manifest_surfaces = manifest.get("non_owner_surfaces")
    if not isinstance(manifest_surfaces, list):
        return ["manifest:non_owner_surfaces_missing"]

    if len(manifest_surfaces) != len(SURFACES):
        failures.append(
            f"manifest:non_owner_surface_count:{len(manifest_surfaces)}"
        )

    for index, expected in enumerate(SURFACES):
        if index >= len(manifest_surfaces):
            failures.append(f"manifest:missing_surface:{expected['surface']}")
            continue

        actual = manifest_surfaces[index]
        for field in ("surface", "owning_phase", "boundary_kind"):
            if actual.get(field) != expected[field]:
                failures.append(
                    f"manifest:{expected['surface']}:{field}:{actual.get(field)!r}"
                )
        why_non_owner = actual.get("why_non_owner")
        if not isinstance(why_non_owner, str) or expected[
            "why_non_owner_fragment"
        ] not in why_non_owner:
            failures.append(f"manifest:{expected['surface']}:why_non_owner")

        if expected["surface"] not in survey_text:
            failures.append(f"survey:{expected['surface']}")

    if REVIEW_CHECKLIST_LINE not in review_checklist:
        failures.append("review_checklist:four_surface_non_owner_line")

    if TARGET_NAME not in makefile_text:
        failures.append("makefile:non_owner_boundary_target_missing")
    if TARGET_COMMAND not in makefile_text:
        failures.append("makefile:non_owner_boundary_target_command_missing")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)

    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Loader Gap Survey",
                "scripts/zigux/kconfig/conf_bridge.zig",
                "scripts/zigux/kconfig/confdata_bridge.zig",
                "rust/exports.c",
                "zigux/kernel/export_shim.zig",
                "boundary references instead of Phase 9 runtime evidence",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / REVIEW_CHECKLIST_PATH).write_text(
        "# Zigux Review Checklist\n\n- " + REVIEW_CHECKLIST_LINE + "\n",
        encoding="utf-8",
    )
    (root / MAKEFILE_PATH).write_text(
        "\n".join(
            [
                "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-non-owner-boundary-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
                "",
                "phase9-non-owner-boundary-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_non_owner_boundary_survey.zig",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / MANIFEST_PATH).writeText if False else None