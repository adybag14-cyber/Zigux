#!/usr/bin/env python3
"""Guard the dedicated Phase 2 genksyms survey reminder packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
GENKSYMS_SURVEY = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
MANIFEST = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

REQUIRED_PATHS = (
    PHASE2_CLOSURE,
    GENKSYMS_SURVEY,
    SCRIPTS_README,
    TESTS_README,
    WORKFLOW,
    MAKEFILE,
    MANIFEST,
)

PHASE2_CLOSURE_MARKERS = (
    "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "- `scripts/zigux/check-genksyms-bridge.py`",
    "- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "- `scripts/zigux/genksyms.zig`",
    "- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "- `zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`",
    "- `make -C zigux phase2-genksyms`",
)

GENKSYMS_SURVEY_MARKERS = (
    "- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.",
    "- The bootstrap ledger still records a bounded genksyms wrapper lane around `scripts/zigux/genksyms.zig` together with a dedicated checker and fixture-backed expected-output packet, so this family remains real product infrastructure rather than wrapper churn.",
    "- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.",
    "- The live helper still exposes the bounded bridge shape rather than a deeper parser rollout: request and command structs, explicit parse-failure variants for option handling, a sixteen-file reference cap, long-option resolution for `help`, `version`, `debug`, `warnings`, `quiet`, `dump`, `reference`, `dump-types`, and `preserve`, and JSON bridge rendering through `renderGenksymsBridge()`.",
    "- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, empty inline `--reference=` and abbreviated `--dump-t=` argument preservation, passthrough handling, dash-prefixed short- and long-option arguments consumed as data, and the sixteen-reference-file cap, so helper-local replay evidence remains materialized.",
    "- Current `master` directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, and restored process-output packet again:",
    "- Current shared Phase 2 reminder surfaces also keep the genksyms packet explicit:",
    "- Current `master` no longer leaves a dedicated tests-root reminder drift outside the checker-owned manifest packet: `zigux/tests/README.md`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `Documentation/zigux/phase2-closure.md`, and `zigux/tests/fixtures/phase2_tool_manifest.json` all now carry both dash-prefixed expected-output fixtures beside the same ten-case bridge roster.",
    "- Relative to the roadmap and ledger, the older inventory-shaped governance gap remains closed on current `master`, and the narrower tests-root reminder undercount is closed again too: the live work is a bounded wrapper-first dual-implementation packet whose checker-owned manifest, workflow, closure note, dedicated survey, and explicit tests-root fixture list are aligned again.",
    "- `2026-05-26` scheduled lane `P2-L07` reread `zigux/tests/README.md`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and the live bridge manifest again, confirming the explicit tests-root list still carries both dash-prefixed expected-output fixtures and that this note should keep that closed state explicit instead of restating the older undercount.",
    "- The exact packet counts confirmed across the current reminder and manifest surfaces remain: `GENKSYMS_CASE_COUNT=10`, `GENKSYMS_PROCESS_OUTPUT_FIXTURE_COUNT=9`, `GENKSYMS_HELP_PACKET_COUNT=1`, `GENKSYMS_MANIFEST_HELPER_ANCHOR_COUNT=15`, `GENKSYMS_MAKEFILE_HOOK_COUNT=5`, `GENKSYMS_WORKFLOW_HOOK_COUNT=6`, and `GENKSYMS_STANDALONE_PROOF_FILE_COUNT=2`.",
    "1. Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`make -C zigux phase2-genksyms`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

TESTS_README_MARKERS = (
    "current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-genksyms",
)

MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
)

EXPECTED_MANIFEST = {
    "case_count": 10,
    "help_packet": ["help_expected.json"],
    "standalone_proof_packet": [
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    ],
    "process_output_packet": [
        "abbreviated_version_expected.json",
        "ambiguous_long_option_expected.json",
        "invalid_option_expected.json",
        "missing_long_dump_types_argument_expected.json",
        "missing_long_reference_argument_expected.json",
        "missing_reference_argument_expected.json",
        "too_many_reference_files_expected.json",
        "unsupported_long_option_expected.json",
        "unexpected_long_help_argument_expected.json",
    ],
    "helper_local_anchor_count": 15,
    "required_bridge_expected_packet_members": [
        "dash_prefixed_long_option_arguments_as_data_expected.json",
        "dash_prefixed_short_option_arguments_as_data_expected.json",
    ],
}

SAMPLE_PHASE2_CLOSURE = """# Phase 2 Closure

## Current Closure Packet

- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`

## Closure Validation

- `make -C zigux phase2-genksyms`
"""

SAMPLE_GENKSYMS_SURVEY = """# Phase 2 genksyms dual-implementation survey

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.
- The bootstrap ledger still records a bounded genksyms wrapper lane around `scripts/zigux/genksyms.zig` together with a dedicated checker and fixture-backed expected-output packet, so this family remains real product infrastructure rather than wrapper churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.
- The live helper still exposes the bounded bridge shape rather than a deeper parser rollout: request and command structs, explicit parse-failure variants for option handling, a sixteen-file reference cap, long-option resolution for `help`, `version`, `debug`, `warnings`, `quiet`, `dump`, `reference`, `dump-types`, and `preserve`, and JSON bridge rendering through `renderGenksymsBridge()`.
- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, empty inline `--reference=` and abbreviated `--dump-t=` argument preservation, passthrough handling, dash-prefixed short- and long-option arguments consumed as data, and the sixteen-reference-file cap, so helper-local replay evidence remains materialized.
- Current `master` directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, and restored process-output packet again:
- Current shared Phase 2 reminder surfaces also keep the genksyms packet explicit:
- Current `master` no longer leaves a dedicated tests-root reminder drift outside the checker-owned manifest packet: `zigux/tests/README.md`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `Documentation/zigux/phase2-closure.md`, and `zigux/tests/fixtures/phase2_tool_manifest.json` all now carry both dash-prefixed expected-output fixtures beside the same ten-case bridge roster.

## Survey result

- Relative to the roadmap and ledger, the older inventory-shaped governance gap remains closed on current `master`, and the narrower tests-root reminder undercount is closed again too: the live work is a bounded wrapper-first dual-implementation packet whose checker-owned manifest, workflow, closure note, dedicated survey, and explicit tests-root fixture list are aligned again.

## Verification note

- `2026-05-26` scheduled lane `P2-L07` reread `zigux/tests/README.md`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and the live bridge manifest again, confirming the explicit tests-root list still carries both dash-prefixed expected-output fixtures and that this note should keep that closed state explicit instead of restating the older undercount.
- The exact packet counts confirmed across the current reminder and manifest surfaces remain: `GENKSYMS_CASE_COUNT=10`, `GENKSYMS_PROCESS_OUTPUT_FIXTURE_COUNT=9`, `GENKSYMS_HELP_PACKET_COUNT=1`, `GENKSYMS_MANIFEST_HELPER_ANCHOR_COUNT=15`, `GENKSYMS_MAKEFILE_HOOK_COUNT=5`, `GENKSYMS_WORKFLOW_HOOK_COUNT=6`, and `GENKSYMS_STANDALONE_PROOF_FILE_COUNT=2`.

## Next bounded same-family step

1. Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.
"""

SAMPLE_SCRIPTS_README = """# scripts/zigux

## Phase 2

- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py` keeps the dedicated survey-alignment packet explicit beside the same returned genksyms bridge helper and fixture roster.
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set
- keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet
"""

SAMPLE_TESTS_README = """# zigux/tests

## Phase 2 review packet

current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder

- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`
"""

SAMPLE_WORKFLOW = "\n".join(WORKFLOW_LINES) + "\n"
SAMPLE_MAKEFILE = "\n".join(MAKEFILE_LINES) + "\n"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}") from exc


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for candidate in text.splitlines() if candidate.strip() == line)


def collect_line_issues(text: str, lines: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for line in lines:
        count = count_exact_line(text, line)
        if count == 0:
            issues.append((missing_code, line))
        elif count != 1:
            issues.append((duplicate_code, f"{count}::{line}"))
    return issues


def collect_manifest_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_SHAPE", type(payload).__name__)]

    issues: list[tuple[str, str]] = []
    for key in ("case_count", "help_packet", "standalone_proof_packet", "process_output_packet"):
        expected = EXPECTED_MANIFEST[key]
        actual = payload.get(key)
        if actual != expected:
            issues.append(("MANIFEST_FIELD_MISMATCH", f"{key}:actual={actual!r}:expected={expected!r}"))

    helper_local_anchors = payload.get("helper_local_anchors")
    if not isinstance(helper_local_anchors, list):
        issues.append(("MANIFEST_FIELD_MISMATCH", f"helper_local_anchors:actual={helper_local_anchors!r}:expected_count={EXPECTED_MANIFEST['helper_local_anchor_count']}"))
    elif len(helper_local_anchors) != EXPECTED_MANIFEST["helper_local_anchor_count"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", f"helper_local_anchors:actual_count={len(helper_local_anchors)}:expected_count={EXPECTED_MANIFEST['helper_local_anchor_count']}"))

    bridge_expected_packet = payload.get("bridge_expected_packet")
    if not isinstance(bridge_expected_packet, list):
        issues.append(("MANIFEST_FIELD_MISMATCH", f"bridge_expected_packet:actual={bridge_expected_packet!r}:expected_list"))
    else:
        for member in EXPECTED_MANIFEST["required_bridge_expected_packet_members"]:
            if member not in bridge_expected_packet:
                issues.append(("MANIFEST_MISSING_BRIDGE_EXPECTED_MEMBER", member))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).is_file():
            issues.append(("MISSING_REQUIRED_PATH", rel.as_posix()))
    if issues:
        return issues

    phase2_closure_text = read_text(root / PHASE2_CLOSURE)
    survey_text = read_text(root / GENKSYMS_SURVEY)
    scripts_text = read_text(root / SCRIPTS_README)
    tests_text = read_text(root / TESTS_README)
    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)
    manifest_payload = read_json(root / MANIFEST)

    issues.extend(collect_missing_markers(phase2_closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKER"))
    issues.extend(collect_missing_markers(survey_text, GENKSYMS_SURVEY_MARKERS, "MISSING_SURVEY_MARKER"))
    issues.extend(collect_missing_markers(scripts_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKER"))
    issues.extend(collect_missing_markers(tests_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"))
    issues.extend(collect_line_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE"))
    issues.extend(collect_line_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE"))
    issues.extend(collect_manifest_issues(manifest_payload))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_SURVEY_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_sample_root(root: Path) -> None:
    write_text(root / PHASE2_CLOSURE, SAMPLE_PHASE2_CLOSURE)
    write_text(root / GENKSYMS_SURVEY, SAMPLE_GENKSYMS_SURVEY)
    write_text(root / SCRIPTS_README, SAMPLE_SCRIPTS_README)
    write_text(root / TESTS_README, SAMPLE_TESTS_README)
    write_text(root / WORKFLOW, SAMPLE_WORKFLOW)
    write_text(root / MAKEFILE, SAMPLE_MAKEFILE)
    write_text(
        root / MANIFEST,
        json.dumps(
            {
                "case_count": EXPECTED_MANIFEST["case_count"],
                "help_packet": EXPECTED_MANIFEST["help_packet"],
                "standalone_proof_packet": EXPECTED_MANIFEST["standalone_proof_packet"],
                "process_output_packet": EXPECTED_MANIFEST["process_output_packet"],
                "helper_local_anchors": [f"anchor-{index}" for index in range(EXPECTED_MANIFEST["helper_local_anchor_count"])],
                "bridge_expected_packet": [
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
                ],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane25_phase2_genksyms_survey_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        write_sample_root(root)
        write_text(root / GENKSYMS_SURVEY, "# broken\n")
        assert any(code == "MISSING_SURVEY_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        write_sample_root(root)
        write_text(root / WORKFLOW, "run: broken\n")
        assert any(code == "MISSING_WORKFLOW_LINE" for code, _ in collect_issues(root))
        checks_run += 1

        write_sample_root(root)
        write_text(root / MAKEFILE, "$(PYTHON) broken.py\n")
        assert any(code == "MISSING_MAKEFILE_LINE" for code, _ in collect_issues(root))
        checks_run += 1

        write_sample_root(root)
        manifest = json.loads(read_text(root / MANIFEST))
        manifest["case_count"] = 9
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("case_count:") for code, value in collect_issues(root))
        checks_run += 1

        write_sample_root(root)
        manifest = json.loads(read_text(root / MANIFEST))
        manifest["process_output_packet"] = ["invalid_option_expected.json"]
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("process_output_packet:") for code, value in collect_issues(root))
        checks_run += 1

        write_sample_root(root)
        (root / TESTS_README).unlink()
        assert ("MISSING_REQUIRED_PATH", TESTS_README.as_posix()) in collect_issues(root)
        checks_run += 1

    print("PHASE2_GENKSYMS_SURVEY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample tree")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_SURVEY_PACKET=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_CLOSURE_MARKER_COUNT={len(PHASE2_CLOSURE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_SURVEY_MARKER_COUNT={len(GENKSYMS_SURVEY_MARKERS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
