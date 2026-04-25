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
        lines = path.read_text(encoding="utf-8").splitlinmuÓ_-¢G§²ÚîÆ­yÒ76W'BÆÂ†6æF–FFRç6ÇVrÒ÷fW&w&÷vå÷v—F…÷&Vf—‚f÷"6æF–FFR–â&VæÖUö6æF–FFW2 ¢&WWF—F—fUö6æöæ–6Å÷6ÇVrÒ&Æö÷×v–æF÷r×öÆ–7’Ö'VFvWB ¢‡F‡2æFö75öF—"òb'†6S2×·&WWF—F—fUö6æöæ–6Å÷6ÇVwÒ×6Æ–6RæÖB"’çw&—FU÷FW‡B€¢'&WWF—F—fR6æöæ–6ÅÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢&WWF—F—fUö6æöæ–6Åöf—‡GW&RÒF‡2æf—‡GW&W5öF—"òb'†6S5÷·&WWF—F—fUö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—Ò ¢&WWF—F—fUö6æöæ–6Åöf—‡GW&RæÖ¶F—"‚¢‡F‡2çFW7G5öF—"òb'†6S5÷·&WWF—F—fUö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"’çw&—FU÷FW‡B€¢"òò&WWF—F—fR6æöæ–6ÅÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢‡&WWF—F—fUö6æöæ–6Åöf—‡GW&Rò&W‡V7FVBæ§6öâ"’çw&—FU÷FW‡B€¢'·ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢&WWF—F—fUö6æöæ–6Åöf—‡GW&P¢òb'†6S5÷·&WWF—F—fUö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’çw&—FU÷FW‡B€¢&–çBÖ–â‡fö–B’²&WGW&â²ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢&WWF—F—fUö6æöæ–6Åöf—‡GW&P¢òb'†6S5÷·&WWF—F—fUö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'†6R#¢%†6R2"Â'7FGW2#¢'&VG’"Â'6Æ–6R#¢'&WWF—F—fR6æöæ–6Â"Â&f–ÆW2#¢µÒÂ&f–ÆUö6÷VçB#¢Ò’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢&WWF—F—fU÷v—F…÷&Vf—‚Òb'·&WWF—F—fUö6æöæ–6Å÷6ÇVwÒ×v–æF÷r×öÆ–7’Ö'VFvWB×v–æF÷r×öÆ–7’ ¢&WWF—F—fUöf—‡GW&RÒF‡2æf—‡GW&W5öF—"òb'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Ò ¢&WWF—F—fUöf—‡GW&RæÖ¶F—"‚¢‡F‡2æFö75öF—"òb'†6S2×·&WWF—F—fU÷v—F…÷&Vf—‡Ò×6Æ–6RæÖB"’çw&—FU÷FW‡B€¢'&WWF—F—fR&Vf—…Æâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢‡F‡2çFW7G5öF—"òb'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"’çw&—FU÷FW‡B€¢"òò&WWF—F—fR&Vf—…Æâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢‡&WWF—F—fUöf—‡GW&Rò&W‡V7FVBæ§6öâ"’çw&—FU÷FW‡B€¢'·ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢&WWF—F—fUöf—‡GW&P¢òb'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’çw&—FU÷FW‡B€¢&–çBÖ–â‡fö–B’²&WGW&â²ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢&WWF—F—fUöf—‡GW&P¢òb'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'†6R#¢%†6R2"Â'7FGW2#¢'&VG’"Â'6Æ–6R#¢'&WWF—F—fR"Â&f–ÆW2#¢µÒÂ&f–ÆUö6÷VçB#¢Ò’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢&VæÖUö6æF–FFW2ÒF—66÷fW%÷†6S5÷6ÇVu÷&VæÖUö6æF–FFW2†F—66÷fW%÷†6S5÷6Æ–6W2‡F‡2’¢76W'BÆÂ†6æF–FFRç6ÇVrÒ÷fW&w&÷vå÷v—F…÷&Vf—‚f÷"6æF–FFR–â&VæÖUö6æF–FFW2¢&WWF—F—fUö6æF–FFRÒæW‡B†6æF–FFRf÷"6æF–FFR–â&VæÖUö6æF–FFW2–b6æF–FFRç6ÇVrÓÒ&WWF—F—fU÷v—F…÷&Vf—‚¢76W'B&WWF—F—fUö6æF–FFRæ6æöæ–6Å÷6ÇVrÓÒ&WWF—F—fUö6æöæ–6Å÷6ÇVp¢76W'B'6ÇVr×&WVFVB×‡&6R"–â&WWF—F—fUö6æF–FFRæ—77VUö6öFW0¢&VæÖUö–×7G2ÒF—66÷fW%÷†6S5÷6ÇVu÷&VæÖUö–×7G2†F—66÷fW%÷†6S5÷6Æ–6W2‡F‡2’¢76W'BÆÂ†–×7Bç6ÇVrÒ÷fW&w&÷vå÷v—F…÷&Vf—‚f÷"–×7B–â&VæÖUö–×7G2¢&VæÖUö–×7BÒæW‡B†–×7Bf÷"–×7B–â&VæÖUö–×7G2–b–×7Bç6ÇVrÓÒ&WWF—F—fU÷v—F…÷&Vf—‚¢76W'B&VæÖUö–×7Bæ6æöæ–6Å÷6ÇVrÓÒ&WWF—F—fUö6æöæ–6Å÷6ÇVp¢76W'B'6ÇVr×&WVFVB×‡&6R"–â&VæÖUö–×7Bæ—77VUö6öFW0¢76W'BÆVâ‡&VæÖUö–×7BçF‡2’ÓÒ`¢76W'Bµ÷&VÂ‡F‚ÂF‡2ç&ö÷B’f÷"F‚–â&VæÖUö–×7BçF‡7ÒÓÒ°¢b$Fö7VÖVçFF–öâ÷¦–wW‚÷†6S2×·&WWF—F—fU÷v—F…÷&Vf—‡Ò×6Æ–6RæÖB"À¢b'¦–wW‚÷FW7G2÷†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"À¢b'¦–wW‚÷FW7G2öf—‡GW&W2÷†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Ò"À¢b'¦–wW‚÷FW7G2öf—‡GW&W2÷†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÒöW‡V7FVBæ§6öâ"À¢€¢'¦–wW‚÷FW7G2öf—‡GW&W2ò ¢b'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Òò ¢b'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’À¢€¢'¦–wW‚÷FW7G2öf—‡GW&W2ò ¢b'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Òò ¢b'†6S5÷·&WWF—F—fU÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’À¢Ð¢‡F‡2æFö75öF—"ò'†6S2ÖÖW&vRÖæ÷FW2æÖB"’çw&—FU÷FW‡B€¢%Æâ"æ¦ö–â€¢°¢"2ÖW&vRæ÷FW2"À¢""À¢b"Ò—F†öã267&—G2÷¦–wW‚÷'Vâ×†6S2Ö6†V6·2ç’Ò×6ÇVr·&WWF—F—fU÷v—F…÷&Vf—‡Ö"À¢""À¢Ð¢’À¢Væ6öF–æsÒ'WFbÓ‚"À¢æWvÆ–æSÒ%Æâ"À¢¢‡F‡2çFW7G5öF—"ò&'V–ÆBç¦–r"’çw&—FU÷FW‡B€¢%Æâ"æ¦ö–â€¢°¢&6öç7B7FBÒ–×÷'B…Â'7FEÂ"“²"À¢""À¢'V"fâ'V–ÆB†#¢§7FBä'V–ÆB’fö–B²"À¢b"òÒ"ç7FW…Â'¶'V–ÆE÷7FWöf÷%÷6ÇVr‡&WWF—F—fU÷v—F…÷&Vf—‚—ÕÂ"ÂÂ&FVÖò7FWÂ"“²"À¢'Ò"À¢""À¢Ð¢’À¢Væ6öF–æsÒ'WFbÓ‚"À¢æWvÆ–æSÒ%Æâ"À¢¢ÖW&vU÷&WÒF—66÷fW%÷†6S5÷6ÇVuöÖW&vU÷&W†F—66÷fW%÷†6S5÷6Æ–6W2‡F‡2’ÂF‡2¢ÖW&vUöVçG'’ÒæW‡B‡&Wf÷"&W–âÖW&vU÷&W–b&Wç6ÇVrÓÒ&WWF—F—fU÷v—F…÷&Vf—‚¢76W'BÖW&vUöVçG'’æ6æöæ–6Å÷6ÇVrÓÒ&WWF—F—fUö6æöæ–6Å÷6ÇVp¢76W'BGWÆR…÷&VÂ‡F‚ÂF‡2ç&ö÷B’f÷"F‚–âÖW&vUöVçG'’ç&WF—&U÷F‡2’ÓÒGWÆR€¢÷&VÂ‡F‚ÂF‡2ç&ö÷B’f÷"F‚–â&VæÖUö–×7BçF‡0¢¢76W'B·&VfW&Væ6RçFõ÷&÷r‚’f÷"&VfW&Væ6R–âÖW&vUöVçG'’ç&VfW&Væ6W5ÒÓÒ°¢$Fö7VÖVçFF–öâ÷¦–wW‚÷†6S2ÖÖW&vRÖæ÷FW2æÖEÇC5ÇFFö7VÖVçFF–öåÇG'VææW"Ç6ÇVr"À¢'¦–wW‚÷FW7G2ö'V–ÆBç¦–uÇCEÇF'V–ÆB×7FWÇF'V–ÆB×7FWÇ6ÇVr"À¢Ð ¢Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVrÒ&Ö—6ÖF6‚×v–æF÷r×öÆ–7’Ö'VFvWB ¢‡F‡2æFö75öF—"òb'†6S2×¶Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVwÒ×6Æ–6RæÖB"’çw&—FU÷FW‡B€¢&Ö—6ÖF6†VB6æöæ–6ÅÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢Ö—6ÖF6†VEö6æöæ–6Åöf—‡GW&RÒF‡2æf—‡GW&W5öF—"òb'†6S5÷¶Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—Ò ¢Ö—6ÖF6†VEö6æöæ–6Åöf—‡GW&RæÖ¶F—"‚¢‡F‡2çFW7G5öF—"òb'†6S5÷¶Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"’çw&—FU÷FW‡B€¢"òòÖ—6ÖF6†VB6æöæ–6ÅÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢†Ö—6ÖF6†VEö6æöæ–6Åöf—‡GW&Rò&W‡V7FVBæ§6öâ"’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'7VÖÖ'’#¢²&6¶VB#¢×ÒÂ6÷'Eö¶W—3ÕG'VR’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Ö—6ÖF6†VEö6æöæ–6Åöf—‡GW&P¢òb'†6S5÷¶Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’çw&—FU÷FW‡B€¢&–çBÖ–â‡fö–B’²&WGW&â²ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Ö—6ÖF6†VEö6æöæ–6Åöf—‡GW&P¢òb'†6S5÷¶Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'†6R#¢%†6R2"Â'7FGW2#¢'&VG’"Â'6Æ–6R#¢&Ö—6ÖF6†VB6æöæ–6Â"Â&f–ÆW2#¢µÒÂ&f–ÆUö6÷VçB#¢Ò’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢Ö—6ÖF6†VE÷v—F…÷&Vf—‚Òb'¶Ö—6ÖF6†VEö6æöæ–6Å÷6ÇVwÒ×v–æF÷r×öÆ–7’Ö'VFvWB×v–æF÷r×öÆ–7’ ¢Ö—6ÖF6†VEöf—‡GW&RÒF‡2æf—‡GW&W5öF—"òb'†6S5÷¶Ö—6ÖF6†VE÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Ò ¢Ö—6ÖF6†VEöf—‡GW&RæÖ¶F—"‚¢‡F‡2æFö75öF—"òb'†6S2×¶Ö—6ÖF6†VE÷v—F…÷&Vf—‡Ò×6Æ–6RæÖB"’çw&—FU÷FW‡B€¢&Ö—6ÖF6†VB&Vf—…Æâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢‡F‡2çFW7G5öF—"òb'†6S5÷¶Ö—6ÖF6†VE÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"’çw&—FU÷FW‡B€¢"òòÖ—6ÖF6†VB&Vf—…Æâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢†Ö—6ÖF6†VEöf—‡GW&Rò&W‡V7FVBæ§6öâ"’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'7VÖÖ'’#¢²&6¶VB#¢Â&FVfW'&VB#¢×ÒÂ6÷'Eö¶W—3ÕG'VR’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Ö—6ÖF6†VEöf—‡GW&P¢òb'†6S5÷¶Ö—6ÖF6†VE÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’çw&—FU÷FW‡B€¢&–çBÖ–â‡fö–B’²&WGW&â²ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Ö—6ÖF6†VEöf—‡GW&P¢òb'†6S5÷¶Ö—6ÖF6†VE÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'†6R#¢%†6R2"Â'7FGW2#¢'&VG’"Â'6Æ–6R#¢&Ö—6ÖF6†VB&Vf—‚"Â&f–ÆW2#¢µÒÂ&f–ÆUö6÷VçB#¢Ò’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢&VæÖUö6æF–FFW2ÒF—66÷fW%÷†6S5÷6ÇVu÷&VæÖUö6æF–FFW2†F—66÷fW%÷†6S5÷6Æ–6W2‡F‡2’¢76W'BÆÂ†6æF–FFRç6ÇVrÒÖ—6ÖF6†VE÷v—F…÷&Vf—‚f÷"6æF–FFR–â&VæÖUö6æF–FFW2 ¢Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVrÒ&Öæ–fW7B×v–æF÷r×öÆ–7’Ö'VFvWB ¢‡F‡2æFö75öF—"òb'†6S2×¶Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVwÒ×6Æ–6RæÖB"’çw&—FU÷FW‡B€¢&Öæ–fW7B6æöæ–6ÅÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢Öæ–fW7EööæÇ•ö6æöæ–6Åöf—‡GW&RÒF‡2æf—‡GW&W5öF—"òb'†6S5÷¶Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—Ò ¢Öæ–fW7EööæÇ•ö6æöæ–6Åöf—‡GW&RæÖ¶F—"‚¢‡F‡2çFW7G5öF—"òb'†6S5÷¶Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"’çw&—FU÷FW‡B€¢"òòÖæ–fW7B6æöæ–6ÅÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢†Öæ–fW7EööæÇ•ö6æöæ–6Åöf—‡GW&Rò&W‡V7FVBæ§6öâ"’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'7VÖÖ'’#¢²&6¶VB#¢×ÒÂ6÷'Eö¶W—3ÕG'VR’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Öæ–fW7EööæÇ•ö6æöæ–6Åöf—‡GW&P¢òb'†6S5÷¶Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’çw&—FU÷FW‡B€¢&–çBÖ–â‡fö–B’²&WGW&â²ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Öæ–fW7EööæÇ•ö6æöæ–6Åöf—‡GW&P¢òb'†6S5÷¶Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVrç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'†6R#¢%†6R2"Â'7FGW2#¢'&VG’"Â'6Æ–6R#¢&Öæ–fW7B6æöæ–6Â"Â&f–ÆW2#¢·²'F‚#¢&W‡V7FVBæ§6öâ'ÕÒÂ&f–ÆUö6÷VçB#¢ÒÂ6÷'Eö¶W—3ÕG'VR’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢Öæ–fW7EööæÇ•÷v—F…÷&Vf—‚Òb'¶Öæ–fW7EööæÇ•ö6æöæ–6Å÷6ÇVwÒ×v–æF÷r×öÆ–7’Ö'VFvWB×v–æF÷r×öÆ–7’ ¢Öæ–fW7EööæÇ•öf—‡GW&RÒF‡2æf—‡GW&W5öF—"òb'†6S5÷¶Öæ–fW7EööæÇ•÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Ò ¢Öæ–fW7EööæÇ•öf—‡GW&RæÖ¶F—"‚¢‡F‡2æFö75öF—"òb'†6S2×¶Öæ–fW7EööæÇ•÷v—F…÷&Vf—‡Ò×6Æ–6RæÖB"’çw&—FU÷FW‡B€¢&Öæ–fW7B&Vf—…Æâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢‡F‡2æFW7G5öF—"òb'†6S5÷¶Öæ–fW7EööæÇ•÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöGV×ç¦–r"’çw&—FU÷FW‡B€¢"òòÖæ–fW7B&Vf—…Æâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢†Öæ–fW7EööæÇ•öf—‡GW&Rò&W‡V7FVBæ§6öâ"’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'7VÖÖ'’#¢²&6¶VB#¢×ÒÂ6÷'Eö¶W—3ÕG'VR’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Öæ–fW7EööæÇ•öf—‡GW&P¢òb'†6S5÷¶Öæ–fW7EööæÇ•÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—Õö5ö†&æW72æ2 ¢’çw&—FU÷FW‡B€¢&–çBÖ–â‡fö–B’²&WGW&â²ÕÆâ"À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢€¢Öæ–fW7EööæÇ•öf—‡GW&P¢òb'†6S5÷¶Öæ–fW7EööæÇ•÷v—F…÷&Vf—‚ç&WÆ6R‚rÒrÂuòr—ÕöÖæ–fW7Bæ§6öâ ¢’çw&—FU÷FW‡B€¢§6öâæGV×2‡²'†6R#¢%†6R2"Â'7FGW2#¢'&VG’"Â'6Æ–6R#¢&Öæ–fW7B&Vf—‚"Â&f–ÆW2#¢·²'F‚#¢&W‡V7FVBæ§6öâ"Â&¶–æB#¢&W‡G&'ÕÒÂ&f–ÆUö6÷VçB#¢ÒÂ6÷'Eö¶W—3ÕG'VR’À¢Væ6öF–æsÒ'WFbÓ‚"À¢¢&VæÖUö6æF–FFW2ÒF—66÷fW%÷†6S5÷6ÇVu÷&VæÖUö6æF–FFW2†F—66÷fW%÷†6S5÷6Æ–6W2‡F‡2’¢76W'BÆÂ†6æF–FFRç6ÇVrÒÖæ–fW7EööæÇ•÷v—F…÷&Vf—‚f÷"6æF–FFR–â&VæÖUö6æF–FFW2 ¢'6W"Ò'V–ÆE÷'6W"‚¢76W'B'6W"ç'6Uö&w2…²"Ò×&Ww&—FRÖÆVv7’×w&W"×&VfW&Væ6W2%Ò’ç&Ww&—FUöÆVv7•÷w&W%÷&VfW&Væ6W2—2G'VP¢76W'B'6W"ç'6Uö&w2…²"Ò×&Ww&—FR×6†&VB×'VææW"×&VfW&Væ6RÖFö72%Ò’ç&Ww&—FUöÆVv7•÷w&W%÷&VfW&Væ6W2—2G'VP¢76W'B'6W"ç'6Uö&w2…²"ÒÖVF—BÖFö2×7–æ2%Ò’æVF—EöFö5÷7–æ2—2G'VP¢76W'B'6W"ç'6Uö&w2…²"ÒÖVF—B×6ÇVr×6æ—G’%Ò’æVF—E÷6ÇVu÷6æ—G’—2G'VP¢76W'B'6W"ç'6Uö&w2…²"Ò×7VvvW7B×6ÇVr×&VæÖW2%Ò’ç7VvvW7E÷6ÇVu÷&VæÖW2—2G'VP¢76W'B'6W"ç'6Uö&w2…²"Ò×7VvvW7B×6ÇVr×&VæÖR×F‡2%Ò’ç7VvvW7E÷6ÇVu÷&VæÖU÷F‡2—2G'VP¢76W'B'6W"ç'6Uö&w2…²"Ò×7VvvW7B×6ÇVrÖÖW&vR×&W%Ò’ç7VvvW7E÷6ÇVuöÖW&vU÷&W—2G'VP¢76W'B'6W"ç'6Uö&w2…²"Ò×7VvvW7B×6ÇVrÖÖW&vR×Æç2%Ò’ç7VvvW7E÷6ÇVuöÖW&vU÷&W—2G'VP ¢&–çB‚%„4S5ô4DÄôuõ4TÄeõDU5C×72"¢&WGW&â   ¦FVb'V–ÆE÷'6W"‚’Óâ&w'6Rä&wVÖVçE'6W# ¢'6W"Ò&w'6Rä&wVÖVçE'6W"†FW67&—F–öãÒ$F—66÷fW"¦–wW‚†6R26Æ–6W2æBF†V—"vVæW&FVB6ö×æ–öâF‡2â"¢'6W"æFEö&wVÖVçB‚"Ò×6VÆb×FW7B"Â7F–öãÒ'7F÷&U÷G'VR"Â†VÇÒ%'Vâ—6öÆFVBF—66÷fW'’æBÖæ–fW7B×6VÆV7F–öâ6†V6·2â"¢'6W"æFEö&wVÖVçB€¢"ÒÖÆVv7’×w&W"ÖFö72"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ$Æ—7BF—66÷fW&VB†6R26Æ–6W2v†÷6RFö727F–ÆÂö–çBBÆVv7’W"×6Æ–6Rw&W"6öÖÖæG2â"À¢¢'6W"æFEö&wVÖVçB€¢"Ò×&Ww&—FR×6†&VB×'VææW"ÖFö72"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ%&Ww&—FRF—66÷fW&VBÆVv7’†6R2Fö26öÖÖæG2FòF†R6†&VB'Vâ×†6S2Ö6†V6·2ç’Ò×6ÇVrf÷&Òâ"À¢¢'6W"æFEö&wVÖVçB€¢"ÒÖÆVv7’×w&W"×&VfW&Væ6W2"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ$Æ—7B&VÖ–æ–ærF—66÷fW&VB†6R2w&W"ÖVçF–öç2–âæöâ×6Æ–6RFö7VÖVçFF–öââ"À¢¢'6W"æFEö&wVÖVçB€¢"Ò×&Ww&—FRÖÆVv7’×w&W"×&VfW&Væ6W2"À¢"Ò×&Ww&—FR×6†&VB×'VææW"×&VfW&Væ6RÖFö72"À¢FW7CÒ'&Ww&—FUöÆVv7•÷w&W%÷&VfW&Væ6W2"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ%&Ww&—FRæöâ×6Æ–6RFö7VÖVçFF–öâw&W"ÖVçF–öç2FòF†R6†&VB'Vâ×†6S2Ö6†V6·2ç’Ò×6ÇVrf÷&Òâ"À¢¢'6W"æFEö&wVÖVçB€¢"Ò×&Ww&—FRÖ'F–f7BÖF–fb×†6S2×6V7F–öâ"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ%&Ww&—FRF†R'F–f7BÖF–fb†6R26V7F–öâg&öÒF†RF—66÷fW&VB6Æ–6R6FÆörâ"À¢¢'6W"æFEö&wVÖVçB€¢"ÒÖVF—BÖFö2×7–æ2"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ%&W÷'B7FÆRæöâ×6Æ–6Rw&W"&VfW&Væ6W2æB'F–f7BÖF–fb†6R2G&–gBÂF†VâW†—Bæöâ×¦W&òv†Vâç’&Rf÷VæBâ"À¢¢'6W"æFEö&wVÖVçB€¢"ÒÖVF—B×6ÇVr×6æ—G’"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ%&W÷'B7W7–6–÷W6Ç’&WWF—F—fR÷"÷fW&w&÷vâF—66÷fW&VB†6R26ÇVw2ÂF†VâW†—Bæöâ×¦W&òv†Vâç’&Rf÷VæBâ"À¢¢'6W"æFEö&wVÖVçB€¢"Ò×7VvvW7B×6ÇVr×&VæÖW2"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ$Æ—7B÷fW&w&÷vâF—66÷fW&VB†6R26ÇVw2F†B†fR6†÷'FW"6ÆVâ&Vf—‚Ç&VG’&W6VçB–âF†R6FÆörâ"À¢¢'6W"æFEö&wVÖVçB€¢"Ò×7VvvW7B×6ÇVr×&VæÖR×F‡2"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ$Æ—7BF†R6÷&R6Æ–6Rf–ÆW2æBF—&V7F÷&–W2F†B7VvvW7FVB†6R26ÇVr&VæÖRv÷VÆBF÷V6‚â"À¢¢'6W"æFEö&wVÖVçB€¢"Ò×7VvvW7B×6ÇVrÖÖW&vR×&W"À¢"Ò×7VvvW7B×6ÇVrÖÖW&vR×Æç2"À¢7F–öãÒ'7F÷&U÷G'VR"À¢†VÇÒ$Æ—7BF†R&WF—&V&ÆR6Æ–6R'F–f7G2ÇW2F†RW‡G&Fö72Âv÷&¶fÆ÷rÂ67&—BÂ÷"'V–ÆB×7FW&VfW&Væ6W2F†B7F–ÆÂÖVçF–öâV6‚6fRÆöær6ÇVrVÇ6Wv†W&R–âF†RG&VRâ"À¢¢&WGW&â'6W   ¦–bõöæÖUõòÓÒ%õöÖ–åõò# ¢'6W"Ò'V–ÆE÷'6W"‚¢&w2Ò'6W"ç'6Uö&w2‚ ¢–b&w2ç6VÆe÷FW7C ¢&—6R7—7FVÔW†—B‡'Vå÷6VÆe÷FW7B‚’ ¢VçG&–W2ÒF—66÷fW%÷†6S5÷6Æ–6W2‚¢–b&w2æÆVv7•÷w&W%öFö73 ¢G'“ ¢f÷"VçG'’–âVçG&–W3 ¢–bVçG'’æ–çFW&÷övFUöÖöFRÓÒ&ÆVv7’×w&W"# ¢&–çB†b'¶VçG'’ç6ÇVwÕÇGµ÷&VÂ†VçG'’æFö5÷F‚ÂVçG'’ç&ö÷B—ÕÇG¶VçG'’æ–çFW&÷övFWÒ"¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ¢–b&w2ç&Ww&—FU÷6†&VE÷'VææW%öFö73 ¢&Ww&—GFVâÒ&Ww&—FUöÆVv7•÷w&W%öFö72†VçG&–W2¢f÷"F‚–â&Ww&—GFVã ¢&–çB‡F‚¢&—6R7—7FVÔW†—Bƒ¢–b&w2æÆVv7•÷w&W%÷&VfW&Væ6W3 ¢G'“ ¢f÷"&VfW&Væ6R–âF—66÷fW%öæöåöFö5öÆVv7•÷w&W%÷&VfW&Væ6W2†VçG&–W2“ ¢&–çB‡&VfW&Væ6RçFõ÷&÷r‚’¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ¢–b&w2ç&Ww&—FUöÆVv7•÷w&W%÷&VfW&Væ6W3 ¢&Ww&—GFVâÒ&Ww&—FUöæöåöFö5öÆVv7•÷w&W%÷&VfW&Væ6W2†VçG&–W2¢f÷"F‚–â&Ww&—GFVã ¢&–çB‡F‚¢&—6R7—7FVÔW†—Bƒ¢–b&w2ç&Ww&—FUö'F–f7EöF–fe÷†6S5÷6V7F–öã ¢–b&Ww&—FUö'F–f7EöF–fe÷†6S5÷6V7F–öâ†VçG&–W2“ ¢&–çB…÷&VÂ„%D”d5EôD”deõD‚’¢&—6R7—7FVÔW†—Bƒ¢–b&w2æVF—EöFö5÷7–æ3 ¢G'“ ¢—77VW2ÒVF—E÷†6S5öFö5÷7–æ2†VçG&–W2¢f÷"—77VR–â—77VW3 ¢&–çB†—77VRçFõ÷&÷r‚’¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ–b—77VW2VÇ6R¢–b&w2æVF—E÷6ÇVu÷6æ—G“ ¢G'“ ¢—77VW2ÒVF—E÷†6S5÷6ÇVu÷6æ—G’†VçG&–W2¢f÷"—77VR–â—77VW3 ¢&–çB†—77VRçFõ÷&÷r‚’¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ–b—77VW2VÇ6R¢–b&w2ç7VvvW7E÷6ÇVu÷&VæÖW3 ¢G'“ ¢6æF–FFW2ÒF—66÷fW%÷†6S5÷6ÇVu÷&VæÖUö6æF–FFW2†VçG&–W2¢f÷"6æF–FFR–â6æF–FFW3 ¢&–çB†6æF–FFRçFõ÷&÷r‚’¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ¢–b&w2ç7VvvW7E÷6ÇVu÷&VæÖU÷F‡3 ¢G'“ ¢–×7G2ÒF—66÷fW%÷†6S5÷6ÇVu÷&VæÖUö–×7G2†VçG&–W2¢f÷"–×7B–â–×7G3 ¢&–çB†–×7BçFõ÷&÷r‚’¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ¢–b&w2ç7VvvW7E÷6ÇVuöÖW&vU÷&W ¢G'“ ¢ÖW&vU÷&WÒF—66÷fW%÷†6S5÷6ÇVuöÖW&vU÷&W†VçG&–W2¢f÷"&W–âÖW&vU÷&W ¢&–çB‡&WçFõ÷&÷r‚’¢W†6WB'&ö¶Vå—TW'&÷# ¢7—2æW†—Bƒ¢&—6R7—7FVÔW†—Bƒ ¢&–çB†§6öâæGV×2…¶VçG'’çFõöF–7B‚’f÷"VçG'’–âVçG&–W5ÒÂ–æFVçCÓ"Â6÷'Eö¶W—3ÕG'VR’