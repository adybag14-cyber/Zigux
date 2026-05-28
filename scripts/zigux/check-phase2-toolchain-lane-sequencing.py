#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

LANE_NOTE = Path("Documentation/zigux/phase2-toolchain-lane-sequencing.md")
BOOTSTRAP_NOTE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
CROSS_TARGETS = Path("zigux/tests/fixtures/phase2_cross_targets.json")
MAKEFILE = Path("zigux/Makefile")

LANE_NOTE_MARKERS = (
    "# Phase 2 Toolchain Lane Sequencing",
    "Use this note when a Phase 2 change touches the shared toolchain packet recorded in `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-lane-sequencing.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`.",
    "shared sequencing lane `P2-Y10` owns only shared Phase 2 toolchain reminder and anti-overlap work",
    "shared backlog truthfulness lane `P2-Y12` owns turning current cross-family backlog evidence into one bounded next-safe-step correction",
    "Makefile toolchain lane `P2-X09` owns the repo-local `.zig-toolchain` fallback and the six Linux-style Phase 2 routes in `zigux/Makefile`",
    "fixdep route-governance lane `P2-Y01` owns fixdep gate-marker and route-inventory wording",
    "fixdep closure lane `P2-Y02` owns bounded next-step or closure truthfulness",
    "genksyms roadmap-survey lane `P2-L07` owns repo-versus-roadmap evidence",
    "genksyms note-truthfulness lane `P2-L12` owns same-family survey or closure wording corrections",
    "genksyms fixture lane `P2-L10` owns bounded genksyms bridge fixture and expected-output drift",
    "genksyms gate lane `P2-L11` owns workflow-backed replay or validator wiring",
    "kconfig bridge behavior lane `P2-X05` owns `scripts/zigux/kconfig/conf_bridge.zig` behavior follow-up",
    "kconfig bridge checker parity lane `P2-L18` owns the current `conf_bridge` checker-and-manifest helper-anchor parity",
    "confdata survey lane `P2-L19` stays parked as the scaffold-closed survey note",
    "confdata checker lane `P2-Y07` owns current checker-underflow repair",
    "confdata bridge truthfulness lane `P2-L24` owns malformed-quote and helper-anchor follow-through",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "- `make -C zigux phase2-toolchain`",
    "- `make -C zigux phase2-tools`",
    "- `make -C zigux phase2-kconfig`",
    "- `make -C zigux phase2-cross`",
    "- `make -C zigux phase2`",
)

BOOTSTRAP_NOTE_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)

EXPECTED_MAKE_WRAPPERS = [
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

EXPECTED_SHARED_CHECKERS = [
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(root: Path, rel_path: Path) -> str:
    path = root / rel_path
    if not path.is_file():
        raise SystemExit(f"required file missing: {rel_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def read_json_dict(root: Path, rel_path: Path) -> dict:
    path = root / rel_path
    if not path.is_file():
        raise SystemExit(f"required file missing: {rel_path.as_posix()}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {rel_path.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in {rel_path.as_posix()}")
    return payload


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    lane_note_text = read_text(root, LANE_NOTE)
    bootstrap_text = read_text(root, BOOTSTRAP_NOTE)
    review_text = read_text(root, REVIEW_CHECKLIST)
    makefile_text = read_text(root, MAKEFILE)
    tool_manifest = read_json_dict(root, TOOL_MANIFEST)
    cross_targets = read_json_dict(root, CROSS_TARGETS)

    issues.extend(collect_marker_issues(lane_note_text, LANE_NOTE_MARKERS, "MISSING_LANE_NOTE_MARKER"))
    issues.extend(collect_marker_issues(bootstrap_text, BOOTSTRAP_NOTE_MARKERS, "MISSING_BOOTSTRAP_NOTE_MARKER"))
    issues.extend(collect_marker_issues(review_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKER"))
    issues.extend(collect_marker_issues(makefile_text, MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKER"))

    if tool_manifest.get("phase") != "Phase 2":
        issues.append(("TOOL_MANIFEST_TOP_LEVEL", "phase"))
    if tool_manifest.get("status") != "active":
        issues.append(("TOOL_MANIFEST_TOP_LEVEL", "status"))

    present_surfaces = tool_manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("TOOL_MANIFEST_SHAPE", "present_surfaces"))
    else:
        make_wrappers = present_surfaces.get("make_wrappers")
        if make_wrappers != EXPECTED_MAKE_WRAPPERS:
            issues.append(("TOOL_MANIFEST_MAKE_WRAPPERS", repr(make_wrappers)))

        checkers = present_surfaces.get("checkers")
        if not isinstance(checkers, list):
            issues.append(("TOOL_MANIFEST_SHAPE", "checkers"))
        else:
            for checker in EXPECTED_SHARED_CHECKERS:
                if checker not in checkers:
                    issues.append(("TOOL_MANIFEST_MISSING_CHECKER", checker))

    if cross_targets.get("phase") != "Phase 2":
        issues.append(("CROSS_TARGETS_TOP_LEVEL", "phase"))
    if cross_targets.get("status") != "active":
        issues.append(("CROSS_TARGETS_TOP_LEVEL", "status"))
    if cross_targets.get("route") != "make -C zigux phase2-cross":
        issues.append(("CROSS_TARGETS_TOP_LEVEL", "route"))

    expected_cross_targets = [
        {
            "target": "x86_64-linux",
            "review_status": "pinned bootstrap archive",
            "validation_mode": "archive_required",
            "route": "make -C zigux phase2-cross",
        },
        {
            "target": "aarch64-linux",
            "review_status": "route contract only",
            "validation_mode": "route_contract_only",
            "route": "make -C zigux phase2-cross",
        },
    ]
    if cross_targets.get("cross_targets") != expected_cross_targets:
        issues.append(("CROSS_TARGETS_PACKET", repr(cross_targets.get("cross_targets"))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_LANE_SEQUENCING=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_good_tree(root: Path) -> None:
    write_text(root / LANE_NOTE, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root / BOOTSTRAP_NOTE, "\n".join(BOOTSTRAP_NOTE_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / MAKEFILE, "\n".join(MAKEFILE_MARKERS) + "\n")

    tool_manifest = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "make_wrappers": EXPECTED_MAKE_WRAPPERS,
            "checkers": EXPECTED_SHARED_CHECKERS,
        },
    }
    write_text(root / TOOL_MANIFEST, json.dumps(tool_manifest, indent=2) + "\n")

    cross_targets = {
        "phase": "Phase 2",
        "status": "active",
        "route": "make -C zigux phase2-cross",
        "cross_targets": [
            {
                "target": "x86_64-linux",
                "review_status": "pinned bootstrap archive",
                "validation_mode": "archive_required",
                "route": "make -C zigux phase2-cross",
            },
            {
                "target": "aarch64-linux",
                "review_status": "route contract only",
                "validation_mode": "route_contract_only",
                "route": "make -C zigux phase2-cross",
            },
        ],
    }
    write_text(root / CROSS_TARGETS, json.dumps(cross_targets, indent=2) + "\n")


def run_self_test() -> int:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_lane_sequencing_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:good_tree")
        cases_run += 1

        build_good_tree(root)
        path = root / LANE_NOTE
        path.write_text(path.read_text(encoding="utf-8").replace(LANE_NOTE_MARKERS[2], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_LANE_NOTE_MARKER", LANE_NOTE_MARKERS[2]) not in issues:
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:lane_marker")
        cases_run += 1

        build_good_tree(root)
        path = root / BOOTSTRAP_NOTE
        path.write_text(path.read_text(encoding="utf-8").replace(BOOTSTRAP_NOTE_MARKERS[2], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_BOOTSTRAP_NOTE_MARKER", BOOTSTRAP_NOTE_MARKERS[2]) not in issues:
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:bootstrap_marker")
        cases_run += 1

        build_good_tree(root)
        path = root / REVIEW_CHECKLIST
        path.write_text(path.read_text(encoding="utf-8").replace(REVIEW_CHECKLIST_MARKERS[3], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_REVIEW_CHECKLIST_MARKER", REVIEW_CHECKLIST_MARKERS[3]) not in issues:
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:review_marker")
        cases_run += 1

        build_good_tree(root)
        path = root / MAKEFILE
        path.write_text(path.read_text(encoding="utf-8").replace(MAKEFILE_MARKERS[-1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        if ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[-1]) not in issues:
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:makefile_marker")
        cases_run += 1

        build_good_tree(root)
        tool_manifest = read_json_dict(root, TOOL_MANIFEST)
        tool_manifest["present_surfaces"]["make_wrappers"] = EXPECTED_MAKE_WRAPPERS[:-1]
        write_text(root / TOOL_MANIFEST, json.dumps(tool_manifest, indent=2) + "\n")
        issues = collect_issues(root)
        if not any(code == "TOOL_MANIFEST_MAKE_WRAPPERS" for code, _ in issues):
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:manifest_wrappers")
        cases_run += 1

        build_good_tree(root)
        tool_manifest = read_json_dict(root, TOOL_MANIFEST)
        tool_manifest["present_surfaces"]["checkers"] = EXPECTED_SHARED_CHECKERS[:-1]
        write_text(root / TOOL_MANIFEST, json.dumps(tool_manifest, indent=2) + "\n")
        issues = collect_issues(root)
        if ("TOOL_MANIFEST_MISSING_CHECKER", EXPECTED_SHARED_CHECKERS[-1]) not in issues:
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:manifest_checker")
        cases_run += 1

        build_good_tree(root)
        cross_targets = read_json_dict(root, CROSS_TARGETS)
        cross_targets["cross_targets"] = cross_targets["cross_targets"][:1]
        write_text(root / CROSS_TARGETS, json.dumps(cross_targets, indent=2) + "\n")
        issues = collect_issues(root)
        if not any(code == "CROSS_TARGETS_PACKET" for code, _ in issues):
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:cross_packet")
        cases_run += 1

        build_good_tree(root)
        (root / LANE_NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise
        else:
            raise SystemExit("phase2-toolchain-lane-sequencing:self-test:missing_file")
        cases_run += 1

    print("PHASE2_TOOLCHAIN_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 toolchain lane-sequencing packet aligned with the live owner-map surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing synthetic sample tree to the given directory",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_good_tree(args.write_sample_root)
        print(f"PHASE2_TOOLCHAIN_LANE_SEQUENCING_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_LANE_SEQUENCING=pass")
    print(f"PHASE2_TOOLCHAIN_LANE_SEQUENCING_LANE_MARKER_COUNT={len(LANE_NOTE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_LANE_SEQUENCING_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_NOTE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_LANE_SEQUENCING_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_LANE_SEQUENCING_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
