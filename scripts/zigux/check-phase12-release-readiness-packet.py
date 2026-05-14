#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=release_readiness_packet

Fail-closed checker for the bounded Phase 12 release-readiness note and shipped validation route.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=release_readiness_packet"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
ROADMAP_PATH = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE12_SECTION_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"

ROADMAP_ANCHORS = [
    "`drivers/net/virtio_net.c`",
    "`drivers/nvme/host/pci.c`",
    "`drivers/scsi/virtio_scsi.c`",
    "`tools/lib/bpf/libbpf.c`",
]

RELEASE_READINESS_MARKERS = [
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` already keep the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard plus the shipped `make -C zigux phase12-validate` route explicit, and `zigux/tests/README.md` now does the same in its Phase 12 inventory, so the docs-root, review-checklist, and tests-root reminders are no longer part of the live PMO drift.",
    "The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
    "Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
    "`scripts/zigux/README.md` still lacks any dedicated Phase 12 scripts-root summary and `scripts/zigux/check-build-only-phase12-surface.py` still carries older marker expectations around the shipped `phase12-validate` route.",
    "`scripts/zigux/README.md` still lacks a dedicated Phase 12 flow block and `scripts/zigux/check-build-only-phase12-surface.py` still needs a later reminder-marker sync before that broader reminder stack is fully current.",
]

REVIEW_CHECKLIST_MARKERS = [
    "avoid implying a broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay, while keeping the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route",
    "if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
]

SCRIPTS_README_MARKERS = [
    "`scripts/zigux/check-phase12-release-readiness-packet.py`",
]

MAKEFILE_MARKERS = [
    "phase12-validate:",
    "scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "scripts/zigux/validate-phase12.py",
    "phase12: phase12-validate phase12-smoke phase12-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 12 degraded-workflow bundle",
    "run: make -C zigux phase12-validate",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
]


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def extract_phase12_anchor_bullets(text: str) -> list[str]:
    lines = text.splitlines()
    in_phase12 = False
    in_anchor_list = False
    anchors: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == PHASE12_SECTION_HEADING:
            in_phase12 = True
            continue
        if in_phase12 and stripped.startswith("## "):
            break
        if not in_phase12:
            continue
        if stripped == "Primary Linux anchors:":
            in_anchor_list = True
            continue
        if in_anchor_list:
            if stripped.startswith("- "):
                anchors.append(stripped[2:])
                continue
            if anchors:
                break
    return anchors


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    required_files = [
        RELEASE_READINESS_PATH,
        SCRIPTS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        ROADMAP_PATH,
        BUILD_ONLY_CHECKER_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ]

    for rel_path in required_files:
        if not (root / rel_path).exists():
            errors.append(f"missing file: {rel_path}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    require_exact_count(
        errors,
        RELEASE_READINESS_PATH,
        read_text(root / RELEASE_READINESS_PATH),
        RELEASE_READINESS_MARKERS,
    )
    require_exact_count(
        errors,
        REVIEW_CHECKLIST_PATH,
        read_text(root / REVIEW_CHECKLIST_PATH),
        REVIEW_CHECKLIST_MARKERS,
    )
    require_exact_count(
        errors,
        SCRIPTS_README_PATH,
        read_text(root / SCRIPTS_README_PATH),
        SCRIPTS_README_MARKERS,
    )
    require_exact_count(
        errors,
        MAKEFILE_PATH,
        read_text(root / MAKEFILE_PATH),
        MAKEFILE_MARKERS,
    )
    require_exact_count(
        errors,
        WORKFLOW_PATH,
        read_text(root / WORKFLOW_PATH),
        WORKFLOW_MARKERS,
    )

    anchors = extract_phase12_anchor_bullets(read_text(root / ROADMAP_PATH))
    if anchors != ROADMAP_ANCHORS:
        errors.append(
            "roadmap Phase 12 anchor list drifted from the expected four-entry set"
        )

    return errors


def good_release_readiness_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Release Readiness Survey",
            "",
            "## Status",
            "- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
            "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "",
            "## Current Release Reading",
            "- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` already keep the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard plus the shipped `make -C zigux phase12-validate` route explicit, and `zigux/tests/README.md` now does the same in its Phase 12 inventory, so the docs-root, review-checklist, and tests-root reminders are no longer part of the live PMO drift.",
            "- The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
            "- Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
            "- `scripts/zigux/README.md` still lacks any dedicated Phase 12 scripts-root summary and `scripts/zigux/check-build-only-phase12-surface.py` still carries older marker expectations around the shipped `phase12-validate` route.",
            "",
            "## Next Bounded Step",
            "- `scripts/zigux/README.md` still lacks a dedicated Phase 12 flow block and `scripts/zigux/check-build-only-phase12-surface.py` still needs a later reminder-marker sync before that broader reminder stack is fully current.",
            "",
        ]
    )


def good_review_checklist_text() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "",
            "- avoid implying a broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay, while keeping the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route?",
            "- if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
            "",
        ]
    )


def good_scripts_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "- `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "",
        ]
    )


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "# Roadmap",
            "",
            PHASE12_SECTION_HEADING,
            "",
            "Primary Linux anchors:",
            *[f"- {anchor}" for anchor in ROADMAP_ANCHORS],
            "",
        ]
    )


def good_makefile_text() -> str:
    return "\n".join(
        [
            "phase12-validate:",
            "\t$(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "\t$(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "\t$(PYTHON) scripts/zigux/validate-phase12.py",
            "",
            "phase12: phase12-validate phase12-smoke phase12-test",
            "",
        ]
    )


def good_workflow_text() -> str:
    return "\n".join(
        [
            "- name: Validate Phase 12 degraded-workflow bundle",
            "  run: make -C zigux phase12-validate",
            "- name: Run focused Phase 12 smoke shard",
            "  run: make -C zigux phase12-smoke",
            "- name: Run Phase 12 complex driver tests",
            "  run: zig build test --build-file zigux/tests/phase12_build.zig --summary all",
            "",
        ]
    )


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-check-"))
    try:
        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write_text(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")
        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())

        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "missing support-checker marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` already keep the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard plus the shipped `make -C zigux phase12-validate` route explicit, and `zigux/tests/README.md` now does the same in its Phase 12 inventory, so the docs-root, review-checklist, and tests-root reminders are no longer part of the live PMO drift.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "docs-root, review-checklist, and tests-root reminders are no longer part of the live PMO drift",
            "missing resolved-reminder marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "`scripts/zigux/README.md` still lacks any dedicated Phase 12 scripts-root summary and `scripts/zigux/check-build-only-phase12-surface.py` still carries older marker expectations around the shipped `phase12-validate` route.",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "still lacks any dedicated Phase 12 scripts-root summary and `scripts/zigux/check-build-only-phase12-surface.py` still carries older marker expectations around the shipped `phase12-validate` route",
            "missing current-gap marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / REVIEW_CHECKLIST_PATH,
            good_review_checklist_text().replace(
                "avoid implying a broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay, while keeping the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route?",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "support-bundle evidence rather than as a second direct replay route",
            "missing review-checklist marker",
        )

        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write_text(
            tmp_root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "- `scripts/zigux/check-phase12-release-readiness-packet.py`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in scripts/zigux/README.md: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "missing scripts-readme marker",
        )

        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "phase12: phase12-validate phase12-smoke phase12-test",
                "phase12: phase12-smoke phase12-test",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "phase12: phase12-validate phase12-smoke phase12-test",
            "missing makefile route",
        )

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace(
                "run: make -C zigux phase12-validate",
                "run: make -C zigux phase12-smoke",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "run: make -C zigux phase12-validate",
            "missing workflow route",
        )

        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())
        write_text(
            tmp_root / ROADMAP_PATH,
            good_roadmap_text().replace("- `drivers/scsi/virtio_scsi.c`\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "roadmap Phase 12 anchor list drifted",
            "roadmap anchor drift not detected",
        )

        write_text(tmp_root / ROADMAP_PATH, good_roadmap_text())
        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "missing checker marker not detected",
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate (defaults to the checker directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 release-readiness packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())