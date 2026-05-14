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
REVIEW_CHECKLIST_REQUIRED_MARKERS = [
    "avoid implying a shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route that current `master` does not ship?",
    "if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
]
RELEASE_READINESS_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "Repo-first inspection against current `adybag14-cyber/Zigux` `master` shows that the shared Phase 12 packet is validator-backed but still smoke-first on replay:",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped Phase 12 surface.",
    "The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
    "Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
    "The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.",
    "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts.",
    "while `Documentation/zigux/review-checklist.md` still carries one older clause that treats that route as absent and `scripts/zigux/README.md` plus `scripts/zigux/check-build-only-phase12-surface.py` still carry older wording that treats `scripts/zigux/validate-phase12.py` as support material or denies the shipped route.",
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


def extract_section(text: str, heading: str) -> str | None:
    active = False
    collected: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            active = True
        elif active and stripped.startswith("## "):
            break
        if active:
            collected.append(line)
    if not collected:
        return None
    return "\n".join(collected) + "\n"


def extract_bullets(text: str, heading: str) -> list[str]:
    active = False
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            active = True
            continue
        if not active:
            continue
        if bullets and stripped and not stripped.startswith("- "):
            break
        if stripped.startswith("- "):
            bullets.append(stripped[2:])
    return bullets


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    required_files = [
        root / RELEASE_READINESS_PATH,
        root / SCRIPTS_README_PATH,
        root / REVIEW_CHECKLIST_PATH,
        root / ROADMAP_PATH,
        root / BUILD_ONLY_CHECKER_PATH,
        root / MAKEFILE_PATH,
        root / WORKFLOW_PATH,
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(root).as_posix()}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    release_text = read_text(root / RELEASE_READINESS_PATH)
    require_exact_count(errors, RELEASE_READINESS_PATH, release_text, RELEASE_READINESS_MARKERS)

    scripts_readme_text = read_text(root / SCRIPTS_README_PATH)
    require_exact_count(errors, SCRIPTS_README_PATH, scripts_readme_text, SCRIPTS_README_MARKERS)

    review_checklist_text = read_text(root / REVIEW_CHECKLIST_PATH)
    require_exact_count(
        errors, REVIEW_CHECKLIST_PATH, review_checklist_text, REVIEW_CHECKLIST_REQUIRED_MARKERS
    )

    makefile_text = read_text(root / MAKEFILE_PATH)
    require_exact_count(errors, MAKEFILE_PATH, makefile_text, MAKEFILE_MARKERS)

    workflow_text = read_text(root / WORKFLOW_PATH)
    require_exact_count(errors, WORKFLOW_PATH, workflow_text, WORKFLOW_MARKERS)

    roadmap_section = extract_section(read_text(root / ROADMAP_PATH), PHASE12_SECTION_HEADING)
    if roadmap_section is None:
        errors.append(f"missing roadmap section: {PHASE12_SECTION_HEADING}")
    else:
        anchors = extract_bullets(roadmap_section, "Primary Linux anchors:")
        if anchors != ROADMAP_ANCHORS:
            errors.append("roadmap Phase 12 anchor list drifted from the expected four-entry set")

    return errors


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def good_release_readiness_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Release Readiness Survey",
            "",
            "## Status",
            "- `PHASE12_STATUS=active`",
            "- `PHASE12_RELEASE_CLOSED=no`",
            "- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
            "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "",
            "## Current Release Reading",
            "- Repo-first inspection against current `adybag14-cyber/Zigux` `master` shows that the shared Phase 12 packet is validator-backed but still smoke-first on replay:",
            "- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped Phase 12 surface.",
            "- The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
            "- Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
            "- The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.",
            "- During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts.",
            "- while `Documentation/zigux/review-checklist.md` still carries one older clause that treats that route as absent and `scripts/zigux/README.md` plus `scripts/zigux/check-build-only-phase12-surface.py` still carry older wording that treats `scripts/zigux/validate-phase12.py` as support material or denies the shipped route.",
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


def good_review_checklist_text() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "",
            "- avoid implying a shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route that current `master` does not ship?",
            "- if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
            "",
        ]
    )


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "# ZAR to Zigux Product Roadmap",
            "",
            PHASE12_SECTION_HEADING,
            "",
            "Primary Linux anchors:",
            *[f"- {item}" for item in ROADMAP_ANCHORS],
            "",
        ]
    )


def good_makefile_text() -> str:
    return "\n".join(
        [
            "phase12-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py",
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
        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")
        write(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write(tmp_root / WORKFLOW_PATH, good_workflow_text())

        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write(
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
            "self-test expected support-checker failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
            "self-test expected build-only-guard failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- Repo-first inspection against current `adybag14-cyber/Zigux` `master` shows that the shared Phase 12 packet is validator-backed but still smoke-first on replay:\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "validator-backed but still smoke-first on replay",
            "self-test expected validator-backed summary failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped Phase 12 surface.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "If `zig` is unavailable on `PATH`",
            "self-test expected fallback-order failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The smaller validator-first boundary in the lane is now shipped",
            "self-test expected validator-route failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Keep the same degraded-workflow validation trio explicit too:",
            "self-test expected validation-trio failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The public fallback split must stay explicit:",
            "self-test expected fallback-split failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet",
            "self-test expected shared-tree-anchor failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
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
            "self-test expected scripts-readme marker failure",
        )

        write(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write(
            tmp_root / REVIEW_CHECKLIST_PATH,
            good_review_checklist_text().replace(
                "- avoid implying a shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route that current `master` does not ship?\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in Documentation/zigux/review-checklist.md: avoid implying a shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route that current `master` does not ship?",
            "self-test expected review-checklist lag marker failure",
        )

        write(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write(
            tmp_root / REVIEW_CHECKLIST_PATH,
            good_review_checklist_text().replace(
                "- if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in Documentation/zigux/review-checklist.md: if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes",
            "self-test expected review-checklist support-route failure",
        )

        write(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write(
            tmp_root / ROADMAP_PATH,
            good_roadmap_text().replace("- `drivers/scsi/virtio_scsi.c`\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "roadmap Phase 12 anchor list drifted",
            "self-test expected roadmap-anchor failure",
        )

        write(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in zigux/Makefile: scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "self-test expected makefile readiness-self-test failure",
        )

        write(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in zigux/Makefile: scripts/zigux/validate-phase12.py",
            "self-test expected makefile validator-route failure",
        )

        write(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace("phase12: phase12-validate phase12-smoke phase12-test", "phase12: phase12-smoke phase12-test", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in zigux/Makefile: phase12: phase12-validate phase12-smoke phase12-test",
            "self-test expected makefile route failure",
        )

        write(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace("run: make -C zigux phase12-validate", "run: make -C zigux phase12-smoke", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in .github/workflows/zigux-bootstrap.yml: run: make -C zigux phase12-validate",
            "self-test expected workflow route failure",
        )

        write(tmp_root / WORKFLOW_PATH, good_workflow_text())
        (tmp_root / BUILD_ONLY_CHECKER_PATH).unlink()
        expect_contains(
            check(tmp_root, source_text=MARKER),
            f"missing file: {BUILD_ONLY_CHECKER_PATH}",
            "self-test expected companion-checker presence failure",
        )
        write(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")

        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "self-test expected checker-marker failure",
        )

    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=17")
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