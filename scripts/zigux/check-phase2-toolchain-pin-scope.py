#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


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

EXPECTED_PIN_TARGETS = [
    "x86_64-linux",
]

ARCHIVE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

NOTE_STATIC_MARKERS = [
    "the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
    "the Linux-style `make -C zigux phase2-validate` and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the docs-root summary, the shared validators, the closure note, and the shared review checklist",
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-zig-toolchain.py": 2,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
}

WORKFLOW_FORBIDDEN_FRAGMENTS = [
    "scripts/zigux/install-zig.py --system",
    "scripts/zigux/install-zig.py --arch",
    "scripts/zigux/check-zig-toolchain.py --system",
    "scripts/zigux/check-zig-toolchain.py --arch",
]

README_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "x86_64-linux bootstrap host target",
    "cross-target compile matrix stays a separate Phase 2 surface",
]

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "pinned Zig toolchain",
    "make -C zigux phase2-validate",
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
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 2 toolchain packet",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

CLOSURE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1",
    "PHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json",
]

PHASE2_VALIDATOR_MARKERS = [
    "TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / \"scripts\" / \"zigux\" / \"check-phase2-toolchain-pin-scope.py\"",
    "\"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass\"",
    "\"PHASE2_TOOLCHAIN_PIN_SCOPE=pass\"",
]

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    "CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py'",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [",
    "'PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',",
    "'PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',",
    "PHASE2_MAKEFILE_RUN_COUNTS = {",
    "'scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1,",
    "'scripts/zigux/check-phase2-toolchain-pin-scope.py': 1,",
    "missing_markers.extend(validate_exact_makefile_runs(makefile))",
]

MAKEFILE_MARKERS = [
    "phase2-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
]


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
    if not isinstance(channel, str) or not channel:
        issues.append("policy:channel:expected_nonempty_string")

    minimum_version = payload.get("minimum_version")
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append("policy:minimum_version:expected_nonempty_string")

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



def validate_phase2_notes(text: str, *, payload: dict[str, object]) -> list[str]:
    issues: list[str] = []

    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel:
        issues.append("policy:channel:expected_nonempty_string")
    else:
        marker = f"- current pinned Zig channel: `{channel}`"
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")

    minimum_version = payload.get("minimum_version")
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append("policy:minimum_version:expected_nonempty_string")
    else:
        marker = f"- current minimum Zig version: `{minimum_version}`"
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")

    archive_sha256 = payload.get("archive_sha256")
    if isinstance(archive_sha256, dict):
        pin_target = EXPECTED_PIN_TARGETS[0]
        target_marker = f"- current pinned bootstrap archive target: `{pin_target}`"
        if target_marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{target_marker}")

        digest = archive_sha256.get(pin_target)
        if isinstance(digest, str):
            digest_marker = (
                f"- current pinned bootstrap archive sha256 (`{pin_target}`): `{digest}`"
            )
            if digest_marker not in text:
                issues.append(f"phase2_toolchain_notes:missing_marker:{digest_marker}")

    for marker in NOTE_STATIC_MARKERS:
        if marker not in text:
            issues.append(f"phase2_toolchain_notes:missing_marker:{marker}")
    return issues



def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues



def validate_exact_workflow_runs(text: str, *, payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel:
        issues.append("policy:channel:expected_nonempty_string")
        return issues

    lines = [line.strip() for line in text.splitlines()]
    expected_install_command = (
        f"python3 scripts/zigux/install-zig.py --channel {channel} --dest .zig-toolchain"
    )
    expected_install_line = f"run: {expected_install_command}"
    install_count = sum(1 for line in lines if line == expected_install_line)
    if install_count != 2:
        issues.append(
            f"workflow_exact_run:{expected_install_command}:count={install_count}:expected=2"
        )

    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    for fragment in WORKFLOW_FORBIDDEN_FRAGMENTS:
        if fragment in text:
            issues.append(f"workflow_forbidden_fragment:{fragment}")
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

    valid_notes = "\n".join(
        [
            "- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`",
            "- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`",
            "- current pinned bootstrap archive target: `x86_64-linux`",
            "- current pinned bootstrap archive sha256 (`x86_64-linux`): `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
            "- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence",
            "- the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
            "- the Linux-style `make -C zigux phase2-validate` and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the docs-root summary, the shared validators, the closure note, and the shared review checklist",
        ]
    )
    if validate_phase2_notes(valid_notes, payload=valid_policy):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_notes")

    valid_readme = "\n".join(README_MARKERS)
    if validate_required_markers(
        valid_readme,
        label="scripts_readme",
        markers=README_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_readme")

    valid_docs_root = "\n".join(DOCS_ROOT_MARKERS)
    if validate_required_markers(
        valid_docs_root,
        label="docs_root_readme",
        markers=DOCS_ROOT_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_docs_root")

    valid_tests_readme = "\n".join(TESTS_README_MARKERS)
    if validate_required_markers(
        valid_tests_readme,
        label="tests_readme",
        markers=TESTS_README_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_tests_readme")

    valid_review_checklist = "\n".join(REVIEW_CHECKLIST_MARKERS)
    if validate_required_markers(
        valid_review_checklist,
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_review_checklist")

    valid_closure = "\n".join(CLOSURE_MARKERS)
    if validate_required_markers(
        valid_closure,
        label="phase2_closure_doc",
        markers=CLOSURE_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_closure")

    valid_phase2_validator = "\n".join(PHASE2_VALIDATOR_MARKERS)
    if validate_required_markers(
        valid_phase2_validator,
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_phase2_validator")

    valid_phase2_closure_validator = "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS)
    if validate_required_markers(
        valid_phase2_closure_validator,
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_phase2_closure_validator")

    valid_makefile = "\n".join(MAKEFILE_MARKERS)
    if validate_required_markers(
        valid_makefile,
        label="phase2_makefile",
        markers=MAKEFILE_MARKERS,
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_makefile")

    bad_phase = dict(valid_policy)
    bad_phase["phase"] = "Phase 3"
    issues = validate_policy(bad_phase)
    if "policy:phase='Phase 3':expected='Phase 2'" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase_mismatch")

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

    bad_notes = valid_notes.replace(
        "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )
    issues = validate_phase2_notes(bad_notes, payload=valid_policy)
    expected_note_issue = (
        "phase2_toolchain_notes:missing_marker:- current pinned bootstrap archive sha256 "
        "(`x86_64-linux`): `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`"
    )
    if expected_note_issue not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:note_sha_mismatch")

    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
            "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
        ]
    )
    if validate_exact_workflow_runs(workflow_text, payload=valid_policy):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_counts")

    workflow_count_issues = validate_exact_workflow_runs(
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
                "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
            ]
        ),
        payload=valid_policy,
    )
    if "workflow_exact_run:python3 scripts/zigux/check-zig-toolchain.py:count=3:expected=2" not in workflow_count_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_count_mismatch")

    issues = validate_exact_workflow_runs(
        "run: python3 scripts/zigux/install-zig.py --channel master --dest .zig-toolchain",
        payload=valid_policy,
    )
    if not any(
        issue.startswith(
            "workflow_exact_run:python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain"
        )
        for issue in issues
    ):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_channel_mismatch")

    issues = validate_exact_workflow_runs(
        "run: python3 scripts/zigux/check-zig-toolchain.py --arch x86_64",
        payload=valid_policy,
    )
    if not any(issue.startswith("workflow_forbidden_fragment:") for issue in issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_forbidden_fragment")

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

    readme_issues = validate_required_markers(
        "check-phase2-toolchain-pin-scope.py --self-test\ncheck-phase2-toolchain-pin-scope.py",
        label="scripts_readme",
        markers=README_MARKERS,
    )
    if not any(issue.startswith("scripts_readme:missing_marker:") for issue in readme_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:readme_marker_failure")

    docs_root_issues = validate_required_markers(
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md\nscripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        label="docs_root_readme",
        markers=DOCS_ROOT_MARKERS,
    )
    if not any(issue.startswith("docs_root_readme:missing_marker:") for issue in docs_root_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:docs_root_marker_failure")

    tests_readme_issues = validate_required_markers(
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md\nscripts/zigux/check-phase2-toolchain-pin-scope.py",
        label="tests_readme",
        markers=TESTS_README_MARKERS,
    )
    if not any(issue.startswith("tests_readme:missing_marker:") for issue in tests_readme_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:tests_readme_marker_failure")

    review_issues = validate_required_markers(
        "if the change touches the shared Phase 2 toolchain packet\npython3 scripts/zigux/install-zig.py --self-test",
        label="review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if not any(issue.startswith("review_checklist:missing_marker:") for issue in review_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:review_marker_failure")

    closure_issues = validate_required_markers(
        "PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1\nPHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux",
        label="phase2_closure_doc",
        markers=CLOSURE_MARKERS,
    )
    if not any(issue.startswith("phase2_closure_doc:missing_marker:") for issue in closure_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:closure_marker_failure")

    validator_issues = validate_required_markers(
        "TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / \"scripts\" / \"zigux\" / \"check-phase2-toolchain-pin-scope.py\"",
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    )
    if not any(issue.startswith("phase2_validator:missing_marker:") for issue in validator_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase2_validator_marker_failure")

    closure_validator_issues = validate_required_markers(
        "CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py'",
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    )
    if not any(issue.startswith("phase2_closure_validator:missing_marker:") for issue in closure_validator_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase2_closure_validator_marker_failure")

    makefile_issues = validate_required_markers(
        "phase2-validate:\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        label="phase2_makefile",
        markers=MAKEFILE_MARKERS,
    )
    if not any(issue.startswith("phase2_makefile:missing_marker:") for issue in makefile_issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:makefile_marker_failure")

    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_pin_scope_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "toolchain.json"
        manifest_path.write_text(json.dumps(valid_policy), encoding="utf-8")
        round_trip = load_json_object(manifest_path, label="policy")
        if round_trip["archive_sha256"] != valid_policy["archive_sha256"]:
            raise SystemExit("phase2-toolchain-pin-scope:self-test:json_round_trip")

        duplicate_top_level_path = tmp_root / "duplicate-top-level.json"
        duplicate_top_level_path.write_text(
            '{"phase":"Phase 2","phase":"Phase 3","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"}}',
            encoding="utf-8",
        )
        try:
            load_json_object(duplicate_top_level_path, label="policy")
        except SystemExit as exc:
            if str(exc) != "policy:duplicate_key:phase":
                raise SystemExit("phase2-toolchain-pin-scope:self-test:duplicate_top_level_shape") from exc
        else:
            raise SystemExit("phase2-toolchain-pin-scope:self-test:duplicate_top_level_missing")

        duplicate_archive_key_path = tmp_root / "duplicate-archive-key.json"
        duplicate_archive_key_path.write_text(
            '{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77","x86_64-linux":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}',
            encoding="utf-8",
        )
        try:
            load_json_object(duplicate_archive_key_path, label="policy")
        except SystemExit as exc:
            if str(exc) != "policy:duplicate_key:x86_64-linux":
                raise SystemExit("phase2-toolchain-pin-scope:self-test:duplicate_archive_key_shape") from exc
        else:
            raise SystemExit("phase2-toolchain-pin-scope:self-test:duplicate_archive_key_missing")

    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=28")
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
    issues.extend(
        validate_phase2_notes(
            NOTES_DOC.read_text(encoding="utf-8"),
            payload=policy_payload,
        )
    )
    issues.extend(
        validate_required_markers(
            README.read_text(encoding="utf-8"),
            label="scripts_readme",
            markers=README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            DOCS_ROOT_README.read_text(encoding="utf-8"),
            label="docs_root_readme",
            markers=DOCS_ROOT_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            TESTS_README.read_text(encoding="utf-8"),
            label="tests_readme",
            markers=TESTS_README_MARKERS,
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
            CLOSURE_DOC.read_text(encoding="utf-8"),
            label="phase2_closure_doc",
            markers=CLOSURE_MARKERS,
        )
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
            MAKEFILE.read_text(encoding="utf-8"),
            label="phase2_makefile",
            markers=MAKEFILE_MARKERS,
        )
    )
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
