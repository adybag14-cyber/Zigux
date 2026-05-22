#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOL_MANIFEST_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

EXPECTED_CROSS_ROUTE_SUPPORT = [
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
]
EXPECTED_POLICY_SURFACES = [
    "scripts/zigux/zig-toolchain-policy.json",
]
EXPECTED_MAKE_WRAPPERS = [
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]
EXPECTED_CROSS_CHECKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
]
EXPECTED_NOTE_MARKERS = [
    "direct cross-route checker",
    "phase2_cross_targets fixture",
]
EXPECTED_CHECKER_MARKERS = [
    '"cross_route_support": (',
    '"scripts/zigux/check-phase2-cross.py",',
    '"scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '"zigux/tests/fixtures/phase2_cross_targets.json",',
    '"scripts/zigux/zig-toolchain-policy.json",',
    '"make -C zigux phase2-cross",',
    '"direct cross-route checker"',
    '"phase2_cross_targets fixture"',
]


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


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def duplicate_strings(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def expect_string_list(payload: object, *, label: str, issues: list[tuple[str, str]]) -> list[str] | None:
    if not isinstance(payload, list):
        issues.append(("INVALID_LIST_FIELD", label))
        return None
    if not all(isinstance(entry, str) for entry in payload):
        issues.append(("INVALID_LIST_ENTRY", label))
        return None
    duplicates = duplicate_strings(payload)
    for duplicate in duplicates:
        issues.append(("DUPLICATE_LIST_ENTRY", f"{label}:{duplicate}"))
    return payload


def collect_checker_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, TOOL_MANIFEST_CHECKER))
    issues: list[tuple[str, str]] = []
    for marker in EXPECTED_CHECKER_MARKERS:
        if marker not in text:
            issues.append(("MISSING_CHECKER_MARKER", marker))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = read_json(resolve_path(root, TOOL_MANIFEST))
    policy = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    cross_targets = read_json(resolve_path(root, CROSS_TARGETS))
    issues: list[tuple[str, str]] = []

    if not isinstance(payload, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", type(payload).__name__))
        return issues

    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            issues.append(("TOP_LEVEL_MISMATCH", key))

    if payload.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps"))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("MISSING_PRESENT_SURFACES", "present_surfaces"))
        return issues

    cross_support = expect_string_list(
        present_surfaces.get("cross_route_support"),
        label="cross_route_support",
        issues=issues,
    )
    if cross_support is not None and cross_support != EXPECTED_CROSS_ROUTE_SUPPORT:
        issues.append(("LIST_MISMATCH", "cross_route_support"))

    policy_surfaces = expect_string_list(
        present_surfaces.get("policy"),
        label="policy",
        issues=issues,
    )
    if policy_surfaces is not None and policy_surfaces != EXPECTED_POLICY_SURFACES:
        issues.append(("LIST_MISMATCH", "policy"))

    make_wrappers = expect_string_list(
        present_surfaces.get("make_wrappers"),
        label="make_wrappers",
        issues=issues,
    )
    if make_wrappers is not None and make_wrappers != EXPECTED_MAKE_WRAPPERS:
        issues.append(("LIST_MISMATCH", "make_wrappers"))

    checker_surfaces = expect_string_list(
        present_surfaces.get("checkers"),
        label="checkers",
        issues=issues,
    )
    if checker_surfaces is not None:
        for checker in EXPECTED_CROSS_CHECKERS:
            if checker not in checker_surfaces:
                issues.append(("MISSING_CROSS_CHECKER", checker))

    notes = expect_string_list(payload.get("notes"), label="notes", issues=issues)
    if notes is not None:
        for marker in EXPECTED_NOTE_MARKERS:
            if not any(marker in note for note in notes):
                issues.append(("MISSING_NOTE_MARKER", marker))

    if not isinstance(policy, dict):
        issues.append(("INVALID_POLICY_SHAPE", type(policy).__name__))
    else:
        upgrade_policy = policy.get("upgrade_policy")
        if not isinstance(upgrade_policy, dict):
            issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        else:
            archive_target_scope = upgrade_policy.get("archive_target_scope")
            if not isinstance(archive_target_scope, list) or not archive_target_scope:
                issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))

    if not isinstance(cross_targets, dict):
        issues.append(("INVALID_CROSS_TARGETS_SHAPE", type(cross_targets).__name__))
    else:
        entries = cross_targets.get("cross_targets")
        if not isinstance(entries, list) or not entries:
            issues.append(("INVALID_CROSS_TARGETS_FIELD", "cross_targets"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, TOOL_MANIFEST_CHECKER),
        "\n".join(EXPECTED_CHECKER_MARKERS) + "\n",
    )
    write_text(
        resolve_path(root, TOOL_MANIFEST),
        json.dumps(
            {
                **EXPECTED_TOP_LEVEL,
                "notes": [
                    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option version-side-effect proof, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
                    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
                ],
                "present_surfaces": {
                    "cross_route_support": EXPECTED_CROSS_ROUTE_SUPPORT,
                    "policy": EXPECTED_POLICY_SURFACES,
                    "make_wrappers": EXPECTED_MAKE_WRAPPERS,
                    "checkers": [
                        "scripts/zigux/check-zig-toolchain.py",
                        *EXPECTED_CROSS_CHECKERS,
                    ],
                },
                "repo_reality_gaps": [],
            },
            indent=2,
        )
        + "\n",
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CROSS_TARGETS),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": "make -C zigux phase2-cross",
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": "make -C zigux phase2-cross",
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": "make -C zigux phase2-cross",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(EXPECTED_CHECKER_MARKERS)
        + len(EXPECTED_NOTE_MARKERS)
        + 11
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_checker_issues(root) == []
        assert collect_manifest_issues(root) == []
        checks_run += 1

        for marker in EXPECTED_CHECKER_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TOOL_MANIFEST_CHECKER)
            path.write_text(remove_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_CHECKER_MARKER", marker) in collect_checker_issues(root)
            checks_run += 1

        for marker in EXPECTED_NOTE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["notes"] = [note for note in payload["notes"] if marker not in note]
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_NOTE_MARKER", marker) in collect_manifest_issues(root)
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["cross_route_support"] = ["scripts/zigux/check-phase2-cross.py"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("LIST_MISMATCH", "cross_route_support") in collect_manifest_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["policy"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_manifest_issues(root)
        assert ("LIST_MISMATCH", "policy") in issues or ("INVALID_LIST_FIELD", "policy") in issues
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["make_wrappers"][4] = "make -C zigux phase2-tools"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("LIST_MISMATCH", "make_wrappers") in collect_manifest_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-cross-selftest-alignment.py")
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_CROSS_CHECKER", "scripts/zigux/check-phase2-cross-selftest-alignment.py") in collect_manifest_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["repo_reality_gaps"] = ["unexpected-gap"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps") in collect_manifest_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        del payload["upgrade_policy"]["archive_target_scope"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "archive_target_scope") in collect_manifest_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGETS_FIELD", "cross_targets") in collect_manifest_issues(root)
        checks_run += 1

        for path in (TOOL_MANIFEST_CHECKER, TOOL_MANIFEST, TOOLCHAIN_POLICY, CROSS_TARGETS):
            build_sample_root(root)
            resolve_path(root, path).unlink()
            try:
                if path == TOOL_MANIFEST_CHECKER:
                    collect_checker_issues(root)
                else:
                    collect_manifest_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 direct cross-route packet aligned inside the Phase 2 tool manifest surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    issues = collect_checker_issues(root)
    issues.extend(collect_manifest_issues(root))
    if issues:
        return emit_issues(issues)

    policy = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    assert isinstance(policy, dict)
    upgrade_policy = policy["upgrade_policy"]
    assert isinstance(upgrade_policy, dict)
    archive_target_scope = upgrade_policy["archive_target_scope"]
    assert isinstance(archive_target_scope, list)

    cross_targets = read_json(resolve_path(root, CROSS_TARGETS))
    assert isinstance(cross_targets, dict)
    target_entries = cross_targets["cross_targets"]
    assert isinstance(target_entries, list)

    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_CHECKER_MARKER_COUNT={len(EXPECTED_CHECKER_MARKERS)}")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_ARCHIVE_SCOPE_COUNT={len(archive_target_scope)}")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_TARGET_COUNT={len(target_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
