#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "Documentation" / "zigux"
SCRIPTS_DIR = ROOT / "scripts" / "zigux"
TESTS_DIR = ROOT / "zigux" / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
ARTIFACT_DIFF_PATH = DOCS_DIR / "artifact-diff.md"

DOC_PREFIX = "phase3-"
DOC_SUFFIX = "-slice.md"
SCRIPT_PREFIX = "check-phase3-"
SCRIPT_SUFFIX = ".py"
FIXTURE_PREFIX = "phase3_"
MANIFEST_SUFFIX = "_manifest.json"
DUMP_SUFFIX = "_dump.zig"

SPECIAL_BUILD_STEPS = {
    "abi": "phase3-dump",
}

SPECIAL_DESCRIPTIONS = {
    "abi": "ABI layout",
    "bitmap-cpumask": "bitmap/cpumask",
    "list-hlist": "list/hlist",
    "errptr-xarray": "err_ptr/xarray",
    "xarray-slot": "xarray slot",
    "idr-slot": "idr slot",
    "ida-alloc": "ida allocation",
    "ida-bitmap": "ida bitmap",
    "ida-range": "ida range",
    "ida-range-set": "ida range-set",
    "ida-policy": "ida policy",
    "minor-alloc": "minor allocation",
}

INTEROP_GATE_PREFIX = "PHASE3_INTEROP_GATE="
LEGACY_WRAPPER_REF_RE = re.compile(r"(?P<command>python3\s+)?scripts/zigux/check-phase3-(?P<slug>[a-z0-9-]+)\.py")
ARTIFACT_DIFF_PHASE3_SLUG_RE = re.compile(r"--slug (?P<slug>[a-z0-9-]+)")


@dataclass(frozen=True)
class Phase3Paths:
    root: Path
    docs_dir: Path
    scripts_dir: Path
    tests_dir: Path
    fixtures_dir: Path


@dataclass(frozen=True)
class Phase3Slice:
    root: Path
    slug: str
    description: str
    build_step: str
    doc_path: Path
    check_script: Path
    dump_path: Path
    fixture_dir: Path
    expected_path: Path
    harness_path: Path
    manifest_candidates: tuple[Path, ...]
    manifest_path: Path | None
    interop_gate: str | None
    interop_gate_mode: str

    @property
    def fixture_key(self) -> str:
        return f"{FIXTURE_PREFIX}{self.slug.replace('-', '_')}"

    def to_dict(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "description": self.description,
            "build_step": self.build_step,
            "doc": _rel(self.doc_path, self.root),
            "check_script": _rel(self.check_script, self.root),
            "dump": _rel(self.dump_path, self.root),
            "fixture_dir": _rel(self.fixture_dir, self.root),
            "expected": _rel(self.expected_path, self.root),
            "harness": _rel(self.harness_path, self.root),
            "manifest_candidates": [_rel(path, self.root) for path in self.manifest_candidates],
            "manifest": _rel(self.manifest_path, self.root) if self.manifest_path else None,
            "interop_gate": self.interop_gate,
            "interop_gate_mode": self.interop_gate_mode,
        }


@dataclass(frozen=True)
class LegacyWrapperReference:
    root: Path
    path: Path
    line_number: int
    slug: str
    line: str
    kind: str
    scope: str

    @property
    def replacement(self) -> str:
        return f"python3 scripts/zigux/run-phase3-checks.py --slug {self.slug}"

    def to_row(self) -> str:
        return "\t".join(
            [
                _rel(self.path, self.root),
                str(self.line_number),
                self.slug,
                self.kind,
                self.scope,
                self.replacement,
            ]
        )


DEFAULT_PATHS = Phase3Paths(
    root=ROOT,
    docs_dir=DOCS_DIR,
    scripts_dir=SCRIPTS_DIR,
    tests_dir=TESTS_DIR,
    fixtures_dir=FIXTURES_DIR,
)


def _rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def _slug_from_doc(path: Path) -> str | None:
    name = path.name
    if not name.startswith(DOC_PREFIX) or not name.endswith(DOC_SUFFIX):
        return None
    return name[len(DOC_PREFIX) : -len(DOC_SUFFIX)]


def _slug_from_script(path: Path) -> str | None:
    name = path.name
    if not name.startswith(SCRIPT_PREFIX) or not name.endswith(SCRIPT_SUFFIX):
        return None
    return name[len(SCRIPT_PREFIX) : -len(SCRIPT_SUFFIX)]


def _slug_from_fixture_key(raw: str) -> str | None:
    if not raw.startswith(FIXTURE_PREFIX):
        return None
    return raw[len(FIXTURE_PREFIX) :].replace("_", "-")


def _slug_from_dump(path: Path) -> str | None:
    name = path.name
    if not name.startswith(FIXTURE_PREFIX) or not name.endswith(DUMP_SUFFIX):
        return None
    return _slug_from_fixture_key(name[: -len(DUMP_SUFFIX)])


def _slug_from_manifest(path: Path) -> str | None:
    name = path.name
    if not name.startswith(FIXTURE_PREFIX) or not name.endswith(MANIFEST_SUFFIX):
        return None
    return _slug_from_fixture_key(name[: -len(MANIFEST_SUFFIX)])


def _collect_slugs(paths: Phase3Paths = DEFAULT_PATHS) -> list[str]:
    slugs: set[str] = set()

    for path in paths.docs_dir.glob(f"{DOC_PREFIX}*{DOC_SUFFIX}"):
        slug = _slug_from_doc(path)
        if slug:
            slugs.add(slug)

    for path in paths.tests_dir.glob(f"{FIXTURE_PREFIX}*{DUMP_SUFFIX}"):
        slug = _slug_from_dump(path)
        if slug:
            slugs.add(slug)

    for path in paths.fixtures_dir.glob(f"{FIXTURE_PREFIX}*"):
        if path.is_dir():
            slug = _slug_from_fixture_key(path.name)
        else:
            slug = _slug_from_manifest(path)
        if slug:
            slugs.add(slug)

    return sorted(slugs)


def discover_phase3_wrapper_scripts(paths: Phase3Paths = DEFAULT_PATHS) -> list[Path]:
    return sorted(paths.scripts_dir.glob(f"{SCRIPT_PREFIX}*{SCRIPT_SUFFIX}"))


def _load_manifest(path: Path) -> dict[str, object] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _manifest_score(data: dict[str, object], slug: str) -> tuple[int, int]:
    files = data.get("files")
    file_count = data.get("file_count")
    score = 0
    if data.get("phase") == "Phase 3":
        score += 4
    if isinstance(data.get("status"), str) and data["status"]:
        score += 2
    if isinstance(data.get("slice"), str) and data["slice"]:
        score += 2
    if isinstance(files, list):
        score += 2
        if isinstance(file_count, int) and file_count == len(files):
            score += 1
    if slug == "abi" and data.get("slice") == "abi-substrate-skeleton":
        score += 2
    return score, 1 if isinstance(files, list) else 0


def _pick_manifest(slug: str, candidates: Iterable[Path]) -> Path | None:
    best_path: Path | None = None
    best_score: tuple[int, int] = (-1, -1)
    for path in candidates:
        data = _load_manifest(path)
        if data is None:
            continue
        score = _manifest_score(data, slug)
        if score > best_score:
            best_score = score
            best_path = path
    if best_path is not None:
        return best_path
    for path in candidates:
        if path.exists():
            return path
    return None


def description_for_slug(slug: str) -> str:
    return SPECIAL_DESCRIPTIONS.get(slug, slug.replace("-", " "))


def build_step_for_slug(slug: str) -> str:
    return SPECIAL_BUILD_STEPS.get(slug, f"phase3-{slug}-dump")


def shared_runner_gate_for_slug(slug: str) -> str:
    return f"{INTEROP_GATE_PREFIX}python3 scripts/zigux/run-phase3-checks.py --slug {slug}"


def legacy_wrapper_gate_for_slug(slug: str) -> str:
    return f"{INTEROP_GATE_PREFIX}python3 scripts/zigux/check-phase3-{slug}.py"


def _extract_interop_gate_marker(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("- `") and stripped.endswith("`"):
        stripped = stripped[3:-1]
    if stripped.startswith(INTEROP_GATE_PREFIX):
        return stripped
    return None


def discover_doc_interop_gate(doc_path: Path, slug: str) -> tuple[str | None, str]:
    try:
        lines = doc_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None, "missing_doc"

    marker = next((candidate for line in lines if (candidate := _extract_interop_gate_marker(line)) is not None), None)
    if marker is None:
        return None, "missing"
    if marker == shared_runner_gate_for_slug(slug):
        return marker, "shared-runner"
    if marker == legacy_wrapper_gate_for_slug(slug):
        return marker, "legacy-wrapper"
    return marker, "custom"


def rewrite_legacy_wrapper_docs(entries: list[Phase3Slice]) -> list[str]:
    rewritten: list[str] = []
    for entry in entries:
        if entry.interop_gate_mode != "legacy-wrapper":
            continue
        legacy = f"python3 scripts/zigux/check-phase3-{entry.slug}.py"
        shared = f"python3 scripts/zigux/run-phase3-checks.py --slug {entry.slug}"
        doc = entry.doc_path.read_text(encoding="utf-8")
        updated = doc.replace(legacy, shared)
        if updated == doc:
            continue
        entry.doc_path.write_text(updated, encoding="utf-8", newline="\n")
        rewritten.append(_rel(entry.doc_path, entry.root))
    return rewritten


def rewrite_non_doc_legacy_wrapper_references(
    entries: list[Phase3Slice],
    paths: Phase3Paths = DEFAULT_PATHS,
) -> list[str]:
    rewritten: list[str] = []
    doc_paths: list[Path] = []
    discovered_slugs = {entry.slug for entry in entries}
    docs_exclude = {entry.doc_path.resolve() for entry in entries}
    for path in sorted(paths.docs_dir.glob("*.md")):
        if path.resolve() in docs_exclude:
            continue
        doc_paths.append(path)

    for path in doc_paths:
        original = path.read_text(encoding="utf-8")
        updated = LEGACY_WRAPPER_REF_RE.sub(
            lambda match: (
                f"python3 scripts/zigux/run-phase3-checks.py --slug {match.group('slug')}"
                if match.group("slug") in discovered_slugs
                else match.group(0)
            ),
            original,
        )
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8", newline="\n")
        rewritten.append(_rel(path, paths.root))
    return rewritten


def discover_artifact_diff_phase3_order(
    entries: list[Phase3Slice],
    artifact_diff_path: Path = ARTIFACT_DIFF_PATH,
) -> list[Phase3Slice]:
    entry_map = {entry.slug: entry for entry in entries}
    ordered_entries: list[Phase3Slice] = []
    seen: set[str] = set()

    try:
        lines = artifact_diff_path.read_text(encoding="utf-8").splitlines()
        start = lines.index("Current Phase 3 use")
        end = lines.index("Rules")
    except (FileNotFoundError, ValueError):
        return entries

    for line in lines[start + 1 : end]:
        match = ARTIFACT_DIFF_PHASE3_SLUG_RE.search(line)
        if not match:
            continue
        slug = match.group("slug")
        if slug in seen or slug not in entry_map:
            continue
        ordered_entries.append(entry_map[slug])
        seen.add(slug)

    for entry in entries:
        if entry.slug in seen:
            continue
        ordered_entries.append(entry)
    return ordered_entries


def artifact_diff_phase3_lines(
    entries: list[Phase3Slice],
    artifact_diff_path: Path = ARTIFACT_DIFF_PATH,
) -> list[str]:
    lines: list[str] = []
    for entry in discover_artifact_diff_phase3_order(entries, artifact_diff_path):
        lines.append(
            f"- `{_rel(entry.expected_path, entry.root)}` anchors the bounded Phase 3 {entry.description} parity claim."
        )
        lines.append(
            f"- `python3 scripts/zigux/run-phase3-checks.py --slug {entry.slug}` compares that committed JSON fixture against both the bounded C harness and the Zig {entry.description} dump."
        )
    return lines


def rewrite_artifact_diff_phase3_section(
    entries: list[Phase3Slice],
    artifact_diff_path: Path = ARTIFACT_DIFF_PATH,
) -> bool:
    original = artifact_diff_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    try:
        start = lines.index("Current Phase 3 use")
        end = lines.index("Rules")
    except ValueError as exc:
        raise ValueError(f"artifact diff headings missing in {artifact_diff_path}") from exc
    replacement = ["Current Phase 3 use", *artifact_diff_phase3_lines(entries), "", "Rules"]
    updated_lines = [*lines[:start], *replacement, *lines[end + 1 :]]
    updated = "\n".join(updated_lines) + "\n"
    if updated == original:
        return False
    artifact_diff_path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def _discover_legacy_wrapper_references_in_file(
    path: Path,
    root: Path,
    discovered_slugs: set[str],
    scope: str,
) -> list[LegacyWrapperReference]:
    references: list[LegacyWrapperReference] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, OSError):
        return references

    for line_number, line in enumerate(lines, start=1):
        for match in LEGACY_WRAPPER_REF_RE.finditer(line):
            slug = match.group("slug")
            if slug not in discovered_slugs:
                continue
            kind = "command" if match.group("command") else "path"
            references.append(
                LegacyWrapperReference(
                    root=root,
                    path=path,
                    line_number=line_number,
                    slug=slug,
                    line=line.strip(),
                    kind=kind,
                    scope=scope,
                )
            )
    return references


def discover_non_doc_legacy_wrapper_references(
    entries: list[Phase3Slice],
    paths: Phase3Paths = DEFAULT_PATHS,
) -> list[LegacyWrapperReference]:
    discovered_slugs = {entry.slug for entry in entries}
    references: list[LegacyWrapperReference] = []

    docs_exclude = {entry.doc_path.resolve() for entry in entries}
    for path in sorted(paths.docs_dir.glob("*.md")):
        if path.resolve() in docs_exclude:
            continue
        references.extend(
            _discover_legacy_wrapper_references_in_file(path, paths.root, discovered_slugs, "documentation")
        )

    manifest_paths = sorted(paths.fixtures_dir.glob(f"{FIXTURE_PREFIX}*{MANIFEST_SUFFIX}"))
    for path in manifest_paths:
        references.extend(
            _discover_legacy_wrapper_references_in_file(path, paths.root, discovered_slugs, "manifest")
        )

    return references


def discover_phase3_slices(paths: Phase3Paths = DEFAULT_PATHS) -> list[Phase3Slice]:
    slices: list[Phase3Slice] = []
    for slug in _collect_slugs(paths):
        fixture_key = f"{FIXTURE_PREFIX}{slug.replace('-', '_')}"
        fixture_dir = paths.fixtures_dir / fixture_key
        manifest_candidates = (
            paths.fixtures_dir / f"{fixture_key}_manifest.json",
            fixture_dir / f"{fixture_key}_manifest.json",
        )
        doc_path = paths.docs_dir / f"{DOC_PREFIX}{slug}{DOC_SUFFIX}"
        interop_gate, interop_gate_mode = discover_doc_interop_gate(doc_path, slug)
        slices.append(
            Phase3Slice(
                root=paths.root,
                slug=slug,
                description=description_for_slug(slug),
                build_step=build_step_for_slug(slug),
                doc_path=doc_path,
                check_script=paths.scripts_dir / f"{SCRIPT_PREFIX}{slug}{SCRIPT_SUFFIX}",
                dump_path=paths.tests_dir / f"{fixture_key}{DUMP_SUFFIX}",
                fixture_dir=fixture_dir,
                expected_path=fixture_dir / "expected.json",
                harness_path=fixture_dir / f"{fixture_key}_c_harness.c",
                manifest_candidates=manifest_candidates,
                manifest_path=_pick_manifest(slug, manifest_candidates),
                interop_gate=interop_gate,
                interop_gate_mode=interop_gate_mode,
            )
        )
    return slices


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        paths = Phase3Paths(
            root=root,
            docs_dir=root / "Documentation" / "zigux",
            scripts_dir=root / "scripts" / "zigux",
            tests_dir=root / "zigux" / "tests",
            fixtures_dir=root / "zigux" / "tests" / "fixtures",
        )
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, paths.fixtures_dir):
            path.mkdir(parents=True, exist_ok=True)

        (paths.docs_dir / "phase3-alpha-slice.md").write_text("alpha\n", encoding="utf-8")
        (paths.scripts_dir / "check-phase3-beta.py").write_text("# beta\n", encoding="utf-8")
        (paths.tests_dir / "phase3_gamma_dump.zig").write_text("// gamma\n", encoding="utf-8")
        (paths.fixtures_dir / "phase3_delta_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "open", "slice": "delta-root", "files": [], "file_count": 0}),
            encoding="utf-8",
        )

        alpha_fixture = paths.fixtures_dir / "phase3_alpha"
        alpha_fixture.mkdir()
        (alpha_fixture / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-fixture",
                    "files": ["zigux/tests/fixtures/phase3_alpha/expected.json"],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
        )
        (paths.fixtures_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "", "slice": "", "files": []}),
            encoding="utf-8",
        )

        abi_fixture = paths.fixtures_dir / "phase3_abi"
        abi_fixture.mkdir()
        (paths.fixtures_dir / "phase3_abi_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "open", "slice": "abi-root", "files": [], "file_count": 0}),
            encoding="utf-8",
        )
        (abi_fixture / "phase3_abi_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-substrate-skeleton",
                    "files": ["zigux/tests/fixtures/phase3_abi/expected.json"],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
        )

        entries = discover_phase3_slices(paths)
        slugs = [entry.slug for entry in entries]
        assert slugs == ["abi", "alpha", "delta", "gamma"], slugs
        assert [_rel(path, paths.root) for path in discover_phase3_wrapper_scripts(paths)] == [
            "scripts/zigux/check-phase3-beta.py"
        ]

        entry_map = {entry.slug: entry for entry in entries}
        assert _rel(entry_map["alpha"].manifest_path, paths.root) == "zigux/tests/fixtures/phase3_alpha/phase3_alpha_manifest.json"
        assert _rel(entry_map["abi"].manifest_path, paths.root) == "zigux/tests/fixtures/phase3_abi/phase3_abi_manifest.json"
        assert entry_map["abi"].build_step == "phase3-dump"
        assert entry_map["abi"].description == "ABI layout"
        assert entry_map["alpha"].interop_gate is None
        assert entry_map["alpha"].interop_gate_mode == "missing"
        assert entry_map["gamma"].build_step == "phase3-gamma-dump"
        assert entry_map["gamma"].description == "gamma"
        assert entry_map["gamma"].interop_gate is None
        assert entry_map["gamma"].interop_gate_mode == "missing_doc"
        assert _rel(entry_map["gamma"].dump_path, paths.root) == "zigux/tests/phase3_gamma_dump.zig"
        assert _rel(entry_map["delta"].manifest_path, paths.root) == "zigux/tests/fixtures/phase3_delta_manifest.json"

        alpha_dict = entry_map["alpha"].to_dict()
        assert alpha_dict["doc"] == "Documentation/zigux/phase3-alpha-slice.md"
        assert alpha_dict["build_step"] == "phase3-alpha-dump"
        assert alpha_dict["manifest"] == "zigux/tests/fixtures/phase3_alpha/phase3_alpha_manifest.json"
        assert alpha_dict["interop_gate"] is None
        assert alpha_dict["interop_gate_mode"] == "missing"

        legacy_doc = paths.docs_dir / "phase3-legacy-slice.md"
        legacy_doc.write_text(legacy_wrapper_gate_for_slug("legacy") + "\n", encoding="utf-8")
        shared_doc = paths.docs_dir / "phase3-shared-slice.md"
        shared_doc.write_text(shared_runner_gate_for_slug("shared") + "\n", encoding="utf-8")
        custom_doc = paths.docs_dir / "phase3-custom-slice.md"
        custom_doc.write_text(f"{INTEROP_GATE_PREFIX}python3 scripts/zigux/custom-phase3-custom.py\n", encoding="utf-8")

        entries = discover_phase3_slices(paths)
        entry_map = {entry.slug: entry for entry in entries}
        assert entry_map["legacy"].interop_gate_mode == "legacy-wrapper"
        assert entry_map["legacy"].interop_gate == legacy_wrapper_gate_for_slug("legacy")
        assert entry_map["shared"].interop_gate_mode == "shared-runner"
        assert entry_map["shared"].interop_gate == shared_runner_gate_for_slug("shared")
        assert entry_map["custom"].interop_gate_mode == "custom"
        assert entry_map["custom"].interop_gate == f"{INTEROP_GATE_PREFIX}python3 scripts/zigux/custom-phase3-custom.py"
        assert _extract_interop_gate_marker(f"- `{legacy_wrapper_gate_for_slug('legacy')}`") == legacy_wrapper_gate_for_slug("legacy")
        assert _extract_interop_gate_marker("scope: none") is None

        (paths.docs_dir / "phase3-legacy-slice.md").write_text(
            "\n".join(
                [
                    "2. check legacy parity",
                    f"- `python3 scripts/zigux/check-phase3-legacy.py`",
                    f"- `{legacy_wrapper_gate_for_slug('legacy')}`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        rewritten = rewrite_legacy_wrapper_docs(discover_phase3_slices(paths))
        assert "Documentation/zigux/phase3-legacy-slice.md" in rewritten
        legacy_doc_text = (paths.docs_dir / "phase3-legacy-slice.md").read_text(encoding="utf-8")
        assert "python3 scripts/zigux/check-phase3-legacy.py" not in legacy_doc_text
        assert "python3 scripts/zigux/run-phase3-checks.py --slug legacy" in legacy_doc_text
        entries = discover_phase3_slices(paths)
        entry_map = {entry.slug: entry for entry in entries}
        assert entry_map["legacy"].interop_gate_mode == "shared-runner"
        assert rewrite_legacy_wrapper_docs(entries) == []

        (paths.docs_dir / "artifact-diff.md").write_text(
            "\n".join(
                [
                    "- `scripts/zigux/check-phase3-alpha.py` compares artifacts.",
                    "- `python3 scripts/zigux/check-phase3-gamma.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.fixtures_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-fixture",
                    "files": ["scripts/zigux/check-phase3-alpha.py"],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        references = discover_non_doc_legacy_wrapper_references(discover_phase3_slices(paths), paths)
        assert [reference.to_row() for reference in references] == [
            "Documentation/zigux/artifact-diff.md\t1\talpha\tpath\tdocumentation\tpython3 scripts/zigux/run-phase3-checks.py --slug alpha",
            "Documentation/zigux/artifact-diff.md\t2\tgamma\tcommand\tdocumentation\tpython3 scripts/zigux/run-phase3-checks.py --slug gamma",
            "zigux/tests/fixtures/phase3_alpha_manifest.json\t1\talpha\tpath\tmanifest\tpython3 scripts/zigux/run-phase3-checks.py --slug alpha",
        ]
        rewritten = rewrite_non_doc_legacy_wrapper_references(discover_phase3_slices(paths), paths)
        assert rewritten == ["Documentation/zigux/artifact-diff.md"]
        artifact_diff = (paths.docs_dir / "artifact-diff.md").read_text(encoding="utf-8")
        assert "scripts/zigux/check-phase3-alpha.py" not in artifact_diff
        assert "python3 scripts/zigux/check-phase3-gamma.py" not in artifact_diff
        assert "python3 scripts/zigux/run-phase3-checks.py --slug alpha" in artifact_diff
        assert "python3 scripts/zigux/run-phase3-checks.py --slug gamma" in artifact_diff
        assert "python3 python3 scripts/zigux/run-phase3-checks.py" not in artifact_diff
        references = discover_non_doc_legacy_wrapper_references(discover_phase3_slices(paths), paths)
        assert [reference.to_row() for reference in references] == [
            "zigux/tests/fixtures/phase3_alpha_manifest.json\t1\talpha\tpath\tmanifest\tpython3 scripts/zigux/run-phase3-checks.py --slug alpha",
        ]
        assert rewrite_non_doc_legacy_wrapper_references(discover_phase3_slices(paths), paths) == []

        artifact_diff_path = paths.docs_dir / "artifact-diff.md"
        artifact_diff_path.write_text(
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 3 use",
                    "- stale line",
                    "",
                    "Rules",
                    "- keep fixtures reviewable",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        entries = discover_phase3_slices(paths)
        expected_block = [
            "Current Phase 3 use",
            "- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug abi` compares that committed JSON fixture against both the bounded C harness and the Zig ABI layout dump.",
        ]
        generated = artifact_diff_phase3_lines(entries)
        assert generated[:2] == expected_block[1:]
        artifact_diff_path.write_text(
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 3 use",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug delta`",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug abi`",
                    "",
                    "Rules",
                    "- keep fixtures reviewable",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        ordered_entries = discover_artifact_diff_phase3_order(entries, artifact_diff_path)
        assert [entry.slug for entry in ordered_entries[:3]] == ["delta", "abi", "alpha"]
        assert rewrite_artifact_diff_phase3_section(entries, artifact_diff_path) is True
        rewritten_artifact_diff = artifact_diff_path.read_text(encoding="utf-8")
        assert "stale line" not in rewritten_artifact_diff
        assert "- `zigux/tests/fixtures/phase3_delta/expected.json` anchors the bounded Phase 3 delta parity claim." in rewritten_artifact_diff
        assert "- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim." in rewritten_artifact_diff
        assert "Rules\n- keep fixtures reviewable\n" in rewritten_artifact_diff
        assert rewrite_artifact_diff_phase3_section(entries, artifact_diff_path) is False

    print("PHASE3_CATALOG_SELF_TEST=pass")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover Zigux Phase 3 slices and their generated companion paths.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated discovery and manifest-selection checks.")
    parser.add_argument(
        "--legacy-wrapper-docs",
        action="store_true",
        help="List discovered Phase 3 slices whose docs still point at legacy per-slice wrapper commands.",
    )
    parser.add_argument(
        "--rewrite-shared-runner-docs",
        action="store_true",
        help="Rewrite discovered legacy Phase 3 doc commands to the shared run-phase3-checks.py --slug form.",
    )
    parser.add_argument(
        "--legacy-wrapper-references",
        action="store_true",
        help="List remaining discovered Phase 3 wrapper mentions outside the slice docs.",
    )
    parser.add_argument(
        "--rewrite-shared-runner-reference-docs",
        action="store_true",
        help="Rewrite non-slice documentation wrapper mentions to the shared run-phase3-checks.py --slug form.",
    )
    parser.add_argument(
        "--rewrite-artifact-diff-phase3-section",
        action="store_true",
        help="Rewrite the artifact-diff Phase 3 section from the discovered slice catalog.",
    )
    parser.add_argument(
        "--rewrite-legacy-wrapper-references",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(run_self_test())

    entries = discover_phase3_slices()
    if args.legacy_wrapper_docs:
        try:
            for entry in entries:
                if entry.interop_gate_mode == "legacy-wrapper":
                    print(f"{entry.slug}\t{_rel(entry.doc_path, entry.root)}\t{entry.interop_gate}")
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(0)
    if args.rewrite_shared_runner_docs:
        rewritten = rewrite_legacy_wrapper_docs(entries)
        for path in rewritten:
            print(path)
        raise SystemExit(0)
    if args.legacy_wrapper_references:
        try:
            for reference in discover_non_doc_legacy_wrapper_references(entries):
                print(reference.to_row())
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(0)
    if args.rewrite_shared_runner_reference_docs or args.rewrite_legacy_wrapper_references:
        rewritten = rewrite_non_doc_legacy_wrapper_references(entries)
        for path in rewritten:
            print(path)
        raise SystemExit(0)
    if args.rewrite_artifact_diff_phase3_section:
        if rewrite_artifact_diff_phase3_section(entries):
            print(_rel(ARTIFACT_DIFF_PATH))
        raise SystemExit(0)

    print(json.dumps([entry.to_dict() for entry in entries], indent=2, sort_keys=True))
