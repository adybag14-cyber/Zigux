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
RELEASE_COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
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
    "`zigux/tests/phase12_build.zig` wires `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` into the active `smoke` and `test` steps",
    "The shared release packet now also carries the bounded `virtio_net_transmit_recycle` and `virtio_net_queue_resume` follow-ups through `drivers/net/virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_queue_resume.zig`, and `zigux/tests/phase12_virtio_net_queue_resume.zig`: current `zigux/tests/phase12_build.zig` runs both replays in `smoke` and `test`, but the release reading must keep them framed as transmit-disposition and queue-resume reviewability rather than as live interrupt-backed completion, refill execution, queue restart parity, or DMA parity.",
    "The broader shared-summary packet is now closed on current `master`: `scripts/zigux/README.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/check-build-only-phase12-surface.py`, and `Documentation/zigux/review-checklist.md` all keep the shipped `python3 scripts/zigux/check-phase12-cross.py --self-test` companion and the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard explicit inside the same `make -C zigux phase12-validate` support bundle.",
    "`scripts/zigux/check-phase12-release-readiness-packet.py` is now the fail-closed truthfulness guard for that narrower shared packet: this note can keep the older reviewer-facing reminder drift closed instead of carrying it forward, because `Documentation/zigux/review-checklist.md` now calls out the bounded `scripts/zigux/check-phase12-cross.py --self-test` companion beside the dedicated release-readiness checker and the shipped validator-first route.",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped Phase 12 surface.",
    "The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, the bounded `scripts/zigux/check-phase12-cross.py --self-test` companion, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a standalone Phase 12 cross-build replay, a focused libbpf-only replay, or another shared cross-target route, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
    "Keep the same degraded-workflow validation quartet explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-cross.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
    "The older reviewer-facing review-checklist gap is now closed too, so leave this readiness companion parked unless a fresher repo-first reread finds a different one-file reminder drift before widening into any new driver claims.",
]

RELEASE_COORDINATION_MATRIX_MARKERS = [
    "If `zig` is unavailable on `PATH`, keep the shipped degraded-workflow bundle plus that same smoke-first order explicit through the Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped PMO surface.",
]

REVIEW_CHECKLIST_MARKERS = [
    "while keeping the bounded `scripts/zigux/check-phase12-cross.py --self-test` companion, the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route?",
    "do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-cross.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the bounded cross-selftest companion, the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
]

FREEZE_MAP_MARKERS = [
    "the shared Phase 12 PMO release packet also stays release-planning-only beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`",
    "queueing, throughput, rollback, and recovery wording there, in the shipped validator-first `make -C zigux phase12-validate` support bundle, and in the smoke-first shared replay packet must stay bounded to driver-local review evidence, lab-only reversible-delivery scaffolding, and shared anti-overlap notes without implying active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`",
]

SCRIPTS_README_MARKERS = [
    "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned across `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `zigux/tests/phase12_build.zig`, the starter-present `virtio_net` packet, the shipped `virtio_scsi` packet, and the bounded NVMe starter-plus-verifier-plus-direct-test-plus-manifest packet before the shared validator-first then smoke-first routes run.",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-cross.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` keep the degraded-workflow support bundle explicit in this scripts-root summary so the shipped validator-first route stays visible as support-bundle evidence rather than as a second direct replay route.",
]

MAKEFILE_MARKERS = [
    "phase12-validate:",
    "scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "scripts/zigux/check-phase12-cross.py --self-test",
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
            errors.append(f"marker count drift in {rel_path}: {marker} (expected 1, found {count})")


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
        RELEASE_COORDINATION_MATRIX_PATH,
        SCRIPTS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_MAP_PATH,
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

    require_exact_count(errors, RELEASE_READINESS_PATH, read_text(root / RELEASE_READINESS_PATH), RELEASE_READINESS_MARKERS)
    require_exact_count(errors, RELEASE_COORDINATION_MATRIX_PATH, read_text(root / RELEASE_COORDINATION_MATRIX_PATH), RELEASE_COORDINATION_MATRIX_MARKERS)
    require_exact_count(errors, REVIEW_CHECKLIST_PATH, read_text(root / REVIEW_CHECKLIST_PATH), REVIEW_CHECKLIST_MARKERS)
    require_exact_count(errors, FREEZE_MAP_PATH, read_text(root / FREEZE_MAP_PATH), FREEZE_MAP_MARKERS)
    require_exact_count(errors, SCRIPTS_README_PATH, read_text(root / SCRIPTS_README_PATH), SCRIPTS_README_MARKERS)
    require_exact_count(errors, MAKEFILE_PATH, read_text(root / MAKEFILE_PATH), MAKEFILE_MARKERS)
    require_exact_count(errors, WORKFLOW_PATH, read_text(root / WORKFLOW_PATH), WORKFLOW_MARKERS)

    anchors = extract_phase12_anchor_bullets(read_text(root / ROADMAP_PATH))
    if anchors != ROADMAP_ANCHORS:
        errors.append("roadmap Phase 12 anchor list drifted from the expected four-entry set")

    return errors


def marker_doc(title: str, markers: list[str]) -> str:
    lines = [title, ""]
    lines.extend(f"- {marker}" for marker in markers)
    lines.append("")
    return "\n".join(lines)


def good_release_readiness_text() -> str:
    return marker_doc("# Phase 12 Release Readiness Survey", RELEASE_READINESS_MARKERS)


def good_release_coordination_matrix_text() -> str:
    return marker_doc("# Phase 12 Release Coordination Matrix", RELEASE_COORDINATION_MATRIX_MARKERS)


def good_review_checklist_text() -> str:
    return marker_doc("# Zigux Review Checklist", REVIEW_CHECKLIST_MARKERS)


def good_freeze_map_text() -> str:
    return marker_doc("# Zigux Freeze Map", FREEZE_MAP_MARKERS)


def good_scripts_readme_text() -> str:
    return marker_doc("# scripts/zigux", SCRIPTS_README_MARKERS)


def good_roadmap_text() -> str:
    return "\n".join([
        "# Roadmap",
        "",
        PHASE12_SECTION_HEADING,
        "",
        "Primary Linux anchors:",
        *[f"- {anchor}" for anchor in ROADMAP_ANCHORS],
        "",
    ])


def good_makefile_text() -> str:
    return "\n".join([
        "phase12-validate:",
        "\t$(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "\t$(PYTHON) scripts/zigux/check-phase12-cross.py --self-test",
        "\t$(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "\t$(PYTHON) scripts/zigux/validate-phase12.py",
        "",
        "phase12: phase12-validate phase12-smoke phase12-test",
        "",
    ])


def good_workflow_text() -> str:
    return "\n".join([
        "- name: Validate Phase 12 degraded-workflow bundle",
        "  run: make -C zigux phase12-validate",
        "- name: Run focused Phase 12 smoke shard",
        "  run: make -C zigux phase12-smoke",
        "- name: Run Phase 12 complex driver tests",
        "  run: zig build test --build-file zigux/tests/phase12_build.zig --summary all",
        "",
    ])


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-check-"))
    case_count = 0
    try:
        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(tmp_root / RELEASE_COORDINATION_MATRIX_PATH, good_release_coordination_matrix_text())
        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write_text(tmp_root / FREEZE_MAP_PATH, good_freeze_map_text())
        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write_text(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")
        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())

        errors = check(tmp_root, source_text=MARKER)
        if errors:
            raise SystemExit(f"self-test expected success but failed: {errors!r}")
        case_count += 1

        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text().replace(REVIEW_CHECKLIST_MARKERS[0], "", 1))
        if not any(REVIEW_CHECKLIST_MARKERS[0] in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing review-checklist marker was not detected")
        case_count += 1
        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text().replace(RELEASE_READINESS_MARKERS[4], "", 1))
        if not any(RELEASE_READINESS_MARKERS[4] in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing readiness closure marker was not detected")
        case_count += 1
        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text().replace("scripts/zigux/check-phase12-cross.py --self-test", "", 1))
        if not any("scripts/zigux/check-phase12-cross.py --self-test" in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing makefile cross self-test marker was not detected")
        case_count += 1
        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())

        write_text(
            tmp_root / RELEASE_COORDINATION_MATRIX_PATH,
            good_release_coordination_matrix_text().replace(RELEASE_COORDINATION_MATRIX_MARKERS[0], "", 1),
        )
        if not any(RELEASE_COORDINATION_MATRIX_MARKERS[0] in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing coordination matrix attached-toolchain marker was not detected")
        case_count += 1
        write_text(tmp_root / RELEASE_COORDINATION_MATRIX_PATH, good_release_coordination_matrix_text())

        write_text(
            tmp_root / FREEZE_MAP_PATH,
            good_freeze_map_text().replace(FREEZE_MAP_MARKERS[1], "", 1),
        )
        if not any(FREEZE_MAP_MARKERS[1] in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing freeze-map validator bundle marker was not detected")
        case_count += 1
        write_text(tmp_root / FREEZE_MAP_PATH, good_freeze_map_text())

        write_text(
            tmp_root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(SCRIPTS_README_MARKERS[1], "", 1),
        )
        if not any(SCRIPTS_README_MARKERS[1] in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing scripts-readme degraded-workflow marker was not detected")
        case_count += 1
        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace("run: make -C zigux phase12-validate", "", 1),
        )
        if not any("run: make -C zigux phase12-validate" in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("missing workflow phase12-validate step was not detected")
        case_count += 1
        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())

        write_text(tmp_root / ROADMAP_PATH, good_roadmap_text().replace("- `drivers/scsi/virtio_scsi.c`\n", "", 1))
        if not any("roadmap Phase 12 anchor list drifted" in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("roadmap anchor drift was not detected")
        case_count += 1

        if not any("checker marker missing from checker source" in error for error in check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken")):
            raise SystemExit("missing checker marker was not detected")
        case_count += 1
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test cases")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("PHASE12_RELEASE_READINESS_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())