#!/usr/bin/env python3
"""Guard the current Phase 6 manifest-backed direct entrypoints."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOCS_README_PATH = Path("Documentation/zigux/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
SURVEY_PATH = Path("Documentation/zigux/phase6-runtime-command-environment-gap-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_PARITY_FOLLOW_THROUGH_GAPS: list[str] = []
EXPECTED_HELPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_CURRENT_REPO_REALITY_GAPS: list[str] = []
EXPECTED_PUBLIC_TREE_COMPANIONS: list[str] = []
EXPECTED_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_SHARED_DIRECT_EVIDENCE = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_DOCS_README_SNIPPETS = [
    "- `Documentation/zigux/phase6-helper-evidence-catalog.md` - `Documentation/zigux/phase6-helper-parity-catalog.md` - `Documentation/zigux/phase6-perf-gate-survey.md`",
    "* current `master` directly serves the four roadmap-backed helper anchors through `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`",
    "* authenticated current-master rereads now directly recover both `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`",
]
EXPECTED_CATALOG_SNIPPETS = [
    "- surveyed head: `current-master-readback-2026-05-22`",
    "Authenticated current-master rereads now directly recover `Documentation/zigux/phase6-perf-gate-survey.md`",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the Phase 6 base64 packet no longer carries a known direct-readback generator gap.",
]
EXPECTED_SURVEY_SNIPPETS = [
    "This note records the bounded control-surface gap between the Phase 6 Zigux roadmap packet and the much broader runtime command, session, and persisted environment surfaces described in the attached ZAR runtime references.",
    "That is a runtime command substrate, not a Phase 6 leaf-helper replay.",
    "Do not use it to claim that Zigux Phase 6 has already landed:",
    "- shell execution semantics",
    "- TTY session control",
    "- runtime RPC/session control",
    "- persisted workspace or app-runtime environment orchestration",
]
REQUIRED_BUILD_SNIPPETS = [
    'const bsearch_perf_root_module = b.createModule(.{',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    'const checksum_perf_matrix_test_step = b.step(',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
]
REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-bsearch-perf:",
    "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf-matrix-test:",
    "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "phase6-hexdump-perf:",
]
EXPECTED_BASE64_CASES = ["STD_PAD", "STD_NO_PAD", "URLSAFE_PAD", "URLSAFE_NO_PAD", "IMAP_PAD", "IMAP_NO_PAD"]
EXPECTED_BASE64_RERUN_ROUTES = [
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_BASE64_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-base64-corpus-determinism.py",
    "scripts/zigux/check-phase6-base64-c-parity.py",
]
EXPECTED_BSEARCH_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "scripts/zigux/check-phase6-bsearch-c-parity.py",
]
EXPECTED_BSEARCH_CASES = ["len15", "len64", "len1024"]
EXPECTED_BSEARCH_RERUN_ROUTES = [
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_BSEARCH_C_ABI_REPLAYS = [
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
]
EXPECTED_CHECKSUM_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]
EXPECTED_CHECKSUM_PAYLOAD_CASES = [
    {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
    {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
]
EXPECTED_CHECKSUM_FAST_PATH_CASES = [
    {"label": "IPV4_20B", "iterations": 600000, "max_slowdown_pct": 100},
    {"label": "IPV4_20B_UPDATED", "iterations": 600000, "max_slowdown_pct": 100},
    {"label": "IPV4_24B", "iterations": 500000, "max_slowdown_pct": 100},
    {"label": "IPV4_60B", "iterations": 250000, "max_slowdown_pct": 100},
]
EXPECTED_CHECKSUM_RERUN_ROUTES = [
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_HEXDUMP_EVIDENCE_RERUN_ROUTES = [
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_PARITY_RERUN_ROUTES = [
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_PERF_CASES = [
    {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
    {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
]
EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS = [
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
]
SELF_TEST_CASE_COUNT = 32


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        parsed = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return parsed


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def get_helper(helpers: object, key: str) -> dict[str, object]:
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helpers list missing")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper row: {key}")


def require_list_contains(values: object, expected_items: list[str], label: str) -> None:
    if not isinstance(values, list):
        raise ValidationError(f"{label} missing")
    missing = [item for item in expected_items if item not in values]
    if missing:
        raise ValidationError(f"{label} missing expected items: {', '.join(missing)}")


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / DOCS_README_PATH, EXPECTED_DOCS_README_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, EXPECTED_CATALOG_SNIPPETS)
    require_snippets(repo_root / SURVEY_PATH, EXPECTED_SURVEY_SNIPPETS)
    require_snippets(repo_root / BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)

    manifest = read_json(repo_root / MANIFEST_PATH)
    parity = read_json(repo_root / PARITY_MANIFEST_PATH)

    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase6 helper-evidence packet drift")
    if parity.get("packet") != EXPECTED_PARITY_PACKET:
        raise ValidationError("phase6 helper-parity packet drift")
    if manifest.get("phase") != EXPECTED_PHASE or parity.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 phase drift")
    if manifest.get("lane_scope") != EXPECTED_LANE_SCOPE:
        raise ValidationError("phase6 helper-evidence lane-scope drift")
    if parity.get("lane_scope") != EXPECTED_PARITY_LANE_SCOPE:
        raise ValidationError("phase6 helper-parity lane-scope drift")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("phase6 helper-evidence surveyed-head drift")
    if parity.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("phase6 helper-parity surveyed-head drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_DIRECT_COMPANIONS:
        raise ValidationError("phase6 direct-readback companions mismatch")
    if manifest.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_COMPANIONS:
        raise ValidationError("phase6 public-tree companions mismatch")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 roadmap anchors mismatch")
    if manifest.get("current_repo_reality_gaps") != EXPECTED_CURRENT_REPO_REALITY_GAPS:
        raise ValidationError("phase6 repo-reality gaps mismatch")
    if parity.get("shared_direct_evidence") != EXPECTED_SHARED_DIRECT_EVIDENCE:
        raise ValidationError("phase6 parity shared direct evidence mismatch")
    if parity.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_COMPANIONS:
        raise ValidationError("phase6 parity public-tree companions mismatch")
    if parity.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 parity roadmap anchors mismatch")
    if parity.get("shared_follow_through_gaps") != EXPECTED_PARITY_FOLLOW_THROUGH_GAPS:
        raise ValidationError("phase6 parity follow-through gaps mismatch")

    helpers = manifest.get("helpers")
    parity_helpers = parity.get("helpers")
    if [helper.get("key") for helper in helpers if isinstance(helper, dict)] != EXPECTED_HELPER_KEYS:
        raise ValidationError("phase6 helper key order mismatch")
    if [helper.get("key") for helper in parity_helpers if isinstance(helper, dict)] != EXPECTED_HELPER_KEYS:
        raise ValidationError("phase6 parity helper key order mismatch")

    base64_evidence = get_helper(helpers, "base64")
    if base64_evidence.get("checker_surfaces") != EXPECTED_BASE64_CHECKER_SURFACES:
        raise ValidationError("phase6 base64 checker surfaces mismatch")

    base64_parity = get_helper(parity_helpers, "base64")
    if base64_parity.get("checker_surfaces") != EXPECTED_BASE64_CHECKER_SURFACES:
        raise ValidationError("phase6 parity base64 checker surfaces mismatch")
    base64_perf = base64_parity.get("current_perf_evidence")
    if not isinstance(base64_perf, dict):
        raise ValidationError("phase6 base64 perf evidence missing")
    if base64_perf.get("case_labels") != EXPECTED_BASE64_CASES:
        raise ValidationError("phase6 base64 perf labels mismatch")
    if base64_perf.get("iterations") != 12000:
        raise ValidationError("phase6 base64 perf iterations mismatch")
    if base64_perf.get("max_encode_slowdown_pct") != 150:
        raise ValidationError("phase6 base64 encode threshold mismatch")
    if base64_perf.get("max_decode_slowdown_pct") != 325:
        raise ValidationError("phase6 base64 decode threshold mismatch")
    if base64_perf.get("linux_style_rerun_routes") != EXPECTED_BASE64_RERUN_ROUTES:
        raise ValidationError("phase6 base64 rerun routes mismatch")

    bsearch = get_helper(helpers, "bsearch")
    if bsearch.get("checker_surfaces") != EXPECTED_BSEARCH_CHECKER_SURFACES:
        raise ValidationError("phase6 bsearch checker surfaces mismatch")
    if bsearch.get("current_review_posture") != "direct-helper-readback-restored":
        raise ValidationError("phase6 bsearch review posture mismatch")
    bsearch_perf = bsearch.get("current_perf_evidence")
    if not isinstance(bsearch_perf, dict):
        raise ValidationError("phase6 bsearch perf evidence missing")
    if bsearch_perf.get("case_labels") != EXPECTED_BSEARCH_CASES:
        raise ValidationError("phase6 bsearch perf labels mismatch")
    if bsearch_perf.get("query_count") != 16:
        raise ValidationError("phase6 bsearch query count mismatch")
    if bsearch_perf.get("budget_formula") != "std.math.log2_int_ceil(len) + 1":
        raise ValidationError("phase6 bsearch budget formula mismatch")
    if bsearch_perf.get("linux_style_rerun_routes") != EXPECTED_BSEARCH_RERUN_ROUTES:
        raise ValidationError("phase6 bsearch rerun routes mismatch")

    bsearch_parity = get_helper(parity_helpers, "bsearch")
    if bsearch_parity.get("checker_surfaces") != EXPECTED_BSEARCH_CHECKER_SURFACES:
        raise ValidationError("phase6 parity bsearch checker surfaces mismatch")
    bsearch_parity_perf = bsearch_parity.get("current_perf_evidence")
    if not isinstance(bsearch_parity_perf, dict):
        raise ValidationError("phase6 parity bsearch perf evidence missing")
    if bsearch_parity_perf.get("budget_model") != "comparison_budget":
        raise ValidationError("phase6 parity bsearch budget model mismatch")
    if bsearch_parity_perf.get("bound_budget_formula") != "std.math.log2_int_ceil(len) + 1":
        raise ValidationError("phase6 parity bsearch budget formula mismatch")
    if bsearch_parity_perf.get("runtime_selected_c_abi_replays") != EXPECTED_BSEARCH_C_ABI_REPLAYS:
        raise ValidationError("phase6 parity bsearch C ABI rerun mismatch")
    if bsearch_parity_perf.get("linux_style_rerun_routes") != EXPECTED_BSEARCH_RERUN_ROUTES:
        raise ValidationError("phase6 parity bsearch rerun routes mismatch")

    checksum = get_helper(helpers, "checksum")
    if checksum.get("checker_surfaces") != EXPECTED_CHECKSUM_CHECKER_SURFACES:
        raise ValidationError("phase6 checksum checker surfaces mismatch")
    checksum_perf = checksum.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("phase6 checksum perf evidence missing")
    if checksum_perf.get("cases") != EXPECTED_CHECKSUM_PAYLOAD_CASES:
        raise ValidationError("phase6 checksum payload matrix mismatch")
    if checksum_perf.get("ipv4_fast_path_cases") != EXPECTED_CHECKSUM_FAST_PATH_CASES:
        raise ValidationError("phase6 checksum fast-path matrix mismatch")
    if checksum_perf.get("linux_style_rerun_routes") != EXPECTED_CHECKSUM_RERUN_ROUTES:
        raise ValidationError("phase6 checksum rerun routes mismatch")

    checksum_parity = get_helper(parity_helpers, "checksum")
    if checksum_parity.get("checker_surfaces") != EXPECTED_CHECKSUM_CHECKER_SURFACES:
        raise ValidationError("phase6 parity checksum checker surfaces mismatch")

    hexdump = get_helper(helpers, "hexdump")
    if hexdump.get("checker_surfaces") != EXPECTED_HEXDUMP_CHECKER_SURFACES:
        raise ValidationError("phase6 hexdump checker surfaces mismatch")
    if hexdump.get("perf_matrix_preflight") != "zigux/tests/phase6_hexdump_perf_matrix.zig":
        raise ValidationError("phase6 hexdump perf-matrix preflight mismatch")
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("phase6 hexdump perf evidence missing")
    if hexdump_perf.get("cases") != EXPECTED_HEXDUMP_PERF_CASES:
        raise ValidationError("phase6 hexdump perf cases mismatch")
    if hexdump_perf.get("linux_style_rerun_routes") != EXPECTED_HEXDUMP_EVIDENCE_RERUN_ROUTES:
        raise ValidationError("phase6 hexdump evidence rerun routes mismatch")

    hexdump_parity = get_helper(parity_helpers, "hexdump")
    if hexdump_parity.get("checker_surfaces") != EXPECTED_HEXDUMP_CHECKER_SURFACES:
        raise ValidationError("phase6 parity hexdump checker surfaces mismatch")
    hexdump_parity_perf = hexdump_parity.get("current_perf_evidence")
    if not isinstance(hexdump_parity_perf, dict):
        raise ValidationError("phase6 parity hexdump perf evidence missing")
    if hexdump_parity_perf.get("linux_style_rerun_routes") != EXPECTED_HEXDUMP_PARITY_RERUN_ROUTES:
        raise ValidationError("phase6 parity hexdump rerun routes mismatch")

    require_list_contains(
        manifest.get("current_shared_replay_inventory"),
        EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS,
        "phase6 shared replay inventory",
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / DOCS_README_PATH, "\n".join(EXPECTED_DOCS_README_SNIPPETS) + "\n")
    write(root / CATALOG_PATH, "\n".join(EXPECTED_CATALOG_SNIPPETS) + "\n")
    write(root / SURVEY_PATH, "\n".join(EXPECTED_SURVEY_SNIPPETS) + "\n")
    write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "lane_scope": EXPECTED_LANE_SCOPE,
                "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_repo_reality_gaps": EXPECTED_CURRENT_REPO_REALITY_GAPS,
                "current_shared_replay_inventory": EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS,
                "helpers": [
                    {
                        "key": "base64",
                        "checker_surfaces": EXPECTED_BASE64_CHECKER_SURFACES,
                    },
                    {
                        "key": "bsearch",
                        "checker_surfaces": EXPECTED_BSEARCH_CHECKER_SURFACES,
                        "current_review_posture": "direct-helper-readback-restored",
                        "current_perf_evidence": {
                            "case_labels": EXPECTED_BSEARCH_CASES,
                            "query_count": 16,
                            "budget_formula": "std.math.log2_int_ceil(len) + 1",
                            "linux_style_rerun_routes": EXPECTED_BSEARCH_RERUN_ROUTES,
                        },
                    },
                    {
                        "key": "checksum",
                        "checker_surfaces": EXPECTED_CHECKSUM_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "cases": EXPECTED_CHECKSUM_PAYLOAD_CASES,
                            "ipv4_fast_path_cases": EXPECTED_CHECKSUM_FAST_PATH_CASES,
                            "linux_style_rerun_routes": EXPECTED_CHECKSUM_RERUN_ROUTES,
                        },
                    },
                    {
                        "key": "hexdump",
                        "checker_surfaces": EXPECTED_HEXDUMP_CHECKER_SURFACES,
                        "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",
                        "current_perf_evidence": {
                            "cases": EXPECTED_HEXDUMP_PERF_CASES,
                            "linux_style_rerun_routes": EXPECTED_HEXDUMP_EVIDENCE_RERUN_ROUTES,
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / PARITY_MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PARITY_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "lane_scope": EXPECTED_PARITY_LANE_SCOPE,
                "shared_direct_evidence": EXPECTED_SHARED_DIRECT_EVIDENCE,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "shared_follow_through_gaps": EXPECTED_PARITY_FOLLOW_THROUGH_GAPS,
                "helpers": [
                    {
                        "key": "base64",
                        "checker_surfaces": EXPECTED_BASE64_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "case_labels": EXPECTED_BASE64_CASES,
                            "iterations": 12000,
                            "max_encode_slowdown_pct": 150,
                            "max_decode_slowdown_pct": 325,
                            "linux_style_rerun_routes": EXPECTED_BASE64_RERUN_ROUTES,
                        },
                    },
                    {
                        "key": "bsearch",
                        "checker_surfaces": EXPECTED_BSEARCH_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "budget_model": "comparison_budget",
                            "bound_budget_formula": "std.math.log2_int_ceil(len) + 1",
                            "runtime_selected_c_abi_replays": EXPECTED_BSEARCH_C_ABI_REPLAYS,
                            "linux_style_rerun_routes": EXPECTED_BSEARCH_RERUN_ROUTES,
                        },
                    },
                    {
                        "key": "checksum",
                        "checker_surfaces": EXPECTED_CHECKSUM_CHECKER_SURFACES,
                    },
                    {
                        "key": "hexdump",
                        "checker_surfaces": EXPECTED_HEXDUMP_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "linux_style_rerun_routes": EXPECTED_HEXDUMP_PARITY_RERUN_ROUTES,
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, rel_path: Path, mutate) -> None:
    path = root / rel_path
    original = read_text(path)
    mutate(path)
    try:
        validate(root)
    except ValidationError:
        return
    finally:
        write(path, original)
    raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")


def rewrite_json(path: Path, mutate) -> None:
    data = json.loads(read_text(path))
    mutate(data)
    write(path, json.dumps(data, indent=2) + "\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_present_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0

        expect_failure(root, DOCS_README_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_DOCS_README_SNIPPETS[2] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, CATALOG_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_CATALOG_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, SURVEY_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_SURVEY_SNIPPETS[3] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, BUILD_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_BUILD_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, MAKEFILE_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_MAKEFILE_SNIPPETS[2] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"surveyed_head": "current-master-readback-2026-05-21"})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("Documentation/zigux/phase6-runtime-command-environment-gap-survey.md")))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"public_tree_backed_shared_companions": ["Documentation/zigux/phase6-perf-gate-survey.md"]})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"current_repo_reality_gaps": ["zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig"]})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][0].update({"checker_surfaces": [EXPECTED_BASE64_CHECKER_SURFACES[0]]})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][1]["checker_surfaces"].pop()))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][1]["current_perf_evidence"].update({"budget_formula": "len + 1"})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][2].update({"checker_surfaces": ["scripts/zigux/check-phase6-checksum-corpus-evidence.py"]})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][3]["current_perf_evidence"].update({"linux_style_rerun_routes": EXPECTED_HEXDUMP_EVIDENCE_RERUN_ROUTES[:-1]})))
        cases_run += 1
        expect_failure(root, MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_shared_replay_inventory"].remove("make -C zigux phase6-hexdump-review")))
        cases_run += 1
        expect_failure(
            root,
            MANIFEST_PATH,
            lambda path: rewrite_json(
                path,
                lambda data: data.update(
                    {
                        "helpers": [
                            data["helpers"][1],
                            data["helpers"][0],
                            data["helpers"][2],
                            data["helpers"][3],
                        ]
                    }
                ),
            ),
        )
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"packet": EXPECTED_PACKET})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"lane_scope": "shared helper-parity rows only"})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"surveyed_head": "current-master-readback-2026-05-21"})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"roadmap_anchors": EXPECTED_ROADMAP_ANCHORS[:-1]})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"shared_follow_through_gaps": ["Documentation/zigux/phase6-helper-parity-catalog.md"]})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["shared_direct_evidence"].remove("scripts/zigux/check-phase6-base64-bsearch-perf-markers.py")))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["shared_direct_evidence"].remove("scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py")))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["shared_direct_evidence"].remove("scripts/zigux/check-phase6-hexdump-packet.py")))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["shared_direct_evidence"].remove("scripts/zigux/check-phase6-hexdump-route.py")))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"public_tree_backed_shared_companions": ["Documentation/zigux/phase6-perf-gate-survey.md"]})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][0].update({"checker_surfaces": [EXPECTED_BASE64_CHECKER_SURFACES[0]]})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][0]["current_perf_evidence"].update({"max_decode_slowdown_pct": 350})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][1].update({"checker_surfaces": [EXPECTED_BSEARCH_CHECKER_SURFACES[0]]})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][1]["current_perf_evidence"].update({"runtime_selected_c_abi_replays": EXPECTED_BSEARCH_C_ABI_REPLAYS[:1]})))
        cases_run += 1
        expect_failure(root, PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][3]["current_perf_evidence"].update({"linux_style_rerun_routes": EXPECTED_HEXDUMP_PARITY_RERUN_ROUTES[:-1]})))
        cases_run += 1
        expect_failure(
            root,
            PARITY_MANIFEST_PATH,
            lambda path: rewrite_json(
                path,
                lambda data: data.update(
                    {
                        "helpers": [
                            data["helpers"][1],
                            data["helpers"][0],
                            data["helpers"][2],
                            data["helpers"][3],
                        ]
                    }
                ),
            ),
        )
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
    print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1
    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
