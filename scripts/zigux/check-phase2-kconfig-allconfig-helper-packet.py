#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
PHASE2_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

SELF_TEST_IMPLICIT_OMISSION_MODES = [
    "allmodconfig",
    "randconfig",
]

SELF_TEST_EXPLICIT_OVERRIDE_MODES = [
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
]

REQUIRED_HELPER_ANCHORS = [
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
]

REQUIRED_BRIDGE_SOURCE_MARKERS = [
    "var alldefconfig_path_capture = try TestCapture.init(std.testing.allocator, 224);",
    "try runConfBridge(&alldefconfig_path_capture, .{",
    '.allconfig = "mini-all.config",',
]

REQUIRED_CLOSURE_MARKERS = [
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4",
]

REQUIRED_PHASE2_VALIDATE_MARKERS = [
    '"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",',
    '"run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",',
]

REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS = [
    '"`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",',
    'KCONFIG_ALLCONFIG_HELPER_PACKET_REL = Path("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py")',
    "EXPECTED_CONF_CASE_DETAILS = [",
    "EXPECTED_CONF_MANIFEST = {",
    "EXPECTED_CONFDATA_CASE_DETAILS = [",
    "EXPECTED_CONFDATA_MANIFEST = {",
]

REQUIRED_TOOL_MANIFEST_CHECKERS = [
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
]

BRIDGE_CHECKER_IMPLICIT_OMISSION_MODES_CONST = "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES"
BRIDGE_CHECKER_EXPLICIT_OVERRIDE_MODES_CONST = "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES"
BRIDGE_CHECKER_HELPER_ANCHORS_CONST = "REQUIRED_CONF_HELPER_ANCHORS"
EXPECTED_SELF_TEST_CASE_COUNT = 29


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_literal(module_text: str, const_name: str) -> object:
    module = ast.parse(module_text)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == const_name:
                return ast.literal_eval(node.value)
    raise SystemExit(f"failed to parse {const_name} from {KCONFIG_BRIDGE_CHECKER}")


def load_bridge_checker_contract(path: Path) -> tuple[list[str], list[str], list[str]]:
    module_text = read_text(path)
    implicit_modes = extract_literal(module_text, BRIDGE_CHECKER_IMPLICIT_OMISSION_MODES_CONST)
    explicit_modes = extract_literal(module_text, BRIDGE_CHECKER_EXPLICIT_OVERRIDE_MODES_CONST)
    helper_anchors = extract_literal(module_text, BRIDGE_CHECKER_HELPER_ANCHORS_CONST)
    if not isinstance(implicit_modes, list) or not all(isinstance(mode, str) for mode in implicit_modes):
        raise SystemExit("failed to parse implicit omission packet from check-kconfig-bridge.py")
    if not isinstance(explicit_modes, list) or not all(isinstance(mode, str) for mode in explicit_modes):
        raise SystemExit("failed to parse explicit override packet from check-kconfig-bridge.py")
    if not isinstance(helper_anchors, list) or not all(isinstance(anchor, str) for anchor in helper_anchors):
        raise SystemExit("failed to parse helper anchors from check-kconfig-bridge.py")
    return implicit_modes, explicit_modes, helper_anchors


def load_tool_manifest_checkers(path: Path) -> list[str]:
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid tool manifest payload in {path}")
    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        raise SystemExit(f"invalid tool manifest present_surfaces in {path}")
    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list) or not all(isinstance(entry, str) for entry in checkers):
        raise SystemExit(f"invalid tool manifest checker list in {path}")
    return list(checkers)


def collect_exact_line_issues(
    path: Path,
    markers: list[str],
    missing_issue_code: str,
    duplicate_issue_code: str,
) -> list[tuple[str, str]]:
    text = read_text(path)
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_issue_code, marker))
        elif count != 1:
            issues.append((duplicate_issue_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
    bridge_path = root / CONF_BRIDGE.relative_to(ROOT)
    checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
    phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
    phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
    closure_path = root / PHASE2_CLOSURE.relative_to(ROOT)
    tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)

    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        return [("INVALID_CONF_MANIFEST_PAYLOAD", type(manifest).__name__)]

    checker_implicit_modes, checker_explicit_modes, checker_helper_anchors = load_bridge_checker_contract(checker_path)

    implicit_modes = manifest.get("helper_local_allconfig_implicit_omission_modes")
    if implicit_modes != checker_implicit_modes:
        issues.append(
            (
                "CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES_MISMATCH",
                f"actual={implicit_modes!r}:expected={checker_implicit_modes!r}",
            )
        )

    explicit_modes = manifest.get("helper_local_allconfig_explicit_override_modes")
    if explicit_modes != checker_explicit_modes:
        issues.append(
            (
                "CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES_MISMATCH",
                f"actual={explicit_modes!r}:expected={checker_explicit_modes!r}",
            )
        )

    bridge_text = read_text(bridge_path)
    for anchor in REQUIRED_HELPER_ANCHORS:
        if anchor not in bridge_text:
            issues.append(("MISSING_CONF_BRIDGE_HELPER_ANCHOR", anchor))
    for marker in REQUIRED_BRIDGE_SOURCE_MARKERS:
        if marker not in bridge_text:
            issues.append(("MISSING_CONF_BRIDGE_SOURCE_MARKER", marker))

    for anchor in REQUIRED_HELPER_ANCHORS:
        if anchor not in checker_helper_anchors:
            issues.append(("CONF_BRIDGE_CHECKER_MISSING_HELPER_ANCHOR", anchor))

    closure_text = read_text(closure_path)
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    issues.extend(
        collect_exact_line_issues(
            phase2_validate_path,
            REQUIRED_PHASE2_VALIDATE_MARKERS,
            "MISSING_PHASE2_VALIDATE_MARKER",
            "DUPLICATE_PHASE2_VALIDATE_MARKER",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            phase2_closure_validate_path,
            REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS,
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            "DUPLICATE_PHASE2_CLOSURE_VALIDATE_MARKER",
        )
    )

    manifest_checkers = load_tool_manifest_checkers(tool_manifest_path)
    for checker in REQUIRED_TOOL_MANIFEST_CHECKERS:
        if checker not in manifest_checkers:
            issues.append(("MISSING_TOOL_MANIFEST_CHECKER", checker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_bridge_checker_stub(
    implicit_modes: list[str] | None = None,
    explicit_modes: list[str] | None = None,
    helper_anchors: list[str] | None = None,
) -> str:
    if implicit_modes is None:
        implicit_modes = SELF_TEST_IMPLICIT_OMISSION_MODES
    if explicit_modes is None:
        explicit_modes = SELF_TEST_EXPLICIT_OVERRIDE_MODES
    if helper_anchors is None:
        helper_anchors = REQUIRED_HELPER_ANCHORS
    return (
        f"{BRIDGE_CHECKER_IMPLICIT_OMISSION_MODES_CONST} = {implicit_modes!r}\n"
        f"{BRIDGE_CHECKER_EXPLICIT_OVERRIDE_MODES_CONST} = {explicit_modes!r}\n"
        f"{BRIDGE_CHECKER_HELPER_ANCHORS_CONST} = {helper_anchors!r}\n"
    )


def build_self_test_root(root: Path) -> None:
    write_text(
        root / CONF_MANIFEST.relative_to(ROOT),
        json.dumps(
            {
                "helper_local_allconfig_implicit_omission_modes": SELF_TEST_IMPLICIT_OMISSION_MODES,
                "helper_local_allconfig_explicit_override_modes": SELF_TEST_EXPLICIT_OVERRIDE_MODES,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / CONF_BRIDGE.relative_to(ROOT),
        "\n".join(
            [
                *(f'test \"{anchor}\" {{}}' for anchor in REQUIRED_HELPER_ANCHORS),
                *REQUIRED_BRIDGE_SOURCE_MARKERS,
            ]
        )
        + "\n",
    )
    write_text(root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT), render_bridge_checker_stub())
    write_text(
        root / PHASE2_VALIDATE.relative_to(ROOT),
        "\n".join(REQUIRED_PHASE2_VALIDATE_MARKERS) + "\n",
    )
    write_text(
        root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT),
        "\n".join(REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS) + "\n",
    )
    write_text(root / PHASE2_CLOSURE.relative_to(ROOT), "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(
        root / PHASE2_TOOL_MANIFEST.relative_to(ROOT),
        json.dumps(
            {
                "present_surfaces": {
                    "checkers": REQUIRED_TOOL_MANIFEST_CHECKERS,
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_allconfig_helper_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["helper_local_allconfig_implicit_omission_modes"] = ["randconfig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(
            code == "CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES_MISMATCH"
            for code, _ in collect_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["helper_local_allconfig_explicit_override_modes"] = ["randconfig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(
            code == "CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES_MISMATCH"
            for code, _ in collect_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        bridge_path = root / CONF_BRIDGE.relative_to(ROOT)
        bridge_text = read_text(bridge_path).replace(REQUIRED_HELPER_ANCHORS[-1], "drifted anchor", 1)
        write_text(bridge_path, bridge_text)
        assert ("MISSING_CONF_BRIDGE_HELPER_ANCHOR", REQUIRED_HELPER_ANCHORS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bridge_path = root / CONF_BRIDGE.relative_to(ROOT)
        bridge_text = read_text(bridge_path).replace(REQUIRED_BRIDGE_SOURCE_MARKERS[-1], '.allconfig = "drifted-all.config",', 1)
        write_text(bridge_path, bridge_text)
        assert ("MISSING_CONF_BRIDGE_SOURCE_MARKER", REQUIRED_BRIDGE_SOURCE_MARKERS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
        write_text(checker_path, render_bridge_checker_stub(implicit_modes=["drifted-implicit"]))
        assert any(
            code == "CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES_MISMATCH"
            for code, _ in collect_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
        write_text(checker_path, render_bridge_checker_stub(explicit_modes=["drifted-explicit"]))
        assert any(
            code == "CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES_MISMATCH"
            for code, _ in collect_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
        write_text(checker_path, render_bridge_checker_stub(helper_anchors=REQUIRED_HELPER_ANCHORS[:-1]))
        assert ("CONF_BRIDGE_CHECKER_MISSING_HELPER_ANCHOR", REQUIRED_HELPER_ANCHORS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE.relative_to(ROOT)
        write_text(closure_path, REQUIRED_CLOSURE_MARKERS[1] + "\n")
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE.relative_to(ROOT)
        write_text(closure_path, REQUIRED_CLOSURE_MARKERS[0] + "\n")
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(phase2_validate_path, REQUIRED_PHASE2_VALIDATE_MARKERS[1] + "\n")
        assert (
            "MISSING_PHASE2_VALIDATE_MARKER",
            REQUIRED_PHASE2_VALIDATE_MARKERS[0],
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_VALIDATE_MARKERS
                if marker != '\"run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test\",'
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_VALIDATE_MARKER",
            '"run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_VALIDATE_MARKERS
                if marker != '\"run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\",'
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_VALIDATE_MARKER",
            '"run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_VALIDATE_MARKERS
                if marker != '\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test\",'
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_VALIDATE_MARKER",
            '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_VALIDATE_MARKERS
                if marker != '\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py\",'
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_VALIDATE_MARKER",
            '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_validate_path,
            "\n".join((REQUIRED_PHASE2_VALIDATE_MARKERS[0], REQUIRED_PHASE2_VALIDATE_MARKERS[0], *REQUIRED_PHASE2_VALIDATE_MARKERS[1:])) + "\n",
        )
        assert (
            "DUPLICATE_PHASE2_VALIDATE_MARKER",
            REQUIRED_PHASE2_VALIDATE_MARKERS[0] + ":count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(phase2_closure_validate_path, REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[1] + "\n")
        assert (
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0],
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS
                if marker != 'KCONFIG_ALLCONFIG_HELPER_PACKET_REL = Path(\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\")'
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            'KCONFIG_ALLCONFIG_HELPER_PACKET_REL = Path("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py")',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                (REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0], REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0], *REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[1:])
            )
            + "\n",
        )
        assert (
            "DUPLICATE_PHASE2_CLOSURE_VALIDATE_MARKER",
            REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0] + ":count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                (
                    REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0],
                    REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[1],
                    REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[1],
                    *REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[2:],
                )
            )
            + "\n",
        )
        assert (
            "DUPLICATE_PHASE2_CLOSURE_VALIDATE_MARKER",
            REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[1] + ":count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS
                if marker != "EXPECTED_CONF_CASE_DETAILS = ["
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            "EXPECTED_CONF_CASE_DETAILS = [",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS
                if marker != "EXPECTED_CONF_MANIFEST = {"
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            "EXPECTED_CONF_MANIFEST = {",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS
                if marker != "EXPECTED_CONFDATA_CASE_DETAILS = ["
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            "EXPECTED_CONFDATA_CASE_DETAILS = [",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join(
                marker
                for marker in REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS
                if marker != "EXPECTED_CONFDATA_MANIFEST = {"
            )
            + "\n",
        )
        assert (
            "MISSING_PHASE2_CLOSURE_VALIDATE_MARKER",
            "EXPECTED_CONFDATA_MANIFEST = {",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_closure_validate_path = root / PHASE2_CLOSURE_VALIDATE.relative_to(ROOT)
        write_text(
            phase2_closure_validate_path,
            "\n".join((REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0], REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0], *REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[1:])) + "\n",
        )
        assert (
            "DUPLICATE_PHASE2_CLOSURE_VALIDATE_MARKER",
            REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS[0] + ":count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
        write_text(manifest_path, json.dumps([], indent=2) + "\n")
        assert collect_issues(root) == [("INVALID_CONF_MANIFEST_PAYLOAD", "list")]
        checks_run += 1

        build_self_test_root(root)
        tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)
        write_text(tool_manifest_path, json.dumps([], indent=2) + "\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid tool manifest payload" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid tool manifest payload did not abort")

        build_self_test_root(root)
        tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)
        write_text(
            tool_manifest_path,
            json.dumps({"present_surfaces": []}, indent=2) + "\n",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid tool manifest present_surfaces" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid tool manifest present_surfaces did not abort")

        build_self_test_root(root)
        tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)
        write_text(
            tool_manifest_path,
            json.dumps({"present_surfaces": {"checkers": [1]}}, indent=2) + "\n",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid tool manifest checker list" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid tool manifest checker list did not abort")

        build_self_test_root(root)
        tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)
        write_text(
            tool_manifest_path,
            json.dumps({"present_surfaces": {"checkers": []}}, indent=2) + "\n",
        )
        assert ("MISSING_TOOL_MANIFEST_CHECKER", REQUIRED_TOOL_MANIFEST_CHECKERS[0]) in collect_issues(root)
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the helper-local conf_bridge allconfig packet against the manifest."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET=pass")
    print(f"PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT={len(REQUIRED_HELPER_ANCHORS)}")
    print(
        "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_IMPLICIT_ALLCONFIG_OMISSION_MODE_COUNT="
        f"{len(SELF_TEST_IMPLICIT_OMISSION_MODES)}"
    )
    print(
        "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_EXPLICIT_ALLCONFIG_OVERRIDE_MODE_COUNT="
        f"{len(SELF_TEST_EXPLICIT_OVERRIDE_MODES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())