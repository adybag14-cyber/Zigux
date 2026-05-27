#!/usr/bin/env python3
"""Guard the bounded Phase 7 shared leaf-library evidence packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")
MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
CMDLINE_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-cmdline-packet.py")
ARGV_SPLIT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")
STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH = Path(
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py"
)
RBTREE_PARITY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-rbtree-parity.py")

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
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
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
EXPECTED_GAPS = [
    "shared `Documentation/zigux/README.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory",
    "shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory",
]
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase7-build-wiring.py",
    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase7-cmdline-packet.py",
    "python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
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
    (
        "rbtree",
        "lib/rbtree.zig",
        ["pub const Node = struct", "pub const RootCached = struct", "pub fn add(", "pub fn rb_find_add_cached("],
    ),
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
            "phase7-string-helpers-survey",
            "phase7-string-helpers-sample-boundary",
            "phase7-string-helpers-format-boundary",
            "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
            "phase7-cmdline-test",
            "phase7-cmdline-survey",
            "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)",
            "phase7-argv-split-test",
            "phase7-argv-split-survey",
            "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)",
            "phase7-rbtree-test",
            "phase7-rbtree-survey",
            'const test_step = b.step("test", "Run the Phase 7 runtime helper tests");',
            "test_step.dependOn(&run_string_helpers_tests.step)",
            "test_step.dependOn(&run_string_helpers_survey_tests.step)",
            "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
            "test_step.dependOn(&run_cmdline_tests.step)",
            "test_step.dependOn(&run_cmdline_survey_tests.step)",
            "test_step.dependOn(&run_argv_split_tests.step)",
            "test_step.dependOn(&run_argv_split_survey_tests.step)",
            "test_step.dependOn(&run_rbtree_tests.step)",
            "test_step.dependOn(&run_rbtree_survey_tests.step)",
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
REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback companions",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/check-phase7-build-wiring.py`",
    "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "- `scripts/zigux/check-phase7-cmdline-packet.py`",
    "- `scripts/zigux/check-phase7-argv-split-packet.py`",
    "- `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`",
    "- `scripts/zigux/check-phase7-rbtree-parity.py`",
    "- `scripts/zigux/README.md`",
    "- `zigux/tests/README.md`",
    "- `zigux/tests/phase7_build.zig`",
    "- `lib/rbtree.zig`",
    "## Current replay inventory",
    "- `python3 scripts/zigux/check-phase7-build-wiring.py`",
    "- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "- `python3 scripts/zigux/check-phase7-cmdline-packet.py`",
    "- `python3 scripts/zigux/check-phase7-argv-split-packet.py`",
    "- `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`",
    "- `python3 scripts/zigux/check-phase7-rbtree-parity.py`",
    "- `make -C zigux phase7-validate`",
    "## Current build-wiring evidence",
    "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.",
    "- `zigux/tests/phase7_build.zig` still exposes the dedicated helper, survey, sample-boundary, and format-boundary routes through `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-string-helpers-format-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey`.",
    "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.",
    "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
    "## Current repo-reality gaps",
    "- shared `Documentation/zigux/README.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory",
    "- shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory",
]
REQUIRED_DOCS_README_SNIPPETS = [
    "Phase 7 notes - `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
    "* `zigux/tests/phase7_build.zig` keeps `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` wired through the dedicated helper, survey, sample-boundary, and format-boundary routes plus the shared `test` step, while `zigux/Makefile` keeps only the narrow `make -C zigux phase7-validate` foothold explicit and leaves broader wrapper routes outside this packet.",
    "* `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` replay the bounded current Phase 7 docs-root reminder packet without widening it into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes.",
]
REQUIRED_REVIEW_CHECKLIST_SNIPPETS = [
    "* if the change touches the shared Phase 7 leaf-library packet, do `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase7-shared-surface.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_leaf_library_evidence_manifest.json`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig` still agree on the current bounded Phase 7 packet, keep the returned helper-anchor set and shared build-wiring packet explicit, keep `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` explicit as the current bounded replay surfaces, and keep broader wrapper families or deeper runtime validation claims out of the Phase 7 reminder packet?",
]
REQUIRED_SCRIPTS_README_SNIPPETS = [
    "- Phase 7 flow - the current scripts-root leaf-library packet stays reviewable through the returned leaf-library evidence catalog, the shared docs-root and tests-root reminder packet, the shipped shared-surface, build-wiring, make-wrapper self-test alignment, dedicated `cmdline`, `argv_split`, `string_helpers` format-boundary, and `rbtree` parity guards, the validator entrypoint, the shared machine-readable manifest, the shared build graph, the narrow `phase7-validate` wrapper foothold, and the four roadmap-backed helper anchors instead of reopening helper semantics or reconstructing a broader missing-wrapper story",
    "- `python3 scripts/zigux/check-phase7-shared-surface.py --self-test`, `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`, `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test`, `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`, and `python3 scripts/zigux/validate-phase7.py --self-test` replay the shipped shared Phase 7 scripts-root reminder guards",
]
REQUIRED_TESTS_README_SNIPPETS = [
    "## Phase 7 leaf-library packet",
    "Keep the validator-first reminder packet explicit too: `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-cmdline-packet.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/check-phase7-rbtree-parity.py`, `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`, `python3 scripts/zigux/validate-phase7.py`, `python3 scripts/zigux/validate-phase7.py --self-test`, and `make -C zigux phase7-validate` remain the shipped bounded replay surfaces, and `zigux/Makefile` still keeps only the narrow `phase7-validate` foothold explicit rather than a broader wrapper family.",
]
REQUIRED_MAKEFILE_SNIPPETS = [
    "phase7-validate:",
    "$(PYTHON) scripts/zigux/validate-phase7.py",
]
REQUIRED_BUILD_SNIPPETS = [
    "../../lib/rbtree.zig",
    "phase7-string-helpers-format-boundary",
    "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
    "phase7-rbtree-test",
    "phase7-rbtree-survey",
    'const test_step = b.step("test", "Run the Phase 7 runtime helper tests");',
    "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
]
REQUIRED_FILES = [
    CATALOG_PATH,
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
    MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH,
    CMDLINE_PACKET_CHECKER_PATH,
    ARGV_SPLIT_PACKET_CHECKER_PATH,
    STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH,
    RBTREE_PARITY_PACKET_CHECKER_PATH,
    Path("lib/string_helpers.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
    Path("lib/rbtree.zig"),
]
SELF_TEST_CASE_COUNT = 54

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
    require_snippets(repo_root / DOCS_README_PATH, REQUIRED_DOCS_README_SNIPPETS)
    require_snippets(repo_root / REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_SNIPPETS)
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_SNIPPETS)
    require_snippets(repo_root / TESTS_README_PATH, REQUIRED_TESTS_README_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(repo_root / BUILD_PATH, REQUIRED_BUILD_SNIPPETS)

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
    expected_helpers = [
        {"key": key, "zig_helper": path, "expected_markers": markers}
        for key, path, markers in EXPECTED_HELPERS
    ]
    if helpers != expected_helpers:
        raise ValidationError("phase7 helper evidence ordering drift")
    if manifest.get("current_build_wiring_evidence") != EXPECTED_BUILD_WIRING_EVIDENCE:
        raise ValidationError("phase7 build-wiring evidence mismatch")

    for key, rel_path, markers in EXPECTED_HELPERS:
        content = read_text(repo_root / rel_path)
        for marker in markers:
            if marker not in content:
                raise ValidationError(f"phase7 helper marker missing for {key}: {marker}")

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def scaffold_repo(root: Path) -> None:
    write(
        root / CATALOG_PATH,
        "\n".join([
            "- packet: `phase7-leaf-library-evidence`",
            "- phase: `Phase 7`",
            "- lane scope: shared leaf-library evidence rows and validation foothold only",
            "",
            *REQUIRED_CATALOG_SNIPPETS,
        ]) + "\n",
    )
    write(root / DOCS_README_PATH, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
    write(root / REVIEW_CHECKLIST_PATH, "\n".join(REQUIRED_REVIEW_CHECKLIST_SNIPPETS) + "\n")
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n")
    write(root / TESTS_README_PATH, "\n".join(REQUIRED_TESTS_README_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "#!/usr/bin/env python3\nprint('PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass')\n")
    write(root / CMDLINE_PACKET_CHECKER_PATH, "#!/usr/bin/env python3\nprint('PHASE7_CMDLINE_PACKET=pass')\n")
    write(root / ARGV_SPLIT_PACKET_CHECKER_PATH, "#!/usr/bin/env python3\nprint('PHASE7_ARGV_SPLIT_PACKET=pass')\n")
    write(
        root / STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\nprint('PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass')\n",
    )
    write(root / RBTREE_PARITY_PACKET_CHECKER_PATH, "#!/usr/bin/env python3\nprint('PHASE7_RBTREE_PARITY=pass')\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": EXPECTED_SCOPE,
                "current_direct_readback_companions": EXPECTED_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_direct_helper_evidence": [
                    {"key": key, "zig_helper": path, "expected_markers": markers}
                    for key, path, markers in EXPECTED_HELPERS
                ],
                "current_build_wiring_evidence": EXPECTED_BUILD_WIRING_EVIDENCE,
                "current_replay_inventory": EXPECTED_REPLAYS,
                "current_repo_reality_gaps": EXPECTED_GAPS,
            },
            indent=2,
        ) + "\n",
    )
    marker_blocks: dict[str, list[str]] = {}
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

def run_self_test() -> None:
    missing_file_cases = [(f"missing_{rel.name}", rel) for rel in REQUIRED_FILES]
    marker_cases = [
        ("missing_docs_readme_phase7_section", DOCS_README_PATH, "Phase 7 notes - `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`", "Phase 6 notes - `Documentation/zigux/phase6-helper-evidence-catalog.md`"),
        ("missing_docs_readme_phase7_build_route_sentence", DOCS_README_PATH, "* `zigux/tests/phase7_build.zig` keeps `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` wired through the dedicated helper, survey, sample-boundary, and format-boundary routes plus the shared `test` step, while `zigux/Makefile` keeps only the narrow `make -C zigux phase7-validate` foothold explicit and leaves broader wrapper routes outside this packet.", "* `zigux/tests/phase7_build.zig` keeps `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` wired through the dedicated helper, survey, and sample-boundary routes plus the shared `test` step, while `zigux/Makefile` keeps only the narrow `make -C zigux phase7-validate` foothold explicit and leaves broader wrapper routes outside this packet."),
        ("missing_docs_readme_phase7_validate_sentence", DOCS_README_PATH, "* `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` replay the bounded current Phase 7 docs-root reminder packet without widening it into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes.", "* `python3 scripts/zigux/check-phase7-shared-surface.py` and `python3 scripts/zigux/validate-phase7.py` replay the bounded current Phase 7 docs-root reminder packet."),
        ("missing_review_checklist_phase7_packet_question", REVIEW_CHECKLIST_PATH, "* if the change touches the shared Phase 7 leaf-library packet, do `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase7-shared-surface.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_leaf_library_evidence_manifest.json`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig` still agree on the current bounded Phase 7 packet, keep the returned helper-anchor set and shared build-wiring packet explicit, keep `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` explicit as the current bounded replay surfaces, and keep broader wrapper families or deeper runtime validation claims out of the Phase 7 reminder packet?", "* if the change touches the shared Phase 7 leaf-library packet, do the current docs and scripts still agree on the packet?"),
        ("missing_scripts_readme_phase7_flow", SCRIPTS_README_PATH, "- Phase 7 flow - the current scripts-root leaf-library packet stays reviewable through the returned leaf-library evidence catalog, the shared docs-root and tests-root reminder packet, the shipped shared-surface, build-wiring, make-wrapper self-test alignment, dedicated `cmdline`, `argv_split`, `string_helpers` format-boundary, and `rbtree` parity guards, the validator entrypoint, the shared machine-readable manifest, the shared build graph, the narrow `phase7-validate` wrapper foothold, and the four roadmap-backed helper anchors instead of reopening helper semantics or reconstructing a broader missing-wrapper story", "- Phase 7 flow - the current scripts-root leaf-library packet stays reviewable through the validator entrypoint and helper anchors."),
        ("missing_scripts_readme_phase7_selftests", SCRIPTS_README_PATH, "- `python3 scripts/zigux/check-phase7-shared-surface.py --self-test`, `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`, `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test`, `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`, and `python3 scripts/zigux/validate-phase7.py --self-test` replay the shipped shared Phase 7 scripts-root reminder guards", "- `python3 scripts/zigux/validate-phase7.py --self-test` replays the shipped shared Phase 7 scripts-root reminder guards"),
        ("missing_tests_readme_phase7_heading", TESTS_README_PATH, "## Phase 7 leaf-library packet", "## Phase 7 packet"),
        ("missing_tests_readme_phase7_validate_sentence", TESTS_README_PATH, "Keep the validator-first reminder packet explicit too: `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-cmdline-packet.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/check-phase7-rbtree-parity.py`, `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`, `python3 scripts/zigux/validate-phase7.py`, `python3 scripts/zigux/validate-phase7.py --self-test`, and `make -C zigux phase7-validate` remain the shipped bounded replay surfaces, and `zigux/Makefile` still keeps only the narrow `phase7-validate` foothold explicit rather than a broader wrapper family.", "Keep the validator-first reminder packet explicit too: `python3 scripts/zigux/validate-phase7.py` remains the shipped bounded replay surface."),
        ("missing_catalog_build_wiring_companion_marker", CATALOG_PATH, "- `scripts/zigux/check-phase7-build-wiring.py`", "- `scripts/zigux/check-phase7-build-route.py`"),
        ("missing_catalog_make_wrapper_companion_marker", CATALOG_PATH, "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`", "- `scripts/zigux/check-phase7-make-wrapper.py`"),
        ("missing_catalog_format_boundary_companion_marker", CATALOG_PATH, "- `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`", "- `scripts/zigux/check-phase7-string-helpers-sample-boundary-packet.py`"),
        ("missing_catalog_rbtree_marker", CATALOG_PATH, "- `lib/rbtree.zig`", "- `tools/lib/rbtree.zig`"),
        ("missing_catalog_docs_readme_gap_marker", CATALOG_PATH, "- shared `Documentation/zigux/README.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory", "- shared `Documentation/zigux/README.md` Phase 7 reminder text is fully aligned with the current packet inventory"),
        ("missing_catalog_review_checklist_gap_marker", CATALOG_PATH, "- shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory", "- shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text is fully aligned with the current packet inventory"),
        ("missing_catalog_build_graph_sentence", CATALOG_PATH, "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.", "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig` and `../../lib/cmdline.zig` into the shared Phase 7 build graph."),
        ("missing_catalog_dedicated_route_sentence", CATALOG_PATH, "- `zigux/tests/phase7_build.zig` still exposes the dedicated helper, survey, sample-boundary, and format-boundary routes through `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-string-helpers-format-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey`.", "- `zigux/tests/phase7_build.zig` still exposes the dedicated helper routes through `phase7-string-helpers-test`, `phase7-cmdline-test`, `phase7-argv-split-test`, and `phase7-rbtree-test`."),
        ("missing_catalog_shared_test_step_sentence", CATALOG_PATH, "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.", "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper replay through the current `test_step.dependOn(...)` handoff list."),
        ("missing_catalog_phase7_validate_sentence", CATALOG_PATH, "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.", "- `zigux/Makefile` keeps the shared Phase 7 routes explicit while broader wrapper routes remain outside this packet."),
        ("missing_phase7_validate_route", MAKEFILE_PATH, "phase7-validate:", "phase7-verify:"),
        ("missing_phase7_validate_run", MAKEFILE_PATH, "$(PYTHON) scripts/zigux/validate-phase7.py", "$(PYTHON) scripts/zigux/check-phase7-shared-surface.py"),
        ("missing_manifest_build_wiring_companion", MANIFEST_PATH, '\"scripts/zigux/check-phase7-build-wiring.py\",', '\"scripts/zigux/check-phase7-build-route.py\",'),
        ("missing_manifest_make_wrapper_companion", MANIFEST_PATH, '\"scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py\",', '\"scripts/zigux/check-phase7-make-wrapper.py\",'),
        ("missing_manifest_format_boundary_companion", MANIFEST_PATH, '\"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py\",', '\"scripts/zigux/check-phase7-string-helpers-sample-boundary-packet.py\",'),
        ("missing_manifest_build_file_companion", MANIFEST_PATH, '\"zigux/tests/phase7_build.zig\",', '\"zigux/tests/phase7_rbtree.zig\",'),
        ("missing_manifest_rbtree_helper_entry", MANIFEST_PATH, '\"lib/rbtree.zig\"', '\"tools/lib/rbtree.zig\"'),
        ("missing_manifest_build_wiring_evidence", MANIFEST_PATH, '\"phase7-rbtree-test\"', '\"phase7-rbtree-helper\"'),
        ("missing_build_rbtree_import", BUILD_PATH, "../../lib/rbtree.zig", "../../tools/lib/rbtree.zig"),
        ("missing_build_format_boundary_step", BUILD_PATH, "phase7-string-helpers-format-boundary", "phase7-string-helpers-format-gap"),
        ("missing_build_format_boundary_dependson", BUILD_PATH, "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)", "string_helpers_format_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)"),
        ("missing_build_rbtree_test_route", BUILD_PATH, "phase7-rbtree-test", "phase7-rbtree-helper"),
        ("missing_build_rbtree_survey_route", BUILD_PATH, "phase7-rbtree-survey", "phase7-rbtree-gap"),
        ("missing_build_shared_test_route", BUILD_PATH, 'const test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");', 'const test_step = b.step(\"phase7-test\", \"Run the Phase 7 runtime helper tests\");'),
        ("missing_build_shared_test_dependson", BUILD_PATH, "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)", "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)"),
        ("missing_string_helpers_marker", Path("lib/string_helpers.zig"), "pub fn kstrdupQuotableCmdline", "pub fn kstrdupQuotedCmdline"),
        ("missing_cmdline_marker", Path("lib/cmdline.zig"), "pub fn getOption", "pub fn readOption"),
        ("missing_argv_split_marker", Path("lib/argv_split.zig"), "pub fn argvSplit", "pub fn splitArgv"),
        ("missing_rbtree_marker", Path("lib/rbtree.zig"), "pub fn rb_find_add_cached(", "pub fn rb_find_cached("),
    ]

    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_shared_surface_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        for case, rel in missing_file_cases:
            scaffold_repo(root)
            (root / rel).unlink()
            try:
                validate(root)
            except ValidationError:
                cases += 1
                continue
            raise AssertionError(case)

        for case, rel, old, new in marker_cases:
            scaffold_repo(root)
            _mutate_text(root, rel, old, new, case)
            try:
                validate(root)
            except ValidationError:
                cases += 1
                continue
            raise AssertionError(case)

    if cases != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases}")
    print("PHASE7_SHARED_SURFACE_SELF_TEST=pass")
    print(f"PHASE7_SHARED_SURFACE_SELF_TEST_CASE_COUNT={cases}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Guard the bounded Phase 7 shared leaf-library evidence packet.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_SHARED_SURFACE=fail: {exc}")
        return 1

    print("PHASE7_SHARED_SURFACE=pass")
    print(f"PHASE7_SHARED_SURFACE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_SHARED_SURFACE_REPLAY_COUNT={len(EXPECTED_REPLAYS)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())