#!/usr/bin/env python3
"""Guard the bounded Phase 7 shared leaf-library evidence packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")
MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
ARGV_SPLIT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")

EXPECTED_PACKET = "phase7-leaf-library-evidence"
EXPECTED_PHASE = "Phase 7"
EXPECTED_SCOPE = "shared leaf-library evidence rows and validation foothold only"
EXPECTED_COMPANIONS = [
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase7-shared-surface.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
]
EXPECTED_ROADMAP_ANCHORS = [
    "lib/string_helpers.c",
    "lib/cmdline.c",
    "lib/argv_split.c",
    "lib/rbtree.c",
]
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase7-build-wiring.py",
    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]
EXPECTED_GAPS: list[str] = []
EXPECTED_HELPERS = {
    Path("lib/string_helpers.zig"): [
        "pub const STRING_UNITS_10",
        "pub const KasprintfStrarrayResult",
        "pub fn kstrdupQuotable",
        "pub fn kstrdupQuotableCmdline",
        "pub const ParseIntArrayError",
        "pub fn parseIntArray",
    ],
    Path("lib/cmdline.zig"): ["pub fn parseOptionStr", "pub fn getOption"],
    Path("lib/argv_split.zig"): ["pub const ArgvSplitResult", "pub fn argvSplit"],
    Path("lib/rbtree.zig"): ["pub const Node = struct", "pub const RootCached = struct", "pub fn add(", "pub fn rb_find_add_cached("],
}
REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback companions",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/check-phase7-build-wiring.py`",
    "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "- `scripts/zigux/check-phase7-argv-split-packet.py`",
    "## Current repo-reality gaps",
    "- none currently",
]
REQUIRED_BUILD_SNIPPETS = [
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7-rbtree-test",
    "phase7-rbtree-survey",
]
REQUIRED_FILES = [
    REVIEW_CHECKLIST_PATH,
    CATALOG_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
    MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH,
    ARGV_SPLIT_PACKET_CHECKER_PATH,
    Path("scripts/zigux/check-phase7-build-wiring.py"),
    Path("scripts/zigux/validate-phase7.py"),
    Path("scripts/zigux/README.md"),
    Path("zigux/tests/README.md"),
    Path("lib/string_helpers.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
    Path("lib/rbtree.zig"),
]
SELF_TEST_CASE_COUNT = 6


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_snippets(path: Path, snippets: list[str]) -> None:
    text = read_text(path)
    for snippet in snippets:
        if snippet not in text:
            raise ValidationError(f"missing expected Phase 7 marker in {path.as_posix()}: {snippet}")


def validate(repo_root: Path) -> None:
    missing = [str(path) for path in REQUIRED_FILES if not (repo_root / path).is_file()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / BUILD_PATH, REQUIRED_BUILD_SNIPPETS)

    manifest = json.loads(read_text(repo_root / MANIFEST_PATH))
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

    for rel_path, markers in EXPECTED_HELPERS.items():
        helper_text = read_text(repo_root / rel_path)
        for marker in markers:
            if marker not in helper_text:
                raise ValidationError(f"phase7 helper marker missing in {rel_path.as_posix()}: {marker}")


def scaffold_repo(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST_PATH, "# Phase 7 Review Checklist\n")
    write_text(root / Path("Documentation/zigux/README.md"), "# Zigux Docs\n")
    write_text(root / Path("scripts/zigux/README.md"), "# Zigux Scripts\n")
    write_text(root / Path("zigux/tests/README.md"), "# Zigux Tests\n")
    write_text(root / MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "#!/usr/bin/env python3\nprint('PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass')\n")
    write_text(root / ARGV_SPLIT_PACKET_CHECKER_PATH, "#!/usr/bin/env python3\nprint('PHASE7_ARGV_SPLIT_PACKET=pass')\n")
    write_text(root / Path("scripts/zigux/check-phase7-build-wiring.py"), "#!/usr/bin/env python3\nprint('PHASE7_BUILD_WIRING=pass')\n")
    write_text(root / Path("scripts/zigux/validate-phase7.py"), "#!/usr/bin/env python3\nprint('PHASE7_VALIDATE=pass')\n")
    write_text(root / CATALOG_PATH, "\n".join([
        "- packet: `phase7-leaf-library-evidence`",
        "- phase: `Phase 7`",
        "- lane scope: shared leaf-library evidence rows and validation foothold only",
        "",
        *REQUIRED_CATALOG_SNIPPETS,
    ]) + "\n")
    write_text(root / MAKEFILE_PATH, "phase7-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n")
    write_text(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    for rel_path, markers in EXPECTED_HELPERS.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": EXPECTED_SCOPE,
                "current_direct_readback_companions": EXPECTED_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_replay_inventory": EXPECTED_REPLAYS,
                "current_repo_reality_gaps": EXPECTED_GAPS,
            },
            indent=2,
        ) + "\n",
    )


def expect_failure(root: Path, rel_path: Path, old: str | None = None, new: str = "") -> None:
    if old is None:
        (root / rel_path).unlink()
    else:
        path = root / rel_path
        text = read_text(path)
        updated = text.replace(old, new, 1)
        if updated == text:
            raise AssertionError(f"marker not found: {old}")
        write_text(path, updated)
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_shared_surface_") as tmp_dir:
        root = Path(tmp_dir)
        scaffold_repo(root)
        validate(root)

        for rel_path, old, new in [
            (REVIEW_CHECKLIST_PATH, None, ""),
            (MANIFEST_PATH, '"Documentation/zigux/review-checklist.md",', '"Documentation/zigux/review-notes.md",'),
            (CATALOG_PATH, "- `Documentation/zigux/review-checklist.md`", "- `Documentation/zigux/review-notes.md`"),
            (BUILD_PATH, "phase7-rbtree-test", "phase7-rbtree-helper"),
            (Path("lib/rbtree.zig"), "pub fn rb_find_add_cached(", "pub fn rb_find_add_helper("),
            (MANIFEST_PATH, '"make -C zigux phase7-validate"', '"make -C zigux phase7-test"'),
        ]:
            scaffold_repo(root)
            expect_failure(root, rel_path, old, new)
            cases += 1

    if cases != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases}")
    print("PHASE7_SHARED_SURFACE_SELF_TEST=pass")
    print(f"PHASE7_SHARED_SURFACE_SELF_TEST_CASE_COUNT={cases}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            return 0
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_SHARED_SURFACE=fail: {exc}")
        return 1
    print("PHASE7_SHARED_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
