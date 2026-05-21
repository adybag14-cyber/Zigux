#!/usr/bin/env python3
"""Guard the bounded Phase 7 shared leaf-library evidence packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

EXPECTED_PACKET = "phase7-leaf-library-evidence"
EXPECTED_PHASE = "Phase 7"
EXPECTED_SCOPE = "shared leaf-library evidence rows and validation foothold only"
EXPECTED_COMPANIONS = [
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/check-phase7-shared-surface.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
]
EXPECTED_ROADMAP_ANCHORS = [
    "lib/string_helpers.c",
    "lib/cmdline.c",
    "lib/argv_split.c",
    "lib/rbtree.c",
]
EXPECTED_GAPS = [
    "lib/rbtree.zig",
    "zigux/tests/phase7_build.zig",
]
EXPECTED_HELPERS = [
    (
        "string_helpers",
        "lib/string_helpers.zig",
        [
            "pub const STRING_UNITS_10",
            "pub const KasprintfStrarrayResult",
            "pub fn kstrdupQuotable",
            "pub fn kstrdupQuotableCmdline",
        ],
    ),
    (
        "string_helpers_parse_int_array",
        "lib/string_helpers.zig",
        ["pub const ParseIntArrayError", "pub fn parseIntArray"],
    ),
    ("cmdline", "lib/cmdline.zig", ["pub fn parseOptionStr", "pub fn getOption"]),
    ("argv_split", "lib/argv_split.zig", ["pub const ArgvSplitResult", "pub fn argvSplit"]),
]
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]
REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback companions",
    "- `Documentation/zigux/README.md`",
    "- `scripts/zigux/check-phase7-build-wiring.py`",
    "- `scripts/zigux/README.md`",
    "- `zigux/tests/README.md`",
    "## Current replay inventory",
    "- `make -C zigux phase7-validate`",
    "## Current repo-reality gaps",
    "- `lib/rbtree.zig`",
    "`kstrdupQuotable()`",
    "`kstrdupQuotableCmdline()`",
    "`parseIntArray()`",
]
REQUIRED_MAKEFILE_SNIPPETS = [
    "phase7-validate:",
    "$(PYTHON) scripts/zigux/validate-phase7.py",
]
README_REQUIRED_RULES = [
    (DOCS_README_PATH, ["Phase 7 notes"]),
    (SCRIPTS_README_PATH, ["## Phase 7"]),
    (TESTS_README_PATH, ["## Phase 7"]),
]
REQUIRED_FILES = [
    CATALOG_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    Path("lib/string_helpers.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
]
SELF_TEST_CASE_COUNT = 12


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 7 marker in {path.as_posix()}: {snippet}")


def validate(repo_root: Path) -> None:
    missing = [str(rel) for rel in REQUIRED_FILES if not (repo_root / rel).is_file()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)

    manifest = read_json(repo_root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase7 packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase7 phase drift")
    if manifest.get("lane_scope") != EXPECTED_SCOPE:
        raise ValidationError("phase7 lane-scope drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_COMPANIONS:
        raise ValidationError("phase7 direct-readback companions mismatch")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase7 roadmap anchors mismatch")
    if manifest.get("current_replay_inventory") != EXPECTED_REPLAYS:
        raise ValidationError("phase7 replay inventory mismatch")
    if manifest.get("current_repo_reality_gaps") != EXPECTED_GAPS:
        raise ValidationError("phase7 repo-reality gaps mismatch")

    helpers = manifest.get("current_direct_helper_evidence")
    if not isinstance(helpers, list):
        raise ValidationError("phase7 helper evidence list missing")
    observed = []
    for helper in helpers:
        if not isinstance(helper, dict):
            raise ValidationError("phase7 helper evidence entry shape drift")
        observed.append((helper.get("key"), helper.get("zig_helper"), helper.get("expected_markers")))
    expected_observed = [(key, path, markers) for key, path, markers in EXPECTED_HELPERS]
    if observed != expected_observed:
        raise ValidationError("phase7 helper evidence ordering drift")

    for key, rel_path, markers in EXPECTED_HELPERS:
        content = read_text(repo_root / rel_path)
        for marker in markers:
            if marker not in content:
                raise ValidationError(f"phase7 helper marker missing for {key}: {marker}")

    for rel_path, required_snippets in README_REQUIRED_RULES:
        require_snippets(repo_root / rel_path, required_snippets)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / CATALOG_PATH, "\n".join([
        "- packet: `phase7-leaf-library-evidence`",
        "- phase: `Phase 7`",
        "- lane scope: shared leaf-library evidence rows and validation foothold only",
        "",
        *REQUIRED_CATALOG_SNIPPETS,
    ]) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / DOCS_README_PATH, "# Zigux Documentation\nPhase 7 notes\n")
    write(root / SCRIPTS_README_PATH, "# scripts/zigux\n\n## Phase 7\n")
    write(root / TESTS_README_PATH, "# zigux/tests\n\n## Phase 7\n")
    write(root / MANIFEST_PATH, json.dumps({
        "packet": EXPECTED_PACKET,
        "phase": EXPECTED_PHASE,
        "lane_scope": EXPECTED_SCOPE,
        "current_direct_readback_companions": EXPECTED_COMPANIONS,
        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
        "current_direct_helper_evidence": [
            {"key": key, "zig_helper": path, "expected_markers": markers}
            for key, path, markers in EXPECTED_HELPERS
        ],
        "current_replay_inventory": EXPECTED_REPLAYS,
        "current_repo_reality_gaps": EXPECTED_GAPS,
    }, indent=2) + "\n")
    marker_blocks = {}
    for _, rel_path, markers in EXPECTED_HELPERS:
        marker_blocks.setdefault(rel_path, [])
        for marker in markers:
            if marker not in marker_blocks[rel_path]:
                marker_blocks[rel_path].append(marker)
    for rel_path, markers in marker_blocks.items():
        write(root / rel_path, "\n".join(markers) + "\n")


def _mutate_text(root: Path, rel: Path, old: str, new: str, case: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    assert updated != text, case
    path.write_text(updated, encoding="utf-8")


def _append_text(root: Path, rel: Path, extra: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [(f"missing_{rel.name}", rel) for rel in REQUIRED_FILES]
    marker_cases = [
        (
            "missing_catalog_build_wiring_companion_marker",
            CATALOG_PATH,
            "- `scripts/zigux/check-phase7-build-wiring.py`",
            "- `scripts/zigux/check-phase7-build-route.py`",
        ),
        (
            "missing_catalog_validate_route_marker",
            CATALOG_PATH,
            "- `make -C zigux phase7-validate`",
            "- `make -C zigux phase7-verify`",
        ),
        (
            "missing_phase7_validate_route",
            MAKEFILE_PATH,
            "phase7-validate:",
            "phase7-verify:",
        ),
        (
            "missing_phase7_validate_run",
            MAKEFILE_PATH,
            "$(PYTHON) scripts/zigux/validate-phase7.py",
            "$(PYTHON) scripts/zigux/check-phase7-shared-surface.py",
        ),
        (
            "missing_manifest_build_wiring_companion",
            MANIFEST_PATH,
            '"scripts/zigux/check-phase7-build-wiring.py",',
            '"scripts/zigux/check-phase7-build-route.py",',
        ),
        (
            "missing_manifest_repo_gap_entry",
            MANIFEST_PATH,
            '"zigux/tests/phase7_build.zig"',
            '"zigux/tests/phase7_rbtree.zig"',
        ),
        (
            "missing_helper_parse_int_array_entry",
            MANIFEST_PATH,
            '"pub const ParseIntArrayError"',
            '"pub const ParseIntArrayMissing"',
        ),
    ]
    unexpected_marker_cases = [
        ("phase7_test_route_returned", "phase7-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig\n"),
        ("phase7_aggregate_route_returned", "phase7: phase7-validate phase7-test\n"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_shared_surface_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        scaffold_repo(root)
        validate(root)

        for case, rel in missing_file_cases:
            (root / rel).unlink()
            try:
                validate(root)
            except ValidationError:
                pass
            else:
                raise AssertionError(case)
            scaffold_repo(root)

        for case, rel, old, new in marker_cases:
            _mutate_text(root, rel, old, new, case)
            try:
                validate(root)
            except ValidationError:
                pass
            else:
                raise AssertionError(case)
            scaffold_repo(root)

        for case, extra in unexpected_marker_cases:
            _append_text(root, MAKEFILE_PATH, extra)
            try:
                validate(root)
            except ValidationError:
                pass
            else:
                raise AssertionError(case)
            scaffold_repo(root)

    print("PHASE7_SHARED_SURFACE_SELF_TEST=pass")
    print(
        "PHASE7_SHARED_SURFACE_SELF_TEST_CASE_COUNT=%d"
        % (len(missing_file_cases) + len(marker_cases) + len(unexpected_marker_cases))
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_SHARED_SURFACE=fail: {exc}")
        return 1

    print("PHASE7_SHARED_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
