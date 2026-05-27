#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the current Phase 14 rollback-threshold packet.

This checker stays inside the rollback-automation lane. It validates that the
shared smoke reminder surfaces still agree on the current study-only rollback
contract, on the returned route checker and tests-root reminder checker, on the
returned rollback-threshold checker, dedicated skbuff stay-in-C guard,
dedicated skbuff compile-route guard, dedicated ring-buffer compile-route
guard, dedicated RCU compile-route guard, dedicated RCU rollback guard,
ring-buffer survey companion, dedicated RCU survey companion, and shared smoke
manifest, and on the current repo-reality split where the Makefile is readable,
ships `phase14-validate`, and still does not ship the broader `phase14-smoke`,
`phase14-test`, or `phase14` wrapper targets.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"
ROLLBACK_OWNER = "Repo Tooling Pod"
STATUS_BUCKET = "study_only"

SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

ROLLBACK_THRESHOLD_MARKER = (
    "  * rollback threshold: `0` tolerated same-packet drifts across the "
    "recovered documentation packet, the directly readable shared-smoke route "
    "checker, the directly readable tests-root reminder checker, the directly "
    "readable validator path, the directly readable rollback-threshold "
    "sequencing checker, the directly readable dedicated skbuff stay-in-C "
    "guard, the directly readable dedicated skbuff compile-route guard, the "
    "directly readable dedicated ring-buffer compile-route guard, the "
    "directly readable dedicated RCU rollback guard, the readable current "
    "Makefile body, the directly readable release-boundary exact-count guard, "
    "the directly readable workqueue boundary shard, the directly readable "
    "ring-buffer survey companion, the directly readable dedicated RCU survey "
    "companion, the directly readable shared smoke manifest, and the "
    "still-missing broader wrapper-backed rerun routes`"
)
ROLLBACK_FALLBACK_MARKER = (
    "  * fallback path: keep this shared smoke lane aligned with the current "
    "gap notes until the broader shared reminder packet stops treating the "
    "current Makefile body as if it still shipped `phase14-smoke`, "
    "`phase14-test`, and `phase14`, and until the build-side and broader "
    "executable packet members return through exact current-`master` readback; "
    "once they do, rerun the packet-local commands below before restoring any "
    "stronger validator-first claim"
)
ROLLBACK_TRIGGER_MARKERS = [
    "    * recovered documentation packet drift",
    "    * route-checker-versus-reminder-surface drift",
    "    * tests-root-checker-versus-reminder-surface drift",
    "    * validator-versus-reminder-surface drift",
    "    * rollback-threshold-sequencing drift",
    "    * dedicated-skbuff-stay-in-c-guard drift",
    "    * dedicated-skbuff-compile-route-guard drift",
    "    * dedicated-ring-buffer-compile-route-guard drift",
    "    * dedicated-rcu-rollback-guard drift",
    "    * workqueue-boundary-shard drift",
    "    * ring-buffer-survey drift",
    "    * dedicated-rcu-survey drift",
    "    * wrapper-route drift",
    "    * build-side exact-readback-gap drift",
    "    * broader executable-layer exact-readback-gap drift",
    "    * attached-toolchain guidance drift inside the shared smoke note",
]
HISTORICAL_ROUTE_VOCABULARY_MARKERS = [
    "`phase14-smoke`",
    "`phase14-test`",
    "`phase14`",
]
MAKEFILE_ROUTE_ABSENCE_MARKER = (
    "`phase14-smoke`, `phase14-test`, or `phase14` targets"
)
RETURNED_PHASE4_ROUTE_MARKERS = [
    "`phase4-validate`",
    "`phase4-test`",
    "`phase4`",
]
PRODUCTIZATION_GAP_MARKERS = [
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
    "The higher-value same-lane task is reminder-surface truthfulness:",
    "the directly readable shared-smoke route checker",
    "the directly readable tests-root reminder checker",
    "the directly readable validator surface",
    "the directly readable release-boundary exact-count guard",
    "the directly readable shared smoke manifest",
    "the directly readable dedicated ring-buffer compile-route guard",
    "the current Makefile posture",
]
CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet",
    "keep `zigux/Makefile` framed as readable current evidence",
    "`phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
]
MAKEFILE_PRESENT_ROUTE_MARKERS = [
    "phase3-validate:",
    "phase4-validate:",
    "phase4-test:",
    "phase4: phase4-validate phase4-test",
    "phase6-base64-test:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-smoke:",
    "phase14-validate:",
]
MAKEFILE_ABSENT_ROUTE_MARKERS = [
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
]
REQUIRED_MANIFEST_VALUES = {
    ("smoke_commands",): ["make -C zigux phase14-validate"],
    ("smoke_shard_commands",): [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
    ],
}
REQUIRED_MANIFEST_SHARED_SMOKE_SURFACES = [
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-rcu-compile-route.py",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-productization-gap-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "zigux/Makefile",
]
REQUIRED_SURVEY_SUMMARY_FLAGS = {
    "phase14_validate_runs_rollback_threshold_sequencing": True,
    "phase14_validate_runs_rcu_compile_route_checker": True,
    "review_checklist_has_rollback_threshold_prompt": True,
    "smoke_note_records_rollback_threshold": True,
    "scripts_readme_records_rollback_threshold": True,
    "phase14_make_target_present": True,
    "phase14_make_smoke_target_present": False,
    "shared_manifest_records_rcu_compile_route_checker": True,
}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def require_present(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing marker in {rel.as_posix()}: {marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"unexpected stale marker in {rel.as_posix()}: {marker}")


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_manifest_values(errors: list[str], manifest: object) -> None:
    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            errors.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(
                "manifest_value_mismatch:"
                f"{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )


def require_manifest_shared_smoke_surfaces(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
    if not isinstance(shared_smoke_surfaces, list):
        errors.append("missing_manifest_key:shared_smoke_surfaces")
        return

    for surface in REQUIRED_MANIFEST_SHARED_SMOKE_SURFACES:
        if surface not in shared_smoke_surfaces:
            errors.append(f"missing_shared_smoke_surface:{surface}")


def require_manifest_survey_summary(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        errors.append("missing_manifest_key:survey_summary")
        return

    for key, expected in REQUIRED_SURVEY_SUMMARY_FLAGS.items():
        actual = survey_summary.get(key)
        if actual != expected:
            errors.append(
                "survey_summary_mismatch:"
                f"{key}:expected={expected!r}:actual={actual!r}"
            )


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    required_paths = [
        SMOKE_NOTE_PATH,
        RELEASE_BOUNDARY_PATH,
        PRODUCTIZATION_GAP_PATH,
        CHECKLIST_PATH,
        MAKEFILE_PATH,
        MANIFEST_PATH,
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    require_present(
        errors,
        SMOKE_NOTE_PATH,
        smoke_note,
        [
            "  * `PHASE14_STAY_IN_C_BOUNDARY=explicit`",
            "  * `PHASE14_EXECUTABLE_PACKET_READBACK=partial`",
            "  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
            f"  * rollback owner: `{ROLLBACK_OWNER}`",
            f"  * status bucket: `{STATUS_BUCKET}`",
            ROLLBACK_THRESHOLD_MARKER,
            ROLLBACK_FALLBACK_MARKER,
            "  * automatic return-to-blocked triggers:",
            *ROLLBACK_TRIGGER_MARKERS,
            "  * packet-local command posture preserved by this note:",
            "no current attached-toolchain `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux phase14` fallback is usable from this note",
            "keep those older wrapper names recorded only as historical packet vocabulary",
            *HISTORICAL_ROUTE_VOCABULARY_MARKERS,
            MAKEFILE_ROUTE_ABSENCE_MARKER,
            *RETURNED_PHASE4_ROUTE_MARKERS,
            "same-lane follow-through should only touch the smallest shared reminder surface that drifts against this returned Makefile split",
        ],
    )

    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    require_present(
        errors,
        RELEASE_BOUNDARY_PATH,
        release_boundary,
        [
            MAKEFILE_ROUTE_ABSENCE_MARKER,
            *RETURNED_PHASE4_ROUTE_MARKERS,
            "- current shared-smoke route: `make -C zigux phase14-validate`",
            "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
            "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
        ],
    )

    productization_gap = read_text(root, PRODUCTIZATION_GAP_PATH)
    require_present(
        errors,
        PRODUCTIZATION_GAP_PATH,
        productization_gap,
        PRODUCTIZATION_GAP_MARKERS,
    )

    checklist = read_text(root, CHECKLIST_PATH)
    require_present(errors, CHECKLIST_PATH, checklist, CHECKLIST_MARKERS)

    makefile = read_text(root, MAKEFILE_PATH)
    require_present(errors, MAKEFILE_PATH, makefile, MAKEFILE_PRESENT_ROUTE_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile, MAKEFILE_ABSENT_ROUTE_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    require_manifest_values(errors, manifest)
    require_manifest_shared_smoke_surfaces(errors, manifest)
    require_manifest_survey_summary(errors, manifest)

    return errors


def fixture_smoke_note() -> str:
    return "\n".join(
        [
            "# Phase 14 End-to-End Smoke Survey",
            "  * `PHASE14_EXECUTABLE_PACKET_READBACK=partial`",
            "  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
            "  * `PHASE14_STAY_IN_C_BOUNDARY=explicit`",
            f"  * rollback owner: `{ROLLBACK_OWNER}`",
            f"  * status bucket: `{STATUS_BUCKET}`",
            ROLLBACK_THRESHOLD_MARKER,
            ROLLBACK_FALLBACK_MARKER,
            "  * automatic return-to-blocked triggers:",
            *ROLLBACK_TRIGGER_MARKERS,
            "  * packet-local command posture preserved by this note:",
            (
                "    * the current readable route layer still stops at `make -C zigux "
                "phase14-validate`; no current attached-toolchain `make -C zigux "
                "phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux "
                "phase14` fallback is usable from this note because the readable "
                "`zigux/Makefile` body still omits those targets"
            ),
            (
                "    * `zigux/Makefile` is directly readable again through the current "
                "contents path, and its live body now exposes the shipped Phase 2 "
                "toolchain and kbuild routes together with the bounded `phase3-validate`, "
                "`phase3`, `phase4-validate`, `phase4-test`, `phase4`, "
                "`phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, "
                "`phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, "
                "`phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, "
                "`phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, "
                "`phase12-smoke`, `phase12-test`, `phase12`, and `phase14-validate`, but "
                "no `phase14-smoke`, `phase14-test`, or `phase14` targets"
            ),
            (
                "    * keep those older wrapper names recorded only as historical packet "
                "vocabulary until the same exact readback mode restores the broader "
                "Phase 14 Makefile routes on current `master`"
            ),
            (
                "    * that means later same-lane follow-through should only touch the "
                "smallest shared reminder surface that drifts against this returned "
                "Makefile split"
            ),
            (
                "    * that means later same-lane follow-through should only touch the "
                "smallest shared reminder surface that drifts against this returned "
                "Makefile split, not default back to a validator-local exact-line sync "
                "or an already-aligned tests-root rewrite"
            ),
            "",
        ]
    )


def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            "- current Makefile posture: `zigux/Makefile` is readable again on current `master`, and its live body now exposes the shipped Phase 2 toolchain and kbuild routes together with the bounded `phase3-validate`, `phase3`, `phase4-validate`, `phase4-test`, `phase4`, `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, `phase12-smoke`, `phase12-test`, `phase12`, and `phase14-validate` routes, and no `phase14-smoke`, `phase14-test`, or `phase14` targets",
            "- current shared-smoke route: `make -C zigux phase14-validate`",
            "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
            "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
            "",
        ]
    )


def fixture_productization_gap() -> str:
    return "\n".join(
        [
            "# Phase 14 Productization Gap Survey",
            "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
            "The higher-value same-lane task is reminder-surface truthfulness: keep shared notes aligned with the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable validator surface, the directly readable release-boundary exact-count guard, the directly readable shared smoke manifest, the directly readable dedicated ring-buffer compile-route guard, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships the old `phase14-*` routes.",
            "",
        ]
    )


def fixture_checklist() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "if the change touches the shared Phase 14 smoke packet",
            "keep `zigux/Makefile` framed as readable current evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes while `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
            "",
        ]
    )


def fixture_makefile() -> str:
    return "\n".join(
        [
            "phase3-validate:",
            "phase4-validate:",
            "phase4-test:",
            "phase4: phase4-validate phase4-test",
            "phase6-base64-test:",
            "phase8-validate:",
            "phase10-validate:",
            "phase12-smoke:",
            "phase14-validate:",
            "",
        ]
    )


def fixture_manifest() -> str:
    payload = {
        "shared_smoke_surfaces": REQUIRED_MANIFEST_SHARED_SMOKE_SURFACES,
        "smoke_commands": ["make -C zigux phase14-validate"],
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "survey_summary": {
            "phase14_validate_runs_rollback_threshold_sequencing": True,
            "phase14_validate_runs_rcu_compile_route_checker": True,
            "review_checklist_has_rollback_threshold_prompt": True,
            "smoke_note_records_rollback_threshold": True,
            "scripts_readme_records_rollback_threshold": True,
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "shared_manifest_records_rcu_compile_route_checker": True,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def write_manifest_payload(root: Path, payload: object) -> None:
    write(root, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(root, CHECKLIST_PATH, fixture_checklist())
        write(root, MAKEFILE_PATH, fixture_makefile())
        write(root, MANIFEST_PATH, fixture_manifest())

        if errors := check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        for trigger, fragment, label in [
            ("    * route-checker-versus-reminder-surface drift\n", "route-checker-versus-reminder-surface drift", "route-checker trigger drift"),
            ("    * tests-root-checker-versus-reminder-surface drift\n", "tests-root-checker-versus-reminder-surface drift", "tests-root trigger drift"),
            ("    * rollback-threshold-sequencing drift\n", "rollback-threshold-sequencing drift", "rollback-threshold trigger drift"),
            ("    * dedicated-skbuff-stay-in-c-guard drift\n", "dedicated-skbuff-stay-in-c-guard drift", "dedicated skbuff stay-in-C trigger drift"),
            ("    * dedicated-skbuff-compile-route-guard drift\n", "dedicated-skbuff-compile-route-guard drift", "dedicated skbuff compile-route trigger drift"),
            ("    * dedicated-ring-buffer-compile-route-guard drift\n", "dedicated-ring-buffer-compile-route-guard drift", "dedicated ring-buffer compile-route trigger drift"),
            ("    * dedicated-rcu-rollback-guard drift\n", "dedicated-rcu-rollback-guard drift", "dedicated RCU rollback trigger drift"),
            ("    * workqueue-boundary-shard drift\n", "workqueue-boundary-shard drift", "workqueue boundary trigger drift"),
            ("    * ring-buffer-survey drift\n", "ring-buffer-survey drift", "ring-buffer trigger drift"),
            ("    * dedicated-rcu-survey drift\n", "dedicated-rcu-survey drift", "dedicated RCU survey trigger drift"),
            ("    * build-side exact-readback-gap drift\n", "build-side exact-readback-gap drift", "build-side exact-readback gap trigger drift"),
            ("    * wrapper-route drift\n", "wrapper-route drift", "trigger-catalog drift"),
            ("    * attached-toolchain guidance drift inside the shared smoke note\n", "attached-toolchain guidance drift inside the shared smoke note", "attached-toolchain guidance trigger drift"),
        ]:
            write(root, SMOKE_NOTE_PATH, fixture_smoke_note().replace(trigger, "", 1))
            if not any(fragment in error for error in check(root)):
                print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
                print(f"expected {label} to fail")
                return 1
            write(root, SMOKE_NOTE_PATH, fixture_smoke_note())

        write(
            root,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`\n",
                "",
                1,
            ),
        )
        if not any("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected attached-toolchain guidance marker drift to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, MAKEFILE_PATH, fixture_makefile().replace("phase14-validate:\n", "", 1))
        if not any("phase14-validate:" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected returned phase14 validate route to fail")
            return 1

        write(root, MAKEFILE_PATH, fixture_makefile())
        write(
            root,
            RELEASE_BOUNDARY_PATH,
            fixture_release_boundary().replace(MAKEFILE_ROUTE_ABSENCE_MARKER, "missing marker", 1),
        )
        if not any(MAKEFILE_ROUTE_ABSENCE_MARKER in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected release-boundary makefile posture drift to fail")
            return 1

        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
        write(
            root,
            CHECKLIST_PATH,
            fixture_checklist().replace(
                "`phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
                "",
                1,
            ),
        )
        if not any("packet-local or repo-reality-gap vocabulary" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected checklist route-vocabulary drift to fail")
            return 1

        write(root, CHECKLIST_PATH, fixture_checklist())
        write(
            root,
            PRODUCTIZATION_GAP_PATH,
            fixture_productization_gap().replace(
                "the directly readable shared smoke manifest",
                "missing shared smoke manifest",
                1,
            ),
        )
        if not any("the directly readable shared smoke manifest" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected productization-gap shared-manifest drift to fail")
            return 1

        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(
            root,
            PRODUCTIZATION_GAP_PATH,
            fixture_productization_gap().replace(
                "the directly readable dedicated ring-buffer compile-route guard",
                "missing ring-buffer compile-route guard",
                1,
            ),
        )
        if not any("the directly readable dedicated ring-buffer compile-route guard" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected productization-gap ring-buffer compile-route drift to fail")
            return 1

        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(
            root,
            MAKEFILE_PATH,
            fixture_makefile() + "phase14-smoke:\n",
        )
        if not any("unexpected stale marker" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected stale phase14 smoke route to fail")
            return 1

        write(root, MAKEFILE_PATH, fixture_makefile())
        manifest = json.loads(fixture_manifest())
        manifest["shared_smoke_surfaces"].remove(
            "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
        )
        write_manifest_payload(root, manifest)
        if "missing_shared_smoke_surface:scripts/zigux/check-phase14-rollback-threshold-sequencing.py" not in check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected manifest shared-smoke surface drift to fail")
            return 1

        write(root, MANIFEST_PATH, fixture_manifest())
        manifest = json.loads(fixture_manifest())
        manifest["shared_smoke_surfaces"].remove(
            "scripts/zigux/check-phase14-rcu-compile-route.py"
        )
        write_manifest_payload(root, manifest)
        if "missing_shared_smoke_surface:scripts/zigux/check-phase14-rcu-compile-route.py" not in check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected manifest RCU compile-route surface drift to fail")
            return 1

        write(root, MANIFEST_PATH, fixture_manifest())
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_rollback_threshold_sequencing"] = False
        write_manifest_payload(root, manifest)
        if not any(
            error.startswith("survey_summary_mismatch:phase14_validate_runs_rollback_threshold_sequencing:")
            for error in check(root)
        ):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected manifest survey-summary drift to fail")
            return 1

        write(root, MANIFEST_PATH, fixture_manifest())
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_rcu_compile_route_checker"] = False
        write_manifest_payload(root, manifest)
        if not any(
            error.startswith("survey_summary_mismatch:phase14_validate_runs_rcu_compile_route_checker:")
            for error in check(root)
        ):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected manifest RCU compile-route survey-summary drift to fail")
            return 1

        write(root, MANIFEST_PATH, fixture_manifest())
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["shared_manifest_records_rcu_compile_route_checker"] = False
        write_manifest_payload(root, manifest)
        if not any(
            error.startswith("survey_summary_mismatch:shared_manifest_records_rcu_compile_route_checker:")
            for error in check(root)
        ):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected manifest shared-manifest RCU compile-route summary drift to fail")
            return 1

        write(root, MANIFEST_PATH, fixture_manifest())
        manifest = json.loads(fixture_manifest())
        manifest["smoke_commands"] = ["make -C zigux phase14-test"]
        write_manifest_payload(root, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:smoke_commands:")
            for error in check(root)
        ):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected manifest smoke-command drift to fail")
            return 1

    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass")
    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST_CASE_COUNT=26")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(Path.cwd())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 rollback-threshold sequencing packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
