#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")

PHASE9_MARKER = "Phase 9 notes - `Documentation/zigux/freeze-map.md`"
PHASE12_HEADING = "Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md`"

REQUIRED_MARKERS = (
    "Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` - `Documentation/zigux/phase12-release-readiness-survey.md` - `Documentation/zigux/phase12-release-closure-checklist.md` - `Documentation/zigux/phase12-release-coordination-matrix.md` - `Documentation/zigux/phase12-raw-github-coverage-survey.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.",
    "* the current docs-root Phase 12 reminder packet should stay parked on `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` so the docs root matches the same shipped PMO packet already kept current by the sequencing, readiness, closure, coordination, scripts-root, tests-root, and checklist reminder surfaces.",
    "* `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, and `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns on current `master`.",
    "* current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.",
    "* keep the degraded rerun order honest here too: rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile` before attached-Zig rerun vocabulary, and if that local fallback is absent keep `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` framed only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text.",
    "* keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` is the driver-local current-master gap-note companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than extra commit-pinned fallback artifacts.",
    "* keep the bounded driver-family split explicit here too: the shared route stays the five-file `virtio_net` smoke-and-test quintet in `zigux/tests/phase12_build.zig`, `virtio_scsi` remains the rollback-lab packet through its dedicated survey companions outside the shared route, `nvme_pci` remains the bounded driver-local foothold outside the shared route, and the parked libbpf packet stays tied to `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being promoted into a focused shared replay claim.",
    "* keep the docs-root Phase 12 note bounded below DMA-safe receive ownership, queue-restart parity, throughput delivery, recovery, deeper transport lifecycle, `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` claims until fresh current-`master` proof lands for those deeper surfaces.",
)


def collect_errors(root: Path) -> list[str]:
    docs_root = (root / DOCS_ROOT_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in docs_root:
            errors.append(f"missing:{marker}")

    phase9_index = docs_root.find(PHASE9_MARKER)
    phase12_index = docs_root.find(PHASE12_HEADING)
    if phase9_index == -1:
        errors.append(f"missing:{PHASE9_MARKER}")
    if phase12_index == -1:
        errors.append(f"missing:{PHASE12_HEADING}")
    if phase9_index != -1 and phase12_index != -1 and phase9_index > phase12_index:
        errors.append("order:Phase 9 notes must appear before Phase 12 notes")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_root() -> str:
    return """# Zigux Documentation

Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.
Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` - `Documentation/zigux/phase12-release-readiness-survey.md` - `Documentation/zigux/phase12-release-closure-checklist.md` - `Documentation/zigux/phase12-release-coordination-matrix.md` - `Documentation/zigux/phase12-raw-github-coverage-survey.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.
* the current docs-root Phase 12 reminder packet should stay parked on `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` so the docs root matches the same shipped PMO packet already kept current by the sequencing, readiness, closure, coordination, scripts-root, tests-root, and checklist reminder surfaces.
* `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, and `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns on current `master`.
* current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.
* keep the degraded rerun order honest here too: rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile` before attached-Zig rerun vocabulary, and if that local fallback is absent keep `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` framed only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text.
* keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` is the driver-local current-master gap-note companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than extra commit-pinned fallback artifacts.
* keep the bounded driver-family split explicit here too: the shared route stays the five-file `virtio_net` smoke-and-test quintet in `zigux/tests/phase12_build.zig`, `virtio_scsi` remains the rollback-lab packet through its dedicated survey companions outside the shared route, `nvme_pci` remains the bounded driver-local foothold outside the shared route, and the parked libbpf packet stays tied to `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being promoted into a focused shared replay claim.
* keep the docs-root Phase 12 note bounded below DMA-safe receive ownership, queue-restart parity, throughput delivery, recovery, deeper transport lifecycle, `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` claims until fresh current-`master` proof lands for those deeper surfaces.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase12_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())

        if collect_errors(root):
            raise AssertionError("baseline Lane 01 Phase 12 docs-root fixture should pass")
        case_count += 1

        _write(root / DOCS_ROOT_PATH, _sample_docs_root().replace(PHASE12_HEADING, "Phase Twelve notes", 1))
        expected = [f"missing:{REQUIRED_MARKERS[0]}", f"missing:{PHASE12_HEADING}"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for Phase 12 heading case: {missing}")
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())
        case_count += 1

        _write(root / DOCS_ROOT_PATH, _sample_docs_root().replace(REQUIRED_MARKERS[2] + "\n", "", 1))
        expected = [f"missing:{REQUIRED_MARKERS[2]}"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for validator-support case: {missing}")
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())
        case_count += 1

        _write(root / DOCS_ROOT_PATH, _sample_docs_root().replace(REQUIRED_MARKERS[4] + "\n", "", 1))
        expected = [f"missing:{REQUIRED_MARKERS[4]}"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for rerun-order case: {missing}")
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())
        case_count += 1

        _write(root / DOCS_ROOT_PATH, _sample_docs_root().replace(REQUIRED_MARKERS[5] + "\n", "", 1))
        expected = [f"missing:{REQUIRED_MARKERS[5]}"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for fallback-split case: {missing}")
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())
        case_count += 1

        _write(root / DOCS_ROOT_PATH, _sample_docs_root().replace(REQUIRED_MARKERS[6] + "\n", "", 1))
        expected = [f"missing:{REQUIRED_MARKERS[6]}"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for driver-family case: {missing}")
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())
        case_count += 1

        _write(root / DOCS_ROOT_PATH, _sample_docs_root().replace(REQUIRED_MARKERS[7] + "\n", "", 1))
        expected = [f"missing:{REQUIRED_MARKERS[7]}"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for bounded-claims case: {missing}")
        _write(root / DOCS_ROOT_PATH, _sample_docs_root())
        case_count += 1

        swapped = _sample_docs_root().replace(
            "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.\n"
            + REQUIRED_MARKERS[0],
            REQUIRED_MARKERS[0] + "\n"
            + "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
            1,
        )
        _write(root / DOCS_ROOT_PATH, swapped)
        expected = ["order:Phase 9 notes must appear before Phase 12 notes"]
        missing = collect_errors(root)
        if missing != expected:
            raise AssertionError(f"unexpected errors for section-order case: {missing}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE12_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE12_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 12 reminder packet stays aligned on current master."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic docs-root fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_errors(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE12_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE12_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())