#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from phase3_catalog import (
    Phase3Paths,
    audit_phase3_slug_sanity,
    artifact_diff_phase3_lines,
    discover_phase3_slug_rename_candidates,
    discover_phase3_slices,
)
from phase3_check_lib import legacy_wrapper_gate_for_slug, render_wrapper_stub, shared_runner_gate_for_slug


ROOT = Path(__file__).resolve().parents[2]
BUILD_FILE_REL = "zigux/tests/build.zig"
ABI_DUMP_GATE = "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig"
ABI_REQUIRED_EXPECTED_CONSTANTS = {
    "facility_kernel": 1,
    "status_flag_error": 1,
    "panic_abort": 0,
    "allocator_caller_provided": 0,
    "unsafe_scope_raw_pointer_bridge": 2,
}
ABI_REQUIRED_MANIFEST_FILES = (
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/README.md",
    ".github/workflows/zigux-bootstrap.yml",
)
PHASE3_CHECK_SUPPORT_SCRIPTS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
)
LOW_LEVEL_WRAPPER_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"
LOW_LEVEL_WRAPPER_REQUIRED_MARKERS = (
    "atomic.load(u32, &value, .seq_cst)",
    "atomic.store(u32, &value, 8, .seq_cst)",
    "atomic.exchange(u32, &value, 13, .seq_cst)",
    "atomic.fetchAdd(u32, &value, 4, .seq_cst)",
    "atomic.fetchSub(u32, &value, 3, .seq_cst)",
    "atomic.fetchAnd(u32, &value, 12, .seq_cst)",
    "atomic.fetchOr(u32, &value, 3, .seq_cst)",
    "atomic.fetchXor(u32, &value, 6, .seq_cst)",
    "atomic.fetchNand(u32, &value, 10, .seq_cst)",
    "atomic.fetchMin(u32, &value, 4, .seq_cst)",
    "atomic.fetchMax(u32, &value, 19, .seq_cst)",
    "atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst)",
    "atomic.compareExchangeWeak(u32, &weak_value, 21, 34, .seq_cst, .seq_cst)",
    "barrier.acquire();",
    "barrier.release();",
    "barrier.full();",
    "barrier.acquireRelease();",
    "const byte_desc = mmio.range(base, 24, 1);",
    "const halfword_desc = mmio.range(base, 24, 2);",
    "const word_desc = mmio.range(base, 24, 4);",
    "const dword_desc = mmio.range(base, 24, 8);",
    "mmio.write8(base, 1, 0x5a);",
    "mmio.read8(base, 1)",
    "mmio.write16(base, 2, 0xbeef);",
    "mmio.read16(base, 2)",
    "mmio.write32(base, @sizeOf(u32), 0xfeedbeef);",
    "mmio.read32(base, @sizeOf(u32))",
    "mmio.write64(base, @sizeOf(u64), 0x0123_4567_89ab_cdef);",
    "mmio.read64(base, @sizeOf(u64))",
    "mmio.write16(base, 1, 0x1234);",
    "mmio.read16(base, 1)",
    "mmio.write32(base, 3, 0x89abcdef);",
    "mmio.read32(base, 3)",
    "mmio.write64(base, 5, 0xfedc_ba98_7654_3210);",
    "mmio.read64(base, 5)",
    "atomic.store(u32, &handoff_value, 41, .release)",
    "atomic.load(u32, &handoff_value, .acquire)",
    "atomic.fetchMin(i32, &signed_value, -3, .seq_cst)",
    "atomic.fetchMax(i32, &signed_value, 6, .seq_cst)",
    "atomic.fetchAdd(i32, &signed_arithmetic_value, 5, .seq_cst)",
    "atomic.fetchSub(i32, &signed_arithmetic_value, 7, .seq_cst)",
    "atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic)",
    "atomic.compareExchange(u32, &monotonic_value, 5, 7, .monotonic, .monotonic)",
    "const monotonic_mismatch = atomic.compareExchange(",
    "try std.testing.expectEqual(@as(?u32, 7), monotonic_mismatch);",
    "atomic.compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire)",
    "const acq_rel_mismatch = atomic.compareExchange(",
    "try std.testing.expectEqual(@as(?u32, 11), acq_rel_mismatch);",
    "atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic)",
    "const weak_release_mismatch = atomic.compareExchangeWeak(",
    "try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);",
)
ABI_WRAPPER_STUB = "\n".join(
    [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "",
        "import subprocess",
        "import sys",
        "from pathlib import Path",
        "",
        "from phase3_check_lib import run_from_wrapper",
        "",
        "",
        "ROOT = Path(__file__).resolve().parents[2]",
        'SYNTAX_CHECKER = ROOT / "scripts" / "zigux" / "validate-phase3-abi-bindings-syntax.py"',
        "",
        "",
        'if __name__ == "__main__":',
        "    syntax_result = subprocess.run([sys.executable, str(SYNTAX_CHECKER)], check=False)",
        "    if syntax_result.returncode != 0:",
        "        raise SystemExit(syntax_result.returncode)",
        "    raise SystemExit(run_from_wrapper(__file__))",
        "",
    ]
)


def _is_generated_legacy_wrapper_manifest_file(rel: str) -> bool:
    return rel.startswith("scripts/zigux/check-phase3-") and rel.endswith(".py") and rel not in PHASE3_CHECK_SUPPORT_SCRIPTS


def _allowed_generated_legacy_wrapper_manifest_files_for_slug(slug: str) -> tuple[str, ...]:
    if slug == "abi":
        return (f"scripts/zigux/check-phase3-{slug}.py",)
    return ()


def _required_manifest_files_for_slug(slug: str) -> tuple[str, ...]:
    if slug == "abi":
        return ABI_REQUIRED_MANIFEST_FILES
    return ()


def _required_expected_constants_for_slug(slug: str) -> dict[str, int]:
    if slug == "abi":
        return ABI_REQUIRED_EXPECTED_CONSTANTS
    return {}


def _expected_wrapper_template_for_slug(slug: str) -> str:
    if slug == "abi":
        return ABI_WRAPPER_STUB
    return render_wrapper_stub()


def select_slices(entries: list[object], selected_slugs: list[str]) -> list[object]:
    slices = list(entries)
    selected = set(selected_slugs)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")
    return slices


def _phase3_paths_for_root(root: Path) -> Phase3Paths:
    return Phase3Paths(
        root=root,
        docs_dir=root / "Documentation" / "zigux",
        scripts_dir=root / "scripts" / "zigux",
        tests_dir=root / "zigux" / "tests",
        fixtures_dir=root / "zigux" / "tests" / "fixtures",
    )


def validate_manifest(root: Path, path: Path | None, slug: str, issues: list[str]) -> dict[str, object] | None:
    if path is None:
        issues.append(f"{slug}:missing_manifest")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"{slug}:missing_manifest:{path.relative_to(root).as_posix()}")
        return None
    except json.JSONDecodeError as exc:
        issues.append(f"{slug}:invalid_manifest:{path.relative_to(root).as_posix()}:{exc.msg}")
        return None

    if data.get("phase") != "Phase 3":
        issues.append(f"{slug}:manifest_phase={data.get('phase')}")
    if not isinstance(data.get("status"), str) or not data["status"]:
        issues.append(f"{slug}:manifest_status={data.get('status')}")
    if not isinstance(data.get("slice"), str) or not data["slice"]:
        issues.append(f"{slug}:manifest_slice={data.get('slice')}")
    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        issues.append(f"{slug}:manifest_files={type(files).__name__}")
        return data
    duplicate_files = sorted(rel for rel, count in Counter(files).items() if count > 1)
    for rel in duplicate_files:
        issues.append(f"{slug}:manifest_duplicate_file={rel}")
    file_count = data.get("file_count")
    if file_count != len(files):
        issues.append(f"{slug}:manifest_file_count={file_count}")
    required_files = _required_manifest_files_for_slug(slug)
    if required_files and file_count != len(required_files):
        issues.append(f"{slug}:manifest_required_file_count={file_count}!={len(required_files)}")
    for rel in required_files:
        if rel not in files:
            issues.append(f"{slug}:manifest_missing_required_file={rel}")
    allowed_legacy_wrappers = set(_allowed_generated_legacy_wrapper_manifest_files_for_slug(slug))
    required_file_set = set(required_files)
    for rel in files:
        if _is_generated_legacy_wrapper_manifest_file(rel) and rel not in allowed_legacy_wrappers:
            issues.append(f"{slug}:manifest_legacy_wrapper_file={rel}")
        if required_file_set and rel not in required_file_set:
            issues.append(f"{slug}:manifest_unexpected_file={rel}")
        if not (root / rel).exists():
            issues.append(f"{slug}:manifest_missing_file={rel}")
    return data


def validate_doc_markers(root: Path, doc_path: Path, slug: str, manifest: dict[str, object] | None, issues: list[str]) -> None:
    if not doc_path.exists():
        issues.append(f"{slug}:missing_doc:{doc_path.relative_to(root).as_posix()}")
        return
    doc = doc_path.read_text(encoding="utf-8")
    normalized_lines = Counter(_normalize_doc_marker_line(line) for line in doc.splitlines())
    required_markers = [
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
        "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    ]
    if slug == "abi":
        required_markers.append(ABI_DUMP_GATE)
    if manifest:
        required_markers.insert(0, f"PHASE3_STATUS={manifest.get('status')}")
        required_markers.insert(1, f"PHASE3_SLICE={manifest.get('slice')}")
    for marker in required_markers:
        marker_count = normalized_lines.get(marker, 0)
        if marker_count == 0:
            issues.append(f"{slug}:missing_doc_marker={marker}")
        elif marker_count != 1:
            issues.append(f"{slug}:duplicate_doc_marker={marker}")

    interop_markers = [shared_runner_gate_for_slug(slug), legacy_wrapper_gate_for_slug(slug)]
    interop_count = sum(normalized_lines.get(marker, 0) for marker in interop_markers)
    if interop_count == 0:
        issues.append(f"{slug}:missing_doc_marker_one_of={'|'.join(interop_markers)}")
    elif interop_count != 1:
        issues.append(f"{slug}:duplicate_doc_marker_one_of={'|'.join(interop_markers)}")


def _normalize_doc_marker_line(line: str) -> str:
    normalized = line.strip()
    if normalized.startswith("- "):
        normalized = normalized[2:].lstrip()
    if normalized.startswith("* "):
        normalized = normalized[2:].lstrip()
    if normalized.startswith("`") and normalized.endswith("`") and len(normalized) >= 2:
        normalized = normalized[1:-1]
    return normalized


def validate_wrapper_template(root: Path, script_path: Path, slug: str, issues: list[str]) -> None:
    if not script_path.exists():
        return
    expected = _expected_wrapper_template_for_slug(slug)
    current = script_path.read_text(encoding="utf-8")
    if current != expected:
        issues.append(f"{slug}:wrapper_template_mismatch:{script_path.relative_to(root).as_posix()}")


def validate_expected_fixture(path: Path, slug: str, issues: list[str]) -> None:
    required_constants = _required_expected_constants_for_slug(slug)
    if not required_constants:
        return

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"{slug}:missing_expected:{path.as_posix()}")
        return
    except json.JSONDecodeError as exc:
        issues.append(f"{slug}:invalid_expected:{path.as_posix()}:{exc.msg}")
        return

    constants = payload.get("constants")
    if not isinstance(constants, dict):
        issues.append(f"{slug}:expected_constants={type(constants).__name__}")
        return

    for key, value in required_constants.items():
        if constants.get(key) != value:
            issues.append(f"{slug}:expected_constant={key}:{constants.get(key)}!={value}")


def validate_low_level_wrapper_markers(root: Path, slug: str, issues: list[str]) -> None:
    if slug != "abi":
        return
    wrapper_test_path = root / LOW_LEVEL_WRAPPER_TEST_REL
    if not wrapper_test_path.exists():
        issues.append(f"{slug}:missing_low_level_wrapper_test:{LOW_LEVEL_WRAPPER_TEST_REL}")
        return
    source = wrapper_test_path.read_text(encoding="utf-8")
    for marker in LOW_LEVEL_WRAPPER_REQUIRED_MARKERS:
        if marker not in source:
            issues.append(f"{slug}:missing_low_level_wrapper_marker={marker}")


def _has_build_step(build_file: Path, step_name: str) -> bool:
    marker = f'b.step("{step_name}"'
    return marker in build_file.read_text(encoding="utf-8")


def _is_generated_wrapper_script(path: Path) -> bool:
    try:
        current = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    if current in (render_wrapper_stub(), ABI_WRAPPER_STUB):
        return True
    return (
        "from phase3_check_lib import run_from_wrapper" in current
        and "run_from_wrapper(__file__)" in current
    )


def validate_build_steps(root: Path, slices: list[object], issues: list[str]) -> None:
    build_file = root / BUILD_FILE_REL
    if not build_file.exists():
        issues.append(f"build:missing_file:{BUILD_FILE_REL}")
        return

    if not _has_build_step(build_file, "phase3-test"):
        issues.append(f"build:missing_step:{BUILD_FILE_REL}:phase3-test")

    for entry in slices:
        if not _has_build_step(build_file, entry.build_step):
            issues.append(f"{entry.slug}:missing_build_step:{BUILD_FILE_REL}:{entry.build_step}")


def validate_obsolete_wrappers(
    root: Path,
    slices: list[object],
    issues: list[str],
    *,
    check_all_wrappers: bool,
    catalog_slices: list[object] | None = None,
) -> None:
    if not check_all_wrappers:
        return
    expected_entries = catalog_slices if catalog_slices is not None else slices
    expected_paths = {entry.check_script.resolve() for entry in expected_entries}
    scripts_dir = root / "scripts" / "zigux"
    for path in sorted(scripts_dir.glob("check-phase3-*.py")):
        if path.resolve() in expected_paths:
            continue
        if not _is_generated_wrapper_script(path):
            continue
        issues.append(f"obsolete_wrapper:{path.relative_to(root).as_posix()}")


def validate_artifact_diff_phase3_section(root: Path, slices: list[object], issues: list[str]) -> None:
    artifact_diff_path = root / "Documentation" / "zigux" / "artifact-diff.md"
    try:
        lines = artifact_diff_path.read_text(encoding="utf-8").splitlines()
        start = lines.index("Current Phase 3 use")
        end = lines.index("Rules")
    except FileNotFoundError:
        issues.append("artifact_diff:missing_doc:Documentation/zigux/artifact-diff.md")
        return
    except ValueError:
        issues.append("artifact_diff:missing_phase3_section:Documentation/zigux/artifact-diff.md")
        return

    current = lines[start + 1 : end]
    while current and not current[-1]:
        current.pop()
    expected = artifact_diff_phase3_lines(slices, artifact_diff_path)
    if current != expected:
        issues.append("artifact_diff:stale_phase3_section:Documentation/zigux/artifact-diff.md")


def _format_slug_audit_issue(issue) -> str:
    return "slug_audit:" + issue.to_row().replace("\t", ":")


def _format_slug_rename_candidate(candidate) -> str:
    return "slug_rename_candidate:" + candidate.to_row().replace("\t", ":")


def validate_slices(
    root: Path,
    slices: list[object],
    *,
    check_artifact_diff: bool = False,
    check_slug_sanity: bool = False,
    check_all_wrappers: bool = True,
) -> list[str]:
    issues: list[str] = []
    catalog_slices = discover_phase3_slices(_phase3_paths_for_root(root))

    for entry in slices:
        required = {
            "dump": entry.dump_path,
            "fixture_dir": entry.fixture_dir,
            "expected": entry.expected_path,
            "harness": entry.harness_path,
        }
        for label, path in required.items():
            if not path.exists():
                issues.append(f"{entry.slug}:missing_{label}:{path.relative_to(root).as_posix()}")

        manifest = validate_manifest(root, entry.manifest_path, entry.slug, issues)
        validate_doc_markers(root, entry.doc_path, entry.slug, manifest, issues)
        validate_wrapper_template(root, entry.check_script, entry.slug, issues)
        validate_expected_fixture(entry.expected_path, entry.slug, issues)
        validate_low_level_wrapper_markers(root, entry.slug, issues)

    validate_build_steps(root, slices, issues)
    validate_obsolete_wrappers(
        root,
        slices,
        issues,
        check_all_wrappers=check_all_wrappers,
        catalog_slices=catalog_slices,
    )
    if check_artifact_diff:
        validate_artifact_diff_phase3_section(root, slices, issues)
    if check_slug_sanity:
        slug_issues = audit_phase3_slug_sanity(slices)
        issues.extend(_format_slug_audit_issue(issue) for issue in slug_issues)
        if slug_issues:
            issues.extend(_format_slug_rename_candidate(candidate) for candidate in discover_phase3_slug_rename_candidates(slices))
    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        scripts_dir = root / "scripts" / "zigux"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        alpha_wrapper = scripts_dir / "check-phase3-alpha.py"
        alpha_wrapper.write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        abi_wrapper = scripts_dir / "check-phase3-abi.py"
        abi_wrapper.write_text(ABI_WRAPPER_STUB, encoding="utf-8", newline="\n")

        issues: list[str] = []
        validate_wrapper_template(root, alpha_wrapper, "alpha", issues)
        validate_wrapper_template(root, abi_wrapper, "abi", issues)
        assert issues == []
        assert _is_generated_wrapper_script(alpha_wrapper)
        assert _is_generated_wrapper_script(abi_wrapper)
        case_count += 1

        abi_wrapper.write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        abi_issues: list[str] = []
        validate_wrapper_template(root, abi_wrapper, "abi", abi_issues)
        assert abi_issues == ["abi:wrapper_template_mismatch:scripts/zigux/check-phase3-abi.py"]
        case_count += 1

        for rel in ABI_REQUIRED_MANIFEST_FILES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("// stub\n", encoding="utf-8", newline="\n")

        manifest_path = root / "zigux/tests/fixtures/phase3_abi_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "phase": "Phase 3",
            "status": "ready",
            "slice": "abi-substrate-skeleton",
            "files": list(ABI_REQUIRED_MANIFEST_FILES),
            "file_count": len(ABI_REQUIRED_MANIFEST_FILES),
        }
        manifest_path.write_text(
            json.dumps(manifest_payload),
            encoding="utf-8",
            newline="\n",
        )
        manifest_issues: list[str] = []
        manifest = validate_manifest(root, manifest_path, "abi", manifest_issues)
        assert manifest is not None
        assert manifest_issues == []
        case_count += 1

        doc_path = root / "Documentation" / "zigux" / "phase3-abi-slice.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=abi-substrate-skeleton",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    ABI_DUMP_GATE,
                    shared_runner_gate_for_slug("abi"),
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        doc_issues: list[str] = []
        validate_doc_markers(root, doc_path, "abi", manifest_payload, doc_issues)
        assert doc_issues == []
        case_count += 1

        doc_path.write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=abi-substrate-skeleton",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    shared_runner_gate_for_slug("abi"),
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        missing_dump_gate_issues: list[str] = []
        validate_doc_markers(root, doc_path, "abi", manifest_payload, missing_dump_gate_issues)
        assert missing_dump_gate_issues == [f"abi:missing_doc_marker={ABI_DUMP_GATE}"]
        case_count += 1

        abi_expected_path = root / "tmp" / "phase3_abi_expected.json"
        abi_expected_path.parent.mkdir(parents=True, exist_ok=True)
        abi_expected_path.write_text(
            json.dumps({"constants": {"panic_abort": 0}}),
            encoding="utf-8",
            newline="\n",
        )
        abi_issues = []
        validate_expected_fixture(abi_expected_path, "abi", abi_issues)
        for key, value in ABI_REQUIRED_EXPECTED_CONSTANTS.items():
            if key == "panic_abort":
                continue
            assert f"abi:expected_constant={key}:None!={value}" in abi_issues
        case_count += 1

        abi_expected_path.write_text(
            json.dumps({"constants": ABI_REQUIRED_EXPECTED_CONSTANTS}),
            encoding="utf-8",
            newline="\n",
        )
        abi_issues = []
        validate_expected_fixture(abi_expected_path, "abi", abi_issues)
        assert abi_issues == []
        case_count += 1

        missing_required = "scripts/zigux/artifact_diff.py"
        manifest_payload["files"] = [
            rel for rel in ABI_REQUIRED_MANIFEST_FILES if rel != missing_required
        ]
        manifest_payload["file_count"] = len(manifest_payload["files"])
        manifest_path.write_text(
            json.dumps(manifest_payload),
            encoding="utf-8",
            newline="\n",
        )
        missing_required_issues: list[str] = []
        validate_manifest(root, manifest_path, "abi", missing_required_issues)
        assert missing_required_issues == [
            f"abi:manifest_required_file_count={len(ABI_REQUIRED_MANIFEST_FILES) - 1}!={len(ABI_REQUIRED_MANIFEST_FILES)}",
            f"abi:manifest_missing_required_file={missing_required}",
        ]
        case_count += 1

        manifest_payload["files"] = list(ABI_REQUIRED_MANIFEST_FILES)
        manifest_payload["file_count"] = len(manifest_payload["files"])
        manifest_path.write_text(
            json.dumps(manifest_payload),
            encoding="utf-8",
            newline="\n",
        )
        missing_manifest_file = root / ABI_REQUIRED_MANIFEST_FILES[13]
        missing_manifest_file.unlink()
        missing_manifest_file_issues: list[str] = []
        validate_manifest(root, manifest_path, "abi", missing_manifest_file_issues)
        assert missing_manifest_file_issues == [
            f"abi:manifest_missing_file={ABI_REQUIRED_MANIFEST_FILES[13]}"
        ]
        case_count += 1

        extra_wrapper_path = root / "scripts" / "zigux" / "check-phase3-bitmap-cpumask.py"
        extra_wrapper_path.write_text("// stub\n", encoding="utf-8", newline="\n")
        manifest_payload["files"] = list(ABI_REQUIRED_MANIFEST_FILES) + [
            "scripts/zigux/check-phase3-bitmap-cpumask.py"
        ]
        manifest_payload["file_count"] = len(manifest_payload["files"])
        manifest_path.write_text(
            json.dumps(manifest_payload),
            encoding="utf-8",
            newline="\n",
        )
        unexpected_wrapper_issues: list[str] = []
        validate_manifest(root, manifest_path, "abi", unexpected_wrapper_issues)
        assert unexpected_wrapper_issues == [
            f"abi:manifest_required_file_count={len(ABI_REQUIRED_MANIFEST_FILES) + 1}!={len(ABI_REQUIRED_MANIFEST_FILES)}",
            "abi:manifest_legacy_wrapper_file=scripts/zigux/check-phase3-bitmap-cpumask.py",
            "abi:manifest_unexpected_file=scripts/zigux/check-phase3-bitmap-cpumask.py",
        ]
        case_count += 1

        wrapper_test_path = root / LOW_LEVEL_WRAPPER_TEST_REL
        wrapper_test_path.parent.mkdir(parents=True, exist_ok=True)
        wrapper_test_path.write_text(
            "\n".join(LOW_LEVEL_WRAPPER_REQUIRED_MARKERS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        low_level_issues: list[str] = []
        validate_low_level_wrapper_markers(root, "abi", low_level_issues)
        assert low_level_issues == []
        case_count += 1

        wrapper_test_path.write_text(
            "\n".join(
                marker
                for marker in LOW_LEVEL_WRAPPER_REQUIRED_MARKERS
                if marker != "atomic.fetchNand(u32, &value, 10, .seq_cst)"
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        missing_fetch_nand_issues: list[str] = []
        validate_low_level_wrapper_markers(root, "abi", missing_fetch_nand_issues)
        assert missing_fetch_nand_issues == [
            "abi:missing_low_level_wrapper_marker=atomic.fetchNand(u32, &value, 10, .seq_cst)"
        ]
        case_count += 1

        wrapper_test_path.write_text(
            "\n".join(
                marker
                for marker in LOW_LEVEL_WRAPPER_REQUIRED_MARKERS
                if marker != "atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic)"
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        missing_monotonic_fetch_nand_issues: list[str] = []
        validate_low_level_wrapper_markers(root, "abi", missing_monotonic_fetch_nand_issues)
        assert missing_monotonic_fetch_nand_issues == [
            "abi:missing_low_level_wrapper_marker=atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic)"
        ]
        case_count += 1

        wrapper_test_path.write_text(
            "\n".join(LOW_LEVEL_WRAPPER_REQUIRED_MARKERS[:-1]) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        missing_low_level_issues: list[str] = []
        validate_low_level_wrapper_markers(root, "abi", missing_low_level_issues)
        assert missing_low_level_issues == [
            f"abi:missing_low_level_wrapper_marker={LOW_LEVEL_WRAPPER_REQUIRED_MARKERS[-1]}"
        ]
        case_count += 1

    print("PHASE3_VALIDATE_SELF_TEST=pass")
    print(f"PHASE3_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate shipped Phase 3 slice metadata, wrapper gates, and shared replay surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated Phase 3 validator coverage.")
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Only validate the named Phase 3 slug. Repeat to validate more than one bounded slice.",
    )
    parser.add_argument(
        "--check-artifact-diff-phase3-section",
        action="store_true",
        help="Also require Documentation/zigux/artifact-diff.md to match the generated Phase 3 section from the catalog.",
    )
    parser.add_argument(
        "--check-slug-sanity",
        action="store_true",
        help="Also require discovered Phase 3 slugs to pass the optional catalog sanity audit.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    slices = select_slices(discover_phase3_slices(), args.slug)
    if not slices:
        raise SystemExit("no Phase 3 slices discovered")

    issues = validate_slices(
        ROOT,
        slices,
        check_artifact_diff=args.check_artifact_diff_phase3_section,
        check_slug_sanity=args.check_slug_sanity,
        check_all_wrappers=True,
    )
    if issues:
        print("PHASE3_VALIDATION=fail")
        print("MISSING_PHASE3_MARKERS_START")
        for issue in issues:
            print(issue)
        print("MISSING_PHASE3_MARKERS_END")
        return 1
    print("PHASE3_VALIDATION=pass")
    print(f"PHASE3_SLICE_COUNT={len(slices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
