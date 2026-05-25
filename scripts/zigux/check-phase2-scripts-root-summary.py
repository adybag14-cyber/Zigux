#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "keep those installer, helper-local kconfig allconfig guard, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

EXACT_COUNT_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "keep those installer, helper-local kconfig allconfig guard, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
)

REQUIRED_MANIFEST_SURFACES = (
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

REQUIRED_MANIFEST_NOTE = (
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize."
)

DEFAULT_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
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


def read_manifest(path: Path) -> dict[str, object]:
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def collect_manifest_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(collect_manifest_strings(item))
        return strings
    if isinstance(value, dict):
        strings: set[str] = set()
        for item in value.values():
            strings.update(collect_manifest_strings(item))
        return strings
    return set()


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def load_required_make_routes(root: Path) -> tuple[str, ...]:
    payload = read_manifest(resolve_path(root, TOOLCHAIN_POLICY))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
        route = route.strip()
        if route in seen:
            raise SystemExit(f"duplicate required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}: {route}")
        normalized.append(route)
        seen.add(route)
    return tuple(normalized)


def collect_manifest_surface_issues(strings: set[str], required_make_routes: tuple[str, ...]) -> list[tuple[str, str]]:
    issues = [
        ("MISSING_MANIFEST_SURFACE", surface)
        for surface in REQUIRED_MANIFEST_SURFACES
        if surface not in strings
    ]
    for route in required_make_routes:
        wrapper = f"make -C zigux {route}"
        if wrapper not in strings:
            issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", wrapper))
    if "make -C zigux phase2" not in strings:
        issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", "make -C zigux phase2"))
    return issues


def collect_readme_make_wrapper_issues(text: str, required_make_routes: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for route in required_make_routes:
        wrapper = f"`make -C zigux {route}`"
        if wrapper not in text:
            issues.append(("MISSING_README_MAKE_WRAPPER", wrapper))
    if "`make -C zigux phase2`" not in text:
        issues.append(("MISSING_README_MAKE_WRAPPER", "`make -C zigux phase2`"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    manifest = read_manifest(resolve_path(root, PHASE2_TOOL_MANIFEST))
    manifest_strings = collect_manifest_strings(manifest)
    required_make_routes = load_required_make_routes(root)

    issues = collect_missing_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKER")
    issues.extend(collect_exact_count_markers(scripts_readme_text, EXACT_COUNT_MARKERS, "EXACT_COUNT_SCRIPTS_README_MARKER"))
    issues.extend(collect_forbidden_markers(scripts_readme_text, FORBIDDEN_MARKERS, "FORBIDDEN_SCRIPTS_README_MARKER"))
    issues.extend(collect_manifest_surface_issues(manifest_strings, required_make_routes))
    issues.extend(collect_readme_make_wrapper_issues(scripts_readme_text, required_make_routes))

    if REQUIRED_MANIFEST_NOTE not in manifest_strings:
        issues.append(("MISSING_MANIFEST_NOTE", REQUIRED_MANIFEST_NOTE))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_MANIFEST_GAPS", json.dumps(manifest.get("repo_reality_gaps"), sort_keys=True)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_SCRIPTS_ROOT_SUMMARY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_manifest(required_make_routes: tuple[str, ...] = DEFAULT_REQUIRED_MAKE_ROUTES) -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "status": "active",
        "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
        "workflow": ".github/workflows/zigux-bootstrap.yml",
        "present_surfaces": {
            "review_surfaces": [
                "Documentation/zigux/README.md",
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/review-checklist.md",
                "scripts/zigux/README.md",
                "zigux/tests/README.md",
            ],
            "bootstrap_helpers": [
                "scripts/zigux/install-zig.py",
                "scripts/zigux/stage-pinned-zig-archive.py",
            ],
            "checkers": [
                "scripts/zigux/check-genksyms-bridge.py",
                "scripts/zigux/check-phase2-cross.py",
                "scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "scripts/zigux/check-phase2-docs-shared-reminder.py",
                "scripts/zigux/check-phase2-fixdep-gate.py",
                "scripts/zigux/check-fixdep-diff.py",
                "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
                "scripts/zigux/check-phase2-required-make-routes.py",
                "scripts/zigux/check-phase2-tool-manifest.py",
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            ],
            "artifact_support": [
                "scripts/zigux/artifact_diff.py",
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
            ],
            "cross_route_support": [
                "scripts/zigux/check-phase2-cross.py",
                "zigux/tests/fixtures/phase2_cross_targets.json",
            ],
            "validators": [
                "scripts/zigux/validate-phase2.py",
                "scripts/zigux/validate-phase2-closure.py",
            ],
            "make_wrappers": [
                "zigux/Makefile",
                *(f"make -C zigux {route}" for route in required_make_routes),
                "make -C zigux phase2",
            ],
        },
        "repo_reality_gaps": [],
        "notes": [REQUIRED_MANIFEST_NOTE],
    }


def build_sample_root(root: Path, required_make_routes: tuple[str, ...] = DEFAULT_REQUIRED_MAKE_ROUTES) -> None:
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(
        resolve_path(root, PHASE2_TOOL_MANIFEST),
        json.dumps(build_self_test_manifest(required_make_routes), indent=2) + "\n",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(required_make_routes),
                },
            },
            indent=2,
        )
        + "\n",
    )


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(SCRIPTS_README_MARKERS)
        + len(EXACT_COUNT_MARKERS)
        + len(FORBIDDEN_MARKERS)
        + len(REQUIRED_MANIFEST_SURFACES)
        + 1
        + 1
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_root_summary_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        scripts_readme_path = resolve_path(root, SCRIPTS_README)
        scripts_readme_text = read_text(scripts_readme_path)
        for marker in SCRIPTS_README_MARKERS:
            write_text(scripts_readme_path, remove_all(scripts_readme_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in issues, (marker, issues)
            build_sample_root(root)
            scripts_readme_text = read_text(scripts_readme_path)
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            write_text(scripts_readme_path, scripts_readme_text + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_SCRIPTS_README_MARKER", f"2::{marker}") in issues, (marker, issues)
            build_sample_root(root)
            scripts_readme_text = read_text(scripts_readme_path)
            checks_run += 1

        for marker in FORBIDDEN_MARKERS:
            write_text(scripts_readme_path, scripts_readme_text + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_SCRIPTS_README_MARKER", marker) in issues, (marker, issues)
            build_sample_root(root)
            scripts_readme_text = read_text(scripts_readme_path)
            checks_run += 1

        manifest_path = resolve_path(root, PHASE2_TOOL_MANIFEST)
        manifest = read_manifest(manifest_path)
        for surface in REQUIRED_MANIFEST_SURFACES:
            strings = collect_manifest_strings(manifest)
            assert surface in strings, surface
            pruned = json.loads(json.dumps(manifest))
            for key, value in pruned.get("present_surfaces", {}).items():
                if isinstance(value, list):
                    pruned["present_surfaces"][key] = [entry for entry in value if entry != surface]
            write_text(manifest_path, json.dumps(pruned, indent=2) + "\n")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_SURFACE", surface) in issues, (surface, issues)
            build_sample_root(root)
            manifest = read_manifest(manifest_path)
            checks_run += 1

        manifest["notes"] = []
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_NOTE", REQUIRED_MANIFEST_NOTE) in issues, issues
        build_sample_root(root)
        manifest = read_manifest(manifest_path)
        checks_run += 1

        manifest["repo_reality_gaps"] = ["gap"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("NONEMPTY_MANIFEST_GAPS", json.dumps(["gap"])) in issues, issues
        build_sample_root(root)
        checks_run += 1

        build_sample_root(root, DEFAULT_REQUIRED_MAKE_ROUTES + ("phase2-future",))
        issues = collect_issues(root)
        assert ("MISSING_README_MAKE_WRAPPER", "`make -C zigux phase2-future`") in issues, issues
        assert ("MISSING_MANIFEST_MAKE_WRAPPER", "make -C zigux phase2-future") not in issues, issues
        checks_run += 1

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_SCRIPTS_ROOT_SUMMARY=self-test-pass")
    print(f"PHASE2_SCRIPTS_ROOT_SUMMARY_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 scripts-root reminder packet aligned with the current manifest and make-route surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in regression coverage")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like synthetic repository root for focused checker validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_SCRIPTS_ROOT_SUMMARY_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_SCRIPTS_ROOT_SUMMARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
