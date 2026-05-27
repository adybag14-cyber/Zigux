#!/usr/bin/env python3
"""Guard the current Phase 2 scripts-root reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent

SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")
MAKEFILE = Path("zigux/Makefile")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

SCRIPTS_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master`",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_MARKERS = (
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "helper-local kconfig allconfig",
    "kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

THIRD_PARTY_MARKERS = (
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": [
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    ],
}

REQUIRED_TOOL_MANIFEST_STRINGS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)

REQUIRED_ARTIFACT_MANIFEST_STRINGS = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "text",
    "json",
    "bytes",
)


def read_text(root: Path, path: Path) -> str:
    target = root / path
    try:
        return target.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {target}") from exc


def write_text(root: Path, path: Path, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def read_json(root: Path, path: Path) -> object:
    return json.loads(read_text(root, path))


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        found: set[str] = set()
        for item in value:
            found.update(collect_strings(item))
        return found
    if isinstance(value, dict):
        found: set[str] = set()
        for item in value.values():
            found.update(collect_strings(item))
        return found
    return set()


def missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def exact_line_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    counts = {marker: 0 for marker in markers}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line in counts:
            counts[line] += 1
    return [(code, f"{count}::{marker}") for marker, count in counts.items() if count != 1]


def policy_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", type(payload).__name__)]
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    if payload.get("channel") != EXPECTED_POLICY["channel"]:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != EXPECTED_POLICY["minimum_version"]:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(payload.get("minimum_version"))))
    upgrade = payload.get("upgrade_policy")
    if not isinstance(upgrade, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade).__name__)]
    if upgrade.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(("POLICY_REQUIRED_ROUTES_MISMATCH", repr(upgrade.get("required_make_routes"))))
    return issues


def required_string_issues(strings: set[str], required: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, item) for item in required if item not in strings]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    scripts_text = read_text(root, SCRIPTS_README)
    bootstrap_text = read_text(root, BOOTSTRAP_NOTES)
    closure_text = read_text(root, PHASE2_CLOSURE)
    review_text = read_text(root, REVIEW_CHECKLIST)
    tests_text = read_text(root, TESTS_README)
    third_party_text = read_text(root, THIRD_PARTY_README)
    makefile_text = read_text(root, MAKEFILE)

    tool_manifest = read_json(root, TOOL_MANIFEST)
    artifact_manifest = read_json(root, ARTIFACT_MANIFEST)
    policy = read_json(root, TOOLCHAIN_POLICY)

    issues: list[tuple[str, str]] = []
    issues.extend(missing_markers(scripts_text, SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(missing_markers(bootstrap_text, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(missing_markers(closure_text, CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS"))
    issues.extend(missing_markers(review_text, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(missing_markers(tests_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(missing_markers(third_party_text, THIRD_PARTY_MARKERS, "MISSING_THIRD_PARTY_MARKERS"))
    issues.extend(exact_line_issues(makefile_text, MAKEFILE_LINES, "MAKEFILE_LINE_COUNT_MISMATCH"))
    issues.extend(policy_issues(policy))
    issues.extend(required_string_issues(collect_strings(tool_manifest), REQUIRED_TOOL_MANIFEST_STRINGS, "MISSING_TOOL_MANIFEST_STRINGS"))
    issues.extend(required_string_issues(collect_strings(artifact_manifest), REQUIRED_ARTIFACT_MANIFEST_STRINGS, "MISSING_ARTIFACT_MANIFEST_STRINGS"))
    if isinstance(tool_manifest, dict) and tool_manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_TOOL_MANIFEST_GAPS", json.dumps(tool_manifest.get("repo_reality_gaps"), sort_keys=True)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)
    print("PHASE2_SCRIPTS_README_CURRENT_PACKET=fail")
    for code, details in grouped.items():
        print(f"{code}_START")
        for detail in details:
            print(detail)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root, SCRIPTS_README, "\n".join(SCRIPTS_MARKERS) + "\n")
    write_text(root, BOOTSTRAP_NOTES, "\n".join(BOOTSTRAP_MARKERS) + "\n")
    write_text(root, PHASE2_CLOSURE, "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(root, REVIEW_CHECKLIST, "\n".join(REVIEW_MARKERS) + "\n")
    write_text(root, TESTS_README, "\n".join(TESTS_MARKERS) + "\n")
    write_text(root, THIRD_PARTY_README, "\n".join(THIRD_PARTY_MARKERS) + "\n")
    write_text(root, MAKEFILE, "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        root,
        TOOLCHAIN_POLICY,
        json.dumps(
            {
                "phase": EXPECTED_POLICY["phase"],
                "channel": EXPECTED_POLICY["channel"],
                "minimum_version": EXPECTED_POLICY["minimum_version"],
                "archive_sha256": {"x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_POLICY["archive_target_scope"],
                    "required_make_routes": EXPECTED_POLICY["required_make_routes"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "repo_reality_gaps": [],
                "present_surfaces": {"all": list(REQUIRED_TOOL_MANIFEST_STRINGS)},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_text(
        root,
        ARTIFACT_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "tooling": {
                    "primary": ["scripts/zigux/artifact_diff.py"],
                    "consumers": ["scripts/zigux/check-kconfig-bridge.py", "scripts/zigux/check-fixdep-diff.py"],
                    "checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],
                    "supported_modes": ["text", "json", "bytes"],
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="lane25_scripts_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        if collect_issues(root):
            raise SystemExit(f"sample root should pass: {collect_issues(root)}")

        write_text(root, SCRIPTS_README, read_text(root, SCRIPTS_README).replace(SCRIPTS_MARKERS[0], "", 1))
        issues = collect_issues(root)
        if ("MISSING_SCRIPTS_MARKERS", SCRIPTS_MARKERS[0]) not in issues:
            raise SystemExit(f"expected missing scripts marker failure: {issues}")

        build_sample_root(root)
        write_text(root, MAKEFILE, read_text(root, MAKEFILE) + MAKEFILE_LINES[0] + "\n")
        issues = collect_issues(root)
        if ("MAKEFILE_LINE_COUNT_MISMATCH", f"2::{MAKEFILE_LINES[0]}") not in issues:
            raise SystemExit(f"expected duplicate makefile line failure: {issues}")

        build_sample_root(root)
        payload = read_json(root, TOOLCHAIN_POLICY)
        if not isinstance(payload, dict):
            raise SystemExit("sample policy should be a dict")
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_text(root, TOOLCHAIN_POLICY, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        if not any(code == "POLICY_REQUIRED_ROUTES_MISMATCH" for code, _ in issues):
            raise SystemExit(f"expected policy route mismatch: {issues}")

        build_sample_root(root)
        payload = read_json(root, TOOL_MANIFEST)
        if not isinstance(payload, dict):
            raise SystemExit("sample manifest should be a dict")
        payload["repo_reality_gaps"] = ["gap"]
        write_text(root, TOOL_MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        if ("NONEMPTY_TOOL_MANIFEST_GAPS", json.dumps(["gap"])) not in issues:
            raise SystemExit(f"expected nonempty manifest gap failure: {issues}")

        build_sample_root(root)
        payload = read_json(root, ARTIFACT_MANIFEST)
        if not isinstance(payload, dict):
            raise SystemExit("sample artifact manifest should be a dict")
        payload["tooling"]["supported_modes"] = ["text", "json"]
        write_text(root, ARTIFACT_MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        if ("MISSING_ARTIFACT_MANIFEST_STRINGS", "bytes") not in issues:
            raise SystemExit(f"expected artifact manifest mode failure: {issues}")

    print("PHASE2_SCRIPTS_README_CURRENT_PACKET_SELF_TEST=pass")
    print("PHASE2_SCRIPTS_README_CURRENT_PACKET_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_SCRIPTS_README_CURRENT_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_README_CURRENT_PACKET=pass")
    print(f"PHASE2_SCRIPTS_README_CURRENT_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_CURRENT_PACKET_COMPANION_MARKER_COUNT={len(BOOTSTRAP_MARKERS) + len(CLOSURE_MARKERS) + len(REVIEW_MARKERS) + len(TESTS_MARKERS) + len(THIRD_PARTY_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_CURRENT_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_SCRIPTS_README_CURRENT_PACKET_TOOL_MANIFEST_STRING_COUNT={len(REQUIRED_TOOL_MANIFEST_STRINGS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
