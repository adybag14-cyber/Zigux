#!/usr/bin/env python3
"""Fail-closed checker for the surviving Phase 11 UAPI header current-head packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SURVEY = Path("Documentation/zigux/phase11-uapi-header-parity-survey.md")
MATRIX = Path("Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md")
INVENTORY = Path("zigux/tests/fixtures/phase11_build_inventory.json")
EXPORT_PROOF = Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig")
HV_OPS_PROOF = Path("zigux/tests/phase11_hvc_hv_ops_layout_proof.zig")
HEADER = Path("drivers/tty/hvc/hvc_console.h")

SURVEY_MARKERS = (
    "`PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_gap_reopened`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "the broader shared ABI replay remains a real gap on current `master`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`zigux/tests/phase11_build.zig`",
)

MATRIX_MARKERS = (
    "`PHASE11_UAPI_HEADER_MATRIX_STATUS=adjacent_proof_shard_readback_only`",
    "- lane: `P11-L02`",
    "`Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "keep those paths framed as repo-reality gaps or archival wording until a future reread proves they returned",
    "using the HVC-only inventory as proof that the full shared header-boundary packet is landed again",
)

EXPORT_PROOF_MARKERS = (
    'test "phase11 HVC exported helper proof keeps winsize layout explicit" {',
    'layout_assert.assertOffset(WinsizeLayout, "ws_row", 0);',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    'try expectContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");',
)

HV_OPS_PROOF_MARKERS = (
    'test "phase11 hvc hv_ops layout proof keeps callback table explicit" {',
    'try layout_assert.expectOffset(HvOps, "notifier_hangup", 40);',
    'try expectContains(hvc_header, "(*dtr_rts)");',
)

HEADER_MARKERS = (
    "#define MAX_NR_HVC_CONSOLES 16",
    "#define HVC_ALLOC_TTY_ADAPTERS 1",
    "struct hv_ops {",
    "(*get_chars)",
    "(*notifier_hangup)",
    "void notifier_hangup_irq(struct hvc_struct *hp, int irq);",
)

EXPECTED_INVENTORY = {
    "proof_build_file": "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_replay_command": "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_step_name": "test",
    "proof_test_artifact_name": "phase11-hvc-cleanup-packet-proof",
    "build_test_names": [
        "phase11-hvc-hv-ops-layout-proof-tests",
        "phase11-hvc-export-surface-layout-proof-tests",
        "phase11-hvc-cleanup-packet-proof",
    ],
    "shared_test_depend_steps": [],
    "dedicated_survey_replays": [],
    "shared_split_replays": [],
    "shared_replay_markers": [],
}


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def run_check(root: Path) -> None:
    require_markers(root, SURVEY, "survey", SURVEY_MARKERS)
    require_markers(root, MATRIX, "matrix", MATRIX_MARKERS)
    require_markers(root, EXPORT_PROOF, "export proof", EXPORT_PROOF_MARKERS)
    require_markers(root, HV_OPS_PROOF, "hv_ops proof", HV_OPS_PROOF_MARKERS)
    require_markers(root, HEADER, "header", HEADER_MARKERS)

    payload = json.loads(read_text(root / INVENTORY))
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {INVENTORY}")
    for key, value in EXPECTED_INVENTORY.items():
        if payload.get(key) != value:
            raise CheckError(f"{key} does not match the current-head Phase 11 packet")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY, "\n".join(SURVEY_MARKERS) + "\n")
    write(root / MATRIX, "\n".join(MATRIX_MARKERS) + "\n")
    write(root / EXPORT_PROOF, "\n".join(EXPORT_PROOF_MARKERS) + "\n")
    write(root / HV_OPS_PROOF, "\n".join(HV_OPS_PROOF_MARKERS) + "\n")
    write(root / HEADER, "\n".join(HEADER_MARKERS) + "\n")
    write(root / INVENTORY, json.dumps(EXPECTED_INVENTORY, indent=2) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_uapi_header_current_head_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_survey = tmpdir / "missing_survey"
        shutil.copytree(fixture, missing_survey, dirs_exist_ok=True)
        write(
            missing_survey / SURVEY,
            read_text(missing_survey / SURVEY).replace("`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`\n", "", 1),
        )
        expect_failure(missing_survey, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`")
        case_count += 1

        missing_matrix = tmpdir / "missing_matrix"
        shutil.copytree(fixture, missing_matrix, dirs_exist_ok=True)
        write(
            missing_matrix / MATRIX,
            read_text(missing_matrix / MATRIX).replace("`Documentation/zigux/phase11-shared-replay-contract.md`\n", "", 1),
        )
        expect_failure(missing_matrix, "`Documentation/zigux/phase11-shared-replay-contract.md`")
        case_count += 1

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        payload = json.loads(read_text(wrong_inventory / INVENTORY))
        payload["build_test_names"] = payload["build_test_names"][:-1]
        write(wrong_inventory / INVENTORY, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_inventory, "build_test_names does not match")
        case_count += 1

        print("PHASE11_UAPI_HEADER_CURRENT_HEAD_PACKET_SELF_TEST=pass")
        print(f"PHASE11_UAPI_HEADER_CURRENT_HEAD_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_UAPI_HEADER_CURRENT_HEAD_PACKET=fail: {exc}")
        return 1

    print("PHASE11_UAPI_HEADER_CURRENT_HEAD_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
