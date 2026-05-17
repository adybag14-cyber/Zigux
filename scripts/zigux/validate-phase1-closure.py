#!/usr/bin/env python3
"""Validate the current-master-safe Phase 1 closure note against the live helper manifest."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

REQUIRED_NOTE_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=partial`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "manifest": "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "current_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,zigux/tests/README.md,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "gap_packet": "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,scripts/zigux/check-phase1-bench.py,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
    "shared_sync_pending": "`PHASE1_SHARED_REMINDER_SYNC_PENDING=Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,zigux/tests/README.md`",
    "validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "next_step": "`PHASE1_NEXT_SAFE_STEP=restore zigux/tests/build.zig and then one missing replay-side closure companion at a time before claiming the older validator-first or bench routes as current-master evidence again`",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(load_text(path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    closure_path = root / CLOSURE_NOTE_REL
    manifest_path = root / MANIFEST_REL

    if not closure_path.exists():
        failures.append(f"missing_file:{CLOSURE_NOTE_REL.as_posix()}")
        return failures
    if not manifest_path.exists():
        failures.append(f"missing_file:{MANIFEST_REL.as_posix()}")
        return failures

    closure_text = load_text(closure_path)
    for label, marker in REQUIRED_NOTE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, f"closure_note:{label}", marker))

    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        failures.append("manifest:expected_json_object")
        return failures

    if manifest.get("phase") != "Phase 1":
        failures.append("manifest:phase")
    if manifest.get("status") != "closed":
        failures.append("manifest:status")
    if manifest.get("helper_count") != 13:
        failures.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        failures.append("manifest:helpers")

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_note_text() -> str:
    return "\n".join(
        [
            "# Phase 1 Closure",
            "",
            "This note restores the Lane 15 closure anchor in a current-master-safe form.",
            "",
            "## Status",
            "",
            "- `PHASE1_STATUS=parked`",
            "- `PHASE1_CLOSURE_RESTORE_STATE=partial`",
            "- `PHASE1_HELPER_COUNT=13`",
            "- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
            "",
            "## Current Reminder Packet",
            "",
            "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,zigux/tests/README.md,zigux/tests/fixtures/phase1_helper_manifest.json`",
            "",
            "## Current Repo-Reality Gaps",
            "",
            "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,scripts/zigux/check-phase1-bench.py,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
            "- `PHASE1_SHARED_REMINDER_SYNC_PENDING=Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,zigux/tests/README.md`",
            "",
            "## Closure Validation",
            "",
            "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
            "",
            "## Next Step",
            "",
            "- `PHASE1_NEXT_SAFE_STEP=restore zigux/tests/build.zig and then one missing replay-side closure companion at a time before claiming the older validator-first or bench routes as current-master evidence again`",
            "",
        ]
    )


def sample_manifest() -> dict[str, Any]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": EXPECTED_HELPERS,
    }


def build_sample_repo(root: Path) -> None:
    write_file(root, CLOSURE_NOTE_REL, sample_note_text())
    write_file(root, MANIFEST_REL, json.dumps(sample_manifest(), indent=2) + "\n")


def run_self_test() -> int:
    cases = [("success", None, None)]
    cases.extend((f"remove_{label}", "note", marker) for label, marker in REQUIRED_NOTE_MARKERS.items())
    cases.extend(
        [
            ("manifest_wrong_phase", "manifest_phase", None),
            ("manifest_wrong_status", "manifest_status", None),
            ("manifest_wrong_helper_count", "manifest_count", None),
            ("manifest_wrong_helpers", "manifest_helpers", None),
        ]
    )

    for name, mode, marker in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mode == "note" and marker:
                note_path = root / CLOSURE_NOTE_REL
                text = note_path.read_text(encoding="utf-8")
                note_path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
            elif mode and mode.startswith("manifest_"):
                manifest_path = root / MANIFEST_REL
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if mode == "manifest_phase":
                    manifest["phase"] = "Phase X"
                elif mode == "manifest_status":
                    manifest["status"] = "parked"
                elif mode == "manifest_count":
                    manifest["helper_count"] = 12
                elif mode == "manifest_helpers":
                    manifest["helpers"] = manifest["helpers"][:-1]
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for item in failures:
                        print(item)
                    return 1
                continue
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("phase1-closure-self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
