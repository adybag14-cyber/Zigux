#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase13-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

FILES = [
    "scripts/zigux/validate-phase13-release.py",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
]

MAKE_MARKERS = [
    "PHONY += phase13-validate phase13-test phase13",
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "phase13-test:",
    "$(ZIG) build test --build-file zigux/tests/phase13_build.zig",
    "phase13: phase13-validate phase13-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 13 release-discipline packet",
    "make -C zigux phase13-validate",
    "Run Phase 13 shared helper tests",
    "zig build test --build-file zigux/tests/phase13_build.zig --summary all",
]

RELEASE_MARKERS = [
    "PHASE13_STATUS=active",
    "PHASE13_TRANCHE=shared-helper-bundle",
    "PHASE13_RELEASE_SURVEY=present",
    "PHASE13_RELEASE_VALIDATOR=present",
    "PHASE13_ROADMAP_ANCHOR_COUNT=4",
    "PHASE13_MANIFEST_BACKED_SURVEY_COUNT=3",
    "PHASE13_ACTIVE_ASYMMETRIC_ANCHOR_COUNT=1",
    "PHASE13_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase13-release.py",
    "PHASE13_VALIDATE_ENTRYPOINT=make -C zigux phase13-validate",
    "PHASE13_SHARED_BUILD_PRESENT=yes",
    "PHASE13_SHARED_MAKE_TARGET_PRESENT=yes",
    "PHASE13_RELEASE_CLOSED=no",
    "lib/devres.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey still missing",
    "phase13_notifier_list_reviewability.zig",
]

TRACEABILITY_MARKERS = [
    "Shared tranche entrypoints already present on `master`:",
    "`zigux/tests/phase13_build.zig`",
    "`zigux/Makefile` via `make -C zigux phase13`",
    "`lib/devres.c` is represented by real helper code, real tests, and a slice note, but not yet by a committed manifest-backed survey packet",
]

BUILD_NAME_MARKERS = [
    "phase13-libfs-tests",
    "phase13-devres-tests",
    "phase13-landlock-ruleset-tests",
    "phase13-landlock-syscalls-tests",
    "phase13-libfs-reviewability-tests",
    "phase13-notifier-list-reviewability-tests",
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE13_RELEASE_VALIDATION=fail")
    print("MISSING_PHASE13_RELEASE_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE13_RELEASE_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("release", text("Documentation/zigux/phase13-release-notes-survey.md"), RELEASE_MARKERS),
    ("traceability", text("Documentation/zigux/phase13-roadmap-traceability.md"), TRACEABILITY_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

release_text = text("Documentation/zigux/phase13-release-notes-survey.md")
for rel in [
    "scripts/zigux/validate-phase13-release.py",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase13_build.zig",
    "zigux/Makefile",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
]:
    if rel not in release_text:
        missing.append(f"release:evidence_path:{rel}")

build_text = text("zigux/tests/phase13_build.zig")
build_names = BUILD_TEST_NAME_RE.findall(build_text)
if build_names != BUILD_NAME_MARKERS:
    missing.append("build:test_names")
depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
if len(depend_steps) != 6:
    missing.append(f"build:depend_step_count={len(depend_steps)}")

for manifest_path, lane_key, anchor in [
    ("zigux/tests/phase13_libfs_manifest.json", "P13-L06", "fs/libfs.c"),
    ("zigux/tests/phase13_landlock_ruleset_manifest.json", "P13-L12", "security/landlock/ruleset.c"),
    ("zigux/tests/phase13_landlock_syscalls_manifest.json", "P13-L13", "security/landlock/syscalls.c"),
]:
    manifest = load_json(manifest_path)
    if manifest.get("phase") != "Phase 13":
        missing.append(f"{manifest_path}:phase")
    if manifest.get("lane_key") != lane_key:
        missing.append(f"{manifest_path}:lane_key")
    if manifest.get("anchor") != anchor:
        missing.append(f"{manifest_path}:anchor")
    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append(f"{manifest_path}:survey_summary")
        continue
    if summary.get("preexisting_phase13_build_present") is not True:
        missing.append(f"{manifest_path}:build_present")
    if summary.get("preexisting_phase13_make_target_present") is not True:
        missing.append(f"{manifest_path}:make_present")

notifier_manifest = load_json("zigux/tests/phase13_notifier_list_manifest.json")
if notifier_manifest.get("phase") != "Phase 13":
    missing.append("zigux/tests/phase13_notifier_list_manifest.json:phase")

if missing:
    print("PHASE13_RELEASE_VALIDATION=fail")
    print("PHASE13_RELEASE_VALIDATION_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE13_RELEASE_VALIDATION_MISSING_END")
    sys.exit(1)

print("PHASE13_RELEASE_VALIDATION=pass")
print(f"PHASE13_RELEASE_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE13_RELEASE_REQUIRED_MARKER_COUNT="
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(RELEASE_MARKERS) + len(TRACEABILITY_MARKERS)}"
)
print(f"PHASE13_RELEASE_BUILD_TEST_COUNT={len(build_names)}")
print(f"PHASE13_RELEASE_BUILD_DEPEND_STEP_COUNT={len(depend_steps)}")
