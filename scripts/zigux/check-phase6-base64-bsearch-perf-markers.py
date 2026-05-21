#!/usr/bin/env python3
"""Guard the current Phase 6 base64 and bsearch perf-marker packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
BSEARCH_PERF_PATH = Path("zigux/tests/phase6_bsearch_perf.zig")
CHECKER_PATH = Path("scripts/zigux/check-phase6-base64-bsearch-perf-markers.py")
REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "`zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-base64-perf`",
    "`zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-bsearch-perf`",
]

REQUIRED_CATALOG_SNIPPETS = [
    "base64` keeps a dedicated helper-local slowdown replay in `zigux/tests/phase6_base64_perf.zig`",
    "bsearch` now keeps a dedicated helper-local perf replay in `zigux/tests/phase6_bsearch_perf.zig`",
    "- `make -C zigux phase6-base64-perf`",
    "- `make -C zigux phase6-bsearch-perf`",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_BSEARCH_PERF_SNIPPETS = [
    "fn compareCountedDescending(key: *const u32, item: *const u32) i32 {",
    "fn compareCountedOpaqueDescending(key: *const anyopaque, item: *const anyopaque) i32 {",
    "populateDescending(descending_values, ascending_values);",
    "const descending_witness = try runWitnessCases(",
    "compareCountedDescending,",
    "compareCountedOpaqueDescending,",
    "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
]

REQUIRED_SHARED_REPLAYS = [
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
]

REQUIRED_DIRECT_READBACK_COMPANION = CHECKER_PATH.as_posix()
REQUIRED_BASE64_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-base64-corpus-determinism.py",
]
REQUIRED_BSEARCH_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
]
EXPECTED_BASE64_LABELS = [
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
]
EXPECTED_BSEARCH_LABELS = ["len15", "len64", "len1024"]
EXPECTED_BSEARCH_C_ABI_REPLAYS = [
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
]

SELF_TEST_CASE_COUNT = 17


class ValidationError(RuntimeError):
    """Raised when the Phase 6 base64/bsearch perf packet drifts."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 base64/bsearch perf marker in {path.as_posix()}: {snippet}"
            )


def load_manifest(path: Path) -> dict[str, object]:
    try:
        parsed = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return parsed


def get_helper(manifest: dict[str, object], key: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"manifest helpers[] missing for {key}")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper row in manifest: {key}")


def require_checker_surfaces(
    helper: dict[str, object],
    key: str,
    expected_surfaces: list[str],
) -> None:
    checker_surfaces = helper.get("checker_surfaces")
    if not isinstance(checker_surfaces, list):
        raise ValidationError(f"{key} checker_surfaces missing")
    for surface in expected_surfaces:
        if surface not in checker_surfaces:
            raise ValidationError(f"{key} checker surface drifted: {surface}")


def require_string_list(value: object, label: str, expected: list[str]) -> None:
    if value != expected:
        raise ValidationError(f"{label} drifted")


def validate_evidence_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-evidence":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")

    companions = manifest.get("current_direct_readback_companions")
    if not isinstance(companions, list):
        raise ValidationError("current_direct_readback_companions is missing")
    if REQUIRED_DIRECT_READBACK_COMPANION not in companions:
        raise ValidationError(
            f"missing direct readback companion in {path.as_posix()}: {REQUIRED_DIRECT_READBACK_COMPANION}"
        )

    base64 = get_helper(manifest, "base64")
    bsearch = get_helper(manifest, "bsearch")

    if base64.get("dedicated_slowdown_replay") != "zigux/tests/phase6_base64_perf.zig":
        raise ValidationError("base64 dedicated_slowdown_replay drifted")
    if bsearch.get("dedicated_slowdown_replay") != "zigux/tests/phase6_bsearch_perf.zig":
        raise ValidationError("bsearch dedicated_slowdown_replay drifted")
    require_checker_surfaces(base64, "base64", REQUIRED_BASE64_CHECKER_SURFACES)
    require_checker_surfaces(bsearch, "bsearch", REQUIRED_BSEARCH_CHECKER_SURFACES)
    require_string_list(
        bsearch.get("focused_c_abi_replays"),
        "bsearch focused_c_abi_replays",
        EXPECTED_BSEARCH_C_ABI_REPLAYS,
    )

    inventory = manifest.get("current_shared_replay_inventory")
    if not isinstance(inventory, list):
        raise ValidationError("current_shared_replay_inventory is missing")
    for replay in REQUIRED_SHARED_REPLAYS:
        if replay not in inventory:
            raise ValidationError(
                f"missing shared replay inventory marker in {path.as_posix()}: {replay}"
            )


def validate_parity_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-parity":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")

    base64 = get_helper(manifest, "base64")
    bsearch = get_helper(manifest, "bsearch")

    base64_perf = base64.get("current_perf_evidence")
    bsearch_perf = bsearch.get("current_perf_evidence")
    if not isinstance(base64_perf, dict):
        raise ValidationError("base64 current_perf_evidence missing")
    if not isinstance(bsearch_perf, dict):
        raise ValidationError("bsearch current_perf_evidence missing")

    if base64_perf.get("case_labels") != EXPECTED_BASE64_LABELS:
        raise ValidationError("base64 perf labels drifted")
    if base64_perf.get("iterations") != 12000:
        raise ValidationError("base64 perf iterations drifted")
    if base64_perf.get("max_encode_slowdown_pct") != 150:
        raise ValidationError("base64 encode threshold drifted")
    if base64_perf.get("max_decode_slowdown_pct") != 325:
        raise ValidationError("base64 decode threshold drifted")
    base64_routes = base64_perf.get("linux_style_rerun_routes")
    if not isinstance(base64_routes, list):
        raise ValidationError("base64 rerun routes missing")
    if "make -C zigux phase6-base64-perf" not in base64_routes:
        raise ValidationError("base64 rerun route missing phase6-base64-perf")

    if bsearch_perf.get("budget_model") != "comparison_budget":
        raise ValidationError("bsearch budget model drifted")
    if bsearch_perf.get("case_labels") != EXPECTED_BSEARCH_LABELS:
        raise ValidationError("bsearch perf labels drifted")
    if bsearch_perf.get("query_count") != 16:
        raise ValidationError("bsearch query count drifted")
    if bsearch_perf.get("bound_budget_formula") != "std.math.log2_int_ceil(len) + 1":
        raise ValidationError("bsearch bound budget formula drifted")
    require_string_list(
        bsearch_perf.get("runtime_selected_c_abi_replays"),
        "bsearch runtime_selected_c_abi_replays",
        EXPECTED_BSEARCH_C_ABI_REPLAYS,
    )
    bsearch_routes = bsearch_perf.get("linux_style_rerun_routes")
    if not isinstance(bsearch_routes, list):
        raise ValidationError("bsearch rerun routes missing")
    if "make -C zigux phase6-bsearch-perf" not in bsearch_routes:
        raise ValidationError("bsearch rerun route missing phase6-bsearch-perf")


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(repo_root / BSEARCH_PERF_PATH, REQUIRED_BSEARCH_PERF_SNIPPETS)
    validate_evidence_manifest(repo_root / EVIDENCE_MANIFEST_PATH)
    validate_parity_manifest(repo_root / PARITY_MANIFEST_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / BSEARCH_PERF_PATH, "\n".join(REQUIRED_BSEARCH_PERF_SNIPPETS) + "\n")
    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-evidence",
                "phase": "Phase 6",
                "current_direct_readback_companions": [REQUIRED_DIRECT_READBACK_COMPANION],
                "helpers": [
                    {
                        "key": "base64",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",
                        "checker_surfaces": REQUIRED_BASE64_CHECKER_SURFACES,
                    },
                    {
                        "key": "bsearch",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig",
                        "checker_surfaces": REQUIRED_BSEARCH_CHECKER_SURFACES,
                        "focused_c_abi_replays": EXPECTED_BSEARCH_C_ABI_REPLAYS,
                    },
                ],
                "current_shared_replay_inventory": REQUIRED_SHARED_REPLAYS,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / PARITY_MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-parity",
                "phase": "Phase 6",
                "helpers": [
                    {
                        "key": "base64",
                        "current_perf_evidence": {
                            "case_labels": EXPECTED_BASE64_LABELS,
                            "iterations": 12000,
                            "max_encode_slowdown_pct": 150,
                            "max_decode_slowdown_pct": 325,
                            "linux_style_rerun_routes": [
                                "make -C zigux phase6-base64-perf",
                                "make -C zigux phase6-perf",
                            ],
                        },
                    },
                    {
                        "key": "bsearch",
                        "current_perf_evidence": {
                            "budget_model": "comparison_budget",
                            "case_labels": EXPECTED_BSEARCH_LABELS,
                            "query_count": 16,
                            "bound_budget_formula": "std.math.log2_int_ceil(len) + 1",
                            "runtime_selected_c_abi_replays": EXPECTED_BSEARCH_C_ABI_REPLAYS,
                            "linux_style_rerun_routes": [
                                "make -C zigux phase6-bsearch-perf",
                                "make -C zigux phase6-perf",
                            ],
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def mutate_text(path: Path, old: str, new: str) -> None:
    content = read_text(path)
    write(path, content.replace(old, new, 1))


def expect_failure(root: Path, mutate, expected_fragment: str) -> None:
    mutate()
    try:
        validate(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected {expected_fragment!r} in {str(exc)!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        expect_failure(
            root,
            lambda: mutate_text(
                root / SCRIPTS_README_PATH,
                "`make -C zigux phase6-base64-perf`",
                "`make -C zigux phase6-base64-test`",
            ),
            "phase6-base64-perf",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / CATALOG_PATH,
                "zigux/tests/phase6_bsearch_perf.zig",
                "zigux/tests/phase6_bsearch.zig",
            ),
            "phase6_bsearch",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / MAKEFILE_PATH,
                "phase6-bsearch-perf:",
                "phase6-bsearch-test:",
            ),
            "phase6-bsearch-perf:",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / BSEARCH_PERF_PATH,
                "fn compareCountedDescending(key: *const u32, item: *const u32) i32 {",
                "fn compareCounted(key: *const u32, item: *const u32) i32 {",
            ),
            "compareCountedDescending",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / BSEARCH_PERF_PATH,
                "populateDescending(descending_values, ascending_values);",
                "populateDescending(ascending_values, descending_values);",
            ),
            "populateDescending(descending_values, ascending_values);",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / BSEARCH_PERF_PATH,
                "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
                "for (ascending_queries, ascending_expected_hits) |query, expected_hit| {",
            ),
            "descending_queries",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
                "scripts/zigux/check-phase6-shared-surface.py",
            ),
            "missing direct readback companion",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                "zigux/tests/phase6_base64_perf.zig",
                "zigux/tests/phase6_base64.zig",
            ),
            "base64 dedicated_slowdown_replay drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
                "scripts/zigux/check-phase6-shared-surface.py",
            ),
            "bsearch checker surface drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                "zigux/tests/phase6_bsearch_lower_bound.zig",
            ),
            "bsearch focused_c_abi_replays drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                "make -C zigux phase6-bsearch-perf",
                "make -C zigux phase6-bsearch-test",
            ),
            "missing shared replay inventory marker",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"packet": "phase6-helper-parity"',
                '"packet": "phase6-helper-evidence"',
            ),
            "unexpected packet id",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"max_decode_slowdown_pct": 325',
                '"max_decode_slowdown_pct": 400',
            ),
            "base64 decode threshold drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"bound_budget_formula": "std.math.log2_int_ceil(len) + 1"',
                '"bound_budget_formula": "len"',
            ),
            "bsearch bound budget formula drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                "zigux/tests/phase6_bsearch_lower_bound.zig",
            ),
            "bsearch runtime_selected_c_abi_replays drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                "make -C zigux phase6-bsearch-perf",
                "make -C zigux phase6-bsearch-test",
            ),
            "bsearch rerun route missing phase6-bsearch-perf",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"case_labels": [\n          "len15",\n          "len64",\n          "len1024"\n        ]',
                '"case_labels": ["len15", "len64"]',
            ),
            "bsearch perf labels drifted",
        )
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_BASE64_BSEARCH_PERF_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_BASE64_BSEARCH_PERF_MARKERS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
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
        print(f"PHASE6_BASE64_BSEARCH_PERF_MARKERS=fail: {exc}")
        return 1

    print("PHASE6_BASE64_BSEARCH_PERF_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
