#!/usr/bin/env python3
"""Fail closed when the Phase 2 archive-support manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
README_PATH = Path("third_party/README.md")
ARCHIVE_PATH = Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")

EXPECTED_ARCHIVE_SUPPORT = (
    README_PATH.as_posix(),
    ARCHIVE_PATH.as_posix(),
)

EXPECTED_NOTE_MARKERS = (
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
)

README_MARKERS = (
    "# Zigux third-party archives",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    _write(path, json.dumps(payload, indent=2) + "\n")


def _sample_manifest(
    archive_support: list[object] | None = None,
    *,
    present_surfaces: object | None = None,
    notes: list[object] | None = None,
) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": (
            {"archive_support": list(EXPECTED_ARCHIVE_SUPPORT)}
            if present_surfaces is None
            else present_surfaces
        ),
        "notes": list(EXPECTED_NOTE_MARKERS) if notes is None else notes,
    }
    if archive_support is not None:
        payload["present_surfaces"] = {"archive_support": list(archive_support)}
    return json.dumps(payload, indent=2) + "\n"


def count_exact_entries(entries: list[str], marker: str) -> int:
    return sum(1 for entry in entries if entry == marker)


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def validate(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    if not isinstance(manifest, dict):
        return ["invalid manifest root"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    archive_support = surfaces.get("archive_support")
    if not isinstance(archive_support, list):
        return ["invalid archive_support list"]

    issues: list[str] = []
    for index, entry in enumerate(archive_support):
        if not isinstance(entry, str):
            issues.append(f"invalid archive_support entry at index {index}: {entry!r}")

    string_entries = [entry for entry in archive_support if isinstance(entry, str)]

    if len(archive_support) != len(EXPECTED_ARCHIVE_SUPPORT):
        issues.append(
            "archive_support count drift: "
            f"expected {len(EXPECTED_ARCHIVE_SUPPORT)}, found {len(archive_support)}"
        )

    for expected in EXPECTED_ARCHIVE_SUPPORT:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing archive_support entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate archive_support entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_ARCHIVE_SUPPORT):
        if index >= len(archive_support):
            continue
        actual = archive_support[index]
        if actual != expected:
            issues.append(
                f"archive_support order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_ARCHIVE_SUPPORT:
            issues.append(f"unexpected archive_support entry: {entry}")
        elif not (root / entry).exists():
            issues.append(f"missing archive_support path: {entry}")

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append("invalid notes list")
    else:
        string_notes = [note for note in notes if isinstance(note, str)]
        for marker in EXPECTED_NOTE_MARKERS:
            if marker not in string_notes:
                issues.append(f"missing archive_support note marker: {marker}")

    readme_path = root / README_PATH
    if not readme_path.is_file():
        issues.append(f"missing archive_support path: {README_PATH.as_posix()}")
    else:
        readme_text = readme_path.read_text(encoding="utf-8")
        for marker in README_MARKERS:
            count = count_exact_occurrences(readme_text, marker)
            if count == 0:
                issues.append(f"missing archive_support readme marker: {marker}")
            elif count != 1:
                issues.append(f"duplicate archive_support readme marker: {marker}:count={count}")

    return issues


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(
        root / README_PATH,
        "\n".join(
            (
                README_MARKERS[0],
                "",
                "## Current pinned Zig archive contract",
                "",
                README_MARKERS[1],
                "",
            )
        ),
    )
    _write(root / ARCHIVE_PATH, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_archive_support_surface_") as temp_dir:
        root = Path(temp_dir)

        write_sample_root(root)
        issues = validate(root)
        if issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","present_surfaces":[]}\n')
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(
            root / MANIFEST_PATH,
            '{"phase":"Phase 2","present_surfaces":{"archive_support":"bad"},"notes":[]}\n',
        )
        issues = validate(root)
        if "invalid archive_support list" not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid archive_support list was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, _sample_manifest(list(EXPECTED_ARCHIVE_SUPPORT[:-1])))
        issues = validate(root)
        missing_issue = (
            "missing archive_support entry: "
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        )
        if missing_issue not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing archive_support entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(
            root / MANIFEST_PATH,
            _sample_manifest([EXPECTED_ARCHIVE_SUPPORT[0], 7]),
        )
        issues = validate(root)
        if "invalid archive_support entry at index 1: 7" not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid archive_support entry type was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        duplicate_entries = list(EXPECTED_ARCHIVE_SUPPORT)
        duplicate_entries[-1] = EXPECTED_ARCHIVE_SUPPORT[0]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = (
            "duplicate archive_support entry: third_party/README.md:count=2"
        )
        if duplicate_issue not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected duplicate archive_support entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        reordered_entries = list(EXPECTED_ARCHIVE_SUPPORT)
        reordered_entries[0], reordered_entries[1] = reordered_entries[1], reordered_entries[0]
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "archive_support order drift at index 0: "
            "expected 'third_party/README.md', "
            "found 'third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'"
        )
        if order_issue not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected archive_support order drift was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        extra_entries = list(EXPECTED_ARCHIVE_SUPPORT) + ["third_party/extra.tar.xz"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "third_party/extra.tar.xz", "present\n")
        issues = validate(root)
        if "unexpected archive_support entry: third_party/extra.tar.xz" not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected unexpected archive_support entry was not reported")
            return 1
        case_count += 1

        for marker in EXPECTED_NOTE_MARKERS:
            write_sample_root(root)
            _write(
                root / MANIFEST_PATH,
                _sample_manifest(notes=[note for note in EXPECTED_NOTE_MARKERS if note != marker]),
            )
            issues = validate(root)
            if f"missing archive_support note marker: {marker}" not in issues:
                print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
                print("expected missing archive_support note marker was not reported")
                return 1
            case_count += 1

        for marker in README_MARKERS:
            write_sample_root(root)
            readme_path = root / README_PATH
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(marker, "", 1),
                encoding="utf-8",
            )
            issues = validate(root)
            if f"missing archive_support readme marker: {marker}" not in issues:
                print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
                print("expected missing archive_support readme marker was not reported")
                return 1
            case_count += 1

        write_sample_root(root)
        (root / ARCHIVE_PATH).unlink()
        issues = validate(root)
        missing_path_issue = (
            "missing archive_support path: "
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        )
        if missing_path_issue not in issues:
            print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing archive_support path was not reported")
            return 1
        case_count += 1

    print("PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_ARCHIVE_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 archive support surface."
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
        print("PHASE2_ARCHIVE_SUPPORT_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_ARCHIVE_SUPPORT_SURFACE=pass")
    print(f"PHASE2_ARCHIVE_SUPPORT_SURFACE_COUNT={len(EXPECTED_ARCHIVE_SUPPORT)}")
    print(f"PHASE2_ARCHIVE_SUPPORT_SURFACE_NOTE_COUNT={len(EXPECTED_NOTE_MARKERS)}")
    print(f"PHASE2_ARCHIVE_SUPPORT_SURFACE_README_MARKER_COUNT={len(README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
