#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the shared Phase 14 rollback-owner and sequencing-split packet.
It keeps the manifest, shared smoke note, release-boundary note, and review checklist
aligned around the current stay-in-C and freeze-in-C split on master.
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
        "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.",
        "Fallback path:",
        "Keep `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.",
        "Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift.",
        "- review blocker status: `blocked_on_stay_in_c_evidence`",
    ],
    "Documentation/zigux/phase14-release-boundary-survey.md": [
        "`PHASE14_STUDY_ONLY_ANCHOR_COUNT=2`",
        "`PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2`",
        "`kernel/workqueue.c`: boundary-study-only anchor",
        "`kernel/trace/ring_buffer.c`: boundary-study-only anchor",
        "`kernel/rcu/tree.c`: remains blocked from active delivery",
        "`net/core/skbuff.c`: remains blocked from active delivery",
        "reviewability packet rather than a release-closure or status-change claim",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared Phase 14 smoke packet",
        "same study-only stay-in-C posture without implying an active deep-core port claim?",
    ],
}
MANIFEST_EXACT_COUNT_MARKERS = [
    '"rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence"',
    '"kernel/workqueue.c"',
    '"kernel/trace/ring_buffer.c"',
    '"kernel/rcu/tree.c"',
    '"net/core/skbuff.c"',
]
SMOKE_SURVEY_EXACT_COUNT_MARKERS = [
    "- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`",
    "Attached-toolchain fallback examples:",
    "- `make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig`",
    "- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`",
    "- `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`",
    "- `make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig`",
    "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.",
    "Fallback path:",
    "Keep `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.",
    "Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift.",
    "- review blocker status: `blocked_on_stay_in_c_evidence`",
    "- `zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "- `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- `zigux/tests/phase14_ring_buffer_manifest.json`",
    "- `zigux/tests/phase14_rcu_tree_manifest.json`",
]
RELEASE_BOUNDARY_EXACT_COUNT_MARKERS = [
    "`PHASE14_STUDY_ONLY_ANCHOR_COUNT=2`",
    "`PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2`",
    "`kernel/workqueue.c`: boundary-study-only anchor",
    "`kernel/trace/ring_buffer.c`: boundary-study-only anchor",
    "`kernel/rcu/tree.c`: remains blocked from active delivery",
    "`net/core/skbuff.c`: remains blocked from active delivery",
    "reviewability packet rather than a release-closure or status-change claim",
]
REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet",
    "same study-only stay-in-C posture without implying an active deep-core port claim?",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_exact_marker_count(errors: list[str], rel_path: str, text: str, marker: str) -> None:
    actual_count = text.count(marker)
    if actual_count != 1:
        errors.append(
            f"marker count drift in {rel_path}: {marker} (expected 1, found {actual_count})"
        )


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")
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
            for marker in MANIFEST_EXACT_COUNT_MARKERS:
                require_exact_marker_count(errors, rel_path, text, marker)
        if rel_path == "Documentation/zigux/phase14-release-boundary-survey.md":
            for marker in RELEASE_BOUNDARY_EXACT_COUNT_MARKERS:
                require_exact_marker_count(errors, rel_path, text, marker)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")
    smoke_survey_path = root / SMOKE_SURVEY_PATH
    if smoke_survey_path.exists():
        smoke_text = read_text(smoke_survey_path)
        for marker in SMOKE_SURVEY_EXACT_COUNT_MARKERS:
            actual_count = smoke_text.count(marker)
            if actual_count != 1:
                errors.append(
                    f"marker count drift in {SMOKE_SURVEY_PATH}: {marker} (expected 1, found {actual_count})"
                )
    review_checklist_path = root / "Documentation/zigux/review-checklist.md"
    if review_checklist_path.exists():
        review_checklist_text = read_text(review_checklist_path)
        for marker in REVIEW_CHECKLIST_EXACT_COUNT_MARKERS:
            actual_count = review_checklist_text.count(marker)
            if actual_count != 1:
                errors.append(
                    "marker count drift in Documentation/zigux/review-checklist.md: "
                    f"{marker} (expected 1, found {actual_count})"
                )
    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def required_text(rel_path: str) -> str:
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
    markers = list(REQUIRED_FILE_MARKERS[rel_path])
    if rel_path == SMOKE_SURVEY_PATH:
        markers.extend(SMOKE_SURVEY_EXACT_COUNT_MARKERS[11:])
    return "\n".join(markers) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        current_checker_path = Path(__file__)
        original_checker_source = current_checker_path.read_text(encoding="utf-8")
        write_text(
            root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            MARKER + "\nraise SystemExit(0)\n",
        )
        for rel_path in REQUIRED_FILE_MARKERS:
            write_text(root / rel_path, required_text(rel_path))

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken_path = root / "Documentation/zigux/phase14-release-boundary-survey.md"
        broken_path.write_text("`PHASE14_STUDY_ONLY_ANCHOR_COUNT=1`\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any("PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2" in error for error in errors):
            print("self-test expected failure when release-boundary markers drifted", file=sys.stderr)
            return 1

        write_text(
            broken_path,
            required_text("Documentation/zigux/phase14-release-boundary-survey.md"),
        )

        broken_path.write_text(
            broken_path.read_text(encoding="utf-8").replace(
                "`kernel/workqueue.c`: boundary-study-only anchor\n",
                "`kernel/workqueue.c`: boundary-study-only anchor\n"
                "`kernel/workqueue.c`: boundary-study-only anchor\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-release-boundary-survey.md: "
            "`kernel/workqueue.c`: boundary-study-only anchor (expected 1, found 2)" in error
            for error in errors
        ):
            print("self-test expected failure when the release-boundary workqueue anchor duplicated", file=sys.stderr)
            return 1

        write_text(
            broken_path,
            required_text("Documentation/zigux/phase14-release-boundary-survey.md"),
        )

        broken_path.write_text(
            broken_path.read_text(encoding="utf-8").replace(
                "reviewability packet rather than a release-closure or status-change claim\n",
                "reviewability packet rather than a release-closure or status-change claim\n"
                "reviewability packet rather than a release-closure or status-change claim\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-release-boundary-survey.md: "
            "reviewability packet rather than a release-closure or status-change claim (expected 1, found 2)" in error
            for error in errors
        ):
            print("self-test expected failure when the release-boundary reviewability line duplicated", file=sys.stderr)
            return 1

        write_text(broken_path, required_text("Documentation/zigux/phase14-release-boundary-survey.md"))

        broken_smoke_path = root / SMOKE_SURVEY_PATH
        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- `zigux/tests/phase14_rcu_tree_manifest.json`\n",
                "",
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `zigux/tests/phase14_rcu_tree_manifest.json` (expected 1, found 0)"
            in error
            for error in errors
        ):
            print("self-test expected failure when shared smoke manifest inventory drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- `zigux/tests/phase14_rcu_tree_manifest.json`\n",
                "- `zigux/tests/phase14_rcu_tree_manifest.json`\n- `zigux/tests/phase14_rcu_tree_manifest.json`\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `zigux/tests/phase14_rcu_tree_manifest.json` (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected failure when shared smoke manifest inventory duplicated", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`\n",
                "- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`\n"
                "- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence` (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected failure when the rollback-owner line duplicated", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "Attached-toolchain fallback examples:\n",
                "Attached-toolchain fallback examples:\nAttached-toolchain fallback examples:\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: Attached-toolchain fallback examples: (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected failure when the attached-toolchain fallback heading duplicated", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_manifest_path = root / MANIFEST_PATH
        broken_manifest_path.write_text(
            broken_manifest_path.read_text(encoding="utf-8").replace(
                '  "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            'missing marker in zigux/tests/phase14_end_to_end_smoke_manifest.json: "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence"'
            in error
            for error in errors
        ):
            print("self-test expected failure when the shared smoke manifest lost the rollback-owner marker", file=sys.stderr)
            return 1

        write_text(broken_manifest_path, required_text(MANIFEST_PATH))

        broken_manifest_path.write_text(
            broken_manifest_path.read_text(encoding="utf-8").replace(
                '  "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",\n',
                '  "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",\n'
                '  "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",\n',
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            'marker count drift in zigux/tests/phase14_end_to_end_smoke_manifest.json: "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence" (expected 1, found 2)'
            in error
            for error in errors
        ):
            print("self-test expected failure when the shared smoke manifest duplicated the rollback-owner marker", file=sys.stderr)
            return 1

        write_text(broken_manifest_path, required_text(MANIFEST_PATH))

        broken_manifest_path.write_text(
            broken_manifest_path.read_text(encoding="utf-8").replace(
                '    "kernel/rcu/tree.c",\n',
                '    "kernel/rcu/tree.c",\n    "kernel/rcu/tree.c",\n',
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            'marker count drift in zigux/tests/phase14_end_to_end_smoke_manifest.json: "kernel/rcu/tree.c" (expected 1, found 2)'
            in error
            for error in errors
        ):
            print("self-test expected failure when the shared smoke manifest duplicated a blocked anchor marker", file=sys.stderr)
            return 1

        write_text(broken_manifest_path, required_text(MANIFEST_PATH))

        broken_manifest_path.write_text(
            broken_manifest_path.read_text(encoding="utf-8").replace(
                '    "kernel/rcu/tree.c",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            'missing marker in zigux/tests/phase14_end_to_end_smoke_manifest.json: "kernel/rcu/tree.c"'
            in error
            for error in errors
        ):
            print("self-test expected failure when the shared smoke manifest lost a blocked anchor marker", file=sys.stderr)
            return 1

        write_text(broken_manifest_path, required_text(MANIFEST_PATH))

        broken_manifest_path.write_text(
            "{\n" + required_text(MANIFEST_PATH),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "invalid json in zigux/tests/phase14_end_to_end_smoke_manifest.json:"
            in error
            for error in errors
        ):
            print("self-test expected failure when the shared smoke manifest JSON was invalid", file=sys.stderr)
            return 1

        write_text(broken_manifest_path, required_text(MANIFEST_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "Attached-toolchain fallback examples:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: Attached-toolchain fallback examples:"
            in error
            for error in errors
        ):
            print("self-test expected failure when the attached-toolchain fallback heading drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`"
            in error
            for error in errors
        ):
            print("self-test expected failure when the attached-toolchain fallback example drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`\n",
                "- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`\n"
                "- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig` (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected failure when the attached-toolchain smoke fallback command duplicated", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope."
            in error
            for error in errors
        ):
            print("self-test expected failure when the attached-toolchain scope boundary drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "Fallback path:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: Fallback path:"
            in error
            for error in errors
        ):
            print("self-test expected failure when the fallback-path heading drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- review blocker status: `blocked_on_stay_in_c_evidence`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - review blocker status: `blocked_on_stay_in_c_evidence`"
            in error
            for error in errors
        ):
            print("self-test expected failure when the explicit review-blocker status drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift."
            in error
            for error in errors
        ):
            print("self-test expected failure when the smoke-note parking guidance drifted", file=sys.stderr)
            return 1

        write_text(broken_smoke_path, required_text(SMOKE_SURVEY_PATH))

        broken_checklist_path = root / "Documentation/zigux/review-checklist.md"
        broken_checklist_path.write_text(
            broken_checklist_path.read_text(encoding="utf-8").replace(
                "if the change touches the shared Phase 14 smoke packet\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/review-checklist.md: if the change touches the shared Phase 14 smoke packet"
            in error
            for error in errors
        ):
            print("self-test expected failure when the review-checklist packet prompt drifted", file=sys.stderr)
            return 1

        write_text(broken_checklist_path, required_text("Documentation/zigux/review-checklist.md"))

        broken_checklist_path.write_text(
            broken_checklist_path.read_text(encoding="utf-8").replace(
                "same study-only stay-in-C posture without implying an active deep-core port claim?\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/review-checklist.md: same study-only stay-in-C posture without implying an active deep-core port claim?"
            in error
            for error in errors
        ):
            print("self-test expected failure when the review-checklist stay-in-C prompt drifted", file=sys.stderr)
            return 1

        write_text(broken_checklist_path, required_text("Documentation/zigux/review-checklist.md"))

        broken_checklist_path.write_text(
            broken_checklist_path.read_text(encoding="utf-8").replace(
                "if the change touches the shared Phase 14 smoke packet\n",
                "if the change touches the shared Phase 14 smoke packet\n"
                "if the change touches the shared Phase 14 smoke packet\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/review-checklist.md: if the change touches the shared Phase 14 smoke packet (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected failure when the review-checklist packet prompt duplicated", file=sys.stderr)
            return 1

        write_text(broken_checklist_path, required_text("Documentation/zigux/review-checklist.md"))

        broken_checklist_path.write_text(
            broken_checklist_path.read_text(encoding="utf-8").replace(
                "same study-only stay-in-C posture without implying an active deep-core port claim?\n",
                "same study-only stay-in-C posture without implying an active deep-core port claim?\n"
                "same study-only stay-in-C posture without implying an active deep-core port claim?\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "marker count drift in Documentation/zigux/review-checklist.md: same study-only stay-in-C posture without implying an active deep-core port claim? (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected failure when the review-checklist stay-in-C prompt duplicated", file=sys.stderr)
            return 1

        write_text(broken_checklist_path, required_text("Documentation/zigux/review-checklist.md"))

        for rel_path in REQUIRED_FILE_MARKERS:
            broken_file = root / rel_path
            broken_file.unlink()
            errors = check(root)
            expected_error = f"missing file: {rel_path}"
            if expected_error not in errors:
                print(f"self-test expected missing-file failure for {rel_path}", file=sys.stderr)
                return 1
            write_text(broken_file, required_text(rel_path))

        current_checker_path.write_text(
            original_checker_source.replace(MARKER, "PHASE14_CHECK_PACKET=broken_marker"),
            encoding="utf-8",
        )
        errors = check(root)
        if "checker marker missing from checker source" not in errors:
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
