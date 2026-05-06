#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the shared Phase 14 rollback-owner and sequencing-split packet.
It keeps the manifest, shared smoke note, release-boundary note, and review checklist
aligned around the current stay-in-C and freeze-in-C split on master.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"
REQUIRED_FILE_MARKERS = {
    "zigux/tests/phase14_end_to_end_smoke_manifest.json": [
        '"rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence"',
        '"kernel/workqueue.c"',
        '"kernel/trace/ring_buffer.c"',
        '"kernel/rcu/tree.c"',
        '"net/core/skbuff.c"',
    ],
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "`PHASE14_STAY_IN_C_BOUNDARY=explicit`",
        "- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`",
        "Attached-toolchain fallback examples:",
        "- `make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig`",
        "- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`",
        "- `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`",
        "- `make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig`",
        "Fallback path:",
        "Keep `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.",
        "Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift.",
        "- review blocker status: `blocked_on_stay_in_c_evidence`",
        "- `zigux/tests/phase14_workqueue_bridge_manifest.json`",
        "- `zigux/tests/phase14_skbuff_bridge_manifest.json`",
        "- `zigux/tests/phase14_ring_buffer_manifest.json`",
        "- `zigux/tests/phase14_rcu_tree_manifest.json`",
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")
    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_text(
            root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            MARKER + "\nraise SystemExit(0)\n",
        )
        for rel_path, markers in REQUIRED_FILE_MARKERS.items():
            write_text(root / rel_path, "\n".join(markers) + "\n")

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
            "\n".join(REQUIRED_FILE_MARKERS["Documentation/zigux/phase14-release-boundary-survey.md"]) + "\n",
        )

        broken_smoke_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
        broken_smoke_path.write_text(
            broken_smoke_path.read_text(encoding="utf-8").replace(
                "- `zigux/tests/phase14_rcu_tree_manifest.json`\n",
                "",
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: - `zigux/tests/phase14_rcu_tree_manifest.json`"
            in error
            for error in errors
        ):
            print("self-test expected failure when shared smoke manifest inventory drifted", file=sys.stderr)
            return 1

        write_text(
            broken_smoke_path,
            "\n".join(REQUIRED_FILE_MARKERS["Documentation/zigux/phase14-end-to-end-smoke-survey.md"]) + "\n",
        )

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
