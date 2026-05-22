#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-sequencing.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
RELEASE_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
MAKEFILE_PATH = "zigux/Makefile"

SHARED_WRAPPERS = [
    "make -C zigux phase12-validate",
    "make -C zigux phase12-smoke",
    "make -C zigux phase12-test",
    "make -C zigux phase12",
]

SHARED_VIRTIO_NET_SEXTET = [
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
]

REQUIRED_FILES = [
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_PATH,
    RELEASE_CLOSURE_PATH,
    RELEASE_MATRIX_PATH,
    MAKEFILE_PATH,
]

REQUIRED_MARKERS = {
    RELEASE_SEQUENCING_PATH: [
        "This note is the release-order companion for the active Phase 12 packet.",
        "validator-first then smoke-first",
        "repo-local `.zig-toolchain` fallback",
        *SHARED_WRAPPERS,
        *SHARED_VIRTIO_NET_SEXTET,
    ],
    RELEASE_READINESS_PATH: [
        "It is a PMO release artifact, not a new replay route.",
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "repo-local `.zig-toolchain` fallback",
        *SHARED_WRAPPERS,
        *SHARED_VIRTIO_NET_SEXTET,
    ],
    RELEASE_CLOSURE_PATH: [
        "It is a PMO release artifact only.",
        "Keep Phase 12 marked open until every item below is true on current `master`:",
        "repo-local `.zig-toolchain` fallback",
        *SHARED_WRAPPERS,
        *SHARED_VIRTIO_NET_SEXTET,
    ],
    RELEASE_MATRIX_PATH: [
        "This matrix is the compact PMO coordination companion for the active Phase 12 packet.",
        "repo-local `.zig-toolchain` fallback",
        *SHARED_WRAPPERS,
        *SHARED_VIRTIO_NET_SEXTET,
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if the bounded Phase 12 release sequencing, readiness, "
            "closure, and coordination packet drifts away from the shipped wrapper "
            "set or the current shared virtio_net smoke-and-test sextet."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect (defaults to auto-detected repo root).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in sample replay and exit.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample tree to the given path and exit.",
    )
    return parser.parse_args()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def check_packet(root: Path) -> None:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            missing_files.append(relative_path)
            continue

        text = read_text(root, relative_path)
        for marker in REQUIRED_MARKERS[relative_path]:
            if marker not in text:
                missing_markers.append(f"{relative_path}: {marker}")

    if missing_files or missing_markers:
        details = []
        if missing_files:
            details.append("missing files: " + ", ".join(missing_files))
        if missing_markers:
            details.append("missing markers: " + "; ".join(missing_markers))
        raise SystemExit(
            "Phase 12 release coordination packet drift detected: "
            + " | ".join(details)
        )

    print("PHASE12_RELEASE_COORDINATION_PACKET=pass")
    print(f"PHASE12_RELEASE_COORDINATION_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_RELEASE_COORDINATION_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )


def sample_text(relative_path: str) -> str:
    if relative_path == MAKEFILE_PATH:
        return "\n".join(
            [
                "phase12-validate:",
                "\t@true",
                "phase12-smoke:",
                "\t@true",
                "phase12-test:",
                "\t@true",
                "phase12: phase12-validate phase12-smoke phase12-test",
                "",
            ]
        )

    lines = [
        "# Sample",
        "This note is the release-order companion for the active Phase 12 packet.",
        "It is a PMO release artifact, not a new replay route.",
        "It is a PMO release artifact only.",
        "This matrix is the compact PMO coordination companion for the active Phase 12 packet.",
        "Keep Phase 12 marked open until every item below is true on current `master`:",
        "validator-first then smoke-first",
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "repo-local `.zig-toolchain` fallback",
        *SHARED_WRAPPERS,
        *SHARED_VIRTIO_NET_SEXTET,
        "",
    ]
    return "\n".join(lines)


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for relative_path in REQUIRED_FILES:
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(sample_text(relative_path), encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir) / "sample"
        write_sample_root(root)
        check_packet(root)
    print("PHASE12_RELEASE_COORDINATION_PACKET_SELF_TEST=pass")
    print(
        "PHASE12_RELEASE_COORDINATION_PACKET_SELF_TEST_CASE_COUNT=1"
    )


def main() -> None:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return
    if args.self_test:
        run_self_test()
        return
    check_packet(args.root.resolve())


if __name__ == "__main__":
    main()
