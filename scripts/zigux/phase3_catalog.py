#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "Documentation" / "zigux"
SCRIPTS_DIR = ROOT / "scripts" / "zigux"
TESTS_DIR = ROOT / "zigux" / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"

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


def discover_phase3_slices(paths: Phase3Paths = DEFAULT_PATHS) -> list[Phase3Slice]:
    slices: list[Phase3Slice] = []
    for slug in _collect_slugs(paths):
        fixture_key = f"{FIXTURE_PREFIX}{slug.replace('-', '_')}"
        fixture_dir = paths.fixtures_dir / fixture_key
        manifest_candidates = (
            paths.fixtures_dir / f"{fixture_key}_manifest.json",
            fixture_dir / f"{fixture_key}_manifest.json",
        )
        slices.append(
            Phase3Slice(
                root=paths.root,
                slug=slug,
                description=description_for_slug(slug),
                build_step=build_step_for_slug(slug),
                doc_path=paths.docs_dir / f"{DOC_PREFIX}{slug}{DOC_SUFFIX}",
                check_script=paths.scripts_dir / f"{SCRIPT_PREFIX}{slug}{SCRIPT_SUFFIX}",
                dump_path=paths.tests_dir / f"{fixture_key}{DUMP_SUFFIX}",
                fixture_dir=fixture_dir,
                expected_path=fixture_dir / "expected.json",
                harness_path=fixture_dir / f"{fixture_key}_c_harness.c",
                manifest_candidates=manifest_candidates,
                manifest_path=_pick_manifest(slug, manifest_candidates),
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
        assert entry_map["gamma"].build_step == "phase3-gamma-dump"
        assert entry_map["gamma"].description == "gamma"
        assert _rel(entry_map["gamma"].dump_path, paths.root) == "zigux/tests/phase3_gamma_dump.zig"
        assert _rel(entry_map["delta"].manifest_path, paths.root) == "zigux/tests/fixtures/phase3_delta_manifest.json"

        alpha_dict = entry_map["alpha"].to_dict()
        assert alpha_dict["doc"] == "Documentation/zigux/phase3-alpha-slice.md"
        assert alpha_dict["build_step"] == "phase3-alpha-dump"
        assert alpha_dict["manifest"] == "zigux/tests/fixtures/phase3_alpha/phase3_alpha_manifest.json"

    print("PHASE3_CATALOG_SELF_TEST=pass")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover Zigux Phase 3 slices and their generated companion paths.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated discovery and manifest-selection checks.")
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(run_self_test())

    print(json.dumps([entry.to_dict() for entry in discover_phase3_slices()], indent=2, sort_keys=True))