#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

EXPECTED_PHASE = "Phase 8"
EXPECTED_SURFACES = [
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/help.zig",
]
EXPECTED_EXEC_ENV_NAMES = ["PERF_EXEC_PATH", "PATH"]
EXPECTED_TERMINAL_ENV_NAMES = ["LINES", "COLUMNS"]

SURVEY_MARKERS = [
    "The roadmap's first command and environment plumbing surfaces also sit outside this runtime lane.",
    "Those controls belong to `Phase 8`",
    "`tools/lib/subcmd/exec-cmd.zig`",
    "`tools/lib/subcmd/help.zig`",
    "The shared request contract now records an optional shared `command_name` field",
    "no broader shared runtime command or environment control surface yet records argv policy or environment-derived activation cues",
]

SUBSTRATE_MARKERS = [
    "The shared request keeps `command_name` reviewable as a narrow handoff clue",
    "Any future non-null `command_name` must keep a truthful Phase 8 owner such as `tools/lib/subcmd/exec-cmd.zig` and `ExtractArgv0Result.command_name`",
    "This slice still does not claim `Config.exec_path_env`, `PERF_EXEC_PATH`, `PATH`, or other environment-derived activation handling as runtime-loader behavior.",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def require_substrings(text: str, label: str, markers: list[str]) -> list[str]:
    errors: list[str] = []
    for marker in markers:
        if marker not in text:
            errors.append(f"{label}:missing_marker:{marker}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_text = read_text(root, "zigux/tests/runtime_loader_gap_manifest.json")
    survey_text = read_text(root, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")
    substrate_text = read_text(root, "Documentation/zigux/phase9-runtime-loader-substrate-plan.md")

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return ["manifest:json_decode_failed"]

    if manifest.get("roadmap_command_environment_phase") != EXPECTED_PHASE:
        errors.append("manifest:unexpected_command_environment_phase")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        errors.append("manifest:missing_survey_summary")
    elif summary.get("shared_command_environment_control_present") is not False:
        errors.append("manifest:shared_command_environment_control_present_should_be_false")

    surfaces = manifest.get("phase8_command_environment_surfaces")
    if surfaces != EXPECTED_SURFACES:
        errors.append("manifest:phase8_command_environment_surfaces_mismatch")

    markers = manifest.get("phase8_control_surface_markers")
    if not isinstance(markers, dict):
        errors.append("manifest:missing_phase8_control_surface_markers")
    else:
        if markers.get("exec_cmd_surface") != EXPECTED_SURFACES[0]:
            errors.append("manifest:exec_cmd_surface_mismatch")
        if markers.get("help_surface") != EXPECTED_SURFACES[1]:
            errors.append("manifest:help_surface_mismatch")
        if markers.get("command_name_field") != "ExtractArgv0Result.command_name":
            errors.append("manifest:command_name_field_mismatch")
        if markers.get("exec_path_env_field") != "Config.exec_path_env":
            errors.append("manifest:exec_path_env_field_mismatch")
        if markers.get("shared_runtime_loader_field") != "shared command_name field":
            errors.append("manifest:shared_runtime_loader_field_mismatch")
        if markers.get("exec_env_names") != EXPECTED_EXEC_ENV_NAMES:
            errors.append("manifest:exec_env_names_mismatch")
        if markers.get("terminal_env_names") != EXPECTED_TERMINAL_ENV_NAMES:
            errors.append("manifest:terminal_env_names_mismatch")

    errors.extend(require_substrings(survey_text, "gap_survey", SURVEY_MARKERS))
    errors.extend(require_substrings(substrate_text, "substrate_plan", SUBSTRATE_MARKERS))

    return errors


def run_self_test() -> int:
    baseline_manifest = json.dumps(
        {
            "roadmap_command_environment_phase": "Phase 8",
            "survey_summary": {
                "shared_command_environment_control_present": False,
            },
            "phase8_command_environment_surfaces": [
                "tools/lib/subcmd/exec-cmd.zig",
                "tools/lib/subcmd/help.zig",
            ],
            "phase8_control_surface_markers": {
                "exec_cmd_surface": "tools/lib/subcmd/exec-cmd.zig",
                "help_surface": "tools/lib/subcmd/help.zig",
                "command_name_field": "ExtractArgv0Result.command_name",
                "exec_path_env_field": "Config.exec_path_env",
                "shared_runtime_loader_field": "shared command_name field",
                "exec_env_names": ["PERF_EXEC_PATH", "PATH"],
                "terminal_env_names": ["LINES", "COLUMNS"],
            },
        },
        indent=2,
    )
    baseline_survey = "\n".join(
        [
            "# Gap Survey",
            "The roadmap's first command and environment plumbing surfaces also sit outside this runtime lane.",
            "Those controls belong to `Phase 8`.",
            "The live repo now lands them as `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig`.",
            "The shared request contract now records an optional shared `command_name` field, but no broader shared runtime command or environment control surface yet records argv policy or environment-derived activation cues.",
            "",
        ]
    )
    baseline_substrate = "\n".join(
        [
            "# Substrate Plan",
            "The shared request keeps `command_name` reviewable as a narrow handoff clue.",
            "Any future non-null `command_name` must keep a truthful Phase 8 owner such as `tools/lib/subcmd/exec-cmd.zig` and `ExtractArgv0Result.command_name`.",
            "This slice still does not claim `Config.exec_path_env`, `PERF_EXEC_PATH`, `PATH`, or other environment-derived activation handling as runtime-loader behavior.",
            "",
        ]
    )

    with tempfile.TemporaryDirectory(prefix="phase9_runtime_loader_command_env_") as tmp_dir:
        root = Path(tmp_dir)
        (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)

        manifest_path = root / "zigux/tests/runtime_loader_gap_manifest.json"
        survey_path = root / "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
        substrate_path = root / "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"

        manifest_path.write_text(baseline_manifest, encoding="utf-8")
        survey_path.write_text(baseline_survey, encoding="utf-8")
        substrate_path.write_text(baseline_substrate, encoding="utf-8")

        baseline_errors = validate(root)
        if baseline_errors:
            raise SystemExit(
                "phase9-runtime-loader-command-environment:self-test:baseline_failed:"
                + ",".join(baseline_errors)
            )

        manifest_path.write_text(
            baseline_manifest.replace('"Phase 8"', '"Phase 7"', 1),
            encoding="utf-8",
        )
        manifest_errors = validate(root)
        if "manifest:unexpected_command_environment_phase" not in manifest_errors:
            raise SystemExit(
                "phase9-runtime-loader-command-environment:self-test:expected_phase_failure:"
                + ",".join(manifest_errors or ["none"])
            )
        manifest_path.write_text(baseline_manifest, encoding="utf-8")

        survey_path.write_text(
            baseline_survey.replace("Those controls belong to `Phase 8`.", "", 1),
            encoding="utf-8",
        )
        survey_errors = validate(root)
        if not any(error.startswith("gap_survey:missing_marker:Those controls belong to `Phase 8`") for error in survey_errors):
            raise SystemExit(
                "phase9-runtime-loader-command-environment:self-test:expected_survey_marker_failure:"
                + ",".join(survey_errors or ["none"])
            )
        survey_path.write_text(baseline_survey, encoding="utf-8")

        substrate_path.write_text(
            baseline_substrate.replace("`Config.exec_path_env`, ", "", 1),
            encoding="utf-8",
        )
        substrate_errors = validate(root)
        if not any(error.startswith("substrate_plan:missing_marker:") for error in substrate_errors):
            raise SystemExit(
                "phase9-runtime-loader-command-environment:self-test:expected_substrate_marker_failure:"
                + ",".join(substrate_errors or ["none"])
            )

    print("PHASE9_RUNTIME_LOADER_COMMAND_ENVIRONMENT_SELF_TEST=pass")
    print("PHASE9_RUNTIME_LOADER_COMMAND_ENVIRONMENT_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 8 command/environment ownership markers in the shared Phase 9 runtime-loader packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root of the Zigux checkout to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in validator self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        print("PHASE9_RUNTIME_LOADER_COMMAND_ENVIRONMENT=fail")
        print("PHASE9_RUNTIME_LOADER_COMMAND_ENVIRONMENT_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE9_RUNTIME_LOADER_COMMAND_ENVIRONMENT_ERRORS_END")
        return 1

    print("PHASE9_RUNTIME_LOADER_COMMAND_ENVIRONMENT=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
