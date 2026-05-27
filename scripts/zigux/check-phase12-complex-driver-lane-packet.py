#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 12 complex-driver lane packet."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK_NAME = "PHASE12_COMPLEX_DRIVER_LANE_PACKET"

NOTE_PATH = Path("Documentation/zigux/phase12-complex-driver-lane-sequencing.md")
SUPPORT_BUNDLE_MAP_PATH = Path(
    "Documentation/zigux/phase12-release-support-bundle-map.md"
)
README_PATH = Path("scripts/zigux/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH = Path(
    "scripts/zigux/check-phase12-virtio-net-manifest-presence.py"
)

REQUIRED_FILES = (
    NOTE_PATH,
    SUPPORT_BUNDLE_MAP_PATH,
    README_PATH,
    WORKFLOW_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH,
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
    "The note-local compile-smoke companion in this lane is `Documentation/zigux/phase12-cross-compile-smoke.md`, and its directly readable rerun handle is `python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test` plus `python3 scripts/zigux/check-phase12-cross-compile-smoke.py`; keep that narrower smoke packet explicit beside the broader validator-first support bundle without treating it as DMA, queue ownership, throughput, recovery, or driver-delivery proof.",
)

SUPPORT_BUNDLE_MAP_MARKERS = (
    "- lane owner: `pmo-release`",
    "- `scripts/zigux/check-phase12-complex-driver-lane-packet.py`",
    "- `scripts/zigux/check-phase12-cross-compile-smoke.py`",
    "- `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py`",
    "Those wrappers are current release-planning evidence again, but they do not by themselves close the broader complex-driver tranche.",
)

README_MARKERS = (
    "## Phase 12",
    "- Phase 12 flow - the current scripts-root complex-driver reminder should keep the shared release packet reviewable through the build-only checker, the readiness-note checker, the dedicated anti-overlap checker, the validator entrypoint, the returned `phase12-validate` / `phase12-smoke` / `phase12-test` / `phase12` wrapper split, and the split-helper `virtio_net` evidence packet while keeping the rollback-evidence `virtio_scsi` survey family, the published-but-unwired NVMe foothold, and the parked libbpf packet distinct",
    "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
    "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    "`drivers/net/virtio_net_queue_resume.zig`, `drivers/net/virtio_net_receive_refill_replay.zig`, `drivers/net/virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_post_reset_replay.zig`, `drivers/net/virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` stay the isolated syntax-lab compile-smoke companions, and `make -C zigux phase12-virtio-net-syntax-lab-test` keeps that review-only rerun hook explicit outside the shared smoke-first route.",
    "`drivers/net/virtio_net.zig` and `zigux/tests/phase12_virtio_net.zig` stay absent on current `master`, so keep the shared reminder scoped to the returned split-helper packet rather than reviving the older monolithic starter vocabulary.",
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


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: Path) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def require_counts(text: str, counts: dict[str, int], label: Path) -> None:
    for marker, expected in counts.items():
        actual = text.count(marker)
        if actual != expected:
            raise CheckFailure(
                f"{label} wrong count for {marker!r}: expected {expected}, got {actual}"
            )


def require_paths_present(root: Path, paths: tuple[Path, ...]) -> None:
    for path in paths:
        if not (root / path).is_file():
            raise CheckFailure(f"{CHECK_NAME} missing path: {path}")


def require_paths_absent(root: Path, paths: tuple[Path, ...]) -> None:
    for path in paths:
        if (root / path).exists():
            raise CheckFailure(f"{CHECK_NAME} unexpected path present: {path}")


def run_manifest_presence_checker(root: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(root / VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH),
            "--root",
            str(root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return

    combined_output = " | ".join(
        line.strip()
        for line in f"{result.stdout}\n{result.stderr}".splitlines()
        if line.strip()
    )
    if combined_output:
        raise CheckFailure(
            "virtio_net manifest presence checker failed: "
            f"{combined_output}"
        )
    raise CheckFailure("virtio_net manifest presence checker failed")


def check(root: Path) -> None:
    for path in REQUIRED_FILES:
        if not (root / path).is_file():
            raise CheckFailure(f"missing required file: {path}")

    require_paths_present(root, REQUIRED_PRESENT_PATHS)
    require_paths_absent(root, FORBIDDEN_PRESENT_PATHS)
    run_manifest_presence_checker(root)

    require_markers(read_text(root, NOTE_PATH), NOTE_MARKERS, NOTE_PATH)
    require_markers(
        read_text(root, SUPPORT_BUNDLE_MAP_PATH),
        SUPPORT_BUNDLE_MAP_MARKERS,
        SUPPORT_BUNDLE_MAP_PATH,
    )
    require_markers(read_text(root, README_PATH), README_MARKERS, README_PATH)
    require_markers(read_text(root, WORKFLOW_PATH), WORKFLOW_MARKERS, WORKFLOW_PATH)

    build_text = read_text(root, BUILD_PATH)
    require_markers(build_text, BUILD_MARKERS, BUILD_PATH)
    require_counts(build_text, BUILD_COUNT_MARKERS, BUILD_PATH)

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(makefile_text, MAKEFILE_MARKERS, MAKEFILE_PATH)
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile_text:
            raise CheckFailure(f"{MAKEFILE_PATH} stale marker present: {marker}")


def build_fixture_text() -> str:
    lines: list[str] = []
    for marker, count in BUILD_COUNT_MARKERS.items():
        lines.extend(marker for _ in range(count))
    lines.extend(BUILD_MARKERS)
    return "\n".join(lines) + "\n"


def manifest_presence_checker_fixture_text() -> str:
    return """#!/usr/bin/env python3
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--root")
args = parser.parse_args()
marker_path = Path(args.root) / "virtio_net_manifest_presence_should_fail"
if marker_path.exists():
    print("PHASE12_VIRTIO_NET_MANIFEST_PRESENCE=fail")
    print("PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_DETAIL=fixture failure")
    raise SystemExit(1)
print("PHASE12_VIRTIO_NET_MANIFEST_PRESENCE=pass")
"""


def write_fixture(root: Path) -> None:
    fixtures = {
        NOTE_PATH: "\n".join(NOTE_MARKERS) + "\n",
        SUPPORT_BUNDLE_MAP_PATH: "\n".join(SUPPORT_BUNDLE_MAP_MARKERS) + "\n",
        README_PATH: "\n".join(README_MARKERS) + "\n",
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        BUILD_PATH: build_fixture_text(),
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH: (
            manifest_presence_checker_fixture_text()
        ),
    }
    for path, text in fixtures.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    for path in REQUIRED_PRESENT_PATHS:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("// fixture\n", encoding="utf-8")

    for path in FORBIDDEN_PRESENT_PATHS:
        target = root / path
        if target.exists():
            target.unlink()

    failure_marker = root / "virtio_net_manifest_presence_should_fail"
    if failure_marker.exists():
        failure_marker.unlink()


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        check(root)
    except CheckFailure as exc:
        if expected_fragment not in str(exc):
            raise
        return
    raise AssertionError(f"expected failure containing: {expected_fragment}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-complex-driver-lane-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / NOTE_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, str(NOTE_PATH))
        cases += 1

        write_fixture(root)
        (root / SUPPORT_BUNDLE_MAP_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, str(SUPPORT_BUNDLE_MAP_PATH))
        cases += 1

        write_fixture(root)
        (root / README_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, str(README_PATH))
        cases += 1

        write_fixture(root)
        (root / WORKFLOW_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, str(WORKFLOW_PATH))
        cases += 1

        write_fixture(root)
        (root / BUILD_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, str(BUILD_PATH))
        cases += 1

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text("phase12-smoke:\n", encoding="utf-8")
        expect_failure(root, str(MAKEFILE_PATH))
        cases += 1

        write_fixture(root)
        (root / VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH).unlink()
        expect_failure(root, str(VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH))
        cases += 1

        write_fixture(root)
        (root / REQUIRED_PRESENT_PATHS[0]).unlink()
        expect_failure(root, str(REQUIRED_PRESENT_PATHS[0]))
        cases += 1

        write_fixture(root)
        forbidden = root / FORBIDDEN_PRESENT_PATHS[0]
        forbidden.parent.mkdir(parents=True, exist_ok=True)
        forbidden.write_text("// stale monolith\n", encoding="utf-8")
        expect_failure(root, str(FORBIDDEN_PRESENT_PATHS[0]))
        cases += 1

        write_fixture(root)
        (root / "virtio_net_manifest_presence_should_fail").write_text(
            "fail\n", encoding="utf-8"
        )
        expect_failure(root, "virtio_net manifest presence checker failed")
        cases += 1

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-tests.")
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
