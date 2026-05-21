#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase12_cross_targets.json")
BUILD_FILE_REL = Path("zigux/tests/phase12_cross_build.zig")

EXPECTED_FIXTURE = {
    "phase": "Phase 12",
    "lane_key": "P12-L02",
    "build_file": BUILD_FILE_REL.as_posix(),
    "build_step": "cross",
    "target_count": 3,
    "targets": [
        "x86_64-linux-musl",
        "aarch64-linux-musl",
        "riscv64-linux-musl",
    ],
}

EXPECTED_BUILD_MARKERS = [
    'b.path("phase12_virtio_net.zig")',
    'b.path("phase12_virtio_net_survey.zig")',
    'b.path("phase12_virtio_net_syntax_lab.zig")',
    'b.path("phase12_virtio_scsi.zig")',
    'b.path("phase12_virtio_scsi_survey.zig")',
    'b.path("phase12_virtio_scsi_syntax_lab.zig")',
    'b.path("phase12_nvme_pci.zig")',
    'b.path("phase12_nvme_pci_survey.zig")',
    'b.path("phase12_raw_github_coverage_survey.zig")',
    'b.path("phase12_libbpf_segments.zig")',
    'b.path("phase12_libbpf_reviewability.zig")',
    '.name = "phase12-cross-virtio-net-tests"',
    '.name = "phase12-cross-virtio-net-survey-tests"',
    '.name = "phase12-cross-virtio-net-syntax-lab-tests"',
    '.name = "phase12-cross-virtio-scsi-tests"',
    '.name = "phase12-cross-virtio-scsi-survey-tests"',
    '.name = "phase12-cross-virtio-scsi-syntax-lab-tests"',
    '.name = "phase12-cross-nvme-pci-tests"',
    '.name = "phase12-cross-nvme-pci-survey-tests"',
    '.name = "phase12-cross-raw-github-coverage-survey-tests"',
    '.name = "phase12-cross-libbpf-segment-survey-tests"',
    '.name = "phase12-cross-libbpf-reviewability-tests"',
    'const cross_step = b.step("cross", "Compile the bounded Phase 12 packet for approved non-native musl targets");',
    "cross_step.dependOn(&phase12_virtio_net_tests.step);",
    "cross_step.dependOn(&phase12_virtio_net_survey_tests.step);",
    "cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_survey_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_nvme_pci_tests.step);",
    "cross_step.dependOn(&phase12_nvme_pci_survey_tests.step);",
    "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);",
    "cross_step.dependOn(&phase12_libbpf_segments_tests.step);",
    "cross_step.dependOn(&phase12_libbpf_reviewability_tests.step);",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json_object(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("phase12-cross-build-packet:fixture_expected_object")
    return data


def require_file(root: Path, rel_path: Path) -> Path:
    path = root / rel_path
    if not path.is_file():
        raise SystemExit(f"phase12-cross-build-packet:missing_file:{rel_path.as_posix()}")
    return path


def validate_fixture(doc: dict[str, object]) -> None:
    for key, expected in EXPECTED_FIXTURE.items():
        if doc.get(key) != expected:
            raise SystemExit(f"phase12-cross-build-packet:fixture_{key}")


def require_markers(rel_path: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase12-cross-build-packet:missing_marker:{rel_path.as_posix()}:{marker}"
            )


def check_packet(root: Path) -> None:
    fixture_path = require_file(root, FIXTURE_REL)
    build_path = require_file(root, BUILD_FILE_REL)
    validate_fixture(load_json_object(fixture_path))
    require_markers(BUILD_FILE_REL, build_path.read_text(encoding="utf-8"), EXPECTED_BUILD_MARKERS)


def sample_build_file() -> str:
    return "\n".join(
        [
            "const std = @import(\"std\");",
            "",
            "pub fn build(b: *std.Build) void {",
            *[f"    {marker}" for marker in EXPECTED_BUILD_MARKERS],
            "}",
            "",
        ]
    )


def write_sample_root(root: Path) -> None:
    write_text(root / FIXTURE_REL, json.dumps(EXPECTED_FIXTURE, indent=2) + "\n")
    write_text(root / BUILD_FILE_REL, sample_build_file())


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual = str(exc)
        if actual != expected_message:
            raise SystemExit(
                f"phase12-cross-build-packet:self-test:{label}:expected={expected_message!r}:actual={actual!r}"
            ) from exc
        return
    raise SystemExit(
        f"phase12-cross-build-packet:self-test:{label}:missing_system_exit:{expected_message!r}"
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase12-cross-build-packet-") as tmp:
        root = Path(tmp)
        checks_run = 0

        write_sample_root(root)
        check_packet(root)
        checks_run += 1

        (root / BUILD_FILE_REL).unlink()
        expect_system_exit(
            "missing_build_file",
            lambda: check_packet(root),
            f"phase12-cross-build-packet:missing_file:{BUILD_FILE_REL.as_posix()}",
        )
        checks_run += 1

        write_sample_root(root)
        payload = load_json_object(root / FIXTURE_REL)
        payload["lane_key"] = "P12-L06"
        write_text(root / FIXTURE_REL, json.dumps(payload, indent=2) + "\n")
        expect_system_exit(
            "fixture_lane_key",
            lambda: check_packet(root),
            "phase12-cross-build-packet:fixture_lane_key",
        )
        checks_run += 1

        write_sample_root(root)
        payload = load_json_object(root / FIXTURE_REL)
        payload["target_count"] = 2
        write_text(root / FIXTURE_REL, json.dumps(payload, indent=2) + "\n")
        expect_system_exit(
            "fixture_target_count",
            lambda: check_packet(root),
            "phase12-cross-build-packet:fixture_target_count",
        )
        checks_run += 1

        write_sample_root(root)
        build_path = root / BUILD_FILE_REL
        build_text = build_path.read_text(encoding="utf-8").replace(
            'const cross_step = b.step("cross", "Compile the bounded Phase 12 packet for approved non-native musl targets");',
            "",
            1,
        )
        write_text(build_path, build_text)
        expect_system_exit(
            "missing_cross_step_marker",
            lambda: check_packet(root),
            "phase12-cross-build-packet:missing_marker:zigux/tests/phase12_cross_build.zig:const cross_step = b.step(\"cross\", \"Compile the bounded Phase 12 packet for approved non-native musl targets\");",
        )
        checks_run += 1

        write_sample_root(root)
        build_path = root / BUILD_FILE_REL
        build_text = build_path.read_text(encoding="utf-8").replace(
            '.name = "phase12-cross-libbpf-reviewability-tests"',
            "",
            1,
        )
        write_text(build_path, build_text)
        expect_system_exit(
            "missing_test_marker",
            lambda: check_packet(root),
            'phase12-cross-build-packet:missing_marker:zigux/tests/phase12_cross_build.zig:.name = "phase12-cross-libbpf-reviewability-tests"',
        )
        checks_run += 1

    print("PHASE12_CROSS_BUILD_PACKET_SELF_TEST=pass")
    print(f"PHASE12_CROSS_BUILD_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail close when the Phase 12 cross-build packet drifts away from the expected P12-L02 inventory."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in packet checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for the checker and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    check_packet(args.root.resolve())
    print("PHASE12_CROSS_BUILD_PACKET=pass")
    print("PHASE12_CROSS_BUILD_PACKET_REQUIRED_FILE_COUNT=2")
    print(f"PHASE12_CROSS_BUILD_PACKET_REQUIRED_MARKER_COUNT={len(EXPECTED_BUILD_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
