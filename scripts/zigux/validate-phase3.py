#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile

from phase3_catalog import (
    Phase3Paths,
    audit_phase3_slug_sanity,
    artifact_diff_phase3_lines,
    discover_phase3_slug_rename_candidates,
    discover_phase3_slices,
)
from phase3_check_lib import (
    build_step_for_slug as runner_build_step_for_slug,
    description_for_slug as runner_description_for_slug,
    legacy_wrapper_gate_for_slug,
    render_wrapper_stub,
    shared_runner_gate_for_slug,
)


ROOT = Path(__file__).resolve().parents[2]
BUILD_FILE_REL = "zigux/tests/build.zig"
ABI_LOW_LEVEL_BUILD_FILE_REL = "zigux/tests/phase3_low_level_wrappers_build.zig"
ABI_EXPORT_UAPI_BUILD_FILE_REL = "zigux/tests/phase3_export_uapi_build.zig"
ABI_POLICY_UNSAFE_BUILD_FILE_REL = "zigux/tests/phase3_policy_unsafe_build.zig"
ABI_REQUIRED_MANIFEST_FILES = (
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    ABI_LOW_LEVEL_BUILD_FILE_REL,
    "zigux/tests/phase3_low_level_wrappers.zig",
    ABI_POLICY_UNSAFE_BUILD_FILE_REL,
    "zigux/tests/phase3_policy_unsafe.zig",
    "zigux/tests/phase3_abi.zig",
    ABI_EXPORT_UAPI_BUILD_FILE_REL,
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
)
ABI_REQUIRED_DOC_MARKERS = (
    "PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-fetch-add",
    "PHASE3_BARRIER_SCOPE=acquire-release-full",
    "PHASE3_MMIO_SCOPE=range-read16-read32-write16-write32-plus-scoped-read16-write16-read32-write32",
)
ABI_REQUIRED_SOURCE_MARKERS = {
    "zigux/helpers/layout_assert.zig": (
        'test "phase3 layout assertions cover canonical bindings"',
        'assertOffset(abi.InteropPolicy, "unsafe_scope", 2);',
    ),
    "zigux/helpers/panic_policy.zig": (
        "pub fn actionFor(mode: abi.PanicMode) Action {",
        'test "phase3 panic policy stays explicit"',
    ),
    "zigux/helpers/allocator_policy.zig": (
        "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {",
        'test "phase3 allocator policy stays explicit"',
    ),
    "zigux/unsafe/narrow.zig": (
        "pub const UnsafeScopeTag = enum(u8) {",
        "raw_pointer_bridge = 2,",
        'test "phase3 narrow unsafe scope stays explicit"',
    ),
}
LIST_HLIST_REQUIRED_DOC_MARKERS = (
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug list-hlist",
    "PHASE3_LIST_HLIST_BOUNDARY=descriptor-only-no-container-of-no-lockless-no-rcu-no-notifier-chains",
)


def _required_manifest_files_for_slug(slug: str) -> tuple[str, ...]:
    return ABI_REQUIRED_MANIFEST_FILES if slug == "abi" else ()


def _required_doc_markers_for_slug(slug: str) -> tuple[str, ...]:
    if slug == "abi":
        return ABI_REQUIRED_DOC_MARKERS
    if slug == "list-hlist":
        return LIST_HLIST_REQUIRED_DOC_MARKERS
    return ()


def _required_source_markers_for_slug(slug: str) -> dict[str, tuple[str, ...]]:
    return ABI_REQUIRED_SOURCE_MARKERS if slug == "abi" else {}


def _has_build_step(build_file: Path, step_name: str) -> bool:
    return re.search(r'b\.step\(\s*"' + re.escape(step_name) + r'"', build_file.read_text(encoding="utf-8")) is not None


def _format_slug_audit_issue(issue) -> str:
    return "slug_audit:" + issue.to_row().replace("\t", ":")


def _format_slug_rename_candidate(candidate) -> str:
    return "slug_rename_candidate:" + candidate.to_row().replace("\t", ":")


def select_slices(entries: list[object], selected_slugs: list[str]) -> list[object]:
    if not selected_slugs:
        return list(entries)
    selected = set(selected_slugs)
    filtered = [entry for entry in entries if entry.slug in selected]
    missing = sorted(selected.difference({entry.slug for entry in filtered}))
    if missing:
        raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")
    return filtered


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

    files = data.get("files")
    if data.get("phase") != "Phase 3":
        issues.append(f"{slug}:manifest_phase={data.get('phase')}")
    if not isinstance(data.get("status"), str) or not data["status"]:
        issues.append(f"{slug}:manifest_status={data.get('status')}")
    if not isinstance(data.get("slice"), str) or not data["slice"]:
        issues.append(f"{slug}:manifest_slice={data.get('slice')}")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        issues.append(f"{slug}:manifest_files={type(files).__name__}")
        return data
    if data.get("file_count") != len(files):
        issues.append(f"{slug}:manifest_file_count={data.get('file_count')}")
    for rel in _required_manifest_files_for_slug(slug):
        if rel not in files:
            issues.append(f"{slug}:manifest_missing_required_file={rel}")
    for rel in files:
        if rel.startswith("scripts/zigux/check-phase3-") and rel.endswith(".py"):
            issues.append(f"{slug}:manifest_legacy_wrapper_file={rel}")
        if not (root / rel).exists():
            issues.append(f"{slug}:manifest_missing_file={rel}")
    return data


def validate_doc_markers(root: Path, doc_path: Path, slug: str, manifest: dict[str, object] | None, issues: list[str]) -> None:
    if not doc_path.exists():
        issues.append(f"{slug}:missing_doc:{doc_path.relative_to(root).as_posix()}")
        return
    doc = doc_path.read_text(encoding="utf-8")
    required = [
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
        "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    ]
    if manifest is not None:
        required[:0] = [f"PHASE3_STATUS={manifest.get('status')}", f"PHASE3_SLICE={manifest.get('slice')}"]
    required.extend(_required_doc_markers_for_slug(slug))
    for marker in required:
        if marker not in doc:
            issues.append(f"{slug}:missing_doc_marker={marker}")
    interop_markers = [shared_runner_gate_for_slug(slug), legacy_wrapper_gate_for_slug(slug)]
    if not any(marker in doc for marker in interop_markers):
        issues.append(f"{slug}:missing_doc_marker_one_of={'|'.join(interop_markers)}")


def validate_wrapper_template(root: Path, script_path: Path, slug: str, issues: list[str]) -> None:
    if not script_path.exists():
        return
    if script_path.read_text(encoding="utf-8") != render_wrapper_stub():
        issues.append(f"{slug}:wrapper_template_mismatch:{script_path.relative_to(root).as_posix()}" )


def validate_source_markers(root: Path, slug: str, issues: list[str]) -> None:
    for rel, markers in _required_source_markers_for_slug(slug).items():
        path = root / rel
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            issues.append(f"{slug}:missing_source_file={rel}")
            continue
        for marker in markers:
            if marker not in content:
                issues.append(f"{slug}:missing_source_marker={rel}:{marker}")


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


def validate_abi_focused_build(root: Path, issues: list[str]) -> None:
    build_file = root / ABI_LOW_LEVEL_BUILD_FILE_REL
    if not build_file.exists():
        issues.append(f"abi:missing_file:{ABI_LOW_LEVEL_BUILD_FILE_REL}")
        return
    if not _has_build_step(build_file, "phase3-low-level-wrappers-test"):
        issues.append(f"abi:missing_build_step:{ABI_LOW_LEVEL_BUILD_FILE_REL}:phase3-low-level-wrappers-test")


def validate_export_uapi_focused_build(root: Path, issues: list[str]) -> None:
    build_file = root / ABI_EXPORT_UAPI_BUILD_FILE_REL
    if not build_file.exists():
        issues.append(f"abi:missing_file:{ABI_EXPORT_UAPI_BUILD_FILE_REL}")
        return
    if not _has_build_step(build_file, "phase3-export-uapi-test"):
        issues.append(f"abi:missing_build_step:{ABI_EXPORT_UAPI_BUILD_FILE_REL}:phase3-export-uapi-test")


def validate_policy_unsafe_focused_build(root: Path, issues: list[str]) -> None:
    build_file = root / ABI_POLICY_UNSAFE_BUILD_FILE_REL
    if not build_file.exists():
        issues.append(f"abi:missing_file:{ABI_POLICY_UNSAFE_BUILD_FILE_REL}")
        return
    if not _has_build_step(build_file, "phase3-policy-unsafe-test"):
        issues.append(f"abi:missing_build_step:{ABI_POLICY_UNSAFE_BUILD_FILE_REL}:phase3-policy-unsafe-test")


def validate_runner_metadata(slices: list[object], issues: list[str]) -> None:
    for entry in slices:
        if runner_build_step_for_slug(entry.slug) != entry.build_step:
            issues.append(f"{entry.slug}:runner_build_step_mismatch")
        if runner_description_for_slug(entry.slug) != entry.description:
            issues.append(f"{entry.slug}:runner_description_mismatch")


def validate_obsolete_wrappers(root: Path, slices: list[object], issues: list[str], *, check_all_wrappers: bool) -> None:
    if not check_all_wrappers:
        return
    expected = {entry.check_script.resolve() for entry in slices}
    for path in sorted((root / "scripts" / "zigux").glob("check-phase3-*.py")):
        if path.resolve() not in expected:
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
    if current != artifact_diff_phase3_lines(slices, artifact_diff_path):
        issues.append("artifact_diff:stale_phase3_section:Documentation/zigux/artifact-diff.md")


def validate_slices(
    root: Path,
    slices: list[object],
    *,
    check_artifact_diff: bool = False,
    check_slug_sanity: bool = False,
    check_all_wrappers: bool = True,
) -> list[str]:
    issues: list[str] = []
    for entry in slices:
        for label, path in {
            "dump": entry.dump_path,
            "fixture_dir": entry.fixture_dir,
            "expected": entry.expected_path,
            "harness": entry.harness_path,
        }.items():
            if not path.exists():
                issues.append(f"{entry.slug}:missing_{label}:{path.relative_to(root).as_posix()}")
        manifest = validate_manifest(root, entry.manifest_path, entry.slug, issues)
        validate_doc_markers(root, entry.doc_path, entry.slug, manifest, issues)
        validate_wrapper_template(root, entry.check_script, entry.slug, issues)
        validate_source_markers(root, entry.slug, issues)
    validate_buildSteps = validate_build_steps
    validate_buildSteps(root, slices, issues)
    validate_abi_focused_build(root, issues)
    validate_export_uapi_focused_build(root, issues)
    validate_policy_unsafe_focused_build(root, issues)
    validate_runner_metadata(slices, issues)
    validate_obsolete_wrappers(root, slices, issues, check_all_wrappers=check_all_wrappers)
    if check_artifact_diff:
        validate_artifact_diff_phase3_section(root, slices, issues)
    if check_slug_sanity:
        slug_issues = audit_phase3_slug_sanity(slices)
        issues.extend(_format_slug_audit_issue(issue) for issue in slug_issues)
        if slug_issues:
            issues.extend(_format_slug_rename_candidate(candidate) for candidate in discover_phase3_slug_rename_candidates(slices))
    return issues


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
        fixture_dir = paths.fixtures_dir / "phase3_alpha"
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, fixture_dir):
            path.mkdir(parents=True, exist_ok=True)

        for rel in ABI_REQUIRED_MANIFEST_FILES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("// abi boundary\n", encoding="utf-8", newline="\n")

        (root / "zigux" / "helpers" / "layout_assert.zig").write_text(
            'test "phase3 layout assertions cover canonical bindings" {\n'
            '    comptime {\n'
            '        assertOffset(abi.InteropPolicy, "unsafe_scope", 2);\n'
            "    }\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "panic_policy.zig").write_text(
            "pub fn actionFor(mode: abi.PanicMode) Action {\n"
            "    _ = mode;\n"
            "    return .abort_now;\n"
            "}\n\n"
            'test "phase3 panic policy stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "allocator_policy.zig").write_text(
            "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {\n"
            "    _ = mode;\n"
            "    return .caller_prepared;\n"
            "}\n\n"
            'test "phase3 allocator policy stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "unsafe" / "narrow.zig").write_text(
            "pub const UnsafeScopeTag = enum(u8) {\n"
            "    none = 0,\n"
            "    volatile_mmio = 1,\n"
            "    raw_pointer_bridge = 2,\n"
            "};\n\n"
            'test "phase3 narrow unsafe scope stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )

        (paths.tests_dir / "build.zig").write_text(
            'const phase3_test_step = b.step("phase3-test", "Run Phase 3 tests");\n'
            'const phase3_alpha_dump_step = b.step("phase3-alpha-dump", "Run Phase 3 alpha dump");\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_export_uapi_build.zig").write_text(
            'const phase3_export_uapi_step = b.step("phase3-export-uapi-test", "Run Phase 3 export shim and uapi smoke tests");\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_policy_unsafe_build.zig").write_text(
            'const phase3_policy_unsafe_step = b.step("phase3-policy-unsafe-test", "Run focused Phase 3 policy and unsafe substrate tests");\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_low_level_wrappers_build.zig").write_text(
            'const phase3_low_level_step = b.step("phase3-low-level-wrappers-test", "Run focused Phase 3 low-level wrapper tests");\n',
            encoding="utf-8",
            newline="\n",
        )

        abi_manifest_path = root / "tmp" / "abi_manifest.json"
        abi_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        partial_abi_manifest_files = list(ABI_REQUIRED_MANIFEST_FILES[:-8])
        abi_manifest_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-slice",
                    "files": partial_abi_manifest_files,
                    "file_count": len(partial_abi_manifest_files),
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        abi_issues: list[str] = []
        validate_manifest(root, abi_manifest_path, "abi", abi_issues)
        assert abi_issues == [
            "abi:manifest_missing_required_file=zigux/tests/phase3_policy_unsafe_build.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_policy_unsafe.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_abi.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_export_uapi_build.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_export_uapi.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_abi_dump.zig",
            "abi:manifest_missing_required_file=zigux/tests/fixtures/phase3_abi/expected.json",
            "abi:manifest_missing_required_file=zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
        ]

        abi_manifest_path.write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "abi-slice", "files": list(ABI_REQUIRED_MANIFEST_FILES), "file_count": len(ABI_REQUIRED_MANIFEST_FILES)}),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_manifest(root, abi_manifest_path, "abi", []) is not None

        abi_doc_path = root / "tmp" / "phase3-abi-slice.md"
        abi_doc_path.write_text(
            "\n".join([
                "PHASE3_STATUS=ready",
                "PHASE3_SLICE=abi-slice",
                *ABI_REQUIRED_DOC_MARKERS,
                "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
                "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                "",
            ]),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_slices(root, []) == []

        (root / "zigux" / "helpers" / "panic_policy.zig").write_text(
            "pub fn actionFor(mode: abi.PanicMode) Action {\n"
            "    _ = mode;\n"
            "    return .abort_now;\n"
            "}\n\n"
            'test "phase3 panic modes drifted" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        drift_issues: list[str] = []
        validate_source_markers(root, "abi", drift_issues)
        assert drift_issues == [
            'abi:missing_source_marker=zigux/helpers/panic_policy.zig:test "phase3 panic policy stays explicit"',
        ]
        (root / "zigux" / "helpers" / "panic_policy.zig").write_text(
            "pub fn actionFor(mode: abi.PanicMode) Action {\n"
            "    _ = mode;\n"
            "    return .abort_now;\n"
            "}\n\n"
            'test "phase3 panic policy stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )

        manifest_rel = "zigux/tests/fixtures/phase3_alpha/expected.json"
        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join([
                "PHASE3_STATUS=ready",
                "PHASE3_SLICE=alpha-slice",
                "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha",
                "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                "",
            ]),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-alpha.py").write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        (paths.tests_dir / "phase3_alpha_dump.zig").write_text("// alpha\n", encoding="utf-8", newline="\n")
        (fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_c_harness.c").write_text("int main(void) { return 0; }\n", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "alpha-slice", "files": [manifest_rel], "file_count": 1}),
            encoding="utf-8",
            newline="\n",
        )

        discovered = discover_phase3_slices(paths)
        alpha = [entry for entry in discovered if entry.slug == "alpha"]
        assert len(alpha) == 1
        assert validate_slices(root, alpha) == []

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 3 slice catalog and metadata.")
    parser.add_argument("--slug", action="append", default=[], help="Only validate the named Phase 3 slug. Repeat to validate more than one.")
    parser.add_argument("--check-artifact-diff", action="store_true", help="Also validate the generated Current Phase 3 use section.")
    parser.add_argument("--check-slug-sanity", action="store_true", help="Also audit discovered Phase 3 slugs for naming drift.")
    parser.add_argument("--skip-obsolete-wrapper-check", action="store_true", help="Skip the stale wrapper-file scan.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    slices = select_slices(discover_phase3_slices(), args.slug)
    if not slices:
        raise SystemExit("no Phase 3 slugs discovered")

    issues = validate_slices(
        ROOT,
        slices,
        check_artifact_diff=args.check_artifact_diff,
        check_slug_sanity=args.check_slug_sanity,
        check_all_wrappers=not args.skip_obsolete_wrapper_check,
    )
    if issues:
        print("PHASE3_VALIDATION=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_VALIDATION=pass")
    print("PHASE3_VALIDATED_SLUGS=" + ",".join(entry.slug for entry in slices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
