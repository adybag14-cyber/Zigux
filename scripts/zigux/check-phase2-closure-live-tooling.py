#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
THIRD_PARTY_README = Path("third_party/README.md")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
MAKEFILE = Path("zigux/Makefile")
CROSS_TARGETS = Path("zigux/tests/fixtures/phase2_cross_targets.json")
GENKSYMS_MANIFEST = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`third_party/README.md`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
)

EXACT_COUNT_CLOSURE_MARKERS = (
    "`PHASE2_CURRENT_GAP_PACKET=`",
)

FORBIDDEN_CLOSURE_MARKERS = (
    "older validator-first claims",
)

REQUIRED_THIRD_PARTY_MARKERS = (
    "# Zigux third-party archives",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate:",
    "phase2: phase2-validate",
)

EXPECTED_TOOLCHAIN_REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

EXPECTED_GENKSYMS_CASES = (
    "minimal",
    "debug_reference_types",
    "long_options",
    "abbreviated_long_options",
    "quiet_overrides_warning",
    "explicit_option_terminator",
    "positional_passthrough",
    "lone_dash_passthrough",
    "dash_prefixed_long_option_arguments_as_data",
    "dash_prefixed_short_option_arguments_as_data",
)

EXPECTED_GENKSYMS_EXPECTED_PACKET = (
    "minimal_expected.json",
    "debug_reference_types_expected.json",
    "long_options_expected.json",
    "abbreviated_long_options_expected.json",
    "quiet_overrides_warning_expected.json",
    "explicit_option_terminator_expected.json",
    "positional_passthrough_expected.json",
    "lone_dash_passthrough_expected.json",
    "dash_prefixed_long_option_arguments_as_data_expected.json",
    "dash_prefixed_short_option_arguments_as_data_expected.json",
)

EXPECTED_STANDALONE_PROOF_PACKET = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

EXPECTED_PROCESS_OUTPUT_PACKET = (
    "abbreviated_version_expected.json",
    "ambiguous_long_option_expected.json",
    "invalid_option_expected.json",
    "missing_long_dump_types_argument_expected.json",
    "missing_long_reference_argument_expected.json",
    "missing_reference_argument_expected.json",
    "too_many_reference_files_expected.json",
    "unsupported_long_option_expected.json",
    "unexpected_long_help_argument_expected.json",
    "abbreviated_unexpected_long_help_argument_expected.json",
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
        raise SystemExit(f"invalid json: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def resolve_path(root: Path, rel: Path) -> Path:
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


def collect_toolchain_policy_issues(policy: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(policy, dict):
        return [("INVALID_TOOLCHAIN_POLICY", "policy-root-not-object")]
    if policy.get("channel") != "0.17.0-dev.87+9b177a7d2":
        issues.append(("INVALID_TOOLCHAIN_POLICY", f"channel::{policy.get('channel')}"))
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_TOOLCHAIN_POLICY", "upgrade_policy-not-object")]
    if upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
        issues.append(
            ("INVALID_TOOLCHAIN_POLICY", f"archive_target_scope::{upgrade_policy.get('archive_target_scope')}")
        )
    if tuple(upgrade_policy.get("required_make_routes", ())) != EXPECTED_TOOLCHAIN_REQUIRED_ROUTES:
        issues.append(
            ("INVALID_TOOLCHAIN_POLICY", f"required_make_routes::{upgrade_policy.get('required_make_routes')}")
        )
    return issues


def collect_cross_target_issues(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_CROSS_TARGETS", "cross-root-not-object")]
    if payload.get("route") != "make -C zigux phase2-cross":
        issues.append(("INVALID_CROSS_TARGETS", f"route::{payload.get('route')}"))
    if payload.get("archive_target_scope") != ["x86_64-linux"]:
        issues.append(("INVALID_CROSS_TARGETS", f"archive_target_scope::{payload.get('archive_target_scope')}"))
    targets = payload.get("cross_targets")
    if not isinstance(targets, list):
        return issues + [("INVALID_CROSS_TARGETS", "cross_targets-not-list")]
    expected = {
        ("x86_64-linux", "pinned bootstrap archive", "archive_required", "make -C zigux phase2-cross"),
        ("aarch64-linux", "route contract only", "route_contract_only", "make -C zigux phase2-cross"),
    }
    found = {
        (
            entry.get("target"),
            entry.get("review_status"),
            entry.get("validation_mode"),
            entry.get("route"),
        )
        for entry in targets
        if isinstance(entry, dict)
    }
    if found != expected:
        issues.append(("INVALID_CROSS_TARGETS", f"cross_targets::{sorted(found)}"))
    return issues


def collect_genksyms_manifest_issues(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_GENKSYMS_MANIFEST", "manifest-root-not-object")]
    if payload.get("case_count") != len(EXPECTED_GENKSYMS_CASES):
        issues.append(("INVALID_GENKSYMS_MANIFEST", f"case_count::{payload.get('case_count')}"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or tuple(cases) != EXPECTED_GENKSYMS_CASES:
        issues.append(("INVALID_GENKSYMS_MANIFEST", f"cases::{cases}"))
    expected_packet = payload.get("bridge_expected_packet")
    if not isinstance(expected_packet, list) or tuple(expected_packet) != EXPECTED_GENKSYMS_EXPECTED_PACKET:
        issues.append(("INVALID_GENKSYMS_MANIFEST", f"bridge_expected_packet::{expected_packet}"))
    proof_packet = payload.get("standalone_proof_packet")
    if not isinstance(proof_packet, list) or tuple(proof_packet) != EXPECTED_STANDALONE_PROOF_PACKET:
        issues.append(("INVALID_GENKSYMS_MANIFEST", f"standalone_proof_packet::{proof_packet}"))
    process_packet = payload.get("process_output_packet")
    if not isinstance(process_packet, list) or tuple(process_packet) != EXPECTED_PROCESS_OUTPUT_PACKET:
        issues.append(("INVALID_GENKSYMS_MANIFEST", f"process_output_packet::{process_packet}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    third_party_text = read_text(resolve_path(root, THIRD_PARTY_README))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    policy = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    cross_targets = read_json(resolve_path(root, CROSS_TARGETS))
    genksyms_manifest = read_json(resolve_path(root, GENKSYMS_MANIFEST))

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(closure_text, REQUIRED_CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS"))
    issues.extend(
        collect_exact_count_markers(closure_text, EXACT_COUNT_CLOSURE_MARKERS, "EXACT_COUNT_CLOSURE_MARKERS")
    )
    issues.extend(collect_forbidden_markers(closure_text, FORBIDDEN_CLOSURE_MARKERS, "FORBIDDEN_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(third_party_text, REQUIRED_THIRD_PARTY_MARKERS, "MISSING_THIRD_PARTY_MARKERS"))
    issues.extend(collect_missing_markers(makefile_text, REQUIRED_MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKERS"))
    issues.extend(collect_toolchain_policy_issues(policy))
    issues.extend(collect_cross_target_issues(cross_targets))
    issues.extend(collect_genksyms_manifest_issues(genksyms_manifest))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_LIVE_TOOLING=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, THIRD_PARTY_README), "\n".join(REQUIRED_THIRD_PARTY_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")
    write_json(
        resolve_path(root, TOOLCHAIN_POLICY),
        {
            "channel": "0.17.0-dev.87+9b177a7d2",
            "upgrade_policy": {
                "archive_target_scope": ["x86_64-linux"],
                "required_make_routes": list(EXPECTED_TOOLCHAIN_REQUIRED_ROUTES),
            },
        },
    )
    write_json(
        resolve_path(root, CROSS_TARGETS),
        {
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
    )
    write_json(
        resolve_path(root, GENKSYMS_MANIFEST),
        {
            "case_count": len(EXPECTED_GENKSYMS_CASES),
            "cases": list(EXPECTED_GENKSYMS_CASES),
            "bridge_expected_packet": list(EXPECTED_GENKSYMS_EXPECTED_PACKET),
            "standalone_proof_packet": list(EXPECTED_STANDALONE_PROOF_PACKET),
            "process_output_packet": list(EXPECTED_PROCESS_OUTPUT_PACKET),
        },
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_CLOSURE_MARKERS)
        + len(EXACT_COUNT_CLOSURE_MARKERS)
        + len(FORBIDDEN_CLOSURE_MARKERS)
        + len(REQUIRED_THIRD_PARTY_MARKERS)
        + len(REQUIRED_MAKEFILE_MARKERS)
        + 6
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_live_tooling_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            write_text(path, replace_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_CLOSURE_MARKERS", marker) in issues
            checks_run += 1

        for marker in EXACT_COUNT_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            write_text(path, read_text(path) + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_CLOSURE_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for marker in FORBIDDEN_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            write_text(path, read_text(path) + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_CLOSURE_MARKERS", marker) in issues
            checks_run += 1

        for marker in REQUIRED_THIRD_PARTY_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, THIRD_PARTY_README)
            write_text(path, replace_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_THIRD_PARTY_MARKERS", marker) in issues
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            write_text(path, replace_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        write_json(policy_path, {"channel": "bad", "upgrade_policy": {"archive_target_scope": [], "required_make_routes": []}})
        issues = collect_issues(root)
        assert ("INVALID_TOOLCHAIN_POLICY", "channel::bad") in issues
        checks_run += 1

        build_self_test_root(root)
        cross_path = resolve_path(root, CROSS_TARGETS)
        write_json(cross_path, {"route": "bad", "archive_target_scope": [], "cross_targets": []})
        issues = collect_issues(root)
        assert any(code == "INVALID_CROSS_TARGETS" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, GENKSYMS_MANIFEST)
        write_json(
            manifest_path,
            {"case_count": 7, "cases": [], "bridge_expected_packet": [], "standalone_proof_packet": [], "process_output_packet": []},
        )
        issues = collect_issues(root)
        assert any(code == "INVALID_GENKSYMS_MANIFEST" for code, _ in issues)
        checks_run += 1

        for rel_path in (PHASE2_CLOSURE, THIRD_PARTY_README, TOOLCHAIN_POLICY):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_CLOSURE_LIVE_TOOLING_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_LIVE_TOOLING_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note aligned to the current live tooling, wrapper, and fixture packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a focused current-like root for replay")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_LIVE_TOOLING=pass")
    print(f"PHASE2_CLOSURE_LIVE_TOOLING_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print("PHASE2_CLOSURE_LIVE_TOOLING_JSON_PACKET_COUNT=3")
    print(f"PHASE2_CLOSURE_LIVE_TOOLING_MAKEFILE_MARKER_COUNT={len(REQUIRED_MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
