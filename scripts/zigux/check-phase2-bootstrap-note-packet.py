#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_CHANNEL = "0.17.0-dev.87+9b177a7d2"
ARCHIVE_PATH = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"

REQUIRED_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "## Current direct packet",
    "## Current repo-reality gaps",
    "## Follow-through",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are the current shipped Phase 2 reminder, parity, archive-staging, and alignment guards visible on `master`.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    f"`third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive {ARCHIVE_PATH} --archive-target {ARCHIVE_TARGET}` replay contract explicit beside the policy-driven toolchain packet.",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
)

EXACT_COUNT_MARKERS = (
    "The rematerialized make-wrapper packet is directly readable on current `master` through",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

FORBIDDEN_MARKERS = ("historical-only evidence",)

REQUIRED_MANIFEST_SURFACES = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json_dict(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


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


def load_required_make_routes(root: Path) -> tuple[str, ...]:
    policy = read_json_dict(root / TOOLCHAIN_POLICY)
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / TOOLCHAIN_POLICY}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {root / TOOLCHAIN_POLICY}")
    normalized: list[str] = []
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes entry in required file: {root / TOOLCHAIN_POLICY}")
        normalized.append(route.strip())
    return tuple(normalized)


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    note_text = read_text(root / PHASE2_NOTES)
    policy = read_json_dict(root / TOOLCHAIN_POLICY)
    manifest = read_json_dict(root / TOOL_MANIFEST)
    issues: list[tuple[str, str]] = []

    if policy.get("channel") != ARCHIVE_CHANNEL:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(policy.get("channel"))))
    archive_scope = policy.get("upgrade_policy", {}).get("archive_target_scope") if isinstance(policy.get("upgrade_policy"), dict) else None
    if archive_scope != [ARCHIVE_TARGET]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(archive_scope)))

    for marker in REQUIRED_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))

    for marker in EXACT_COUNT_MARKERS:
        count = count_exact_occurrences(note_text, marker)
        if count != 1:
            issues.append(("EXACT_COUNT_NOTE_MARKER", f"{count}::{marker}"))

    for marker in FORBIDDEN_MARKERS:
        if marker in note_text:
            issues.append(("FORBIDDEN_NOTE_MARKER", marker))

    for route in load_required_make_routes(root):
        route_marker = f"`make -C zigux {route}`"
        if route_marker not in note_text:
            issues.append(("MISSING_REQUIRED_ROUTE_MARKER", route_marker))

    if "`make -C zigux phase2`" not in note_text:
        issues.append(("MISSING_REQUIRED_ROUTE_MARKER", "`make -C zigux phase2`"))

    manifest_strings = collect_strings(manifest)
    for surface in REQUIRED_MANIFEST_SURFACES:
        if surface not in manifest_strings:
            issues.append(("MISSING_MANIFEST_SURFACE", surface))
        marker = f"`{surface}`"
        if marker not in note_text:
            issues.append(("MISSING_NOTE_SURFACE_MARKER", marker))

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_NOTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    routes = (
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    )
    policy_payload = {
        "phase": "Phase 2",
        "channel": ARCHIVE_CHANNEL,
        "minimum_version": ARCHIVE_CHANNEL,
        "archive_sha256": {ARCHIVE_TARGET: "3" * 64},
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": [ARCHIVE_TARGET],
            "required_make_routes": list(routes),
        },
    }
    manifest_payload = {
        "phase": "Phase 2",
        "present_surfaces": {"all": list(REQUIRED_MANIFEST_SURFACES)},
        "repo_reality_gaps": [],
    }
    note_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "## Current direct packet",
        "",
        f"- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `{ARCHIVE_CHANNEL}`, keeps the minimum version in lockstep, limits archive digests to `{ARCHIVE_TARGET}`, and names `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` as the required Linux-style make routes when those routes are rematerialized.",
        *[f"- {marker}" for marker in REQUIRED_MARKERS[4:]],
        "- The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
        "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` plus restored `zigux/tests/fixtures/genksyms_bridge/` manifest and process-output roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, tool-manifest, fixture-backed artifact-support, primary artifact-diff helper, genksyms, fixdep, and bridge packet reviewable without widening back into older validator-first claims.",
        "- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
        "",
        "## Current repo-reality gaps",
        "",
        "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
        "- Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
        "",
        "## Follow-through",
        "",
        "- Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
        "- Do not widen this note into genksyms parser behavior, conf or confdata bridge semantics, or deeper cross-target execution claims beyond the returned `phase2_cross_targets.json` packet unless current `master` materializes the companion wider surfaces and their reminder checks.",
    ]
    write_text(root / PHASE2_NOTES, "\n".join(note_lines) + "\n")
    write_text(root / TOOLCHAIN_POLICY, json.dumps(policy_payload, indent=2) + "\n")
    write_text(root / TOOL_MANIFEST, json.dumps(manifest_payload, indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_note_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        note_path = root / PHASE2_NOTES
        note_text = read_text(note_path)
        note_path.write_text(replace_once(note_text, REQUIRED_MARKERS[4]), encoding="utf-8")
        assert ("MISSING_NOTE_MARKER", REQUIRED_MARKERS[4]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        note_path = root / PHASE2_NOTES
        note_path.write_text(read_text(note_path) + EXACT_COUNT_MARKERS[0] + "\n", encoding="utf-8")
        assert ("EXACT_COUNT_NOTE_MARKER", f"2::{EXACT_COUNT_MARKERS[0]}") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        note_path = root / PHASE2_NOTES
        note_path.write_text(read_text(note_path) + FORBIDDEN_MARKERS[0] + "\n", encoding="utf-8")
        assert ("FORBIDDEN_NOTE_MARKER", FORBIDDEN_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = root / TOOLCHAIN_POLICY
        payload = json.loads(read_text(policy_path))
        payload["channel"] = "broken"
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        assert ("POLICY_CHANNEL_MISMATCH", repr("broken")) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        note_path = root / PHASE2_NOTES
        note_path.write_text(replace_once(read_text(note_path), "`make -C zigux phase2-cross`"), encoding="utf-8")
        assert ("MISSING_REQUIRED_ROUTE_MARKER", "`make -C zigux phase2-cross`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / TOOL_MANIFEST
        payload = json.loads(read_text(manifest_path))
        payload["present_surfaces"]["all"].remove("scripts/zigux/artifact_diff.py")
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_SURFACE", "scripts/zigux/artifact_diff.py") in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / TOOL_MANIFEST
        payload = json.loads(read_text(manifest_path))
        payload["repo_reality_gaps"] = ["gap"]
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert ("NONEMPTY_MANIFEST_GAPS", "['gap']") in collect_issues(root)
        checks_run += 1

    print("PHASE2_BOOTSTRAP_NOTE_PACKET=self-test-pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 toolchain bootstrap note aligned with the current policy, manifest, and route packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_NOTE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
