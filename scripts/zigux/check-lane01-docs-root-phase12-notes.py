#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")

PHASE10_MARKER = "Phase 10 notes - "
PHASE12_MARKER = "Phase 12 notes - "
PHASE14_MARKER = "Phase 14 notes - "

REQUIRED_MARKERS = (
    "Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` - `Documentation/zigux/phase12-release-readiness-survey.md` - `Documentation/zigux/phase12-release-closure-checklist.md` - `Documentation/zigux/phase12-release-coordination-matrix.md` - `Documentation/zigux/phase12-raw-github-coverage-survey.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` keep the bounded Phase 12 docs-root packet explicit",
    "the current docs-root Phase 12 reminder packet should stay parked on `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
    "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again",
    "current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.",
    "keep the degraded rerun order honest here too: rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile` before attached-Zig rerun vocabulary",
    "keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog",
    "keep the bounded driver-family split explicit here too: the shared route stays the six-file `virtio_net` smoke-and-test sextet in `zigux/tests/phase12_build.zig`",
    "keep the docs-root Phase 12 note bounded below DMA-safe receive ownership, queue-restart parity, throughput delivery, recovery, deeper transport lifecycle, `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` claims until fresh current-`master` proof lands for those deeper surfaces.",
)

REQUIRED_PATHS = (
    Path("Documentation/zigux/phase12-release-sequencing.md"),
    Path("Documentation/zigux/phase12-release-readiness-survey.md"),
    Path("Documentation/zigux/phase12-release-closure-checklist.md"),
    Path("Documentation/zigux/phase12-release-coordination-matrix.md"),
    Path("Documentation/zigux/phase12-raw-github-coverage-survey.md"),
    Path("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"),
    Path("Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("zigux/tests/README.md"),
    Path("scripts/zigux/validate-phase12.py"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    Path("scripts/zigux/check-phase12-release-readiness-packet.py"),
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("zigux/tests/phase12_build.zig"),
    Path("zigux/Makefile"),
)


def check_phase12_notes(root: Path) -> list[str]:
    text = (root / README_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing marker: {marker}")

    phase10_pos = text.find(PHASE10_MARKER)
    phase12_pos = text.find(PHASE12_MARKER)
    phase14_pos = text.find(PHASE14_MARKER)
    if min(phase10_pos, phase12_pos, phase14_pos) == -1:
        errors.append("missing Phase 10, Phase 12, or Phase 14 boundary marker")
    elif not (phase10_pos < phase12_pos < phase14_pos):
        errors.append("phase order mismatch: expected Phase 10 -> Phase 12 -> Phase 14")

    phase12_count = text.count(PHASE12_MARKER)
    if phase12_count != 1:
        errors.append(f"unexpected Phase 12 marker count: {phase12_count}")

    for path in REQUIRED_PATHS:
        if not (root / path).exists():
            errors.append(f"missing linked path: {path.as_posix()}")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation

Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md` keep the shared Phase 10 docs-root reminder packet explicit.

Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` - `Documentation/zigux/phase12-release-readiness-survey.md` - `Documentation/zigux/phase12-release-closure-checklist.md` - `Documentation/zigux/phase12-release-coordination-matrix.md` - `Documentation/zigux/phase12-raw-github-coverage-survey.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.
* the current docs-root Phase 12 reminder packet should stay parked on `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` so the docs root matches the same shipped PMO packet already kept current by the sequencing, readiness, closure, coordination, scripts-root, tests-root, and checklist reminder surfaces.
* `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.
* current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.
* keep the degraded rerun order honest here too: rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile` before attached-Zig rerun vocabulary, and if that local fallback is absent keep `make -C zigux phase12-validate` explicit as shipped current-route proof ahead of the attached-Zig rerun vocabulary `make -C zigux phase12-smoke ZIG=`, `make -C zigux phase12-test ZIG=`, and `make -C zigux phase12 ZIG=`.
* keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` is the driver-local current-master gap-note companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than extra commit-pinned fallback artifacts.
* keep the bounded driver-family split explicit here too: the shared route stays the six-file `virtio_net` smoke-and-test sextet in `zigux/tests/phase12_build.zig` through `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`, `virtio_scsi` remains the rollback-lab packet through its dedicated survey companions outside the shared route, `nvme_pci` remains the bounded driver-local foothold outside the shared route, and the parked libbpf packet stays tied to `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being promoted into a focused shared replay claim.
* keep the docs-root Phase 12 note bounded below DMA-safe receive ownership, queue-restart parity, throughput delivery, recovery, deeper transport lifecycle, `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` claims until fresh current-`master` proof lands for those deeper surfaces.

Phase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keep the bounded Phase 14 docs-root packet explicit.
"""


def _materialize_current_like_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    for path in REQUIRED_PATHS:
        _write(root / path, "")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase12_notes_") as tmp_dir:
        root = Path(tmp_dir)
        _materialize_current_like_root(root)

        errors = check_phase12_notes(root)
        if errors:
            raise AssertionError(f"baseline Phase 12 fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(PHASE12_MARKER, "Phase Twelve notes - ", 1))
        errors = check_phase12_notes(root)
        if "missing Phase 10, Phase 12, or Phase 14 boundary marker" not in errors:
            raise AssertionError(f"expected missing Phase 12 heading error, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py`",
                "`scripts/zigux/validate-phase12.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`",
                1,
            ),
        )
        errors = check_phase12_notes(root)
        if not any(error.startswith("missing marker: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`") for error in errors):
            raise AssertionError(f"expected missing validator marker, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md` keep the shared Phase 10 docs-root reminder packet explicit.\n\n"
                "Phase 12 notes - ",
                "Phase 12 notes - ",
                1,
            ).replace(
                "\n\nPhase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keep the bounded Phase 14 docs-root packet explicit.",
                "\n\nPhase 10 notes - `Documentation/zigux/phase10-closure-evidence.md` keep the shared Phase 10 docs-root reminder packet explicit."
                "\n\nPhase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keep the bounded Phase 14 docs-root packet explicit.",
                1,
            ),
        )
        errors = check_phase12_notes(root)
        if "phase order mismatch: expected Phase 10 -> Phase 12 -> Phase 14" not in errors:
            raise AssertionError(f"expected order mismatch, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.",
                "current `master` also directly serves `.github/workflows/zigux-bootstrap.yml` and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.",
                1,
            ),
        )
        errors = check_phase12_notes(root)
        if not any("zigux/tests/phase12_build.zig" in error for error in errors):
            raise AssertionError(f"expected missing build gate marker, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog",
                "keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` is the driver-local current-master gap-note companion",
                1,
            ),
        )
        errors = check_phase12_notes(root)
        if not any(error.startswith("missing marker: keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`") for error in errors):
            raise AssertionError(f"expected missing fallback marker, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        (root / Path("zigux/Makefile")).unlink()
        errors = check_phase12_notes(root)
        if "missing linked path: zigux/Makefile" not in errors:
            raise AssertionError(f"expected missing linked path error, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(PHASE12_MARKER, f"{PHASE12_MARKER}\n{PHASE12_MARKER}", 1))
        errors = check_phase12_notes(root)
        if "unexpected Phase 12 marker count: 2" not in errors:
            raise AssertionError(f"expected duplicate heading error, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "* keep the docs-root Phase 12 note bounded below DMA-safe receive ownership, queue-restart parity, throughput delivery, recovery, deeper transport lifecycle, `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` claims until fresh current-`master` proof lands for those deeper surfaces.\n",
                "",
                1,
            ),
        )
        errors = check_phase12_notes(root)
        if not any(error.startswith("missing marker: keep the docs-root Phase 12 note bounded below DMA-safe receive ownership") for error in errors):
            raise AssertionError(f"expected missing bounded-scope marker, got: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE12_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE12_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 docs-root Phase 12 reminder packet remains aligned."
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
        help="exercise the checker against synthetic docs-root Phase 12 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_phase12_notes(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE12_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE12_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE12_NOTES_SECTION_ORDER=Phase10->Phase12->Phase14")
    print(f"LANE01_DOCS_ROOT_PHASE12_NOTES_LINKED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
