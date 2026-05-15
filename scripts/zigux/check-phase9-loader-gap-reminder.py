#!/usr/bin/env python3
"""Guard the Phase 9 shared loader-gap packet around its remaining checklist gap.

This checker keeps the current shared survey and manifest honest while the
Phase 9 review checklist still lacks the cross-phase non-owner reminder for the
older Phase 2 config bridges and Phase 3 export-boundary references.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_SURVEY = Path("Documentation/zigux/phase9-runtime-loader-gap-survey.md")
DEFAULT_MANIFEST = Path("zigux/tests/runtime_loader_gap_manifest.json")

REQUIRED_SURVEY_MARKERS = (
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "rust/exports.c",
    "zigux/kernel/export_shim.zig",
    ".modinfo",
    "MODULE_ALIAS()",
    "modules.alias",
    "modules.order",
    "modules.builtin",
    "depmod",
)

REQUIRED_GAP = {
    "id": "runtime-loader-checklist-cross-phase-non-owner-reminder",
    "status": "review_only_gap",
    "kind": "shared_reminder_truthfulness",
    "zigux_destination": "Documentation/zigux/review-checklist.md",
}


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read {path}: {exc}") from exc


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"failed to read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"failed to parse {path}: {exc}") from exc


def require_markers(survey_text: str) -> None:
    missing = [marker for marker in REQUIRED_SURVEY_MARKERS if marker not in survey_text]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"survey missing required Phase 9 gap markers: {joined}")


def require_manifest_gap(manifest: dict) -> None:
    repo_reality = manifest.get("current_repo_reality", {})
    if repo_reality.get("review_checklist_cross_phase_non_owner_boundary_present") is not False:
        raise SystemExit(
            "manifest no longer records the review checklist cross-phase non-owner "
            "boundary as absent"
        )

    gaps = manifest.get("gaps", [])
    matching_gap = None
    for gap in gaps:
        if gap.get("id") == REQUIRED_GAP["id"]:
            matching_gap = gap
            break
    if matching_gap is None:
        raise SystemExit("manifest is missing the Phase 9 checklist reminder gap entry")

    for key, expected in REQUIRED_GAP.items():
        actual = matching_gap.get(key)
        if actual != expected:
            raise SystemExit(
                f"manifest gap field {key!r} drifted: expected {expected!r}, got {actual!r}"
            )


def run_check(survey_path: Path, manifest_path: Path) -> None:
    require_markers(load_text(survey_path))
    require_manifest_gap(load_manifest(manifest_path))
    print("PHASE9_LOADER_GAP_REMINDER=pass")


def run_self_test() -> None:
    good_survey = """
Fresh repo-first inspection now also shows `Documentation/zigux/review-checklist.md`
does not yet restate that `scripts/zigux/kconfig/conf_bridge.zig` and
`scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge
references while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3
export-boundary references, and the blocked `.modinfo`, `MODULE_ALIAS()`,
`modules.alias`, `modules.order`, `modules.builtin`, and `depmod` publication
boundary still stays explicit.
""".strip()

    good_manifest = {
        "current_repo_reality": {
            "review_checklist_cross_phase_non_owner_boundary_present": False,
        },
        "gaps": [REQUIRED_GAP],
    }

    with tempfile.TemporaryDirectory(prefix="phase9-gap-reminder-") as tmp:
        tmp_path = Path(tmp)
        survey_path = tmp_path / "survey.md"
        manifest_path = tmp_path / "manifest.json"
        survey_path.write_text(good_survey, encoding="utf-8")
        manifest_path.write_text(json.dumps(good_manifest, indent=2), encoding="utf-8")
        run_check(survey_path, manifest_path)

        survey_path.write_text(good_survey.replace("rust/exports.c", ""), encoding="utf-8")
        try:
            run_check(survey_path, manifest_path)
        except SystemExit as exc:
            if "rust/exports.c" not in str(exc):
                raise
        else:
            raise SystemExit("self-test expected survey marker failure")

        survey_path.write_text(good_survey, encoding="utf-8")
        broken_manifest = {
            "current_repo_reality": {
                "review_checklist_cross_phase_non_owner_boundary_present": True,
            },
            "gaps": [REQUIRED_GAP],
        }
        manifest_path.write_text(json.dumps(broken_manifest, indent=2), encoding="utf-8")
        try:
            run_check(survey_path, manifest_path)
        except SystemExit as exc:
            if "no longer records" not in str(exc):
                raise
        else:
            raise SystemExit("self-test expected manifest drift failure")

    print("PHASE9_LOADER_GAP_REMINDER_SELF_TEST=pass")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Phase 9 shared loader-gap survey and manifest aligned around "
            "the remaining checklist-side cross-phase non-owner reminder."
        )
    )
    parser.add_argument("--survey", type=Path, default=DEFAULT_SURVEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    run_check(args.survey, args.manifest)


if __name__ == "__main__":
    main()
