#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the current Phase 14 rollback-owner packet.

This lane stays narrow on purpose: it verifies the shared smoke manifest,
smoke note, release-boundary note, review checklist, and local make route
around the current study-only rollback posture on `master` without reopening
older missing notes or anchor-local survey ownership.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"
VALIDATION_GATE = (
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all "
    "&& make -C zigux phase14"
)
ROLLBACK_OWNER = "Repo Tooling Pod"
STATUS_BUCKET = "study_only"
TESTS_README_CHECKER_PATH = "scripts/zigux/check-phase14-tests-readme-smoke-summary.py"
SELF_TEST_SHARED_SURVEYED_COMMIT = "b9afa7c3be853219eba57856e08aeea900414116"
SMOKE_NOTE_SHARED_GUARD_MARKER = (
    "- `zigux/Makefile` now replays `scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test`, "
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`, and "
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test` before the three live checker invocations inside "
    "`make -C zigux phase14-validate`, while `scripts/zigux/validate-phase14.py` continues to rerun "
    f"`{TESTS_README_CHECKER_PATH}` inside that same validator-first route. That keeps all four dedicated Phase 14 "
    "drift guards on the shared contract path without implying a separate tests-readme make target that current `master` "
    "does not ship."
)
ATTACHED_TOOLCHAIN_EXAMPLES = [
    "- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`",
    "- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`",
    "- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`",
]
ANCHOR_MANIFEST_MARKERS = [
    "- `zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "- `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- `zigux/tests/phase14_ring_buffer_manifest.json`",
    "- `zigux/tests/phase14_rcu_tree_manifest.json`",
]
ROLLBACK_THRESHOLD_MARKER = "- rollback threshold: `0` tolerated same-packet drifts across anchor-local manifests, anchor-local survey notes, the compile shard matrix, and shared replay wiring"
ROLLBACK_FALLBACK_PATH_MARKER = "- fallback path: keep this shared smoke lane parked and rerun `make -C zigux phase14-validate` before reopening any anchor-local or shared follow-up"
ROLLBACK_TRIGGER_MARKERS = [
    "  - anchor-local manifest drift",
    "  - anchor-local survey note drift",
    "  - compile shard matrix drift",
    "  - shared replay wiring drift",
]
RELEASE_BOUNDARY_MARKERS = [
    "- bounded-internal sequencing guard: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain the two study-only anchors that can still receive same-phase bounded boundary-map or concurrency-audit follow-through, while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors carried by the current Phase 14 shared smoke packet through their dedicated Phase 14 survey and manifest evidence instead of active delivery lanes; any status-change or reopen request still belongs to the Phase 15 freeze-map governance packet",
    "- `kernel/rcu/tree.c`: remains blocked from active delivery and is currently governed by the shared smoke packet plus its dedicated Phase 14 survey note `Documentation/zigux/phase14-rcu-tree-survey.md` and manifest `zigux/tests/phase14_rcu_tree_manifest.json`; the Phase 15 readiness and handoff packet only governs any later freeze-map status review, so `zigux/tests/phase14_rcu_tree_survey.zig` remains the current full-bundle-only freeze-in-C survey replay rather than a placeholder bridge or status-change claim",
    "- `net/core/skbuff.c`: remains blocked from active delivery and is currently governed by the shared smoke packet plus its dedicated Phase 14 survey note `Documentation/zigux/phase14-skbuff-bridge-survey.md` and manifest `zigux/tests/phase14_skbuff_bridge_manifest.json`; the Phase 15 freeze-map governance packet only owns any later status-change discussion, so the current lane stays a Phase 14 review-only bridge packet rather than an active delivery lane",
]
RELEASE_BOUNDARY_FALLBACK_MARKER = (
    "- attached-toolchain replay fallback: `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`, "
    "`ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`, and "
    "`ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14` remain the release-facing fallback when neither "
    "the repo-local `.zig-toolchain` candidate nor the shell's default `zig` binary is available, so the same "
    "bounded smoke-shard, full-bundle, and combined replay routes stay usable without inventing a separate "
    "environment-only command packet"
)
SELF_TEST_ANCHOR_PACKETS = [
    {
        "lane_key": "P14-L04",
        "manifest_path": "zigux/tests/phase14_workqueue_bridge_manifest.json",
        "surveyed_commit": "9b98d3b9c812840bf279508030be0b8de093736c",
    },
    {
        "lane_key": "P14-L11",
        "manifest_path": "zigux/tests/phase14_skbuff_bridge_manifest.json",
        "surveyed_commit": "f05e02445443e7743c3675a6f8ca4f70f6e736fb",
    },
    {
        "lane_key": "P14-L08",
        "manifest_path": "zigux/tests/phase14_ring_buffer_manifest.json",
        "surveyed_commit": "99cd3249c4bab05b74227ed7ca3869284e818588",
    },
    {
        "lane_key": "P14-L16",
        "manifest_path": "zigux/tests/phase14_rcu_tree_manifest.json",
        "surveyed_commit": "4c889233d157960514b241bcd5aff7cac5fda312",
    },
]
MAKEFILE_EXACT_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]

ROOT = Path.cwd()
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
MAKEFILE_PATH = Path("zigux/Makefile")

def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")

def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")

def anchor_note_fragment(packet: dict[str, object]) -> str:
    return (
        f"`{packet['manifest_path']}`, lane `{packet['lane_key']}`, "
        f"surveyed commit `{packet['surveyed_commit']}`"
    )

def require_exact_line_count(errors: list[str], rel_path: str, text: str) -> None:
    lines = text.splitlines()
    for marker in MAKEFILE_EXACT_LINES:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} "
                f"(expected 1, found {count})"
            )

def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    for rel in [MANIFEST_PATH, SMOKE_NOTE_PATH, RELEASE_BOUNDARY_PATH, CHECKLIST_PATH, MAKEFILE_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {MANIFEST_PATH.as_posix()}: {exc}")
        return errors

    productization = manifest.get("productization")
    if not isinstance(productization, dict):
        errors.append("manifest:productization missing")
    else:
        if productization.get("status_bucket") != STATUS_BUCKET:
            errors.append("manifest:productization.status_bucket drifted")
        if productization.get("rollback_owner") != ROLLBACK_OWNER:
            errors.append("manifest:productization.rollback_owner drifted")
        if productization.get("validation_gate") != VALIDATION_GATE:
            errors.append("manifest:productization.validation_gate drifted")

    if manifest.get("phase") != "Phase 14":
        errors.append(f"manifest:phase {manifest.get('phase')!r} != 'Phase 14'")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or len(surveyed_commit) != 40 or any(
        ch not in "0123456789abcdef" for ch in surveyed_commit
    ):
        errors.append("manifest:surveyed_commit must be a 40-character lowercase hex sha")
        surveyed_commit = None
    if manifest.get("smoke_commands") != [
        "make -C zigux phase14-validate",
        "make -C zigux phase14-test",
        "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
        "make -C zigux phase14",
    ]:
        errors.append("manifest:smoke_commands drifted")
    if manifest.get("smoke_shard_commands") != [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
        "make -C zigux phase14-smoke",
    ]:
        errors.append("manifest:smoke_shard_commands drifted")

    anchor_packets = manifest.get("anchor_packets")
    if not isinstance(anchor_packets, list) or len(anchor_packets) != 4:
        errors.append("manifest:anchor_packets must list four shared anchors")
        anchor_packets = []

    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    for marker in [
        "- `PHASE14_STAY_IN_C_BOUNDARY=explicit`",
        f"- rollback owner: `{ROLLBACK_OWNER}`",
        f"- status bucket: `{STATUS_BUCKET}`",
        f"- validation gate: `{VALIDATION_GATE}`",
        ROLLBACK_THRESHOLD_MARKER,
        ROLLBACK_FALLBACK_PATH_MARKER,
        "- automatic return-to-blocked triggers:",
        *ROLLBACK_TRIGGER_MARKERS,
        "- attached-toolchain fallback examples for this note's shared replay routes only:",
        SMOKE_NOTE_SHARED_GUARD_MARKER,
        "Keep this shared smoke lane parked unless one of the four anchor-local manifests, survey notes, the compile shard matrix, or the shared replay wiring drifts.",
    ]:
        if marker not in smoke_note:
            errors.append(f"missing marker in {SMOKE_NOTE_PATH.as_posix()}: {marker}")
    if surveyed_commit is not None:
        for marker in [
            f"- survey provenance captured against verified `master` head `{surveyed_commit}`",
            f"- verified `master` head: `{surveyed_commit}`",
        ]:
            if marker not in smoke_note:
                errors.append(f"missing marker in {SMOKE_NOTE_PATH.as_posix()}: {marker}")

    for marker in ATTACHED_TOOLCHAIN_EXAMPLES + ANCHOR_MANIFEST_MARKERS + ROLLBACK_TRIGGER_MARKERS:
        count = smoke_note.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {SMOKE_NOTE_PATH.as_posix()}: {marker} "
                f"(expected 1, found {count})"
            )

    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    for marker in [*RELEASE_BOUNDARY_MARKERS, RELEASE_BOUNDARY_FALLBACK_MARKER]:
        if marker not in release_boundary:
            errors.append(
                f"missing marker in {RELEASE_BOUNDARY_PATH.as_posix()}: {marker}"
            )

    for packet in anchor_packets:
        if not isinstance(packet, dict):
            errors.append("manifest:anchor_packet must be an object")
            continue
        packet_field_errors: list[str] = []
        for key in ["manifest_path", "lane_key", "surveyed_commit"]:
            value = packet.get(key)
            if not isinstance(value, str) or not value:
                packet_field_errors.append(f"manifest:anchor_packet missing {key}")
        if packet_field_errors:
            errors.extend(packet_field_errors)
            continue
        fragment = anchor_note_fragment(packet)
        if fragment not in smoke_note:
            errors.append(
                "shared smoke note anchor metadata drifted for "
                f"{packet['manifest_path']}: expected fragment {fragment}"
            )

    checklist = read_text(root, CHECKLIST_PATH)
    for marker in [
        "if the change touches the shared Phase 14 smoke packet",
        "same study-only stay-in-C posture without implying an active deep-core port claim?",
    ]:
        if marker not in checklist:
            errors.append(f"missing marker in {CHECKLIST_PATH.as_posix()}: {marker}")

    makefile = read_text(root, MAKEFILE_PATH)
    for marker in [
        "phase14-validate:",
        "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
        "phase14-smoke:",
        "phase14-test:",
        "phase14: phase14-validate phase14-smoke phase14-test",
    ]:
        if marker not in makefile:
            errors.append(f"missing marker in {MAKEFILE_PATH.as_posix()}: {marker}")
    require_exact_line_count(errors, MAKEFILE_PATH.as_posix(), makefile)

    return errors

def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def current_manifest_text() -> str:
    return json.dumps(
        {
            "lane_key": "P14-L03",
            "phase": "Phase 14",
            "surveyed_commit": SELF_TEST_SHARED_SURVEYED_COMMIT,
            "productization": {
                "status_bucket": STATUS_BUCKET,
                "validation_gate": VALIDATION_GATE,
                "rollback_owner": ROLLBACK_OWNER,
            },
            "smoke_commands": [
                "make -C zigux phase14-validate",
                "make -C zigux phase14-test",
                "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
                "make -C zigux phase14",
            ],
            "smoke_shard_commands": [
                "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
                "make -C zigux phase14-smoke",
            ],
            "anchor_packets": SELF_TEST_ANCHOR_PACKETS,
        },
        indent=2,
    ) + "\n"

def current_smoke_note_text() -> str:
    parts = [
        "- `PHASE14_STAY_IN_C_BOUNDARY=explicit`",
        f"- survey provenance captured against verified `master` head `{SELF_TEST_SHARED_SURVEYED_COMMIT}`",
        f"- verified `master` head: `{SELF_TEST_SHARED_SURVEYED_COMMIT}`",
        f"- rollback owner: `{ROLLBACK_OWNER}`",
        f"- status bucket: `{STATUS_BUCKET}`",
        f"- validation gate: `{VALIDATION_GATE}`",
        ROLLBACK_THRESHOLD_MARKER,
        ROLLBACK_FALLBACK_PATH_MARKER,
        "- automatic return-to-blocked triggers:",
        *ROLLBACK_TRIGGER_MARKERS,
        "- attached-toolchain fallback examples for this note's shared replay routes only:",
        *ATTACHED_TOOLCHAIN_EXAMPLES,
        *[
            f"- anchor packet: {anchor_note_fragment(packet)}"
            for packet in SELF_TEST_ANCHOR_PACKETS
        ],
        *ANCHOR_MANIFEST_MARKERS,
        SMOKE_NOTE_SHARED_GUARD_MARKER,
        "Keep this shared smoke lane parked unless one of the four anchor-local manifests, survey notes, the compile shard matrix, or the shared replay wiring drifts.",
    ]
    return "\n".join(parts) + "\n"

def current_release_boundary_text() -> str:
    return "\n".join(
        [
            *RELEASE_BOUNDARY_MARKERS,
            RELEASE_BOUNDARY_FALLBACK_MARKER,
            "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
            "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
        ]
    ) + "\n"

def current_checklist_text() -> str:
    return (
        "if the change touches the shared Phase 14 smoke packet\n"
        "same study-only stay-in-C posture without implying an active deep-core port claim?\n"
    )

def current_makefile_text() -> str:
    return "\n".join(
        [
            "phase14-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
            "phase14-smoke:",
            "phase14-test:",
            "phase14: phase14-validate phase14-smoke phase14-test",
        ]
    ) + "\n"

def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write(root, MANIFEST_PATH, current_manifest_text())
        write(root, SMOKE_NOTE_PATH, current_smoke_note_text())
        write(root, RELEASE_BOUNDARY_PATH, current_release_boundary_text())
        write(root, CHECKLIST_PATH, current_checklist_text())
        write(root, MAKEFILE_PATH, current_makefile_text())
        if errors := check(root):
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        write(
            root,
            SMOKE_NOTE_PATH,
            current_smoke_note_text().replace(
                f"- verified `master` head: `{SELF_TEST_SHARED_SURVEYED_COMMIT}`\n",
                "",
                1,
            ),
        )
        if not any("verified `master` head" in error for error in check(root)):
            print("self-test expected shared surveyed-head note failure", file=sys.stderr)
            return 1
        write(root, SMOKE_NOTE_PATH, current_smoke_note_text())

        write(
            root,
            MANIFEST_PATH,
            current_manifest_text().replace(
                f"\"surveyed_commit\": \"{SELF_TEST_SHARED_SURVEYED_COMMIT}\"",
                "\"surveyed_commit\": \"not-a-commit\"",
                1,
            ),
        )
        if not any("manifest:surveyed_commit" in error for error in check(root)):
            print("self-test expected manifest surveyed-commit format failure", file=sys.stderr)
            return 1
    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass")
    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST_CASE_COUNT=18")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    errors = check(ROOT)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 rollback-threshold sequencing packet validated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
