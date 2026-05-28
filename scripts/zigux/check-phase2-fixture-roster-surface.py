#!/usr/bin/env python3
"""Fail closed when the Phase 2 fixture-roster manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_FIXTURE_ROSTER = (
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/oldaskconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/syncconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/oldconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allyesconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allmodconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/alldefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/listnewconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/yes2modconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/mod2yesconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/mod2noconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/sample.config",
    "zigux/tests/fixtures/kconfig_bridge/escaped_strings.config",
    "zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences.config",
    "zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash.config",
    "zigux/tests/fixtures/kconfig_bridge/sample_crlf.config",
    "zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate.config",
    "zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return.config",
    "zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment.config",
    "zigux/tests/fixtures/kconfig_bridge/uppercase_tristate.config",
    "zigux/tests/fixtures/kconfig_bridge/non_config_lines.config",
    "zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names.config",
    "zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens.config",
    "zigux/tests/fixtures/kconfig_bridge/last_state_transitions.config",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_assignments.config",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment.config",
    "zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments.config",
    "zigux/tests/fixtures/kconfig_bridge/sample_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/escaped_strings_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/sample_crlf_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/uppercase_tristate_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/non_config_lines_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/last_state_transitions_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_assignments_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(entries: list[str] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "fixture_roster": list(
                EXPECTED_FIXTURE_ROSTER if entries is None else entries
            ),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def count_exact_entries(entries: list[str], marker: str) -> int:
    return sum(1 for entry in entries if entry == marker)


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    if not isinstance(manifest, dict):
        return ["invalid manifest root object"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    fixture_roster = surfaces.get("fixture_roster")
    if not isinstance(fixture_roster, list):
        return ["invalid fixture_roster list"]

    issues: list[str] = []
    for index, entry in enumerate(fixture_roster):
        if not isinstance(entry, str):
            issues.append(f"invalid fixture_roster entry at index {index}: {entry!r}")

    string_entries = [entry for entry in fixture_roster if isinstance(entry, str)]
    if len(fixture_roster) != len(EXPECTED_FIXTURE_ROSTER):
        issues.append(
            "fixture_roster count drift: "
            f"expected {len(EXPECTED_FIXTURE_ROSTER)}, found {len(fixture_roster)}"
        )

    for expected in EXPECTED_FIXTURE_ROSTER:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing fixture_roster entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate fixture_roster entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_FIXTURE_ROSTER):
        if index >= len(fixture_roster):
            continue
        actual = fixture_roster[index]
        if actual != expected:
            issues.append(
                f"fixture_roster order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_FIXTURE_ROSTER:
            issues.append(f"unexpected fixture_roster entry: {entry}")
        elif not (repo_root / entry).exists():
            issues.append(f"missing fixture_roster path: {entry}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixture_roster_surface_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        for relative_path in EXPECTED_FIXTURE_ROSTER:
            _write(root / relative_path, "present\n")

        issues = validate(root)
        if issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "[]\n")
        issues = validate(root)
        if "invalid manifest root object" not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest root object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": []}\n',
        )
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"fixture_roster": "bad"}}\n',
        )
        issues = validate(root)
        if "invalid fixture_roster list" not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected invalid fixture_roster list was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_FIXTURE_ROSTER[:-1])),
        )
        missing_issue = (
            "missing fixture_roster entry: "
            "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"
        )
        issues = validate(root)
        if missing_issue not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected missing fixture_roster entry was not reported")
            return 1
        case_count += 1

        invalid_entries = list(EXPECTED_FIXTURE_ROSTER)
        invalid_entries[1] = 7  # type: ignore[list-item]
        payload = {
            "phase": "Phase 2",
            "present_surfaces": {
                "fixture_roster": invalid_entries,
            },
        }
        _write(root / MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        issues = validate(root)
        if "invalid fixture_roster entry at index 1: 7" not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected invalid fixture_roster entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_FIXTURE_ROSTER)
        duplicate_entries[-1] = EXPECTED_FIXTURE_ROSTER[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        duplicate_issue = (
            "duplicate fixture_roster entry: "
            "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json:count=2"
        )
        issues = validate(root)
        if duplicate_issue not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected duplicate fixture_roster entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_FIXTURE_ROSTER)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        order_issue = (
            "fixture_roster order drift at index 0: "
            "expected 'zigux/tests/fixtures/kconfig_bridge/cases.json', "
            "found 'zigux/tests/fixtures/kconfig_bridge/conf_manifest.json'"
        )
        issues = validate(root)
        if order_issue not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected fixture_roster order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_FIXTURE_ROSTER) + [
            "zigux/tests/fixtures/genksyms_bridge/unexpected_extra_expected.json"
        ]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / extra_entries[-1], "present\n")
        issues = validate(root)
        if (
            "unexpected fixture_roster entry: "
            "zigux/tests/fixtures/genksyms_bridge/unexpected_extra_expected.json"
        ) not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected unexpected fixture_roster entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        missing_path = root / EXPECTED_FIXTURE_ROSTER[-1]
        missing_path.unlink()
        issues = validate(root)
        missing_path_issue = (
            "missing fixture_roster path: "
            "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"
        )
        if missing_path_issue not in issues:
            print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=fail")
            print("expected missing fixture_roster path was not reported")
            return 1
        case_count += 1

    print("PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_FIXTURE_ROSTER_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_FIXTURE_ROSTER:
        _write(root / relative_path, "present\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 fixture-roster surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 2 tool manifest",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"wrote sample root to {args.write_sample_root}")
        return 0

    issues = validate(args.root)
    if issues:
        print("PHASE2_FIXTURE_ROSTER_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_FIXTURE_ROSTER_SURFACE=pass")
    print(f"PHASE2_FIXTURE_ROSTER_SURFACE_COUNT={len(EXPECTED_FIXTURE_ROSTER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
