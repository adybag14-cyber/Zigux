#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

TESTS_README_MARKERS = (
    "- `scripts/zigux/check-phase2-fixdep-gate.py`",
    "- `scripts/zigux/check-fixdep-diff.py`",
    "- `scripts/zigux/fixdep.zig`",
    "- `zigux/tests/fixtures/fixdep/cases.json`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "Does the bounded Phase 2 reminder keep the current direct-readback toolchain self-check, repo-local archive workflow, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

MANIFEST_MARKERS = (
    "zigux/tests/README.md",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings: set[str] = set()
        for item in value.values():
            strings.update(collect_strings(item))
        return strings
    return set()


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_missing_manifest_markers(strings: set[str]) -> list[tuple[str, str]]:
    return [("MISSING_MANIFEST_MARKERS", marker) for marker in MANIFEST_MARKERS if marker not in strings]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    tests_text = read_text(resolve_path(root, TESTS_README))
    manifest_data = read_json(resolve_path(root, TOOL_MANIFEST))
    manifest_strings = collect_strings(manifest_data)
    issues.extend(collect_missing_markers(tests_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(collect_missing_manifest_markers(manifest_strings))
    if isinstance(manifest_data, dict) and manifest_data.get("repo_reality_gaps") != []:
        issues.append(
            (
                "NONEMPTY_MANIFEST_GAPS",
                json.dumps(manifest_data.get("repo_reality_gaps"), sort_keys=True),
            )
        )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TESTS_README_FIXDEP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    manifest_payload = {
        "present_surfaces": {
            "review_surfaces": ["zigux/tests/README.md"],
            "fixdep_support": [
                "scripts/zigux/check-phase2-fixdep-gate.py",
                "scripts/zigux/check-fixdep-diff.py",
                "scripts/zigux/fixdep.zig",
                "zigux/tests/fixtures/fixdep/cases.json",
            ],
        },
        "repo_reality_gaps": [],
    }
    write_text(resolve_path(root, TOOL_MANIFEST), json.dumps(manifest_payload, indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(TESTS_README_MARKERS) + len(MANIFEST_MARKERS) + 3
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_readme_fixdep_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in MANIFEST_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_MARKERS", marker) in issues
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["repo_reality_gaps"] = ["stale-gap"]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("NONEMPTY_MANIFEST_GAPS", '["stale-gap"]') in issues
        checks_run += 1

        for rel_path in (TESTS_README, TOOL_MANIFEST):
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_TESTS_README_FIXDEP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_FIXDEP_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the tests-root Phase 2 fixdep reminder aligned with the current manifest-backed packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample root for no-checkout validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_TESTS_README_FIXDEP_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_README_FIXDEP_PACKET=pass")
    print(f"PHASE2_TESTS_README_FIXDEP_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_FIXDEP_PACKET_MANIFEST_MARKER_COUNT={len(MANIFEST_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
