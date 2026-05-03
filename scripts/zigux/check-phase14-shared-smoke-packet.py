#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
]

SURVEY_MARKERS = [
    "PHASE14_STATUS=active",
    "PHASE14_SHARED_LANE=P14-L01",
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14",
    "PHASE14_FOCUSED_SHARD_COUNT=1",
    "PHASE14_STAY_IN_C_BOUNDARY=explicit",
    "PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence",
    "PHASE14_BOUNDARY_MAP=shared-anchor-packet-bundle",
    "PHASE14_CONCURRENCY_AUDIT_SCOPE=anchor-local-packets-only",
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>",
    "named owner: `Core-Adjacent Pod`",
    "rollback owner: `Repo Tooling Pod`",
    "automatic return-to-blocked triggers:",
]

SURVEY_EXACT_COUNT_MARKERS = {
    "PHASE14_SHARED_LANE=P14-L01": 1,
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate": 1,
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all": 1,
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14": 1,
    "PHASE14_FOCUSED_SHARD_COUNT=1": 1,
    "PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence": 1,
    "PHASE14_BOUNDARY_MAP=shared-anchor-packet-bundle": 1,
    "PHASE14_CONCURRENCY_AUDIT_SCOPE=anchor-local-packets-only": 1,
}

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture",
    "`kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate",
]

DOCS_ROOT_EXACT_COUNT_MARKERS = {
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": 1,
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate": 1,
}

SCRIPTS_README_MARKERS = [
    "`validate-phase14.py`",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
    "`zigux/tests/phase14_build.zig`",
    "shared Phase 14 smoke packet",
    "focused smoke-shard replay contract",
    "stay-in-C boundary",
    "roadmap risk bundle",
    "hidden runtime behavior",
    "memory-ordering mistakes",
    "overpromising full parity",
    "deep-core scope creep",
    "rollback threshold",
    "fallback path",
    "automatic return-to-blocked trigger catalog",
    "four-anchor boundary map",
    "bounded concurrency-audit scope",
    "`make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`",
    "`make -C zigux phase14-smoke ZIG=<attached-zig-path>`",
    "`make -C zigux phase14-test ZIG=<attached-zig-path>`",
    "`make -C zigux phase14 ZIG=<attached-zig-path>`",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet, do `scripts/zigux/validate-phase14.py`, `scripts/zigux/README.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_build.zig`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, and the four Phase 14 anchor-local manifests plus survey notes still agree on the same exact validator-backed smoke commands, the same focused `phase14-smoke` shard commands, ready-next versus blocked posture, stay-in-C boundary, named owner, validation gate, rollback owner, rollback threshold, automatic return-to-blocked trigger catalog, roadmap risk bundle (`hidden runtime behavior`, `memory-ordering mistakes`, `overpromising full parity`, `deep-core scope creep`), and explicit ZAR-to-product transfer rationale?",
    "if the change touches the shared Phase 14 smoke packet, do the same shared smoke note, scripts index, and manifest-backed survey summary still keep the current four-anchor boundary map and bounded concurrency-audit scope explicit instead of leaving that roadmap evidence implicit behind the anchor list?",
]

FREEZE_MAP_MARKERS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "net/core/skbuff.c",
    "kernel/rcu/tree.c",
    "Architecture Council",
]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def collect_marker_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_exact_count_misses(
    text: str, expected_counts: dict[str, int], prefix: str
) -> list[str]:
    missing: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(
                f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}"
            )
    return missing


def collect_missing(
    *,
    present_files: set[str],
    survey_text: str,
    docs_root_text: str,
    scripts_readme_text: str,
    review_checklist_text: str,
    freeze_map_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_marker_misses(survey_text, SURVEY_MARKERS, "survey"))
    missing.extend(
        collect_exact_count_misses(survey_text, SURVEY_EXACT_COUNT_MARKERS, "survey_count")
    )
    missing.extend(collect_marker_misses(docs_root_text, DOCS_ROOT_MARKERS, "docs_root"))
    missing.extend(
        collect_exact_count_misses(
            docs_root_text, DOCS_ROOT_EXACT_COUNT_MARKERS, "docs_root_count"
        )
    )
    missing.extend(
        collect_marker_misses(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts_readme")
    )
    missing.extend(
        collect_marker_misses(
            review_checklist_text, REVIEW_CHECKLIST_MARKERS, "review_checklist"
        )
    )
    missing.extend(collect_marker_misses(freeze_map_text, FREEZE_MAP_MARKERS, "freeze_map"))
    return missing


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "survey_text": read_text("Documentation/zigux/phase14-end-to-end-smoke-survey.md"),
        "docs_root_text": read_text("Documentation/zigux/README.md"),
        "scripts_readme_text": read_text("scripts/zigux/README.md"),
        "review_checklist_text": read_text("Documentation/zigux/review-checklist.md"),
        "freeze_map_text": read_text("Documentation/zigux/freeze-map.md"),
    }


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase14-shared-smoke-packet-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "survey_text": "\n".join(SURVEY_MARKERS) + "\n",
        "docs_root_text": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "scripts_readme_text": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "review_checklist_text": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "freeze_map_text": "\n".join(FREEZE_MAP_MARKERS) + "\n",
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase14-shared-smoke-packet-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(**{**base_inputs, "present_files": set(REQUIRED_FILES[1:])})
    expect_contains(
        "missing_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace(
                "PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence\n", "", 1
            ),
        }
    )
    expect_contains(
        "survey_marker_detection",
        missing,
        "survey:PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"]
            + "PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence\n",
        }
    )
    expect_contains(
        "survey_exact_count_detection",
        missing,
        "survey_count:PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"].replace(
                DOCS_ROOT_MARKERS[4] + "\n", "", 1
            ),
        }
    )
    expect_contains("docs_root_marker_detection", missing, f"docs_root:{DOCS_ROOT_MARKERS[4]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"] + DOCS_ROOT_MARKERS[4] + "\n",
        }
    )
    expect_contains(
        "docs_root_exact_count_detection",
        missing,
        f"docs_root_count:{DOCS_ROOT_MARKERS[4]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": base_inputs["scripts_readme_text"].replace(
                "automatic return-to-blocked trigger catalog\n", "", 1
            ),
        }
    )
    expect_contains(
        "scripts_readme_marker_detection",
        missing,
        "scripts_readme:automatic return-to-blocked trigger catalog",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "review_checklist_text": base_inputs["review_checklist_text"].replace(
                REVIEW_CHECKLIST_MARKERS[1] + "\n", "", 1
            ),
        }
    )
    expect_contains(
        "review_checklist_marker_detection",
        missing,
        f"review_checklist:{REVIEW_CHECKLIST_MARKERS[1]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "freeze_map_text": base_inputs["freeze_map_text"].replace(
                "kernel/rcu/tree.c\n", "", 1
            ),
        }
    )
    expect_contains("freeze_map_marker_detection", missing, "freeze_map:kernel/rcu/tree.c")

    print("PHASE14_SHARED_SMOKE_PACKET_SELF_TEST=pass")
    print("PHASE14_SHARED_SMOKE_PACKET_SELF_TEST_CASE_COUNT=8")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = build_live_inputs()
missing = collect_missing(**live_inputs)
if missing:
    print("PHASE14_SHARED_SMOKE_PACKET=fail")
    print("PHASE14_SHARED_SMOKE_PACKET_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE14_SHARED_SMOKE_PACKET_MISSING_END")
    sys.exit(1)

print("PHASE14_SHARED_SMOKE_PACKET=pass")
print(f"PHASE14_SHARED_SMOKE_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE14_SHARED_SMOKE_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
print(f"PHASE14_SHARED_SMOKE_PACKET_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_MARKERS)}")
print(f"PHASE14_SHARED_SMOKE_PACKET_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
print(f"PHASE14_SHARED_SMOKE_PACKET_REVIEW_CHECKLIST_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
