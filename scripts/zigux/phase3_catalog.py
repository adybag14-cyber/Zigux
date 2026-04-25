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
        # A long token chain alone is too weak a signal because legitimate
        # follow-on slices can cross the token threshold before the name
        # actually starts looping. Only suggest a rename once repetition or
        # outright overlength shows up alongside the prefix match.
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
        paths = [
            entry.doc_path,
            entry.dump_path,
            entry.fixture_dir,
            entry.expected_path,
            entry.harness_path,
        ]
        if entry.manifest_path is not None:
            paths.append(entry.manifest_path)
        unique_paths = tuple(sorted(dict.fromkeys(path.resolve() for path in paths)))
        impacts.append(
            Phase3SlugRenameImpact(
                root=entry.root,
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                paths=unique_paths,
            )
        )
    return impacts


def _candidate_slug_tokens(slug: str) -> set[str]:
    return {token for token in slug.replace("_", "-").split("-") if token}


def _classify_merge_prep_reference(path: Path, line: str, slug: str, build_step: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    kinds: list[str] = []
    if f"--slug {slug}" in stripped:
        kinds.append("runner")
    if slug in stripped:
        kinds.append("slug")
    if build_step in stripped:
        kinds.append("build-step")
    if not kinds:
        return None
    return tuple(kinds)


def _discover_merge_prep_references(
    paths: Phase3Paths,
    candidate: Phase3SlugRenameCandidate,
    retire_paths: set[Path],
) -> tuple[Phase3SlugMergePrepReference, ...]:
    slug = candidate.slug
    build_step = build_step_for_slug(slug)
    references: list[Phase3SlugMergePrepReference] = []
    search_roots = [paths.docs_dir, paths.scripts_dir, paths.tests_dir]
    allowed_suffixes = {".md", ".py", ".zig", ".yml", ".yaml", ".json"}

    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in retire_paths:
                continue
            if path.suffix not in allowed_suffixes:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for line_number, line in enumerate(lines, start=1):
                kinds = _classify_merge_prep_reference(path, line, slug, build_step)
                if kinds is None:
                    continue
                scope = "documentation"
                path_text = _rel(path, paths.root)
                if path_text.endswith((".yml", ".yaml")):
                    scope = "workflow"
                elif path_text.endswith("build.zig"):
                    scope = "build-step"
                elif path_text.endswith(".py"):
                    scope = "script"
                references.append(
                    Phase3SlugMergePrepReference(
                        root=paths.root,
                        path=resolved,
                        line_number=line_number,
                        scope=scope,
                        kinds=kinds,
                    )
                )
    return tuple(references)


def discover_phase3_slug_merge_prep(
    entries: list[Phase3Slice],
    paths: Phase3Paths = DEFAULT_PATHS,
) -> list[Phase3SlugMergePrep]:
    impacts = discover_phase3_slug_rename_impacts(entries)
    if not impacts:
        return []

    impact_by_slug = {impact.slug: impact for impact in impacts}
    merge_prep: list[Phase3SlugMergePrep] = []
    for candidate in discover_phase3_slug_rename_candidates(entries):
        impact = impact_by_slug.get(candidate.slug)
        if impact is None:
            continue
        retire_paths = set(impact.paths)
        references = _discover_merge_prep_references(paths, candidate, retire_paths)
        merge_prep.append(
            Phase3SlugMergePrep(
                root=paths.root,
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                retire_paths=impact.paths,
                references=references,
            )
        )
    return merge_prep


def summarize_phase3_slug_merge_prep(
    candidates: Iterable[Phase3SlugMergePrep],
) -> list[Phase3SlugMergePrepSummary]:
    summaries: list[Phase3SlugMergePrepSummary] = []
    for candidate in candidates:
        scope_counts = Counter(reference.scope for reference in candidate.references)
        kind_counts = Counter(
            kind for reference in candidate.references for kind in reference.kinds
        )
        merge_cost = len(candidate.retire_paths) * 34 + len(candidate.references)
        summaries.append(
            Phase3SlugMergePrepSummary(
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                retire_path_count=len(candidate.retire_paths),
                reference_count=len(candidate.references),
                reference_scope_counts=tuple(sorted(scope_counts.items())),
                reference_kind_counts=tuple(sorted(kind_counts.items(), key=lambda item: (item[1], item[0]))),
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
        manifest_candidates = tuple(sorted(fixture_dir.glob(f"{FIXTURE_PREFIX}*{MANIFEST_SUFFIX}")))
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
                _rel(ARTIFACT_DIFF_PATH),
            )
        )
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        paths = Phase3Paths(
            root=root,
            docs_dir=root / "Documentation" / "zigux",
            scripts_dir=root / "scripts" / "zigux",
            tests_dir=root / "zigux" / "tests",
            fixtures_dir=root / "zigux" / "tests" / "fixtures",
        )
        paths.docs_dir.mkdir(parents=True)
        paths.scripts_dir.mkdir(parents=True)
        paths.tests_dir.mkdir(parents=True)
        paths.fixtures_dir.mkdir(parents=True)

        slices = [
            "abi",
            "bitmap-cpumask",
            "ida-range-set",
        ]
        for slug in slices:
            (paths.docs_dir / f"phase3-{slug}-slice.md").write_text(
                "\n".join(
                    [
                        f"# {slug}",
                        "",
                        f"- `{legacy_wrapper_gate_for_slug(slug)}`",
                        "",
                    ]
                ),
                encoding="utf-8",
                newline="\n",
            )
            fixture_dir = paths.fixtures_dir / f"phase3_{slug.replace('-', '_')}"
            fixture_dir.mkdir(parents=True)
            expected_path = fixture_dir / "expected.json"
            expected_path.write_text(
                json.dumps({"slug": slug}, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (fixture_dir / f"phase3_{slug.replace('-', '_')}_c_harness.c").write_text(
                "int main(void) { return 0; }\n",
                encoding="utf-8",
            )
            (paths.tests_dir / f"phase3_{slug.replace('-', '_')}_dump.zig").write_text(
                f"// dump for {slug}\n",
                encoding="utf-8",
            )
            (fixture_dir / f"phase3_{slug.replace('-', '_')}_manifest.json").write_text(
                json.dumps(
                    {
                        "phase": "Phase 3",
                        "status": "ready",
                        "slice": slug,
                        "files": [{"path": "expected.json"}],
                        "file_count": 1,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

        abi_fixture_dir = paths.fixtures_dir / "phase3_abi"
        (abi_fixture_dir / "phase3_abi_extra_manifest.json").write_text(
            json.dumps({"phase": "Phase 2", "status": "stale"}) + "\n",
            encoding="utf-8",
        )
        (abi_fixture_dir / "phase3_abi_primary_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-substrate-skeleton",
                    "files": [{"path": "expected.json"}, {"path": "abi.json"}],
                    "file_count": 2,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        entries = discover_phase3_slices(paths)
        assert [entry.slug for entry in entries] == ["abi", "bitmap-cpumask", "ida-range-set"]
        assert entries[0].description == "ABI layout"
        assert entries[0].build_step == "phase3-dump"
        assert entries[1].description == "bitmap/cpumask"
        assert entries[1].build_step == "phase3-bitmap-cpumask-dump"
        assert entries[0].manifest_path == abi_fixture_dir / "phase3_abi_primary_manifest.json"
        assert entries[1].manifest_path == (
            paths.fixtures_dir / "phase3_bitmap_cpumask" / "phase3_bitmap_cpumask_manifest.json"
        )
        assert entries[2].manifest_path == (
            paths.fixtures_dir / "phase3_ida_range_set" / "phase3_ida_range_set_manifest.json"
        )
        assert all(entry.interop_gate_mode == "legacy-wrapper" for entry in entries)
        assert discover_phase3_wrapper_scripts(paths) == []

        rewritten = rewrite_legacy_wrapper_docs(entries)
        assert rewritten == [
            "Documentation/zigux/phase3-abi-slice.md",
            "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
            "Documentation/zigux/phase3-ida-range-set-slice.md",
        ]
        updated_entries = discover_phase3_slices(paths)
        assert all(entry.interop_gate_mode == "shared-runner" for entry in updated_entries)
        assert all(entry.interop_gate == shared_runner_gate_for_slug(entry.slug) for entry in updated_entries)

        doc_index_path = paths.docs_dir / "phase3-index.md"
        doc_index_path.write_text(
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

        rewritten_docs = rewrite_non_doc_legacy_wrapper_references(updated_entries, paths)
        assert rewritten_docs == ["Documentation/zigux/phase3-index.md"]
        assert discover_non_doc_legacy_wrapper_references(updated_entries, paths) == []
        rewritten_doc_text = doc_index_path.read_text(encoding="utf-8")
        assert "check-phase3-abi.py" not in rewritten_doc_text
        assert "run-phase3-checks.py --slug abi" in rewritten_doc_text
        assert "run-phase3-checks.py --slug bitmap-cpumask" in rewritten_doc_text

        artifact_diff_path = paths.docs_dir / "artifact-diff.md"
        artifact_diff_path.write_text(
            "\n".join(
                [
                    "# Artifact diff",
                    "",
                    "Current Phase 3 use",
                    "- stale entry",
                    "",
                    "Rules",
                    "- keep helpers narrow and product-facing",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert artifact_diff_phase3_section_needs_rewrite(updated_entries, artifact_diff_path) is True
        assert rewrite_artifact_diff_phase3_section(updated_entries, artifact_diff_path) is True
        expected_artifact_lines = [
            "# Artifact diff",
            "",
            "Current Phase 3 use",
            "- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug abi` compares that committed JSON fixture against both the bounded C harness and the Zig ABI layout dump.",
            "- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json` anchors the bounded Phase 3 bitmap/cpumask parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug bitmap-cpumask` compares that committed JSON fixture against both the bounded C harness and the Zig bitmap/cpumask dump.",
            "- `zigux/tests/fixtures/phase3_ida_range_set/expected.json` anchors the bounded Phase 3 ida range-set parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug ida-range-set` compares that committed JSON fixture against both the bounded C harness and the Zig ida range-set dump.",
            "",
            "Rules",
            "- keep helpers narrow and product-facing",
            "",
        ]
        assert artifact_diff_path.read_text(encoding="utf-8").splitlines() == expected_artifact_lines
        assert artifact_diff_phase3_section_needs_rewrite(updated_entries, artifact_diff_path) is False
        assert rewrite_artifact_diff_phase3_section(updated_entries, artifact_diff_path) is False

        out_of_order_artifact_diff = paths.docs_dir / "artifact-diff-custom-order.md"
        out_of_order_artifact_diff.write_text(
            "\n".join(
                [
                    "# Artifact diff",
                    "",
                    "Current Phase 3 use",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug ida-range-set` compares the old entry.",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug abi` compares the old entry.",
                    "",
                    "Rules",
                    "- keep helpers narrow and product-facing",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert [entry.slug for entry in discover_artifact_diff_phase3_order(updated_entries, out_of_order_artifact_diff)] == [
            "ida-range-set",
            "abi",
            "bitmap-cpumask",
        ]
        ordered_lines = artifact_diff_phase3_lines(updated_entries, out_of_order_artifact_diff)
        assert ordered_lines[:2] == [
            "- `zigux/tests/fixtures/phase3_ida_range_set/expected.json` anchors the bounded Phase 3 ida range-set parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug ida-range-set` compares that committed JSON fixture against both the bounded C harness and the Zig ida range-set dump.",
        ]
        assert ordered_lines[2:4] == [
            "- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug abi` compares that committed JSON fixture against both the bounded C harness and the Zig ABI layout dump.",
        ]
        assert ordered_lines[4:6] == [
            "- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json` anchors the bounded Phase 3 bitmap/cpumask parity claim.",
            "- `python3 scripts/zigux/run-phase3-checks.py --slug bitmap-cpumask` compares that committed JSON fixture against both the bounded C harness and the Zig bitmap/cpumask dump.",
        ]
        assert rewrite_artifact_diff_phase3_section(updated_entries, out_of_order_artifact_diff) is True
        rewritten_custom = out_of_order_artifact_diff.read_text(encoding="utf-8").splitlines()
        assert rewritten_custom[3:9] == ordered_lines

        audit_issues = audit_phase3_doc_sync(updated_entries)
        assert audit_issues == []
        doc_index_path.write_text(
            "\n".join(
                [
                    "# Phase 3 index",
                    "",
                    "- `python3 scripts/zigux/check-phase3-abi.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        stale_artifact_diff_path = paths.docs_dir / "artifact-diff-stale.md"
        stale_artifact_diff_path.write_text(
            "\n".join(
                [
                    "# Artifact diff",
                    "",
                    "Current Phase 3 use",
                    "- stale entry",
                    "",
                    "Rules",
                    "- keep helpers narrow and product-facing",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        original_artifact_diff = ARTIFACT_DIFF_PATH
        try:
            globals()["ARTIFACT_DIFF_PATH"] = stale_artifact_diff_path
            stale_audit_issues = audit_phase3_doc_sync(updated_entries)
        finally:
            globals()["ARTIFACT_DIFF_PATH"] = original_artifact_diff
        assert [issue.to_row() for issue in stale_audit_issues] == [
            "legacy-wrapper-reference\tDocumentation/zigux/phase3-index.md\t3\tabi\tcommand\tdocumentation\tpython3 scripts/zigux/run-phase3-checks.py --slug abi",
            "artifact-diff-phase3-stale\tDocumentation/zigux/artifact-diff-stale.md",
        ]

        overgrown_slug = "one-two-three-four-five-six-seven-eight-nine-ten-eleven-twelve-thirteen"
        (paths.docs_dir / f"phase3-{overgrown_slug}-slice.md").write_text(
            "tokens\n",
            encoding="utf-8",
        )
        too_long_slug = "this-is-a-deliberately-overgrown-phase3-slug-with-many-extra-descriptor-tokens-for-audit-coverage-padding"
        (paths.docs_dir / f"phase3-{too_long_slug}-slice.md").write_text(
            "length\n",
            encoding="utf-8",
        )
        repetitive_slug = "loop-window-policy-budget-window-policy-budget-window-policy-budget-window-policy"
        (paths.docs_dir / f"phase3-{repetitive_slug}-slice.md").write_text(
            "loop\n",
            encoding="utf-8",
        )
        slug_issues = [issue.to_row() for issue in audit_phase3_slug_sanity(discover_phase3_slices(paths))]
        assert (
            f"slug-too-many-tokens\t{overgrown_slug}\t13"
            in slug_issues
        )
        assert any(row.startswith(f"slug-too-long\t{too_long_slug}\t") for row in slug_issues)
        assert (
            f"slug-repeated-token\t{repetitive_slug}\tpolicy:4,window:4"
            in slug_issues
        )
        assert (
            f"slug-repeated-phrase\t{repetitive_slug}\tbudget-window:3,policy-budget:3,window-policy:4"
            in slug_issues
        )

        canonical_slug = "alpha-beta-gamma-delta"
        (paths.docs_dir / f"phase3-{canonical_slug}-slice.md").write_text(
            "canonical\n",
            encoding="utf-8",
        )
        overgrown_with_prefix = f"{canonical_slug}-epsilon-zeta-eta-theta-iota-kappa-lambda-mu-nu"
        overgrown_with_prefix_fixture = paths.fixtures_dir / f"phase3_{overgrown_with_prefix.replace('-', '_')}"
        overgrown_with_prefix_fixture.mkdir()
        (paths.docs_dir / f"phase3-{overgrown_with_prefix}-slice.md").write_text(
            "prefix\n",
            encoding="utf-8",
        )
        (paths.tests_dir / f"phase3_{overgrown_with_prefix.replace('-', '_')}_dump.zig").write_text(
            "// prefix\n",
            encoding="utf-8",
        )
        (overgrown_with_prefix_fixture / "expected.json").write_text(
            "{}\n",
            encoding="utf-8",
        )
        (
            overgrown_with_prefix_fixture
            / f"phase3_{overgrown_with_prefix.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            overgrown_with_prefix_fixture
            / f"phase3_{overgrown_with_prefix.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "prefix", "files": [], "file_count": 0}),
            encoding="utf-8",
        )
        rename_candidates = discover_phase3_slug_rename_candidates(discover_phase3_slices(paths))
        assert all(candidate.slug != overgrown_with_prefix for candidate in rename_candidates)

        repetitive_canonical_slug = "loop-window-policy-budget"
        (paths.docs_dir / f"phase3-{repetitive_canonical_slug}-slice.md").write_text(
            "repetitive canonical\n",
            encoding="utf-8",
        )
        repetitive_canonical_fixture = paths.fixtures_dir / f"phase3_{repetitive_canonical_slug.replace('-', '_')}"
        repetitive_canonical_fixture.mkdir()
        (paths.tests_dir / f"phase3_{repetitive_canonical_slug.replace('-', '_')}_dump.zig").write_text(
            "// repetitive canonical\n",
            encoding="utf-8",
        )
        (repetitive_canonical_fixture / "expected.json").write_text(
            "{}\n",
            encoding="utf-8",
        )
        (
            repetitive_canonical_fixture
            / f"phase3_{repetitive_canonical_slug.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            repetitive_canonical_fixture
            / f"phase3_{repetitive_canonical_slug.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "repetitive canonical", "files": [], "file_count": 0}),
            encoding="utf-8",
        )
        repetitive_with_prefix = f"{repetitive_canonical_slug}-window-policy-budget-window-policy"
        repetitive_fixture = paths.fixtures_dir / f"phase3_{repetitive_with_prefix.replace('-', '_')}"
        repetitive_fixture.mkdir()
        (paths.docs_dir / f"phase3-{repetitive_with_prefix}-slice.md").write_text(
            "repetitive prefix\n",
            encoding="utf-8",
        )
        (paths.tests_dir / f"phase3_{repetitive_with_prefix.replace('-', '_')}_dump.zig").write_text(
            "// repetitive prefix\n",
            encoding="utf-8",
        )
        (repetitive_fixture / "expected.json").write_text(
            "{}\n",
            encoding="utf-8",
        )
        (
            repetitive_fixture
            / f"phase3_{repetitive_with_prefix.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            repetitive_fixture
            / f"phase3_{repetitive_with_prefix.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "repetitive", "files": [], "file_count": 0}),
            encoding="utf-8",
        )
        rename_candidates = discover_phase3_slug_rename_candidates(discover_phase3_slices(paths))
        assert all(candidate.slug != overgrown_with_prefix for candidate in rename_candidates)
        repetitive_candidate = next(candidate for candidate in rename_candidates if candidate.slug == repetitive_with_prefix)
        assert repetitive_candidate.canonical_slug == repetitive_canonical_slug
        assert "slug-repeated-phrase" in repetitive_candidate.issue_codes
        rename_impacts = discover_phase3_slug_rename_impacts(discover_phase3_slices(paths))
        assert all(impact.slug != overgrown_with_prefix for impact in rename_impacts)
        rename_impact = next(impact for impact in rename_impacts if impact.slug == repetitive_with_prefix)
        assert rename_impact.canonical_slug == repetitive_canonical_slug
        assert "slug-repeated-phrase" in rename_impact.issue_codes
        assert len(rename_impact.paths) == 6
        assert {_rel(path, paths.root) for path in rename_impact.paths} == {
            f"Documentation/zigux/phase3-{repetitive_with_prefix}-slice.md",
            f"zigux/tests/phase3_{repetitive_with_prefix.replace('-', '_')}_dump.zig",
            f"zigux/tests/fixtures/phase3_{repetitive_with_prefix.replace('-', '_')}",
            f"zigux/tests/fixtures/phase3_{repetitive_with_prefix.replace('-', '_')}/expected.json",
            (
                "zigux/tests/fixtures/"
                f"phase3_{repetitive_with_prefix.replace('-', '_')}/"
                f"phase3_{repetitive_with_prefix.replace('-', '_')}_c_harness.c"
            ),
            (
                "zigux/tests/fixtures/"
                f"phase3_{repetitive_with_prefix.replace('-', '_')}/"
                f"phase3_{repetitive_with_prefix.replace('-', '_')}_manifest.json"
            ),
        }
        (paths.docs_dir / "phase3-merge-notes.md").write_text(
            "\n".join(
                [
                    "# Merge notes",
                    "",
                    f"- `python3 scripts/zigux/run-phase3-checks.py --slug {repetitive_with_prefix}`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "build.zig").write_text(
            "\n".join(
                [
                    "const std = @import(\"std\");",
                    "",
                    "pub fn build(b: *std.Build) void {",
                    f"    _ = b.step(\"{build_step_for_slug(repetitive_with_prefix)}\", \"demo step\");",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        merge_prep = discover_phase3_slug_merge_prep(discover_phase3_slices(paths), paths)
        merge_entry = next(prep for prep in merge_prep if prep.slug == repetitive_with_prefix)
        assert merge_entry.canonical_slug == repetitive_canonical_slug
        assert tuple(_rel(path, paths.root) for path in merge_entry.retire_paths) == tuple(
            _rel(path, paths.root) for path in rename_impact.paths
        )
        assert [reference.to_row() for reference in merge_entry.references] == [
            "Documentation/zigux/phase3-merge-notes.md\t3\tdocumentation\trunner,slug",
            "zigux/tests/build.zig\t4\tbuild-step\tbuild-step,slug",
        ]
        merge_prep_summaries = summarize_phase3_slug_merge_prep(merge_prep)
        merge_summary = next(summary for summary in merge_prep_summaries if summary.slug == repetitive_with_prefix)
        assert merge_summary.canonical_slug == repetitive_canonical_slug
        assert merge_summary.retire_path_count == len(rename_impact.paths)
        assert merge_summary.reference_count == 2
        assert merge_summary.reference_scope_counts == (("build-step", 1), ("documentation", 1))
        assert merge_summary.reference_kind_counts == (("slug", 2), ("build-step", 1), ("runner", 1))
        assert merge_summary.merge_cost == 206
        assert merge_summary.to_dict() == {
            "slug": repetitive_with_prefix,
            "canonical_slug": repetitive_canonical_slug,
            "issue_codes": ["slug-repeated-phrase"],
            "retire_path_count": len(rename_impact.paths),
            "reference_count": 2,
            "reference_scope_counts": {"build-step": 1, "documentation": 1},
            "reference_kind_counts": {"slug": 2, "build-step": 1, "runner": 1},
            "merge_cost": 206,
        }

        mismatched_canonical_slug = "mismatch-window-policy-budget"
        (paths.docs_dir / f"phase3-{mismatched_canonical_slug}-slice.md").write_text(
            "mismatched canonical\n",
            encoding="utf-8",
        )
        mismatched_canonical_fixture = paths.fixtures_dir / f"phase3_{mismatched_canonical_slug.replace('-', '_')}"
        mismatched_canonical_fixture.mkdir()
        (paths.tests_dir / f"phase3_{mismatched_canonical_slug.replace('-', '_')}_dump.zig").write_text(
            "// mismatched canonical\n",
            encoding="utf-8",
        )
        (mismatched_canonical_fixture / "expected.json").write_text(
            json.dumps({"summary": {"acked": 1}}, sort_keys=True),
            encoding="utf-8",
        )
        (
            mismatched_canonical_fixture
            / f"phase3_{mismatched_canonical_slug.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            mismatched_canonical_fixture
            / f"phase3_{mismatched_canonical_slug.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "mismatched canonical", "files": [], "file_count": 0}),
            encoding="utf-8",
        )
        mismatched_with_prefix = f"{mismatched_canonical_slug}-window-policy-budget-window-policy"
        mismatched_fixture = paths.fixtures_dir / f"phase3_{mismatched_with_prefix.replace('-', '_')}"
        mismatched_fixture.mkdir()
        (paths.docs_dir / f"phase3-{mismatched_with_prefix}-slice.md").write_text(
            "mismatched prefix\n",
            encoding="utf-8",
        )
        (paths.tests_dir / f"phase3_{mismatched_with_prefix.replace('-', '_')}_dump.zig").write_text(
            "// mismatched prefix\n",
            encoding="utf-8",
        )
        (mismatched_fixture / "expected.json").write_text(
            json.dumps({"summary": {"acked": 1, "deferred": 0}}, sort_keys=True),
            encoding="utf-8",
        )
        (
            mismatched_fixture
            / f"phase3_{mismatched_with_prefix.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            mismatched_fixture
            / f"phase3_{mismatched_with_prefix.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "mismatched prefix", "files": [], "file_count": 0}),
            encoding="utf-8",
        )
        rename_candidates = discover_phase3_slug_rename_candidates(discover_phase3_slices(paths))
        assert all(candidate.slug != mismatched_with_prefix for candidate in rename_candidates)

        manifest_only_canonical_slug = "manifest-window-policy-budget"
        (paths.docs_dir / f"phase3-{manifest_only_canonical_slug}-slice.md").write_text(
            "manifest canonical\n",
            encoding="utf-8",
        )
        manifest_only_canonical_fixture = paths.fixtures_dir / f"phase3_{manifest_only_canonical_slug.replace('-', '_')}"
        manifest_only_canonical_fixture.mkdir()
        (paths.tests_dir / f"phase3_{manifest_only_canonical_slug.replace('-', '_')}_dump.zig").write_text(
            "// manifest canonical\n",
            encoding="utf-8",
        )
        (manifest_only_canonical_fixture / "expected.json").write_text(
            json.dumps({"summary": {"acked": 1}}, sort_keys=True),
            encoding="utf-8",
        )
        (
            manifest_only_canonical_fixture
            / f"phase3_{manifest_only_canonical_slug.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            manifest_only_canonical_fixture
            / f"phase3_{manifest_only_canonical_slug.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "manifest canonical", "files": [{"path": "expected.json"}], "file_count": 1}, sort_keys=True),
            encoding="utf-8",
        )
        manifest_only_with_prefix = f"{manifest_only_canonical_slug}-window-policy-budget-window-policy"
        manifest_only_fixture = paths.fixtures_dir / f"phase3_{manifest_only_with_prefix.replace('-', '_')}"
        manifest_only_fixture.mkdir()
        (paths.docs_dir / f"phase3-{manifest_only_with_prefix}-slice.md").write_text(
            "manifest prefix\n",
            encoding="utf-8",
        )
        (paths.tests_dir / f"phase3_{manifest_only_with_prefix.replace('-', '_')}_dump.zig").write_text(
            "// manifest prefix\n",
            encoding="utf-8",
        )
        (manifest_only_fixture / "expected.json").write_text(
            json.dumps({"summary": {"acked": 1}}, sort_keys=True),
            encoding="utf-8",
        )
        (
            manifest_only_fixture
            / f"phase3_{manifest_only_with_prefix.replace('-', '_')}_c_harness.c"
        ).write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (
            manifest_only_fixture
            / f"phase3_{manifest_only_with_prefix.replace('-', '_')}_manifest.json"
        ).write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "manifest prefix", "files": [{"path": "expected.json", "kind": "extra"}], "file_count": 1}, sort_keys=True),
            encoding="utf-8",
        )
        rename_candidates = discover_phase3_slug_rename_candidates(discover_phase3_slices(paths))
        assert all(candidate.slug != manifest_only_with_prefix for candidate in rename_candidates)

        parser = build_parser()
        assert parser.parse_args(["--rewrite-legacy-wrapper-references"]).rewrite_legacy_wrapper_references is True
        assert parser.parse_args(["--rewrite-shared-runner-reference-docs"]).rewrite_legacy_wrapper_references is True
        assert parser.parse_args(["--audit-doc-sync"]).audit_doc_sync is True
        assert parser.parse_args(["--audit-slug-sanity"]).audit_slug_sanity is True
        assert parser.parse_args(["--suggest-slug-renames"]).suggest_slug_renames is True
        assert parser.parse_args(["--suggest-slug-rename-paths"]).suggest_slug_rename_paths is True
        assert parser.parse_args(["--suggest-slug-merge-prep"]).suggest_slug_merge_prep is True
        assert parser.parse_args(["--suggest-slug-merge-plans"]).suggest_slug_merge_prep is True
        assert parser.parse_args(["--suggest-slug-merge-prep-summary"]).suggest_slug_merge_prep_summary is True
        assert parser.parse_args(["--suggest-slug-merge-plans-summary"]).suggest_slug_merge_prep_summary is True

    print("PHASE3_CATALOG_SELF_TEST=pass")
    return 0


def build_parser() -> argparse.ArgumentParser:
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
        help="List remaining discovered Phase 3 wrapper mentions in non-slice documentation.",
    )
    parser.add_argument(
        "--rewrite-legacy-wrapper-references",
        "--rewrite-shared-runner-reference-docs",
        dest="rewrite_legacy_wrapper_references",
        action="store_true",
        help="Rewrite non-slice documentation wrapper mentions to the shared run-phase3-checks.py --slug form.",
    )
    parser.add_argument(
        "--rewrite-artifact-diff-phase3-section",
        action="store_true",
        help="Rewrite the artifact-diff Phase 3 section from the discovered slice catalog.",
    )
    parser.add_argument(
        "--audit-doc-sync",
        action="store_true",
        help="Report stale non-slice wrapper references and artifact-diff Phase 3 drift, then exit non-zero when any are found.",
    )
    parser.add_argument(
        "--audit-slug-sanity",
        action="store_true",
        help="Report suspiciously repetitive or overgrown discovered Phase 3 slugs, then exit non-zero when any are found.",
    )
    parser.add_argument(
        "--suggest-slug-renames",
        action="store_true",
        help="List overgrown discovered Phase 3 slugs that have a shorter clean prefix already present in the catalog.",
    )
    parser.add_argument(
        "--suggest-slug-rename-paths",
        action="store_true",
        help="List the core slice files and directories that a suggested Phase 3 slug rename would touch.",
    )
    parser.add_argument(
        "--suggest-slug-merge-prep",
        "--suggest-slug-merge-plans",
        action="store_true",
        help="List the retireable slice artifacts plus the extra docs, workflow, script, or build-step references that still mention each safe long slug elsewhere in the tree.",
    )
    parser.add_argument(
        "--suggest-slug-merge-prep-summary",
        "--suggest-slug-merge-plans-summary",
        dest="suggest_slug_merge_prep_summary",
        action="store_true",
        help="Emit a safer-to-parse JSON summary of merge-prep candidates with retire counts, reference counts, scope/kind breakdowns, and a simplest-first merge_cost ranking.",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
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
    if args.rewrite_legacy_wrapper_references:
        rewritten = rewrite_non_doc_legacy_wrapper_references(entries)
        for path in rewritten:
            print(path)
        raise SystemExit(0)
    if args.rewrite_artifact_diff_phase3_section:
        if rewrite_artifact_diff_phase3_section(entries):
            print(_rel(ARTIFACT_DIFF_PATH))
        raise SystemExit(0)
    if args.audit_doc_sync:
        try:
            issues = audit_phase3_doc_sync(entries)
            for issue in issues:
                print(issue.to_row())
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(1 if issues else 0)
    if args.audit_slug_sanity:
        try:
            issues = audit_phase3_slug_sanity(entries)
            for issue in issues:
                print(issue.to_row())
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(1 if issues else 0)
    if args.suggest_slug_renames:
        try:
            candidates = discover_phase3_slug_rename_candidates(entries)
            for candidate in candidates:
                print(candidate.to_row())
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(0)
    if args.suggest_slug_rename_paths:
        try:
            impacts = discover_phase3_slug_rename_impacts(entries)
            for impact in impacts:
                print(impact.to_row())
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(0)
    if args.suggest_slug_merge_prep:
        try:
            merge_prep = discover_phase3_slug_merge_prep(entries)
            for prep in merge_prep:
                print(prep.to_row())
        except BrokenPipeError:
            sys.exit(0)
        raise SystemExit(0)
    if args.suggest_slug_merge_prep_summary:
        merge_prep = discover_phase3_slug_merge_prep(entries)
        summaries = summarize_phase3_slug_merge_prep(merge_prep)
        print(json.dumps([summary.to_dict() for summary in summaries], indent=2, sort_keys=True))
        raise SystemExit(0)

    print(json.dumps([entry.to_dict() for entry in entries], indent=2, sort_keys=True))