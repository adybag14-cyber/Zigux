#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FIXDEP_NOTE = Path("Documentation/zigux/phase2-fixdep-next-step-note.md")
CONFDATA_NOTE = Path("Documentation/zigux/phase2-confdata-bridge-survey.md")
FIXDEP_GATE = Path("scripts/zigux/check-phase2-fixdep-gate.py")
KCONFIG_ALIGNMENT = Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py")
FIXDEP_CASES = Path("zigux/tests/fixtures/fixdep/cases.json")
KCONFIG_CASES = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")
CONFDATA_MANIFEST = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")

REQUIRED_FILES = (
    FIXDEP_NOTE,
    CONFDATA_NOTE,
    FIXDEP_GATE,
    KCONFIG_ALIGNMENT,
    FIXDEP_CASES,
    KCONFIG_CASES,
    CONFDATA_MANIFEST,
)

FIXDEP_CASE_NAMES = (
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_continuation",
    "sample_double_backslash_comment",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
)

CONFDATA_CASE_NAMES = (
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

FIXDEP_NOTE_MARKERS = (
    "`zigux/tests/fixtures/fixdep/cases.json` currently inventories 13 external fixdep cases",
    "`sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current stdout-failure replay cases.",
    "The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, `make -C zigux phase2-fixdep`, and `zig test scripts/zigux/fixdep.zig`.",
    "the live parity checker no longer pins that C path directly and instead stays bounded to `scripts/zigux/fixdep.zig`, `Documentation/zigux/artifact-diff.md`, and the committed fixture packet.",
)

CONFDATA_NOTE_MARKERS = (
    "ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary, alongside `25` helper-local tests",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with `15` fixture cases",
    "`malformed_unset_comment_tokens`, `last_state_transitions`, `duplicate_assignments`, and `duplicate_malformed_quoted_assignment`.",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same `15`-case packet",
    "`scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "the live duplicate-assignment, malformed-quote, and malformed-unset-comment coverage now have a shared `15`-case external packet behind them",
)

FIXDEP_GATE_MARKERS = (
    'REQUIRED_FIXDEP_CASE_NAMES = (',
    '"sample_double_backslash_comment",',
    '"run: make -C zigux phase2-fixdep",',
)

KCONFIG_ALIGNMENT_MARKERS = (
    "EXPECTED_CONFDATA_CASE_NAMES = (",
    '"malformed_unset_comment_tokens",',
    '"duplicate_assignments",',
    '"duplicate_malformed_quoted_assignment",',
)

EXPECTED_SELF_TEST_CASE_COUNT = 6


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def collect_missing_markers(text: str, markers: tuple[str, ...], prefix: str) -> list[str]:
    return [f"{prefix}:missing_marker:{marker}" for marker in markers if marker not in text]


def collect_fixdep_case_issues(path: Path) -> list[str]:
    raw = read_json(path)
    if not isinstance(raw, list):
        return [f"{FIXDEP_CASES.as_posix()}:invalid_json_shape"]

    names: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            return [f"{FIXDEP_CASES.as_posix()}:case[{index}]:expected_object"]
        name = item.get("name")
        if not isinstance(name, str):
            return [f"{FIXDEP_CASES.as_posix()}:case[{index}].name:expected_string"]
        names.append(name)

    issues: list[str] = []
    if len(names) != len(FIXDEP_CASE_NAMES):
        issues.append(
            f"{FIXDEP_CASES.as_posix()}:case_count={len(names)}:expected={len(FIXDEP_CASE_NAMES)}"
        )
    for name in FIXDEP_CASE_NAMES:
        if name not in names:
            issues.append(f"{FIXDEP_CASES.as_posix()}:missing_case:{name}")
    for name in sorted(set(names) - set(FIXDEP_CASE_NAMES)):
        issues.append(f"{FIXDEP_CASES.as_posix()}:unexpected_case:{name}")
    return issues


def collect_confdata_packet_issues(cases_path: Path, manifest_path: Path) -> list[str]:
    issues: list[str] = []

    raw_cases = read_json(cases_path)
    if not isinstance(raw_cases, dict):
        return [f"{KCONFIG_CASES.as_posix()}:invalid_json_shape"]
    confdata_cases = raw_cases.get("confdata_cases")
    if not isinstance(confdata_cases, list):
        return [f"{KCONFIG_CASES.as_posix()}:confdata_cases:expected_list"]

    names: list[str] = []
    for index, item in enumerate(confdata_cases):
        if not isinstance(item, dict):
            return [f"{KCONFIG_CASES.as_posix()}:confdata_cases[{index}]:expected_object"]
        name = item.get("name")
        if not isinstance(name, str):
            return [f"{KCONFIG_CASES.as_posix()}:confdata_cases[{index}].name:expected_string"]
        names.append(name)

    if len(names) != len(CONFDATA_CASE_NAMES):
        issues.append(
            f"{KCONFIG_CASES.as_posix()}:confdata_case_count={len(names)}:expected={len(CONFDATA_CASE_NAMES)}"
        )
    for name in CONFDATA_CASE_NAMES:
        if name not in names:
            issues.append(f"{KCONFIG_CASES.as_posix()}:missing_confdata_case:{name}")
    for name in sorted(set(names) - set(CONFDATA_CASE_NAMES)):
        issues.append(f"{KCONFIG_CASES.as_posix()}:unexpected_confdata_case:{name}")

    raw_manifest = read_json(manifest_path)
    if not isinstance(raw_manifest, dict):
        return issues + [f"{CONFDATA_MANIFEST.as_posix()}:invalid_json_shape"]

    case_count = raw_manifest.get("case_count")
    if case_count != len(CONFDATA_CASE_NAMES):
        issues.append(
            f"{CONFDATA_MANIFEST.as_posix()}:case_count={case_count}:expected={len(CONFDATA_CASE_NAMES)}"
        )

    manifest_cases = raw_manifest.get("cases")
    if manifest_cases != list(CONFDATA_CASE_NAMES):
        issues.append(f"{CONFDATA_MANIFEST.as_posix()}:cases_mismatch")

    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).is_file():
            issues.append(f"missing_file:{rel.as_posix()}")

    if issues:
        return issues

    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, FIXDEP_NOTE)),
            FIXDEP_NOTE_MARKERS,
            FIXDEP_NOTE.as_posix(),
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, CONFDATA_NOTE)),
            CONFDATA_NOTE_MARKERS,
            CONFDATA_NOTE.as_posix(),
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, FIXDEP_GATE)),
            FIXDEP_GATE_MARKERS,
            FIXDEP_GATE.as_posix(),
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, KCONFIG_ALIGNMENT)),
            KCONFIG_ALIGNMENT_MARKERS,
            KCONFIG_ALIGNMENT.as_posix(),
        )
    )
    issues.extend(collect_fixdep_case_issues(resolve(root, FIXDEP_CASES)))
    issues.extend(
        collect_confdata_packet_issues(
            resolve(root, KCONFIG_CASES),
            resolve(root, CONFDATA_MANIFEST),
        )
    )
    return issues


def build_sample_root(root: Path) -> None:
    write_text(
        resolve(root, FIXDEP_NOTE),
        "\n".join(
            [
                "# Phase 2 fixdep next step note",
                "",
                *FIXDEP_NOTE_MARKERS,
                "",
            ]
        ),
    )
    write_text(
        resolve(root, CONFDATA_NOTE),
        "\n".join(
            [
                "# Phase 2 Confdata Bridge Survey",
                "",
                *CONFDATA_NOTE_MARKERS,
                "",
            ]
        ),
    )
    write_text(resolve(root, FIXDEP_GATE), "\n".join(FIXDEP_GATE_MARKERS) + "\n")
    write_text(resolve(root, KCONFIG_ALIGNMENT), "\n".join(KCONFIG_ALIGNMENT_MARKERS) + "\n")
    write_text(
        resolve(root, FIXDEP_CASES),
        json.dumps([{"name": name} for name in FIXDEP_CASE_NAMES], indent=2) + "\n",
    )
    write_text(
        resolve(root, KCONFIG_CASES),
        json.dumps(
            {
                "conf_cases": [],
                "confdata_cases": [
                    {"name": name, "input": f"{name}.config", "expected": f"{name}_expected.json"}
                    for name in CONFDATA_CASE_NAMES
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, CONFDATA_MANIFEST),
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
                "status": "closed",
                "case_count": len(CONFDATA_CASE_NAMES),
                "cases": list(CONFDATA_CASE_NAMES),
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_companion_notes_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        if collect_issues(root):
            raise SystemExit("phase2-companion-notes:self-test:good_tree")
        checks_run += 1

        build_sample_root(root)
        write_text(resolve(root, FIXDEP_NOTE), "# Phase 2 fixdep next step note\n")
        issues = collect_issues(root)
        if not any(issue.startswith(f"{FIXDEP_NOTE.as_posix()}:missing_marker:") for issue in issues):
            raise SystemExit("phase2-companion-notes:self-test:fixdep_note_marker")
        checks_run += 1

        build_sample_root(root)
        write_text(
            resolve(root, FIXDEP_CASES),
            json.dumps([{"name": name} for name in FIXDEP_CASE_NAMES[:-1]], indent=2) + "\n",
        )
        issues = collect_issues(root)
        if f"{FIXDEP_CASES.as_posix()}:case_count=12:expected=13" not in issues:
            raise SystemExit("phase2-companion-notes:self-test:fixdep_case_count")
        checks_run += 1

        build_sample_root(root)
        payload = json.loads(read_text(resolve(root, CONFDATA_MANIFEST)))
        payload["case_count"] = 14
        write_text(resolve(root, CONFDATA_MANIFEST), json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        if (
            f"{CONFDATA_MANIFEST.as_posix()}:case_count=14:expected=15"
            not in issues
        ):
            raise SystemExit("phase2-companion-notes:self-test:confdata_manifest_count")
        checks_run += 1

        build_sample_root(root)
        write_text(resolve(root, KCONFIG_ALIGNMENT), "EXPECTED_CONFDATA_CASE_NAMES = (\n)\n")
        issues = collect_issues(root)
        if (
            f'{KCONFIG_ALIGNMENT.as_posix()}:missing_marker:"duplicate_assignments",'
            not in issues
        ):
            raise SystemExit("phase2-companion-notes:self-test:kconfig_alignment_marker")
        checks_run += 1

        build_sample_root(root)
        resolve(root, CONFDATA_NOTE).unlink()
        issues = collect_issues(root)
        if f"missing_file:{CONFDATA_NOTE.as_posix()}" not in issues:
            raise SystemExit("phase2-companion-notes:self-test:missing_file")
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit(
            f"phase2-companion-notes:self-test:count={checks_run}:expected={EXPECTED_SELF_TEST_CASE_COUNT}"
        )

    print("PHASE2_COMPANION_NOTES_PACKET_SELF_TEST=pass")
    print(f"PHASE2_COMPANION_NOTES_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 2 companion notes packet against the current fixdep and confdata evidence surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_COMPANION_NOTES_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_COMPANION_NOTES_PACKET=fail")
        print("PHASE2_COMPANION_NOTES_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_COMPANION_NOTES_PACKET_ISSUES_END")
        return 1

    print("PHASE2_COMPANION_NOTES_PACKET=pass")
    print(f"PHASE2_COMPANION_NOTES_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_COMPANION_NOTES_PACKET_FIXDEP_CASE_COUNT={len(FIXDEP_CASE_NAMES)}")
    print(f"PHASE2_COMPANION_NOTES_PACKET_CONFDATA_CASE_COUNT={len(CONFDATA_CASE_NAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
