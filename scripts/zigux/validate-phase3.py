#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from phase3_catalog import Phase3Paths, discover_phase3_slices
from phase3_check_lib import legacy_wrapper_gate_for_slug, render_wrapper_stub, shared_runner_gate_for_slug


ROOT = Path(__file__).resolve().parents[2]


def _is_legacy_wrapper_manifest_file(rel: str) -> bool:
    return rel.startswith("scripts/zigux/check-phase3-") and rel.endswith(".py")


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
    file_count = data.get("file_count")
    if file_count != len(files):
        issues.append(f"{slug}:manifest_file_count={file_count}")
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
    required_markers = [
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
        "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    ]
    if manifest:
        required_markers.insert(0, f"PHASE3_STATUS={manifest.get('status')}")
        required_markers.insert(1, f"PHASE3_SLICE={manifest.get('slice')}")
    for marker in required_markers:
        if marker not in doc:
            issues.append(f"{slug}:missing_doc_marker={marker}")

    interop_markers = [shared_runner_gate_for_slug(slug), legacy_wrapper_gate_for_slug(slug)]
    if not any(marker in doc for marker in interop_markers):
        issues.append(f"{slug}:missing_doc_marker_one_of={'|'.join(interop_markers)}")


def validate_wrapper_template(root: Path, script_path: Path, slug: str, issues: list[str]) -> None:
    if not script_path.exists():
        return
    expected = render_wrapper_stub()
    current = script_path.read_text(encoding="utf-8")
    if current != expected:
        issues.append(f"{slug}:wrapper_template_mismatch:{script_path.relative_to(root).as_posix()}" )


def validate_obsolete_wrappers(root: Path, slices: list[object], issues: list[str]) -> None:
    expected_paths = {entry.check_script.resolve() for entry in slices}
    scripts_dir = root / "scripts" / "zigux"
    for path in sorted(scripts_dir.glob("check-phase3-*.py")):
        if path.resolve() in expected_paths:
            continue
        issues.append(f"obsolete_wrapper:{path.relative_to(root).as_posix()}")


def validate_slices(root: Path, slices: list[object]) -> list[str]:
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

    validate_obsolete_wrappers(root, slices, issues)
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

        slices = discover_phase3_slices(paths)
        assert validate_slices(root, slices) == []

        paths.scripts_dir.joinpath("check-phase3-alpha.py").unlink()
        assert validate_slices(root, slices) == []

        obsolete_wrapper = paths.scripts_dir / "check-phase3-stale.py"
        obsolete_wrapper.write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices)
        assert "obsolete_wrapper:scripts/zigux/check-phase3-stale.py" in issues
        obsolete_wrapper.unlink()

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
        assert validate_slices(root, slices) == []

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
        issues = validate_slices(root, slices)
        assert "alpha:manifest_legacy_wrapper_file=scripts/zigux/check-phase3-alpha.py" in issues

        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-alpha.py").write_text("# stale\n", encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices)
        assert "alpha:wrapper_template_mismatch:scripts/zigux/check-phase3-alpha.py" in issues

        (paths.scripts_dir / "check-phase3-alpha.py").write_text(render_wrapper_stub(), encoding="utf-8", newline="\n")
        (paths.docs_dir / "phase3-alpha-slice.md").write_text("PHASE3_STATUS=ready\n", encoding="utf-8", newline="\n")
        issues = validate_slices(root, slices)
        assert "alpha:missing_doc_marker=PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py" in issues
        assert (
            "alpha:missing_doc_marker_one_of="
            "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha"
            "|PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha.py"
        ) in issues

    print("PHASE3_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate discovered Phase 3 slice assets and documentation markers.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated Phase 3 validation coverage in a temporary workspace.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    slices = discover_phase3_slices()
    issues = validate_slices(ROOT, slices)
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
