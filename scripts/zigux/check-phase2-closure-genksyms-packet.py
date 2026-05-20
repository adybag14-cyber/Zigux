#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE_NOTE = Path("Documentation/zigux/phase2-closure.md")
GENKSYMS_CASES = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
POSITIONAL_EXPECTED = Path("zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json")

REQUIRED_CLOSURE_MARKERS = (
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "PHASE2_CURRENT_CLOSURE_PACKET=",
)

EXPECTED_POSITIONAL_CASE = {
    "name": "positional_passthrough",
    "args": ["leftover.c", "-d", "rightover.h", "-r", "foo.symref"],
    "expected_file": "positional_passthrough_expected.json",
}

EXPECTED_POSITIONAL_JSON = {
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
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc



def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc



def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(root / CLOSURE_NOTE)
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    cases = read_json(root / GENKSYMS_CASES)
    if not isinstance(cases, list):
        issues.append(("INVALID_CASES_SHAPE", "root"))
    elif EXPECTED_POSITIONAL_CASE not in cases:
        issues.append(("MISSING_POSITIONAL_CASE", json.dumps(EXPECTED_POSITIONAL_CASE, sort_keys=True)))

    positional_payload = read_json(root / POSITIONAL_EXPECTED)
    if positional_payload != EXPECTED_POSITIONAL_JSON:
        issues.append(("POSITIONAL_EXPECTED_JSON_MISMATCH", "positional_passthrough_expected.json"))

    return issues



def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_GENKSYMS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1



def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")



def build_self_test_root(root: Path) -> None:
    write_text(
        root / CLOSURE_NOTE,
        "\n".join(
            [
                "# Phase 2 Closure",
                "",
                "- `zigux/tests/fixtures/genksyms_bridge/cases.json`",
                "- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
                "- `PHASE2_CURRENT_CLOSURE_PACKET=`",
                "",
            ]
        ),
    )
    write_json(root / GENKSYMS_CASES, [EXPECTED_POSITIONAL_CASE])
    write_json(root / POSITIONAL_EXPECTED, EXPECTED_POSITIONAL_JSON)



def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_genksyms_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        note_path = root / CLOSURE_NOTE
        note_path.write_text(note_path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_json(root / GENKSYMS_CASES, [])
        assert any(code == "MISSING_POSITIONAL_CASE" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        broken_payload = dict(EXPECTED_POSITIONAL_JSON)
        broken_payload["argv"] = ["scripts/genksyms/genksyms", "broken"]
        write_json(root / POSITIONAL_EXPECTED, broken_payload)
        assert ("POSITIONAL_EXPECTED_JSON_MISMATCH", "positional_passthrough_expected.json") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / POSITIONAL_EXPECTED).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing positional expected file did not abort")

    print("PHASE2_CLOSURE_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note aligned with the live genksyms positional passthrough packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_GENKSYMS_PACKET=pass")
    print("PHASE2_CLOSURE_GENKSYMS_PACKET_MARKER_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
