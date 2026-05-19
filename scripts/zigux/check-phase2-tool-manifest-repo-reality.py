#!/usr/bin/env python3
"""Keep the Phase 2 tool manifest honest about split readback versus older gap lists."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

RETURNED_PACKET_PATHS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

README_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current `master` now directly materializes",
)

NOTE_MARKERS = (
    "Current master already directly materializes scripts/zigux/install-zig.py, scripts/zigux/check-phase2-cross.py, and zigux/tests/fixtures/phase2_cross_targets.json through the tests-root packet, so keep that returned direct-readback trio explicit here even while the older shared closure-side vocabulary still lists it in repo_reality_gaps.",
    "Do not drop the installer and direct cross-route trio from repo_reality_gaps until the shared closure-side and reminder-owner packets reconcile to the returned direct-readback story.",
)

RETURNED_PACKET_STATUS = (
    "present_on_current_master_but_still_listed_in_repo_reality_gaps_until_shared_closure_surfaces_reconcile"
)
EXPECTED_SELF_TEST_CASE_COUNT = 14


def resolve(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    manifest_path = resolve(root, MANIFEST)
    tests_readme_path = resolve(root, TESTS_README)
    manifest = read_json(manifest_path)
    tests_readme = read_text(tests_readme_path)

    for relative in RETURNED_PACKET_PATHS:
        if not resolve(root, Path(relative)).exists():
            issues.append(("MISSING_RETURNED_PACKET_FILE", relative))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(repo_reality_gaps, list):
        issues.append(("INVALID_MANIFEST_SHAPE", "repo_reality_gaps"))
        return issues

    for relative in RETURNED_PACKET_PATHS:
        if relative not in repo_reality_gaps:
            issues.append(("MISSING_REPO_REALITY_GAP", relative))

    returned_packet = manifest.get("returned_direct_readback_packet")
    if not isinstance(returned_packet, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "returned_direct_readback_packet"))
        return issues

    if returned_packet.get("status") != RETURNED_PACKET_STATUS:
        issues.append(("INVALID_RETURNED_PACKET_FIELD", "status"))
    if returned_packet.get("evidence_anchor") != "zigux/tests/README.md":
        issues.append(("INVALID_RETURNED_PACKET_FIELD", "evidence_anchor"))
    if returned_packet.get("paths") != list(RETURNED_PACKET_PATHS):
        issues.append(("INVALID_RETURNED_PACKET_FIELD", "paths"))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_MANIFEST_SHAPE", "notes"))
        return issues
    for marker in NOTE_MARKERS:
        if marker not in notes:
            issues.append(("MISSING_NOTE_MARKER", marker))

    for marker in README_MARKERS:
        if marker not in tests_readme:
            issues.append(("MISSING_TESTS_README_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOL_MANIFEST_REPO_REALITY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve(root, MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "repo_reality_gaps": list(RETURNED_PACKET_PATHS),
                "returned_direct_readback_packet": {
                    "status": RETURNED_PACKET_STATUS,
                    "evidence_anchor": "zigux/tests/README.md",
                    "paths": list(RETURNED_PACKET_PATHS),
                },
                "notes": list(NOTE_MARKERS),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, TESTS_README),
        "\n".join(README_MARKERS) + "\n",
    )
    for relative in RETURNED_PACKET_PATHS:
        write_text(resolve(root, Path(relative)), "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_repo_reality_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        manifest_path = resolve(root, MANIFEST)

        for relative in RETURNED_PACKET_PATHS:
            build_self_test_root(root)
            manifest = read_json(manifest_path)
            assert isinstance(manifest, dict)
            manifest["repo_reality_gaps"] = [value for value in manifest["repo_reality_gaps"] if value != relative]
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            assert ("MISSING_REPO_REALITY_GAP", relative) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["returned_direct_readback_packet"]["paths"] = ["scripts/zigux/install-zig.py"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("INVALID_RETURNED_PACKET_FIELD", "paths") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["returned_direct_readback_packet"]["status"] = "stale"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("INVALID_RETURNED_PACKET_FIELD", "status") in collect_issues(root)
        checks_run += 1

        for marker in NOTE_MARKERS:
            build_self_test_root(root)
            manifest = read_json(manifest_path)
            assert isinstance(manifest, dict)
            manifest["notes"] = [value for value in manifest["notes"] if value != marker]
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            tests_readme_path = resolve(root, TESTS_README)
            tests_readme = read_text(tests_readme_path).replace(marker, "", 1)
            write_text(tests_readme_path, tests_readme)
            assert ("MISSING_TESTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        resolve(root, Path(RETURNED_PACKET_PATHS[0])).unlink()
        assert ("MISSING_RETURNED_PACKET_FILE", RETURNED_PACKET_PATHS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(manifest_path, "{not-json}\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid manifest json did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOL_MANIFEST_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_REPO_REALITY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 tool manifest keeps the returned direct-readback packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST_REPO_REALITY=pass")
    print(f"PHASE2_TOOL_MANIFEST_REPO_REALITY_GAP_COUNT={len(RETURNED_PACKET_PATHS)}")
    print(f"PHASE2_TOOL_MANIFEST_REPO_REALITY_RETURNED_PACKET_COUNT={len(RETURNED_PACKET_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
