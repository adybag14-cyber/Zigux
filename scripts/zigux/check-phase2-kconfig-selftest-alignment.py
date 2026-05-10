#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

CHECKER = Path("scripts/zigux/check-kconfig-bridge.py")
VALIDATOR = Path("scripts/zigux/validate-phase2.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPT_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
CLOSURE = Path("Documentation/zigux/phase2-closure.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

CONF_PACKET_PATH = "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json"
CONFDATA_PACKET_PATH = "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"
CONF_MANIFEST = Path(CONF_PACKET_PATH)
CONFDATA_MANIFEST = Path(CONFDATA_PACKET_PATH)

REQUIRED_CHECKER_MARKERS = (
    "REQUIRED_CONF_CASE_MODES = [",
    "REQUIRED_CONFDATA_CASES = [",
    "ALLCONFIG_OVERRIDE_MODES = {",
    "def expected_conf_case_order(conf_cases: list[dict[str, object]]) -> list[str]:",
    "cmd.append(f\"allconfig={case['allconfig']}\")",
    "cmd.append(f\"seed={case['seed']}\")",
    "cmd.append(f\"probability={case['probability']}\")",
    "cmd.append(f\"nosilentupdate={case['nosilentupdate']}\")",
    "cmd.append(\"silent\")",
    "EXPECTED_SELF_TEST_CASE_COUNT = 21",
    "print(\"KCONFIG_BRIDGE_SELF_TEST=pass\")",
    "print(f\"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}\")",
)

REQUIRED_VALIDATOR_MARKERS = (
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
)

REQUIRED_VALIDATOR_GUARD_MARKERS = (
    "KCONFIG_BRIDGE_SELF_TEST=pass",
    "KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=21",
    "KCONFIG_BRIDGE_DIFF=pass",
    "FIXTURE_DIR=",
)

REQUIRED_SCRIPT_README_MARKERS = (
    "check-phase2-kconfig-selftest-alignment.py",
    "check-kconfig-bridge.py",
    "phase2-kconfig",
    "bounded kconfig bridge packet",
)

REQUIRED_TESTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "the shipped direct kconfig bridge replays",
)

REQUIRED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
)

REQUIRED_CLOSURE_MARKERS = (
    f"`PHASE2_KCONFIG_BRIDGE_CONF_PACKET={CONF_PACKET_PATH}`",
    "`kconfig_conf_bridge_packet`",
    f"`PHASE2_KCONFIG_BRIDGE_CONFDATA_PACKET={CONFDATA_PACKET_PATH}`",
    "`kconfig_confdata_bridge_packet`",
)

REQUIRED_CONF_MANIFEST_HELPER_ANCHORS = (
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits defconfig mode argument before kconfig",
    "conf bridge emits savedefconfig mode argument before kconfig",
)

REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS = (
    "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
    "confdata bridge keeps only the last state across unset and set transitions",
)

REQUIRED_CONF_MANIFEST_MODE_ARG_CASES = [
    "defconfig",
    "savedefconfig",
]

REQUIRED_CONF_MANIFEST_ALLCONFIG_OVERRIDE_PACKET = [
    "allmodconfig_expected.json",
    "randconfig_expected.json",
]

REQUIRED_CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET = [
    "allnoconfig_expected.json",
    "allyesconfig_expected.json",
    "alldefconfig_expected.json",
]

EXPECTED_SELF_TEST_CASE_COUNT = 64


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + ("\n" if lines else "")
    raise AssertionError(f"marker line not found: {marker}")


def remove_substring_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker substring not found: {marker}")
    return text.replace(marker, "", 1)


def duplicate_substring_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker substring not found: {marker}")
    return text.replace(marker, marker + "\n" + marker, 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    required_files = (
        CHECKER,
        VALIDATOR,
        MAKEFILE,
        WORKFLOW,
        SCRIPT_README,
        TESTS_README,
        CLOSURE,
        TOOL_MANIFEST,
        CONF_MANIFEST,
        CONFDATA_MANIFEST,
    )
    issues: list[tuple[str, str]] = []
    for rel_path in required_files:
        if not (root / rel_path).exists():
            issues.append(("MISSING_REQUIRED_FILES", str(rel_path)))
    if issues:
        return issues

    checker_text = read_text(root / CHECKER)
    validator_text = read_text(root / VALIDATOR)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)
    script_readme_text = read_text(root / SCRIPT_README)
    tests_readme_text = read_text(root / TESTS_README)
    closure_text = read_text(root / CLOSURE)
    tool_manifest = json.loads(read_text(root / TOOL_MANIFEST))
    conf_manifest = json.loads(read_text(root / CONF_MANIFEST))
    confdata_manifest = json.loads(read_text(root / CONFDATA_MANIFEST))

    for marker in REQUIRED_CHECKER_MARKERS:
        count = checker_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CHECKER_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CHECKER_MARKERS", f"{marker}:count={count}:expected=1"))

    for marker in REQUIRED_VALIDATOR_MARKERS:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKERS", f"{marker}:count={count}:expected=1"))

    for marker in REQUIRED_VALIDATOR_GUARD_MARKERS:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_GUARD_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_GUARD_MARKERS", f"{marker}:count={count}:expected=1"))

    for marker in REQUIRED_SCRIPT_README_MARKERS:
        count = script_readme_text.count(marker)
        if count == 0:
            issues.append(("MISSING_SCRIPT_README_MARKERS", marker))
        elif marker in ("check-phase2-kconfig-selftest-alignment.py", "check-kconfig-bridge.py") and count != 1:
            issues.append(("DUPLICATE_SCRIPT_README_MARKERS", f"{marker}:count={count}:expected=1"))

    for marker in REQUIRED_TESTS_README_MARKERS:
        count = tests_readme_text.count(marker)
        if count == 0:
            issues.append(("MISSING_TESTS_README_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_TESTS_README_MARKERS", f"{marker}:count={count}:expected=1"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_CLOSURE_MARKERS:
        count = closure_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CLOSURE_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CLOSURE_MARKERS", f"{marker}:count={count}:expected=1"))

    if tool_manifest.get("kconfig_conf_bridge_packet") != CONF_PACKET_PATH:
        issues.append(("INVALID_TOOL_MANIFEST_CONF_PACKET", f"kconfig_conf_bridge_packet={tool_manifest.get('kconfig_conf_bridge_packet')!r}"))
    if tool_manifest.get("kconfig_confdata_bridge_packet") != CONFDATA_PACKET_PATH:
        issues.append(("INVALID_TOOL_MANIFEST_CONFDATA_PACKET", f"kconfig_confdata_bridge_packet={tool_manifest.get('kconfig_confdata_bridge_packet')!r}"))

    helper_local_anchors = conf_manifest.get("helper_local_anchors")
    if not isinstance(helper_local_anchors, list):
        issues.append(("INVALID_CONF_MANIFEST_HELPER_LOCAL_ANCHORS", f"helper_local_anchors={helper_local_anchors!r}"))
    else:
        for anchor in REQUIRED_CONF_MANIFEST_HELPER_ANCHORS:
            anchor_count = helper_local_anchors.count(anchor)
            if anchor_count == 0:
                issues.append(("MISSING_CONF_MANIFEST_HELPER_ANCHORS", anchor))
            elif anchor_count != 1:
                issues.append(("DUPLICATE_CONF_MANIFEST_HELPER_ANCHORS", f"{anchor}:count={anchor_count}"))

    if conf_manifest.get("mode_arg_cases") != REQUIRED_CONF_MANIFEST_MODE_ARG_CASES:
        issues.append(
            (
                "INVALID_CONF_MANIFEST_MODE_ARG_CASES",
                f"mode_arg_cases={conf_manifest.get('mode_arg_cases')!r}:expected={REQUIRED_CONF_MANIFEST_MODE_ARG_CASES!r}",
            )
        )
    if conf_manifest.get("allconfig_override_packet") != REQUIRED_CONF_MANIFEST_ALLCONFIG_OVERRIDE_PACKET:
        issues.append(
            (
                "INVALID_CONF_MANIFEST_ALLCONFIG_OVERRIDE_PACKET",
                "allconfig_override_packet="
                f"{conf_manifest.get('allconfig_override_packet')!r}:expected={REQUIRED_CONF_MANIFEST_ALLCONFIG_OVERRIDE_PACKET!r}",
            )
        )
    if conf_manifest.get("allconfig_sentinel_packet") != REQUIRED_CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET:
        issues.append(
            (
                "INVALID_CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET",
                "allconfig_sentinel_packet="
                f"{conf_manifest.get('allconfig_sentinel_packet')!r}:expected={REQUIRED_CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET!r}",
            )
        )

    confdata_helper_local_anchors = confdata_manifest.get("helper_local_anchors")
    if not isinstance(confdata_helper_local_anchors, list):
        issues.append(
            (
                "INVALID_CONFDATA_MANIFEST_HELPER_LOCAL_ANCHORS",
                f"helper_local_anchors={confdata_helper_local_anchors!r}",
            )
        )
    else:
        for anchor in REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS:
            anchor_count = confdata_helper_local_anchors.count(anchor)
            if anchor_count == 0:
                issues.append(("MISSING_CONFDATA_MANIFEST_HELPER_ANCHORS", anchor))
            elif anchor_count != 1:
                issues.append(("DUPLICATE_CONFDATA_MANIFEST_HELPER_ANCHORS", f"{anchor}:count={anchor_count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_KCONFIG_ALIGNMENT=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root / CHECKER,
        "\n".join(
            (
                "REQUIRED_CONF_CASE_MODES = [",
                "REQUIRED_CONFDATA_CASES = [",
                "ALLCONFIG_OVERRIDE_MODES = {",
                "def expected_conf_case_order(conf_cases: list[dict[str, object]]) -> list[str]:",
                "cmd.append(f\"allconfig={case['allconfig']}\")",
                "cmd.append(f\"seed={case['seed']}\")",
                "cmd.append(f\"probability={case['probability']}\")",
                "cmd.append(f\"nosilentupdate={case['nosilentupdate']}\")",
                "cmd.append(\"silent\")",
                "EXPECTED_SELF_TEST_CASE_COUNT = 21",
                "print(\"KCONFIG_BRIDGE_SELF_TEST=pass\")",
                "print(f\"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}\")",
                "",
            )
        ),
    )
    write_text(
        root / VALIDATOR,
        "\n".join(
            REQUIRED_VALIDATOR_MARKERS
            + REQUIRED_VALIDATOR_GUARD_MARKERS
            + ("",)
        ),
    )
    write_text(
        root / SCRIPT_README,
        "\n".join(REQUIRED_SCRIPT_README_MARKERS + ("",)),
    )
    write_text(
        root / TESTS_README,
        "\n".join(REQUIRED_TESTS_README_MARKERS + ("",)),
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase2-kconfig:",
                "\t" + REQUIRED_MAKEFILE_LINES[0],
                "\t" + REQUIRED_MAKEFILE_LINES[1],
                "\t" + REQUIRED_MAKEFILE_LINES[2],
                "\t" + REQUIRED_MAKEFILE_LINES[3],
                "\t" + REQUIRED_MAKEFILE_LINES[4],
                "\t" + REQUIRED_MAKEFILE_LINES[5],
                REQUIRED_MAKEFILE_LINES[6],
                "",
            )
        ),
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 2 kconfig selftest alignment",
                "        " + REQUIRED_WORKFLOW_LINES[0],
                "      - name: Check Phase 2 kconfig selftest alignment",
                "        " + REQUIRED_WORKFLOW_LINES[1],
                "      - name: Self-test bounded kconfig bridge parity checker",
                "        " + REQUIRED_WORKFLOW_LINES[2],
                "      - name: Check bounded kconfig bridge parity",
                "        " + REQUIRED_WORKFLOW_LINES[3],
                "      - name: Run bounded conf bridge unit tests",
                "        " + REQUIRED_WORKFLOW_LINES[4],
                "      - name: Run bounded confdata bridge unit tests",
                "        " + REQUIRED_WORKFLOW_LINES[5],
                "",
            )
        ),
    )
    write_text(
        root / CLOSURE,
        "\n".join(
            (
                "## Phase 2 Kconfig Packet",
                f"- {REQUIRED_CLOSURE_MARKERS[0]}",
                f"- the shared Phase 2 tool manifest points at that same tool-local packet through {REQUIRED_CLOSURE_MARKERS[1]}",
                f"- {REQUIRED_CLOSURE_MARKERS[2]}",
                f"- the shared Phase 2 tool manifest points at that same tool-local packet through {REQUIRED_CLOSURE_MARKERS[3]}",
                "",
            )
        ),
    )
    write_text(
        root / TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "closed",
                "tool_count": 6,
                "kconfig_conf_bridge_packet": CONF_PACKET_PATH,
                "kconfig_confdata_bridge_packet": CONFDATA_PACKET_PATH,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / CONF_MANIFEST,
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/conf_bridge.zig",
                "helper_local_anchors": list(REQUIRED_CONF_MANIFEST_HELPER_ANCHORS),
                "mode_arg_cases": REQUIRED_CONF_MANIFEST_MODE_ARG_CASES,
                "allconfig_override_packet": REQUIRED_CONF_MANIFEST_ALLCONFIG_OVERRIDE_PACKET,
                "allconfig_sentinel_packet": REQUIRED_CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / CONFDATA_MANIFEST,
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
                "helper_local_anchors": [
                    "confdata bridge emits bounded json output",
                    REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS[0],
                    REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS[1],
                ],
            },
            indent=2,
        )
        + "\n",
    )



def mutate_remove_substring(root: Path, rel_path: Path, marker: str) -> None:
    path = root / rel_path
    write_text(path, remove_substring_once(read_text(path), marker))



def mutate_duplicate_substring(root: Path, rel_path: Path, marker: str) -> None:
    path = root / rel_path
    write_text(path, duplicate_substring_once(read_text(path), marker))



def mutate_remove_line(root: Path, rel_path: Path, marker: str) -> None:
    path = root / rel_path
    write_text(path, remove_exact_line(read_text(path), marker))



def mutate_duplicate_line(root: Path, rel_path: Path, marker: str) -> None:
    path = root / rel_path
    write_text(path, duplicate_exact_line(read_text(path), marker))



def run_self_test() -> int:
    def json_edit(rel_path: Path, editor) -> callable:
        def apply(root: Path) -> None:
            path = root / rel_path
            payload = json.loads(read_text(path))
            editor(payload)
            write_text(path, json.dumps(payload, indent=2) + "\n")

        return apply

    specs: list[tuple[callable, tuple[str, str]]] = [
        (lambda root: (root / CHECKER).unlink(), ("MISSING_REQUIRED_FILES", str(CHECKER))),
    ]

    specs.extend(
        (lambda root, marker=marker: mutate_remove_substring(root, CHECKER, marker), ("MISSING_CHECKER_MARKERS", marker))
        for marker in REQUIRED_CHECKER_MARKERS
    )
    specs.extend(
        (
            lambda root, marker=marker: mutate_remove_line(root, VALIDATOR, marker),
            ("MISSING_VALIDATOR_MARKERS", marker),
        )
        for marker in REQUIRED_VALIDATOR_MARKERS
    )
    specs.extend(
        (
            lambda root, marker=marker: mutate_remove_line(root, VALIDATOR, marker),
            ("MISSING_VALIDATOR_GUARD_MARKERS", marker),
        )
        for marker in REQUIRED_VALIDATOR_GUARD_MARKERS
    )
    specs.extend(
        (
            lambda root, marker=marker: write_text(
                root / MAKEFILE,
                replace_exact_line(read_text(root / MAKEFILE), marker, "\ttrue"),
            ),
            ("MISSING_MAKEFILE_HOOKS", marker),
        )
        for marker in REQUIRED_MAKEFILE_LINES
    )
    specs.extend(
        (
            lambda root, marker=marker: write_text(
                root / WORKFLOW,
                replace_exact_line(read_text(root / WORKFLOW), marker, "        run: true"),
            ),
            ("MISSING_WORKFLOW_HOOKS", marker),
        )
        for marker in REQUIRED_WORKFLOW_LINES
    )
    specs.extend(
        (
            lambda root, marker=marker: mutate_remove_substring(root, CLOSURE, marker),
            ("MISSING_CLOSURE_MARKERS", marker),
        )
        for marker in REQUIRED_CLOSURE_MARKERS
    )
    specs.extend(
        [
            (
                json_edit(TOOL_MANIFEST, lambda payload: payload.pop("kconfig_conf_bridge_packet")),
                ("INVALID_TOOL_MANIFEST_CONF_PACKET", "kconfig_conf_bridge_packet=None"),
            ),
            (
                json_edit(
                    TOOL_MANIFEST,
                    lambda payload: payload.__setitem__(
                        "kconfig_conf_bridge_packet",
                        "zigux/tests/fixtures/kconfig_bridge/other_manifest.json",
                    ),
                ),
                (
                    "INVALID_TOOL_MANIFEST_CONF_PACKET",
                    "kconfig_conf_bridge_packet='zigux/tests/fixtures/kconfig_bridge/other_manifest.json'",
                ),
            ),
            (
                json_edit(TOOL_MANIFEST, lambda payload: payload.pop("kconfig_confdata_bridge_packet")),
                ("INVALID_TOOL_MANIFEST_CONFDATA_PACKET", "kconfig_confdata_bridge_packet=None"),
            ),
            (
                json_edit(
                    TOOL_MANIFEST,
                    lambda payload: payload.__setitem__(
                        "kconfig_confdata_bridge_packet",
                        "zigux/tests/fixtures/kconfig_bridge/other_manifest.json",
                    ),
                ),
                (
                    "INVALID_TOOL_MANIFEST_CONFDATA_PACKET",
                    "kconfig_confdata_bridge_packet='zigux/tests/fixtures/kconfig_bridge/other_manifest.json'",
                ),
            ),
        ]
    )
    specs.extend(
        (
            json_edit(
                CONF_MANIFEST,
                lambda payload, anchor=anchor: payload.__setitem__(
                    "helper_local_anchors",
                    [item for item in payload["helper_local_anchors"] if item != anchor],
                ),
            ),
            ("MISSING_CONF_MANIFEST_HELPER_ANCHORS", anchor),
        )
        for anchor in REQUIRED_CONF_MANIFEST_HELPER_ANCHORS
    )
    specs.extend(
        [
            (
                json_edit(
                    CONF_MANIFEST,
                    lambda payload: payload.__setitem__(
                        "helper_local_anchors",
                        payload["helper_local_anchors"] + [REQUIRED_CONF_MANIFEST_HELPER_ANCHORS[0]],
                    ),
                ),
                (
                    "DUPLICATE_CONF_MANIFEST_HELPER_ANCHORS",
                    f"{REQUIRED_CONF_MANIFEST_HELPER_ANCHORS[0]}:count=2",
                ),
            ),
            (
                json_edit(
                    CONF_MANIFEST,
                    lambda payload: payload.__setitem__("mode_arg_cases", ["savedefconfig"]),
                ),
                (
                    "INVALID_CONF_MANIFEST_MODE_ARG_CASES",
                    "mode_arg_cases=['savedefconfig']:expected=['defconfig', 'savedefconfig']",
                ),
            ),
            (
                json_edit(
                    CONF_MANIFEST,
                    lambda payload: payload.__setitem__("allconfig_override_packet", ["randconfig_expected.json"]),
                ),
                (
                    "INVALID_CONF_MANIFEST_ALLCONFIG_OVERRIDE_PACKET",
                    "allconfig_override_packet=['randconfig_expected.json']:expected=['allmodconfig_expected.json', 'randconfig_expected.json']",
                ),
            ),
            (
                json_edit(
                    CONF_MANIFEST,
                    lambda payload: payload.__setitem__("allconfig_sentinel_packet", ["allnoconfig_expected.json"]),
                ),
                (
                    "INVALID_CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET",
                    "allconfig_sentinel_packet=['allnoconfig_expected.json']:expected=['allnoconfig_expected.json', 'allyesconfig_expected.json', 'alldefconfig_expected.json']",
                ),
            ),
        ]
    )
    specs.extend(
        (
            json_edit(
                CONFDATA_MANIFEST,
                lambda payload, anchor=anchor: payload.__setitem__(
                    "helper_local_anchors",
                    [item for item in payload["helper_local_anchors"] if item != anchor],
                ),
            ),
            ("MISSING_CONFDATA_MANIFEST_HELPER_ANCHORS", anchor),
        )
        for anchor in REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS
    )
    specs.extend(
        [
            (
                json_edit(
                    CONFDATA_MANIFEST,
                    lambda payload: payload.__setitem__(
                        "helper_local_anchors",
                        payload["helper_local_anchors"] + [REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS[0]],
                    ),
                ),
                (
                    "DUPLICATE_CONFDATA_MANIFEST_HELPER_ANCHORS",
                    f"{REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS[0]}:count=2",
                ),
            ),
            (
                json_edit(
                    CONFDATA_MANIFEST,
                    lambda payload: payload.__setitem__(
                        "helper_local_anchors",
                        payload["helper_local_anchors"] + [REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS[1]],
                    ),
                ),
                (
                    "DUPLICATE_CONFDATA_MANIFEST_HELPER_ANCHORS",
                    f"{REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS[1]}:count=2",
                ),
            ),
            (
                json_edit(
                    CONFDATA_MANIFEST,
                    lambda payload: payload.__setitem__("helper_local_anchors", "not-a-list"),
                ),
                (
                    "INVALID_CONFDATA_MANIFEST_HELPER_LOCAL_ANCHORS",
                    "helper_local_anchors='not-a-list'",
                ),
            ),
            (
                lambda root: mutate_duplicate_substring(root, CHECKER, REQUIRED_CHECKER_MARKERS[0]),
                (
                    "DUPLICATE_CHECKER_MARKERS",
                    f"{REQUIRED_CHECKER_MARKERS[0]}:count=2:expected=1",
                ),
            ),
            (
                lambda root: mutate_duplicate_line(root, VALIDATOR, REQUIRED_VALIDATOR_MARKERS[0]),
                (
                    "DUPLICATE_VALIDATOR_MARKERS",
                    f"{REQUIRED_VALIDATOR_MARKERS[0]}:count=2:expected=1",
                ),
            ),
            (
                lambda root: mutate_duplicate_line(root, VALIDATOR, REQUIRED_VALIDATOR_GUARD_MARKERS[0]),
                (
                    "DUPLICATE_VALIDATOR_GUARD_MARKERS",
                    f"{REQUIRED_VALIDATOR_GUARD_MARKERS[0]}:count=2:expected=1",
                ),
            ),
            (
                lambda root: write_text(
                    root / WORKFLOW,
                    duplicate_exact_line(read_text(root / WORKFLOW), REQUIRED_WORKFLOW_LINES[0]),
                ),
                (
                    "DUPLICATE_WORKFLOW_HOOKS",
                    f"{REQUIRED_WORKFLOW_LINES[0]}:count=2",
                ),
            ),
            (
                lambda root: mutate_duplicate_substring(root, SCRIPT_README, REQUIRED_SCRIPT_README_MARKERS[0]),
                (
                    "DUPLICATE_SCRIPT_README_MARKERS",
                    f"{REQUIRED_SCRIPT_README_MARKERS[0]}:count=2:expected=1",
                ),
            ),
            (
                lambda root: mutate_duplicate_substring(root, TESTS_README, REQUIRED_TESTS_README_MARKERS[0]),
                (
                    "DUPLICATE_TESTS_README_MARKERS",
                    f"{REQUIRED_TESTS_README_MARKERS[0]}:count=2:expected=1",
                ),
            ),
            (
                lambda root: write_text(
                    root / MAKEFILE,
                    duplicate_exact_line(read_text(root / MAKEFILE), REQUIRED_MAKEFILE_LINES[0]),
                ),
                (
                    "DUPLICATE_MAKEFILE_HOOKS",
                    f"{REQUIRED_MAKEFILE_LINES[0]}:count=2",
                ),
            ),
        ]
    )

    assert len(specs) == EXPECTED_SELF_TEST_CASE_COUNT

    for mutate, expected_issue in specs:
        with tempfile.TemporaryDirectory(prefix="zigux_p2_kconfig_alignment_") as tmp_dir:
            root = Path(tmp_dir)
            build_self_test_root(root)
            assert collect_issues(root) == []
            mutate(root)
            issues = collect_issues(root)
            assert expected_issue in issues, (expected_issue, issues)

    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={len(specs)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 kconfig replay gate stays aligned with the shared conf and confdata packet surface."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CHECKER_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_VALIDATOR_MARKER_COUNT={len(REQUIRED_VALIDATOR_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_VALIDATOR_GUARD_MARKER_COUNT={len(REQUIRED_VALIDATOR_GUARD_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SCRIPT_README_MARKER_COUNT={len(REQUIRED_SCRIPT_README_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_TESTS_README_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CONF_HELPER_ANCHOR_COUNT={len(REQUIRED_CONF_MANIFEST_HELPER_ANCHORS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CONFDATA_HELPER_ANCHOR_COUNT={len(REQUIRED_CONFDATA_MANIFEST_HELPER_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
