#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "lib/devres.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_iomap_reviewability.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "scripts/zigux/validate-phase13-release.py",
    "zigux/Makefile",
]

BUILD_REQUIRED_MARKERS = [
    'b.path("../../lib/devres.zig")',
    'b.path("phase13_devres.zig")',
    'b.path("phase13_devres_dma_coherent.zig")',
    'const phase13_devres_tests = b.addTest(.{',
    'const phase13_devres_dma_coherent_tests = b.addTest(.{',
    'test_step.dependOn(&run_phase13_devres_tests.step);',
    'test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);',
]

DMA_COHERENT_REQUIRED_MARKERS = [
    "test \"phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership\"",
    "test \"phase13 devres coherent-dma boundary note keeps dma and scatterlist out of scope\"",
    "\"preexisting_devres_dma_coherent_zig_present\": true",
    "\"preexisting_phase13_devres_dma_coherent_test_present\": true",
    "\"preexisting_phase13_devres_iomap_reviewability_test_present\": true",
    "\"id\": \"phase13-devres-live-dma-backed-mappings\"",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
]

MAKE_REQUIRED_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet.py",
]

VALIDATOR_REQUIRED_MARKERS = [
    "\"zigux/tests/phase13_devres.zig\",",
    "\"zigux/tests/phase13_devres_manifest.json\",",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _collect_missing_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def _validate_manifest(text: str) -> list[str]:
    issues: list[str] = []
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"phase13-devres-manifest:json:{exc.msg}"]

    summary = manifest.get("survey_summary", {})
    for key in (
        "preexisting_devres_dma_coherent_zig_present",
        "preexisting_phase13_devres_dma_coherent_test_present",
        "preexisting_phase13_devres_iomap_reviewability_test_present",
    ):
        if summary.get(key) is not True:
            issues.append(f"phase13-devres-manifest-summary:{key}")

    gaps = {gap.get("id"): gap for gap in manifest.get("gaps", []) if isinstance(gap, dict)}
    for gap_id in (
        "phase13-devres-dma-coherent-boundary-replay",
        "phase13-devres-live-dma-backed-mappings",
        "phase13-devres-live-scatterlist-ownership",
    ):
        if gap_id not in gaps:
            issues.append(f"phase13-devres-manifest-gap:{gap_id}")
    for gap_id in (
        "phase13-devres-live-dma-backed-mappings",
        "phase13-devres-live-scatterlist-ownership",
    ):
        if gaps.get(gap_id, {}).get("status") != "blocked_on_live_resource_state":
            issues.append(f"phase13-devres-manifest-gap-status:{gap_id}")

    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    issues.extend(_collect_missing_markers(_read(root / "zigux/tests/phase13_build.zig"), BUILD_REQUIRED_MARKERS, "phase13-build"))
    issues.extend(_collect_missing_markers(_read(root / "zigux/tests/phase13_devres_dma_coherent.zig"), DMA_COHERENT_REQUIRED_MARKERS, "phase13-devres-dma-coherent"))
    issues.extend(_collect_missing_markers(_read(root / "zigux/Makefile"), MAKE_REQUIRED_MARKERS, "makefile"))
    issues.extend(_collect_missing_markers(_read(root / "scripts/zigux/validate-phase13-release.py"), VALIDATOR_REQUIRED_MARKERS, "phase13-release-validator"))
    issues.extend(_validate_manifest(_read(root / "zigux/tests/phase13_devres_manifest.json")))
    return issues


def _seed_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        _write(root / rel, "// stub\n")
    _write(root / "zigux/tests/phase13_build.zig", "\n".join(BUILD_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/phase13_devres_dma_coherent.zig", "\n".join(DMA_COHERENT_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/Makefile", "\n".join(MAKE_REQUIRED_MARKERS) + "\n")
    _write(root / "scripts/zigux/validate-phase13-release.py", "\n".join(VALIDATOR_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/phase13_devres_manifest.json", json.dumps({
        "survey_summary": {
            "preexisting_devres_dma_coherent_zig_present": True,
            "preexisting_phase13_devres_dma_coherent_test_present": True,
            "preexisting_phase13_devres_iomap_reviewability_test_present": True,
        },
        "gaps": [
            {"id": "phase13-devres-dma-coherent-boundary-replay", "status": "starter_landed"},
            {"id": "phase13-devres-live-dma-backed-mappings", "status": "blocked_on_live_resource_state"},
            {"id": "phase13-devres-live-scatterlist-ownership", "status": "blocked_on_live_resource_state"},
        ],
    }, indent=2) + "\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase13-devres-packet-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_packet_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        (root / "zigux/tests/phase13_build.zig").write_text('b.path("phase13_devres.zig")\n', encoding="utf-8")
        _assert_only(validate(root), [
            "phase13-build:b.path(\"../../lib/devres.zig\")",
            "phase13-build:b.path(\"phase13_devres_dma_coherent.zig\")",
            "phase13-build:const phase13_devres_tests = b.addTest(.{",
            "phase13-build:const phase13_devres_dma_coherent_tests = b.addTest(.{",
            "phase13-build:test_step.dependOn(&run_phase13_devres_tests.step);",
            "phase13-build:test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
        ], "build_guard_failed")
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase13_devres_manifest.json").write_text(json.dumps({"survey_summary": {}}, indent=2) + "\n", encoding="utf-8")
        _assert_only(validate(root), [
            "phase13-devres-manifest-summary:preexisting_devres_dma_coherent_zig_present",
            "phase13-devres-manifest-summary:preexisting_phase13_devres_dma_coherent_test_present",
            "phase13-devres-manifest-summary:preexisting_phase13_devres_iomap_reviewability_test_present",
            "phase13-devres-manifest-gap:phase13-devres-dma-coherent-boundary-replay",
            "phase13-devres-manifest-gap:phase13-devres-live-dma-backed-mappings",
            "phase13-devres-manifest-gap:phase13-devres-live-scatterlist-ownership",
            "phase13-devres-manifest-gap-status:phase13-devres-live-dma-backed-mappings",
            "phase13-devres-manifest-gap-status:phase13-devres-live-scatterlist-ownership",
        ], "manifest_guard_failed")
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase13_devres_dma_coherent.zig").write_text('test "phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership" {}\n', encoding="utf-8")
        _assert_only(validate(root), [
            "phase13-devres-dma-coherent:test \"phase13 devres coherent-dma boundary note keeps dma and scatterlist out of scope\"",
            "phase13-devres-dma-coherent:\"preexisting_devres_dma_coherent_zig_present\": true",
            "phase13-devres-dma-coherent:\"preexisting_phase13_devres_dma_coherent_test_present\": true",
            "phase13-devres-dma-coherent:\"preexisting_phase13_devres_iomap_reviewability_test_present\": true",
            "phase13-devres-dma-coherent:\"id\": \"phase13-devres-live-dma-backed-mappings\"",
            "phase13-devres-dma-coherent:\"id\": \"phase13-devres-live-scatterlist-ownership\"",
        ], "dma_guard_failed")
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase13_devres_dma_coherent.zig").unlink()
        _assert_only(validate(root), ["missing_file:zigux/tests/phase13_devres_dma_coherent.zig"], "required_file_guard_failed")
        case_count += 1

    print("PHASE13_DEVRES_PACKET=pass")
    print(f"PHASE13_DEVRES_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shipped Phase 13 devres packet surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(f"PHASE13_DEVRES_PACKET_ISSUE={issue}")
        return 1

    print("PHASE13_DEVRES_PACKET=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
