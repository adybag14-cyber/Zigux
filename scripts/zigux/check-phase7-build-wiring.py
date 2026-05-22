#!/usr/bin/env python3
"""Check that the current Phase 7 build-wiring packet matches current master."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")
RBTREE_PATH = Path("lib/rbtree.zig")

EXPECTED_PACKET = "phase7-leaf-library-evidence"
EXPECTED_PHASE = "Phase 7"
EXPECTED_SCOPE = "shared leaf-library evidence rows and validation foothold only"
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase7-build-wiring.py",
    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]
EXPECTED_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/check-phase7-shared-surface.py",
    "scripts/zigux/check-phase7-build-wiring.py",
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
EXPECTED_HELPER_EVIDENCE = [
    {
        "key": "string_helpers",
        "zig_helper": "lib/string_helpers.zig",
        "expected_markers": [
            "pub const STRING_UNITS_10",
            "pub const KasprintfStrarrayResult",
            "pub fn kstrdupQuotable",
            "pub fn kstrdupQuotableCmdline",
        ],
    },
    {
        "key": "string_helpers_parse_int_array",
        "zig_helper": "lib/string_helpers.zig",
        "expected_markers": [
            "pub const ParseIntArrayError",
            "pub fn parseIntArray",
        ],
    },
    {
        "key": "cmdline",
        "zig_helper": "lib/cmdline.zig",
        "expected_markers": [
            "pub fn parseOptionStr",
            "pub fn getOption",
        ],
    },
    {
        "key": "argv_split",
        "zig_helper": "lib/argv_split.zig",
        "expected_markers": [
            "pub const ArgvSplitResult",
            "pub fn argvSplit",
        ],
    },
    {
        "key": "rbtree",
        "zig_helper": "lib/rbtree.zig",
        "expected_markers": [
            "pub const Node = struct",
            "pub const RootCached = struct",
            "pub fn add(",
            "pub fn rb_find_add_cached(",
        ],
    },
]
EXPECTED_BUILD_WIRING_EVIDENCE = [
    {
        "path": "zigux/tests/phase7_build.zig",
        "expected_markers": [
            "../../lib/string_helpers.zig",
            "../../lib/cmdline.zig",
            "../../lib/argv_split.zig",
            "../../lib/rbtree.zig",
            "phase7-string-helpers-test",
            "phase7-cmdline-test",
            "phase7-argv-split-test",
            "phase7-rbtree-test",
            "phase7-rbtree-survey",
        ],
    },
    {
        "path": "zigux/Makefile",
        "expected_markers": [
            "phase7-validate:",
            "$(PYTHON) scripts/zigux/validate-phase7.py --self-test",
            "$(PYTHON) scripts/zigux/validate-phase7.py",
        ],
    },
]
EXPECTED_REPO_GAPS: list[str] = []

REQUIRED_FILES = (
    VALIDATOR_PATH,
    CATALOG_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
    RBTREE_PATH,
)

CATALOG_REQUIRED_SNIPPETS = [
    "## Current direct-readback companions",
    "- `zigux/tests/phase7_build.zig`",
    "- `lib/rbtree.zig`",
    "## Current replay inventory",
    "- `python3 scripts/zigux/check-phase7-build-wiring.py`",
    "- `make -C zigux phase7-validate`",
    "## Current build-wiring evidence",
    "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.",
    "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
    "## Current repo-reality gaps",
    "- none currently",
]

VALIDATOR_REQUIRED_SNIPPETS = [
    "phase7 build-wiring evidence drift",
    "phase7 build marker missing: ../../lib/rbtree.zig",
    "phase7 build marker missing: phase7-rbtree-test",
]

MAKEFILE_REQUIRED_LINES = [
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase7-test:",
    "phase7:",
]
MAKEFILE_FORBIDDEN_LINES = FORBIDDEN_MAKEFILE_MARKERS

BUILD_REQUIRED_SNIPPETS = [
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7-rbtree-test",
    "phase7-rbtree-survey",
]

RBTREE_REQUIRED_SNIPPETS = [
    "pub const Node = struct",
    "pub const RootCached = struct",
    "pub fn add(",
    "pub fn rb_find_add_cached(",
]

SELF_TEST_CASE_COUNT = 5


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def require_snippets(path: Path, snippets: list[str]) -> None:
    text = read_text(path)
    for snippet in snippets:
        if snippet not in text:
            raise ValidationError(f"missing expected marker in {path.as_posix()}: {snippet}")


def require_exact_lines(path: Path, markers: list[str]) -> None:
    text = read_text(path)
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            raise ValidationError(f"missing expected line in {path.as_posix()}: {marker}")
        if count != 1:
            raise ValidationError(f"duplicate expected line in {path.as_posix()}: {marker}")


def require_absent_lines(path: Path, markers: list[str]) -> None:
    text = read_text(path)
    for marker in markers:
        if count_exact_lines(text, marker):
            raise ValidationError(f"unexpected stale line in {path.as_posix()}: {marker}")


def validate(root: Path) -> None:
    missing = [str(rel) for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    require_snippets(root / CATALOG_PATH, CATALOG_REQUIRED_SNIPPETS)
    require_snippets(root / VALIDATOR_PATH, VALIDATOR_REQUIRED_SNIPPETS)
    require_exact_lines(root / MAKEFILE_PATH, MAKEFILE_REQUIRED_LINES)
    require_absent_lines(root / MAKEFILE_PATH, MAKEFILE_FORBIDDEN_LINES)
    require_snippets(root / BUILD_PATH, BUILD_REQUIRED_SNIPPETS)
    require_snippets(root / RBTREE_PATH, RBTREE_REQUIRED_SNIPPETS)

    manifest = read_json(root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase7 packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase7 phase drift")
    if manifest.get("lane_scope") != EXPECTED_SCOPE:
        raise ValidationError("phase7 lane scope drift")
    if manifest.get("current_replay_inventory") != EXPECTED_REPLAYS:
        raise ValidationError("phase7 replay inventory drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_DIRECT_COMPANIONS:
        raise ValidationError("phase7 direct companion drift")
    if manifest.get("current_direct_helper_evidence") != EXPECTED_HELPER_EVIDENCE:
        raise ValidationError("phase7 helper evidence drift")
    if manifest.get("current_build_wiring_evidence") != EXPECTED_BUILD_WIRING_EVIDENCE:
        raise ValidationError("phase7 build-wiring evidence drift")
    if manifest.get("current_repo_reality_gaps") != EXPECTED_REPO_GAPS:
        raise ValidationError("phase7 repo-reality gap drift")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_root(root: Path) -> None:
    write(
        root / VALIDATOR_PATH,
        "\n".join(
            [
                "phase7 build-wiring evidence drift",
                "phase7 build marker missing: ../../lib/rbtree.zig",
                "phase7 build marker missing: phase7-rbtree-test",
            ]
        )
        + "\n",
    )
    write(
        root / CATALOG_PATH,
        "\n".join(CATALOG_REQUIRED_SNIPPETS) + "\n",
    )
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": EXPECTED_SCOPE,
                "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS,
                "current_direct_helper_evidence": EXPECTED_HELPER_EVIDENCE,
                "current_build_wiring_evidence": EXPECTED_BUILD_WIRING_EVIDENCE,
                "current_replay_inventory": EXPECTED_REPLAYS,
                "current_repo_reality_gaps": EXPECTED_REPO_GAPS,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                "phase7-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
            ]
        )
        + "\n",
    )
    write(root / BUILD_PATH, "\n".join(BUILD_REQUIRED_SNIPPETS) + "\n")
    write(root / RBTREE_PATH, "\n".join(RBTREE_REQUIRED_SNIPPETS) + "\n")


def expect_failure(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = read_text(path)
    updated = text.replace(old, new, 1)
    if updated == text:
        raise AssertionError(f"marker not found for mutation: {old}")
    write(path, updated)
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmpdir:
        root = Path(tmpdir)
        build_fixture_root(root)
        validate(root)

        mutations = [
            (CATALOG_PATH, "- `lib/rbtree.zig`", "- `tools/lib/rbtree.zig`"),
            (CATALOG_PATH, "- none currently", "- `lib/rbtree.zig`"),
            (MAKEFILE_PATH, "phase7-validate:", "phase7-verify:"),
            (BUILD_PATH, "../../lib/rbtree.zig", "../../tools/lib/rbtree.zig"),
            (BUILD_PATH, "phase7-rbtree-test", "phase7-rbtree-helper"),
        ]
        for rel, old, new in mutations:
            build_fixture_root(root)
            expect_failure(root, rel, old, new)
            cases += 1

    if cases != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases}")
    print("PHASE7_BUILD_WIRING_SELF_TEST=pass")
    print(f"PHASE7_BUILD_WIRING_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 7 build-wiring reminder matches the returned leaf-library packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_BUILD_WIRING=fail: {exc}")
        return 1

    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_BUILD_WIRING_REPLAY_COUNT={len(EXPECTED_REPLAYS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
