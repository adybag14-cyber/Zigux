#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
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

PHASE3_CATALOG_SELF_TEST_MARKER = "PHASE3_CATALOG_SELF_TEST=pass"
PHASE3_CATALOG_SELF_TEST_CASE_COUNT = 6

MAX_SLUG_TOKENS = 12
MAX_SLUG_CHARS = 96
MAX_REPEATED_TOKEN_COUNT = 3
MAX_REPEATED_BIGRAM_COUNT = 2


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


@dataclass(frozen=True)
class Phase3AuditIssue:
    code: str
    detail: str

    def to_row(self) -> str:
        return f"{self.code}\t{self.detail}"


@dataclass(frozen=True)
class Phase3SlugRenameCandidate:
    slug: str
    canonical_slug: str
    issue_codes: tuple[str, ...]

    def to_row(self) -> str:
        return "\t".join((self.slug, self.canonical_slug, ",".join(self.issue_codes)))


@dataclass(frozen=True)
class Phase3SlugRenameImpact:
    root: Path
    slug: str
    canonical_slug: str
    issue_codes: tuple[str, ...]
    paths: tuple[Path, ...]

    def to_row(self) -> str:
        return "\t".join(
            (
                self.slug,
                self.canonical_slug,
                ",".join(self.issue_codes),
                str(len(self.paths)),
                ",".join(_rel(path, self.root) for path in self.paths),
            )
        )


@dataclass(frozen=True)
class Phase3SlugMergePrepReference:
    root: Path
    path: Path
    line_number: int
    scope: str
    kinds: tuple[str, ...]

    def to_row(self) -> str:
        return "\t".join(
            (
                _rel(self.path, self.root),
                str(self.line_number),
                self.scope,
                ",".join(self.kinds),
            )
        )


@dataclass(frozen=True)
class Phase3SlugMergePrep:
    root: Path
    slug: str
    canonical_slug: str
    issue_codes: tuple[str, ...]
    retire_paths: tuple[Path, ...]
    references: tuple[Phase3SlugMergePrepReference, ...]

    def to_row(self) -> str:
        return "\t".join(
            (
                self.slug,
                self.canonical_slug,
                ",".join(self.issue_codes),
                str(len(self.retire_paths)),
                ",".join(_rel(path, self.root) for path in self.retire_paths),
                str(len(self.references)),
                ",".join(reference.to_row().replace("\t", ":") for reference in self.references),
            )
        )


@dataclass(frozen=True)
class Phase3SlugMergePrepSummary:
    slug: str
    canonical_slug: str
    issue_codes: tuple[str, ...]
    retire_path_count: int
    reference_count: int
    reference_scope_counts: tuple[tuple[str, int], ...]
    reference_kind_counts: tuple[tuple[str, int], ...]
    merge_cost: int

    def to_dict(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "canonical_slug": self.canonical_slug,
            "issue_codes": list(self.issue_codes),
            "retire_path_count": self.retire_path_count,
            "reference_count": self.reference_count,
            "reference_scope_counts": dict(self.reference_scope_counts),
            "reference_kind_counts": dict(self.reference_kind_counts),
            "merge_cost": self.merge_cost,
        }


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


def _load_expected_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _normalize_slug_text(value: str, slugs: Iterable[str]) -> str:
    normalized = value
    for slug in sorted({slug for slug in slugs if slug}, key=len, reverse=True):
        normalized = normalized.replace(slug, "<slug>")
        normalized = normalized.replace(slug.replace("-", "_"), "<slug_>")
    return normalized


def _normalized_json_shape(value: object, slugs: Iterable[str]) -> object:
    if isinstance(value, dict):
        return {
            _normalize_slug_text(str(key), slugs): _normalized_json_shape(child, slugs)
            for key, child in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, list):
        return [_normalized_json_shape(child, slugs) for child in value]
    if isinstance(value, str):
        return "str"
    if value is None:
        return "null"
    return type(value).__name__


def _slice_expected_schema(entry: Phase3Slice, related_slugs: Iterable[str]) -> object | None:
    payload = _load_expected_json(entry.expected_path)
    if payload is None:
        return None
    return _normalized_json_shape(payload, related_slugs)


def _slice_manifest_shape(entry: Phase3Slice, related_slugs: Iterable[str]) -> object | None:
    if entry.manifest_path is None:
        return None
    payload = _load_manifest(entry.manifest_path)
    if payload is None:
        return None
    return _normalized_json_shape(payload, related_slugs)


def _slice_rename_evidence_matches(entry: Phase3Slice, canonical_entry: Phase3Slice) -> bool:
    related_slugs = (entry.slug, canonical_entry.slug)
    evidence_pairs = (
        (
            _slice_expected_schema(entry, related_slugs),
            _slice_expected_schema(canonical_entry, related_slugs),
        ),
        (
            _slice_manifest_shape(entry, related_slugs),
            _slice_manifest_shape(canonical_entry, related_slugs),
        ),
    )
    comparisons = [left == right for left, right in evidence_pairs if left is not None and right is not None]
    return bool(comparisons) and all(comparisons)


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


def artifact_diff_phase3_section_needs_rewrite(
    entries: list[Phase3Slice],
    artifact_diff_path: Path = ARTIFACT_DIFF_PATH,
) -> bool:
    try:
        original = artifact_diff_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return True
    lines = original.splitlines()
    try:
        start = lines.index("Current Phase 3 use")
        end = lines.index("Rules")
    except ValueError:
        return True
    replacement = ["Current Phase 3 use", *artifact_diff_phase3_lines(entries, artifact_diff_path), "", "Rules"]
    updated_lines = [*lines[:start], *replacement, *lines[end + 1 :]]
    updated = "\n".join(updated_lines) + "\n"
    return updated != original


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

    return references


def _repeated_ngrams(tokens: list[str], size: int) -> list[tuple[str, int]]:
    if len(tokens) < size:
        return []
    counts = Counter("-".join(tokens[index : index + size]) for index in range(len(tokens) - size + 1))
    return sorted((ngram, count) for ngram, count in counts.items() if count > 1)


def audit_phase3_slug_sanity(entries: list[Phase3Slice]) -> list[Phase3AuditIssue]:
    issues: list[Phase3AuditIssue] = []
    for entry in entries:
        tokens = [token for token in entry.slug.split("-") if token]
        if len(tokens) > MAX_SLUG_TOKENS:
            issues.append(Phase3AuditIssue("slug-too-many-tokens", f"{entry.slug}\t{len(tokens)}"))
        if len(entry.slug) > MAX_SLUG_CHARS:
            issues.append(Phase3AuditIssue("slug-too-long", f"{entry.slug}\t{len(entry.slug)}"))

        repeated_tokens = sorted(
            f"{token}:{count}" for token, count in Counter(tokens).items() if count > MAX_REPEATED_TOKEN_COUNT
        )
        if repeated_tokens:
            issues.append(Phase3AuditIssue("slug-repeated-token", f"{entry.slug}\t{','.join(repeated_tokens)}"))

        repeated_bigrams = [
            f"{ngram}:{count}" for ngram, count in _repeated_ngrams(tokens, 2) if count > MAX_REPEATED_BIGRAM_COUNT
        ]
        if repeated_bigrams:
            issues.append(Phase3AuditIssue("slug-repeated-phrase", f"{entry.slug}\t{','.join(repeated_bigrams)}"))
    return issues


def discover_phase3_slug_rename_candidates(entries: list[Phase3Slice]) -> list[Phase3SlugRenameCandidate]:
    issues_by_slug: dict[str, set[str]] = {}
    for issue in audit_phase3_slug_sanity(entries):
        slug, _, _detail = issue.detail.partition("\t")
        issues_by_slug.setdefault(slug, set()).add(issue.code)

    if not issues_by_slug:
        return []

    entry_by_slug = {entry.slug: entry for entry in entries}
    clean_slugs = {
        entry.slug
        for entry in entries
        if entry.slug not in issues_by_slug
    }
    rename_candidates: list[Phase3SlugRenameCandidate] = []

    for slug in sorted(issues_by_slug):
        issue_codes = issues_by_slug[slug]
        if issue_codes == {"slug-too-many-tokens"}:
            continue
        tokens = slug.split("-")
        canonical_slug: str | None = None
        for prefix_len in range(len(tokens) - 1, 0, -1):
            candidate = "-".join(tokens[:prefix_len])
            if candidate in clean_slugs and candidate in entry_by_slug:
                canonical_slug = candidate
                break
        if canonical_slug is None:
            continue
        if not _slice_rename_evidence_matches(entry_by_slug[slug], entry_by_slug[canonical_slug]):
            continue
        rename_candidates.append(
            Phase3SlugRenameCandidate(
                slug=slug,
                canonical_slug=canonical_slug,
                issue_codes=tuple(sorted(issue_codes)),
            )
        )
    return rename_candidates


def discover_phase3_slug_rename_impacts(entries: list[Phase3Slice]) -> list[Phase3SlugRenameImpact]:
    entry_by_slug = {entry.slug: entry for entry in entries}
    impacts: list[Phase3SlugRenameImpact] = []
    for candidate in discover_phase3_slug_rename_candidates(entries):
        entry = entry_by_slug[candidate.slug]
        paths: list[Path] = [entry.doc_path, entry.dump_path, entry.fixture_dir, entry.expected_path, entry.harness_path]
        if entry.manifest_path is not None:
            paths.append(entry.manifest_path)
        impacts.append(
            Phase3SlugRenameImpact(
                root=entry.root,
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                paths=tuple(paths),
            )
        )
    return impacts


def _candidate_slug_tokens(slug: str) -> set[str]:
    return {token for token in slug.replace("_", "-").split("-") if token}


def _classify_merge_prep_reference(path: Path, line: str, slug: str, build_step: str) -> tuple[str, ...] | None:
    kinds: list[str] = []
    stripped = line.strip()
    if f"--slug {slug}" in stripped:
        kinds.append("runner")
    if slug in stripped:
        kinds.append("slug")
    if build_step in stripped:
        kinds.append("build-step")
    if not kinds:
        return None
    scope = "documentation"
    if path.suffix == ".yml" or path.suffix == ".yaml":
        scope = "workflow"
    elif path.suffix == ".py":
        scope = "script"
    elif path.suffix == ".zig":
        scope = "build-step" if path.name == "build.zig" else "zig"
    return tuple(dict.fromkeys(kinds))


def discover_phase3_slug_merge_prep(
    entries: list[Phase3Slice],
    paths: Phase3Paths = DEFAULT_PATHS,
) -> list[Phase3SlugMergePrep]:
    impacts = discover_phase3_slug_rename_impacts(entries)
    if not impacts:
        return []
    impact_by_slug = {impact.slug: impact for impact in impacts}
    merge_preps: list[Phase3SlugMergePrep] = []
    for candidate in discover_phase3_slug_rename_candidates(entries):
        impact = impact_by_slug.get(candidate.slug)
        if impact is None:
            continue
        references: list[Phase3SlugMergePrepReference] = []
        build_step = build_step_for_slug(candidate.slug)
        for path in sorted(paths.root.rglob("*")):
            if not path.is_file():
                continue
            if any(path == retired_path for retired_path in impact.paths):
                continue
            if path.suffix not in {".md", ".py", ".yml", ".yaml", ".zig"}:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (FileNotFoundError, OSError, UnicodeDecodeError):
                continue
            for line_number, line in enumerate(lines, start=1):
                kinds = _classify_merge_prep_reference(path, line, candidate.slug, build_step)
                if kinds is None:
                    continue
                references.append(
                    Phase3SlugMergePrepReference(
                        root=paths.root,
                        path=path,
                        line_number=line_number,
                        scope=("build-step" if "build-step" in kinds and path.name == "build.zig" else ("workflow" if path.suffix in {".yml", ".yaml"} else ("script" if path.suffix == ".py" else "documentation"))),
                        kinds=kinds,
                    )
                )
        merge_preps.append(
            Phase3SlugMergePrep(
                root=paths.root,
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                retire_paths=impact.paths,
                references=tuple(references),
            )
        )
    return merge_preps


def summarize_phase3_slug_merge_prep(
    merge_preps: list[Phase3SlugMergePrep],
) -> list[Phase3SlugMergePrepSummary]:
    summaries: list[Phase3SlugMergePrepSummary] = []
    for candidate in merge_preps:
        scope_counts = Counter(reference.scope for reference in candidate.references)
        kind_counts = Counter(kind for reference in candidate.references for kind in reference.kinds)
        merge_cost = len(candidate.retire_paths) * 20 + len(candidate.references) * 43
        summaries.append(
            Phase3SlugMergePrepSummary(
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                retire_path_count=len(candidate.retire_paths),
                reference_count=len(candidate.references),
                reference_scope_counts=tuple(sorted(scope_counts.items())),
                reference_kind_counts=tuple(sorted(kind_counts.items())),
                merge_cost=merge_cost,
            )
        )
    return sorted(summaries, key=lambda summary: (summary.merge_cost, summary.slug))


def discover_phase3_slices(paths: Phase3Paths = DEFAULT_PATHS) -> list[Phase3Slice]:
    entries: list[Phase3Slice] = []
    for slug in _collect_slugs(paths):
        doc_path = paths.docs_dir / f"{DOC_PREFIX}{slug}{DOC_SUFFIX}"
        check_script = paths.scripts_dir / f"{SCRIPT_PREFIX}{slug}{SCRIPT_SUFFIX}"
        dump_path = paths.tests_dir / f"{FIXTURE_PREFIX}{slug.replace('-', '_')}{DUMP_SUFFIX}"
        fixture_dir = paths.fixtures_dir / f"{FIXTURE_PREFIX}{slug.replace('-', '_')}"
        expected_path = fixture_dir / "expected.json"
        harness_path = fixture_dir / f"{FIXTURE_PREFIX}{slug.replace('-', '_')}_c_harness.c"
        fixture_key = f"{FIXTURE_PREFIX}{slug.replace('-', '_')}"
        manifest_candidates = tuple(
            sorted(
                {
                    *fixture_dir.glob(f"{FIXTURE_PREFIX}*{MANIFEST_SUFFIX}"),
                    paths.fixtures_dir / f"{fixture_key}{MANIFEST_SUFFIX}",
                }
            )
        )
        manifest_path = _pick_manifest(slug, manifest_candidates)
        interop_gate, interop_gate_mode = discover_doc_interop_gate(doc_path, slug)
        entries.append(
            Phase3Slice(
                root=paths.root,
                slug=slug,
                description=description_for_slug(slug),
                build_step=build_step_for_slug(slug),
                doc_path=doc_path,
                check_script=check_script,
                dump_path=dump_path,
                fixture_dir=fixture_dir,
                expected_path=expected_path,
                harness_path=harness_path,
                manifest_candidates=manifest_candidates,
                manifest_path=manifest_path,
                interop_gate=interop_gate,
                interop_gate_mode=interop_gate_mode,
            )
        )
    return entries


def audit_phase3_doc_sync(entries: list[Phase3Slice]) -> list[Phase3AuditIssue]:
    issues: list[Phase3AuditIssue] = []
    for reference in discover_non_doc_legacy_wrapper_references(entries):
        issues.append(
            Phase3AuditIssue(
                "legacy-wrapper-reference",
                reference.to_row(),
            )
        )
    if artifact_diff_phase3_section_needs_rewrite(entries):
        issues.append(
            Phase3AuditIssue(
                "artifact-diff-phase3-stale",
                _rel(ARTIFACT_DIFF_PATH, entries[0].root if entries else ROOT),
            )
        )
    return issues


def _phase3_paths_for_root(root: Path) -> Phase3Paths:
    return Phase3Paths(
        root=root,
        docs_dir=root / "Documentation" / "zigux",
        scripts_dir=root / "scripts" / "zigux",
        tests_dir=root / "zigux" / "tests",
        fixtures_dir=root / "zigux" / "tests" / "fixtures",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        paths = _phase3_paths_for_root(root)
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, paths.fixtures_dir):
            path.mkdir(parents=True, exist_ok=True)

        abi_fixture_dir = paths.fixtures_dir / "phase3_abi"
        abi_fixture_dir.mkdir()
        (paths.docs_dir / "phase3-abi-slice.md").write_text(
            "\n".join(
                [
                    "# ABI",
                    "",
                    "- `PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-abi.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_abi_dump.zig").write_text("// abi\n", encoding="utf-8", newline="\n")
        (abi_fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (abi_fixture_dir / "phase3_abi_c_harness.c").write_text("int main(void) { return 0; }\n", encoding="utf-8", newline="\n")
        (abi_fixture_dir / "phase3_abi_alt_manifest.json").write_text(
            json.dumps({"phase": "Phase 2", "status": "draft", "slice": "alt", "files": []}),
            encoding="utf-8",
            newline="\n",
        )
        (abi_fixture_dir / "phase3_abi_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-substrate-skeleton",
                    "files": ["include/zigux/abi.h"],
                    "file_count": 1,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )

        bitmap_fixture_dir = paths.fixtures_dir / "phase3_bitmap_cpumask"
        bitmap_fixture_dir.mkdir()
        (paths.docs_dir / "phase3-bitmap-cpumask-slice.md").write_text(
            "\n".join(
                [
                    "# bitmap/cpumask",
                    "",
                    "- `PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-bitmap-cpumask.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_bitmap_cpumask_dump.zig").write_text("// bitmap\n", encoding="utf-8", newline="\n")
        (bitmap_fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (bitmap_fixture_dir / "phase3_bitmap_cpumask_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
            newline="\n",
        )
        (bitmap_fixture_dir / "phase3_bitmap_cpumask_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "bitmap", "files": []}),
            encoding="utf-8",
            newline="\n",
        )

        range_fixture_dir = paths.fixtures_dir / "phase3_ida_range_set"
        range_fixture_dir.mkdir()
        (paths.docs_dir / "phase3-ida-range-set-slice.md").write_text(
            "\n".join(
                [
                    "# ida range-set",
                    "",
                    "- `PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-range-set.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_ida_range_set_dump.zig").write_text("// range\n", encoding="utf-8", newline="\n")
        (range_fixture_dir / "expected.json").write_text("{}\n", encoding="utf-8", newline="\n")
        (range_fixture_dir / "phase3_ida_range_set_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
            newline="\n",
        )
        (range_fixture_dir / "phase3_ida_range_set_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "ida-range-set", "files": []}),
            encoding="utf-8",
            newline="\n",
        )
        (range_fixture_dir / "phase3_ida_range_set_secondary_manifest.json").write_text(
            json.dumps({"phase": "Phase 1", "status": "old", "slice": "secondary", "files": []}),
            encoding="utf-8",
            newline="\n",
        )

        entries = discover_phase3_slices(paths)
        assert [entry.slug for entry in entries] == ["abi", "bitmap-cpumask", "ida-range-set"]
        assert entries[0].check_script == paths.scripts_dir / "check-phase3-abi.py"
        assert entries[0].dump_path == paths.tests_dir / "phase3_abi_dump.zig"
        assert entries[0].fixture_dir == abi_fixture_dir
        assert entries[0].expected_path == abi_fixture_dir / "expected.json"
        assert entries[0].harness_path == abi_fixture_dir / "phase3_abi_c_harness.c"
        assert entries[0].manifest_path == abi_fixture_dir / "phase3_abi_manifest.json"
        assert entries[1].manifest_path == bitmap_fixture_dir / "phase3_bitmap_cpumask_manifest.json"
        assert entries[2].manifest_path == range_fixture_dir / "phase3_ida_range_set_manifest.json"
        assert [entry.interop_gate_mode for entry in entries] == [
            "legacy-wrapper",
            "legacy-wrapper",
            "legacy-wrapper",
        ]
        assert description_for_slug("bitmap-cpumask") == "bitmap/cpumask"
        assert build_step_for_slug("abi") == "phase3-dump"

        rewritten = rewrite_legacy_wrapper_docs(entries)
        assert rewritten == [
            "Documentation/zigux/phase3-abi-slice.md",
            "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
            "Documentation/zigux/phase3-ida-range-set-slice.md",
        ]
        updated_entries = discover_phase3_slices(paths)
        assert all(entry.interop_gate_mode == "shared-runner" for entry in updated_entries)
        assert all(entry.interop_gate == shared_runner_gate_for_slug(entry.slug) for entry in updated_entries)

        (paths.docs_dir / "phase3-index.md").write_text(
            "\n".join(
                [
                    "# Phase 3 index",
                    "",
                    "- `python3 scripts/zigux/check-phase3-abi.py`",
                    "- `scripts/zigux/check-phase3-bitmap-cpumask.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        references = discover_non_doc_legacy_wrapper_references(updated_entries, paths)
        assert [reference.to_row() for reference in references] == [
            "Documentation/zigux/phase3-index.md\t3\tabi\tcommand\tdocumentation\tpython3 scripts/zigux/run-phase3-checks.py --slug abi",
            "Documentation/zigux/phase3-index.md\t4\tbitmap-cpumask\tpath\tdocumentation\tpython3 scripts/zigux/run-phase3-checks.py --slug bitmap-cpumask",
        ]
        rewritten_refs = rewrite_non_doc_legacy_wrapper_references(updated_entries, paths)
        assert rewritten_refs == ["Documentation/zigux/phase3-index.md"]
        rewritten_doc_text = (paths.docs_dir / "phase3-index.md").read_text(encoding="utf-8")
        assert "check-phase3-abi.py" not in rewritten_doc_text
        assert "check-phase3-bitmap-cpumask.py" not in rewritten_doc_text
        assert "run-phase3-checks.py --slug abi" in rewritten_doc_text
        assert "run-phase3-checks.py --slug bitmap-cpumask" in rewritten_doc_text

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
        assert rewrite_artifact_diff_phase3_section(updated_entries, artifact_diff_path) is True
        assert artifact_diff_phase3_section_needs_rewrite(updated_entries, artifact_diff_path) is False
        assert discover_non_doc_legacy_wrapper_references(updated_entries, paths) == []

        overgrown_slug = "one-two-three-four-five-six-seven-eight-nine-ten-eleven-twelve-thirteen"
        (paths.docs_dir / f"phase3-{overgrown_slug}-slice.md").write_text("tokens\n", encoding="utf-8", newline="\n")
        slug_issues = [issue.to_row() for issue in audit_phase3_slug_sanity(discover_phase3_slices(paths))]
        assert f"slug-too-many-tokens\t{overgrown_slug}\t13" in slug_issues

    return 0


def _emit_rows(rows: Iterable[str]) -> None:
    for row in rows:
        print(row)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover and maintain the Phase 3 ABI/runtime slice catalog."
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Path to the Zigux repository root.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated catalog coverage and emit a pass marker.")
    parser.add_argument("--legacy-wrapper-docs", action="store_true", help="List slice docs that still use legacy per-slice wrappers.")
    parser.add_argument("--rewrite-shared-runner-docs", action="store_true", help="Rewrite slice docs to the shared runner form.")
    parser.add_argument("--legacy-wrapper-references", action="store_true", help="List non-slice docs that still mention legacy Phase 3 wrappers.")
    parser.add_argument(
        "--rewrite-legacy-wrapper-references",
        action="store_true",
        help="Rewrite non-slice docs to the shared Phase 3 runner form.",
    )
    parser.add_argument(
        "--rewrite-artifact-diff-phase3-section",
        action="store_true",
        help="Regenerate the Phase 3 section inside Documentation/zigux/artifact-diff.md.",
    )
    parser.add_argument("--audit-doc-sync", action="store_true", help="Report stale non-slice references or artifact-diff drift.")
    parser.add_argument("--check-slug-sanity", action="store_true", help="Report overgrown or repetitive Phase 3 slugs.")
    parser.add_argument("--suggest-slug-renames", action="store_true", help="Suggest safe slug rename candidates.")
    parser.add_argument("--suggest-slug-rename-paths", action="store_true", help="List file-family impact for safe slug rename candidates.")
    parser.add_argument("--suggest-slug-merge-prep", action="store_true", help="List merge-prep cleanup rows for safe slug rename candidates.")
    parser.add_argument(
        "--suggest-slug-merge-plans",
        action="store_true",
        help="Compatibility alias for --suggest-slug-merge-prep.",
    )
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test()
        if result == 0:
            print(PHASE3_CATALOG_SELF_TEST_MARKER)
            print(f"PHASE3_CATALOG_SELF_TEST_CASE_COUNT={PHASE3_CATALOG_SELF_TEST_CASE_COUNT}")
        return result

    paths = _phase3_paths_for_root(Path(args.repo_root).resolve())
    entries = discover_phase3_slices(paths)

    if args.legacy_wrapper_docs:
        _emit_rows(_rel(entry.doc_path, entry.root) for entry in entries if entry.interop_gate_mode == "legacy-wrapper")
        return 0

    if args.rewrite_shared_runner_docs:
        _emit_rows(rewrite_legacy_wrapper_docs(entries))
        return 0

    if args.legacy_wrapper_references:
        _emit_rows(reference.to_row() for reference in discover_non_doc_legacy_wrapper_references(entries, paths))
        return 0

    if args.rewrite_legacy_wrapper_references:
        _emit_rows(rewrite_non_doc_legacy_wrapper_references(entries, paths))
        return 0

    if args.rewrite_artifact_diff_phase3_section:
        artifact_diff_path = paths.docs_dir / "artifact-diff.md"
        if rewrite_artifact_diff_phase3_section(entries, artifact_diff_path):
            print(_rel(artifact_diff_path, paths.root))
        return 0

    if args.audit_doc_sync:
        issues = audit_phase3_doc_sync(entries)
        if issues:
            print("PHASE3_DOC_SYNC=fail")
            _emit_rows(issue.to_row() for issue in issues)
            return 1
        print("PHASE3_DOC_SYNC=pass")
        return 0

    if args.check_slug_sanity:
        issues = audit_phase3_slug_sanity(entries)
        if issues:
            print("PHASE3_SLUG_SANITY=fail")
            _emit_rows(issue.to_row() for issue in issues)
            return 1
        print("PHASE3_SLUG_SANITY=pass")
        return 0

    if args.suggest_slug_renames:
        _emit_rows(candidate.to_row() for candidate in discover_phase3_slug_rename_candidates(entries))
        return 0

    if args.suggest_slug_rename_paths:
        _emit_rows(impact.to_row() for impact in discover_phase3_slug_rename_impacts(entries))
        return 0

    if args.suggest_slug_merge_prep or args.suggest_slug_merge_plans:
        _emit_rows(prep.to_row() for prep in discover_phase3_slug_merge_prep(entries, paths))
        return 0

    print(json.dumps([entry.to_dict() for entry in entries], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
