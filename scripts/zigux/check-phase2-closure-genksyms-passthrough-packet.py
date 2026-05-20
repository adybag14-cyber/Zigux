#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
EXPLICIT_REL = Path("zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json")
POSITIONAL_REL = Path("zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json")
LONE_DASH_REL = Path("zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json")

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`make -C zigux phase2-genksyms`",
    "`zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
)

EXPECTED_CASES = {
    "explicit_option_terminator": {
        "args": ["-d", "leftover.c", "--", "--leftover", "positional"],
        "expected_file": "explicit_option_terminator_expected.json",
    },
    "positional_passthrough": {
        "args": ["leftover.c", "-d", "rightover.h", "-r", "foo.symref"],
        "expected_file": "positional_passthrough_expected.json",
    },
    "lone_dash_passthrough": {
        "args": ["-", "-d"],
        "expected_file": "lone_dash_passthrough_expected.json",
    },
}

EXPECTED_PAYLOADS = {
    EXPLICIT_REL: {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": [
            "scripts/genksyms/genksyms",
            "-d",
            "leftover.c",
            "--",
            "--leftover",
            "positional",
        ],
        "options": {
            "debug_level": 1,
            "warnings": False,
            "dump_defs": False,
            "preserve": False,
            "reference_files": [],
            "dump_types_file": None,
        },
    },
    POSITIONAL_REL: {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": [
            "scripts/genksyms/genksyms",
            "-d",
            "-r",
            "foo.symref",
            "leftover.c",
            "rightover.h",
        ],
        "options": {
            "debug_level": 1,
            "warnings": False,
            "dump_defs": False,
            "preserve": False,
            "reference_files": ["foo.symref"],
            "dump_types_file": None,
        },
    },
    LONE_DASH_REL: {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": [
            "scripts/genksyms/genksyms",
            "-d",
            "-",
        ],
        "options": {
            "debug_level": 1,
            "warnings": False,
            "dump_defs": False,
            "preserve": False,
            "reference_files": [],
            "dump_types_file": None,
        },
    },
}


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_case_map(cases: object) -> dict[str, dict[str, object]]:
    if not isinstance(cases, list):
        raise SystemExit("required json invalid: cases.json: root must be a list")
    case_map: dict[str, dict[str, object]] = {}
    for entry in cases:
        if not isinstance(entry, dict):
            raise SystemExit("required json invalid: cases.json: case entry must be an object")
        name = entry.get("name")
        if not isinstance(name, str):
            raise SystemExit("required json invalid: cases.json: case name must be a string")
        case_map[name] = entry
    return case_map


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(resolve(root, CLOSURE_REL))
    cases_payload = read_json(resolve(root, CASES_REL))
    case_map = collect_case_map(cases_payload)

    for marker in REQUIRED_CLOSURE_MARKERS:
        if closure_text.count(marker) != 1:
            issues.append(("CLOSURE_MARKER_COUNT_MISMATCH", marker))

    for name, expected in EXPECTED_CASES.items():
        actual = case_map.get(name)
        if actual is None:
            issues.append(("MISSING_CASE", name))
            continue
        actual_args = actual.get("args")
        actual_expected_file = actual.get("expected_file")
        if actual_args != expected["args"]:
            issues.append(("CASE_ARGS_MISMATCH", name))
        if actual_expected_file != expected["expected_file"]:
            issues.append(("CASE_EXPECTED_FILE_MISMATCH", name))

    for rel_path, expected_payload in EXPECTED_PAYLOADS.items():
        actual_payload = read_json(resolve(root, rel_path))
        if actual_payload != expected_payload:
            issues.append(("EXPECTED_PAYLOAD_MISMATCH", rel_path.as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve(root, CLOSURE_REL),
        "\n".join(
            [
                "# Phase 2 Closure",
                "",
                "- `scripts/zigux/check-genksyms-bridge.py`",
                "- `make -C zigux phase2-genksyms`",
                "- `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
                "- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
                "- `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, CASES_REL),
        json.dumps(
            [
                {
                    "name": name,
                    "args": payload["args"],
                    "expected_file": payload["expected_file"],
                }
                for name, payload in EXPECTED_CASES.items()
            ],
            indent=2,
        )
        + "\n",
    )
    for rel_path, payload in EXPECTED_PAYLOADS.items():
        write_text(resolve(root, rel_path), json.dumps(payload, indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="zigux_lane25_phase2_closure_passthrough_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = resolve(root, CLOSURE_REL)
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), REQUIRED_CLOSURE_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("CLOSURE_MARKER_COUNT_MISMATCH", REQUIRED_CLOSURE_MARKERS[2]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        cases_path = resolve(root, CASES_REL)
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        cases[0]["expected_file"] = "wrong.json"
        cases_path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        assert ("CASE_EXPECTED_FILE_MISMATCH", "explicit_option_terminator") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        cases[1]["args"] = ["wrong"]
        cases_path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        assert ("CASE_ARGS_MISMATCH", "positional_passthrough") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        explicit_path = resolve(root, EXPLICIT_REL)
        payload = json.loads(explicit_path.read_text(encoding="utf-8"))
        payload["argv"] = ["wrong"]
        explicit_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("EXPECTED_PAYLOAD_MISMATCH", EXPLICIT_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve(root, CASES_REL).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing cases file did not abort")

        build_sample_root(root)
        cases_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required json invalid" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid json did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 closure-side genksyms passthrough packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample repository root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET=pass")
    print(f"PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET_CASE_COUNT={len(EXPECTED_CASES)}")
    print(f"PHASE2_CLOSURE_GENKSYMS_PASSTHROUGH_PACKET_EXPECTED_FILE_COUNT={len(EXPECTED_PAYLOADS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
