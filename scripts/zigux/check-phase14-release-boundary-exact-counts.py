#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the current Phase 14 release-boundary count posture.

This guard keeps the release-boundary packet honest around the exact manifest-
backed compile-shard counts, the dedicated compile-shard matrix survey, the
returned manifest posture in the shared smoke survey, the dedicated validator-side
skbuff stay-in-C and compile-route packets, the dedicated ring-buffer compile-route
packet, the dedicated RCU compile-route and rollback packets, and the still-unreadable
build-side or broader executable-layer gap while cross-reading the shared smoke
survey markers that define the current Phase 14 route split.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
COMPILE_SHARD_MATRIX_SURVEY_PATH = Path(
    "Documentation/zigux/phase14-compile-shard-matrix-survey.md"
)
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
SKBUFF_COMPILE_ROUTE_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-skbuff-compile-route.py"
)
RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-ring-buffer-compile-route.py"
)
RCU_COMPILE_ROUTE_CHECKER_PATH = Path("scripts/zigux/check-phase14-rcu-compile-route.py")

EXACT_COUNT_MARKERS = [
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
]

EXECUTABLE_GAP_MARKERS = [
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
]

RELEASE_BOUNDARY_TEXT_MARKERS = [
    "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the current shared reminder packet",
    "- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now returns through the current contents path and publishes the exact six-row compile-shard matrix with one `focused_and_full_bundle` shard and five `full_bundle_only` shards",
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
]

COMPILE_SHARD_MATRIX_MARKERS = [
    *EXACT_COUNT_MARKERS,
    "- shared gate: `make -C zigux phase14-validate`",
    "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    "- machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "- checker: `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "- skbuff compile-route checker: `scripts/zigux/check-phase14-skbuff-compile-route.py`",
    "- ring-buffer compile-route checker: `scripts/zigux/check-phase14-ring-buffer-compile-route.py`",
    "- rcu compile-route checker: `scripts/zigux/check-phase14-rcu-compile-route.py`",
    "- shared survey shard: `phase14-end-to-end-smoke-tests` (`focused_and_full_bundle`)",
    "- `scripts/zigux/check-phase14-ring-buffer-compile-route.py` now fail-closes on the shared-manifest row together with the note's returned ring-buffer-local replay wording even while the lane remains study-only and maintenance-scoped",
    "- the manifest-backed compile row is present, and `scripts/zigux/check-phase14-rcu-compile-route.py` now fail-closes on the shared-manifest row, the dedicated build-shard wiring, and the survey note's public-fallback replay wording while the anchor stays freeze-in-C initially",
]

SURVEY_EXACT_LINE_SNIPPETS = [
    "  * directly readable current-`master` companion surfaces in this lane's current evidence split:",
    "    * `scripts/zigux/check-phase14-shared-smoke-route.py` through the current contents path",
    "    * `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` through the current contents path",
    "    * `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` through the current contents path",
    "    * `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path",
    "  * exact-readback gaps that still belong to this shared note:",
    "    * `zigux/tests/phase14_build.zig`",
    "    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "    * broad reminder text should therefore frame that build-side and broader executable layer as exact-readback gaps rather than as directly recovered shared-smoke proof",
    "    * the current readable route layer still stops at `make -C zigux phase14-validate`; no current attached-toolchain `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux phase14` fallback is usable from this note because the readable `zigux/Makefile` body still omits those targets",
]

REQUIRED_COMPILE_SHARD_LABELS = {
    "phase14-workqueue-bridge-tests": "full_bundle_only",
    "phase14-workqueue-reviewability-tests": "full_bundle_only",
    "phase14-skbuff-bridge-tests": "full_bundle_only",
    "phase14-ring-buffer-survey-tests": "full_bundle_only",
    "phase14-rcu-tree-survey-tests": "full_bundle_only",
    "phase14-end-to-end-smoke-tests": "focused_and_full_bundle",
}

REQUIRED_MANIFEST_VALUES = {
    ("smoke_commands",): ["make -C zigux phase14-validate"],
    ("smoke_shard_commands",): [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
    ],
    ("survey_summary", "phase14_make_target_present"): True,
    ("survey_summary", "phase14_make_smoke_target_present"): False,
    ("survey_summary", "workflow_runs_phase14_validate"): True,
    ("survey_summary", "workflow_runs_phase14_build"): False,
    ("survey_summary", "workflow_runs_phase14_smoke_shard"): False,
    ("survey_summary", "phase14_validate_runs_skbuff_stay_in_c_guardrail"): True,
    ("survey_summary", "phase14_validate_runs_skbuff_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_skbuff_compile_route_checker"): True,
    ("survey_summary", "phase14_validate_runs_rcu_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_rcu_compile_route_checker"): True,
    ("survey_summary", "phase14_validate_runs_rcu_rollback_guardrail"): True,
}


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_exact_once(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")
        elif count != 1:
            errors.append(f"duplicate_marker:{rel.as_posix()}:{marker}:{count}")


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


def require_compile_shards(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return
    compile_shards = manifest.get("compile_shards")
    if not isinstance(compile_shards, list):
        errors.append("missing_manifest_key:compile_shards")
        return

    if len(compile_shards) != len(REQUIRED_COMPILE_SHARD_LABELS):
        errors.append(
            "compile_shard_count_mismatch:"
            f"expected={len(REQUIRED_COMPILE_SHARD_LABELS)}:actual={len(compile_shards)}"
        )

    seen_labels: dict[str, str] = {}
    for row in compile_shards:
        if not isinstance(row, dict):
            errors.append(f"compile_shard_row_not_object:{row!r}")
            continue
        label = row.get("label")
        coverage = row.get("coverage")
        if not isinstance(label, str):
            errors.append(f"compile_shard_missing_label:{row!r}")
            continue
        if not isinstance(coverage, str):
            errors.append(f"compile_shard_missing_coverage:{label}")
            continue
        if label in seen_labels:
            errors.append(f"duplicate_compile_shard_label:{label}")
            continue
        seen_labels[label] = coverage

    for label, expected_coverage in REQUIRED_COMPILE_SHARD_LABELS.items():
        actual_coverage = seen_labels.get(label)
        if actual_coverage is None:
            errors.append(f"missing_compile_shard_label:{label}")
        elif actual_coverage != expected_coverage:
            errors.append(
                "compile_shard_coverage_mismatch:"
                f"{label}:expected={expected_coverage}:actual={actual_coverage}"
            )

    focused_count = sum(
        1 for coverage in seen_labels.values() if coverage == "focused_and_full_bundle"
    )
    if focused_count != 1:
        errors.append(
            f"focused_compile_shard_count_mismatch:expected=1:actual={focused_count}"
        )

    full_bundle_only_count = sum(
        1 for coverage in seen_labels.values() if coverage == "full_bundle_only"
    )
    if full_bundle_only_count != 5:
        errors.append(
            "full_bundle_only_compile_shard_count_mismatch:"
            f"expected=5:actual={full_bundle_only_count}"
        )


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    required_paths = [
        RELEASE_BOUNDARY_PATH,
        SURVEY_PATH,
        COMPILE_SHARD_MATRIX_SURVEY_PATH,
        MANIFEST_PATH,
        SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
        RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
        RCU_COMPILE_ROUTE_CHECKER_PATH,
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, EXACT_COUNT_MARKERS)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, EXECUTABLE_GAP_MARKERS)
    require_markers(
        errors, RELEASE_BOUNDARY_PATH, release_boundary, RELEASE_BOUNDARY_TEXT_MARKERS
    )

    survey = read_text(root, SURVEY_PATH)
    require_exact_once(errors, SURVEY_PATH, survey, SURVEY_EXACT_LINE_SNIPPETS)

    compile_shard_survey = read_text(root, COMPILE_SHARD_MATRIX_SURVEY_PATH)
    require_markers(
        errors,
        COMPILE_SHARD_MATRIX_SURVEY_PATH,
        compile_shard_survey,
        COMPILE_SHARD_MATRIX_MARKERS,
    )

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    require_manifest_values(errors, manifest)
    require_compile_shards(errors, manifest)
    return errors


def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            *EXACT_COUNT_MARKERS,
            *RELEASE_BOUNDARY_TEXT_MARKERS,
            "- executable packet members that still do not return through this lane's exact contents readback:",
            *EXECUTABLE_GAP_MARKERS,
            "",
        ]
    )


def fixture_survey() -> str:
    return "\n".join(
        [
            "# Phase 14 End-to-End Smoke Survey",
            *SURVEY_EXACT_LINE_SNIPPETS,
            "",
        ]
    )


def fixture_compile_shard_matrix_survey() -> str:
    return "\n".join(
        [
            "# Phase 14 Compile Shard Matrix Survey",
            *COMPILE_SHARD_MATRIX_MARKERS,
            "",
        ]
    )


def fixture_manifest() -> str:
    payload = {
        "smoke_commands": ["make -C zigux phase14-validate"],
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "survey_summary": {
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "workflow_runs_phase14_validate": True,
            "workflow_runs_phase14_build": False,
            "workflow_runs_phase14_smoke_shard": False,
            "phase14_validate_runs_skbuff_stay_in_c_guardrail": True,
            "phase14_validate_runs_skbuff_compile_route_checker": True,
            "shared_manifest_records_skbuff_compile_route_checker": True,
            "phase14_validate_runs_rcu_compile_route_checker": True,
            "shared_manifest_records_rcu_compile_route_checker": True,
            "phase14_validate_runs_rcu_rollback_guardrail": True,
        },
        "compile_shards": [
            {
                "label": label,
                "coverage": coverage,
                "root_source": "fixture.zig",
            }
            for label, coverage in REQUIRED_COMPILE_SHARD_LABELS.items()
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
    write_text(root, SURVEY_PATH, fixture_survey())
    write_text(
        root,
        COMPILE_SHARD_MATRIX_SURVEY_PATH,
        fixture_compile_shard_matrix_survey(),
    )
    write_text(root, MANIFEST_PATH, fixture_manifest())
    write_text(root, SKBUFF_COMPILE_ROUTE_CHECKER_PATH, "# present for shared-packet file checks\n")
    write_text(
        root,
        RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
        "# present for shared-packet file checks\n",
    )
    write_text(
        root,
        RCU_COMPILE_ROUTE_CHECKER_PATH,
        "# present for shared-packet file checks\n",
    )


def remove_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)


def duplicate_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    if marker not in text:
        raise ValueError(f"marker not found for duplication: {marker}")
    updated = text.replace(marker, marker + "\n" + marker, 1)
    write_text(root, rel, updated)


def write_manifest_payload(root: Path, payload: object) -> None:
    write_text(root, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-release-boundary-counts-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        remove_line(base, RELEASE_BOUNDARY_PATH, EXACT_COUNT_MARKERS[0])
        if not any(EXACT_COUNT_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected exact-count drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, RELEASE_BOUNDARY_PATH, EXECUTABLE_GAP_MARKERS[0])
        if not any(EXECUTABLE_GAP_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected executable-gap drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, RELEASE_BOUNDARY_PATH, RELEASE_BOUNDARY_TEXT_MARKERS[1])
        if not any(RELEASE_BOUNDARY_TEXT_MARKERS[1] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected manifest-count marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, SURVEY_PATH, SURVEY_EXACT_LINE_SNIPPETS[1])
        if not any(SURVEY_EXACT_LINE_SNIPPETS[1] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected missing returned-route-checker marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, SURVEY_PATH, SURVEY_EXACT_LINE_SNIPPETS[3])
        if not any(SURVEY_EXACT_LINE_SNIPPETS[3] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected missing skbuff stay-in-c survey marker drift to fail")
            return 1

        write_fixture_tree(base)
        duplicate_line(base, SURVEY_PATH, SURVEY_EXACT_LINE_SNIPPETS[0])
        if not any(
            error.startswith(
                f"duplicate_marker:{SURVEY_PATH.as_posix()}:{SURVEY_EXACT_LINE_SNIPPETS[0]}"
            )
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected duplicate survey marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(
            base,
            COMPILE_SHARD_MATRIX_SURVEY_PATH,
            "- ring-buffer compile-route checker: `scripts/zigux/check-phase14-ring-buffer-compile-route.py`",
        )
        if not any(
            "ring-buffer compile-route checker" in error for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected ring-buffer compile-route checker marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(
            base,
            COMPILE_SHARD_MATRIX_SURVEY_PATH,
            "- rcu compile-route checker: `scripts/zigux/check-phase14-rcu-compile-route.py`",
        )
        if not any(
            "rcu compile-route checker" in error for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected rcu compile-route checker marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(
            base,
            COMPILE_SHARD_MATRIX_SURVEY_PATH,
            "- `scripts/zigux/check-phase14-ring-buffer-compile-route.py` now fail-closes on the shared-manifest row together with the note's returned ring-buffer-local replay wording even while the lane remains study-only and maintenance-scoped",
        )
        if not any(
            "ring-buffer-local replay wording" in error for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected ring-buffer row-guard marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(
            base,
            COMPILE_SHARD_MATRIX_SURVEY_PATH,
            "- the manifest-backed compile row is present, and `scripts/zigux/check-phase14-rcu-compile-route.py` now fail-closes on the shared-manifest row, the dedicated build-shard wiring, and the survey note's public-fallback replay wording while the anchor stays freeze-in-C initially",
        )
        if not any(
            "public-fallback replay wording" in error for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected rcu row-guard marker drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_skbuff_stay_in_c_guardrail"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:survey_summary.phase14_validate_runs_skbuff_stay_in_c_guardrail")
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected skbuff stay-in-c manifest drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_skbuff_compile_route_checker"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:survey_summary.phase14_validate_runs_skbuff_compile_route_checker")
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected skbuff compile-route manifest drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["shared_manifest_records_skbuff_compile_route_checker"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:survey_summary.shared_manifest_records_skbuff_compile_route_checker")
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected shared manifest skbuff compile-route drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_rcu_compile_route_checker"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:survey_summary.phase14_validate_runs_rcu_compile_route_checker")
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected RCU compile-route manifest drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["shared_manifest_records_rcu_compile_route_checker"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:survey_summary.shared_manifest_records_rcu_compile_route_checker")
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected shared manifest RCU compile-route drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_rcu_rollback_guardrail"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("manifest_value_mismatch:survey_summary.phase14_validate_runs_rcu_rollback_guardrail")
            for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected RCU rollback manifest drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["compile_shards"] = manifest["compile_shards"][:-1]
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("compile_shard_count_mismatch:") for error in check(base)
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected compile-shard count mismatch to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["compile_shards"][0]["coverage"] = "focused_and_full_bundle"
        write_manifest_payload(base, manifest)
        errors = check(base)
        if not any(
            error.startswith("compile_shard_coverage_mismatch:phase14-workqueue-bridge-tests")
            for error in errors
        ):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected compile-shard coverage mismatch to fail")
            return 1

        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=16")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_ISSUES_END")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=pass")
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_EXECUTABLE_GAP_COUNT={len(EXECUTABLE_GAP_MARKERS)}")
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SURVEY_MARKER_COUNT={len(SURVEY_EXACT_LINE_SNIPPETS)}")
    print(
        "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_COMPILE_SHARD_LABEL_COUNT="
        f"{len(REQUIRED_COMPILE_SHARD_LABELS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
