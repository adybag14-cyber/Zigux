#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/README.md",
]

GUIDE_SECTION_MARKERS = [
    "## Checklist carryover prompts",
    "Phase 10: do `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, `scripts/zigux/check-phase10-harness-coverage.py`, `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, and `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` still describe the same validator-first lab bundle and focused harness evidence?",
    "Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `zigux/tests/phase11_build.zig`, and `zigux/tests/phase11_hvc_console_survey.zig` still keep the pre-replay stack and shared-versus-dedicated `hvc_console` split aligned?",
    "Phase 13: do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/README.md`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path and adjacent notifier evidence aligned?",
]

GUIDE_EXACT_COUNT_MARKERS = {
    "## Checklist carryover prompts": 1,
    "Phase 10: do `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, `scripts/zigux/check-phase10-harness-coverage.py`, `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, and `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` still describe the same validator-first lab bundle and focused harness evidence?": 1,
    "Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `zigux/tests/phase11_build.zig`, and `zigux/tests/phase11_hvc_console_survey.zig` still keep the pre-replay stack and shared-versus-dedicated `hvc_console` split aligned?": 1,
    "Phase 13: do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/README.md`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path and adjacent notifier evidence aligned?": 1,
}

CHECKLIST_MARKERS = [
    "if the change touches the active Phase 10, Phase 11, or Phase 13 contributor packet, does `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md` stay aligned with the same validator-first checker stack, shared replay path, and adjacent evidence files named by the packet-local docs and manifests?",
]

DOCS_ROOT_MARKERS = [
    "`Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md` is the shared contributor-facing workflow note for the active Phase 10, Phase 11, and Phase 13 packets",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_marker_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_exact_count_misses(text: str, expected_counts: dict[str, int], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}")
    return missing


def collect_missing(*, present_files: set[str], guide_text: str, checklist_text: str, docs_root_text: str) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_marker_misses(guide_text, GUIDE_SECTION_MARKERS, "guide"))
    missing.extend(collect_exact_count_misses(guide_text, GUIDE_EXACT_COUNT_MARKERS, "guide_count"))
    missing.extend(collect_marker_misses(checklist_text, CHECKLIST_MARKERS, "checklist"))
    missing.extend(collect_marker_misses(docs_root_text, DOCS_ROOT_MARKERS, "docs_root"))
    return missing


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "guide_text": read_text(ROOT, "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"),
        "checklist_text": read_text(ROOT, "Documentation/zigux/review-checklist.md"),
        "docs_root_text": read_text(ROOT, "Documentation/zigux/README.md"),
    }


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase10-phase11-phase13-review-guide-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "guide_text": "\n".join(GUIDE_SECTION_MARKERS) + "\n",
        "checklist_text": "\n".join(CHECKLIST_MARKERS) + "\n",
        "docs_root_text": "\n".join(DOCS_ROOT_MARKERS) + "\n",
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase10-phase11-phase13-review-guide-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(**{**base_inputs, "present_files": set(REQUIRED_FILES[1:])})
    expect_contains(
        "missing_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "guide_text": base_inputs["guide_text"].replace(
                GUIDE_SECTION_MARKERS[1] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains("guide_marker_detection", missing, f"guide:{GUIDE_SECTION_MARKERS[1]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "guide_text": base_inputs["guide_text"] + GUIDE_SECTION_MARKERS[2] + "\n",
        }
    )
    expect_contains(
        "guide_exact_count_detection",
        missing,
        f"guide_count:{GUIDE_SECTION_MARKERS[2]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "checklist_text": base_inputs["checklist_text"].replace(
                CHECKLIST_MARKERS[0],
                "if the change touches the active Phase 10, Phase 11, or Phase 13 contributor packet, does the shared note stay aligned?",
                1,
            ),
        }
    )
    expect_contains("checklist_link_detection", missing, f"checklist:{CHECKLIST_MARKERS[0]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"].replace(
                DOCS_ROOT_MARKERS[0],
                "the docs root names a contributor guide",
                1,
            ),
        }
    )
    expect_contains("docs_root_link_detection", missing, f"docs_root:{DOCS_ROOT_MARKERS[0]}")

    print("PHASE101113_REVIEW_GUIDE_SELF_TEST=pass")
    print("PHASE101113_REVIEW_GUIDE_SELF_TEST_CASE_COUNT=5")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = build_live_inputs()
missing = collect_missing(**live_inputs)
if missing:
    print("PHASE101113_REVIEW_GUIDE=fail")
    print("PHASE101113_REVIEW_GUIDE_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE101113_REVIEW_GUIDE_MISSING_END")
    sys.exit(1)

print("PHASE101113_REVIEW_GUIDE=pass")
print(f"PHASE101113_REVIEW_GUIDE_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE101113_REVIEW_GUIDE_MARKER_COUNT={len(GUIDE_SECTION_MARKERS) + len(CHECKLIST_MARKERS) + len(DOCS_ROOT_MARKERS)}")
