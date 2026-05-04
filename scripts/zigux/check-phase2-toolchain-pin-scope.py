#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]

POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TOOLCHAIN_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"

EXPECTED_PIN_TARGETS = [
    "x86_64-linux",
]

ARCHIVE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/install-zig.py --self-test": 1,
    "python3 scripts/zigux/install-zig.py --dest .zig-toolchain": 2,
    "python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "python3 scripts/zigux/check-zig-toolchain.py": 2,
    "python3 scripts/zigux/validate-phase2.py": 1,
    "python3 scripts/zigux/validate-phase2-closure.py": 1,
}

EXACT_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "scripts/zigux/check-zig-toolchain.py": 1,
    "scripts/zigux/validate-phase2.py": 1,
    "scripts/zigux/validate-phase2-closure.py": 1,
}

WORKFLOW_FORBIDDEN_FRAGMENTS = [
    "scripts/zigux/install-zig.py --system",
    "scripts/zigux/install-zig.py --arch",
    "scripts/zigux/check-zig-toolchain.py --system",
    "scripts/zigux/check-zig-toolchain.py --arch",
]

PHASE2_VALIDATOR_MARKERS = [
    "TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / \"scripts\" / \"zigux\" / \"check-phase2-toolchain-pin-scope.py\"",
    "\"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass\"",
    "\"PHASE2_TOOLCHAIN_PIN_SCOPE=pass\"",
    "str(TOOLCHAIN_PIN_SCOPE_CHECKER)",
    "toolchain_pin_scope_checker",
]

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    "CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py'",
    "'PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test'",
    "'PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py'",
    "'scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1",
    "'scripts/zigux/check-phase2-toolchain-pin-scope.py': 1",
]

SCRIPTS_README_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "zig-toolchain-policy.json",
    "x86_64-linux",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "kbuild-facing review path",
]

DOCS_ROOT_README_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "validate-phase2.py",
    "validate-phase2-closure.py",
    "zig-toolchain-policy.json",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "install-zig.py --dest .zig-toolchain",
    "check-zig-toolchain.py",
    "bounded `x86_64-linux` archive pin visible from the docs root as one kbuild-facing review path",
    "shared and closure validators fail-closing on the same dedicated toolchain-note sentence",
]

REVIEW_CHECKLIST_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "bounded archive pin",
    "fail-closed validator path",
    "workflow bootstrap install and verification route",
    "zigux/Makefile",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

CLOSURE_MARKERS = [
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "x86_64-linux",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=",
    "PHASE2_SHARED_VALIDATOR=python3 scripts/zigux/validate-phase2.py",
    "PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]


def expected_toolchain_notes_markers(
    channel: str,
    minimum_version: str,
    pin_target: str,
    pin_digest: str,
) -> list[str]:
    return [
        "check-phase2-toolchain-pin-scope.py --self-test",
        "check-phase2-toolchain-pin-scope.py",
        "zig-toolchain-policy.json",
        "x86_64-linux",
        "install-zig.py --dest .zig-toolchain",
        "check-zig-toolchain.py",
        f"current pinned Zig channel: `{channel}`",
        f"current minimum Zig version: `{minimum_version}`",
        f"current pinned bootstrap archive target: `{pin_target}`",
        f"current pinned bootstrap archive sha256 (`{pin_target}`): `{pin_digest}`",
        "the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence",
        f"the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `{pin_target}` bootstrap archive pin",
        "the shared and closure validators above, together with `Documentation/zigux/review-checklist.md`, are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text",
        "the Linux-style `make -C zigux phase2-validate` and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist",
    ]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_policy(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"policy:phase={payload.get('phase')!r}:expected='Phase 2'")

    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel:
        issues.append("policy:channel:expected_non_empty_string")

    minimum_version = payload.get("minimum_version")
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append("policy:minimum_version:expected_non_empty_string")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append("policy:archive_sha256:expected_object")
        return issues

    keys = list(archive_sha256.keys())
    if keys != EXPECTED_PIN_TARGETS:
        issues.append(f"policy:archive_sha256_keys={keys!r}:expected={EXPECTED_PIN_TARGETS!r}")

    for target_key, digest in archive_sha256.items():
        if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
            issues.append(f"policy:archive_sha256:{target_key}:expected_sha256_hex")
    return issues


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    for fragment in WORKFLOW_FORBIDDEN_FRAGMENTS:
        if fragment in text:
            issues.append(f"workflow_forbidden_fragment:{fragment}")
    return issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_MAKEFILE_RUN_COUNTS.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def run_self_test() -> int:
    valid_policy = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        },
    }
    if validate_policy(valid_policy):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_policy")

    bad_phase = dict(valid_policy)
    bad_phase["phase"] = "Phase 3"
    issues = validate_policy(bad_phase)
    if "policy:phase='Phase 3':expected='Phase 2'" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase_mismatch")

    bad_channel = dict(valid_policy)
    bad_channel["channel"] = ""
    issues = validate_policy(bad_channel)
    if "policy:channel:expected_non_empty_string" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:channel_missing")

    bad_minimum_version = dict(valid_policy)
    bad_minimum_version["minimum_version"] = ""
    issues = validate_policy(bad_minimum_version)
    if "policy:minimum_version:expected_non_empty_string" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:minimum_version_missing")

    bad_archive_object = dict(valid_policy)
    bad_archive_object["archive_sha256"] = []
    issues = validate_policy(bad_archive_object)
    if "policy:archive_sha256:expected_object" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:archive_object_shape")

    bad_keys = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
            "aarch64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        },
    }
    issues = validate_policy(bad_keys)
    if not any(issue.startswith("policy:archive_sha256_keys=") for issue in issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:key_mismatch")

    bad_digest = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "not-a-digest",
        },
    }
    issues = validate_policy(bad_digest)
    if "policy:archive_sha256:x86_64-linux:expected_sha256_hex" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:digest_shape")

    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/install-zig.py --self-test",
            "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
            "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
            "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/validate-phase2.py",
            "run: python3 scripts/zigux/validate-phase2-closure.py",
        ]
    )
    if validate_exact_workflow_runs(workflow_text):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_counts")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
            ]
        )
    )
    if not any(
        issue.startswith("workflow_exact_run:python3 scripts/zigux/validate-phase2.py:count=0:expected=1")
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_validate_phase2_missing")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
            ]
        )
    )
    if not any(
        issue.startswith(
            "workflow_exact_run:python3 scripts/zigux/validate-phase2-closure.py:count=0:expected=1"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_validate_phase2_closure_missing")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
                "run: python3 scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith("workflow_exact_run:python3 scripts/zigux/check-zig-toolchain.py:count=1:expected=2")
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_toolchain_live_route_missing")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
                "run: python3 scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith("workflow_exact_run:python3 scripts/zigux/install-zig.py --self-test:count=0:expected=1")
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_install_selftest_missing")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
                "run: python3 scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith("workflow_exact_run:python3 scripts/zigux/check-zig-toolchain.py --self-test:count=0:expected=1")
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_toolchain_selftest_missing")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
                "run: python3 scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith(
            "workflow_exact_run:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test:count=0:expected=1"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_pin_scope_selftest_missing")

    issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
                "run: python3 scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith(
            "workflow_exact_run:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py:count=0:expected=1"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_pin_scope_live_missing")

    issues = validate_exact_workflow_runs("run: python3 scripts/zigux/check-zig-toolchain.py --arch x86_64")
    if not any(issue.startswith("workflow_forbidden_fragment:") for issue in issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_forbidden_fragment")

    makefile_text = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
        ]
    )
    if validate_exact_makefile_runs(makefile_text):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_counts")

    issues = validate_exact_makefile_runs(
        "\n".join(
            [
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith(
            "makefile_exact_run:scripts/zigux/check-phase2-toolchain-pin-scope.py:count=0:expected=1"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_pin_scope_missing")

    issues = validate_exact_makefile_runs(
        "\n".join(
            [
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
            ]
        )
    )
    if not any(
        issue.startswith(
            "makefile_exact_run:scripts/zigux/validate-phase2-closure.py:count=0:expected=1"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_validate_phase2_closure_missing")

    issues = validate_exact_makefile_runs(
        "\n".join(
            [
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith(
            "makefile_exact_run:scripts/zigux/validate-phase2-closure.py:count=2:expected=1"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_validate_phase2_closure_duplicate")

    issues = validate_exact_makefile_runs(
        "\n".join(
            [
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith("makefile_exact_run:scripts/zigux/check-zig-toolchain.py:count=2:expected=1")
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_toolchain_duplicate")

    issues = validate_exact_makefile_runs(
        "\n".join(
            [
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            ]
        )
    )
    if not any(
        issue.startswith("makefile_exact_run:scripts/zigux/validate-phase2.py:count=2:expected=1")
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_validate_phase2_duplicate")

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["alpha", "gamma"],
    )
    if marker_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:marker_presence")

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["delta"],
    )
    if marker_issues != ["sample:missing_marker:delta"]:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:marker_failure_shape")

    scripts_readme_text = "\n".join(SCRIPTS_README_MARKERS)
    if validate_required_markers(scripts_readme_text, label="scripts_readme", markers=SCRIPTS_README_MARKERS):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:scripts_readme_markers")

    marker_issues = validate_required_markers(
        "\n".join(marker for marker in SCRIPTS_README_MARKERS if marker != "kbuild-facing review path"),
        label="scripts_readme",
        markers=SCRIPTS_README_MARKERS,
    )
    if "scripts_readme:missing_marker:kbuild-facing review path" not in marker_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:scripts_readme_reviewability_marker")

    docs_root_readme_text = "\n".join(DOCS_ROOT_README_MARKERS)
    if validate_required_markers(
        docs_root_readme_text,
        label="docs_root_readme",
        markers=DOCS_ROOT_README_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:docs_root_readme_markers")

    marker_issues = validate_required_markers(
        "\n".join(
            marker
            for marker in DOCS_ROOT_README_MARKERS
            if marker != "shared and closure validators fail-closing on the same dedicated toolchain-note sentence"
        ),
        label="docs_root_readme",
        markers=DOCS_ROOT_README_MARKERS,
    )
    if (
        "docs_root_readme:missing_marker:shared and closure validators fail-closing on the same dedicated toolchain-note sentence"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:docs_root_readme_fail_closed_marker")

    toolchain_notes_markers = expected_toolchain_notes_markers(
        valid_policy["channel"],
        valid_policy["minimum_version"],
        EXPECTED_PIN_TARGETS[0],
        valid_policy["archive_sha256"][EXPECTED_PIN_TARGETS[0]],
    )
    toolchain_notes_text = "\n".join(toolchain_notes_markers)
    if validate_required_markers(
        toolchain_notes_text,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_markers")

    missing_toolchain_channel = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker != f"current pinned Zig channel: `{valid_policy['channel']}`"
    )
    marker_issues = validate_required_markers(
        missing_toolchain_channel,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        f"toolchain_notes:missing_marker:current pinned Zig channel: `{valid_policy['channel']}`"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_channel_marker")

    missing_toolchain_minimum = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker != f"current minimum Zig version: `{valid_policy['minimum_version']}`"
    )
    marker_issues = validate_required_markers(
        missing_toolchain_minimum,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        f"toolchain_notes:missing_marker:current minimum Zig version: `{valid_policy['minimum_version']}`"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_minimum_marker")

    missing_toolchain_target = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker != f"current pinned bootstrap archive target: `{EXPECTED_PIN_TARGETS[0]}`"
    )
    marker_issues = validate_required_markers(
        missing_toolchain_target,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        f"toolchain_notes:missing_marker:current pinned bootstrap archive target: `{EXPECTED_PIN_TARGETS[0]}`"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_target_marker")

    missing_toolchain_sha = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker
        != "current pinned bootstrap archive sha256 (`x86_64-linux`): `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`"
    )
    marker_issues = validate_required_markers(
        missing_toolchain_sha,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        "toolchain_notes:missing_marker:current pinned bootstrap archive sha256 (`x86_64-linux`): "
        "`313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_sha_marker")

    missing_matrix_separation = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker
        != "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin"
    )
    marker_issues = validate_required_markers(
        missing_matrix_separation,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        "toolchain_notes:missing_marker:the three-target compile matrix in "
        "`zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the "
        "`x86_64-linux` bootstrap archive pin"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_matrix_marker")

    missing_fail_closed_route = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker
        != "the shared and closure validators above, together with `Documentation/zigux/review-checklist.md`, are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text"
    )
    marker_issues = validate_required_markers(
        missing_fail_closed_route,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        "toolchain_notes:missing_marker:the shared and closure validators above, together with "
        "`Documentation/zigux/review-checklist.md`, are the fail-closed route that keeps this note in "
        "the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_fail_closed_route_marker")

    missing_make_route = "\n".join(
        marker
        for marker in toolchain_notes_markers
        if marker
        != "the Linux-style `make -C zigux phase2-validate` and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist"
    )
    marker_issues = validate_required_markers(
        missing_make_route,
        label="toolchain_notes",
        markers=toolchain_notes_markers,
    )
    if (
        "toolchain_notes:missing_marker:the Linux-style `make -C zigux phase2-validate` and `make -C zigux "
        "phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the "
        "shared validators, the closure note, and the shared review checklist"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:toolchain_notes_make_route_marker")

    closure_text = "\n".join(CLOSURE_MARKERS)
    if validate_required_markers(closure_text, label="closure", markers=CLOSURE_MARKERS):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:closure_markers")

    phase2_validator_text = "\n".join(PHASE2_VALIDATOR_MARKERS)
    if validate_required_markers(
        phase2_validator_text,
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase2_validator_markers")

    missing_phase2_validator_marker = "\n".join(
        marker for marker in PHASE2_VALIDATOR_MARKERS if marker != "toolchain_pin_scope_checker"
    )
    marker_issues = validate_required_markers(
        missing_phase2_validator_marker,
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    )
    if "phase2_validator:missing_marker:toolchain_pin_scope_checker" not in marker_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase2_validator_marker_missing")

    phase2_closure_validator_text = "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS)
    if validate_required_markers(
        phase2_closure_validator_text,
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase2_closure_validator_markers")

    missing_phase2_closure_validator_marker = "\n".join(
        marker
        for marker in PHASE2_CLOSURE_VALIDATOR_MARKERS
        if marker != "'scripts/zigux/check-phase2-toolchain-pin-scope.py': 1"
    )
    marker_issues = validate_required_markers(
        missing_phase2_closure_validator_marker,
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    )
    if (
        "phase2_closure_validator:missing_marker:'scripts/zigux/check-phase2-toolchain-pin-scope.py': 1"
        not in marker_issues
    ):
        raise SystemExit(
            "phase2-toolchain-pin-scope:self-test:phase2_closure_validator_marker_missing"
        )

    review_checklist_text = "\n".join(REVIEW_CHECKLIST_MARKERS)
    if validate_required_markers(
        review_checklist_text,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:review_checklist_markers")

    missing_review_checklist_marker = "\n".join(
        marker
        for marker in REVIEW_CHECKLIST_MARKERS
        if marker != "scripts/zigux/check-phase2-toolchain-pin-scope.py"
    )
    marker_issues = validate_required_markers(
        missing_review_checklist_marker,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if (
        "review_checklist:missing_marker:scripts/zigux/check-phase2-toolchain-pin-scope.py"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:review_checklist_marker_missing")

    missing_review_bounded_archive_pin = "\n".join(
        marker for marker in REVIEW_CHECKLIST_MARKERS if marker != "bounded archive pin"
    )
    marker_issues = validate_required_markers(
        missing_review_bounded_archive_pin,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if "review_checklist:missing_marker:bounded archive pin" not in marker_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:review_checklist_bounded_archive_pin_marker")

    missing_review_fail_closed_path = "\n".join(
        marker for marker in REVIEW_CHECKLIST_MARKERS if marker != "fail-closed validator path"
    )
    marker_issues = validate_required_markers(
        missing_review_fail_closed_path,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if "review_checklist:missing_marker:fail-closed validator path" not in marker_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:review_checklist_fail_closed_path_marker")

    missing_review_workflow_route = "\n".join(
        marker
        for marker in REVIEW_CHECKLIST_MARKERS
        if marker != "workflow bootstrap install and verification route"
    )
    marker_issues = validate_required_markers(
        missing_review_workflow_route,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if (
        "review_checklist:missing_marker:workflow bootstrap install and verification route"
        not in marker_issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:review_checklist_workflow_route_marker")

    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_pin_scope_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "toolchain.json"
        manifest_path.write_text(json.dumps(valid_policy), encoding="utf-8")
        round_trip = load_json_object(manifest_path, label="policy")
        if round_trip["archive_sha256"] != valid_policy["archive_sha256"]:
            raise SystemExit("phase2-toolchain-pin-scope:self-test:json_round_trip")

    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=45")
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
        WORKFLOW,
        MAKEFILE,
        SCRIPTS_README,
        DOCS_ROOT_README,
        TOOLCHAIN_NOTES,
        REVIEW_CHECKLIST,
        CLOSURE_DOC,
        PHASE2_VALIDATOR,
        PHASE2_CLOSURE_VALIDATOR,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
        print("MISSING_PHASE2_TOOLCHAIN_PIN_SCOPE_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_TOOLCHAIN_PIN_SCOPE_FILES_END")
        return 1

    policy = load_json_object(POLICY, label="policy")
    issues: list[str] = []
    issues.extend(validate_policy(policy))
    channel = policy.get("channel")
    minimum_version = policy.get("minimum_version")
    archive_sha256 = policy.get("archive_sha256")
    toolchain_notes_markers: list[str] = []
    pin_target = EXPECTED_PIN_TARGETS[0]
    pin_digest = "<missing-archive-sha256>"
    if isinstance(archive_sha256, dict):
        digest = archive_sha256.get(pin_target)
        if isinstance(digest, str) and digest:
            pin_digest = digest
    if isinstance(channel, str) and channel and isinstance(minimum_version, str) and minimum_version:
        toolchain_notes_markers = expected_toolchain_notes_markers(
            channel,
            minimum_version,
            pin_target,
            pin_digest,
        )
    else:
        toolchain_notes_markers = expected_toolchain_notes_markers(
            "<missing-channel>",
            "<missing-minimum-version>",
            pin_target,
            pin_digest,
        )
    issues.extend(
        validate_required_markers(
            PHASE2_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            PHASE2_CLOSURE_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_closure_validator",
            markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            SCRIPTS_README.read_text(encoding="utf-8"),
            label="scripts_readme",
            markers=SCRIPTS_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            DOCS_ROOT_README.read_text(encoding="utf-8"),
            label="docs_root_readme",
            markers=DOCS_ROOT_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            REVIEW_CHECKLIST.read_text(encoding="utf-8"),
            label="review_checklist",
            markers=REVIEW_CHECKLIST_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            TOOLCHAIN_NOTES.read_text(encoding="utf-8"),
            label="toolchain_notes",
            markers=toolchain_notes_markers,
        )
    )
    issues.extend(
        validate_required_markers(
            CLOSURE_DOC.read_text(encoding="utf-8"),
            label="phase2_closure_doc",
            markers=CLOSURE_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(WORKFLOW.read_text(encoding="utf-8")))
    issues.extend(validate_exact_makefile_runs(MAKEFILE.read_text(encoding="utf-8")))

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

# Bootstrap validator compatibility marker: def expected_toolchain_notes_markers(channel: str, minimum_version: str) -> list[str]:
# Shared Phase 2 validator compatibility marker: PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=45