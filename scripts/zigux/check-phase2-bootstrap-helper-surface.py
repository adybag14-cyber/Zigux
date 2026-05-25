#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
INSTALL_ZIG = Path("scripts/zigux/install-zig.py")
STAGE_HELPER = Path("scripts/zigux/stage-pinned-zig-archive.py")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
README = Path("third_party/README.md")

EXPECTED_BOOTSTRAP_HELPERS = (
    INSTALL_ZIG.as_posix(),
    STAGE_HELPER.as_posix(),
)

EXPECTED_NOTE_MARKERS = (
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
)

INSTALL_ZIG_MARKERS = (
    "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
    "def load_policy_channel(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_CHANNEL) -> str:",
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "print('ZIG_INSTALL_STATUS=pass')",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
)

STAGE_HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'THIRD_PARTY_DIR = Path("third_party")',
    "def reconstruct_archive_from_parts(",
    "print(\"STAGE_PINNED_ZIG_ARCHIVE=pass\")",
    "print(\"STAGE_PINNED_ZIG_ARCHIVE=fail\")",
    "print(f\"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}\")",
    "print(\"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass\")",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
)

README_MARKERS = (
    "# Zigux third-party archives",
    "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc.msg}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def count_exact_line_occurrences(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_duplicate_strings(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    manifest = read_json(root / MANIFEST)
    if not isinstance(manifest, dict):
        return [("INVALID_MANIFEST_SHAPE", "root")]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    bootstrap_helpers = surfaces.get("bootstrap_helpers")
    if not isinstance(bootstrap_helpers, list):
        issues.append(("MISSING_BOOTSTRAP_HELPERS", "bootstrap_helpers"))
    else:
        non_string_entries = [repr(entry) for entry in bootstrap_helpers if not isinstance(entry, str)]
        for entry in non_string_entries:
            issues.append(("INVALID_BOOTSTRAP_HELPER_ENTRY", entry))
        string_entries = [entry for entry in bootstrap_helpers if isinstance(entry, str)]
        for entry in find_duplicate_strings(string_entries):
            issues.append(("DUPLICATE_BOOTSTRAP_HELPER_ENTRY", entry))
        for entry in EXPECTED_BOOTSTRAP_HELPERS:
            if entry not in string_entries:
                issues.append(("MISSING_BOOTSTRAP_HELPER_ENTRY", entry))
            elif not (root / entry).exists():
                issues.append(("MISSING_BOOTSTRAP_HELPER_PATH", entry))
        if string_entries != list(EXPECTED_BOOTSTRAP_HELPERS):
            issues.append(("BOOTSTRAP_HELPER_ORDER_MISMATCH", "bootstrap_helpers"))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_NOTES", "notes"))
    else:
        string_notes = [note for note in notes if isinstance(note, str)]
        for marker in EXPECTED_NOTE_MARKERS:
            if marker not in string_notes:
                issues.append(("MISSING_NOTE_MARKER", marker))

    install_text = read_text(root / INSTALL_ZIG)
    for marker in INSTALL_ZIG_MARKERS:
        count = count_exact_occurrences(install_text, marker)
        if count == 0:
            issues.append(("MISSING_INSTALL_ZIG_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_INSTALL_ZIG_MARKER", f"{marker}:count={count}"))

    stage_text = read_text(root / STAGE_HELPER)
    for marker in STAGE_HELPER_MARKERS:
        count = count_exact_occurrences(stage_text, marker)
        if count == 0:
            issues.append(("MISSING_STAGE_HELPER_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_STAGE_HELPER_MARKER", f"{marker}:count={count}"))

    workflow_text = read_text(root / WORKFLOW)
    for marker in WORKFLOW_LINES:
        count = count_exact_line_occurrences(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    readme_text = read_text(root / README)
    for marker in README_MARKERS:
        count = count_exact_occurrences(readme_text, marker)
        if count == 0:
            issues.append(("MISSING_README_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_README_MARKER", f"{marker}:count={count}"))

    if not (root / POLICY).exists():
        issues.append(("MISSING_POLICY_PATH", POLICY.as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_HELPER_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "bootstrap_helpers": list(EXPECTED_BOOTSTRAP_HELPERS),
        },
        "notes": list(EXPECTED_NOTE_MARKERS),
    }


def build_self_test_root(root: Path) -> None:
    write_json(root / MANIFEST, build_self_test_manifest())
    write_text(
        root / INSTALL_ZIG,
        "\n".join(INSTALL_ZIG_MARKERS) + "\n",
    )
    write_text(
        root / STAGE_HELPER,
        "\n".join(STAGE_HELPER_MARKERS) + "\n",
    )
    write_text(root / POLICY, "{}\n")
    write_text(root / WORKFLOW, "name: zigux-bootstrap\n" + "\n".join(WORKFLOW_LINES) + "\n")
    write_text(root / README, "\n".join(README_MARKERS) + "\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(EXPECTED_BOOTSTRAP_HELPERS)
        + 1
        + 1
        + 1
        + len(EXPECTED_NOTE_MARKERS)
        + len(INSTALL_ZIG_MARKERS)
        + len(STAGE_HELPER_MARKERS)
        + len(WORKFLOW_LINES)
        + len(README_MARKERS)
        + 1
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_helper_surface_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for entry in EXPECTED_BOOTSTRAP_HELPERS:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["present_surfaces"]["bootstrap_helpers"].remove(entry)
            write_json(root / MANIFEST, manifest)
            assert ("MISSING_BOOTSTRAP_HELPER_ENTRY", entry) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["present_surfaces"]["bootstrap_helpers"].append(EXPECTED_BOOTSTRAP_HELPERS[0])
        write_json(root / MANIFEST, manifest)
        assert ("DUPLICATE_BOOTSTRAP_HELPER_ENTRY", EXPECTED_BOOTSTRAP_HELPERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["present_surfaces"]["bootstrap_helpers"].append(123)
        write_json(root / MANIFEST, manifest)
        assert ("INVALID_BOOTSTRAP_HELPER_ENTRY", "123") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = build_self_test_manifest()
        manifest["present_surfaces"]["bootstrap_helpers"].reverse()
        write_json(root / MANIFEST, manifest)
        assert ("BOOTSTRAP_HELPER_ORDER_MISMATCH", "bootstrap_helpers") in collect_issues(root)
        checks_run += 1

        for marker in EXPECTED_NOTE_MARKERS:
            build_self_test_root(root)
            manifest = build_self_test_manifest()
            manifest["notes"].remove(marker)
            write_json(root / MANIFEST, manifest)
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in INSTALL_ZIG_MARKERS:
            build_self_test_root(root)
            path = root / INSTALL_ZIG
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_INSTALL_ZIG_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in STAGE_HELPER_MARKERS:
            build_self_test_root(root)
            path = root / STAGE_HELPER
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_STAGE_HELPER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "run: python3 missing.py", 1), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            path = root / README
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        (root / POLICY).unlink()
        assert ("MISSING_POLICY_PATH", POLICY.as_posix()) in collect_issues(root)
        checks_run += 1

        (root / MANIFEST).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_HELPER_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_HELPER_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 tool manifest bootstrap-helper surface aligned with the live installer packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_BOOTSTRAP_HELPER_SURFACE=pass")
    print(f"PHASE2_BOOTSTRAP_HELPER_SURFACE_COUNT={len(EXPECTED_BOOTSTRAP_HELPERS)}")
    print(f"PHASE2_BOOTSTRAP_HELPER_SURFACE_NOTE_COUNT={len(EXPECTED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
