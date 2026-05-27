#!/usr/bin/env python3
"""Fail-closed checker for the Phase 12 tests-root complex-driver packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_TESTS_README_COMPLEX_DRIVER_PACKET"

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/README.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
COMPLEX_DRIVER_NOTE_PATH = Path(
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
RELEASE_READINESS_PATH = Path(
    "Documentation/zigux/phase12-release-readiness-survey.md"
)
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_ONLY_CHECKER_PATH = Path("scripts/zigux/check-build-only-phase12-surface.py")
COMPLEX_DRIVER_CHECKER_PATH = Path(
    "scripts/zigux/check-phase12-complex-driver-lane-packet.py"
)
CROSS_COMPILE_CHECKER_PATH = Path(
    "scripts/zigux/check-phase12-cross-compile-smoke.py"
)
RELEASE_READINESS_CHECKER_PATH = Path(
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
LIBBPF_SNAPSHOT_CHECKER_PATH = Path("scripts/zigux/check-phase12-libbpf-snapshot.py")
LIBBPF_LANE_MARKER_CHECKER_PATH = Path(
    "scripts/zigux/check-phase12-libbpf-lane-marker.py"
)
LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = Path(
    "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py"
)
VALIDATOR_PATH = Path("scripts/zigux/validate-phase12.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    TESTS_README_PATH,
    SCRIPTS_README_PATH,
    COMPLEX_DRIVER_NOTE_PATH,
    RELEASE_READINESS_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    BUILD_ONLY_CHECKER_PATH,
    COMPLEX_DRIVER_CHECKER_PATH,
    CROSS_COMPILE_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    LIBBPF_HEAVY_CONSUMER_CHECKER_PATH,
    VALIDATOR_PATH,
    WORKFLOW_PATH,
)

TESTS_README_MARKERS = (
    "## Phase 12 shared release packet",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`scripts/zigux/check-phase12-complex-driver-lane-packet.py`",
    "`scripts/zigux/check-phase12-cross-compile-smoke.py`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`scripts/zigux/check-phase12-libbpf-snapshot.py`",
    "`scripts/zigux/check-phase12-libbpf-lane-marker.py`",
    "`scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`",
    "`scripts/zigux/validate-phase12.py`",
    "`make -C zigux phase12-validate`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12-test`",
    "`make -C zigux phase12`",
    "`zigux/tests/phase12_virtio_net_queue_resume.zig`",
    "`zigux/tests/phase12_virtio_net_receive_refill_replay.zig`",
    "`zigux/tests/phase12_virtio_net_transmit_recycle.zig`",
    "`zigux/tests/phase12_virtio_net_post_reset_replay.zig`",
    "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_survey.zig`",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
    "phase12-virtio-net-queue-resume-tests",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12-virtio-net-throughput-parity-tests",
    "phase12-virtio-net-survey-tests",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "run: python3 scripts/zigux/validate-phase12.py",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {rel}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            raise CheckFailure(f"missing required file: {rel}")

    require_markers(
        read_text(root, TESTS_README_PATH),
        TESTS_README_MARKERS,
        str(TESTS_README_PATH),
    )
    require_markers(read_text(root, BUILD_PATH), BUILD_MARKERS, str(BUILD_PATH))
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS, str(MAKEFILE_PATH))
    require_markers(read_text(root, WORKFLOW_PATH), WORKFLOW_MARKERS, str(WORKFLOW_PATH))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def bullet_fixture(title: str, markers: tuple[str, ...]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def build_fixture() -> str:
    return "\n".join(BUILD_MARKERS) + "\n"


def write_fixture_tree(root: Path) -> None:
    write_text(root / TESTS_README_PATH, bullet_fixture("# zigux/tests", TESTS_README_MARKERS))
    write_text(root / BUILD_PATH, build_fixture())
    write_text(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / WORKFLOW_PATH, "\n".join(WORKFLOW_MARKERS) + "\n")

    placeholder_files = (
        SCRIPTS_README_PATH,
        COMPLEX_DRIVER_NOTE_PATH,
        RELEASE_READINESS_PATH,
        BUILD_ONLY_CHECKER_PATH,
        COMPLEX_DRIVER_CHECKER_PATH,
        CROSS_COMPILE_CHECKER_PATH,
        RELEASE_READINESS_CHECKER_PATH,
        LIBBPF_SNAPSHOT_CHECKER_PATH,
        LIBBPF_LANE_MARKER_CHECKER_PATH,
        LIBBPF_HEAVY_CONSUMER_CHECKER_PATH,
        VALIDATOR_PATH,
    )
    for rel in placeholder_files:
        if rel.suffix == ".md":
            write_text(root / rel, "# fixture\n")
        else:
            write_text(root / rel, "#!/usr/bin/env python3\n")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-tests-readme-complex-driver-") as tmp:
        root = Path(tmp)

        write_fixture_tree(root)
        check(root)
        cases += 1

        write_fixture_tree(root)
        readme_text = read_text(root, TESTS_README_PATH).replace(
            "`scripts/zigux/check-phase12-complex-driver-lane-packet.py`\n",
            "",
            1,
        )
        write_text(root / TESTS_README_PATH, readme_text)
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/README.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected README marker failure")

        write_fixture_tree(root)
        build_text = read_text(root, BUILD_PATH).replace(
            "phase12_virtio_net_survey.zig\n",
            "",
            1,
        )
        write_text(root / BUILD_PATH, build_text)
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/phase12_build.zig" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build marker failure")

        write_fixture_tree(root)
        makefile_text = read_text(root, MAKEFILE_PATH).replace(
            "phase12-test:\n",
            "",
            1,
        )
        write_text(root / MAKEFILE_PATH, makefile_text)
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected makefile marker failure")

        write_fixture_tree(root)
        (root / COMPLEX_DRIVER_CHECKER_PATH).unlink()
        try:
            check(root)
        except CheckFailure as exc:
            if "missing required file" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected required file failure")

    return cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test suite.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = run_self_test()
        print(f"{CHECK_NAME}_SELF_TEST=pass")
        print(f"{CHECK_NAME}_SELF_TEST_CASE_COUNT={cases}")
        return 0

    check(args.root.resolve())
    print(f"{CHECK_NAME}=pass")
    print("PHASE12_TESTS_README_COMPLEX_DRIVER_SHARED_ROUTE_COUNT=6")
    print("PHASE12_TESTS_README_COMPLEX_DRIVER_WRAPPER_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
