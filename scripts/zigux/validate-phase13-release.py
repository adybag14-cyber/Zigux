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
    "scripts/zigux/README.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
]

MAKE_MARKERS = [
    "PHONY += phase13-validate phase13-test phase13",
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "phase13-test:",
    "$(ZIG) build test --build-file zigux/tests/phase13_build.zig --summary all",
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
    "PHASE13_MANIFEST_BACKED_SURVEY_COUNT=4",
    "PHASE13_ACTIVE_ASYMMETRIC_ANCHOR_COUNT=0",
    "PHASE13_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase13-release.py",
    "PHASE13_VALIDATE_ENTRYPOINT=make -C zigux phase13-validate",
    "PHASE13_SHARED_BUILD_PRESENT=yes",
    "PHASE13_SHARED_MAKE_TARGET_PRESENT=yes",
    "PHASE13_SHARED_REPLAY_STEP_COUNT=7",
    "PHASE13_RELEASE_CLOSED=no",
    "The current release packet also carries one active Phase 13 posture reminder on `master`:",
    "`python3 scripts/zigux/validate-phase13-release.py` and `make -C zigux phase13-validate` currently pass",
    "the earlier `expected statement, found 'EOF'` note for `zigux/tests/phase13_landlock_ruleset.zig` is stale: the current checked-in ruleset test file is syntactically complete, and its dedicated ruleset helper replay still passes against `security/landlock/ruleset.zig`",
    "the remaining live ruleset blocker is the same one already recorded by the manifest-backed survey packet: `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown are still outside the current helper-only lane",
    "a fresh full `zigux/tests/phase13_build.zig` replay is still the right way to confirm shared Phase 13 green status after that stale EOF marker is removed from the release note",
    "The current manifest lane ownership carried by the release packet is:",
    "`fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json` lane `P13-L04`",
    "`lib/devres.c` through `zigux/tests/phase13_devres_manifest.json` lane `P13-L03`",
    "`security/landlock/ruleset.c` through `zigux/tests/phase13_landlock_ruleset_manifest.json` lane `P13-L12`",
    "`security/landlock/syscalls.c` through `zigux/tests/phase13_landlock_syscalls_manifest.json` lane `P13-L16`",
    "adjacent notifier-list reviewability evidence through `zigux/tests/phase13_notifier_list_manifest.json` lane `P13-L17`",
    "lib/devres.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present, and helper-first MMIO or resource planners keep live DMA-backed mappings and scatterlist ownership explicitly blocked",
    "phase13_notifier_list_reviewability.zig",
    "zig build test --build-file zigux/tests/phase13_build.zig --summary all",
]

TRACEABILITY_MARKERS = [
    "Shared tranche entrypoints already present on `master`:",
    "`zigux/tests/phase13_build.zig`",
    "`zigux/Makefile` via `make -C zigux phase13`",
    "`lib/devres.c` is represented by real helper code, real tests, a manifest-backed survey packet, and explicit blocked DMA/scatterlist boundary evidence",
]

DOCS_ROOT_MARKERS = [
    "Phase 13 notes",
    "`Documentation/zigux/phase13-roadmap-traceability.md` now maps the four shared-helper roadmap anchors `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c` to the live Zigux evidence so the current Phase 13 packet is visible from the docs root.",
    "`Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` plus the four `zigux/tests/phase13_*_manifest.json` files now keep the current helper-first boundaries explicit instead of implying broader runtime parity.",
    "`make -C zigux phase13-validate` is the current validator-first entrypoint for the shared Phase 13 release-discipline packet.",
    "`zigux/tests/phase13_build.zig` and `make -C zigux phase13` remain the published shared replay path; the earlier `phase13_landlock_ruleset.zig` EOF blocker note is stale, and the remaining live `P13-L12` blocker is the manifest-backed helper boundary around `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown until a fresh full shared replay is confirmed on current `master`.",
]

SCRIPT_README_MARKERS = [
    "Current bootstrap helpers",
    "`validate-phase13-release.py`",
    "Phase 13 flow",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`make -C zigux phase13-validate`",
    "`zigux/tests/phase13_build.zig`",
    "`make -C zigux phase13` routes through the validator before the shared replay",
    "`Documentation/zigux/phase13-devres-survey.md`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "live DMA-backed mappings and scatterlist ownership",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 13 release-discipline packet, do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` still agree",
    "`make -C zigux phase13` routes through `make -C zigux phase13-validate` before the shared replay",
    "and that the shared replay still names the same seven steps?",
    "if the shared replay is currently blocked on `master`, does `Documentation/zigux/phase13-release-notes-survey.md` still name the exact blocker, the owning lane, and the fact that `phase13-validate` is green while `phase13-test` is not?",
    "if the change touches the shared Phase 13 release-discipline packet, do `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_notifier_list_reviewability.zig` still back the same four manifest-backed roadmap anchors plus the adjacent notifier-list reviewability packet",
    "while keeping live DMA-backed mappings and scatterlist ownership blocked rather than implied?",
]

BUILD_NAME_MARKERS = [
    "phase13-libfs-tests",
    "phase13-devres-tests",
    "phase13-landlock-ruleset-tests",
    "phase13-landlock-syscalls-tests",
    "phase13-libfs-reviewability-tests",
    "phase13-devres-reviewability-tests",
    "phase13-notifier-list-reviewability-tests",
]

RELEASE_EVIDENCE_CORE_PATHS = [
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


def section_text(source: str, start_marker: str, end_marker: str) -> str | None:
    start = source.find(start_marker)
    if start == -1:
        return None
    start += len(start_marker)
    end = source.find(end_marker, start)
    if end == -1:
        return None
    return source[start:end]


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
    ("docs_root", text("Documentation/zigux/README.md"), DOCS_ROOT_MARKERS),
    ("scripts_readme", text("scripts/zigux/README.md"), SCRIPT_README_MARKERS),
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("release", text("Documentation/zigux/phase13-release-notes-survey.md"), RELEASE_MARKERS),
    ("traceability", text("Documentation/zigux/phase13-roadmap-traceability.md"), TRACEABILITY_MARKERS),
    ("review_checklist", text("Documentation/zigux/review-checklist.md"), REVIEW_CHECKLIST_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

release_text = text("Documentation/zigux/phase13-release-notes-survey.md")
product_boundary = section_text(release_text, "product boundary:\n", "\n## Why this record exists")
if product_boundary is None:
    missing.append("release:product_boundary_section")
else:
    for rel in [
        "scripts/zigux/validate-phase13-release.py",
        "scripts/zigux/README.md",
        "Documentation/zigux/phase13-release-notes-survey.md",
        "Documentation/zigux/phase13-roadmap-traceability.md",
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/phase13_build.zig",
        "zigux/Makefile",
        "Documentation/zigux/phase13-libfs-slice.md",
        "Documentation/zigux/phase13-libfs-survey.md",
        "Documentation/zigux/phase13-devres-slice.md",
        "Documentation/zigux/phase13-devres-survey.md",
        "Documentation/zigux/phase13-landlock-ruleset-slice.md",
        "Documentation/zigux/phase13-landlock-ruleset-survey.md",
        "Documentation/zigux/phase13-landlock-syscalls-slice.md",
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        "Documentation/zigux/phase13-notifier-list-survey.md",
        "zigux/tests/phase13_libfs_manifest.json",
        "zigux/tests/phase13_libfs_reviewability.zig",
        "zigux/tests/phase13_devres_manifest.json",
        "zigux/tests/phase13_landlock_ruleset_manifest.json",
        "zigux/tests/phase13_landlock_syscalls_manifest.json",
        "zigux/tests/phase13_notifier_list_manifest.json",
        "zigux/tests/phase13_devres_reviewability.zig",
        "zigux/tests/phase13_notifier_list_reviewability.zig",
    ]:
        if rel not in product_boundary:
            missing.append(f"release:product_boundary_path:{rel}")

for rel in [
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase13_build.zig",
    "zigux/Makefile",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
]:
    if rel not in release_text:
        missing.append(f"release:evidence_path:{rel}")

release_evidence = section_text(
    release_text,
    "The current bounded release-evidence set is:\n",
    "\n## Gates",
)
if release_evidence is None:
    missing.append("release:evidence_set_section")
else:
    for rel in RELEASE_EVIDENCE_CORE_PATHS:
        if rel not in release_evidence:
            missing.append(f"release:evidence_set_path:{rel}")

build_text = text("zigux/tests/phase13_build.zig")
build_names = BUILD_TEST_NAME_RE.findall(build_text)
if build_names != BUILD_NAME_MARKERS:
    missing.append("build:test_names")
for build_name in BUILD_NAME_MARKERS:
    if build_name not in release_text:
        missing.append(f"release:shared_replay_step:{build_name}")
depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
if len(depend_steps) != 7:
    missing.append(f"build:depend_step_count={len(depend_steps)}")

for manifest_path, lane_key, anchor in [
    ("zigux/tests/phase13_libfs_manifest.json", "P13-L04", "fs/libfs.c"),
    ("zigux/tests/phase13_devres_manifest.json", "P13-L03", "lib/devres.c"),
    ("zigux/tests/phase13_landlock_ruleset_manifest.json", "P13-L12", "security/landlock/ruleset.c"),
    ("zigux/tests/phase13_landlock_syscalls_manifest.json", "P13-L16", "security/landlock/syscalls.c"),
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


devres_manifest = load_json("zigux/tests/phase13_devres_manifest.json")
for blocked in ["blocked_on_dma_state", "blocked_on_scatterlist_state"]:
    if not any(gap.get("status") == blocked for gap in devres_manifest.get("gaps", []) if isinstance(gap, dict)):
        missing.append(f"zigux/tests/phase13_devres_manifest.json:{blocked}")

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
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(RELEASE_MARKERS) + len(TRACEABILITY_MARKERS) + len(DOCS_ROOT_MARKERS) + len(SCRIPT_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS)}"
)
print(f"PHASE13_RELEASE_BUILD_TEST_COUNT={len(build_names)}")
print(f"PHASE13_RELEASE_BUILD_DEPEND_STEP_COUNT={len(depend_steps)}")