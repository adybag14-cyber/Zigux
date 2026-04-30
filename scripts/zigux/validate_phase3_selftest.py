from __future__ import annotations

import json
import tempfile
from pathlib import Path

from phase3_catalog import Phase3Paths, Phase3Slice, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub, shared_runner_gate_for_slug
from validate_phase3_core import (
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_SOURCE_MARKERS,
    build_smoke_commands,
    select_slices,
    validate_abi_expected_fixture,
    validate_export_uapi_boundary,
    validate_manifest,
    validate_slices,
    validate_source_markers,
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        paths = Phase3Paths(
            root=root,
            docs_dir=root / "Documentation" / "zigux",
            scripts_dir=root / "scripts" / "zigux",
            tests_dir=root / "zigux" / "tests",
            fixtures_dir=root / "zigux" / "tests" / "fixtures",
        )
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, paths.fixtures_dir):
            path.mkdir(parents=True, exist_ok=True)

        fixture_dir = paths.fixtures_dir / "phase3_alpha"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    shared_runner_gate_for_slug("alpha"),
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-alpha.py").write_text(
            render_wrapper_stub(), encoding="utf-8", newline="\n"
        )
        (paths.scripts_dir / "validate_phase3_core.py").writeText if False else None
