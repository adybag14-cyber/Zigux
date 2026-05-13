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

GENKSYMS_TOOL_REL = "scripts/zigux/genksyms.zig"
GENKSYMS_CHECKER_REL = "scripts/zigux/check-genksyms-bridge.py"
GENKSYMS_CASES_REL = "zigux/tests/fixtures/genksyms_bridge/cases.json"
GENKSYMS_MANIFEST_REL = "zigux/tests/fixtures/genksyms_bridge/manifest.json"
PHASE2_TOOL_MANIFEST_REL = "zigux/tests/fixtures/phase2_tool_manifest.json"
PHASE2_CLOSURE_REL = "Documentation/zigux/phase2-closure.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

EXPECTED_GENKSYMS_CASES = [
    {
        "name": "minimal",
        "argv": [],
        "mode": "stdout_json",
        "expected": "minimal_expected.json",
    },
    {
        "name": "debug_reference_types",
        "argv": [
            "-d",
            "-d",
            "-D",
            "-w",
            "-p",
            "-r",
            "foo.symref",
            "-r",
            "bar.symref",
            "-T",
            "out.symtypes",
        ],
        "mode": "stdout_json",
        "expected": "debug_reference_types_expected.json",
    },
    {
        "name": "long_options",
        "argv": [
            "--debug",
            "--warnings",
            "--quiet",
            "--reference=foo.symref",
            "--dump-types",
            "types.symtypes",
            "--preserve",
        ],
        "mode": "stdout_json",
        "expected": "long_options_expected.json",
    },
    {
        "name": "abbreviated_long_options",
        "argv": [
            "--deb",
            "--warn",
            "--qui",
            "--ref=foo.symref",
            "--dump-t",
            "types.symtypes",
            "--pres",
        ],
        "mode": "stdout_json",
        "expected": "abbreviated_long_options_expected.json",
    },
    {
        "name": "ambiguous_long_option",
        "argv": ["--d"],
        "mode": "process_json",
        "expected": "ambiguous_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "quiet_overrides_warning",
        "argv": ["-w", "-q"],
        "mode": "stdout_json",
        "expected": "quiet_overrides_warning_expected.json",
    },
    {
        "name": "explicit_option_terminator",
        "argv": ["--", "--leftover", "positional"],
        "mode": "stdout_json",
        "expected": "explicit_option_terminator_expected.json",
    },
    {
        "name": "positional_passthrough",
        "argv": ["leftover.c", "-d", "rightover.h", "-r", "foo.symref"],
        "mode": "stdout_json",
        "expected": "positional_passthrough_expected.json",
    },
    {
        "name": "lone_dash_passthrough",
        "argv": ["-", "-d"],
        "mode": "stdout_json",
        "expected": "lone_dash_passthrough_expected.json",
    },
    {
        "name": "help",
        "argv": ["-h"],
        "mode": "process_json",
        "expected": "help_expected.json",
    },
    {
        "name": "version_then_short_help",
        "argv": ["-Vh"],
        "mode": "process_json",
        "expected": "version_then_help_expected.json",
    },
    {
        "name": "version_then_long_help",
        "argv": ["-V", "--help"],
        "mode": "process_json",
        "expected": "version_then_help_expected.json",
    },
    {
        "name": "abbreviated_help",
        "argv": ["--he"],
        "mode": "process_json",
        "expected": "help_expected.json",
    },
    {
        "name": "unexpected_help_argument",
        "argv": ["--help=extra"],
        "mode": "process_json",
        "expected": "unexpected_help_argument_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "version",
        "argv": ["--version"],
        "mode": "process_json",
        "expected": "version_expected.json",
    },
    {
        "name": "abbreviated_version",
        "argv": ["--ver"],
        "mode": "process_json",
        "expected": "abbreviated_version_expected.json",
    },
    {
        "name": "invalid_option",
        "argv": ["-x"],
        "mode": "process_json",
        "expected": "invalid_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "missing_reference_argument",
        "argv": ["-r"],
        "mode": "process_json",
        "expected": "missing_reference_argument_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "unsupported_long_option",
        "argv": ["--unknown"],
        "mode": "process_json",
        "expected": "unsupported_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "missing_long_reference_argument",
        "argv": ["--reference"],
        "mode": "process_json",
        "expected": "missing_long_reference_argument_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "missing_long_dump_types_argument",
        "argv": ["--dump-types"],
        "mode": "process_json",
        "expected": "missing_long_dump_types_argument_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "too_many_reference_files",
        "argv": [
            "-r",
            "01.symref",
            "-r",
            "02.symref",
            "-r",
            "03.symref",
            "-r",
            "04.symref",
            "-r",
            "05.symref",
            "-r",
            "06.symref",
            "-r",
            "07.symref",
            "-r",
            "08.symref",
            "-r",
            "09.symref",
            "-r",
            "10.symref",
            "-r",
            "11.symref",
            "-r",
            "12.symref",
            "-r",
            "13.symref",
            "-r",
            "14.symref",
            "-r",
            "15.symref",
            "-r",
            "16.symref",
            "-r",
            "17.symref",
        ],
        "mode": "process_json",
        "expected": "too_many_reference_files_expected.json",
        "normalize_stderr": True,
    },
]

EXPECTED_GENKSYMS_MANIFEST = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "wrapper-first bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": GENKSYMS_CASES_REL,
    "case_count": len(EXPECTED_GENKSYMS_CASES),
    "cases": [case["name"] for case in EXPECTED_GENKSYMS_CASES],
    "stdout_packet": [
        case["expected"] for case in EXPECTED_GENKSYMS_CASES if case["mode"] == "stdout_json"
    ],
    "process_packet": [
        case["expected"] for case in EXPECTED_GENKSYMS_CASES if case["mode"] == "process_json"
    ],
    "normalized_stderr_packet": [
        case["expected"]
        for case in EXPECTED_GENKSYMS_CASES
        if case["mode"] == "process_json" and case.get("normalize_stderr") is True
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

EXPECTED_WORKFLOW_LINES = [
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
]

EXPECTED_TESTS_README_MARKERS = [
    "scripts/zigux/check-genksyms-bridge.py",
    "the shipped genksyms bridge direct replay",
]

EXPECTED_CLOSURE_MARKERS = [
    "committed genksyms bridge fixture packet: `zigux/tests/fixtures/genksyms_bridge/`",
    "the dedicated `Phase 2 genksyms` bridge packet remains the live `22-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`",
]

EXPECTED_SELF_TEST_CASE_COUNT = 16


def load_json(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"missing_file:{label}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json:{label}:{exc.msg}"]


def validate_expected_object(
    payload: dict[str, object], expected: dict[str, object], label: str
) -> list[str]:
    issues: list[str] = []
    if payload != expected:
        for key, expected_value in expected.items():
            actual_value = payload.get(key)
            if actual_value != expected_value:
                issues.append(f"{label}:{key}:expected={expected_value!r}:actual={actual_value!r}")
        for key in sorted(set(payload) - set(expected)):
            issues.append(f"{label}:unexpected_key:{key}")
    return issues


def validate_expected_case_list(payload: object, label: str) -> list[str]:
    if not isinstance(payload, list):
        return [f"invalid_shape:{label}:expected_list"]

    issues: list[str] = []
    if payload != EXPECTED_GENKSYMS_CASES:
        if len(payload) != len(EXPECTED_GENKSYMS_CASES):
            issues.append(
                f"{label}:case_count:expected={len(EXPECTED_GENKSYMS_CASES)!r}:actual={len(payload)!r}"
            )
        actual_names = [item.get("name") for item in payload if isinstance(item, dict)]
        expected_names = [case["name"] for case in EXPECTED_GENKSYMS_CASES]
        if actual_names != expected_names:
            issues.append(f"{label}:names:expected={expected_names!r}:actual={actual_names!r}")
        for index, expected_case in enumerate(EXPECTED_GENKSYMS_CASES):
            if index >= len(payload):
                break
            actual_case = payload[index]
            if not isinstance(actual_case, dict):
                issues.append(
                    f"{label}:entry:{index}:expected_object:actual={type(actual_case).__name__}"
                )
                continue
            for key, expected_value in expected_case.items():
                actual_value = actual_case.get(key)
                if actual_value != expected_value:
                    issues.append(
                        f"{label}:{expected_case['name']}:{key}:expected={expected_value!r}:actual={actual_value!r}"
                    )
            for key in sorted(set(actual_case) - set(expected_case)):
                issues.append(f"{label}:{expected_case['name']}:unexpected_key:{key}")

    fixture_root = Path(EXPECTED_GENKSYMS_MANIFEST["fixture_root"])
    for case in payload:
        if not isinstance(case, dict):
            continue
        expected_path = fixture_root / str(case.get("expected", ""))
        if not expected_path.name:
            issues.append(f"{label}:{case.get('name', '<unnamed>')}:missing_expected")
        elif not (ROOT / expected_path).is_file():
            issues.append(f"missing_file:{expected_path.as_posix()}")
    return issues


def validate_markers(text: str, markers: list[str], label: str) -> list[str]:
    return [f"missing_marker:{label}:{marker}" for marker in markers if marker not in text]


def validate_exact_counts(text: str, markers: list[str], label: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"exact_count:{label}:{marker}:count={count}:expected=1")
    return issues


def validate_line_counts(text: str, markers: list[str], label: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            issues.append(f"line_count:{label}:{marker}:count={count}:expected=1")
    return issues


def validate_helper_local_anchors(text: str, anchors: list[str]) -> list[str]:
    issues: list[str] = []
    for anchor in anchors:
        marker = f'test "{anchor}"'
        count = text.count(marker)
        if count != 1:
            issues.append(f"anchor_count:{marker}:count={count}:expected=1")
    return issues


def validate_phase2_tool_manifest(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    packet_manifests = payload.get("packet_manifests")
    if not isinstance(packet_manifests, list) or GENKSYMS_MANIFEST_REL not in packet_manifests:
        issues.append(f"phase2_tool_manifest:missing_packet_manifest:{GENKSYMS_MANIFEST_REL}")
    families = payload.get("families")
    if not isinstance(families, list) or "genksyms_bridge" not in families:
        issues.append("phase2_tool_manifest:missing_family:genksyms_bridge")
    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    required = [
        GENKSYMS_TOOL_REL,
        GENKSYMS_CASES_REL,
        GENKSYMS_MANIFEST_REL,
        PHASE2_TOOL_MANIFEST_REL,
        PHASE2_CLOSURE_REL,
        TESTS_README_REL,
        WORKFLOW_REL,
    ]
    for rel_path in required:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path}")

    if issues:
        return issues

    genksyms_cases, load_issues = load_json(root / GENKSYMS_CASES_REL, "genksyms_cases")
    issues.extend(load_issues)
    if genksyms_cases is not None:
        root_for_paths = ROOT
        try:
            globals()["ROOT"] = root
            issues.extend(validate_expected_case_list(genksyms_cases, "genksyms_cases"))
        finally:
            globals()["ROOT"] = root_for_paths

    genksyms_manifest, load_issues = load_json(root / GENKSYMS_MANIFEST_REL, "genksyms_manifest")
    issues.extend(load_issues)
    if isinstance(genksyms_manifest, dict):
        issues.extend(
            validate_expected_object(
                genksyms_manifest, EXPECTED_GENKSYMS_MANIFEST, "genksyms_manifest"
            )
        )
    elif genksyms_manifest is not None:
        issues.append("invalid_shape:genksyms_manifest:expected_object")

    phase2_tool_manifest, load_issues = load_json(
        root / PHASE2_TOOL_MANIFEST_REL, "phase2_tool_manifest"
    )
    issues.extend(load_issues)
    if isinstance(phase2_tool_manifest, dict):
        issues.extend(validate_phase2_tool_manifest(phase2_tool_manifest))
    elif phase2_tool_manifest is not None:
        issues.append("invalid_shape:phase2_tool_manifest:expected_object")

    genksyms_text = (root / GENKSYMS_TOOL_REL).read_text(encoding="utf-8")
    issues.extend(
        validate_helper_local_anchors(
            genksyms_text, EXPECTED_GENKSYMS_MANIFEST["helper_local_anchors"]
        )
    )

    tests_readme = (root / TESTS_README_REL).read_text(encoding="utf-8")
    issues.extend(validate_markers(tests_readme, EXPECTED_TESTS_README_MARKERS, TESTS_README_REL))
    issues.extend(
        validate_exact_counts(tests_readme, EXPECTED_TESTS_README_MARKERS, TESTS_README_REL)
    )

    closure_text = (root / PHASE2_CLOSURE_REL).read_text(encoding="utf-8")
    issues.extend(validate_markers(closure_text, EXPECTED_CLOSURE_MARKERS, PHASE2_CLOSURE_REL))
    issues.extend(validate_exact_counts(closure_text, EXPECTED_CLOSURE_MARKERS, PHASE2_CLOSURE_REL))

    workflow_text = (root / WORKFLOW_REL).read_text(encoding="utf-8")
    issues.extend(validate_line_counts(workflow_text, EXPECTED_WORKFLOW_LINES, WORKFLOW_REL))

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / GENKSYMS_CASES_REL,
        json.dumps(EXPECTED_GENKSYMS_CASES, indent=2) + "\n",
    )
    write_text(
        root / GENKSYMS_MANIFEST_REL,
        json.dumps(EXPECTED_GENKSYMS_MANIFEST, indent=2) + "\n",
    )
    write_text(
        root / PHASE2_TOOL_MANIFEST_REL,
        json.dumps(
            {
                "packet": "phase2_tool_manifest",
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
                    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
                    "Documentation/zigux/review-checklist.md",
                    "zigux/tests/README.md",
                ],
                "packet_manifests": [
                    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
                    GENKSYMS_MANIFEST_REL,
                    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
                    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
                ],
                "families": [
                    "fixdep",
                    "genksyms_bridge",
                    "kconfig_bridge",
                    "confdata_bridge",
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / GENKSYMS_TOOL_REL,
        "\n".join(
            f'test "{anchor}" {{}}'
            for anchor in EXPECTED_GENKSYMS_MANIFEST["helper_local_anchors"]
        )
        + "\n",
    )
    write_text(
        root / TESTS_README_REL,
        "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n",
    )
    write_text(
        root / PHASE2_CLOSURE_REL,
        "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / WORKFLOW_REL,
        "\n".join(EXPECTED_WORKFLOW_LINES) + "\n",
    )
    fixture_root = root / "zigux" / "tests" / "fixtures" / "genksyms_bridge"
    for filename in sorted(
        {
            case["expected"] for case in EXPECTED_GENKSYMS_CASES
        }
    ):
        write_text(fixture_root / filename, "{}\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_genksyms_bridge_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        synthetic_repo = root / "synthetic-repo"
        synthetic_script = synthetic_repo / "scripts" / "zigux" / "check-genksyms-bridge.py"
        assert derive_repo_root(synthetic_script) == synthetic_repo
        case_count += 1

        build_self_test_root(root)
        (root / GENKSYMS_CASES_REL).unlink()
        issues = validate_root(root)
        assert f"missing_file:{GENKSYMS_CASES_REL}" in issues
        case_count += 1

        build_self_test_root(root)
        payload = json.loads((root / GENKSYMS_CASES_REL).read_text(encoding="utf-8"))
        payload.pop()
        write_text(root / GENKSYMS_CASES_REL, json.dumps(payload, indent=2) + "\n")
        issues = validate_root(root)
        assert "genksyms_cases:case_count:expected=22:actual=21" in issues
        assert "genksyms_cases:names:expected=['minimal', 'debug_reference_types', 'long_options', 'abbreviated_long_options', 'ambiguous_long_option', 'quiet_overrides_warning', 'explicit_option_terminator', 'positional_passthrough', 'lone_dash_passthrough', 'help', 'version_then_short_help', 'version_then_long_help', 'abbreviated_help', 'unexpected_help_argument', 'version', 'abbreviated_version', 'invalid_option', 'missing_reference_argument', 'unsupported_long_option', 'missing_long_reference_argument', 'missing_long_dump_types_argument', 'too_many_reference_files']:actual=['minimal', 'debug_reference_types', 'long_options', 'abbreviated_long_options', 'ambiguous_long_option', 'quiet_overrides_warning', 'explicit_option_terminator', 'positional_passthrough', 'lone_dash_passthrough', 'help', 'version_then_short_help', 'version_then_long_help', 'abbreviated_help', 'unexpected_help_argument', 'version', 'abbreviated_version', 'invalid_option', 'missing_reference_argument', 'unsupported_long_option', 'missing_long_reference_argument', 'missing_long_dump_types_argument']" in issues
        case_count += 1

        build_self_test_root(root)
        payload = json.loads((root / GENKSYMS_CASES_REL).read_text(encoding="utf-8"))
        payload[13]["normalize_stderr"] = False
        write_text(root / GENKSYMS_CASES_REL, json.dumps(payload, indent=2) + "\n")
        issues = validate_root(root)
        assert "genksyms_cases:unexpected_help_argument:normalize_stderr:expected=True:actual=False" in issues
        case_count += 1

        build_self_test_root(root)
        payload = json.loads((root / GENKSYMS_CASES_REL).read_text(encoding="utf-8"))
        payload[0]["expected"] = "renamed_expected.json"
        write_text(root / GENKSYMS_CASES_REL, json.dumps(payload, indent=2) + "\n")
        issues = validate_root(root)
        assert "genksyms_cases:minimal:expected:expected='minimal_expected.json':actual='renamed_expected.json'" in issues
        assert "missing_file:zigux/tests/fixtures/genksyms_bridge/renamed_expected.json" in issues
        case_count += 1

        build_self_test_root(root)
        payload = json.loads((root / GENKSYMS_CASES_REL).read_text(encoding="utf-8"))
        payload[0]["argv"] = "--broken"
        write_text(root / GENKSYMS_CASES_REL, json.dumps(payload, indent=2) + "\n")
        issues = validate_root(root)
        assert "genksyms_cases:minimal:argv:expected=[]:actual='--broken'" in issues
        case_count += 1

        build_self_test_root(root)
        manifest = json.loads((root / GENKSYMS_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["fixture_case_source"] = "zigux/tests/fixtures/genksyms_bridge/missing.json"
        write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate_root(root)
        assert (
            "genksyms_manifest:fixture_case_source:expected='zigux/tests/fixtures/genksyms_bridge/cases.json':actual='zigux/tests/fixtures/genksyms_bridge/missing.json'"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(EXPECTED_WORKFLOW_LINES[0] + "\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            f"line_count:{WORKFLOW_REL}:{EXPECTED_WORKFLOW_LINES[0]}:count=0:expected=1" in issues
        )
        case_count += 1

        build_self_test_root(root)
        phase2_tool_manifest = json.loads((root / PHASE2_TOOL_MANIFEST_REL).read_text(encoding="utf-8"))
        phase2_tool_manifest["packet_manifests"] = [
            manifest
            for manifest in phase2_tool_manifest["packet_manifests"]
            if manifest != GENKSYMS_MANIFEST_REL
        ]
        write_text(
            root / PHASE2_TOOL_MANIFEST_REL,
            json.dumps(phase2_tool_manifest, indent=2) + "\n",
        )
        issues = validate_root(root)
        assert f"phase2_tool_manifest:missing_packet_manifest:{GENKSYMS_MANIFEST_REL}" in issues
        case_count += 1

        build_self_test_root(root)
        tests_readme_path = root / TESTS_README_REL
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(
                EXPECTED_TESTS_README_MARKERS[0] + "\n", "", 1
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert f"missing_marker:{TESTS_README_REL}:{EXPECTED_TESTS_README_MARKERS[0]}" in issues
        assert (
            f"exact_count:{TESTS_README_REL}:{EXPECTED_TESTS_README_MARKERS[0]}:count=0:expected=1"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                EXPECTED_CLOSURE_MARKERS[1] + "\n", "", 1
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert f"missing_marker:{PHASE2_CLOSURE_REL}:{EXPECTED_CLOSURE_MARKERS[1]}" in issues
        assert (
            f"exact_count:{PHASE2_CLOSURE_REL}:{EXPECTED_CLOSURE_MARKERS[1]}:count=0:expected=1"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        genksyms_path = root / GENKSYMS_TOOL_REL
        genksyms_path.write_text(
            genksyms_path.read_text(encoding="utf-8").replace(
                f'test "{EXPECTED_GENKSYMS_MANIFEST["helper_local_anchors"][0]}" {{}}\n', "", 1
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            f'anchor_count:test "{EXPECTED_GENKSYMS_MANIFEST["helper_local_anchors"][0]}":count=0:expected=1'
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        fixture_path = root / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "unexpected_help_argument_expected.json"
        fixture_path.unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/genksyms_bridge/unexpected_help_argument_expected.json" in issues
        case_count += 1

        build_self_test_root(root)
        write_text(root / GENKSYMS_CASES_REL, "{\n")
        issues = validate_root(root)
        assert "invalid_json:genksyms_cases:Expecting property name enclosed in double quotes" in issues
        case_count += 1

        build_self_test_root(root)
        write_text(root / GENKSYMS_CASES_REL, json.dumps({"cases": EXPECTED_GENKSYMS_CASES}, indent=2) + "\n")
        issues = validate_root(root)
        assert "invalid_shape:genksyms_cases:expected_list" in issues
        case_count += 1

    assert case_count == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 2 genksyms bridge packet and workflow wiring."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_GENKSYMS_BRIDGE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_GENKSYMS_BRIDGE=pass")
    print(
        f"PHASE2_GENKSYMS_BRIDGE_HELPER_ANCHOR_COUNT={len(EXPECTED_GENKSYMS_MANIFEST['helper_local_anchors'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
