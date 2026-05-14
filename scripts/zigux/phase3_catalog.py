#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RUNNER_MARKER_RE = re.compile(
    r"python3 scripts/zigux/run-phase3-checks.py --slug (?P<slug>[a-z0-9-]+)"
)
BUILD_DUMP_RE = re.compile(r"phase3_(?P<family>[a-z0-9_]+)_dump\.zig")
LEGACY_WRAPPER_PATH_RE = re.compile(
    r"scripts/zigux/check-phase3-(?P<slug>[a-z0-9-]+)\.py"
)
TEXT_FILE_SUFFIXES = {
    ".c",
    ".h",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
    ".zig",
}
TEXT_FILE_NAMES = {"Makefile"}
SUPPORT_WRAPPER_REFERENCE_EXCLUDES = {
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/generate-phase3-check-wrappers.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
}


@dataclass(frozen=True)
class Phase3Slice:
    slug: str
    description: str
    doc_path: Path
    check_script: Path
    dump_path: Path
    expected_path: Path
    harness_path: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "slug": self.slug,
            "description": self.description,
            "doc": self.doc_path.relative_to(ROOT).as_posix(),
            "check_script": self.check_script.relative_to(ROOT).as_posix(),
            "dump": self.dump_path.relative_to(ROOT).as_posix(),
            "expected": self.expected_path.relative_to(ROOT).as_posix(),
            "harness": self.harness_path.relative_to(ROOT).as_posix(),
        }


def _slice_family_from_fixture_dir(path: Path) -> str | None:
    name = path.name
    if not name.startswith("phase3_"):
        return None
    return name[len("phase3_") :]


def _dump_family_from_path(path: Path) -> str | None:
    stem = path.stem
    if not stem.startswith("phase3_") or not stem.endswith("_dump"):
        return None
    family = stem[len("phase3_") : -len("_dump")]
    return family or None


def _build_slice(root: Path, family: str) -> Phase3Slice | None:
    slug = family.replace("_", "-")
    doc_path = root / f"Documentation/zigux/phase3-{slug}-slice.md"
    check_script = root / f"scripts/zigux/check-phase3-{slug}.py"
    dump_path = root / f"zigux/tests/phase3_{family}_dump.zig"
    expected_path = root / f"zigux/tests/fixtures/phase3_{family}/expected.json"
    harness_path = root / f"zigux/tests/fixtures/phase3_{family}/phase3_{family}_c_harness.c"
    required = (
        doc_path,
        check_script,
        dump_path,
        expected_path,
        harness_path,
    )
    if not all(path.exists() for path in required):
        return None
    return Phase3Slice(
        slug=slug,
        description=slug.replace("-", " "),
        doc_path=doc_path,
        check_script=check_script,
        dump_path=dump_path,
        expected_path=expected_path,
        harness_path=harness_path,
    )


def discover_phase3_slices(root: Path = ROOT) -> list[Phase3Slice]:
    entries: list[Phase3Slice] = []
    for expected_path in sorted((root / "zigux/tests/fixtures").glob("phase3_*/expected.json")):
        family = _slice_family_from_fixture_dir(expected_path.parent)
        if family is None:
            continue
        entry = _build_slice(root, family)
        if entry is not None:
            entries.append(entry)
    return entries


def discover_phase3_dump_families(root: Path = ROOT) -> set[str]:
    families: set[str] = set()
    for dump_path in sorted((root / "zigux/tests").glob("phase3_*_dump.zig")):
        family = _dump_family_from_path(dump_path)
        if family is not None:
            families.add(family)
    return families


def discover_phase3_build_dump_families(root: Path = ROOT) -> set[str]:
    build_path = root / "zigux/tests/build.zig"
    if not build_path.exists():
        return set()
    return {
        match.group("family")
        for match in BUILD_DUMP_RE.finditer(build_path.read_text(encoding="utf-8"))
    }


def audit_dump_surface_reality(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    discovered_families = {
        family
        for entry in discover_phase3_slices(root)
        if (family := _dump_family_from_path(entry.dump_path)) is not None
    }
    for family in sorted(discover_phase3_dump_families(root) - discovered_families):
        issues.append(
            f"phase3 dump lacks full slice packet: zigux/tests/phase3_{family}_dump.zig"
        )
    return issues


def audit_build_surface_reality(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    discovered_families = {
        family
        for entry in discover_phase3_slices(root)
        if (family := _dump_family_from_path(entry.dump_path)) is not None
    }
    for family in sorted(discover_phase3_build_dump_families(root) - discovered_families):
        issues.append(
            f"phase3 build surface lacks full slice packet: zigux/tests/phase3_{family}_dump.zig"
        )
    return issues


def _shared_runner_marker(slug: str) -> str:
    return f"python3 scripts/zigux/run-phase3-checks.py --slug {slug}"


def _legacy_wrapper_marker(slug: str) -> str:
    return f"python3 scripts/zigux/check-phase3-{slug}.py"


def audit_legacy_wrapper_docs(root: Path = ROOT) -> list[str]:
    docs: list[str] = []
    for entry in discover_phase3_slices(root):
        text = entry.doc_path.read_text(encoding="utf-8")
        if _shared_runner_marker(entry.slug) in text:
            continue
        if _legacy_wrapper_marker(entry.slug) in text:
            docs.append(entry.doc_path.relative_to(root).as_posix())
    return docs


def _iter_repo_text_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root)
        if any(part.startswith(".git") for part in rel_path.parts):
            continue
        if path.name in TEXT_FILE_NAMES or path.suffix in TEXT_FILE_SUFFIXES:
            candidates.append(path)
    return sorted(candidates)


def audit_legacy_wrapper_references(root: Path = ROOT) -> list[str]:
    slice_docs = {
        entry.doc_path.relative_to(root)
        for entry in discover_phase3_slices(root)
    }
    references: list[str] = []
    for path in _iter_repo_text_files(root):
        rel_path = path.relative_to(root)
        if rel_path in slice_docs or rel_path in SUPPORT_WRAPPER_REFERENCE_EXCLUDES:
            continue
        if rel_path.parent == Path("scripts/zigux") and rel_path.name.startswith("check-phase3-"):
            continue
        matches = sorted(
            {
                match.group(0)
                for match in LEGACY_WRAPPER_PATH_RE.finditer(
                    path.read_text(encoding="utf-8")
                )
            }
        )
        for match in matches:
            references.append(f"{rel_path.as_posix()}: {match}")
    return references


def audit_doc_sync(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    required = [
        root / "Documentation/zigux/artifact-diff.md",
        root / "scripts/zigux/run-phase3-checks.py",
        root / "scripts/zigux/phase3_check_lib.py",
        root / "scripts/zigux/generate-phase3-check-wrappers.py",
    ]
    entries = discover_phase3_slices(root)
    required.extend(entry.doc_path for entry in entries)
    for path in required:
        if not path.exists():
            issues.append(f"missing repo file: {path.relative_to(root).as_posix()}")

    artifact_diff = root / "Documentation/zigux/artifact-diff.md"
    if artifact_diff.exists():
        text = artifact_diff.read_text(encoding="utf-8")
        for entry in entries:
            marker = _shared_runner_marker(entry.slug)
            if marker not in text:
                issues.append(f"missing artifact-diff marker: {marker}")

    issues.extend(audit_dump_surface_reality(root))
    issues.extend(audit_build_surface_reality(root))
    issues.extend(audit_artifact_diff_reality(root))
    return issues


def audit_artifact_diff_reality(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    artifact_diff = root / "Documentation/zigux/artifact-diff.md"
    if not artifact_diff.exists():
        return [f"missing repo file: {artifact_diff.relative_to(root).as_posix()}"]

    documented = {
        match.group("slug")
        for match in RUNNER_MARKER_RE.finditer(artifact_diff.read_text(encoding="utf-8"))
    }
    discovered = {entry.slug for entry in discover_phase3_slices(root)}

    for slug in sorted(discovered - documented):
        issues.append(f"discovered slug missing artifact-diff marker: {slug}")
    for slug in sorted(documented - discovered):
        issues.append(f"artifact-diff documents unsupported Phase 3 slug: {slug}")
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests/fixtures/phase3_abi").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
        for rel in [
            "Documentation/zigux/phase3-abi-slice.md",
            "Documentation/zigux/artifact-diff.md",
            "scripts/zigux/run-phase3-checks.py",
            "scripts/zigux/phase3_check_lib.py",
            "scripts/zigux/generate-phase3-check-wrappers.py",
            "scripts/zigux/check-phase3-abi.py",
            "zigux/tests/phase3_abi_dump.zig",
            "zigux/tests/fixtures/phase3_abi/expected.json",
            "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
        ]:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_shared_runner_marker("abi") + "\n", encoding="utf-8")
        (root / "zigux/tests/build.zig").write_text(
            'const abi_dump = "phase3_abi_dump.zig";\n',
            encoding="utf-8",
        )
        assert [entry.slug for entry in discover_phase3_slices(root)] == ["abi"]
        assert audit_doc_sync(root) == []
        assert audit_artifact_diff_reality(root) == []
        assert audit_build_surface_reality(root) == []
        assert audit_legacy_wrapper_docs(root) == []
        assert audit_legacy_wrapper_references(root) == []

        extra_dir = root / "zigux/tests/fixtures/phase3_bitmap_cpumask"
        extra_dir.mkdir(parents=True, exist_ok=True)
        (extra_dir / "expected.json").write_text("{}", encoding="utf-8")
        assert [entry.slug for entry in discover_phase3_slices(root)] == ["abi"]

        stray_dump = root / "zigux/tests/phase3_bitmap_cpumask_dump.zig"
        stray_dump.write_text("// stray\n", encoding="utf-8")
        expected_dump_issue = (
            "phase3 dump lacks full slice packet: "
            "zigux/tests/phase3_bitmap_cpumask_dump.zig"
        )
        assert audit_dump_surface_reality(root) == [expected_dump_issue]
        assert audit_doc_sync(root) == [expected_dump_issue]
        stray_dump.unlink()

        (root / "zigux/tests/build.zig").write_text(
            'const abi_dump = "phase3_abi_dump.zig";\n'
            'const stray_dump = "phase3_bitmap_cpumask_dump.zig";\n',
            encoding="utf-8",
        )
        expected_build_issue = (
            "phase3 build surface lacks full slice packet: "
            "zigux/tests/phase3_bitmap_cpumask_dump.zig"
        )
        assert audit_build_surface_reality(root) == [expected_build_issue]
        assert audit_doc_sync(root) == [expected_build_issue]
        (root / "zigux/tests/build.zig").write_text(
            'const abi_dump = "phase3_abi_dump.zig";\n',
            encoding="utf-8",
        )

        artifact = root / "Documentation/zigux/artifact-diff.md"
        artifact.write_text(
            _shared_runner_marker("abi") + "\n"
            "python3 scripts/zigux/run-phase3-checks.py --slug bitmap-cpumask\n",
            encoding="utf-8",
        )
        expected_artifact_issue = (
            "artifact-diff documents unsupported Phase 3 slug: bitmap-cpumask"
        )
        assert audit_artifact_diff_reality(root) == [expected_artifact_issue]
        assert audit_doc_sync(root) == [expected_artifact_issue]

        artifact.write_text(_shared_runner_marker("abi") + "\n", encoding="utf-8")
        (root / "zigux/tests/build.zig").write_text(
            'const abi_dump = "phase3_abi_dump.zig";\n',
            encoding="utf-8",
        )
        abi_doc = root / "Documentation/zigux/phase3-abi-slice.md"
        abi_doc.write_text(_legacy_wrapper_marker("abi") + "\n", encoding="utf-8")
        assert audit_legacy_wrapper_docs(root) == [
            "Documentation/zigux/phase3-abi-slice.md"
        ]
        assert audit_legacy_wrapper_references(root) == []

        abi_doc.write_text(_shared_runner_marker("abi") + "\n", encoding="utf-8")
        tests_readme = root / "zigux/tests/README.md"
        tests_readme.write_text(
            "wrapper note: scripts/zigux/check-phase3-abi.py\n",
            encoding="utf-8",
        )
        assert audit_legacy_wrapper_references(root) == [
            "zigux/tests/README.md: scripts/zigux/check-phase3-abi.py"
        ]

        support_note = root / "Documentation/zigux/phase3-support-note.md"
        support_note.write_text(
            "wrapper note: scripts/zigux/check-phase3-abi.py\n",
            encoding="utf-8",
        )
        assert audit_legacy_wrapper_references(root) == [
            "Documentation/zigux/phase3-support-note.md: scripts/zigux/check-phase3-abi.py",
            "zigux/tests/README.md: scripts/zigux/check-phase3-abi.py",
        ]
    print("PHASE3_CATALOG_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Focused Phase 3 catalog helper.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--audit-doc-sync", action="store_true")
    parser.add_argument("--audit-build-surface-reality", action="store_true")
    parser.add_argument("--audit-artifact-diff-reality", action="store_true")
    parser.add_argument("--legacy-wrapper-docs", action="store_true")
    parser.add_argument("--legacy-wrapper-references", action="store_true")
    parser.add_argument("--print-slices", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    entries = discover_phase3_slices()
    if args.print_slices:
        print(json.dumps([entry.to_dict() for entry in entries], indent=2, sort_keys=True))

    if args.audit_doc_sync:
        issues = audit_doc_sync()
        if issues:
            print("PHASE3_DOC_SYNC_AUDIT=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE3_DOC_SYNC_AUDIT=pass")
        return 0

    if args.audit_build_surface_reality:
        issues = audit_build_surface_reality()
        if issues:
            print("PHASE3_BUILD_SURFACE_REALITY=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE3_BUILD_SURFACE_REALITY=pass")
        return 0

    if args.audit_artifact_diff_reality:
        issues = audit_artifact_diff_reality()
        if issues:
            print("PHASE3_ARTIFACT_DIFF_REALITY=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE3_ARTIFACT_DIFF_REALITY=pass")
        return 0

    if args.legacy_wrapper_docs:
        docs = audit_legacy_wrapper_docs()
        if not docs:
            print("PHASE3_LEGACY_WRAPPER_DOCS=none")
            return 0
        for path in docs:
            print(path)
        return 0

    if args.legacy_wrapper_references:
        references = audit_legacy_wrapper_references()
        if not references:
            print("PHASE3_LEGACY_WRAPPER_REFERENCES=none")
            return 0
        for reference in references:
            print(reference)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
