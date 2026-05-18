#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 UAPI header direct-readback packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


FILES = {
    "manifest": "zigux/tests/phase11_uapi_header_direct_readback_manifest.json",
    "matrix": "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
    "survey": "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "matrix_gap": "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "hvc_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "export_proof": "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "hv_ops_proof": "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "proof_build": "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
    "header": "drivers/tty/hvc/hvc_console.h",
}

EXPECTED_MANIFEST = {
    "lane_key": "P11-L02",
    "phase": "Phase 11",
    "packet_status": "adjacent_proof_shard_readback_only",
    "scope": "shared UAPI header direct-readback packet",
    "direct_readback_surfaces": [
        {
            "path": "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
            "sha": "6a9d96ce41ed38ce4f889529b47f85c0418d6e6a",
        },
        {
            "path": "Documentation/zigux/phase11-uapi-header-parity-survey.md",
            "sha": "85265de16d6870921b82f8c49029c37487644802",
        },
        {
            "path": "Documentation/zigux/phase11-driver-lane-sequencing.md",
            "sha": "74275c76e44e642820e4a88e2c02202c704d433c",
        },
        {
            "path": "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
            "sha": "9a81df37cce6219fb3058346e69875afa73299c1",
        },
        {
            "path": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
            "sha": "b41c8e478e4ac81fdfd207cdfb75ad46e9a0859e",
        },
        {
            "path": "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
            "sha": "7b8852efe8ada4b26cdba6746d6ddbd21104590d",
        },
        {
            "path": "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
            "sha": "4b19ff7f739fb62c63677e52b34aa4099f7a5742",
        },
        {
            "path": "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
            "sha": "855803078c6d0e8c2f27afdf4c086dd7bf77616b",
        },
        {
            "path": "zigux/tests/fixtures/phase11_build_inventory.json",
            "sha": "f943c5c0ef282231b0932297728df95acdfb0fb4",
        },
        {
            "path": "drivers/tty/hvc/hvc_console.h",
            "sha": "57f1542b3e6f1901f444bc2d94b5e438f14eb9b3",
        },
    ],
    "missing_shared_replay_surfaces": [
        "zigux/tests/phase11_uapi_header_parity_manifest.json",
        "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "zigux/tests/phase11_build.zig",
        "Documentation/zigux/phase11-shared-replay-contract.md",
        "scripts/zigux/check-phase11-header-boundary-packet.py",
    ],
    "inventory_boundary": {
        "path": "zigux/tests/fixtures/phase11_build_inventory.json",
        "build_test_names": [
            "phase11-hvc-console-tests",
            "phase11-hvc-console-verify-tests",
            "phase11-hvc-cleanup-tests",
            "phase11-hvc-console-survey-tests",
        ],
        "shared_depend_steps": [
            "run_phase11_hvc_console_tests",
            "run_hvc_console_verify_tests",
            "run_phase11_hvc_cleanup_tests",
        ],
        "proof_adjunct_replays": [
            "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
            "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
        ],
    },
    "proof_build": {
        "build_file": "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
        "command": "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig --summary all",
    },
}

MATRIX_MARKERS = (
    "`PHASE11_UAPI_HEADER_MATRIX_STATUS=adjacent_proof_shard_readback_only`",
    "lane: `P11-L02`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
)

SURVEY_MARKERS = (
    "`PHASE11_HEADER_BOUNDARY_STATUS=adjacent_proof_shard_readback_only`",
    "lane: `P11-L18`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`zigux/tests/phase11_uapi_header_parity_survey.zig`",
    "`zigux/tests/phase11_build.zig`",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
)

LANE_NOTE_MARKERS = (
    "shared header-boundary follow-through stays adjacent to `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "Prefer one Phase 11 lane at a time",
)

MATRIX_GAP_MARKERS = (
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "adjacent shared header-boundary matrix",
)

HVC_MATRIX_MARKERS = (
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
)

EXPORT_PROOF_MARKERS = (
    'test "phase11 HVC exported helper proof keeps winsize layout explicit"',
    'test "phase11 HVC exported helper proof keeps hv_ops callback table layout explicit"',
)

HV_OPS_PROOF_MARKERS = (
    'test "phase11 hvc hv_ops layout proof keeps callback table explicit"',
    'test "phase11 hvc hv_ops layout proof stays tied to the exported header"',
)

PROOF_BUILD_MARKERS = (
    "phase11_hvc_hv_ops_layout_proof.zig",
    "phase11_hvc_export_surface_layout_proof.zig",
    'b.step("test", "Run the focused Phase 11 exported-header proofs")',
)

HEADER_MARKERS = (
    "struct winsize {",
    "struct hv_ops {",
    "int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);",
)

EXPECTED_BUILD_TEST_NAMES = [
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
]
EXPECTED_DEPEND_STEPS = [
    "run_phase11_hvc_console_tests",
    "run_hvc_console_verify_tests",
    "run_phase11_hvc_cleanup_tests",
]
EXPECTED_ADJUNCT_REPLAYS = [
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
]


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckError(f"expected object in {path.as_posix()}")
    return data


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path.as_posix()}: {marker}")


def require_manifest(root: Path) -> None:
    manifest = read_json(root / FILES["manifest"])
    if manifest != EXPECTED_MANIFEST:
        raise CheckError("manifest body does not match the current Phase 11 direct-readback packet")


def require_inventory(root: Path) -> None:
    inventory = read_json(root / FILES["inventory"])
    if inventory.get("build_test_names") != EXPECTED_BUILD_TEST_NAMES:
        raise CheckError("phase11 build inventory build_test_names drifted")
    if inventory.get("shared_test_depend_steps") != EXPECTED_DEPEND_STEPS:
        raise CheckError("phase11 build inventory shared_test_depend_steps drifted")
    if inventory.get("shared_adjunct_replays") != EXPECTED_ADJUNCT_REPLAYS:
        raise CheckError("phase11 build inventory shared_adjunct_replays drifted")


def run_check(root: Path) -> None:
    require_manifest(root)
    require_markers(root / FILES["matrix"], MATRIX_MARKERS)
    require_markers(root / FILES["survey"], SURVEY_MARKERS)
    require_markers(root / FILES["lane_note"], LANE_NOTE_MARKERS)
    require_markers(root / FILES["matrix_gap"], MATRIX_GAP_MARKERS)
    require_markers(root / FILES["hvc_matrix"], HVC_MATRIX_MARKERS)
    require_markers(root / FILES["export_proof"], EXPORT_PROOF_MARKERS)
    require_markers(root / FILES["hv_ops_proof"], HV_OPS_PROOF_MARKERS)
    require_markers(root / FILES["proof_build"], PROOF_BUILD_MARKERS)
    require_markers(root / FILES["header"], HEADER_MARKERS)
    require_inventory(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["manifest"], json.dumps(EXPECTED_MANIFEST, indent=2) + "\n")
    write(root / FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
    write(root / FILES["survey"], "\n".join(SURVEY_MARKERS) + "\n")
    write(root / FILES["lane_note"], "\n".join(LANE_NOTE_MARKERS) + "\n")
    write(root / FILES["matrix_gap"], "\n".join(MATRIX_GAP_MARKERS) + "\n")
    write(root / FILES["hvc_matrix"], "\n".join(HVC_MATRIX_MARKERS) + "\n")
    write(root / FILES["export_proof"], "\n".join(EXPORT_PROOF_MARKERS) + "\n")
    write(root / FILES["hv_ops_proof"], "\n".join(HV_OPS_PROOF_MARKERS) + "\n")
    write(root / FILES["proof_build"], "\n".join(PROOF_BUILD_MARKERS) + "\n")
    write(root / FILES["header"], "\n".join(HEADER_MARKERS) + "\n")
    write(
        root / FILES["inventory"],
        json.dumps(
            {
                "build_test_names": EXPECTED_BUILD_TEST_NAMES,
                "shared_test_depend_steps": EXPECTED_DEPEND_STEPS,
                "shared_adjunct_replays": EXPECTED_ADJUNCT_REPLAYS,
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_uapi_header_direct_readback_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        manifest_case = tmpdir / "manifest_case"
        shutil.copytree(fixture, manifest_case, dirs_exist_ok=True)
        manifest = read_json(manifest_case / FILES["manifest"])
        manifest["packet_status"] = "stale"
        write(manifest_case / FILES["manifest"], json.dumps(manifest, indent=2) + "\n")
        expect_failure(manifest_case, "manifest body does not match")

        matrix_case = tmpdir / "matrix_case"
        shutil.copytree(fixture, matrix_case, dirs_exist_ok=True)
        write(
            matrix_case / FILES["matrix"],
            read_text(matrix_case / FILES["matrix"]).replace(MATRIX_MARKERS[1] + "\n", "", 1),
        )
        expect_failure(matrix_case, MATRIX_MARKERS[1])

        survey_case = tmpdir / "survey_case"
        shutil.copytree(fixture, survey_case, dirs_exist_ok=True)
        write(
            survey_case / FILES["survey"],
            read_text(survey_case / FILES["survey"]).replace(SURVEY_MARKERS[4] + "\n", "", 1),
        )
        expect_failure(survey_case, SURVEY_MARKERS[4])

        inventory_case = tmpdir / "inventory_case"
        shutil.copytree(fixture, inventory_case, dirs_exist_ok=True)
        inventory = read_json(inventory_case / FILES["inventory"])
        inventory["shared_adjunct_replays"] = EXPECTED_ADJUNCT_REPLAYS[:1]
        write(inventory_case / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(inventory_case, "shared_adjunct_replays drifted")

        build_case = tmpdir / "build_case"
        shutil.copytree(fixture, build_case, dirs_exist_ok=True)
        write(
            build_case / FILES["proof_build"],
            read_text(build_case / FILES["proof_build"]).replace(PROOF_BUILD_MARKERS[2] + "\n", "", 1),
        )
        expect_failure(build_case, PROOF_BUILD_MARKERS[2])

        header_case = tmpdir / "header_case"
        shutil.copytree(fixture, header_case, dirs_exist_ok=True)
        write(
            header_case / FILES["header"],
            read_text(header_case / FILES["header"]).replace(HEADER_MARKERS[1] + "\n", "", 1),
        )
        expect_failure(header_case, HEADER_MARKERS[1])

        print("PHASE11_UAPI_HEADER_DIRECT_READBACK_SELF_TEST=pass")
        print("PHASE11_UAPI_HEADER_DIRECT_READBACK_SELF_TEST_CASE_COUNT=6")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_root = script_path.parents[2] if len(script_path.parents) > 2 else Path.cwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_UAPI_HEADER_DIRECT_READBACK=fail: {exc}")
        return 1

    print("PHASE11_UAPI_HEADER_DIRECT_READBACK=pass")
    print("PHASE11_UAPI_HEADER_DIRECT_READBACK_SURFACE_COUNT=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
