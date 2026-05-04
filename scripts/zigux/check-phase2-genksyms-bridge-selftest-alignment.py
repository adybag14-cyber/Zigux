#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

REQUIRED_FILES = {
    "bridge_checker": "scripts/zigux/check-genksyms-bridge.py",
    "readme": "scripts/zigux/README.md",
    "closure_doc": "Documentation/zigux/phase2-closure.md",
    "closure_validator": "scripts/zigux/validate-phase2-closure.py",
    "validator": "scripts/zigux/validate-phase2.py",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "makefile": "zigux/Makefile",
    "cases": "zigux/tests/fixtures/genksyms_bridge/cases.json",
}

CASE_NAME_ORDER = [
    "minimal",
    "debug_reference_types",
    "short_inline_reference_dump_types",
    "clustered_short_inline_reference",
    "long_options",
    "abbreviated_long_options",
    "quiet_overrides_warning",
    "explicit_option_terminator",
    "positional_passthrough",
    "lone_dash_passthrough",
    "explicit_terminator_positional_passthrough",
    "help",
    "version",
    "invalid_option",
    "missing_reference_argument",
    "missing_dump_types_argument",
    "unsupported_long_option",
    "ambiguous_abbreviated_long_option",
    "empty_long_option_name",
    "unexpected_long_option_argument",
    "abbreviated_unexpected_long_option_argument",
    "missing_long_reference_argument",
    "abbreviated_missing_long_reference_argument",
    "missing_long_dump_types_argument",
    "abbreviated_missing_long_dump_types_argument",
    "too_many_reference_files",
]

README_MARKERS = [
    "`check-genksyms-bridge.py --self-test` exercises the bounded `genksyms` bridge checker packet itself before the Linux-style `phase2-tools` entrypoint replays live bridge artifacts, so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing bridge replay.",
    "that same committed bridge packet currently spans 26 reviewable cases under `zigux/tests/fixtures/genksyms_bridge/`, including the minimal, clustered short-inline, abbreviated long-option, lone-dash passthrough, explicit-terminator positional, missing-argument, and reference-limit fixtures that keep the widened wrapper-first surface explicit.",
    "`scripts/genksyms/genksyms.c` remains the authoritative parser and export engine for parser-heavy symbol semantics, while `scripts/zigux/genksyms.zig` is intentionally limited to the bounded getopt-style wrapper-first bridge that Phase 2 can prove safely.",
]

CLOSURE_DOC_MARKERS = [
    "- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`",
    "- `PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=26`",
    "- `PHASE2_GENKSYMS_BRIDGE_DETERMINISM=check-genksyms-bridge.py replays C and Zig bridge outputs twice before comparing artifacts`",
    "- `PHASE2_GENKSYMS_BRIDGE_STDERR_POLICY=success-path stderr silence plus repeat-run stderr determinism are required for closure`",
    "- `PHASE2_GENKSYMS_IMPLEMENTATION_BOUNDARY=scripts/genksyms/genksyms.c remains authoritative for parser-heavy symbol parsing and export semantics while scripts/zigux/genksyms.zig stays a bounded wrapper-first getopt bridge`",
]

VALIDATOR_MARKERS = [
    "PHASE2_GENKSYMS_BRIDGE_REQUIRED_SOURCE_MARKERS",
    "PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26",
    "print('GENKSYMS_BRIDGE_DETERMINISM=pass')",
    "\"python3 scripts/zigux/check-genksyms-bridge.py --self-test\": 1,",
    "\"python3 scripts/zigux/check-genksyms-bridge.py\": 1,",
]

CLOSURE_VALIDATOR_MARKERS = [
    "'python3 scripts/zigux/check-genksyms-bridge.py --self-test': 1,",
    "'python3 scripts/zigux/check-genksyms-bridge.py': 1,",
    "'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test': 1,",
    "'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py': 1,",
    "PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=26",
    "PHASE2_GENKSYMS_BRIDGE_DETERMINISM=check-genksyms-bridge.py replays C and Zig bridge outputs twice before comparing artifacts",
]

BRIDGE_CHECKER_MARKERS = [
    "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')",
    "print('GENKSYMS_BRIDGE_DETERMINISM=pass')",
]

WORKFLOW_COUNTS = {
    "python3 scripts/zigux/validate-phase2.py": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/validate-phase2-closure.py": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "zig test scripts/zigux/genksyms.zig": 1,
}

WORKFLOW_ORDER = [
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "zig test scripts/zigux/genksyms.zig",
]

MAKEFILE_VALIDATE_COUNTS = {
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "scripts/zigux/validate-phase2.py": 1,
    "scripts/zigux/validate-phase2-closure.py": 1,
}

MAKEFILE_VALIDATE_ORDER = [
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
]

MAKEFILE_TOOL_COUNTS = {
    "scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "scripts/zigux/check-genksyms-bridge.py": 1,
    "$(ZIG) test scripts/zigux/genksyms.zig": 1,
}


def resolve_root() -> Path:
    args = sys.argv[1:]
    if "--root" in args:
        index = args.index("--root")
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    if "ZIGUX_PHASE2_ROOT" in os.environ:
        return Path(os.environ["ZIGUX_PHASE2_ROOT"]).resolve()
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_order(lines: list[str], commands: list[str], prefix: str) -> list[str]:
    issues: list[str] = []
    positions: dict[str, int] = {}
    for command in commands:
        for index, line in enumerate(lines):
            if line == command or line.endswith(command):
                positions[command] = index
                break
    for before, after in zip(commands, commands[1:]):
        if before in positions and after in positions and positions[before] >= positions[after]:
            issues.append(f"{prefix}:{before}:before:{after}")
    return issues


def validate_cases(root: Path) -> list[str]:
    payload = json.loads(read_text(root, REQUIRED_FILES["cases"]))
    if not isinstance(payload, dict):
        return ["cases:expected_top_level_object"]
    cases = payload.get("cases")
    if not isinstance(cases, list):
        return ["cases:expected_list"]

    issues: list[str] = []
    names = [case.get("name") for case in cases if isinstance(case, dict)]
    if len(cases) != 26:
        issues.append(f"cases:count={len(cases)}:expected=26")
    if names != CASE_NAME_ORDER:
        issues.append("cases:names=expected_exact_case_order")

    by_name = {
        case.get("name"): case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("name"), str)
    }

    help_case = by_name.get("help", {})
    if help_case.get("mode") != "process_json":
        issues.append("cases:help:mode=process_json")
    if help_case.get("argv") != ["--hel"]:
        issues.append("cases:help:argv=['--hel']")

    version_case = by_name.get("version", {})
    if version_case.get("mode") != "process_json":
        issues.append("cases:version:mode=process_json")
    if version_case.get("argv") != ["--ver"]:
        issues.append("cases:version:argv=['--ver']")
    if version_case.get("expected") != "version_expected.json":
        issues.append("cases:version:expected=version_expected.json")

    invalid_case = by_name.get("invalid_option", {})
    if invalid_case.get("normalize_stderr") is not True:
        issues.append("cases:invalid_option:normalize_stderr=true")

    missing_dump_case = by_name.get("abbreviated_missing_long_dump_types_argument", {})
    if missing_dump_case.get("expected") != "abbreviated_missing_long_dump_types_argument_expected.json":
        issues.append("cases:abbreviated_missing_long_dump_types_argument:expected_file")
    if missing_dump_case.get("mode") != "process_json":
        issues.append("cases:abbreviated_missing_long_dump_types_argument:mode=process_json")

    too_many_refs = by_name.get("too_many_reference_files", {})
    if too_many_refs.get("mode") != "process_json":
        issues.append("cases:too_many_reference_files:mode=process_json")

    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            issues.append(f"missing:{label}:{rel_path}")
    if issues:
        return issues

    bridge_checker = read_text(root, REQUIRED_FILES["bridge_checker"])
    readme = read_text(root, REQUIRED_FILES["readme"])
    closure_doc = read_text(root, REQUIRED_FILES["closure_doc"])
    closure_validator = read_text(root, REQUIRED_FILES["closure_validator"])
    validator = read_text(root, REQUIRED_FILES["validator"])
    workflow = read_text(root, REQUIRED_FILES["workflow"])
    makefile = read_text(root, REQUIRED_FILES["makefile"])

    for marker in BRIDGE_CHECKER_MARKERS:
        if marker not in bridge_checker:
            issues.append(f"bridge_checker:{marker}")
    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(f"readme:{marker}")
    for marker in CLOSURE_DOC_MARKERS:
        if marker not in closure_doc:
            issues.append(f"closure_doc:{marker}")
    for marker in VALIDATOR_MARKERS:
        if marker not in validator:
            issues.append(f"validator:{marker}")
    for marker in CLOSURE_VALIDATOR_MARKERS:
        if marker not in closure_validator:
            issues.append(f"closure_validator:{marker}")

    workflow_lines = [line.strip() for line in workflow.splitlines()]
    for command, expected_count in WORKFLOW_COUNTS.items():
        count = sum(1 for line in workflow_lines if line == f"run: {command}")
        if count != expected_count:
            issues.append(f"workflow:{command}:count={count}:expected={expected_count}")
    issues.extend(validate_order(workflow_lines, [f"run: {c}" for c in WORKFLOW_ORDER], "workflow_order"))

    makefile_lines = [line.strip() for line in makefile.splitlines()]
    for command, expected_count in MAKEFILE_VALIDATE_COUNTS.items():
        count = sum(1 for line in makefile_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"makefile_validate:{command}:count={count}:expected={expected_count}")
    issues.extend(validate_order(makefile_lines, MAKEFILE_VALIDATE_ORDER, "makefile_validate_order"))
    for command, expected_count in MAKEFILE_TOOL_COUNTS.items():
        count = sum(1 for line in makefile_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"makefile_tools:{command}:count={count}:expected={expected_count}")

    issues.extend(validate_cases(root))
    return issues


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_fixture_cases() -> str:
    cases: list[dict[str, object]] = []
    for name in CASE_NAME_ORDER:
        case: dict[str, object] = {"name": name, "argv": [], "expected": f"{name}_expected.json"}
        if name == "help":
            case["argv"] = ["--hel"]
            case["mode"] = "process_json"
            case["expected"] = "help_expected.json"
        elif name == "version":
            case["argv"] = ["--ver"]
            case["mode"] = "process_json"
            case["expected"] = "version_expected.json"
        elif name == "invalid_option":
            case["argv"] = ["-x"]
            case["mode"] = "process_json"
            case["normalize_stderr"] = True
            case["expected"] = "invalid_option_expected.json"
        elif name == "abbreviated_missing_long_dump_types_argument":
            case["argv"] = ["--dump-t"]
            case["mode"] = "process_json"
            case["normalize_stderr"] = True
            case["expected"] = "abbreviated_missing_long_dump_types_argument_expected.json"
        elif name == "too_many_reference_files":
            case["mode"] = "process_json"
            case["expected"] = "too_many_reference_files_expected.json"
        cases.append(case)
    return json.dumps({"cases": cases}, indent=2) + "\n"


def clone_fixture_root(root: Path) -> None:
    write(root / REQUIRED_FILES["bridge_checker"], "\n".join(BRIDGE_CHECKER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["readme"], "\n".join(README_MARKERS) + "\n")
    write(root / REQUIRED_FILES["closure_doc"], "\n".join(CLOSURE_DOC_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validator"], "\n".join(VALIDATOR_MARKERS) + "\n")
    write(root / REQUIRED_FILES["closure_validator"], "\n".join(CLOSURE_VALIDATOR_MARKERS) + "\n")

    workflow_lines = [f"run: {command}" for command in WORKFLOW_ORDER]
    write(root / REQUIRED_FILES["workflow"], "\n".join(workflow_lines) + "\n")

    makefile_lines = [
        "phase2-validate:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
        "phase2-tools:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    ]
    write(root / REQUIRED_FILES["makefile"], "\n".join(makefile_lines) + "\n")
    write(root / REQUIRED_FILES["cases"], build_fixture_cases())


def expect_issue(label: str, root: Path, needle: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase2-genksyms-alignment:{label}:unexpected_pass")
    if needle not in result.stdout:
        raise SystemExit(
            f"phase2-genksyms-alignment:{label}:expected={needle!r}:actual={result.stdout.strip()!r}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        clone_fixture_root(root)

        baseline = run_checker(root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase2-genksyms-alignment:baseline_failed:"
                + (baseline.stdout.strip() or baseline.stderr.strip() or "no_output")
            )

        readme_path = root / REQUIRED_FILES["readme"]
        original = readme_path.read_text(encoding="utf-8")
        write(readme_path, original.replace(README_MARKERS[0] + "\n", "", 1))
        expect_issue("readme_marker", root, f"readme:{README_MARKERS[0]}")
        write(readme_path, original)

        original = readme_path.read_text(encoding="utf-8")
        write(readme_path, original.replace(README_MARKERS[2] + "\n", "", 1))
        expect_issue("readme_boundary_marker", root, f"readme:{README_MARKERS[2]}")
        write(readme_path, original)

        closure_doc_path = root / REQUIRED_FILES["closure_doc"]
        original = closure_doc_path.read_text(encoding="utf-8")
        write(closure_doc_path, original.replace(CLOSURE_DOC_MARKERS[0] + "\n", "", 1))
        expect_issue("closure_doc_marker", root, f"closure_doc:{CLOSURE_DOC_MARKERS[0]}")
        write(closure_doc_path, original)

        original = closure_doc_path.read_text(encoding="utf-8")
        write(closure_doc_path, original.replace(CLOSURE_DOC_MARKERS[4] + "\n", "", 1))
        expect_issue("closure_doc_determinism_marker", root, f"closure_doc:{CLOSURE_DOC_MARKERS[4]}")
        write(closure_doc_path, original)

        original = closure_doc_path.read_text(encoding="utf-8")
        write(closure_doc_path, original.replace(CLOSURE_DOC_MARKERS[6] + "\n", "", 1))
        expect_issue("closure_doc_boundary_marker", root, f"closure_doc:{CLOSURE_DOC_MARKERS[6]}")
        write(closure_doc_path, original)

        bridge_checker_path = root / REQUIRED_FILES["bridge_checker"]
        original = bridge_checker_path.read_text(encoding="utf-8")
        write(bridge_checker_path, original.replace(BRIDGE_CHECKER_MARKERS[1] + "\n", "", 1))
        expect_issue("bridge_checker_marker", root, f"bridge_checker:{BRIDGE_CHECKER_MARKERS[1]}")
        write(bridge_checker_path, original)

        original = bridge_checker_path.read_text(encoding="utf-8")
        write(bridge_checker_path, original.replace(BRIDGE_CHECKER_MARKERS[2] + "\n", "", 1))
        expect_issue("bridge_checker_determinism_marker", root, f"bridge_checker:{BRIDGE_CHECKER_MARKERS[2]}")
        write(bridge_checker_path, original)

        validator_path = root / REQUIRED_FILES["validator"]
        original = validator_path.read_text(encoding="utf-8")
        write(validator_path, original.replace(VALIDATOR_MARKERS[1] + "\n", "", 1))
        expect_issue("validator_case_count_marker", root, f"validator:{VALIDATOR_MARKERS[1]}")
        write(validator_path, original)

        validator_path = root / REQUIRED_FILES["validator"]
        original = validator_path.read_text(encoding="utf-8")
        write(validator_path, original.replace(VALIDATOR_MARKERS[2] + "\n", "", 1))
        expect_issue("validator_determinism_marker", root, f"validator:{VALIDATOR_MARKERS[2]}")
        write(validator_path, original)

        validator_path = root / REQUIRED_FILES["validator"]
        original = validator_path.read_text(encoding="utf-8")
        write(validator_path, original.replace(VALIDATOR_MARKERS[3] + "\n", "", 1))
        expect_issue("validator_workflow_self_test_marker", root, f"validator:{VALIDATOR_MARKERS[3]}")
        write(validator_path, original)

        closure_validator_path = root / REQUIRED_FILES["closure_validator"]
        original = closure_validator_path.read_text(encoding="utf-8")
        write(closure_validator_path, original.replace(CLOSURE_VALIDATOR_MARKERS[0] + "\n", "", 1))
        expect_issue("closure_validator_marker", root, f"closure_validator:{CLOSURE_VALIDATOR_MARKERS[0]}")
        write(closure_validator_path, original)

        original = closure_validator_path.read_text(encoding="utf-8")
        write(closure_validator_path, original.replace(CLOSURE_VALIDATOR_MARKERS[5] + "\n", "", 1))
        expect_issue("closure_validator_determinism_marker", root, f"closure_validator:{CLOSURE_VALIDATOR_MARKERS[5]}")
        write(closure_validator_path, original)

        workflow_path = root / REQUIRED_FILES["workflow"]
        lines = workflow_path.read_text(encoding="utf-8").splitlines()
        lines[0], lines[1] = lines[1], lines[0]
        write(workflow_path, "\n".join(lines) + "\n")
        expect_issue("workflow_order", root, "workflow_order:run: python3 scripts/zigux/validate-phase2.py:before:run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test")
        clone_fixture_root(root)

        makefile_path = root / REQUIRED_FILES["makefile"]
        lines = makefile_path.read_text(encoding="utf-8").splitlines()
        lines[1], lines[2] = lines[2], lines[1]
        write(makefile_path, "\n".join(lines) + "\n")
        expect_issue(
            "makefile_validate_order",
            root,
            "makefile_validate_order:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:before:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        )
        clone_fixture_root(root)

        workflow_path = root / REQUIRED_FILES["workflow"]
        original = workflow_path.read_text(encoding="utf-8")
        write(
            workflow_path,
            original.replace(
                "run: zig test scripts/zigux/genksyms.zig\n",
                "",
                1,
            ),
        )
        expect_issue(
            "workflow_genksyms_zig_test_count",
            root,
            "workflow:zig test scripts/zigux/genksyms.zig:count=0:expected=1",
        )
        clone_fixture_root(root)

        makefile_path = root / REQUIRED_FILES["makefile"]
        original = makefile_path.read_text(encoding="utf-8")
        write(
            makefile_path,
            original.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\n",
                "",
                1,
            ),
        )
        expect_issue(
            "makefile_count",
            root,
            "makefile_validate:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:count=0:expected=1",
        )
        clone_fixture_root(root)

        makefile_path = root / REQUIRED_FILES["makefile"]
        original = makefile_path.read_text(encoding="utf-8")
        write(
            makefile_path,
            original.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test\n",
                "",
                1,
            ),
        )
        expect_issue(
            "makefile_tools_count",
            root,
            "makefile_tools:scripts/zigux/check-genksyms-bridge.py --self-test:count=0:expected=1",
        )
        clone_fixture_root(root)

        makefile_path = root / REQUIRED_FILES["makefile"]
        original = makefile_path.read_text(encoding="utf-8")
        write(
            makefile_path,
            original.replace(
                "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig\n",
                "",
                1,
            ),
        )
        expect_issue(
            "makefile_genksyms_zig_test_count",
            root,
            "makefile_tools:$(ZIG) test scripts/zigux/genksyms.zig:count=0:expected=1",
        )
        clone_fixture_root(root)

        cases_path = root / REQUIRED_FILES["cases"]
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["cases"][11]["argv"] = ["--help"]
        write(cases_path, json.dumps(payload, indent=2) + "\n")
        expect_issue("case_sentinel", root, "cases:help:argv=['--hel']")
        clone_fixture_root(root)

        cases_path = root / REQUIRED_FILES["cases"]
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["cases"][12]["expected"] = "renamed_version_expected.json"
        write(cases_path, json.dumps(payload, indent=2) + "\n")
        expect_issue("version_expected_file", root, "cases:version:expected=version_expected.json")

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=21")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail")
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MISSING_END")
    raise SystemExit(1)

print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass")
print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ROOT={ROOT}")