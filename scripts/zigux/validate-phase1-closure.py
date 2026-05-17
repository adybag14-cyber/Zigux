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
BUILD_FILE_REL = Path("zigux/tests/build.zig")
SMOKE_FILE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")

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
    "current_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "gap_packet": "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,scripts/zigux/check-phase1-bench.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
    "shared_sync_pending": "`PHASE1_SHARED_REMINDER_SYNC_PENDING=Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md`",
    "validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "next_step": "`PHASE1_NEXT_SAFE_STEP=realign Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md with the restored closure packet before widening into zigux/tests/phase1_helpers.zig or bench claims`",
}

REQUIRED_BUILD_MARKERS = {
    "step_binding": 'const phase1_step = b.step(',
    "step_description": '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
    "root_source": '"phase1_host_tools_smoke.zig"',
}

REQUIRED_SMOKE_MARKERS = {
    "argv_split_decl": '@hasDecl(argv_split, "argvSplit")',
    "cmdline_decl": '@hasDecl(cmdline, "memparse")',
    "find_bit_decl": '@hasDecl(find_bit, "findFirstBit")',
    "bitmap_decl": '@hasDecl(bitmap, "setRange")',
}

REQUIRED_SCRIPTS_README_MARKERS = {
    "phase1_flow": "the restored closure note, the live owner-map and string-review guards, the narrow closure validator, and the shared tests-root smoke anchor",
    "validator_presence": "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner marker, and current-master-safe closure packet explicit from the scripts root",
    "companion_surfaces": "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet",
    "gap_list": "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "narrow_route": "`python3 scripts/zigux/validate-phase1-closure.py` and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` now replay the narrow closure-side validation route that current `master` honestly supports without claiming the older parity, bench, or Makefile wrappers have returned",
}

FORBIDDEN_SCRIPTS_README_MARKERS = {
    "stale_missing_closure": "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`",
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


def require_absent(text: str, label: str, marker: str) -> list[str]:
    if marker in text:
        return [f"{label}:forbidden_marker_present"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    closure_path = root / CLOSURE_NOTE_REL
    manifest_path = root / MANIFEST_REL
    build_path = root / BUILD_FILE_REL
    smoke_path = root / SMOKE_FILE_REL
    scripts_readme_path = root / SCRIPTS_README_REL

    for relpath, path in (
        (CLOSURE_NOTE_REL, closure_path),
        (MANIFEST_REL, manifest_path),
        (BUILD_FILE_REL, build_path),
        (SMOKE_FILE_REL, smoke_path),
        (SCRIPTS_README_REL, scripts_readme_path),
    ):
        if not path.exists():
            failures.append(f"missing_file:{relpath.as_posix()}")
            return failures

    closure_text = load_text(closure_path)
    for label, marker in REQUIRED_NOTE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, f"closure_note:{label}", marker))

    build_text = load_text(build_path)
    for label, marker in REQUIRED_BUILD_MARKERS.items():
        failures.extend(require_exact_occurrence(build_text, f"build_zig:{label}", marker))

    smoke_text = load_text(smoke_path)
    for label, marker in REQUIRED_SMOKE_MARKERS.items():
        failures.extend(require_exact_occurrence(smoke_text, f"phase1_host_tools_smoke:{label}", marker))

    scripts_readme_text = load_text(scripts_readme_path)
    for label, marker in REQUIRED_SCRIPTS_README_MARKERS.items():
        failures.extend(require_exact_occurrence(scripts_readme_text, f"scripts_readme:{label}", marker))
    for label, marker in FORBIDDEN_SCRIPTS_README_MARKERS.items():
        failures.extend(require_absent(scripts_readme_text, f"scripts_readme:{label}", marker))

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
            "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
            "",
            "## Current Repo-Reality Gaps",
            "",
            "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,scripts/zigux/check-phase1-bench.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
            "- `PHASE1_SHARED_REMINDER_SYNC_PENDING=Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md`",
            "",
            "## Closure Validation",
            "",
            "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
            "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
            "",
            "## Next Step",
            "",
            "- `PHASE1_NEXT_SAFE_STEP=realign Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md with the restored closure packet before widening into zigux/tests/phase1_helpers.zig or bench claims`",
            "",
        ]
    )


def sample_scripts_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            "- the restored closure note, the live owner-map and string-review guards, the narrow closure validator, and the shared tests-root smoke anchor",
            "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner marker, and current-master-safe closure packet explicit from the scripts root",
            "- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet",
            "- `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
            "- `python3 scripts/zigux/validate-phase1-closure.py` and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` now replay the narrow closure-side validation route that current `master` honestly supports without claiming the older parity, bench, or Makefile wrappers have returned",
            "",
        ]
    )


def sample_build_text() -> str:
    return "\n".join(
        [
            'const std = @import("std");',
            "",
            "pub fn build(b: *std.Build) void {",
            '    _ = b.path("phase1_host_tools_smoke.zig");',
            '    const phase1_step = b.step("phase1-host-tools-smoke", "Run the shared Phase 1 host-tools smoke anchor from zigux/tests");',
            "    _ = phase1_step;",
            "}",
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
    write_file(root, SCRIPTS_README_REL, sample_scripts_readme_text())
    write_file(root, BUILD_FILE_REL, sample_build_text())
    write_file(
        root,
        SMOKE_FILE_REL,
        "\n".join(
            [
                'const std = @import("std");',
                'const argv_split = @import("argv_split");',
                'const cmdline = @import("cmdline");',
                'const find_bit = @import("find_bit");',
                'const bitmap = @import("bitmap");',
                'test "phase1 host-tools smoke imports the live helper modules" {',
                '    try std.testing.expect(@hasDecl(argv_split, "argvSplit"));',
                '    try std.testing.expect(@hasDecl(cmdline, "memparse"));',
                '    try std.testing.expect(@hasDecl(find_bit, "findFirstBit"));',
                '    try std.testing.expect(@hasDecl(bitmap, "setRange"));',
                "}",
                "",
            ]
        ),
    )
    write_file(root, MANIFEST_REL, json.dumps(sample_manifest(), indent=2) + "\n")


def run_self_test() -> int:
    cases = [("success", None, None)]
    cases.extend((f"remove_{label}", "note", marker) for label, marker in REQUIRED_NOTE_MARKERS.items())
    cases.extend((f"remove_build_{label}", "build", marker) for label, marker in REQUIRED_BUILD_MARKERS.items())
    cases.extend((f"remove_smoke_{label}", "smoke", marker) for label, marker in REQUIRED_SMOKE_MARKERS.items())
    cases.extend((f"remove_scripts_{label}", "scripts", marker) for label, marker in REQUIRED_SCRIPTS_README_MARKERS.items())
    cases.extend(
        [
            ("scripts_forbidden_marker", "scripts_forbidden", next(iter(FORBIDDEN_SCRIPTS_README_MARKERS.values()))),
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
            elif mode == "build" and marker:
                build_path = root / BUILD_FILE_REL
                text = build_path.read_text(encoding="utf-8")
                build_path.write_text(text.replace(marker, "", 1), encoding="utf-8")
            elif mode == "smoke" and marker:
                smoke_path = root / SMOKE_FILE_REL
                text = smoke_path.read_text(encoding="utf-8")
                smoke_path.write_text(text.replace(marker, "", 1), encoding="utf-8")
            elif mode == "scripts" and marker:
                scripts_path = root / SCRIPTS_README_REL
                text = scripts_path.read_text(encoding="utf-8")
                scripts_path.write_text(text.replace(marker, "", 1), encoding="utf-8")
            elif mode == "scripts_forbidden" and marker:
                scripts_path = root / SCRIPTS_README_REL
                text = scripts_path.read_text(encoding="utf-8")
                scripts_path.write_text(text + marker + "\n", encoding="utf-8")
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
