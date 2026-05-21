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
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_EVIDENCE_SURVEYED_HEAD = "current-master-readback-2026-05-20"
EXPECTED_PARITY_SURVEYED_HEAD = "current-master-readback-2026-05-20"
EXPECTED_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
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
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_PUBLIC_TREE_COMPANIONS = [
    "Documentation/zigux/phase6-perf-gate-survey.md",
]
EXPECTED_DOCS_README_SNIPPETS = [
    "authenticated current-master rereads now directly recover `Documentation/zigux/phase6-helper-parity-catalog.md`, while `Documentation/zigux/phase6-perf-gate-survey.md` still needs public-tree fallback in this runtime, so keep the helper-parity catalog inside the current docs-root evidence packet and keep the broader perf-note surface framed as public-tree-backed companion evidence rather than direct docs-root proof until a fresh authenticated reread recovers that note too.",
    "current `master` directly serves the four roadmap-backed helper anchors through `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`, their focused `zigux/tests/phase6_*` helper and perf replays, the restored `zigux/tests/phase6_build.zig` foothold, and the current `zigux/Makefile` wrapper family, so keep the docs-root reminder reviewable through that returned helper-evidence packet instead of restating helper-local semantics here.",
]
EXPECTED_CATALOG_SNIPPETS = [
    "Current public raw readback still helps recover `Documentation/zigux/phase6-perf-gate-survey.md`",
    "this helper-evidence catalog together with `Documentation/zigux/phase6-helper-parity-catalog.md`,",
]
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_HELPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_BASE64_CASES = [
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
]
EXPECTED_BASE64_ITERATIONS = 12000
EXPECTED_BASE64_ENCODE_SLOWDOWN_PCT = 150
EXPECTED_BASE64_DECODE_SLOWDOWN_PCT = 325
EXPECTED_BASE64_RERUN_ROUTES = [
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_BSEARCH_CHECKER = "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"
EXPECTED_CHECKSUM_CHECKER = "scripts/zigux/check-phase6-checksum-corpus-evidence.py"
EXPECTED_HEXDUMP_CHECKER = "scripts/zigux/check-phase6-hexdump-packet.py"
EXPECTED_HEXDUMP_REVIEW_POSTURE = "direct-helper-readback-restored"
EXPECTED_CURRENT_REPO_REALITY_GAPS = [
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
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
EXPECTED_HEXDUMP_PERF_CASES = [
    {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
    {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
]
EXPECTED_HEXDUMP_RERUN_ROUTES = [
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
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
SELF_TEST_CASE_COUNT = 23


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


def require_list_contains(values: object, expected_items: list[str], label: str) -> None:
    if not isinstance(values, list):
        raise ValidationError(f"{label} missing")
    missing = [item for item in expected_items if item not in values]
    if missing:
        raise ValidationError(f"{label} missing expected items: {', '.join(missing)}")


def validate(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    parity = read_json(repo_root / PARITY_MANIFEST_PATH)

    require_snippets(repo_root / DOCS_README_PATH, EXPECTED_DOCS_README_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, EXPECTED_CATALOG_SNIPPETS)
    require_snippets(repo_root / BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)

    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase6 helper-evidence packet drift")
    if parity.get("packet") != EXPECTED_PARITY_PACKET:
        raise ValidationError("phase6 helper-parity packet drift")
    if manifest.get("phase") != EXPECTED_PHASE or parity.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 phase drift")
    if manifest.get("lane_scope") != EXPECTED_LANE_SCOPE:
        raise ValidationError("phase6 helper-evidence lane-scope drift")
    if manifest.get("surveyed_head") != EXPECTED_EVIDENCE_SURVEYED_HEAD:
        raise ValidationError("phase6 helper-evidence surveyed-head drift")
    if parity.get("surveyed_head") != EXPECTED_PARITY_SURVEYED_HEAD:
        raise ValidationError("phase6 helper-parity surveyed-head drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_DIRECT_COMPANIONS:
        raise ValidationError("phase6 direct-readback companions mismatch")
    if manifest.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_COMPANIONS:
        raise ValidationError("phase6 public-tree-backed shared companions mismatch")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 roadmap anchor packet mismatch")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helpers list missing")
    if [helper.get("key") for helper in helpers if isinstance(helper, dict)] != EXPECTED_HELPER_KEYS:
        raise ValidationError("phase6 helper key order mismatch")

    parity_helpers = parity.get("helpers")
    if not isinstance(parity_helpers, list):
        raise ValidationError("phase6 parity helpers list missing")

    base64 = next(helper for helper in parity_helpers if helper.get("key") == "base64")
    base64_perf = base64.get("current_perf_evidence")
    if not isinstance(base64_perf, dict):
        raise ValidationError("phase6 base64 perf evidence missing")
    if base64_perf.get("case_labels") != EXPECTED_BASE64_CASES:
        raise ValidationError("phase6 base64 perf case labels mismatch")
    if base64_perf.get("iterations") != EXPECTED_BASE64_ITERATIONS:
        raise ValidationError("phase6 base64 perf iterations mismatch")
    if base64_perf.get("max_encode_slowdown_pct") != EXPECTED_BASE64_ENCODE_SLOWDOWN_PCT:
        raise ValidationError("phase6 base64 encode slowdown mismatch")
    if base64_perf.get("max_decode_slowdown_pct") != EXPECTED_BASE64_DECODE_SLOWDOWN_PCT:
        raise ValidationError("phase6 base64 decode slowdown mismatch")
    if base64_perf.get("linux_style_rerun_routes") != EXPECTED_BASE64_RERUN_ROUTES:
        raise ValidationError("phase6 base64 perf rerun routes mismatch")

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
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("phase6 hexdump perf evidence missing")
    if hexdump_perf.get("cases") != EXPECTED_HEXDUMP_PERF_CASES:
        raise ValidationError("phase6 hexdump perf cases mismatch")
    if hexdump_perf.get("linux_style_rerun_routes") != EXPECTED_HEXDUMP_RERUN_ROUTES:
        raise ValidationError("phase6 hexdump perf rerun routes mismatch")

    if manifest.get("current_repo_reality_gaps") != EXPECTED_CURRENT_REPO_REALITY_GAPS:
        raise ValidationError("phase6 current repo reality gaps mismatch")
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
    write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_EVIDENCE_SURVEYED_HEAD,
                "lane_scope": EXPECTED_LANE_SCOPE,
                "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_repo_reality_gaps": EXPECTED_CURRENT_REPO_REALITY_GAPS,
                "current_shared_replay_inventory": EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS,
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
                        "current_perf_evidence": {
                            "cases": EXPECTED_HEXDUMP_PERF_CASES,
                            "linux_style_rerun_routes": EXPECTED_HEXDUMP_RERUN_ROUTES,
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
                "surveyed_head": EXPECTED_PARITY_SURVEYED_HEAD,
                "helpers": [
                    {
                        "key": "base64",
                        "current_perf_evidence": {
                            "case_labels": EXPECTED_BASE64_CASES,
                            "iterations": EXPECTED_BASE64_ITERATIONS,
                            "max_encode_slowdown_pct": EXPECTED_BASE64_ENCODE_SLOWDOWN_PCT,
                            "max_decode_slowdown_pct": EXPECTED_BASE64_DECODE_SLOWDOWN_PCT,
                            "linux_style_rerun_routes": EXPECTED_BASE64_RERUN_ROUTES,
                        },
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, path: Path, mutate) -> None:
    original = read_text(path)
    mutate(path)
    try:
        validate(root)
    except ValidationError:
        return
    finally:
        write(path, original)
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_present_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0

        def rewrite_json(path: Path, fn) -> None:
            data = json.loads(read_text(path))
            fn(data)
            write(path, json.dumps(data, indent=2) + "\n")

        expect_failure(root, root / CATALOG_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_CATALOG_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / CATALOG_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_CATALOG_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / DOCS_README_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_DOCS_README_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / DOCS_README_PATH, lambda path: write(path, read_text(path).replace(EXPECTED_DOCS_README_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"surveyed_head": "deadbee"})))
        cases_run += 1
        expect_failure(root, root / PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"surveyed_head": "deadbee"})))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("Documentation/zigux/phase6-helper-parity-catalog.md")))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("Documentation/zigux/phase6-hexdump-slice.md")))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("scripts/zigux/check-phase6-base64-bsearch-perf-markers.py")))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("scripts/zigux/check-phase6-hexdump-route.py")))
        cases_run += 1
        expect_failure(root, root / PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][0]["current_perf_evidence"]["linux_style_rerun_routes"].remove("make -C zigux phase6-base64-perf")))
        cases_run += 1
        expect_failure(root, root / PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][0]["current_perf_evidence"].update({"max_decode_slowdown_pct": 326})))
        cases_run += 1
        expect_failure(root, root / PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][0]["current_perf_evidence"].update({"case_labels": EXPECTED_BASE64_CASES[:-1]})))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][1].update({"checker_surfaces": []})))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][2]["current_perf_evidence"]["linux_style_rerun_routes"].remove("make -C zigux phase6-checksum-perf")))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][3]["current_perf_evidence"]["cases"][3].update({"max_slowdown_pct": 601})))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["helpers"][3]["current_perf_evidence"]["linux_style_rerun_routes"].remove("make -C zigux phase6-hexdump-perf")))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_repo_reality_gaps"].remove("scripts/zigux/check-phase6-checksum-c-parity.py")))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_shared_replay_inventory"].remove("make -C zigux phase6-hexdump-review")))
        cases_run += 1
        expect_failure(root, root / BUILD_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_BUILD_SNIPPETS[2] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / MAKEFILE_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_MAKEFILE_SNIPPETS[4] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"packet": EXPECTED_PACKET})))
        cases_run += 1
        expect_failure(root, root / MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"lane_scope": "drifted"})))
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