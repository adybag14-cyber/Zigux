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
        canonical_entry = entry_by_slug[canonical_slug]
        entry = entry_by_slug[slug]
        if not _slice_rename_evidence_matches(entry, canonical_entry):
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
        impact_paths: list[Path] = []
        for path in (
            entry.doc_path,
            entry.check_script,
            entry.dump_path,
            entry.fixture_dir,
            entry.expected_path,
            entry.harness_path,
            *entry.manifest_candidates,
        ):
            if path.exists() and path not in impact_paths:
                impact_paths.append(path)
        impacts.append(
            Phase3SlugRenameImpact(
                root=entry.root,
                slug=candidate.slug,
                canonical_slug=candidate.canonical_slug,
                issue_codes=candidate.issue_codes,
                paths=tuple(impact_paths),
            )
        )

    return impacts


def audit_phase3_doc_sync(
    entries: list[Phase3Slice],
    paths: Phase3Paths = DEFAULT_PATHS,
    artifact_diff_path: Path = ARTIFACT_DIFF_PATH,
) -> list[Phase3AuditIssue]:
    issues = [
        Phase3AuditIssue("legacy-wrapper-reference", reference.to_row())
        for reference in discover_non_doc_legacy_wrapper_references(entries, paths)
    ]
    if artifact_diff_phase3_section_needs_rewrite(entries, artifact_diff_path):
        issues.append(
            Phase3AuditIssue(
                "artifact-diff-phase3-stale",
                _rel(artifact_diff_path, paths.root),
            )
        )
    return issues


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
        paths.docs_dir.mkdir(parents=True)
        paths.scripts_dir.mkdir(parents=True)
        paths.fixtures_dir.mkdir(parents=True)

        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "alpha doc\n",
            encoding="utf-8",
        )
        (paths.tests_dir / "phase3_alpha_dump.zig").write_text(
            "// alpha\n",
            encoding="utf-8",
        )
        alpha_fixture = paths.fixtures_dir / "phase3_alpha"
        alpha_fixture.mkdir()
        (alpha_fixture / "expected.json").write_text(
            json.dumps({"kind": "alpha"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (alpha_fixture / "phase3_alpha_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (paths.fixtures_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-fixture",
                    "files": ["expected.json"],
                    "file_count": 1,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (alpha_fixture / "phase3_alpha_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "draft", "slice": "alpha-stale"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        (paths.docs_dir / "phase3-abi-slice.md").write_text(
            "abi doc\n",
            encoding="utf-8",
        )
        (paths.tests_dir / "phase3_abi_dump.zig").write_text(
            "// abi\n",
            encoding="utf-8",
        )
        abi_fixture = paths.fixtures_dir / "phase3_abi"
        abi_fixture.mkdir()
        (abi_fixture / "expected.json").write_text(
            json.dumps({"kind": "abi"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (abi_fixture / "phase3_abi_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (paths.fixtures_dir / "phase3_abi_manifest.json").write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "wrong", "files": []}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (abi_fixture / "phase3_abi_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-substrate-skeleton",
                    "files": ["expected.json"],
                    "file_count": 1,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        (paths.docs_dir / "phase3-gamma-slice.md").write_text(
            "gamma doc\n",
            encoding="utf-8",
        )
        (paths.tests_dir / "phase3_gamma_dump.zig").write_text(
            "// gamma\n",
            encoding="utf-8",
        )
        gamma_fixture = paths.fixtures_dir / "phase3_gamma"
        gamma_fixture.mkdir()
        (gamma_fixture / "expected.json").write_text(
            json.dumps({"kind": "gamma"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (gamma_fixture / "phase3_gamma_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )

        entries = discover_phase3_slices(paths)
        assert [entry.slug for entry in entries] == ["abi", "alpha", "gamma"]
        entry_map = {entry.slug: entry for entry in entries}

        assert entry_map["abi"].build_step == "phase3-dump"
        assert entry_map["abi"].description == "ABI layout"
        assert entry_map["alpha"].build_step == "phase3-alpha-dump"
        assert entry_map["alpha"].description == "alpha"

        assert entry_map["alpha"].manifest_path == paths.fixtures_dir / "phase3_alpha_manifest.json"
        assert entry_map["abi"].manifest_path == abi_fixture / "phase3_abi_manifest.json"
        assert entry_map["gamma"].manifest_path is None
        assert entry_map["gamma"].manifest_candidates == (
            paths.fixtures_dir / "phase3_gamma_manifest.json",
            gamma_fixture / "phase3_gamma_manifest.json",
        )
        assert entry_map["alpha"].fixture_key == "phase3_alpha"
        assert entry_map["alpha"].manifest_candidates == (
            paths.fixtures_dir / "phase3_alpha_manifest.json",
            alpha_fixture / "phase3_alpha_manifest.json",
        )
        assert entry_map["alpha"].interop_gate is None
        assert entry_map["alpha"].interop_gate_mode == "missing"
        assert entry_map["abi"].interop_gate_mode == "missing"
        assert entry_map["gamma"].interop_gate_mode == "missing"
        gamma_dict = entry_map["gamma"].to_dict()
        assert gamma_dict["manifest"] is None
        assert gamma_dict["manifest_candidates"] == [
            "zigux/tests/fixtures/phase3_gamma_manifest.json",
            "zigux/tests/fixtures/phase3_gamma/phase3_gamma_manifest.json",
        ]

        expected_entry_json = {
            "build_step": "phase3-alpha-dump",
            "check_script": "scripts/zigux/check-phase3-alpha.py",
            "description": "alpha",
            "doc": "Documentation/zigux/phase3-alpha-slice.md",
            "dump": "zigux/tests/phase3_alpha_dump.zig",
            "expected": "zigux/tests/fixtures/phase3_alpha/expected.json",
            "fixture_dir": "zigux/tests/fixtures/phase3_alpha",
            "harness": "zigux/tests/fixtures/phase3_alpha/phase3_alpha_c_harness.c",
            "interop_gate": None,
            "interop_gate_mode": "missing",
            "manifest": "zigux/tests/fixtures/phase3_alpha_manifest.json",
            "manifest_candidates": [
                "zigux/tests/fixtures/phase3_alpha_manifest.json",
                "zigux/tests/fixtures/phase3_alpha/phase3_alpha_manifest.json",
            ],
            "slug": "alpha",
        }
        assert entry_map["alpha"].to_dict() == expected_entry_json
        assert description_for_slug("bitmap-cpumask") == "bitmap/cpumask"
        assert build_step_for_slug("bitmap-cpumask") == "phase3-bitmap-cpumask-dump"
        assert shared_runner_gate_for_slug("alpha") == "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha"
        assert legacy_wrapper_gate_for_slug("alpha") == "PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha.py"

        wrapper_scripts = discover_phase3_wrapper_scripts(paths)
        assert wrapper_scripts == []
        (paths.scripts_dir / "check-phase3-alpha.py").write_text(
            "#!/usr/bin/env python3\n",
            encoding="utf-8",
        )
        (paths.scripts_dir / "check-phase3-gamma.py").write_text(
            "#!/usr/bin/env python3\n",
            encoding="utf-8",
        )
        assert [path.name for path in discover_phase3_wrapper_scripts(paths)] == [
            "check-phase3-alpha.py",
            "check-phase3-gamma.py",
        ]

        (paths.docs_dir / "phase3-legacy-slice.md").write_text(
            "\n".join(
                [
                    "legacy doc",
                    f"- `{legacy_wrapper_gate_for_slug('legacy')}`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        legacy_fixture = paths.fixtures_dir / "phase3_legacy"
        legacy_fixture.mkdir()
        (legacy_fixture / "expected.json").write_text(
            json.dumps({"kind": "legacy"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (legacy_fixture / "phase3_legacy_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (paths.tests_dir / "phase3_legacy_dump.zig").write_text(
            "// legacy\n",
            encoding="utf-8",
        )
        (paths.docs_dir / "phase3-shared-slice.md").write_text(
            "\n".join(
                [
                    "shared doc",
                    f"- `{shared_runner_gate_for_slug('shared')}`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        shared_fixture = paths.fixtures_dir / "phase3_shared"
        shared_fixture.mkdir()
        (shared_fixture / "expected.json").write_text(
            json.dumps({"kind": "shared"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (shared_fixture / "phase3_shared_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (paths.tests_dir / "phase3_shared_dump.zig").write_text(
            "// shared\n",
            encoding="utf-8",
        )
        (paths.docs_dir / "phase3-custom-slice.md").write_text(
            "\n".join(
                [
                    "custom doc",
                    f"- `{INTEROP_GATE_PREFIX}python3 scripts/zigux/custom-phase3-custom.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        custom_fixture = paths.fixtures_dir / "phase3_custom"
        custom_fixture.mkdir()
        (custom_fixture / "expected.json").write_text(
            json.dumps({"kind": "custom"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (custom_fixture / "phase3_custom_c_harness.c").write_text(
            "int main(void) { return 0; }\n",
            encoding="utf-8",
        )
        (paths.tests_dir / "phase3_custom_dump.zig").write_text(
            "// custom\n",
            encoding="utf-8",
        )

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
        assert references == []
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
        assert [entry.slug for entry in ordered_entries[:3]] == ["abi", "alpha", "custom"]
        assert rewrite_artifact_diff_phase3_section(entries, artifact_diff_path) is True
        rewritten_artifact_diff = artifact_diff_path.read_text(encoding="utf-8")
        assert "stale line" not in rewritten_artifact_diff
        assert "- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim." in rewritten_artifact_diff
        assert "- `zigux/tests/fixtures/phase3_custom/expected.json` anchors the bounded Phase 3 custom parity claim." in rewritten_artifact_diff
        assert "Rules\n- keep fixtures reviewable\n" in rewritten_artifact_diff
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
        assert artifact_diff_phase3_section_needs_rewrite(entries, artifact_diff_path) is True
        assert rewrite_artifact_diff_phase3_section(entries, artifact_diff_path) is True
        assert artifact_diff_phase3_section_needs_rewrite(entries, artifact_diff_path) is False
        assert rewrite_artifact_diff_phase3_section(entries, artifact_diff_path) is False

        (paths.docs_dir / "artifact-diff.md").write_text(
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
        (paths.docs_dir / "phase3-notes.md").write_text(
            "\n".join(
                [
                    "# Notes",
                    "",
                    "- `python3 scripts/zigux/check-phase3-alpha.py`",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        audit_issues = audit_phase3_doc_sync(entries, paths, artifact_diff_path)
        assert [issue.to_row() for issue in audit_issues] == [
            "legacy-wrapper-reference\tDocumentation/zigux/phase3-notes.md\t3\talpha\tcommand\tdocumentation\tpython3 scripts/zigux/run-phase3-checks.py --slug alpha",
            "artifact-diff-phase3-stale\tDocumentation/zigux/artifact-diff.md",
        ]
        rewrite_non_doc_legacy_wrapper_references(entries, paths)
        rewrite_artifact_diff_phase3_section(entries, artifact_diff_path)
        assert audit_phase3_doc_sync(entries, paths, artifact_diff_path) == []

        overgrown_slug = "alpha-beta-gamma-delta-epsilon-zeta-eta-theta-iota-kappa-lambda-mu-nu"
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

    print(json.dumps([entry.to_dict() for entry in entries], indent=2, sort_keys=True))
