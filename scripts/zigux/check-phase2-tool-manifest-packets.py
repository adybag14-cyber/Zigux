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
    "case_count": 22,
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
        "unexpected_help_argument_expected.json",
        "version_expected.json",
        "abbreviated_version_expected.json",
        "invalid_option_expected.json",
        "missing_reference_argument_expected.json",
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
}

KCONFIG_CONFDATA_MANIFEST_EXPECTED = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "mode": "bounded config bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 12,
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

REQUIRED_FILES = {
    "scripts/zigux/README.md": [
        "check-phase2-tool-manifest-packets.py --self-test",
        "check-phase2-tool-manifest-packets.py",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    ],
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": [
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
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

    for rel_path, markers in REQUIRED_FILES.items():
        path = root / rel_path
        if not path.is_file():
            issues.append(f"missing_file:{rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{rel_path}:{marker}")

    payload, load_issues = load_json(root / PHASE2_TOOL_MANIFEST.relative_to(ROOT), "phase2_tool_manifest")
    issues.extend(load_issues)
    if payload is not None:
        issues.extend(
            validate_expected_object(payload, PHASE2_TOOL_MANIFEST_EXPECTED, "phase2_tool_manifest")
        )

    payload, load_issues = load_json(
        root / PHASE2_ARTIFACT_TOOLS_MANIFEST.relative_to(ROOT),
        "phase2_artifact_tools_manifest",
    )
    issues.extend(load_issues)
    if payload is not None:
        issues.extend(
            validate_expected_object(
                payload,
                PHASE2_ARTIFACT_TOOLS_MANIFEST_EXPECTED,
                "phase2_artifact_tools_manifest",
            )
        )

    payload, load_issues = load_json(
        root / GENKSYMS_BRIDGE_MANIFEST.relative_to(ROOT),
        "genksyms_bridge_manifest",
    )
    issues.extend(load_issues)
    if payload is not None:
        issues.extend(
            validate_expected_object(
                payload,
                GENKSYMS_BRIDGE_MANIFEST_EXPECTED,
                "genksyms_bridge_manifest",
            )
        )

    payload, load_issues = load_json(
        root / KCONFIG_CONF_MANIFEST.relative_to(ROOT), "conf_manifest"
    )
    issues.extend(load_issues)
    if payload is not None:
        issues.extend(validate_expected_object(payload, KCONFIG_CONF_MANIFEST_EXPECTED, "conf_manifest"))

    payload, load_issues = load_json(
        root / KCONFIG_CONFDATA_MANIFEST.relative_to(ROOT), "confdata_manifest"
    )
    issues.extend(load_issues)
    if payload is not None:
        issues.extend(
            validate_expected_object(payload, KCONFIG_CONFDATA_MANIFEST_EXPECTED, "confdata_manifest")
        )

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
        ),
        "scripts/zigux/README.md": "\n".join(REQUIRED_FILES["scripts/zigux/README.md"]) + "\n",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": "\n".join(
            REQUIRED_FILES["Documentation/zigux/phase2-toolchain-bootstrap-notes.md"]
        )
        + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REQUIRED_FILES["Documentation/zigux/review-checklist.md"]) + "\n",
        "zigux/tests/README.md": "\n".join(REQUIRED_FILES["zigux/tests/README.md"]) + "\n",
    }
    for rel_path, content in docs.items():
        write_text(root / rel_path, content)

    write_text(
        root / "zigux/tests/fixtures/phase2_tool_manifest.json",
        json.dumps(PHASE2_TOOL_MANIFEST_EXPECTED, indent=2) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        json.dumps(PHASE2_ARTIFACT_TOOLS_MANIFEST_EXPECTED, indent=2) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/genksyms_bridge/manifest.json",
        json.dumps(GENKSYMS_BRIDGE_MANIFEST_EXPECTED, indent=2) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        json.dumps(KCONFIG_CONF_MANIFEST_EXPECTED, indent=2) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        json.dumps(KCONFIG_CONFDATA_MANIFEST_EXPECTED, indent=2) + "\n",
    )


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
        payload = json.loads((root / "zigux/tests/fixtures/phase2_tool_manifest.json").read_text(encoding="utf-8"))
        payload["families"].append("unexpected")
        write_text(
            root / "zigux/tests/fixtures/phase2_tool_manifest.json",
            json.dumps(payload, indent=2) + "\n",
        )
        issues = validate_root(root)
        assert "phase2_tool_manifest:families:expected=['fixdep', 'genksyms_bridge', 'kconfig_bridge', 'confdata_bridge']:actual=['fixdep', 'genksyms_bridge', 'kconfig_bridge', 'confdata_bridge', 'unexpected']" in issues
        case_count += 1

        build_self_test_root(root)
        payload = json.loads((root / "zigux/tests/fixtures/genksyms_bridge/manifest.json").read_text(encoding="utf-8"))
        payload["case_count"] = 21
        write_text(
            root / "zigux/tests/fixtures/genksyms_bridge/manifest.json",
            json.dumps(payload, indent=2) + "\n",
        )
        issues = validate_root(root)
        assert "genksyms_bridge_manifest:case_count:expected=22:actual=21" in issues
        case_count += 1

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json").unlink()
        issues = validate_root(root)
        assert "missing_file:confdata_manifest" in issues
        case_count += 1

        build_self_test_root(root)
        scripts_readme = root / "scripts/zigux/README.md"
        scripts_readme.write_text(
            scripts_readme.read_text(encoding="utf-8").replace(
                "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            "missing_marker:scripts/zigux/README.md:zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        bootstrap_notes = root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        bootstrap_notes.write_text(
            bootstrap_notes.read_text(encoding="utf-8").replace(
                "zigux/tests/fixtures/phase2_artifact_tools_manifest.json\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            "missing_marker:Documentation/zigux/phase2-toolchain-bootstrap-notes.md:zigux/tests/fixtures/phase2_artifact_tools_manifest.json"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        review_checklist = root / "Documentation/zigux/review-checklist.md"
        review_checklist.write_text(
            review_checklist.read_text(encoding="utf-8").replace(
                "scripts/zigux/check-phase2-tool-manifest-packets.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            "missing_marker:Documentation/zigux/review-checklist.md:scripts/zigux/check-phase2-tool-manifest-packets.py"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        closure_doc = root / PHASE2_CLOSURE_DOC_RELATIVE_PATH
        closure_doc.write_text(
            closure_doc.read_text(encoding="utf-8").replace(
                "- shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`\n",
                "",
                1,
            )
            + "\n- shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`\n",
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            "missing_marker:Documentation/zigux/phase2-closure.md:closure_packet:shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        closure_doc = root / PHASE2_CLOSURE_DOC_RELATIVE_PATH
        closure_doc.write_text(
            closure_doc.read_text(encoding="utf-8").replace(
                "- `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the committed `fixdep`, `genksyms`, `genksyms_crc`, `mk_elfconfig`, `kconfig`, and `confdata` packet visible to the shared validators instead of leaving the bounded tool tranche implicit\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            "missing_marker:Documentation/zigux/phase2-closure.md:review_notes:`zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the committed `fixdep`, `genksyms`, `genksyms_crc`, `mk_elfconfig`, `kconfig`, and `confdata` packet visible to the shared validators instead of leaving the bounded tool tranche implicit"
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
    print("PHASE2_TOOL_MANIFEST_PACKETS_REQUIRED_FILE_COUNT=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
