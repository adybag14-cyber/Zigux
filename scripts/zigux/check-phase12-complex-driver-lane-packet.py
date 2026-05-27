#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 12 complex-driver lane packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_COMPLEX_DRIVER_LANE_PACKET"

NOTE_PATH = Path("Documentation/zigux/phase12-complex-driver-lane-sequencing.md")
README_PATH = Path("scripts/zigux/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = (
    NOTE_PATH,
    README_PATH,
    WORKFLOW_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
)

REQUIRED_PRESENT_PATHS = (
    Path("drivers/net/virtio_net_queue_resume.zig"),
    Path("drivers/net/virtio_net_receive_refill_replay.zig"),
    Path("drivers/net/virtio_net_transmit_recycle.zig"),
    Path("drivers/net/virtio_net_post_reset_replay.zig"),
    Path("drivers/net/virtio_net_throughput_parity.zig"),
    Path("zigux/tests/phase12_virtio_net_queue_resume.zig"),
    Path("zigux/tests/phase12_virtio_net_receive_refill_replay.zig"),
    Path("zigux/tests/phase12_virtio_net_transmit_recycle.zig"),
    Path("zigux/tests/phase12_virtio_net_post_reset_replay.zig"),
    Path("zigux/tests/phase12_virtio_net_throughput_parity.zig"),
    Path("zigux/tests/phase12_virtio_net_survey.zig"),
    Path("zigux/tests/phase12_virtio_net_syntax_lab.zig"),
    Path("zigux/tests/phase12_virtio_net_syntax_lab_build.zig"),
)

FORBIDDEN_PRESENT_PATHS = (
    Path("drivers/net/virtio_net.zig"),
    Path("zigux/tests/phase12_virtio_net.zig"),
)

NOTE_MARKERS = (
    "`PHASE12_LANE=complex-driver-shared-release-packet`",
    "anti-overlap checker: `scripts/zigux/check-phase12-complex-driver-lane-packet.py`",
    "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    "`drivers/net/virtio_net_queue_resume.zig`, `drivers/net/virtio_net_receive_refill_replay.zig`, `drivers/net/virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_post_reset_replay.zig`, and `drivers/net/virtio_net_throughput_parity.zig` are now present on `master`.",
    "`zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig` are now present on `master` as the directly coupled review packet for that split-helper family.",
    "`zigux/tests/phase12_virtio_net_survey.zig` is also present on `master` as the shared survey gate for that same bounded packet; keep it explicit as reviewability support beside the five replay shards without reviving the older monolithic starter or implying live DMA-safe queue ownership, queue restart parity, or completion-path delivery.",
    "`zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` are now present on `master` as isolated compile-smoke companions for the split-helper family, and current `zigux/Makefile` ships `phase12-virtio-net-syntax-lab-test` to keep that review-only rerun hook explicit outside the shared `phase12-validate` / `phase12-smoke` / `phase12-test` route.",
    "`drivers/net/virtio_net.zig` and `zigux/tests/phase12_virtio_net.zig` are currently absent on `master`",
    "current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are current wrapper proof on `master`.",
    "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
    "The note-local compile-smoke companion in this lane is `Documentation/zigux/phase12-cross-compile-smoke.md`, and its directly readable rerun handle is `python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test` plus `python3 scripts/zigux/check-phase12-cross-compile-smoke.py`; keep that narrower smoke packet explicit beside the broader validator-first support bundle without treating it as DMA, queue ownership, throughput, recovery, or driver-delivery proof.",
    "`.github/workflows/zigux-bootstrap.yml` still runs `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig` after the shared `phase12-smoke` and `phase12-test` reruns, so keep that workflow-side throughput anchor explicit as adjacent bounded `virtio_net` evidence rather than shared smoke-route proof.",
    "fresh repo-first readback now returns `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` on current `master`.",
    "`Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py`",
    "`virtio_scsi` survey, survey-build, fallback, fixture, manifest, and checker surfaces framed as rollback-evidence-only driver-local packet truth",
    "`Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` while leaving it outside the shared smoke-first route.",
    "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the one commit-pinned direct replay artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.",
)

README_MARKERS = (
    "## Phase 12",
    "- Phase 12 flow - the current scripts-root complex-driver reminder should keep the shared release packet reviewable through the build-only checker, the readiness-note checker, the dedicated anti-overlap checker, the validator entrypoint, the returned `phase12-validate` / `phase12-smoke` / `phase12-test` / `phase12` wrapper split, and the split-helper `virtio_net` evidence packet while keeping the rollback-evidence `virtio_scsi` survey family, the published-but-unwired NVMe foothold, and the parked libbpf packet distinct",
    "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
    "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that shared Phase 12 packet",
    "`drivers/net/virtio_net_queue_resume.zig`, `drivers/net/virtio_net_receive_refill_replay.zig`, `drivers/net/virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_post_reset_replay.zig`, `drivers/net/virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` stay the isolated syntax-lab compile-smoke companions, and `make -C zigux phase12-virtio-net-syntax-lab-test` keeps that review-only rerun hook explicit outside the shared smoke-first route.",
    "`drivers/net/virtio_net.zig` and `zigux/tests/phase12_virtio_net.zig` stay absent on current `master`, so keep the shared reminder scoped to the returned split-helper packet rather than reviving the older monolithic starter vocabulary.",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "`Documentation/zigux/phase12-nvme-pci-reopen-governance.md`",
    "`zigux/tests/phase12_nvme_pci_manifest.json` keeps the published-but-unwired NVMe foothold explicit without widening this shared scripts-root reminder into driver-local queueing, transport, or DMA claims",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "phase12-virtio-net-queue-resume-tests",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12-virtio-net-throughput-parity-tests",
    "phase12_virtio_net_survey.zig",
    "phase12-virtio-net-survey-tests",
)

BUILD_COUNT_MARKERS = {
    "b.createModule(.{": 11,
    ".addImport(": 5,
    "b.addTest(.{": 6,
    "b.addRunArtifact(": 6,
    "smoke_step.dependOn(": 6,
    "test_step.dependOn(": 6,
}

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase12: phase12-smoke phase12-test",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def require_counts(text: str, counts: dict[str, int], label: str) -> None:
    for marker, expected_count in counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            raise CheckFailure(
                f"{label} wrong count for {marker!r}: expected {expected_count}, got {actual_count}"
            )


def require_forbidden_absent(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"{label} stale marker present: {marker}")


def require_paths_present(root: Path, paths: tuple[Path, ...], label: str) -> None:
    for relative_path in paths:
        if not (root / relative_path).is_file():
            raise CheckFailure(f"{label} missing path: {relative_path}")


def require_paths_absent(root: Path, paths: tuple[Path, ...], label: str) -> None:
    for relative_path in paths:
        if (root / relative_path).exists():
            raise CheckFailure(f"{label} unexpected path present: {relative_path}")


def check(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            raise CheckFailure(f"missing required file: {relative_path}")

    require_paths_present(root, REQUIRED_PRESENT_PATHS, CHECK_NAME)
    require_paths_absent(root, FORBIDDEN_PRESENT_PATHS, CHECK_NAME)

    require_markers(read_text(root, NOTE_PATH), NOTE_MARKERS, str(NOTE_PATH))
    require_markers(read_text(root, README_PATH), README_MARKERS, str(README_PATH))
    require_markers(read_text(root, WORKFLOW_PATH), WORKFLOW_MARKERS, str(WORKFLOW_PATH))

    build_text = read_text(root, BUILD_PATH)
    require_markers(build_text, BUILD_MARKERS, str(BUILD_PATH))
    require_counts(build_text, BUILD_COUNT_MARKERS, str(BUILD_PATH))

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(makefile_text, MAKEFILE_MARKERS, str(MAKEFILE_PATH))
    require_forbidden_absent(
        makefile_text,
        FORBIDDEN_MAKEFILE_MARKERS,
        str(MAKEFILE_PATH),
    )


def build_fixture_text() -> str:
    sections: list[str] = []
    for marker, expected_count in BUILD_COUNT_MARKERS.items():
        sections.extend(marker for _ in range(expected_count))
    sections.extend(BUILD_MARKERS)
    return "\n".join(sections) + "\n"


def write_fixture(root: Path) -> None:
    files = {
        NOTE_PATH: "\n".join(NOTE_MARKERS) + "\n",
        README_PATH: "\n".join(README_MARKERS) + "\n",
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        BUILD_PATH: build_fixture_text(),
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    for relative_path in REQUIRED_PRESENT_PATHS:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-complex-driver-lane-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / NOTE_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-complex-driver-lane-sequencing.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected note marker failure")

        write_fixture(root)
        (root / README_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "scripts/zigux/README.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected README marker failure")

        write_fixture(root)
        build_only_marker = "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`"
        (root / NOTE_PATH).write_text(
            read_text(root, NOTE_PATH).replace(build_only_marker, "", 1),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-complex-driver-lane-sequencing.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build-only contract marker failure")

        write_fixture(root)
        compile_smoke_marker = (
            "The note-local compile-smoke companion in this lane is `Documentation/zigux/phase12-cross-compile-smoke.md`, "
            "and its directly readable rerun handle is `python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test` "
            "plus `python3 scripts/zigux/check-phase12-cross-compile-smoke.py`; keep that narrower smoke packet explicit "
            "beside the broader validator-first support bundle without treating it as DMA, queue ownership, throughput, "
            "recovery, or driver-delivery proof."
        )
        (root / NOTE_PATH).write_text(
            read_text(root, NOTE_PATH).replace(compile_smoke_marker, "", 1),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-complex-driver-lane-sequencing.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected compile-smoke marker failure")

        write_fixture(root)
        direct_read_bridge_readme = "`scripts/zigux/README.md`, "
        (root / NOTE_PATH).writeText(
            read_text(root, NOTE_PATH).replace(direct_read_bridge_readme, "", 1),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-complex-driver-lane-sequencing.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected direct-read bridge README marker failure")

        write_fixture(root)
        survey_build_marker = "`Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py`"
        (root / NOTE_PATH).write_text(
            read_text(root, NOTE_PATH).replace(
                survey_build_marker,
                survey_build_marker.replace(
                    ", `zigux/tests/phase12_virtio_scsi_survey_build.zig`", ""
                ),
                1,
            ),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-complex-driver-lane-sequencing.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected virtio_scsi survey-build marker failure")

        write_fixture(root)
        (root / WORKFLOW_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if ".github/workflows/zigux-bootstrap.yml" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected workflow marker failure")

        write_fixture(root)
        (root / BUILD_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/phase12_build.zig" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build marker failure")

        write_fixture(root)
        (root / BUILD_PATH).write_text(
            read_text(root, BUILD_PATH).replace("smoke_step.dependOn(", "__REMOVED__", 1),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/phase12_build.zig" not in str(exc):
                raise
            if "wrong count" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build count failure")

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text("phase12-smoke:\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected makefile marker failure")

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text(
            "\n".join((
                "phase12-validate:",
                "phase12-smoke:",
                "phase12-test:",
                "phase12: phase12-smoke phase12-test",
            ))
            + "\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected stale makefile marker failure")

        write_fixture(root)
        (root / REQUIRED_PRESENT_PATHS[0]).unlink()
        try:
            check(root)
        except CheckFailure as exc:
            if str(REQUIRED_PRESENT_PATHS[0]) not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected required present path failure")

        write_fixture(root)
        forbidden_path = root / FORBIDDEN_PRESENT_PATHS[0]
        forbidden_path.parent.mkdir(parents=True, exist_ok=True)
        forbidden_path.write_text("// stale monolith\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if str(FORBIDDEN_PRESENT_PATHS[0]) not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected forbidden path failure")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture-backed self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        check(args.root)
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail:{exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())