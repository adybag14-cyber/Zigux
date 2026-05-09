#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the shared Phase 14 rollback-owner and sequencing-split packet.
It keeps the manifest, shared smoke note, release-boundary note, review checklist,
scripts index, and cross-anchor traceability note aligned around the current stay-in-C
and freeze-in-C split on master.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
MANIFEST_PATH = "zigux/tests/phase14_end_to_end_smoke_manifest.json"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TRACEABILITY_PATH = "Documentation/zigux/phase14-core-boundary-traceability.md"
WORKQUEUE_MANIFEST_PATH = "zigux/tests/phase14_workqueue_bridge_manifest.json"
RING_BUFFER_MANIFEST_PATH = "zigux/tests/phase14_ring_buffer_manifest.json"
SKBUFF_MANIFEST_PATH = "zigux/tests/phase14_skbuff_bridge_manifest.json"
RCU_MANIFEST_PATH = "zigux/tests/phase14_rcu_tree_manifest.json"
RELEASE_BOUNDARY_PATH = "Documentation/zigux/phase14-release-boundary-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"

REQUIRED_FILE_MARKERS = {
    MANIFEST_PATH: [
        '"rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence"',
        '"kernel/workqueue.c"',
        '"kernel/trace/ring_buffer.c"',
        '"kernel/rcu/tree.c"',
        '"net/core/skbuff.c"',
    ],
    SMOKE_SURVEY_PATH: [
        "`PHASE14_STAY_IN_C_BOUNDARY=explicit`",
        "- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`",
        "Attached-toolchain fallback examples:",
        "- `make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig`",
        "- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`",
        "- `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`",
        "- `make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig`",
        "- `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`",
        "- `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
        "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.",
        "Fallback path:",
        "Keep `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.",
        "Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift.",
        "- review blocker status: `blocked_on_stay_in_c_evidence`",
    ],
    RELEASE_BOUNDARY_PATH: [
        "`PHASE14_STUDY_ONLY_ANCHOR_COUNT=2`",
        "`PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2`",
        "`kernel/workqueue.c`: boundary-study-only anchor",
        "`kernel/trace/ring_buffer.c`: boundary-study-only anchor",
        "`kernel/rcu/tree.c`: remains blocked from active delivery",
        "`net/core/skbuff.c`: remains blocked from active delivery",
        "reviewability packet rather than a release-closure or status-change claim",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared Phase 14 smoke packet",
        "same study-only stay-in-C posture without implying an active deep-core port claim?",
    ],
    SCRIPTS_README_PATH: [
        "keep the current Phase 14 smoke packet reviewable through",
        "exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim.",
    ],
    TRACEABILITY_PATH: [
        "# Phase 14 Core Boundary Traceability",
        "For shared Phase 14 sequencing and anti-overlap follow-through, treat this cross-anchor note as a summary surface only:",
    ],
}

MANIFEST_EXACT_COUNT_MARKERS = REQUIRED_FILE_MARKERS[MANIFEST_PATH]
SMOKE_SURVEY_EXACT_COUNT_MARKERS = REQUIRED_FILE_MARKERS[SMOKE_SURVEY_PATH] + [
    "- `zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "- `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- `zigux/tests/phase14_ring_buffer_manifest.json`",
    "- `zigux/tests/phase14_rcu_tree_manifest.json`",
]
RELEASE_BOUNDARY_EXACT_COUNT_MARKERS = REQUIRED_FILE_MARKERS[RELEASE_BOUNDARY_PATH]
REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = REQUIRED_FILE_MARKERS[REVIEW_CHECKLIST_PATH]
SCRIPTS_README_EXACT_COUNT_MARKERS = REQUIRED_FILE_MARKERS[SCRIPTS_README_PATH]
TRACEABILITY_EXACT_COUNT_MARKERS = REQUIRED_FILE_MARKERS[TRACEABILITY_PATH]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json_file(path: Path) -> dict:
    return json.loads(read_text(path))


def require_exact_marker_count(errors: list[str], rel_path: str, text: str, marker: str) -> None:
    actual_count = text.count(marker)
    if actual_count != 1:
        errors.append(
            f"marker count drift in {rel_path}: {marker} (expected 1, found {actual_count})"
        )


def traceability_dynamic_markers(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    markers: list[str] = []
    lane_order: list[str] = []
    for manifest_rel_path in [
        WORKQUEUE_MANIFEST_PATH,
        RING_BUFFER_MANIFEST_PATH,
        SKBUFF_MANIFEST_PATH,
        RCU_MANIFEST_PATH,
    ]:
        manifest_path = root / manifest_rel_path
        if not manifest_path.exists():
            errors.append(f"missing file: {manifest_rel_path}")
            continue
        try:
            manifest = load_json_file(manifest_path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid json in {manifest_rel_path}: {exc}")
            continue
        lane_key = manifest.get("lane_key")
        surveyed_commit = manifest.get("surveyed_commit")
        if not isinstance(lane_key, str):
            errors.append(f"missing lane_key in {manifest_rel_path}")
            continue
        if not isinstance(surveyed_commit, str):
            errors.append(f"missing surveyed_commit in {manifest_rel_path}")
            continue
        lane_order.append(lane_key)
        markers.extend(
            [
                f"- manifest: `{manifest_rel_path}`",
                f"- lane key: `{lane_key}`",
                f"- surveyed commit: `{surveyed_commit}`",
            ]
        )
    if len(lane_order) == 4:
        markers.append(
            "the live workqueue, ring-buffer, skbuff, and RCU packets now route through "
            f"`{lane_order[0]}`, `{lane_order[1]}`, `{lane_order[2]}`, and `{lane_order[3]}`"
        )
    return markers, errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")

    exact_markers_by_path = {
        MANIFEST_PATH: MANIFEST_EXACT_COUNT_MARKERS,
        SMOKE_SURVEY_PATH: SMOKE_SURVEY_EXACT_COUNT_MARKERS,
        RELEASE_BOUNDARY_PATH: RELEASE_BOUNDARY_EXACT_COUNT_MARKERS,
        REVIEW_CHECKLIST_PATH: REVIEW_CHECKLIST_EXACT_COUNT_MARKERS,
        SCRIPTS_README_PATH: SCRIPTS_README_EXACT_COUNT_MARKERS,
        TRACEABILITY_PATH: TRACEABILITY_EXACT_COUNT_MARKERS,
    }

    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        text = read_text(path)
        if rel_path == MANIFEST_PATH:
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid json in {MANIFEST_PATH}: {exc}")
                continue
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")
        for marker in exact_markers_by_path.get(rel_path, []):
            require_exact_marker_count(errors, rel_path, text, marker)

    traceability_path = root / TRACEABILITY_PATH
    if traceability_path.exists():
        traceability_text = read_text(traceability_path)
        dynamic_markers, dynamic_errors = traceability_dynamic_markers(root)
        errors.extend(dynamic_errors)
        for marker in dynamic_markers:
            if marker not in traceability_text:
                errors.append(f"missing marker in {TRACEABILITY_PATH}: {marker}")
                continue
            require_exact_marker_count(errors, TRACEABILITY_PATH, traceability_text, marker)

    return errors


def required_text(root: Path, rel_path: str) -> str:
    if rel_path == MANIFEST_PATH:
        return json.dumps(
            {
                "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",
                "blocked_anchors": [
                    "kernel/workqueue.c",
                    "kernel/trace/ring_buffer.c",
                    "kernel/rcu/tree.c",
                    "net/core/skbuff.c",
                ],
            },
            indent=2,
        ) + "\n"
    if rel_path == WORKQUEUE_MANIFEST_PATH:
        return json.dumps({"lane_key": "P14-L02", "surveyed_commit": "9b98d3b9c812840bf279508030be0b8de093736c"}, indent=2) + "\n"
    if rel_path == RING_BUFFER_MANIFEST_PATH:
        return json.dumps({"lane_key": "P14-L08", "surveyed_commit": "946d5c73fdb763ba860a20879b05da54e1896e8c"}, indent=2) + "\n"
    if rel_path == SKBUFF_MANIFEST_PATH:
        return json.dumps({"lane_key": "P14-L11", "surveyed_commit": "4f6dab5f88d8141ecd358d93fe9284bcc98dc1d7"}, indent=2) + "\n"
    if rel_path == RCU_MANIFEST_PATH:
        return json.dumps({"lane_key": "P14-L13", "surveyed_commit": "4c889233d157960514b241bcd5aff7cac5fda312"}, indent=2) + "\n"
    if rel_path == TRACEABILITY_PATH:
        dynamic_markers, dynamic_errors = traceability_dynamic_markers(root)
        if dynamic_errors:
            raise RuntimeError("; ".join(dynamic_errors))
        return "\n".join(REQUIRED_FILE_MARKERS[TRACEABILITY_PATH] + dynamic_markers) + "\n"
    markers = list(REQUIRED_FILE_MARKERS[rel_path])
    if rel_path == SMOKE_SURVEY_PATH:
        markers.extend(SMOKE_SURVEY_EXACT_COUNT_MARKERS[-4:])
    return "\n".join(markers) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        current_checker_path = Path(__file__)
        original_checker_source = current_checker_path.read_text(encoding="utf-8")
        for rel_path in [MANIFEST_PATH, WORKQUEUE_MANIFEST_PATH, RING_BUFFER_MANIFEST_PATH, SKBUFF_MANIFEST_PATH, RCU_MANIFEST_PATH]:
            write_text(root / rel_path, required_text(root, rel_path))
        for rel_path in [SMOKE_SURVEY_PATH, RELEASE_BOUNDARY_PATH, REVIEW_CHECKLIST_PATH, SCRIPTS_README_PATH, TRACEABILITY_PATH]:
            write_text(root / rel_path, required_text(root, rel_path))

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken_traceability_path = root / TRACEABILITY_PATH
        broken_traceability_path.write_text(
            broken_traceability_path.read_text(encoding="utf-8").replace(
                "the live workqueue, ring-buffer, skbuff, and RCU packets now route through `P14-L02`, `P14-L08`, `P14-L11`, and `P14-L13`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: the live workqueue, ring-buffer, skbuff, and RCU packets now route through `P14-L02`, `P14-L08`, `P14-L11`, and `P14-L13`"
            in error
            for error in errors
        ):
            print("self-test expected missing traceability owner-map summary failure", file=sys.stderr)
            return 1
        write_text(broken_traceability_path, required_text(root, TRACEABILITY_PATH))

        broken_traceability_path.write_text(
            broken_traceability_path.read_text(encoding="utf-8").replace(
                "- lane key: `P14-L02`\n",
                "- lane key: `P14-L02`\n- lane key: `P14-L02`\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-core-boundary-traceability.md: - lane key: `P14-L02` (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate workqueue lane-key failure", file=sys.stderr)
            return 1
        write_text(broken_traceability_path, required_text(root, TRACEABILITY_PATH))

        broken_skbuff_manifest_path = root / SKBUFF_MANIFEST_PATH
        broken_skbuff_manifest = json.loads(read_text(broken_skbuff_manifest_path))
        broken_skbuff_manifest.pop("lane_key", None)
        write_text(
            broken_skbuff_manifest_path,
            json.dumps(broken_skbuff_manifest, indent=2) + "\n",
        )
        errors = check(root)
        if not any(
            "missing lane_key in zigux/tests/phase14_skbuff_bridge_manifest.json"
            in error
            for error in errors
        ):
            print("self-test expected missing skbuff lane-key failure", file=sys.stderr)
            return 1
        write_text(broken_skbuff_manifest_path, required_text(root, SKBUFF_MANIFEST_PATH))

        broken_workqueue_manifest_path = root / WORKQUEUE_MANIFEST_PATH
        broken_workqueue_manifest = json.loads(read_text(broken_workqueue_manifest_path))
        broken_workqueue_manifest.pop("surveyed_commit", None)
        write_text(
            broken_workqueue_manifest_path,
            json.dumps(broken_workqueue_manifest, indent=2) + "\n",
        )
        errors = check(root)
        if not any(
            "missing surveyed_commit in zigux/tests/phase14_workqueue_bridge_manifest.json"
            in error
            for error in errors
        ):
            print("self-test expected missing workqueue surveyed-commit failure", file=sys.stderr)
            return 1
        write_text(broken_workqueue_manifest_path, required_text(root, WORKQUEUE_MANIFEST_PATH))

        write_text(broken_workqueue_manifest_path, "{\n")
        errors = check(root)
        if not any(
            "invalid json in zigux/tests/phase14_workqueue_bridge_manifest.json:"
            in error
            for error in errors
        ):
            print("self-test expected invalid workqueue manifest json failure", file=sys.stderr)
            return 1
        write_text(broken_workqueue_manifest_path, required_text(root, WORKQUEUE_MANIFEST_PATH))

        broken_release_path = root / RELEASE_BOUNDARY_PATH
        broken_release_path.write_text("`PHASE14_STUDY_ONLY_ANCHOR_COUNT=1`\n", encoding="utf-8")
        errors = check(root)
        if not any("PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2" in error for error in errors):
            print("self-test expected release-boundary drift failure", file=sys.stderr)
            return 1
        write_text(broken_release_path, required_text(root, RELEASE_BOUNDARY_PATH))

        broken_manifest_path = root / MANIFEST_PATH
        write_text(broken_manifest_path, "{\n")
        errors = check(root)
        if not any(
            "invalid json in zigux/tests/phase14_end_to_end_smoke_manifest.json:"
            in error
            for error in errors
        ):
            print("self-test expected invalid shared smoke manifest json failure", file=sys.stderr)
            return 1
        write_text(broken_manifest_path, required_text(root, MANIFEST_PATH))

        broken_manifest_path.write_text(
            broken_manifest_path.read_text(encoding="utf-8").replace(
                '  "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            'missing marker in zigux/tests/phase14_end_to_end_smoke_manifest.json: "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence"'
            in error
            for error in errors
        ):
            print("self-test expected missing rollback-owner failure", file=sys.stderr)
            return 1
        write_text(broken_manifest_path, required_text(root, MANIFEST_PATH))

        broken_smoke_note_path = root / SMOKE_SURVEY_PATH
        broken_smoke_note_path.write_text(
            broken_smoke_note_path.read_text(encoding="utf-8").replace(
                "- `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`"
            in error
            for error in errors
        ):
            print("self-test expected missing direct smoke fallback example failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note_path, required_text(root, SMOKE_SURVEY_PATH))

        broken_smoke_note_path.write_text(
            broken_smoke_note_path.read_text(encoding="utf-8").replace(
                "- `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`\n",
                "- `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`\n"
                "- `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all` (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate direct smoke fallback example failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note_path, required_text(root, SMOKE_SURVEY_PATH))

        broken_smoke_note_path.write_text(
            broken_smoke_note_path.read_text(encoding="utf-8").replace(
                "- `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`"
            in error
            for error in errors
        ):
            print("self-test expected missing direct full-test fallback example failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note_path, required_text(root, SMOKE_SURVEY_PATH))

        broken_smoke_note_path.write_text(
            broken_smoke_note_path.read_text(encoding="utf-8").replace(
                "- `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`\n",
                "- `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`\n"
                "- `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all` (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate direct full-test fallback example failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note_path, required_text(root, SMOKE_SURVEY_PATH))

        broken_smoke_note_path.write_text(
            broken_smoke_note_path.read_text(encoding="utf-8").replace(
                "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope."
            in error
            for error in errors
        ):
            print("self-test expected missing note-local fallback scope failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note_path, required_text(root, SMOKE_SURVEY_PATH))

        broken_smoke_note_path.write_text(
            broken_smoke_note_path.read_text(encoding="utf-8").replace(
                "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.\n",
                "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.\n"
                "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope. (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate note-local fallback scope failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note_path, required_text(root, SMOKE_SURVEY_PATH))

        broken_scripts_readme_path = root / SCRIPTS_README_PATH
        broken_scripts_readme_path.write_text(
            broken_scripts_readme_path.read_text(encoding="utf-8").replace(
                "exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in scripts/zigux/README.md: exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim."
            in error
            for error in errors
        ):
            print("self-test expected scripts README rollback-summary failure", file=sys.stderr)
            return 1
        write_text(broken_scripts_readme_path, required_text(root, SCRIPTS_README_PATH))

        broken_scripts_readme_path.write_text(
            broken_scripts_readme_path.read_text(encoding="utf-8").replace(
                "exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim.\n",
                "exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim.\n"
                "exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim.\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "marker count drift in scripts/zigux/README.md: exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, freeze-map boundary note, and ZAR-to-product transfer rationale without implying an active deep-core port claim. (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate scripts README rollback-summary failure", file=sys.stderr)
            return 1
        write_text(broken_scripts_readme_path, required_text(root, SCRIPTS_README_PATH))

        current_checker_path.write_text(
            original_checker_source.replace(MARKER, "PHASE14_CHECK_PACKET=broken_marker"),
            encoding="utf-8",
        )
        errors = check(root)
        if not any("checker marker missing from checker source" in error for error in errors):
            print("self-test expected checker-marker failure", file=sys.stderr)
            current_checker_path.write_text(original_checker_source, encoding="utf-8")
            return 1
        current_checker_path.write_text(original_checker_source, encoding="utf-8")

        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 rollback-threshold sequencing packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
