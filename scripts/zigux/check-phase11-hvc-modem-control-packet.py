#!/usr/bin/env python3
"""Fail-closed checker for the current-head Phase 11 HVC modem-control packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 3 else Path.cwd()

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
COMPANION_PATH = Path(
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
)
MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
DRIVER_PATH = Path("drivers/tty/hvc/hvc_console.zig")
PROOF_PATH = Path("zigux/tests/phase11_hvc_modem_control_proof.zig")
BUILD_PATH = Path("zigux/tests/phase11_hvc_modem_control_proof_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_PACKET_FILES = (
    SURVEY_PATH,
    COMPANION_PATH,
    MATRIX_PATH,
    DRIVER_PATH,
    PROOF_PATH,
    BUILD_PATH,
    INVENTORY_PATH,
    MAKEFILE_PATH,
)

SURVEY_MARKERS = (
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "dedicated modem-control proof pair",
    "focused adjunct route",
)

COMPANION_MARKERS = (
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "focused teardown-adjacent proof route",
    "dedicated modem-control proof pair",
)

MATRIX_MARKERS = (
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "keep the modem-control proof pair directly readable through its focused build route",
)

DRIVER_MARKERS = (
    "pub const ModemControlRequest = struct {",
    "pub const ModemControlSummary = struct {",
    "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
    'test "phase11 hvc console keeps modem-control helper surface reviewable" {',
)

PROOF_MARKERS = (
    'test "phase11 hvc console keeps full modem control callback surfaces reviewable" {',
    'test "phase11 hvc console masks tiocmset requests when hv_ops exposes only tiocmget" {',
    'test "phase11 hvc console keeps clear-only requests distinct from DTR assertion visibility" {',
    'test "phase11 hvc console keeps dedicated dtr_rts callbacks distinct from tiocmset masks" {',
    'test "phase11 hvc console keeps hupcl teardown distinct from callback-backed modem control" {',
)

BUILD_MARKERS = (
    '.root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig")',
    '.root_source_file = b.path("phase11_hvc_modem_control_proof.zig")',
    'root_module.addImport("hvc_console", hvc_console_module);',
    '.name = "phase11-hvc-modem-control-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC modem-control proof.");',
)

INVENTORY_EXACT_CHECK = (
    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig"
)

INVENTORY_FOCUSED_REPLAY = "zigux/tests/phase11_hvc_modem_control_proof_build.zig"

MAKEFILE_MARKERS = (
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
)


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, markers: tuple[str, ...], label: str) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"missing {label} marker: {marker}")


def require_inventory(root: Path) -> None:
    try:
        payload = json.loads(read_text(root / INVENTORY_PATH))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{INVENTORY_PATH} is not valid JSON") from exc

    exact_current_checks = payload.get("exact_current_checks")
    if not isinstance(exact_current_checks, list) or INVENTORY_EXACT_CHECK not in exact_current_checks:
        raise ValidationError(
            f"{INVENTORY_PATH} must keep {INVENTORY_EXACT_CHECK!r} in exact_current_checks"
        )

    focused_direct_build_replays = payload.get("focused_direct_build_replays")
    if (
        not isinstance(focused_direct_build_replays, list)
        or INVENTORY_FOCUSED_REPLAY not in focused_direct_build_replays
    ):
        raise ValidationError(
            f"{INVENTORY_PATH} must keep {INVENTORY_FOCUSED_REPLAY!r} in focused_direct_build_replays"
        )


def validate(root: Path) -> None:
    missing = [str(rel) for rel in REQUIRED_PACKET_FILES if not (root / rel).is_file()]
    if missing:
        raise ValidationError(
            "missing required Phase 11 HVC modem-control packet files: " + ", ".join(missing)
        )

    require_markers(root, SURVEY_PATH, SURVEY_MARKERS, "survey")
    require_markers(root, COMPANION_PATH, COMPANION_MARKERS, "companion")
    require_markers(root, MATRIX_PATH, MATRIX_MARKERS, "matrix")
    require_markers(root, DRIVER_PATH, DRIVER_MARKERS, "driver")
    require_markers(root, PROOF_PATH, PROOF_MARKERS, "proof")
    require_markers(root, BUILD_PATH, BUILD_MARKERS, "build")
    require_inventory(root)
    require_markers(root, MAKEFILE_PATH, MAKEFILE_MARKERS, "makefile")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join(("survey", *SURVEY_MARKERS)) + "\n")
    write(root / COMPANION_PATH, "\n".join(("companion", *COMPANION_MARKERS)) + "\n")
    write(root / MATRIX_PATH, "\n".join(("matrix", *MATRIX_MARKERS)) + "\n")
    write(root / DRIVER_PATH, "\n".join(("driver", *DRIVER_MARKERS)) + "\n")
    write(root / PROOF_PATH, "\n".join(("proof", *PROOF_MARKERS)) + "\n")
    write(root / BUILD_PATH, "\n".join(("build", *BUILD_MARKERS)) + "\n")
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "exact_current_checks": [INVENTORY_EXACT_CHECK],
                "focused_direct_build_replays": [INVENTORY_FOCUSED_REPLAY],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")


def expect_failure(root: Path, rel: Path, needle: str) -> None:
    text = read_text(root / rel)
    write(root / rel, text.replace(needle, "", 1))
    try:
        validate(root)
    except ValidationError as exc:
        if needle not in str(exc) and str(rel) not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {needle!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_modem_control_packet_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        validate(fixture)

        cases = [
            (SURVEY_PATH, "`zigux/tests/phase11_hvc_modem_control_proof.zig`"),
            (COMPANION_PATH, "focused teardown-adjacent proof route"),
            (MATRIX_PATH, "keep the modem-control proof pair directly readable through its focused build route"),
            (DRIVER_PATH, "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {"),
            (PROOF_PATH, 'test "phase11 hvc console keeps dedicated dtr_rts callbacks distinct from tiocmset masks" {'),
            (BUILD_PATH, 'root_module.addImport("hvc_console", hvc_console_module);'),
            (MAKEFILE_PATH, "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig"),
        ]

        for index, (rel, needle) in enumerate(cases, start=1):
            broken = tmpdir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(broken, rel, needle)

        bad_inventory = tmpdir / "bad_inventory"
        shutil.copytree(fixture, bad_inventory, dirs_exist_ok=True)
        write(
            bad_inventory / INVENTORY_PATH,
            json.dumps(
                {
                    "exact_current_checks": [],
                    "focused_direct_build_replays": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        try:
            validate(bad_inventory)
        except ValidationError:
            pass
        else:
            raise AssertionError("expected inventory validation failure")

        print("PHASE11_HVC_MODEM_CONTROL_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_MODEM_CONTROL_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 2}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current-head Phase 11 HVC modem-control packet for drift."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--repo-root", type=Path, dest="root_override")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root_override if args.root_override is not None else args.root
    try:
        validate(root.resolve())
    except ValidationError as exc:
        print(f"PHASE11_HVC_MODEM_CONTROL_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_MODEM_CONTROL_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
