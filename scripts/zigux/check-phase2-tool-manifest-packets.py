#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


def derive_repo_root(script_path: Path) -> Path:
    return script_path.parents[2] if len(script_path.parents) >= 3 else script_path.parent


SELF_PATH = Path(__file__).resolve()
ROOT = derive_repo_root(SELF_PATH)

PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_ARTIFACT_TOOLS_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
)
GENKSYMS_BRIDGE_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json"
)
KCONFIG_CONF_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
)
KCONFIG_CONFDATA_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
)

PHASE2_TOOL_MANIFEST_EXPECTED = {
    "packet": "phase2_tool_manifest",
    "phase": "phase2",
    "status": "current_master_packet",
    "shared_checker": "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "shared_routes": [
        "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
        "python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-validate",
    ],
    "docs": [
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ],
    "packet_manifests": [
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "zigux/tests/fixtures/genksyms_bridge/manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    ],
    "families": [
        "fixdep",
        "genksyms_bridge",
        "kconfig_bridge",
        "confdata_bridge",
    ],
}

PHASE2_ARTIFACT_TOOLS_MANIFEST_EXPECTED = {
    "packet": "phase2_artifact_tools_manifest",
    "phase": "phase2",
    "status": "current_master_packet",
    "shared_checker": "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "shared_routes": [
        "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
        "python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
        "make -C zigux phase2-validate",
    ],
    "docs": [
        "Documentation/zigux/phase2-closure.md",
        "zigux/tests/README.md",
    ],
    "artifact_tools": [
        "genksyms_crc",
        "mk_elfconfig",
    ],
}

GENKSYMS_BRIDGE_MANIFEST_EXPECTED = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "wrapper-first bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "case_count": 23,
    "cases": [
        "minimal",
        "debug_reference_types",
        "long_options",
        "abbreviated_long_options",
        "ambiguous_long_option",
        "quiet_overrides_warning",
        "explicit_option_terminator",
        "positional_passthrough",
        "lone_dash_passthrough",
        "help",
        "version_then_short_help",
        "version_then_long_help",
        "abbreviated_help",
        "unexpected_help_argument",
        "version",
        "abbreviated_version",
        "invalid_option",
        "missing_reference_argument",
        "missing_dump_types_argument",
        "unsupported_long_option",
        "missing_long_reference_argument",
        "missing_long_dump_types_argument",
        "too_many_reference_files",
    ],
    "stdout_packet": [
        "minimal_expected.json",
        "debug_reference_types_expected.json",
        "long_options_expected.json",
        "abbreviated_long_options_expected.json",
        "quiet_overrides_warning_expected.json",
        "explicit_option_terminator_expected.json",
        "positional_passthrough_expected.json",
        "lone_dash_passthrough_expected.json",
    ],
    "process_packet": [
        "ambiguous_long_option_expected.json",
        "help_expected.json",
        "version_then_help_expected.json",
        "version_then_help_expected.json",
        "help_expected.json",
        "unexpected_help_argument_expected.json",
        "version_expected.json",
        "abbreviated_version_expected.json",
        "invalid_option_expected.json",
        "missing_reference_argument_expected.json",
        "missing_dump_types_argument_expected.json",
        "unsupported_long_option_expected.json",
        "missing_long_reference_argument_expected.json",
        "missing_long_dump_types_argument_expected.json",
        "too_many_reference_files_expected.json",
    ],
    "normalized_stderr_packet": [
        "ambiguous_long_option_expected.json",
        "unexpected_help_argument_expected.json",
        "invalid_option_expected.json",
        "missing_reference_argument_expected.json",
        "missing_dump_types_argument_expected.json",
        "unsupported_long_option_expected.json",
        "missing_long_reference_argument_expected.json",
        "missing_long_dump_types_argument_expected.json",
        "too_many_reference_files_expected.json",
    ],
    "action_abbrev_cases": [
        "abbreviated_long_options",
        "abbreviated_help",
        "abbreviated_version",
    ],
    "helper_local_anchors": [
        "genksyms bridge parses repeated short flags and arguments",
        "genksyms bridge parses long options and quiet override",
        "genksyms bridge keeps version as a side effect while parsing later options",
        "genksyms bridge accepts unambiguous abbreviated long options",
        "genksyms bridge canonicalizes unexpected long option argument failures",
        "genksyms bridge treats lone dash as positional passthrough",
        "genksyms bridge accepts explicit option terminator",
        "genksyms bridge reports invalid short option in getopt style",
        "genksyms bridge reports missing short option argument in getopt style",
        "genksyms bridge rejects more than sixteen reference files like the C harness",
        "genksyms bridge renders normalized invocation plan",
        "genksyms bridge ignores positional args while still parsing later options",
    ],
}

KCONFIG_CONF_MANIFEST_EXPECTED = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "mode": "bounded request-plan bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 16,
    "cases": [
        "oldaskconfig",
        "syncconfig",
        "oldconfig",
        "allnoconfig",
        "allyesconfig",
        "allmodconfig",
        "alldefconfig",
        "randconfig",
        "defconfig",
        "savedefconfig",
        "listnewconfig",
        "helpnewconfig",
        "olddefconfig",
        "yes2modconfig",
        "mod2yesconfig",
        "mod2noconfig",
    ],
    "stdout_packet": [
        "oldaskconfig_expected.json",
        "syncconfig_expected.json",
        "oldconfig_expected.json",
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "allmodconfig_expected.json",
        "alldefconfig_expected.json",
        "randconfig_expected.json",
        "defconfig_expected.json",
        "savedefconfig_expected.json",
        "listnewconfig_expected.json",
        "helpnewconfig_expected.json",
        "olddefconfig_expected.json",
        "yes2modconfig_expected.json",
        "mod2yesconfig_expected.json",
        "mod2noconfig_expected.json",
    ],
    "mode_arg_cases": ["defconfig", "savedefconfig"],
    "silent_request_packet": ["helpnewconfig_expected.json"],
    "syncconfig_env_packet": ["syncconfig_expected.json"],
    "allconfig_sentinel_packet": [
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "alldefconfig_expected.json",
    ],
    "allconfig_override_packet": [
        "allmodconfig_expected.json",
        "randconfig_expected.json",
    ],
    "helper_local_anchors": [
        "conf bridge mode surface stays aligned with conf.c long options",
        "conf bridge emits olddefconfig argv and env",
        "conf bridge emits syncconfig auto files",
        "conf bridge emits syncconfig nosilentupdate when present",
        "conf bridge emits alldefconfig argv and env",
        "conf bridge emits explicit empty allconfig override for allmodconfig",
        "conf bridge emits randconfig tunables when present",
        "conf bridge emits explicit randconfig allconfig override when present",
        "conf bridge emits yes2modconfig argv and env",
        "conf bridge emits defconfig mode argument before kconfig",
        "conf bridge emits savedefconfig mode argument before kconfig",
        "conf bridge escapes low control bytes in JSON strings",
        "bridge options parser accepts explicit allconfig override for allmodconfig",
        "bridge options parser accepts syncconfig nosilentupdate",
    ],
}

KCONFIG_CONFDATA_MANIFEST_EXPECTED = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "mode": "bounded config bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 13,
    "cases": [
        "sample",
        "escaped_strings",
        "escaped_control_sequences",
        "trailing_escaped_backslash",
        "sample_crlf",
        "explicit_n_tristate",
        "final_trailing_carriage_return",
        "final_unterminated_unset_comment",
        "uppercase_tristate",
        "non_config_lines",
        "empty_config_symbol_names",
        "last_state_transitions",
        "duplicate_malformed_quoted_assignment",
    ],
    "input_packet": [
        "sample.config",
        "escaped_strings.config",
        "escaped_control_sequences.config",
        "trailing_escaped_backslash.config",
        "sample_crlf.config",
        "explicit_n_tristate.config",
        "final_trailing_carriage_return.config",
        "final_unterminated_unset_comment.config",
        "uppercase_tristate.config",
        "non_config_lines.config",
        "empty_config_symbol_names.config",
        "last_state_transitions.config",
        "duplicate_malformed_quoted_assignment.config",
    ],
    "expected_packet": [
        "sample_expected.json",
        "escaped_strings_expected.json",
        "escaped_control_sequences_expected.json",
        "trailing_escaped_backslash_expected.json",
        "sample_crlf_expected.json",
        "explicit_n_tristate_expected.json",
        "final_trailing_carriage_return_expected.json",
        "final_unterminated_unset_comment_expected.json",
        "uppercase_tristate_expected.json",
        "non_config_lines_expected.json",
        "empty_config_symbol_names_expected.json",
        "last_state_transitions_expected.json",
        "duplicate_malformed_quoted_assignment_expected.json",
    ],
    "helper_local_anchors": [
        "confdata bridge parses bounded config states",
        "confdata bridge emits bounded json output",
        "confdata bridge decodes escaped quoted strings",
        "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
        "confdata bridge escapes low control bytes in json output",
        "confdata bridge accepts CRLF config lines",
        "confdata bridge preserves trailing carriage return on final unterminated value line",
        "confdata bridge ignores unterminated unset comment with trailing carriage return",
        "confdata bridge keeps explicit n assignments as tristate values",
        "confdata bridge recognizes uppercase tristate assignments",
        "confdata bridge ignores non-CONFIG lines like upstream confdata",
        "confdata bridge ignores empty CONFIG symbol names",
        "confdata bridge keeps trailing escaped backslashes in quoted strings",
        "confdata bridge emits escaped quoted payloads before trailing suffix bytes",
        "confdata bridge leaves malformed quoted values as raw scalar values",
        "confdata bridge emits no entries for empty CONFIG symbol names",
        "confdata bridge keeps only the last assignment for duplicate symbols",
        "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
        "confdata bridge keeps only the last state across unset and set transitions",
    ],
}

PHASE2_CLOSURE_DOC_RELATIVE_PATH = "Documentation/zigux/phase2-closure.md"
PHASE2_CLOSURE_PACKET_SECTION = "## Closure Packet"
PHASE2_REVIEW_NOTES_SECTION = "## Review Notes"
PHASE2_CLOSURE_PACKET_MARKERS = [
    "shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`",
    "shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
]
PHASE2_REVIEW_NOTES_TOOL_MANIFEST_MARKERS = [
    "`zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the committed `fixdep`, `genksyms`, `genksyms_crc`, `mk_elfconfig`, `kconfig`, and `confdata` packet visible to the shared validators instead of leaving the bounded tool tranche implicit",
]
PHASE2_BOOTSTRAP_TOOL_MANIFEST_MARKERS = [
    "the closure note, tests root, and Makefile keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json` plus `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded direct `zig test scripts/zigux/fixdep.zig` replay, the committed genksyms bridge fixture packet, and the checker-backed kconfig bridge plus confdata manifest packet reviewable without reopening the dedicated genksyms or kconfig lanes from this bootstrap note",
]
PHASE2_BOOTSTRAP_STALE_TOOL_MANIFEST_MARKERS = [
    "the closure note, tests root, and Makefile keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json` plus `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded fixdep replay, the committed genksyms and artifact-tools fixtures, and the direct kconfig and confdata Zig replays reviewable without restating missing standalone checker scripts in this dedicated pin-scope note",
]
DOCS_ROOT_PHASE2_TOOL_MANIFEST_MARKERS = [
    "The broader Phase 2 fixdep, genksyms, kconfig bridge, artifact-tools, manifest, cross-target, and closure-route inventory should stay documented through `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile`",
]
SCRIPTS_PHASE2_STALE_NARROW_HELPER_SUMMARY_MARKER = (
    "`check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, "
    "`validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`, "
    "`check-phase2-tests-readme-alignment.py`, `check-phase2-kconfig-readme-alignment.py`, and "
    "`check-phase2-tool-manifest-packets.py` are the live shared scripts-root Phase 2 "
    "helpers on current `master`; the broader `phase2-toolchain`, `phase2-validate`, "
    "`phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` route inventory plus "
    "the dedicated fixdep, genksyms, manifest, cross-target, and bridge checker packet "
    "should stay documented through `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, "
    "`Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` "
    "instead of being implied as missing current-`master` surfaces."
)
SCRIPTS_PHASE2_FULL_HELPER_SUMMARY_MARKER = (
    "`check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, "
    "`validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`, "
    "`check-phase2-tests-readme-alignment.py`, `check-phase2-kconfig-readme-alignment.py`, "
    "`check-phase2-tool-manifest-packets.py`, `check-phase2-fixdep-gate.py`, "
    "`check-fixdep-diff.py`, `check-genksyms-bridge.py`, `check-phase2-cross.py`, "
    "`check-phase2-cross-selftest-alignment.py`, and "
    "`check-phase2-kconfig-selftest-alignment.py` are the live shared scripts-root Phase 2 "
    "helpers on current `master`; the broader `phase2-toolchain`, `phase2-validate`, "
    "`phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` route inventory plus "
    "the dedicated fixdep, genksyms, manifest, cross-target, and bridge checker packet "
    "should stay documented through `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, "
    "`Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` "
    "instead of being implied as missing current-`master` surfaces."
)
SCRIPTS_PHASE2_TOOL_MANIFEST_MARKER = (
    "`check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` "
    "keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json`, "
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, "
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and "
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` packet visible from this scripts "
    "index beside `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, "
    "and `zigux/tests/README.md` instead of letting the shared Phase 2 manifest guard disappear "
    "behind the broader closure note."
)

REQUIRED_FILES = {
    "Documentation/zigux/README.md": [
        *DOCS_ROOT_PHASE2_TOOL_MANIFEST_MARKERS,
    ],
    "scripts/zigux/README.md": [
        "check-phase2-tool-manifest-packets.py --self-test",
        "check-phase2-tool-manifest-packets.py",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        SCRIPTS_PHASE2_FULL_HELPER_SUMMARY_MARKER,
        SCRIPTS_PHASE2_TOOL_MANIFEST_MARKER,
    ],
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": [
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        *PHASE2_BOOTSTRAP_TOOL_MANIFEST_MARKERS,
    ],
    "Documentation/zigux/review-checklist.md": [
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "scripts/zigux/check-phase2-tool-manifest-packets.py",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "scripts/zigux/check-phase2-tool-manifest-packets.py",
    ],
}

EXACT_FILE_MARKER_COUNTS = {
    "Documentation/zigux/README.md": {
        DOCS_ROOT_PHASE2_TOOL_MANIFEST_MARKERS[0]: 1,
    },
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": {
        PHASE2_BOOTSTRAP_TOOL_MANIFEST_MARKERS[0]: 1,
        PHASE2_BOOTSTRAP_STALE_TOOL_MANIFEST_MARKERS[0]: 0,
    },
    "Documentation/zigux/review-checklist.md": {
        "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    },
    "scripts/zigux/README.md": {
        SCRIPTS_PHASE2_TOOL_MANIFEST_MARKER: 1,
        SCRIPTS_PHASE2_STALE_NARROW_HELPER_SUMMARY_MARKER: 0,
        SCRIPTS_PHASE2_FULL_HELPER_SUMMARY_MARKER: 1,
    },
    "zigux/tests/README.md": {
        "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    },
}

PHASE2_CLOSURE_PACKET_EXACT_COUNTS = {
    PHASE2_CLOSURE_PACKET_MARKERS[0]: 1,
    PHASE2_CLOSURE_PACKET_MARKERS[1]: 1,
}

PHASE2_REVIEW_NOTES_EXACT_COUNTS = {
    PHASE2_REVIEW_NOTES_TOOL_MANIFEST_MARKERS[0]: 1,
}


def load_json(path: Path, label: str) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"missing_file:{label}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json:{label}:{exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"invalid_shape:{label}:expected_object"]
    return payload, []


def validate_expected_object(
    payload: dict[str, object], expected: dict[str, object], label: str
) -> list[str]:
    issues: list[str] = []
    if payload != expected:
        for key, expected_value in expected.items():
            actual_value = payload.get(key)
            if actual_value != expected_value:
                issues.append(
                    f"{label}:{key}:expected={expected_value!r}:actual={actual_value!r}"
                )
        for key in sorted(set(payload) - set(expected)):
            issues.append(f"{label}:unexpected_key:{key}")
    return issues


def extract_markdown_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    in_section = False
    collected: list[str] = []
    for line in lines:
        if in_section and line.startswith("## "):
            break
        if in_section:
            collected.append(line)
            continue
        if line == heading:
            in_section = True
    if not in_section:
        return None
    return "\n".join(collected).strip()


def validate_exact_marker_counts(*, text: str, exact_counts: dict[str, int], label: str) -> list[str]:
    issues: list[str] = []
    for marker, expected_count in exact_counts.items():
        count = text.count(marker)
        if count != expected_count:
            issues.append(
                f"exact_count:{label}:{marker}:count={count}:expected={expected_count}"
            )
    return issues


def validate_markdown_section_markers(
    *, text: str, heading: str, markers: list[str], label: str
) -> list[str]:
    section = extract_markdown_section(text, heading)
    if section is None:
        return [f"missing_section:{label}:{heading}"]

    issues: list[str] = []
    for marker in markers:
        if marker not in section:
            issues.append(f"missing_marker:{label}:{marker}")
    return issues


def validate_markdown_section_exact_counts(
    *, text: str, heading: str, exact_counts: dict[str, int], label: str
) -> list[str]:
    section = extract_markdown_section(text, heading)
    if section is None:
        return [f"missing_section:{label}:{heading}"]
    return validate_exact_marker_counts(text=section, exact_counts=exact_counts, label=label)


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []

    closure_doc = root / PHASE2_CLOSURE_DOC_RELATIVE_PATH
    if not closure_doc.is_file():
        issues.append(f"missing_file:{PHASE2_CLOSURE_DOC_RELATIVE_PATH}")
    else:
        closure_text = closure_doc.read_text(encoding="utf-8")
        issues.extend(
            validate_markdown_section_markers(
                text=closure_text,
                heading=PHASE2_CLOSURE_PACKET_SECTION,
                markers=PHASE2_CLOSURE_PACKET_MARKERS,
                label=f"{PHASE2_CLOSURE_DOC_RELATIVE_PATH}:closure_packet",
            )
        )
        issues.extend(
            validate_markdown_section_markers(
                text=closure_text,
                heading=PHASE2_REVIEW_NOTES_SECTION,
                markers=PHASE2_REVIEW_NOTES_TOOL_MANIFEST_MARKERS,
                label=f"{PHASE2_CLOSURE_DOC_RELATIVE_PATH}:review_notes",
            )
        )
        issues.extend(
            validate_markdown_section_exact_counts(
                text=closure_text,
                heading=PHASE2_CLOSURE_PACKET_SECTION,
                exact_counts=PHASE2_CLOSURE_PACKET_EXACT_COUNTS,
                label=f"{PHASE2_CLOSURE_DOC_RELATIVE_PATH}:closure_packet",
            )
        )
        issues.extend(
            validate_markdown_section_exact_counts(
                text=closure_text,
                heading=PHASE2_REVIEW_NOTES_SECTION,
                exact_counts=PHASE2_REVIEW_NOTES_EXACT_COUNTS,
                label=f"{PHASE2_CLOSURE_DOC_RELATIVE_PATH}:review_notes",
            )
        )

    for rel_path, markers in REQUIRED_FILES.items():
        path = root / rel_path
        if not path.is_file():
            issues.append(f"missing_file:{rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{rel_path}:{marker}")
        if rel_path in EXACT_FILE_MARKER_COUNTS:
            issues.extend(
                validate_exact_marker_counts(
                    text=text,
                    exact_counts=EXACT_FILE_MARKER_COUNTS[rel_path],
                    label=rel_path,
                )
            )

    manifest_specs = [
        (PHASE2_TOOL_MANIFEST.relative_to(ROOT), "phase2_tool_manifest", PHASE2_TOOL_MANIFEST_EXPECTED),
        (
            PHASE2_ARTIFACT_TOOLS_MANIFEST.relative_to(ROOT),
            "phase2_artifact_tools_manifest",
            PHASE2_ARTIFACT_TOOLS_MANIFEST_EXPECTED,
        ),
        (GENKSYMS_BRIDGE_MANIFEST.relative_to(ROOT), "genksyms_bridge_manifest", GENKSYMS_BRIDGE_MANIFEST_EXPECTED),
        (KCONFIG_CONF_MANIFEST.relative_to(ROOT), "conf_manifest", KCONFIG_CONF_MANIFEST_EXPECTED),
        (KCONFIG_CONFDATA_MANIFEST.relative_to(ROOT), "confdata_manifest", KCONFIG_CONFDATA_MANIFEST_EXPECTED),
    ]

    for rel_path, label, expected in manifest_specs:
        payload, load_issues = load_json(root / rel_path, label)
        issues.extend(load_issues)
        if payload is not None:
            issues.extend(validate_expected_object(payload, expected, label))

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    docs = {
        PHASE2_CLOSURE_DOC_RELATIVE_PATH: "\n".join(
            [
                "# Phase 2 Closure",
                "",
                PHASE2_CLOSURE_PACKET_SECTION,
                *[f"- {marker}" for marker in PHASE2_CLOSURE_PACKET_MARKERS],
                "",
                PHASE2_REVIEW_NOTES_SECTION,
                *[f"- {marker}" for marker in PHASE2_REVIEW_NOTES_TOOL_MANIFEST_MARKERS],
                "",
            ]
        )
        + "\n",
        "Documentation/zigux/README.md": "\n".join(DOCS_ROOT_PHASE2_TOOL_MANIFEST_MARKERS) + "\n",
        "scripts/zigux/README.md": "\n".join(REQUIRED_FILES["scripts/zigux/README.md"]) + "\n",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": "\n".join(
            REQUIRED_FILES["Documentation/zigux/phase2-toolchain-bootstrap-notes.md"]
        )
        + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(
            REQUIRED_FILES["Documentation/zigux/review-checklist.md"]
        )
        + "\n",
        "zigux/tests/README.md": "\n".join(REQUIRED_FILES["zigux/tests/README.md"]) + "\n",
    }
    for rel_path, content in docs.items():
        write_text(root / rel_path, content)

    manifest_payloads = {
        "zigux/tests/fixtures/phase2_tool_manifest.json": PHASE2_TOOL_MANIFEST_EXPECTED,
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json": PHASE2_ARTIFACT_TOOLS_MANIFEST_EXPECTED,
        "zigux/tests/fixtures/genksyms_bridge/manifest.json": GENKSYMS_BRIDGE_MANIFEST_EXPECTED,
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json": KCONFIG_CONF_MANIFEST_EXPECTED,
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json": KCONFIG_CONFDATA_MANIFEST_EXPECTED,
    }
    for rel_path, payload in manifest_payloads.items():
        write_text(root / rel_path, json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_tool_manifest_packets_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        synthetic_repo = root / "synthetic-repo"
        synthetic_script = synthetic_repo / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"
        assert derive_repo_root(synthetic_script) == synthetic_repo
        case_count += 1

        build_self_test_root(root)
        payload = json.loads((root / "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json").read_text(encoding="utf-8"))
        payload["helper_local_anchors"] = payload["helper_local_anchors"][:-1]
        write_text(
            root / "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
            json.dumps(payload, indent=2) + "\n",
        )
        issues = validate_root(root)
        assert any(issue.startswith("conf_manifest:helper_local_anchors:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        scripts_readme = root / "scripts/zigux/README.md"
        scripts_readme.write_text(
            scripts_readme.read_text(encoding="utf-8") + SCRIPTS_PHASE2_STALE_NARROW_HELPER_SUMMARY_MARKER + "\n",
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            f"exact_count:scripts/zigux/README.md:{SCRIPTS_PHASE2_STALE_NARROW_HELPER_SUMMARY_MARKER}:count=1:expected=0"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        bootstrap_note = root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        bootstrap_note.write_text(
            bootstrap_note.read_text(encoding="utf-8").replace(
                PHASE2_BOOTSTRAP_TOOL_MANIFEST_MARKERS[0],
                PHASE2_BOOTSTRAP_STALE_TOOL_MANIFEST_MARKERS[0],
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            f"missing_marker:Documentation/zigux/phase2-toolchain-bootstrap-notes.md:{PHASE2_BOOTSTRAP_TOOL_MANIFEST_MARKERS[0]}"
            in issues
        )
        assert (
            f"exact_count:Documentation/zigux/phase2-toolchain-bootstrap-notes.md:{PHASE2_BOOTSTRAP_STALE_TOOL_MANIFEST_MARKERS[0]}:count=1:expected=0"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        closure_doc = root / PHASE2_CLOSURE_DOC_RELATIVE_PATH
        closure_doc.write_text(
            closure_doc.read_text(encoding="utf-8").replace(
                f"- {PHASE2_CLOSURE_PACKET_MARKERS[1]}\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            f"missing_marker:{PHASE2_CLOSURE_DOC_RELATIVE_PATH}:closure_packet:{PHASE2_CLOSURE_PACKET_MARKERS[1]}"
            in issues
        )
        case_count += 1

    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Phase 2 tool-manifest packet, bridge manifests, and kbuild wiring."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_TOOL_MANIFEST_PACKETS=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_TOOL_MANIFEST_PACKETS=pass")
    print("PHASE2_TOOL_MANIFEST_PACKETS_REQUIRED_FILE_COUNT=11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
