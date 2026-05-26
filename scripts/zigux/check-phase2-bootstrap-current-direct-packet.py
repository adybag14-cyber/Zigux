#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_CHANNEL = "0.17.0-dev.87+9b177a7d2"
REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

POLICY_MARKER = (
    "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel "
    "`0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits archive "
    "digests to `x86_64-linux`, and names `phase2-toolchain`, `phase2-tools`, "
    "`phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and "
    "`phase2-validate` as the required Linux-style make routes when those routes are "
    "rematerialized."
)

REQUIRED_SECTION_MARKERS = (
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
    "`scripts/zigux/artifact_diff.py` is directly readable on current `master` and keeps the shipped `text`, `json`, `bytes`, and legacy `sha256`-alias comparison surfaces explicit beneath the fixture-backed artifact-support packet already consumed by the current kconfig and fixdep checks.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, local-first archive workflow, archive-verification, staged repo-local archive helper contract, staged archive helper selftest, third_party README contract, installer, toolchain-pinning, pin-scope, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, primary artifact-diff helper, dedicated genksyms selftest-alignment guard, dedicated kconfig allconfig helper guard, genksyms bridge, kconfig bridge, fixdep governance and parity packet, and make-wrapper-backed `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` route replays instead of leaving the returned Phase 2 packet implicit beside the shipped CI path.",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` plus restored `zigux/tests/fixtures/genksyms_bridge/` manifest and process-output roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, tool-manifest, fixture-backed artifact-support, primary artifact-diff helper, genksyms, fixdep, and bridge packet reviewable without widening back into older validator-first claims.",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "Within that live kconfig roster, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` now records the full sixteen-mode `conf_bridge` packet, including the explicit empty `allmodconfig` `allconfig` override packet beside the `randconfig` override packet and the dedicated `randconfig_env_packet`, so reminder surfaces should mirror the current manifest-backed bridge evidence instead of the older narrower override story.",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
)

EXACT_COUNT_MARKERS = (
    "## Current direct packet",
    "`scripts/zigux/artifact_diff.py` is directly readable on current `master` and keeps the shipped `text`, `json`, `bytes`, and legacy `sha256`-alias comparison surfaces explicit beneath the fixture-backed artifact-support packet already consumed by the current kconfig and fixdep checks.",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
)

FORBIDDEN_SECTION_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain",
    "Keep future Phase 2 follow-up inside one current packet surface at a time",
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def extract_current_direct_packet(text: str) -> str:
    start = "## Current direct packet\n"
    end = "\n## Current repo-reality gaps\n"
    if start not in text or end not in text:
        raise SystemExit(f"required note section markers missing: {PHASE2_NOTES}")
    after_start = text.split(start, 1)[1]
    return after_start.split(end, 1)[0]


def load_required_make_routes(root: Path) -> tuple[str, ...]:
    policy = read_json_dict(root / TOOLCHAIN_POLICY)
    if policy.get("channel") != ARCHIVE_CHANNEL:
        raise SystemExit(f"unexpected toolchain channel in required file: {root / TOOLCHAIN_POLICY}")
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / TOOLCHAIN_POLICY}")
    archive_scope = upgrade_policy.get("archive_target_scope")
    if archive_scope != [ARCHIVE_TARGET]:
        raise SystemExit(f"unexpected archive_target_scope in required file: {root / TOOLCHAIN_POLICY}")
    routes = upgrade_policy.get("required_make_routes")
    if routes != list(REQUIRED_ROUTES):
        raise SystemExit(f"unexpected required_make_routes in required file: {root / TOOLCHAIN_POLICY}")
    return tuple(REQUIRED_ROUTES)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    note_text = read_text(root / PHASE2_NOTES)
    direct_packet = extract_current_direct_packet(note_text)
    issues: list[tuple[str, str]] = []

    load_required_make_routes(root)
    if POLICY_MARKER not in direct_packet:
        issues.append(("MISSING_POLICY_MARKER", POLICY_MARKER))

    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in direct_packet:
            issues.append(("MISSING_SECTION_MARKER", marker))

    for marker in EXACT_COUNT_MARKERS:
        haystack = note_text if marker == "## Current direct packet" else direct_packet
        count = haystack.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_SECTION_MARKER", f"{count}::{marker}"))

    for route in load_required_make_routes(root):
        route_marker = f"`make -C zigux {route}`"
        if route_marker not in direct_packet:
            issues.append(("MISSING_ROUTE_MARKER", route_marker))

    if "`make -C zigux phase2`" not in direct_packet:
        issues.append(("MISSING_ROUTE_MARKER", "`make -C zigux phase2`"))

    for marker in FORBIDDEN_SECTION_MARKERS:
        if marker in direct_packet:
            issues.append(("FORBIDDEN_SECTION_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    sample_text = (
        "# Phase 2 Toolchain Bootstrap Notes\n\n"
        "This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.\n\n"
        "## Current direct packet\n\n"
        f"- {POLICY_MARKER}\n"
        "- `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are the current shipped Phase 2 reminder, parity, archive-staging, and alignment guards visible on `master`.\n"
        + "\n".join(f"- {marker}" for marker in REQUIRED_SECTION_MARKERS)
        + "\n\n## Current repo-reality gaps\n\n"
        "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.\n"
        "- Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.\n\n"
        "## Follow-through\n\n"
        "- Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.\n"
    )
    write_text(root / PHASE2_NOTES, sample_text)
    write_text(
        root / TOOLCHAIN_POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": ARCHIVE_CHANNEL,
                "minimum_version": ARCHIVE_CHANNEL,
                "archive_sha256": {ARCHIVE_TARGET: "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [ARCHIVE_TARGET],
                    "required_make_routes": list(REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    if root.exists():
        for child in root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    build_self_test_root(root)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_current_direct_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        note_path = root / PHASE2_NOTES
        for marker in REQUIRED_SECTION_MARKERS[:4]:
            build_self_test_root(root)
            note_path.write_text(replace_once(read_text(note_path), marker), encoding="utf-8")
            assert ("MISSING_SECTION_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        note_path.write_text(replace_once(read_text(note_path), "`make -C zigux phase2-cross`"), encoding="utf-8")
        assert ("MISSING_ROUTE_MARKER", "`make -C zigux phase2-cross`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        note_path.write_text(read_text(note_path).replace("## Current direct packet\n", "## Current direct packet\n## Current direct packet\n", 1), encoding="utf-8")
        assert ("EXACT_COUNT_SECTION_MARKER", "2::## Current direct packet") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        note_path.write_text(read_text(note_path).replace("## Current repo-reality gaps\n", ""), encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required note section markers missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing section boundary did not abort")

        build_self_test_root(root)
        policy_path = root / TOOLCHAIN_POLICY
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unexpected archive_target_scope" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid policy did not abort")

    print("PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap note current-direct-packet section aligned with the live route and reminder packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal current-like sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET_MARKER_COUNT={len(REQUIRED_SECTION_MARKERS) + 1}")
    print(f"PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET_EXACT_COUNT_MARKER_COUNT={len(EXACT_COUNT_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_CURRENT_DIRECT_PACKET_REQUIRED_ROUTE_COUNT={len(REQUIRED_ROUTES) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
