#!/usr/bin/env python3
"""Guard the shared Phase 2 tooling checker packet in the closure note."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

EXPECTED_SHARED_TOOLING_CHECKERS = (
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
)

REQUIRED_CLOSURE_MARKERS = (
    "## Current Shared Repo-Tooling Evidence",
    "- `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, and `scripts/zigux/check-phase2-artifact-tools-manifest.py` keep the shared manifest, workflow-route, and artifact-support packet explicit from current `master`.",
    "- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` keep the helper-local kconfig, direct cross-route, and fixdep governance/parity packet directly replayable beside the closure note.",
    "- `scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair instead of falling back into repo-reality-gap wording.",
    "- `python3 scripts/zigux/check-phase2-tool-manifest.py`",
    "- `python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "- `python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "- `python3 scripts/zigux/check-phase2-cross.py`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "- `python3 scripts/zigux/check-fixdep-diff.py`",
    "PHASE2_SHARED_TOOLING_CHECKERS="
    + ",".join(EXPECTED_SHARED_TOOLING_CHECKERS),
)

REQUIRED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)

REQUIRED_REVIEW_SURFACES = (
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

REQUIRED_ARTIFACT_SUPPORT = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)

REQUIRED_CROSS_ROUTE_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

REQUIRED_FIXDEP_SUPPORT = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest shape: {path}")
    return payload


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def normalize_str_list(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SystemExit(f"invalid manifest string-list for {label}")
    return tuple(value)


def parse_shared_tooling_checker_line(closure_text: str) -> tuple[str, ...] | None:
    for line in closure_text.splitlines():
        if line.startswith("PHASE2_SHARED_TOOLING_CHECKERS="):
            payload = line.split("=", 1)[1]
            if not payload:
                return tuple()
            return tuple(part.strip() for part in payload.split(","))
    return None


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    manifest = read_manifest(resolve_path(root, PHASE2_TOOL_MANIFEST))
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        raise SystemExit("invalid manifest present_surfaces")

    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    checker_line = parse_shared_tooling_checker_line(closure_text)
    if checker_line is None:
        issues.append(("MISSING_SHARED_TOOLING_CHECKER_LINE", "PHASE2_SHARED_TOOLING_CHECKERS"))
    else:
        if checker_line != EXPECTED_SHARED_TOOLING_CHECKERS:
            issues.append(
                (
                    "SHARED_TOOLING_CHECKER_LINE_DRIFT",
                    json.dumps(checker_line),
                )
            )

    manifest_checkers = normalize_str_list(present_surfaces.get("checkers"), "checkers")
    for checker in REQUIRED_MANIFEST_CHECKERS:
        if checker not in manifest_checkers:
            issues.append(("MISSING_MANIFEST_CHECKER", checker))

    review_surfaces = normalize_str_list(present_surfaces.get("review_surfaces"), "review_surfaces")
    for surface in REQUIRED_REVIEW_SURFACES:
        if surface not in review_surfaces:
            issues.append(("MISSING_REVIEW_SURFACE", surface))

    artifact_support = normalize_str_list(present_surfaces.get("artifact_support"), "artifact_support")
    for surface in REQUIRED_ARTIFACT_SUPPORT:
        if surface not in artifact_support:
            issues.append(("MISSING_ARTIFACT_SUPPORT_SURFACE", surface))

    cross_route_support = normalize_str_list(
        present_surfaces.get("cross_route_support"), "cross_route_support"
    )
    for surface in REQUIRED_CROSS_ROUTE_SUPPORT:
        if surface not in cross_route_support:
            issues.append(("MISSING_CROSS_ROUTE_SURFACE", surface))

    fixdep_support = normalize_str_list(present_surfaces.get("fixdep_support"), "fixdep_support")
    for surface in REQUIRED_FIXDEP_SUPPORT:
        if surface not in fixdep_support:
            issues.append(("MISSING_FIXDEP_SUPPORT_SURFACE", surface))

    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if repo_reality_gaps != []:
        issues.append(("NONEMPTY_REPO_REALITY_GAPS", json.dumps(repo_reality_gaps, sort_keys=True)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_SHARED_TOOLING_CHECKERS=fail")
    for code, value in issues:
        print(f"{code}={value}")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(
        resolve_path(root, PHASE2_TOOL_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {
                    "checkers": list(REQUIRED_MANIFEST_CHECKERS),
                    "review_surfaces": list(REQUIRED_REVIEW_SURFACES),
                    "artifact_support": list(REQUIRED_ARTIFACT_SUPPORT),
                    "cross_route_support": list(REQUIRED_CROSS_ROUTE_SUPPORT),
                    "fixdep_support": list(REQUIRED_FIXDEP_SUPPORT),
                },
                "repo_reality_gaps": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_shared_tooling_checkers_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST=fail")
            print(f"baseline_issues={issues}")
            return 1

        closure_path = resolve_path(root, PHASE2_CLOSURE)
        manifest_path = resolve_path(root, PHASE2_TOOL_MANIFEST)

        closure_text = read_text(closure_path)
        missing_marker = REQUIRED_CLOSURE_MARKERS[1]
        write_text(closure_path, closure_text.replace(missing_marker + "\n", "", 1))
        issues = collect_issues(root)
        if ("MISSING_CLOSURE_MARKER", missing_marker) not in issues:
            print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST=fail")
            print(f"missing_marker_case={issues}")
            return 1

        build_sample_root(root)
        closure_text = read_text(closure_path)
        drifted = closure_text.replace(
            "PHASE2_SHARED_TOOLING_CHECKERS=" + ",".join(EXPECTED_SHARED_TOOLING_CHECKERS),
            "PHASE2_SHARED_TOOLING_CHECKERS="
            + ",".join(
                EXPECTED_SHARED_TOOLING_CHECKERS[:-1]
                + ("python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",)
            ),
            1,
        )
        write_text(closure_path, drifted)
        issues = collect_issues(root)
        if not any(code == "SHARED_TOOLING_CHECKER_LINE_DRIFT" for code, _ in issues):
            print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST=fail")
            print(f"checker_drift_case={issues}")
            return 1

        build_sample_root(root)
        manifest = read_manifest(manifest_path)
        manifest["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-cross.py")
        write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        if ("MISSING_MANIFEST_CHECKER", "scripts/zigux/check-phase2-cross.py") not in issues:
            print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST=fail")
            print(f"missing_manifest_checker_case={issues}")
            return 1

        build_sample_root(root)
        manifest = read_manifest(manifest_path)
        manifest["repo_reality_gaps"] = ["gap"]
        write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        if ("NONEMPTY_REPO_REALITY_GAPS", json.dumps(["gap"])) not in issues:
            print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST=fail")
            print(f"repo_gaps_case={issues}")
            return 1

    print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST=pass")
    print("PHASE2_SHARED_TOOLING_CHECKERS_SELF_TEST_CASE_COUNT=4")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for replay validation.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test suite.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SHARED_TOOLING_CHECKERS=pass")
    print(f"PHASE2_SHARED_TOOLING_CHECKERS_COUNT={len(EXPECTED_SHARED_TOOLING_CHECKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
