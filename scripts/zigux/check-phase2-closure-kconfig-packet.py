#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
CONFDATA_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
CASES_JSON = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
MAKEFILE = ROOT / "zigux" / "Makefile"

CLOSURE_MARKERS = (
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`make -C zigux phase2-kconfig`",
    "`PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15`",
    "`PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=24`",
)

MAKEFILE_MARKERS = (
    "phase2-kconfig:",
    "$(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "$(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
)

EXPECTED_CONF_CASES = (
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
)

EXPECTED_CONFDATA_CASES = (
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
    "malformed_unset_comment_tokens",
    "last_state_transitions",
    "duplicate_assignments",
    "duplicate_malformed_quoted_assignment",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_missing_lines(text: str, lines: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    available = set(text.splitlines())
    return [(code, line) for line in lines if line not in available]


def collect_conf_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, CONF_MANIFEST))
    if not isinstance(payload, dict):
        return [("CONF_MANIFEST_NOT_OBJECT", "top-level object required")]
    if payload.get("tool") != "scripts/zigux/kconfig/conf_bridge.zig":
        issues.append(("CONF_MANIFEST_BAD_TOOL", str(payload.get("tool"))))
    if payload.get("case_count") != len(EXPECTED_CONF_CASES):
        issues.append(("CONF_MANIFEST_BAD_CASE_COUNT", str(payload.get("case_count"))))
    if tuple(payload.get("cases", ())) != EXPECTED_CONF_CASES:
        issues.append(("CONF_MANIFEST_CASE_ROSTER_MISMATCH", json.dumps(payload.get("cases", None))))
    if tuple(payload.get("silent_request_packet", ())) != (
        "listnewconfig_expected.json",
        "helpnewconfig_expected.json",
    ):
        issues.append(("CONF_MANIFEST_BAD_SILENT_PACKET", json.dumps(payload.get("silent_request_packet", None))))
    if tuple(payload.get("allconfig_override_packet", ())) != (
        "allmodconfig_expected.json",
        "randconfig_expected.json",
    ):
        issues.append(("CONF_MANIFEST_BAD_ALLCONFIG_OVERRIDE_PACKET", json.dumps(payload.get("allconfig_override_packet", None))))
    helper_anchors = payload.get("helper_local_anchors", ())
    if not isinstance(helper_anchors, list) or len(helper_anchors) != 28:
        issues.append(("CONF_MANIFEST_BAD_HELPER_ANCHOR_COUNT", str(len(helper_anchors) if isinstance(helper_anchors, list) else "non-list")))
    return issues


def collect_confdata_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, CONFDATA_MANIFEST))
    if not isinstance(payload, dict):
        return [("CONFDATA_MANIFEST_NOT_OBJECT", "top-level object required")]
    if payload.get("tool") != "scripts/zigux/kconfig/confdata_bridge.zig":
        issues.append(("CONFDATA_MANIFEST_BAD_TOOL", str(payload.get("tool"))))
    if payload.get("case_count") != len(EXPECTED_CONFDATA_CASES):
        issues.append(("CONFDATA_MANIFEST_BAD_CASE_COUNT", str(payload.get("case_count"))))
    if tuple(payload.get("cases", ())) != EXPECTED_CONFDATA_CASES:
        issues.append(("CONFDATA_MANIFEST_CASE_ROSTER_MISMATCH", json.dumps(payload.get("cases", None))))
    input_packet = payload.get("input_packet", ())
    expected_packet = payload.get("expected_packet", ())
    if not isinstance(input_packet, list) or len(input_packet) != len(EXPECTED_CONFDATA_CASES):
        issues.append(("CONFDATA_MANIFEST_BAD_INPUT_PACKET_COUNT", str(len(input_packet) if isinstance(input_packet, list) else "non-list")))
    if not isinstance(expected_packet, list) or len(expected_packet) != len(EXPECTED_CONFDATA_CASES):
        issues.append(("CONFDATA_MANIFEST_BAD_EXPECTED_PACKET_COUNT", str(len(expected_packet) if isinstance(expected_packet, list) else "non-list")))
    helper_anchors = payload.get("helper_local_anchors", ())
    if not isinstance(helper_anchors, list) or len(helper_anchors) != 24:
        issues.append(("CONFDATA_MANIFEST_BAD_HELPER_ANCHOR_COUNT", str(len(helper_anchors) if isinstance(helper_anchors, list) else "non-list")))
    return issues


def collect_cases_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, CASES_JSON))
    if not isinstance(payload, dict):
        return [("CASES_JSON_NOT_OBJECT", "top-level object required")]
    conf_cases = payload.get("conf_cases", ())
    confdata_cases = payload.get("confdata_cases", ())
    if not isinstance(conf_cases, list) or len(conf_cases) != len(EXPECTED_CONF_CASES):
        issues.append(("CASES_JSON_BAD_CONF_CASE_COUNT", str(len(conf_cases) if isinstance(conf_cases, list) else "non-list")))
    else:
        if tuple(item.get("name") for item in conf_cases if isinstance(item, dict)) != EXPECTED_CONF_CASES:
            issues.append(("CASES_JSON_CONF_ROSTER_MISMATCH", json.dumps([item.get("name") if isinstance(item, dict) else None for item in conf_cases])))
    if not isinstance(confdata_cases, list) or len(confdata_cases) != len(EXPECTED_CONFDATA_CASES):
        issues.append(("CASES_JSON_BAD_CONFDATA_CASE_COUNT", str(len(confdata_cases) if isinstance(confdata_cases, list) else "non-list")))
    else:
        if tuple(item.get("name") for item in confdata_cases if isinstance(item, dict)) != EXPECTED_CONFDATA_CASES:
            issues.append(("CASES_JSON_CONFDATA_ROSTER_MISMATCH", json.dumps([item.get("name") if isinstance(item, dict) else None for item in confdata_cases])))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, CLOSURE_NOTE)),
            CLOSURE_MARKERS,
            "MISSING_CLOSURE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_lines(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_MARKERS,
            "MISSING_MAKEFILE_MARKERS",
        )
    )
    issues.extend(collect_conf_manifest_issues(root))
    issues.extend(collect_confdata_manifest_issues(root))
    issues.extend(collect_cases_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_KCONFIG_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, CLOSURE_NOTE), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")

    conf_manifest_payload = {
        "tool": "scripts/zigux/kconfig/conf_bridge.zig",
        "case_count": len(EXPECTED_CONF_CASES),
        "cases": list(EXPECTED_CONF_CASES),
        "silent_request_packet": [
            "listnewconfig_expected.json",
            "helpnewconfig_expected.json",
        ],
        "allconfig_override_packet": [
            "allmodconfig_expected.json",
            "randconfig_expected.json",
        ],
        "helper_local_anchors": [f"anchor-{index}" for index in range(28)],
    }
    write_text(resolve_path(root, CONF_MANIFEST), json.dumps(conf_manifest_payload, indent=2) + "\n")

    confdata_manifest_payload = {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "case_count": len(EXPECTED_CONFDATA_CASES),
        "cases": list(EXPECTED_CONFDATA_CASES),
        "input_packet": [f"{name}.config" for name in EXPECTED_CONFDATA_CASES],
        "expected_packet": [f"{name}_expected.json" for name in EXPECTED_CONFDATA_CASES],
        "helper_local_anchors": [f"anchor-{index}" for index in range(24)],
    }
    write_text(resolve_path(root, CONFDATA_MANIFEST), json.dumps(confdata_manifest_payload, indent=2) + "\n")

    cases_payload = {
        "conf_cases": [{"name": name} for name in EXPECTED_CONF_CASES],
        "confdata_cases": [{"name": name} for name in EXPECTED_CONFDATA_CASES],
    }
    write_text(resolve_path(root, CASES_JSON), json.dumps(cases_payload, indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def remove_line_once(text: str, line: str) -> str:
    lines = text.splitlines()
    try:
        index = lines.index(line)
    except ValueError as exc:
        raise AssertionError(f"line not found: {line}") from exc
    del lines[index]
    return "\n".join(lines) + ("\n" if lines else "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(CLOSURE_MARKERS) + len(MAKEFILE_MARKERS) + 6
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_kconfig_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in CLOSURE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, CLOSURE_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_CLOSURE_MARKERS", marker) in issues
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(remove_line_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_MARKERS", marker) in issues
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CONF_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 0
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CONF_MANIFEST_BAD_CASE_COUNT", "0") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["helper_local_anchors"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CONFDATA_MANIFEST_BAD_HELPER_ANCHOR_COUNT", "0") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CASES_JSON)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["conf_cases"] = payload["conf_cases"][:-1]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CASES_JSON_BAD_CONF_CASE_COUNT", str(len(EXPECTED_CONF_CASES) - 1)) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CASES_JSON)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0]["name"] = "wrong"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "CASES_JSON_CONFDATA_ROSTER_MISMATCH" for code, _ in issues)
        checks_run += 1

        for rel_path in (CLOSURE_NOTE, CONF_MANIFEST):
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_CLOSURE_KCONFIG_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_KCONFIG_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure-side kconfig packet aligned to the live bridge helpers, manifests, cases, and make route."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_KCONFIG_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_KCONFIG_PACKET=pass")
    print(f"PHASE2_CLOSURE_KCONFIG_PACKET_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE2_CLOSURE_KCONFIG_PACKET_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    print(f"PHASE2_CLOSURE_KCONFIG_PACKET_CONF_CASE_COUNT={len(EXPECTED_CONF_CASES)}")
    print(f"PHASE2_CLOSURE_KCONFIG_PACKET_CONFDATA_CASE_COUNT={len(EXPECTED_CONFDATA_CASES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
