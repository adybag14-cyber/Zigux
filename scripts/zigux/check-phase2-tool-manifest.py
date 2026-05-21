#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

KCONFIG_CONF_STDOUT_PACKET = (
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
)

KCONFIG_CONFDATA_INPUT_PACKET = (
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
)

KCONFIG_CONFDATA_EXPECTED_PACKET = (
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
)

REQUIRED_PRESENT_SURFACES = {
    "review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
    "closure_notes": (
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ),
    "validators": (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ),
    "checkers": (
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "scripts/zigux/check-lane05-local-archive-readme.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kbuild-routes.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-docs-shared-reminder.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
    ),
    "bootstrap_helpers": (
        "scripts/zigux/install-zig.py",
    ),
    "bridge_helpers": (
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    ),
    "policy": (
        "scripts/zigux/zig-toolchain-policy.json",
    ),
    "archive_support": (
        "third_party/README.md",
        "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    ),
    "make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "cross_route_support": (
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ),
    "artifact_support": (
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "fixdep_support": (
        "scripts/basic/fixdep.c",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
        "zigux/tests/fixtures/fixdep/dep:colon.so",
        "zigux/tests/fixtures/fixdep/dep\\ name.rmeta",
        "zigux/tests/fixtures/fixdep/escaped\\ space-config.h",
        "zigux/tests/fixtures/fixdep/sample-config.h",
        "zigux/tests/fixtures/fixdep/sample.c",
        "zigux/tests/fixtures/fixdep/sample.d",
        "zigux/tests/fixtures/fixdep/sample.h",
        "zigux/tests/fixtures/fixdep/sample.rmeta",
        "zigux/tests/fixtures/fixdep/sample2-config.h",
        "zigux/tests/fixtures/fixdep/sample2.c",
        "zigux/tests/fixtures/fixdep/sample2.so",
        "zigux/tests/fixtures/fixdep/sample_comment_continuation.d",
        "zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so",
        "zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c",
        "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta",
        "zigux/tests/fixtures/fixdep/sample_comment_only.d",
        "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
        "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_concatenated.d",
        "zigux/tests/fixtures/fixdep/sample_concatenated_dep.h",
        "zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_concatenated_source.c",
        "zigux/tests/fixtures/fixdep/sample_concatenated_temp.c",
        "zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h",
        "zigux/tests/fixtures/fixdep/sample_dependency_continuation.d",
        "zigux/tests/fixtures/fixdep/sample_dependency_continuation_dep.so",
        "zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c",
        "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.rmeta",
        "zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d",
        "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt",
        "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta",
        "zigux/tests/fixtures/fixdep/sample_escaped_colon.d",
        "zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c",
        "zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta",
        "zigux/tests/fixtures/fixdep/sample_escaped_space.d",
        "zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_escaped_space_source.c",
        "zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta",
        "zigux/tests/fixtures/fixdep/sample_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
        "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
        "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_missing_dep_source.c",
        "zigux/tests/fixtures/fixdep/sample_multi_target.d",
        "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
        "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt",
        "zigux/tests/fixtures/fixdep/shared#config.h",
        "zigux/tests/fixtures/fixdep/shared:config.h",
    ),
    "fixture_roster": (
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        *KCONFIG_CONF_STDOUT_PACKET,
        *KCONFIG_CONFDATA_INPUT_PACKET,
        *KCONFIG_CONFDATA_EXPECTED_PACKET,
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
        "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    ),
}

REQUIRED_NOTE_MARKERS = (
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option version-side-effect proof, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep the dedicated manifest guards explicit through scripts/zigux/check-phase2-tool-manifest.py and scripts/zigux/check-phase2-artifact-tools-manifest.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option version-side-effect proof, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
)


def read_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def find_duplicate_strings(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def is_repo_relative_path(entry: str) -> bool:
    return not entry.startswith("make -C ")


def iter_required_repo_paths() -> tuple[tuple[str, str], ...]:
    return tuple(
        (category, entry)
        for category, entries in REQUIRED_PRESENT_SURFACES.items()
        for entry in entries
        if is_repo_relative_path(entry)
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_manifest(root / MANIFEST)
    issues: list[tuple[str, str]] = []
    for key, expected in REQUIRED_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            issues.append(("TOP_LEVEL_MISMATCH", key))
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("MISSING_PRESENT_SURFACES", "present_surfaces"))
    else:
        for category, required_entries in REQUIRED_PRESENT_SURFACES.items():
            entries = surfaces.get(category)
            if not isinstance(entries, list):
                issues.append(("MISSING_SURFACE_CATEGORY", category))
                continue
            non_string_entries = [repr(entry) for entry in entries if not isinstance(entry, str)]
            for entry in non_string_entries:
                issues.append(("INVALID_SURFACE_ENTRY", f"{category}:{entry}"))
            string_entries = [entry for entry in entries if isinstance(entry, str)]
            for entry in find_duplicate_strings(string_entries):
                issues.append(("DUPLICATE_SURFACE_ENTRY", f"{category}:{entry}"))
            for entry in required_entries:
                if entry not in string_entries:
                    issues.append(("MISSING_SURFACE_ENTRY", f"{category}:{entry}"))
            if string_entries != list(required_entries):
                issues.append(("SURFACE_ORDER_MISMATCH", category))
            for entry in string_entries:
                if is_repo_relative_path(entry) and not (root / entry).exists():
                    issues.append(("MISSING_SURFACE_PATH", f"{category}:{entry}"))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps"))
    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_NOTES", "notes"))
    else:
        non_string_notes = [repr(note) for note in notes if not isinstance(note, str)]
        for note in non_string_notes:
            issues.append(("INVALID_NOTE_ENTRY", note))
        string_notes = [note for note in notes if isinstance(note, str)]
        for marker in find_duplicate_strings(string_notes):
            issues.append(("DUPLICATE_NOTE_ENTRY", marker))
        for marker in REQUIRED_NOTE_MARKERS:
            if marker not in string_notes:
                issues.append(("MISSING_NOTE_MARKER", marker))
        if string_notes != list(REQUIRED_NOTE_MARKERS):
            issues.append(("NOTE_ORDER_MISMATCH", "notes"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOL_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def build_self_test_manifest() -> dict:
    return {
        **REQUIRED_TOP_LEVEL,
        "present_surfaces": {
            category: list(entries)
            for category, entries in REQUIRED_PRESENT_SURFACES.items()
        },
        "repo_reality_gaps": [],
        "notes": list(REQUIRED_NOTE_MARKERS),
    }


def build_self_test_root(root: Path) -> None:
    write_manifest(root / MANIFEST, build_self_test_manifest())
    for _, entry in iter_required_repo_paths():
        write_text(root / entry, "present\n")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_TOP_LEVEL)
        + 1
        + sum(1 for entries in REQUIRED_PRESENT_SURFACES.values() if len(entries) > 1)
        + sum(len(entries) for entries in REQUIRED_PRESENT_SURFACES.values())
        + len(REQUIRED_PRESENT_SURFACES)
        + len(REQUIRED_PRESENT_SURFACES)
        + len(REQUIRED_PRESENT_SURFACES)
        + len(iter_required_repo_paths())
        + 1
        + 1
        + len(REQUIRED_NOTE_MARKERS)
        + 1
        + 1
        + 1
        + 1
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        manifest_path = root / MANIFEST
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for key in REQUIRED_TOP_LEVEL:
            manifest = build_self_test_manifest()
            manifest[key] = "broken"
            write_manifest(manifest_path, manifest)
            for _, entry in iter_required_repo_paths():
                write_text(root / entry, "present\n")
            assert ("TOP_LEVEL_MISMATCH", key) in collect_issues(root)
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["present_surfaces"] = []
        write_manifest(manifest_path, manifest)
        assert ("MISSING_PRESENT_SURFACES", "present_surfaces") in collect_issues(root)
        checks_run += 1

        for category, entries in REQUIRED_PRESENT_SURFACES.items():
            manifest = build_self_test_manifest()
            del manifest["present_surfaces"][category]
            write_manifest(manifest_path, manifest)
            for _, entry in iter_required_repo_paths():
                write_text(root / entry, "present\n")
            assert ("MISSING_SURFACE_CATEGORY", category) in collect_issues(root)
            checks_run += 1
            for entry in entries:
                manifest = build_self_test_manifest()
                manifest["present_surfaces"][category].remove(entry)
                write_manifest(manifest_path, manifest)
                for _, required_entry in iter_required_repo_paths():
                    write_text(root / required_entry, "present\n")
                assert ("MISSING_SURFACE_ENTRY", f"{category}:{entry}") in collect_issues(root)
                checks_run += 1
            manifest = build_self_test_manifest()
            manifest["present_surfaces"][category].append(entries[0])
            write_manifest(manifest_path, manifest)
            for _, entry in iter_required_repo_paths():
                write_text(root / entry, "present\n")
            assert ("DUPLICATE_SURFACE_ENTRY", f"{category}:{entries[0]}") in collect_issues(root)
            checks_run += 1
            manifest = build_self_test_manifest()
            manifest["present_surfaces"][category].append(123)
            write_manifest(manifest_path, manifest)
            for _, entry in iter_required_repo_paths():
                write_text(root / entry, "present\n")
            assert ("INVALID_SURFACE_ENTRY", f"{category}:123") in collect_issues(root)
            checks_run += 1
            if len(entries) > 1:
                manifest = build_self_test_manifest()
                reordered = manifest["present_surfaces"][category]
                reordered[0], reordered[1] = reordered[1], reordered[0]
                write_manifest(manifest_path, manifest)
                for _, entry in iter_required_repo_paths():
                    write_text(root / entry, "present\n")
                assert ("SURFACE_ORDER_MISMATCH", category) in collect_issues(root)
                checks_run += 1

        for category, entry in iter_required_repo_paths():
            build_self_test_root(root)
            (root / entry).unlink()
            assert ("MISSING_SURFACE_PATH", f"{category}:{entry}") in collect_issues(root)
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["repo_reality_gaps"] = ["unexpected-gap"]
        write_manifest(manifest_path, manifest)
        for _, entry in iter_required_repo_paths():
            write_text(root / entry, "present\n")
        assert ("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps") in collect_issues(root)
        checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"] = "broken"
        write_manifest(manifest_path, manifest)
        for _, entry in iter_required_repo_paths():
            write_text(root / entry, "present\n")
        assert ("MISSING_NOTES", "notes") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            manifest = build_self_test_manifest()
            manifest["notes"].remove(marker)
            write_manifest(manifest_path, manifest)
            for _, entry in iter_required_repo_paths():
                write_text(root / entry, "present\n")
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"].append(REQUIRED_NOTE_MARKERS[0])
        write_manifest(manifest_path, manifest)
        for _, entry in iter_required_repo_paths():
            write_text(root / entry, "present\n")
        assert ("DUPLICATE_NOTE_ENTRY", REQUIRED_NOTE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"].append(123)
        write_manifest(manifest_path, manifest)
        for _, entry in iter_required_repo_paths():
            write_text(root / entry, "present\n")
        assert ("INVALID_NOTE_ENTRY", "123") in collect_issues(root)
        checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"][0], manifest["notes"][1] = manifest["notes"][1], manifest["notes"][0]
        write_manifest(manifest_path, manifest)
        for _, entry in iter_required_repo_paths():
            write_text(root / entry, "present\n")
        assert ("NOTE_ORDER_MISMATCH", "notes") in collect_issues(root)
        checks_run += 1

        manifest_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_TOOL_MANIFEST_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 tool manifest aligned with the current repo-tooling packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_TOOL_MANIFEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_REQUIRED_SURFACE_COUNT={sum(len(entries) for entries in REQUIRED_PRESENT_SURFACES.values())}")
    print(f"PHASE2_TOOL_MANIFEST_REQUIRED_NOTE_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
