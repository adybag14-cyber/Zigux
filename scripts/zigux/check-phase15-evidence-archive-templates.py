#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve()
if SCRIPT_PATH.parent.name == "zigux" and SCRIPT_PATH.parent.parent.name == "scripts":
    ROOT = SCRIPT_PATH.parents[2]
else:
    ROOT = SCRIPT_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
    "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
    "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
    "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase15-architecture-council-review-process.md": [
        "current approval evidence is explicit negative evidence rather than silence",
        "current ownership evidence is explicit in both the scorecard and the anchor templates",
        "requested decision bucket: pending_no_request",
        "decision record ID: pending_no_architecture_council_request",
        "no Architecture Council approval claim",
        "Documentation/zigux/phase15-evidence-archives/",
    ],
    "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md": [
        "requested decision bucket: `pending_no_request`",
        "decision record ID: `pending_no_architecture_council_request`",
        "no Architecture Council approval claim: `true`",
        "lane owner: `Architecture Council`",
        "rollback owner: `Architecture Council + PMO / Release Management`",
        "rollback threshold:",
        "retained discussion state after closeout: `retired_from_active_discussion`",
        "ownership_or_validation_changed",
        "indefinite-C policy link: `Documentation/zigux/phase15-indefinite-c-policy.md`",
        "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`",
    ],
    "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md": [
        "requested decision bucket: `pending_no_request`",
        "decision record ID: `pending_no_architecture_council_request`",
        "no Architecture Council approval claim: `true`",
        "lane owner: `Architecture Council`",
        "rollback owner: `Architecture Council + Validation and Perf Team`",
        "rollback threshold:",
        "retained discussion state after closeout: `retired_from_active_discussion`",
        "ownership_or_validation_changed",
        "indefinite-C policy link: `Documentation/zigux/phase15-indefinite-c-policy.md`",
        "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`",
    ],
    "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md": [
        "requested decision bucket: `pending_no_request`",
        "decision record ID: `pending_no_architecture_council_request`",
        "no Architecture Council approval claim: `true`",
        "lane owner: `ABI and Runtime Team`",
        "rollback owner: `Architecture Council + ABI and Runtime Team`",
        "rollback threshold:",
        "retained discussion state after closeout: `retired_from_active_discussion`",
        "ownership_or_validation_changed",
        "indefinite-C policy link: `Documentation/zigux/phase15-indefinite-c-policy.md`",
        "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`",
    ],
    "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md": [
        "requested decision bucket: `pending_no_request`",
        "decision record ID: `pending_no_architecture_council_request`",
        "no Architecture Council approval claim: `true`",
        "lane owner: `Shared Subsystems Pod`",
        "rollback owner: `Architecture Council + Shared Subsystems Pod`",
        "rollback threshold:",
        "retained discussion state after closeout: `retired_from_active_discussion`",
        "ownership_or_validation_changed",
        "indefinite-C policy link: `Documentation/zigux/phase15-indefinite-c-policy.md`",
        "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`",
    ],
}


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def collect_marker_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_missing(*, present_files: set[str], file_texts: dict[str, str]) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    for path, markers in REQUIRED_MARKERS.items():
        missing.extend(collect_marker_misses(file_texts.get(path, ""), markers, path))
    return missing


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "file_texts": {path: read_text(path) for path in REQUIRED_FILES if (ROOT / path).exists()},
    }


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase15-evidence-archive-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "file_texts": {
            path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()
        },
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase15-evidence-archive-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(**{**base_inputs, "present_files": set(REQUIRED_FILES[1:])})
    expect_contains(
        "missing_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase15-architecture-council-review-process.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "file_texts": {
                **base_inputs["file_texts"],
                "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md": base_inputs[
                    "file_texts"
                ]["Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md"].replace(
                    "no Architecture Council approval claim: `true`\n", "", 1
                ),
            },
        }
    )
    expect_contains(
        "approval_marker_detection",
        missing,
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md:no Architecture Council approval claim: `true`",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "file_texts": {
                **base_inputs["file_texts"],
                "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md": base_inputs[
                    "file_texts"
                ]["Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md"].replace(
                    "rollback threshold:\n", "", 1
                ),
            },
        }
    )
    expect_contains(
        "rollback_marker_detection",
        missing,
        "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md:rollback threshold:",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "file_texts": {
                **base_inputs["file_texts"],
                "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md": base_inputs[
                    "file_texts"
                ]["Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md"].replace(
                    "retained discussion state after closeout: `retired_from_active_discussion`\n",
                    "",
                    1,
                ),
            },
        }
    )
    expect_contains(
        "retained_state_detection",
        missing,
        "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md:retained discussion state after closeout: `retired_from_active_discussion`",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "file_texts": {
                **base_inputs["file_texts"],
                "Documentation/zigux/phase15-architecture-council-review-process.md": base_inputs[
                    "file_texts"
                ]["Documentation/zigux/phase15-architecture-council-review-process.md"].replace(
                    "Documentation/zigux/phase15-evidence-archives/\n",
                    "",
                    1,
                ),
            },
        }
    )
    expect_contains(
        "review_process_link_detection",
        missing,
        "Documentation/zigux/phase15-architecture-council-review-process.md:Documentation/zigux/phase15-evidence-archives/",
    )

    print("PHASE15_EVIDENCE_ARCHIVE_TEMPLATES_SELF_TEST=pass")
    print("PHASE15_EVIDENCE_ARCHIVE_TEMPLATES_SELF_TEST_CASE_COUNT=5")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = build_live_inputs()
missing = collect_missing(**live_inputs)
if missing:
    print("PHASE15_EVIDENCE_ARCHIVE_TEMPLATES=fail")
    print("PHASE15_EVIDENCE_ARCHIVE_TEMPLATES_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE15_EVIDENCE_ARCHIVE_TEMPLATES_MISSING_END")
    sys.exit(1)

print("PHASE15_EVIDENCE_ARCHIVE_TEMPLATES=pass")
print(f"PHASE15_EVIDENCE_ARCHIVE_TEMPLATES_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE15_EVIDENCE_ARCHIVE_TEMPLATES_MARKER_COUNT="
    + str(sum(len(markers) for markers in REQUIRED_MARKERS.values()))
)
