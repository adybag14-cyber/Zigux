from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import replace
from pathlib import Path

from phase3_catalog import Phase3Paths, Phase3Slice, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub, shared_runner_gate_for_slug
from validate_phase3_core import (
    ABI_REVIEW_CHECKLIST_MARKERS,
    ABI_EXPORT_UAPI_SURVEY_CHECK_REL,
    ABI_POLICY_UNSAFE_MMIO_CONSUMER_REL,
    ABI_POLICY_UNSAFE_SURVEY_CHECK_REL,
    ABI_REQUIRED_DOC_MARKERS,
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_MANIFEST_FILES,
    ABI_REQUIRED_SOURCE_MARKERS,
    ABI_EXPORT_UAPI_BUILD_FILE_REL,
    ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL,
    ABI_LOW_LEVEL_BUILD_FILE_REL,
    ABI_LOW_LEVEL_SURVEY_CHECK_REL,
    ABI_POLICY_UNSAFE_BUILD_FILE_REL,
    BUILD_FILE_REL,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS,
    _validate_build_smoke,
    build_smoke_commands,
    select_slices,
    validate_export_uapi_boundary,
    validate_low_level_wrapper_boundary,
    validate_low_level_wrapper_exports,
    validate_policy_unsafe_boundary,
    validate_manifest,
    validate_slices,
    validate_source_markers,
)


RBTREE_SHARED_MISSING_MARKER_CASES = PHASE3_SHARED_RBTREE_RECORD_MARKERS
RBTREE_SHARED_CONTRACT_TEST_REL = "zigux/tests/phase3_rbtree_shared_contract.zig"
RBTREE_SHARED_CHECKER_REL = "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py"
README_TOOLING_INVENTORY_SCRIPT = "check-phase3-readme-tooling-inventory.py"
TOOLING_PACKET_SCRIPT = "check-phase3-tooling-packet.py"
VALIDATION_FLOW_SCRIPT = "check-phase3-validation-flow.py"


def _write_phase3_slice(
    paths: Phase3Paths,
    *,
    slug: str,
    status: str = "ready",
) -> None:
    fixture_dir = paths.fixtures_dir / f"phase3_{slug}"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    (paths.docs_dir / f"phase3-{slug}-slice.md").write_text(
        "\n".join(
            [
                f"PHASE3_STATUS={status}",
                f"PHASE3_SLICE={slug}-slice",
                "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                shared_runner_gate_for_slug(slug),
                "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    (paths.scripts_dir / f"check-phase3-{slug}.py").write_text(
        render_wrapper_stub(),
        encoding="utf-8",
        newline="\n",
    )
    (paths.tests_dir / f"phase3_{slug}_dump.zig").write_text(
        f"// {slug} dump\n",
        encoding="utf-8",
        newline="\n",
    )
    (fixture_dir / "expected.json").write_text(
        json.dumps({"abi_version": 1, "constants": ABI_REQUIRED_EXPECTED_CONSTANTS, "structs": {}}),
        encoding="utf-8",
        newline="\n",
    )
    (fixture_dir / f"phase3_{slug}_c_harness.c").write_text(
        f"// {slug} harness\n",
        encoding="utf-8",
        newline="\n",
    )
    (paths.fixtures_dir / f"phase3_{slug}_manifest.json").write_text(
        json.dumps(
            {
                "phase": "Phase 3",
                "status": status,
                "slice": f"{slug}-slice",
                "files": [
                    f"Documentation/zigux/phase3-{slug}-slice.md",
                    f"zigux/tests/phase3_{slug}_dump.zig",
                    f"zigux/tests/fixtures/phase3_{slug}/expected.json",
                    f"zigux/tests/fixtures/phase3_{slug}/phase3_{slug}_c_harness.c",
                ],
                "file_count": 4,
            }
        ),
        encoding="utf-8",
        newline="\n",
    )


def _write_phase3_abi_fixture(paths: Phase3Paths) -> None:
    _write_phase3_slice(paths, slug="abi")
    manifest_path = paths.fixtures_dir / "phase3_abi_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    extra_files = [rel for rel in ABI_REQUIRED_MANIFEST_FILES if rel not in manifest["files"]]
    for rel in extra_files:
        path = paths.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"// fixture for {rel}\n", encoding="utf-8", newline="\n")
    manifest["files"] = [*manifest["files"], *extra_files]
    manifest["file_count"] = len(manifest["files"])
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")


def _run_export_uapi_build_marker_self_test() -> int:
    rel = ABI_EXPORT_UAPI_BUILD_FILE_REL
    export_uapi_markers = ABI_REQUIRED_SOURCE_MARKERS[rel][:4]
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_build_markers_") as tmp_dir:
        root = Path(tmp_dir)
        build_path = root / rel
        build_path.parent.mkdir(parents=True, exist_ok=True)

        build_path.write_text(
            "\n".join(export_uapi_markers[1:]) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(root, {rel: export_uapi_markers}) == [
            f"source-marker: {rel} missing {export_uapi_markers[0]}"
        ]

        build_path.write_text(
            "\n".join(export_uapi_markers[:3]) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(root, {rel: export_uapi_markers}) == [
            f"source-marker: {rel} missing {export_uapi_markers[3]}"
        ]

        build_path.write_text(
            "\n".join(export_uapi_markers) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(root, {rel: export_uapi_markers}) == []

    return 0


def _run_readme_tooling_inventory_self_test() -> int:
    script_path = Path(__file__).resolve().with_name(README_TOOLING_INVENTORY_SCRIPT)
    result = subprocess.run(
        ["python3", str(script_path), "--self-test"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        result.stdout if not result.stderr else result.stdout + "\n" + result.stderr
    )
    stdout_lines = result.stdout.splitlines()
    assert "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass" in stdout_lines
    assert "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=23" in stdout_lines
    return 0


def _run_tooling_packet_self_test() -> int:
    script_path = Path(__file__).resolve().with_name(TOOLING_PACKET_SCRIPT)
    result = subprocess.run(
        ["python3", str(script_path), "--self-test"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        result.stdout if not result.stderr else result.stdout + "\n" + result.stderr
    )
    stdout_lines = result.stdout.splitlines()
    assert "PHASE3_TOOLING_PACKET_SELF_TEST=pass" in stdout_lines
    assert "PHASE3_TOOLING_PACKET_SELF_TEST_CASE_COUNT=7" in stdout_lines
    return 0


def _run_validation_flow_self_test() -> int:
    script_path = Path(__file__).resolve().with_name(VALIDATION_FLOW_SCRIPT)
    result = subprocess.run(
        ["python3", str(script_path), "--self-test"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        result.stdout if not result.stderr else result.stdout + "\n" + result.stderr
    )
    stdout_lines = result.stdout.splitlines()
    assert "PHASE3_VALIDATION_FLOW_SELF_TEST=pass" in stdout_lines
    assert "PHASE3_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=67" in stdout_lines
    return 0


def _run_rbtree_shared_lift_self_test() -> int:
    script_path = Path(__file__).resolve().with_name(Path(RBTREE_SHARED_CHECKER_REL).name)
    result = subprocess.run(
        ["python3", str(script_path), "--self-test"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        result.stdout if not result.stderr else result.stdout + "\n" + result.stderr
    )
    stdout_lines = result.stdout.splitlines()
    assert "PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST=pass" in stdout_lines
    assert "PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST_CASE_COUNT=63" in stdout_lines
    return 0


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

        _write_phase3_slice(paths, slug="alpha")
        _write_phase3_slice(paths, slug="beta")

        entries = discover_phase3_slices(paths)
        assert [entry.slug for entry in select_slices(entries, [])] == ["alpha", "beta"]
        assert [entry.slug for entry in select_slices(entries, ["beta"])] == ["beta"]
        try:
            select_slices(entries, ["missing"])
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug to fail")

        assert validate_manifest(entries[0]) == []
        abi_entry = replace(entries[0], slug="abi", build_step="phase3-dump")
        assert build_smoke_commands(abi_entry) == (
            ("phase3-dump", BUILD_FILE_REL),
            ("phase3-test", BUILD_FILE_REL),
            ("phase3-low-level-wrappers-test", ABI_LOW_LEVEL_BUILD_FILE_REL),
            ("phase3-export-uapi-test", ABI_EXPORT_UAPI_BUILD_FILE_REL),
            ("phase3-export-uapi-layout-test", ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL),
            ("phase3-policy-unsafe-test", ABI_POLICY_UNSAFE_BUILD_FILE_REL),
        )
        assert validate_slices(
            root,
            entries,
            check_artifact_diff=False,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=True,
            zig_path=None,
        ) == []
        build_log = root / "zig-build-smoke.log"
        fake_zig = root / "fake-zig.sh"
        fake_zig.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    f'printf "%s\\n" "$*" >> "{build_log}"',
                    "exit 0",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        fake_zig.chmod(0o755)
        for rel in (
            "zigux/tests/build.zig",
            "zigux/tests/phase3_export_uapi_build.zig",
            "zigux/tests/phase3_export_uapi_layout_build.zig",
            "zigux/tests/phase3_low_level_wrappers_build.zig",
            "zigux/tests/phase3_policy_unsafe_build.zig",
        ):
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("// build smoke fixture\n", encoding="utf-8", newline="\n")
        abi_build_entry = Phase3Slice(
            root=root,
            slug="abi",
            description="ABI layout",
            build_step="phase3-dump",
            doc_path=paths.docs_dir / "phase3-alpha-slice.md",
            check_script=paths.scripts_dir / "check-phase3-alpha.py",
            dump_path=paths.tests_dir / "phase3_alpha_dump.zig",
            fixture_dir=paths.fixtures_dir / "phase3_alpha",
            expected_path=paths.fixtures_dir / "phase3_alpha" / "expected.json",
            harness_path=paths.fixtures_dir / "phase3_alpha" / "phase3_alpha_c_harness.c",
            manifest_candidates=(paths.fixtures_dir / "phase3_alpha_manifest.json",),
            manifest_path=paths.fixtures_dir / "phase3_alpha_manifest.json",
            interop_gate=shared_runner_gate_for_slug("abi"),
            interop_gate_mode="shared-runner",
        )
        assert _validate_build_smoke(root, abi_build_entry, str(fake_zig)) == []
        assert build_log.read_text(encoding="utf-8").splitlines() == [
            f"build phase3-dump --build-file {root / 'zigux/tests/build.zig'}",
            f"build phase3-test --build-file {root / 'zigux/tests/build.zig'}",
            f"build phase3-low-level-wrappers-test --build-file {root / 'zigux/tests/phase3_low_level_wrappers_build.zig'}",
            f"build phase3-export-uapi-test --build-file {root / 'zigux/tests/phase3_export_uapi_build.zig'}",
            f"build phase3-export-uapi-layout-test --build-file {root / 'zigux/tests/phase3_export_uapi_layout_build.zig'}",
            f"build phase3-policy-unsafe-test --build-file {root / 'zigux/tests/phase3_policy_unsafe_build.zig'}",
        ]

        export_uapi_survey_check = root / ABI_EXPORT_UAPI_SURVEY_CHECK_REL
        assert validate_export_uapi_boundary(root) == [
            f"export-uapi-gate: missing {ABI_EXPORT_UAPI_SURVEY_CHECK_REL}"
        ]
        export_uapi_survey_check.parent.mkdir(parents=True, exist_ok=True)
        export_uapi_survey_check.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import sys",
                    'print("PHASE3_EXPORT_UAPI_SURVEY=fail")',
                    'print("missing_export_uapi_layout_gate")',
                    'print("packet-local drift")',
                    'print("survey gate stderr", file=sys.stderr)',
                    "raise SystemExit(1)",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_export_uapi_boundary(root) == [
            "export-uapi-gate: missing_export_uapi_layout_gate",
            "export-uapi-gate: packet-local drift",
            "export-uapi-gate: stderr: survey gate stderr",
        ]
        export_uapi_survey_check.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    'print("PHASE3_EXPORT_UAPI_SURVEY=pass")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_export_uapi_boundary(root) == []

        _write_phase3_abi_fixture(paths)
        abi_entries = discover_phase3_slices(paths)
        abi_manifest_entry = next(entry for entry in abi_entries if entry.slug == "abi")
        abi_manifest_path = paths.fixtures_dir / "phase3_abi_manifest.json"
        roadmap_gap_doc = "Documentation/zigux/phase3-roadmap-gap-survey.md"
        roadmap_gap_validator = "scripts/zigux/validate-phase3-roadmap-gap-survey.py"
        export_uapi_layout_test = "zigux/tests/phase3_export_uapi_layout.zig"

        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == []

        abi_manifest = json.loads(abi_manifest_path.read_text(encoding="utf-8"))
        abi_manifest["files"].remove(RBTREE_SHARED_CONTRACT_TEST_REL)
        abi_manifest["file_count"] = len(abi_manifest["files"])
        abi_manifest_path.write_text(json.dumps(abi_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == [
            f"abi: manifest missing {RBTREE_SHARED_CONTRACT_TEST_REL}"
        ]

        _write_phase3_abi_fixture(paths)
        (root / RBTREE_SHARED_CHECKER_REL).unlink()
        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == [
            f"abi: manifest references missing file {RBTREE_SHARED_CHECKER_REL}"
        ]
        _write_phase3_abi_fixture(paths)

        abi_manifest = json.loads(abi_manifest_path.read_text(encoding="utf-8"))
        abi_manifest["files"].remove(roadmap_gap_doc)
        abi_manifest["file_count"] = len(abi_manifest["files"])
        abi_manifest_path.write_text(json.dumps(abi_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == [
            f"abi: manifest missing {roadmap_gap_doc}"
        ]

        _write_phase3_abi_fixture(paths)
        (root / roadmap_gap_validator).unlink()
        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == [
            f"abi: manifest references missing file {roadmap_gap_validator}"
        ]
        _write_phase3_abi_fixture(paths)

        abi_manifest = json.loads(abi_manifest_path.read_text(encoding="utf-8"))
        abi_manifest["files"].remove(export_uapi_layout_test)
        abi_manifest["file_count"] = len(abi_manifest["files"])
        abi_manifest_path.write_text(json.dumps(abi_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == [
            f"abi: manifest missing {export_uapi_layout_test}"
        ]

        _write_phase3_abi_fixture(paths)
        (root / ABI_POLICY_UNSAFE_MMIO_CONSUMER_REL).unlink()
        assert validate_manifest(abi_manifest_entry, ABI_REQUIRED_MANIFEST_FILES) == [
            f"abi: manifest references missing file {ABI_POLICY_UNSAFE_MMIO_CONSUMER_REL}"
        ]
        _write_phase3_abi_fixture(paths)

        artifact_diff_path = paths.docs_dir / "artifact-diff.md"
        artifact_diff_path.write_text(
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 3 use",
                    "- stale line",
                    "",
                    "Rules",
                    "- keep fixtures reviewable",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_slices(
            root,
            select_slices(entries, ["alpha"]),
            check_artifact_diff=False,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=True,
            zig_path=None,
        ) == []
        assert validate_slices(
            root,
            select_slices(entries, ["alpha"]),
            check_artifact_diff=True,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=True,
            zig_path=None,
        ) == ["doc-sync: artifact-diff-phase3-stale\tDocumentation/zigux/artifact-diff.md"]

        source_marker_fixture = root / "marker-fixture.zig"
        source_marker_fixture.write_text(
            "pub fn boundaryMarker() void {}\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {
                "marker-fixture.zig": (
                    "pub fn boundaryMarker() void {}",
                    "pub fn policyByteMarker() void {}",
                )
            },
        ) == ["source-marker: marker-fixture.zig missing pub fn policyByteMarker() void {}"]

        assert _run_export_uapi_build_marker_self_test() == 0
        assert _run_readme_tooling_inventory_self_test() == 0
        assert _run_tooling_packet_self_test() == 0
        assert _run_validation_flow_self_test() == 0
        assert _run_rbtree_shared_lift_self_test() == 0

        rbtree_shared_marker_fixture = root / "phase3-rbtree-shared-marker-fixture.zig"

        def assert_missing_rbtree_shared_marker(missing_marker: str) -> None:
            rbtree_shared_marker_fixture.write_text(
                "\n".join(
                    marker
                    for marker in RBTREE_SHARED_MISSING_MARKER_CASES
                    if marker != missing_marker
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            assert validate_source_markers(
                root,
                {"phase3-rbtree-shared-marker-fixture.zig": RBTREE_SHARED_MISSING_MARKER_CASES},
            ) == [
                f"source-marker: phase3-rbtree-shared-marker-fixture.zig missing {missing_marker}"
            ]

        rbtree_shared_marker_fixture.write_text(
            "\n".join(RBTREE_SHARED_MISSING_MARKER_CASES) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {"phase3-rbtree-shared-marker-fixture.zig": RBTREE_SHARED_MISSING_MARKER_CASES},
        ) == []
        for missing_marker in RBTREE_SHARED_MISSING_MARKER_CASES:
            assert_missing_rbtree_shared_marker(missing_marker)

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    print("PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT=28")
    return 0


def main() -> int:
    return run_self_test()


if __name__ == "__main__":
    raise SystemExit(main())
