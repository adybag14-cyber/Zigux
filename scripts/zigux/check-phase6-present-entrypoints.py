#!/usr/bin/env python3
"""Guard the current Phase 6 helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_HELPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]
EXPECTED_PUBLIC_TREE_BACKED_SHARED_COMPANIONS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
]
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_BSEARCH_CHECKER = "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"
EXPECTED_CHECKSUM_CHECKER = "scripts/zigux/check-phase6-checksum-corpus-evidence.py"
EXPECTED_HEXDUMP_CHECKER = "scripts/zigux/check-phase6-hexdump-packet.py"
EXPECTED_HEXDUMP_REVIEW_POSTURE = "direct-readback-limited"
EXPECTED_HEXDUMP_MISSING_COMPANIONS = [
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
]
EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS = [
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
]
EXPECTED_CHECKSUM_PAYLOAD_CASES = ["64B", "1501B"]
EXPECTED_CHECKSUM_FAST_PATH_CASES = ["IPV4_20B", "IPV4_24B", "IPV4_60B"]
EXPECTED_CHECKSUM_RERUN_ROUTES = [
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback warning",
    "Current public raw readback rematerializes `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so keep those broader parity and perf notes as public-tree-backed companion evidence rather than as direct authenticated shared-packet proof in this runtime.",
    "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
    "the `checksum.ipFastCsum` IPv4 fast-path matrix (`IPV4_20B`, `IPV4_24B`, `IPV4_60B`)",
    "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "while the slice note and perf refresh note still need fresh direct reads before they are presented as current shipped evidence",
    "## Current shared replay inventory",
    "- `make -C zigux phase6-bsearch-perf`",
    "- `make -C zigux phase6-checksum-perf`",
    "- `make -C zigux phase6-hexdump-review`",
    "- `make -C zigux phase6-hexdump-perf-matrix-test`",
]
REQUIRED_BUILD_SNIPPETS = [
    'const bsearch_perf_root_module = b.createModule(.{',
    'const bsearch_perf = b.addExecutable(.{',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    'const checksum_perf_matrix_test_step = b.step(',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
]
REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-bsearch-perf:",
    "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf-matrix-test:",
    "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
]
SURVEYED_HEAD_PATTERN = re.compile(r"^- surveyed head: `([^`]+)`$", re.M)
SELF_TEST_CASE_COUNT = 14


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
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def extract_surveyed_head(content: str) -> str:
    match = SURVEYED_HEAD_PATTERN.search(content)
    if match is None:
        raise ValidationError("missing expected Phase 6 marker in catalog: surveyed head")
    return match.group(1)


def require_list_contains(values: object, expected_items: list[str], label: str) -> None:
    if not isinstance(values, list):
        raise ValidationError(f"{label} missing")
    missing = [item for item in expected_items if item not in values]
    if missing:
        raise ValidationError(f"{label} missing expected items: {', '.join(missing)}")


def validate(repo_root: Path) -> None:
    catalog_content = read_text(repo_root / CATALOG_PATH)
    manifest = read_json(repo_root / MANIFEST_PATH)

    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)

    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase6 helper-evidence packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 helper-evidence phase drift")
    if manifest.get("lane_scope") != EXPECTED_LANE_SCOPE:
        raise ValidationError("phase6 helper-evidence lane-scope drift")
    if manifest.get("surveyed_head") != extract_surveyed_head(catalog_content):
        raise ValidationError("phase6 helper-evidence surveyed-head mismatch")
    if manifest.get("current_direct_readback_companions") != EXPECTED_DIRECT_COMPANIONS:
        raise ValidationError("phase6 direct-readback companions mismatch")
    if manifest.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_BACKED_SHARED_COMPANIONS:
        raise ValidationError("phase6 public-tree-backed shared companions mismatch")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 roadmap anchor packet mismatch")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helpers list missing")
    if [helper.get("key") for helper in helpers if isinstance(helper, dict)] != EXPECTED_HELPER_KEYS:
        raise ValidationError("phase6 helper key order mismatch")

    bsearch = next(helper for helper in helpers if helper.get("key") == "bsearch")
    if bsearch.get("checker_surfaces") != [EXPECTED_BSEARCH_CHECKER]:
        raise ValidationError("phase6 bsearch checker surface mismatch")
    if bsearch.get("dedicated_slowdown_replay") != "zigux/tests/phase6_bsearch_perf.zig":
        raise ValidationError("phase6 bsearch perf replay mismatch")

    checksum = next(helper for helper in helpers if helper.get("key") == "checksum")
    if checksum.get("checker_surfaces") != [EXPECTED_CHECKSUM_CHECKER]:
        raise ValidationError("phase6 checksum checker surface mismatch")
    checksum_perf = checksum.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("phase6 checksum perf evidence missing")
    if checksum_perf.get("payload_case_labels") != EXPECTED_CHECKSUM_PAYLOAD_CASES:
        raise ValidationError("phase6 checksum payload perf cases mismatch")
    if checksum_perf.get("ipv4_fast_path_case_labels") != EXPECTED_CHECKSUM_FAST_PATH_CASES:
        raise ValidationError("phase6 checksum ipv4 fast-path cases mismatch")
    if checksum_perf.get("linux_style_rerun_routes") != EXPECTED_CHECKSUM_RERUN_ROUTES:
        raise ValidationError("phase6 checksum perf rerun routes mismatch")

    hexdump = next(helper for helper in helpers if helper.get("key") == "hexdump")
    if hexdump.get("checker_surfaces") != [EXPECTED_HEXDUMP_CHECKER]:
        raise ValidationError("phase6 hexdump checker surface mismatch")
    if hexdump.get("perf_matrix_preflight") != "zigux/tests/phase6_hexdump_perf_matrix.zig":
        raise ValidationError("phase6 hexdump perf-matrix preflight mismatch")
    if hexdump.get("current_review_posture") != EXPECTED_HEXDUMP_REVIEW_POSTURE:
        raise ValidationError("phase6 hexdump review posture mismatch")
    if hexdump.get("still_missing_direct_companions") != EXPECTED_HEXDUMP_MISSING_COMPANIONS:
        raise ValidationError("phase6 hexdump missing-direct-companions mismatch")

    require_list_contains(
        manifest.get("current_repo_reality_gaps"),
        EXPECTED_HEXDUMP_MISSING_COMPANIONS,
        "phase6 current repo reality gaps",
    )
    require_list_contains(
        manifest.get("current_shared_replay_inventory"),
        EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS,
        "phase6 shared replay inventory",
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / CATALOG_PATH,
        "\n".join(
            [
                "- surveyed head: `61e026c`",
                *REQUIRED_CATALOG_SNIPPETS,
            ]
        )
        + "\n",
    )
    write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": "61e026c",
                "lane_scope": EXPECTED_LANE_SCOPE,
                "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_BACKED_SHARED_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_repo_reality_gaps": [
                    *EXPECTED_HEXDUMP_MISSING_COMPANIONS,
                ],
                "current_shared_replay_inventory": [
                    *EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS,
                ],
                "helpers": [
                    {"key": "base64"},
                    {
                        "key": "bsearch",
                        "checker_surfaces": [EXPECTED_BSEARCH_CHECKER],
                        "dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig",
                    },
                    {
                        "key": "checksum",
                        "checker_surfaces": [EXPECTED_CHECKSUM_CHECKER],
                        "current_perf_evidence": {
                            "payload_case_labels": EXPECTED_CHECKSUM_PAYLOAD_CASES,
                            "ipv4_fast_path_case_labels": EXPECTED_CHECKSUM_FAST_PATH_CASES,
                            "linux_style_rerun_routes": EXPECTED_CHECKSUM_RERUN_ROUTES,
                        },
                    },
                    {
                        "key": "hexdump",
                        "checker_surfaces": [EXPECTED_HEXDUMP_CHECKER],
                        "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",
                        "current_review_posture": EXPECTED_HEXDUMP_REVIEW_POSTURE,
                        "still_missing_direct_companions": EXPECTED_HEXDUMP_MISSING_COMPANIONS,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, path: Path, snippet: str) -> None:
    original = read_text(path)
    if path == root / MANIFEST_PATH:
        data = json.loads(original)
        if snippet == '"public_tree_backed_shared_companions"':
            data.pop("public_tree_backed_shared_companions", None)
        elif snippet == '"Documentation/zigux/README.md",':
            data["current_direct_readback_companions"].remove("Documentation/zigux/README.md")
        elif snippet == '"scripts/zigux/check-phase6-checksum-corpus-evidence.py"':
            data["helpers"][2]["checker_surfaces"] = []
        elif snippet == '"make -C zigux phase6-checksum-perf"':
            data["helpers"][2]["current_perf_evidence"]["linux_style_rerun_routes"].remove("make -C zigux phase6-checksum-perf")
        elif snippet == '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"':
            data["helpers"][1]["checker_surfaces"] = []
        elif snippet == '"scripts/zigux/check-phase6-hexdump-packet.py"':
            data["helpers"][3]["checker_surfaces"] = []
        elif snippet == '"Documentation/zigux/phase6-hexdump-perf-refresh.md"':
            data["helpers"][3]["still_missing_direct_companions"].remove("Documentation/zigux/phase6-hexdump-perf-refresh.md")
            data["current_repo_reality_gaps"].remove("Documentation/zigux/phase6-hexdump-perf-refresh.md")
        elif snippet == '"make -C zigux phase6-hexdump-review"':
            data["current_shared_replay_inventory"].remove("make -C zigux phase6-hexdump-review")
        else:
            raise AssertionError(f"unhandled manifest self-test mutation: {snippet}")
        write(path, json.dumps(data, indent=2) + "\n")
    else:
        write(path, original.replace(snippet + "\n", "", 1))
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_present_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        for path, snippet in [
            (root / CATALOG_PATH, "Current public raw readback rematerializes `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so keep those broader parity and perf notes as public-tree-backed companion evidence rather than as direct authenticated shared-packet proof in this runtime."),
            (root / CATALOG_PATH, "the `checksum.ipFastCsum` IPv4 fast-path matrix (`IPV4_20B`, `IPV4_24B`, `IPV4_60B`)"),
            (root / CATALOG_PATH, "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`"),
            (root / CATALOG_PATH, "- `make -C zigux phase6-hexdump-review`"),
            (root / BUILD_PATH, 'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");'),
            (root / MAKEFILE_PATH, "phase6-checksum-perf:"),
            (root / MANIFEST_PATH, '"public_tree_backed_shared_companions"'),
            (root / MANIFEST_PATH, '"Documentation/zigux/README.md",'),
            (root / MANIFEST_PATH, '"scripts/zigux/check-phase6-checksum-corpus-evidence.py"'),
            (root / MANIFEST_PATH, '"make -C zigux phase6-checksum-perf"'),
            (root / MANIFEST_PATH, '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"'),
            (root / MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-packet.py"'),
            (root / MANIFEST_PATH, '"Documentation/zigux/phase6-hexdump-perf-refresh.md"'),
            (root / MANIFEST_PATH, '"make -C zigux phase6-hexdump-review"'),
        ]:
            expect_failure(root, path, snippet)
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
