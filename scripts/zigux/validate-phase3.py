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
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
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
    "atomic.fetchMin(u32, &value, 4, .seq_cst)",
    "atomic.fetchMax(u32, &value, 19, .seq_cst)",
    "atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst)",
    "atomic.compareExchangeWeak(u32, &weak_value, 21, 34, .seq_cst, .seq_cst)",
    "barrier.acquire();",
    "barrier.release();",
    "barrier.full();",
    "barrier.acquireRelease();",
    "const byte_desc = mmio.range(base, 8, 1);",
    "const desc = mmio.range(base, 8, 4);",
    "mmio.write8(base, 1, 0x5a);",
    "mmio.read8(base, 1)",
    "mmio.write32(base, @sizeOf(u32), 0xfeedbeef);",
    "mmio.read32(base, @sizeOf(u32))",
    "atomic.store(u32, &handoff_value, 41, .release);",
    "atomic.load(u32, &handoff_value, .acquire)",
    "atomic.compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire)",
    "atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic)",
    "const weak_release_mismatch = atomic.compareExchangeWeak(",
    "try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);",
)


def _is_legacy_wrapper_manifest_file(rel: str) -> bool:
    return rel.startswith("scripts/zigux/check-phase3-") and rel.endswith(".py")


def _required_manifest_files_for_slug(slug: str) -> tuple[str, ...]:
    if slug == "abi":
        return ABI_REQUIRED_MANIFEST_FILES
    return ()


def select_slices(entries: list[object], selected_slugs: list[str]) -> list[object]:
    slices = list(entries)
    selected = set(selected_slugs)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")
    return slices


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
    for rel in _required_manifest_files_for_slug(slug):
        if rel not in files:
            issues.append(f"{slug}:manifest_missing_required_file={rel}")
    for rel in files:
        if _is_legacy_wrapper_manifest_file(rel):
            issues.append(f"{slug}:manifest_legacy_wrapper_file={rel}")
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
    expected = render_wrapper_stub()
    current = script_path.read_text(encoding="utf-8")
    if current != expected:
        issues.append(f"{slug}:wrapper_template_mismatch:{script_path.relative_to(root).as_posix()}")


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
    expected = render_wrapper_stub()
    if current == expected:
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


def validate_obsolete_wrappers(root: Path, slices: list[object], issues: list[str], *, check_all_wrappers: bool) -> None:
    if not check_all_wrappers:
        return
    expected_paths = {entry.check_script.resolve() for entry in slices}
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
        validate_low_level_wrapper_markers(root, entry.slug, issues)

    validate_build_steps(root, slices, issues)
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

        (paths.tests_dir / "build.zig").write_text(
            "\n".join(
                [
                    'const phase3_test_step = b.step("phase3-test", "Run Phase 3 tests");',
                    'const phase3_alpha_dump_step = b.step("phase3-alpha-dump", "Run Phase 3 alpha dump");',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_low_level_wrappers.zig").write_text(
            "\n".join([*LOW_LEVEL_WRAPPER_REQUIRED_MARKERS, ""]),
            encoding="utf-8",
            newline="\n",
        )

        manifest_rel = "zigux/tests/fixtures/phase3_alpha/expected.json"
        manifest = {
            "phase": "Phase 3",
            "status": "ready",
            "slice": "alpha-slice",
            "files": [manifest_rel],
            "file_count": 1,
        }
        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
            newline="\n",
        )
        abi_manifest_path = root / "tmp" / "abi_manifest.json"
        abi_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        abi_manifest_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-slice",
                    "files": [ABI_REQUIRED_MANIFEST_FILES[0]],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        abi_issues: list[str] = []
        validate_manifest(root, abi_manifest_path, "abi", abi_issues)
        for rel in ABI_REQUIRED_MANIFEST_FILES[1:]:
            assert f"abi:manifest_missing_required_file={rel}" in abi_issues

        abi_manifest_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-slice",
                    "files": list(ABI_REQUIRED_MANIFEST_FILES),
                    "file_count": len(ABI_REQUIRED_MANIFEST_FILES),
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        abi_issues = []
        validate_manifest(root, abi_manifest_path, "abi", abi_issues)
        validate_low_level_wrapper_markers(root, "abi", abi_issues)
        assert abi_issues == []
        (paths.tests_dir / "phase3_low_level_wrappers.zig").write_text(
            "\n".join(LOW_LEVEL_WRAPPER_REQUIRED_MARKERS[:-1]) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        marker_issues: list[str] = []
        validate_low_level_wrapper_markers(root, "abi", marker_issues)
        assert marker_issues == [f"abi:missing_low_level_wrapper_marker={LOW_LEVEL_WRAPPER_REQUIRED_MARKERS[-1]}"]
        (paths.tests_dir / "phase3_low_level_wrappers.zig").write_text(
            "\n".join([*LOW_LEVEL_WRAPPER_REQUIRED_MARKERS, ""]),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-alpha.py").write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        (paths.tests_dir / "phase3_alpha_dump.zig").write_text("// alpha\n", encoding="utf-8", newline="\n")
        (fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_c_harness.c").write_text("int main(void) { return 0; }\n", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-slice",
                    "files": [manifest_rel, manifest_rel],
                    "file_count": 2,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        duplicate_issues: list[str] = []
        validate_manifest(root, fixture_dir / "phase3_alpha_manifest.json", "alpha", duplicate_issues)
        assert duplicate_issues == [f"alpha:manifest_duplicate_file={manifest_rel}"]
        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / "artifact-diff.md").write_text(
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 3 use",
                    "- `zigux/tests/fixtures/phase3_alpha/expected.json` anchors the bounded Phase 3 alpha parity claim.",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug alpha` compares that committed JSON fixture against both the bounded C harness and the Zig alpha dump.",
                    "",
                    "Rules",
                    "- keep fixtures reviewable",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        slices = discover_phase3_slices(paths)
        assert [entry.slug for entry in select_slices(slices, [])] == ["alpha"]
        assert [entry.slug for entry in select_slices(slices, ["alpha"])] == ["alpha"]
        try:
            select_slices(slices, ["missing"])
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug to fail")
        assert validate_slices(root, slices, check_artifact_diff=True) == []

        paths.scripts_dir.joinpath("check-phase3-alpha.py").unlink()
        assert validate_slices(root, slices, check_artifact_diff=True) == []

        obsolete_wrapper = paths.scripts_dir / "check-phase3-stale.py"
        obsolete_wrapper.write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "obsolete_wrapper:scripts/zigux/check-phase3-stale.py" in issues
        obsolete_wrapper.unlink()

        support_checker = paths.scripts_dir / "check-phase3-support.py"
        support_checker.write_text("# support\n", encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "obsolete_wrapper:scripts/zigux/check-phase3-support.py" not in issues

        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha.py",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_slices(root, slices, check_artifact_diff=True) == []

        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-slice",
                    "files": ["scripts/zigux/check-phase3-alpha.py", manifest_rel],
                    "file_count": 2,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "alpha:manifest_legacy_wrapper_file=scripts/zigux/check-phase3-alpha.py" in issues

        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-alpha.py").write_text("# stale\n", encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "alpha:wrapper_template_mismatch:scripts/zigux/check-phase3-alpha.py" in issues

        (paths.scripts_dir / "check-phase3-alpha.py").write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        (paths.docs_dir / "phase3-alpha-slice.md").write_text("PHASE3_STATUS=ready\n", encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "alpha:missing_doc_marker=PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py" in issues
        assert (
            "alpha:missing_doc_marker_one_of="
            "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha"
            "|PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha.py"
        ) in issues

        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "- `PHASE3_STATUS=ready`",
                    "- `PHASE3_SLICE=alpha-slice`",
                    "- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`",
                    "- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`",
                    "- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha`",
                    "- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert (
            "alpha:duplicate_doc_marker=PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py"
            in issues
        )

        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "- `PHASE3_STATUS=ready`",
                    "- `PHASE3_SLICE=alpha-slice`",
                    "- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`",
                    "- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha`",
                    "- `PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha.py`",
                    "- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert (
            "alpha:duplicate_doc_marker_one_of="
            "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha"
            "|PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha.py"
        ) in issues

        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / "artifact-diff.md").write_text(
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
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "artifact_diff:stale_phase3_section:Documentation/zigux/artifact-diff.md" in issues

        (paths.docs_dir / "artifact-diff.md").write_text(
            "# Artifact Diff Policy\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_slices(root, slices, check_artifact_diff=True)
        assert "artifact_diff:missing_phase3_section:Documentation/zigux/artifact-diff.md" in issues

        (paths.tests_dir / "build.zig").write_text(
            'const phase3_alpha_dump_step = b.step("phase3-alpha-dump", "Run Phase 3 alpha dump");\n',
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_slices(root, slices, check_artifact_diff=False)
        assert f"build:missing_step:{BUILD_FILE_REL}:phase3-test" in issues

        (paths.tests_dir / "build.zig").write_text(
            'const phase3_test_step = b.step("phase3-test", "Run Phase 3 tests");\n',
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_slices(root, slices, check_artifact_diff=False)
        assert f"alpha:missing_build_step:{BUILD_FILE_REL}:phase3-alpha-dump" in issues

        (paths.tests_dir / "build.zig").write_text(
            "\n".join(
                [
                    'const phase3_test_step = b.step("phase3-test", "Run Phase 3 tests");',
                    'const phase3_alpha_dump_step = b.step("phase3-alpha-dump", "Run Phase 3 alpha dump");',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        loop_slug = "loop-window-policy-budget-window-policy-budget-window-policy-budget-window-policy"
        loop_fixture_dir = paths.fixtures_dir / "phase3_loop_window_policy_budget_window_policy_budget_window_policy_budget_window_policy"
        loop_fixture_dir.mkdir(parents=True, exist_ok=True)
        loop_manifest_rel = f"{loop_fixture_dir.relative_to(root).as_posix()}/expected.json"
        (loop_fixture_dir / "phase3_loop_window_policy_budget_window_policy_budget_window_POLICY_budget_window_policy_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "loop-slice",
                    "files": [loop_manifest_rel],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / f"phase3-{loop_slug}-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=loop-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    f"PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug {loop_slug}",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_loop_window_policy_budget_window_policy_budget_window_policy_budget_window_policy_dump.zig").write_text(
            "// loop\n",
            encoding="utf-8",
            newline="\n",
        )
        (loop_fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (loop_fixture_dir / "phase3_loop_window_policy_budget_window_policy_budget_window_policy_budget_window_policy_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
            newline="\n",
        )
        canonical_slug = "alpha-beta-gamma-delta"
        (paths.docs_dir / f"phase3-{canonical_slug}-slice.md").write_text(
            "canonical\n",
            encoding="utf-8",
            newline="\n",
        )
        overgrown_slug = "alpha-beta-gamma-delta-epsilon-zeta-eta-theta-iota-kappa-lambda-mu-nu"
        overgrown_fixture_dir = paths.fixtures_dir / "phase3_alpha_beta_gamma_delta_epsilon_zeta_eta_theta_iota_kappa_lambda_mu_nu"
        overgrown_fixture_dir.mkdir(parents=True, exist_ok=True)
        overgrown_manifest_rel = f"{overgrown_fixture_dir.relative_to(root).as_posix()}/expected.json"
        (
            overgrown_fixture_dir
            / "phase3_alpha_beta_gamma_delta_epsilon_zeta_eta_theta_iota_kappa_lambda_mu_nu_manifest.json"
        ).write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "overgrown-slice",
                    "files": [overgrown_manifest_rel],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / f"phase3-{overgrown_slug}-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=overgrown-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    f"PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug {overgrown_slug}",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_alpha_beta_gamma_delta_epsilon_zeta_eta_theta_iota_kappa_lambda_mu_nu_dump.zig").write_text(
            "// overgrown\n",
            encoding="utf-8",
            newline="\n",
        )
        (overgrown_fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (
            overgrown_fixture_dir
            / "phase3_alpha_beta_gamma_delta_epsilon_zeta_eta_theta_iota_kappa_lambda_mu_nu_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
            newline="\n",
        )

        slices = discover_phase3_slices(paths)
        issues = validate_slices(root, slices, check_slug_sanity=True)
        assert any(issue.startswith(f"slug_audit:slug-too-many-tokens:{overgrown_slug}:") for issue in issues)
        assert any(issue.startswith(f"slug_audit:slug-repeated-token:{loop_slug}:") for issue in issues)
        assert any(issue.startswith(f"slug_audit:slug-repeated-phrase:{loop_slug}:") for issue in issues)
        assert not any(
            issue.startswith(f"slug_rename_candidate:{overgrown_slug}:")
            for issue in issues
        )

    print("PHASE3_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate discovered Phase 3 slice assets and documentation markers.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated Phase 3 validation coverage in a temporary workspace.")
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
        check_all_wrappers=not bool(args.slug),
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
