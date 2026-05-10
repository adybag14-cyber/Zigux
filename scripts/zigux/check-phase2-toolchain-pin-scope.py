#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
NOTES_DOC = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
README = ROOT / "scripts" / "zigux" / "README.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
MAKEFILE = ROOT / "zigux" / "Makefile"

EXPECTED_PIN_TARGETS = ["x86_64-linux"]
EXPECTED_APPROVAL_POLICY = {
    "shared_phase2_checklist_ack_required": True,
    "fresh_bootstrap_runner_evidence_required": True,
    "separate_cross_target_expansion_approval_required": True,
}
ARCHIVE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

NOTE_STATIC_MARKERS = [
    "the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
    "the Linux-style `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the docs-root summary, the shared validators, the closure note, and the shared review checklist",
]

NOTE_APPROVAL_MARKERS = [
    "`scripts/zigux/zig-toolchain-policy.json` now also keeps the Phase 2 pin-change approval rule machine-checkable.",
    "pinned toolchain changes require explicit shared Phase 2 checklist acknowledgement and fresh bootstrap-runner evidence before merge.",
    "widening the bootstrap archive beyond `x86_64-linux` still needs separate approval instead of piggybacking on the three-target compile matrix.",
]

README_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "make -C zigux phase2-toolchain",
    "x86_64-linux bootstrap host target",
    "cross-target compile matrix stays a separate Phase 2 surface",
]

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "pinned Zig toolchain",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

TESTS_README_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "pinned `x86_64-linux` bootstrap archive note",
    "bounded three-target compile matrix",
    "kbuild-facing replay surface",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 2 toolchain packet",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

CLOSURE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1",
    "PHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json",
    "make -C zigux phase2-toolchain",
]

PHASE2_VALIDATOR_MARKERS = [
    '"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"',
    '"PHASE2_TOOLCHAIN_PIN_SCOPE=pass"',
]

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    'CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"',
    "PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [",
    '"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",',
    '"PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",',
    "PHASE2_MAKEFILE_RUN_COUNTS = {",
    '"scripts/zigux/check-zig-toolchain.py": 1,',
    '"scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,',
    '"scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,',
    "issues.extend(validate_exact_makefile_runs(makefile_text))",
]

MAKEFILE_MARKERS = [
    "phase2-toolchain:",
    "phase2-validate: phase2-toolchain",
    "phase2-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "phase2-cross:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/install-zig.py --self-test": 1,
    "python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "python3 scripts/zigux/check-zig-toolchain.py": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
}

EXACT_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-zig-toolchain.py": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
}

WORKFLOW_FORBIDDEN_FRAGMENTS = [
    "scripts/zigux/install-zig.py --system",
    "scripts/zigux/install-zig.py --arch",
    "scripts/zigux/check-zig-toolchain.py --system",
    "scripts/zigux/check-zig-toolchain.py --arch",
]

TOOLCHAIN_TARGET_NAME = "phase2-toolchain"
PHASE2_VALIDATE_TARGET_NAME = "phase2-validate"
PHASE2_TOOLS_TARGET_NAME = "phase2-tools"
PHASE2_KCONFIG_TARGET_NAME = "phase2-kconfig"
PHASE2_CROSS_TARGET_NAME = "phase2-cross"
TOOLCHAIN_TARGET_REQUIRED_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
]
PHASE2_TOOLS_TARGET_REQUIRED_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig",
]
PHASE2_KCONFIG_TARGET_REQUIRED_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
]
PHASE2_CROSS_TARGET_REQUIRED_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
]
REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES = [
    "REPO_LOCAL_ZIG := $(lastword $(sort $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig $(ZIGUX_ROOT)/.zig-toolchain/*/zig.exe $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig.exe)))",
    "ifeq ($(origin ZIG), undefined)",
    "ifneq ($(REPO_LOCAL_ZIG),)",
    "export PATH := $(dir $(REPO_LOCAL_ZIG)):$(PATH)",
    "endif",
    "endif",
    "ZIG ?= $(if $(REPO_LOCAL_ZIG),$(REPO_LOCAL_ZIG),zig)",
]

EXACT_SURFACE_COUNTS = {
    "scripts_readme": {
        "check-phase2-toolchain-pin-scope.py --self-test": 1,
        "make -C zigux phase2-toolchain": 1,
        "x86_64-linux bootstrap host target": 1,
    },
    "docs_root_readme": {
        "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
        "pinned Zig toolchain": 1,
        "make -C zigux phase2-toolchain": 1,
        "make -C zigux phase2-validate": 1,
        "make -C zigux phase2-tools": 1,
        "make -C zigux phase2-kconfig": 1,
        "make -C zigux phase2-cross": 1,
    },
    "tests_readme": {
        "pinned `x86_64-linux` bootstrap archive note": 1,
        "bounded three-target compile matrix": 1,
        "make -C zigux phase2-validate": 1,
        "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset": 1,
    },
    "review_checklist": {
        "if the change touches the shared Phase 2 toolchain packet": 1,
        "python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
        "make -C zigux phase2-validate": 1,
        "make -C zigux phase2-tools": 1,
        "make -C zigux phase2-kconfig": 1,
        "make -C zigux phase2-cross": 1,
    },
    "phase2_closure_doc": {
        "PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1": 1,
        "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
        "PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json": 1,
        "make -C zigux phase2-toolchain": 1,
    },
    "phase2_toolchain_notes": {
        "`scripts/zigux/zig-toolchain-policy.json` now also keeps the Phase 2 pin-change approval rule machine-checkable.": 1,
        "pinned toolchain changes require explicit shared Phase 2 checklist acknowledgement and fresh bootstrap-runner evidence before merge.": 1,
        "widening the bootstrap archive beyond `x86_64-linux` still needs separate approval instead of piggybacking on the three-target compile matrix.": 1,
        "make -C zigux phase2-toolchain": 1,
    },
}


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate_key:{key}")
        payload[key] = value
    return payload


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
        )
    except ValueError as exc:
        raise SystemExit(f"{label}:{exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_policy(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"policy:phase={payload.get('phase')!r}:expected='Phase 2'")

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if not isinstance(channel, str) or not channel:
        issues.append("policy:channel:expected_nonempty_string")
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append("policy:minimum_version:expected_nonempty_string")
    if isinstance(channel, str) and isinstance(minimum_version, str) and channel and minimum_version and channel != minimum_version:
        issues.append(
            "policy:channel_minimum_version_mismatch:"
            f"channel={channel!r}:minimum_version={minimum_version!r}"
        )

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append("policy:archive_sha256:expected_object")
    else:
        keys = list(archive_sha256.keys())
        if keys != EXPECTED_PIN_TARGETS:
            issues.append(f"policy:archive_sha256_keys={keys!r}:expected={EXPECTED_PIN_TARGETS!r}")
        for target_key, digest in archive_sha256.items():
            if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
                issues.append(f"policy:archive_sha256:{target_key}:expected_sha256_hex")

    approval_policy = payload.get("approval_policy")
    if not isinstance(approval_policy, dict):
        issues.append("policy:approval_policy:expected_object")
    else:
        expected_keys = list(EXPECTED_APPROVAL_POLICY.keys())
        keys = list(approval_policy.keys())
        if keys != expected_keys:
            issues.append(f"policy:approval_policy_keys={keys!r}:expected={expected_keys!r}")
        for key, expected in EXPECTED_APPROVAL_POLICY.items():
            actual = approval_policy.get(key)
            if actual != expected:
                issues.append(f"policy:approval_policy:{key}={actual!r}:expected={expected!r}")
    return issues


def validate_phase2_notes(text: str, *, payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    archive_sha256 = payload.get("archive_sha256")

    if isinstance(channel, str) and channel:
        marker = f"- current pinned Zig channel: `{channel}`"
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")
    else:
        issues.append("policy:channel:expected_nonempty_string")

    if isinstance(minimum_version, str) and minimum_version:
        marker = f"- current minimum Zig version: `{minimum_version}`"
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")
    else:
        issues.append("policy:minimum_version:expected_nonempty_string")

    if isinstance(archive_sha256, dict):
        pin_target = EXPECTED_PIN_TARGETS[0]
        target_marker = f"- current pinned bootstrap archive target: `{pin_target}`"
        if target_marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{target_marker}")
        digest = archive_sha256.get(pin_target)
        if isinstance(digest, str):
            digest_marker = f"- current pinned bootstrap archive sha256 (`{pin_target}`): `{digest}`"
            if digest_marker not in text:
                issues.append(f"phase2_toolchain_notes:missing_marker:{digest_marker}")

    for marker in NOTE_STATIC_MARKERS:
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")
    for marker in NOTE_APPROVAL_MARKERS:
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")
    return issues


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    return [f"{label}:missing_marker:{marker}" for marker in markers if marker not in text]


def validate_exact_marker_counts(text: str, *, label: str, checks: dict[str, int]) -> list[str]:
    issues: list[str] = []
    for marker, expected_count in checks.items():
        count = text.count(marker)
        if count != expected_count:
            issues.append(f"{label}:exact_count:{marker}:count={count}:expected={expected_count}")
    return issues


def validate_exact_workflow_runs(text: str, *, payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel:
        issues.append("policy:channel:expected_nonempty_string")
        return issues

    lines = [line.strip() for line in text.splitlines()]
    expected_install = f"python3 scripts/zigux/install-zig.py --channel {channel} --dest .zig-toolchain"
    install_count = sum(1 for line in lines if line == f"run: {expected_install}")
    if install_count != 2:
        issues.append(f"workflow_exact_run:{expected_install}:count={install_count}:expected=2")

    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        count = sum(1 for line in lines if line == f"run: {command}")
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    for fragment in WORKFLOW_FORBIDDEN_FRAGMENTS:
        if fragment in text:
            issues.append(f"workflow_forbidden_fragment:{fragment}")
    return issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_MAKEFILE_RUN_COUNTS.items():
        expected_line = f"cd $(ZIGUX_ROOT) && $(PYTHON) {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def extract_makefile_target_lines(text: str, target_name: str) -> list[str] | None:
    target_header = f"{target_name}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(target_header):
            target_lines: list[str] = []
            for following in lines[index + 1 :]:
                if following.startswith("\t"):
                    target_lines.append(following.strip())
                    continue
                if not following.strip():
                    continue
                break
            return target_lines
    return None


def validate_toolchain_target_scope(text: str) -> list[str]:
    issues: list[str] = []
    toolchain_lines = extract_makefile_target_lines(text, TOOLCHAIN_TARGET_NAME)
    if toolchain_lines is None:
        issues.append(f"makefile_target_missing:{TOOLCHAIN_TARGET_NAME}")
    elif toolchain_lines != TOOLCHAIN_TARGET_REQUIRED_LINES:
        issues.append(
            "makefile_target_scope:"
            f"{TOOLCHAIN_TARGET_NAME}:actual={toolchain_lines!r}:expected={TOOLCHAIN_TARGET_REQUIRED_LINES!r}"
        )

    validate_lines = extract_makefile_target_lines(text, PHASE2_VALIDATE_TARGET_NAME)
    if validate_lines is None:
        issues.append(f"makefile_target_missing:{PHASE2_VALIDATE_TARGET_NAME}")
    else:
        forbidden = [line for line in validate_lines if line in TOOLCHAIN_TARGET_REQUIRED_LINES]
        if forbidden:
            issues.append(
                "makefile_target_scope:"
                f"{PHASE2_VALIDATE_TARGET_NAME}:unexpected_toolchain_lines={forbidden!r}"
            )
    return issues


def validate_repo_local_zig_fallback(text: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    anchor = REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES[0]
    anchors = [index for index, line in enumerate(lines) if line == anchor]
    if len(anchors) != 1:
        issues.append(f"makefile_repo_local_zig_anchor_count:count={len(anchors)}:expected=1")
        return issues

    start = anchors[0]
    actual = lines[start : start + len(REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES)]
    if actual != REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES:
        issues.append(
            "makefile_repo_local_zig_block:"
            f"actual={actual!r}:expected={REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES!r}"
        )
    return issues


def validate_repo_local_zig_make_routes(text: str) -> list[str]:
    issues: list[str] = []
    for target_name, expected_lines in (
        (PHASE2_TOOLS_TARGET_NAME, PHASE2_TOOLS_TARGET_REQUIRED_LINES),
        (PHASE2_KCONFIG_TARGET_NAME, PHASE2_KCONFIG_TARGET_REQUIRED_LINES),
        (PHASE2_CROSS_TARGET_NAME, PHASE2_CROSS_TARGET_REQUIRED_LINES),
    ):
        target_lines = extract_makefile_target_lines(text, target_name)
        if target_lines is None:
            issues.append(f"makefile_target_missing:{target_name}")
            continue
        if target_lines != expected_lines:
            issues.append(
                "makefile_target_scope:"
                f"{target_name}:actual={target_lines!r}:expected={expected_lines!r}"
            )
    return issues


def run_self_test() -> int:
    valid_policy = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858",
        },
        "approval_policy": {
            "shared_phase2_checklist_ack_required": True,
            "fresh_bootstrap_runner_evidence_required": True,
            "separate_cross_target_expansion_approval_required": True,
        },
    }
    assert validate_policy(valid_policy) == []

    valid_notes = "\n".join(
        [
            "- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`",
            "- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`",
            "- current pinned bootstrap archive target: `x86_64-linux`",
            "- current pinned bootstrap archive sha256 (`x86_64-linux`): `a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858`",
            *[f"- {marker}" for marker in NOTE_APPROVAL_MARKERS],
            *[f"- {marker}" for marker in NOTE_STATIC_MARKERS],
        ]
    )
    assert validate_phase2_notes(valid_notes, payload=valid_policy) == []

    valid_scripts_readme = "\n".join(README_MARKERS)
    assert validate_required_markers(valid_scripts_readme, label="scripts_readme", markers=README_MARKERS) == []
    missing_scripts_readme = validate_required_markers(
        valid_scripts_readme.replace("x86_64-linux bootstrap host target", "", 1),
        label="scripts_readme",
        markers=README_MARKERS,
    )
    assert "scripts_readme:missing_marker:x86_64-linux bootstrap host target" in missing_scripts_readme

    valid_docs_root = "\n".join(DOCS_ROOT_MARKERS)
    assert validate_required_markers(valid_docs_root, label="docs_root_readme", markers=DOCS_ROOT_MARKERS) == []
    missing_docs_root = validate_required_markers(
        valid_docs_root.replace("make -C zigux phase2-toolchain", "", 1),
        label="docs_root_readme",
        markers=DOCS_ROOT_MARKERS,
    )
    assert "docs_root_readme:missing_marker:make -C zigux phase2-toolchain" in missing_docs_root

    valid_tests_readme = "\n".join(TESTS_README_MARKERS)
    assert validate_required_markers(valid_tests_readme, label="tests_readme", markers=TESTS_README_MARKERS) == []
    missing_tests_readme = validate_required_markers(
        valid_tests_readme.replace("bounded three-target compile matrix", "", 1),
        label="tests_readme",
        markers=TESTS_README_MARKERS,
    )
    assert "tests_readme:missing_marker:bounded three-target compile matrix" in missing_tests_readme

    valid_review_checklist = "\n".join(REVIEW_CHECKLIST_MARKERS)
    assert validate_required_markers(
        valid_review_checklist,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    ) == []
    missing_review_checklist = validate_required_markers(
        valid_review_checklist.replace("make -C zigux phase2-cross", "", 1),
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    assert "review_checklist:missing_marker:make -C zigux phase2-cross" in missing_review_checklist

    valid_closure = "\n".join(CLOSURE_MARKERS)
    assert validate_required_markers(valid_closure, label="phase2_closure_doc", markers=CLOSURE_MARKERS) == []
    missing_closure = validate_required_markers(
        valid_closure.replace("PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json", "", 1),
        label="phase2_closure_doc",
        markers=CLOSURE_MARKERS,
    )
    assert (
        "phase2_closure_doc:missing_marker:PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json"
        in missing_closure
    )

    valid_phase2_validator = "\n".join(PHASE2_VALIDATOR_MARKERS)
    assert validate_required_markers(
        valid_phase2_validator,
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    ) == []
    missing_phase2_validator = validate_required_markers(
        valid_phase2_validator.replace('"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"', "", 1),
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    )
    assert (
        'phase2_validator:missing_marker:"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"'
        in missing_phase2_validator
    )

    valid_phase2_closure_validator = "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS)
    assert validate_required_markers(
        valid_phase2_closure_validator,
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    ) == []
    closure_validator_anchor = (
        'CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"'
    )
    missing_phase2_closure_validator = validate_required_markers(
        valid_phase2_closure_validator.replace(closure_validator_anchor, "", 1),
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    )
    assert (
        f"phase2_closure_validator:missing_marker:{closure_validator_anchor}"
        in missing_phase2_closure_validator
    )

    valid_makefile = "\n".join(
        [
            *REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES,
            "phase2-toolchain:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "phase2-validate: phase2-toolchain",
            "phase2-tools:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig",
            "phase2-kconfig:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
            "phase2-cross:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
            "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
        ]
    )
    assert validate_required_markers(valid_makefile, label="phase2_makefile", markers=MAKEFILE_MARKERS) == []
    assert validate_exact_makefile_runs(valid_makefile) == []
    assert validate_toolchain_target_scope(valid_makefile) == []
    assert validate_repo_local_zig_fallback(valid_makefile) == []
    assert validate_repo_local_zig_make_routes(valid_makefile) == []
    missing_repo_local_fallback = validate_repo_local_zig_fallback(
        valid_makefile.replace("export PATH := $(dir $(REPO_LOCAL_ZIG)):$(PATH)\n", "", 1)
    )
    assert any(issue.startswith("makefile_repo_local_zig_block:") for issue in missing_repo_local_fallback)
    leaked_phase2_tools_route = validate_repo_local_zig_make_routes(
        valid_makefile.replace("\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig", "\tcd $(ZIGUX_ROOT) && zig test scripts/zigux/genksyms.zig", 1)
    )
    assert any(issue.startswith("makefile_target_scope:phase2-tools:") for issue in leaked_phase2_tools_route)
    leaked_phase2_kconfig_route = validate_repo_local_zig_make_routes(
        valid_makefile.replace("\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig\n", "", 1)
    )
    assert any(issue.startswith("makefile_target_scope:phase2-kconfig:") for issue in leaked_phase2_kconfig_route)
    leaked_phase2_cross_route = validate_repo_local_zig_make_routes(
        valid_makefile.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --zig /tmp/other-zig\n",
            1,
        )
    )
    assert any(issue.startswith("makefile_target_scope:phase2-cross:") for issue in leaked_phase2_cross_route)

    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/install-zig.py --self-test",
            "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
            "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
            "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
        ]
    )
    assert validate_exact_workflow_runs(workflow_text, payload=valid_policy) == []

    for label, checks in EXACT_SURFACE_COUNTS.items():
        text = "\n".join(checks.keys())
        assert validate_exact_marker_counts(text, label=label, checks=checks) == []
        duplicated = text + "\n" + next(iter(checks.keys()))
        issues = validate_exact_marker_counts(duplicated, label=label, checks=checks)
        assert issues and issues[0].startswith(f"{label}:exact_count:")

    assert "policy:phase='Phase 3':expected='Phase 2'" in validate_policy({**valid_policy, "phase": "Phase 3"})
    assert any(
        issue.startswith("workflow_forbidden_fragment:")
        for issue in validate_exact_workflow_runs(
            "run: python3 scripts/zigux/check-zig-toolchain.py --arch x86_64",
            payload=valid_policy,
        )
    )
    assert (
        "makefile_exact_run:scripts/zigux/check-zig-toolchain.py:count=2:expected=1"
        in validate_exact_makefile_runs(
            valid_makefile
            + "\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py"
        )
    )
    leaked_scope = "\n".join(
        [
            *REPO_LOCAL_ZIG_FALLBACK_REQUIRED_LINES,
            "phase2-toolchain:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
            "phase2-validate: phase2-toolchain",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
        ]
    )
    leaked_issues = validate_toolchain_target_scope(leaked_scope)
    assert any(issue.startswith("makefile_target_scope:phase2-toolchain:") for issue in leaked_issues)
    assert any(issue.startswith("makefile_target_scope:phase2-validate:") for issue in leaked_issues)
    assert (
        "policy:approval_policy:shared_phase2_checklist_ack_required=False:expected=True"
        in validate_policy(
            {
                **valid_policy,
                "approval_policy": {
                    "shared_phase2_checklist_ack_required": False,
                    "fresh_bootstrap_runner_evidence_required": True,
                    "separate_cross_target_expansion_approval_required": True,
                },
            }
        )
    )

    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_pin_scope_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "toolchain.json"
        manifest_path.write_text(json.dumps(valid_policy), encoding="utf-8")
        assert load_json_object(manifest_path, label="policy")["archive_sha256"] == valid_policy["archive_sha256"]

    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=37")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap archive pin limited to the current workflow host target until new runner evidence lands."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in pin-scope checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = [
        POLICY,
        NOTES_DOC,
        WORKFLOW,
        README,
        DOCS_ROOT_README,
        TESTS_README,
        REVIEW_CHECKLIST,
        CLOSURE_DOC,
        PHASE2_VALIDATOR,
        PHASE2_CLOSURE_VALIDATOR,
        MAKEFILE,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
        print("MISSING_PHASE2_TOOLCHAIN_PIN_SCOPE_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_TOOLCHAIN_PIN_SCOPE_FILES_END")
        return 1

    policy_payload = load_json_object(POLICY, label="policy")
    issues: list[str] = []
    issues.extend(validate_policy(policy_payload))

    notes_text = NOTES_DOC.read_text(encoding="utf-8")
    issues.extend(validate_phase2_notes(notes_text, payload=policy_payload))
    issues.extend(
        validate_exact_marker_counts(
            notes_text,
            label="phase2_toolchain_notes",
            checks=EXACT_SURFACE_COUNTS["phase2_toolchain_notes"],
        )
    )

    scripts_readme_text = README.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(scripts_readme_text, label="scripts_readme", markers=README_MARKERS))
    issues.extend(validate_exact_marker_counts(scripts_readme_text, label="scripts_readme", checks=EXACT_SURFACE_COUNTS["scripts_readme"]))

    docs_root_text = DOCS_ROOT_README.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(docs_root_text, label="docs_root_readme", markers=DOCS_ROOT_MARKERS))
    issues.extend(validate_exact_marker_counts(docs_root_text, label="docs_root_readme", checks=EXACT_SURFACE_COUNTS["docs_root_readme"]))

    tests_readme_text = TESTS_README.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(tests_readme_text, label="tests_readme", markers=TESTS_README_MARKERS))
    issues.extend(validate_exact_marker_counts(tests_readme_text, label="tests_readme", checks=EXACT_SURFACE_COUNTS["tests_readme"]))

    review_text = REVIEW_CHECKLIST.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(review_text, label="review_checklist", markers=REVIEW_CHECKLIST_MARKERS))
    issues.extend(validate_exact_marker_counts(review_text, label="review_checklist", checks=EXACT_SURFACE_COUNTS["review_checklist"]))

    closure_text = CLOSURE_DOC.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(closure_text, label="phase2_closure_doc", markers=CLOSURE_MARKERS))
    issues.extend(validate_exact_marker_counts(closure_text, label="phase2_closure_doc", checks=EXACT_SURFACE_COUNTS["phase2_closure_doc"]))

    issues.extend(validate_required_markers(PHASE2_VALIDATOR.read_text(encoding="utf-8"), label="phase2_validator", markers=PHASE2_VALIDATOR_MARKERS))
    issues.extend(validate_required_markers(PHASE2_CLOSURE_VALIDATOR.read_text(encoding="utf-8"), label="phase2_closure_validator", markers=PHASE2_CLOSURE_VALIDATOR_MARKERS))

    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(makefile_text, label="phase2_makefile", markers=MAKEFILE_MARKERS))
    issues.extend(validate_exact_makefile_runs(makefile_text))
    issues.extend(validate_toolchain_target_scope(makefile_text))
    issues.extend(validate_repo_local_zig_fallback(makefile_text))
    issues.extend(validate_repo_local_zig_make_routes(makefile_text))

    issues.extend(validate_exact_workflow_runs(WORKFLOW.read_text(encoding="utf-8"), payload=policy_payload))

    if issues:
        print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
        print("INVALID_PHASE2_TOOLCHAIN_PIN_SCOPE_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_TOOLCHAIN_PIN_SCOPE_END")
        return 1

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
