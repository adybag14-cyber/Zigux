#!/usr/bin/env python3
"""Guard the current Phase 6 checksum helper packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HELPER_PATH = Path("lib/checksum.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_checksum.zig")
PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
EVIDENCE_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = [
    HELPER_PATH,
    HELPER_TEST_PATH,
    PERF_PATH,
    FIXTURE_PATH,
    SLICE_PATH,
    EVIDENCE_CATALOG_PATH,
    EVIDENCE_MANIFEST_PATH,
    PARITY_CATALOG_PATH,
    PARITY_MANIFEST_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
]

REQUIRED_SNIPPETS = {
    HELPER_PATH: [
        "pub fn add16(sum: u16, addend: u16) u16 {",
        "pub fn sub16(sum: u16, addend: u16) u16 {",
        "pub fn tcpUdpMagic(sum: u32, saddr: u32, daddr: u32, len: u16, proto: u8) u16 {",
        "pub fn tcpUdpV6Magic(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u16 {",
        "pub fn ipFastCsum(header: []const u8) u16 {",
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 checksum carry helpers preserve one\'s-complement replacement behavior" {',
        'test "phase 6 checksum pseudo-header helpers match direct reference accumulation" {',
        'test "phase 6 checksum fast-path fixtures stay aligned with focused correctness replay" {',
        "checksum.tcpUdpMagic(",
        "checksum.tcpUdpV6Magic(",
        "checksum.ipFastCsum(case.header)",
    ],
    PERF_PATH: [
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150,',
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150,',
        '.{ .label = "IPV4_20B", .len = 20, .iterations = 600_000, .max_slowdown_pct = 100,',
        '.{ .label = "IPV4_24B", .len = 24, .iterations = 500_000, .max_slowdown_pct = 100,',
        '.{ .label = "IPV4_60B", .len = 60, .iterations = 250_000, .max_slowdown_pct = 100,',
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
    ],
    FIXTURE_PATH: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "IPV4_20B", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },',
    ],
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- scope: checksum helper parity and perf evidence already shipped on current `master`",
        "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
        "- `tcpUdpNofold`, `tcpUdpMagic`, `tcpUdpV6Nofold`, `tcpUdpV6Magic`, and `ipFastCsum`",
        "- a restored direct C-vs-Zig parity checker on current `master`",
    ],
    EVIDENCE_CATALOG_PATH: [
        "### checksum",
        "- roadmap anchor: `lib/checksum.c`",
        "- Zig helper: `lib/checksum.zig`",
        "- focused helper replay: `zigux/tests/phase6_checksum.zig`",
        "- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`",
        "- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- last-known direct C parity companions still needing fresh direct reads: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`",
        "- current perf packet now keeps both the payload slowdown matrix and the `checksum.ipFastCsum` IPv4 fast-path matrix explicit",
        "`make -C zigux phase6-checksum-perf-matrix-test`",
        "`make -C zigux phase6-checksum-perf`",
        "`make -C zigux phase6-perf`",
    ],
    PARITY_CATALOG_PATH: [
        "### checksum",
        "- roadmap anchor: `lib/checksum.c`",
        "- landed Zig helper: `lib/checksum.zig`",
        "- focused helper replay: `zigux/tests/phase6_checksum.zig`",
        "- helper-evidence row: `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `scripts/zigux/check-phase6-checksum-corpus-evidence.py`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, and `zigux/tests/phase6_helper_parity_manifest.json`",
        "- exact missing direct companions from authenticated 2026-05-20 readback: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, checker, and slice note, while the exact missing direct companions above still returned 404 on 2026-05-20 and therefore remain outside shipped evidence",
    ],
    BUILD_PATH: [
        '.name = "phase6-checksum-perf",',
        'const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");',
        'checksum_test_step.dependOn(&run_checksum_perf_matrix_tests.step);',
        '"phase6-checksum-perf-matrix-test",',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    ],
    MAKEFILE_PATH: [
        "phase6-checksum-test:",
        "phase6-checksum-perf-matrix-test:",
        "phase6-checksum-perf:",
        "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
        "$(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all",
        "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
    ],
}

REQUIRED_EVIDENCE_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
]

REQUIRED_PARITY_DIRECT_EVIDENCE = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]

EXPECTED_PUBLIC_TREE_COMPANIONS = [
    "Documentation/zigux/phase6-perf-gate-survey.md",
]

EXPECTED_CHECKSUM_MISSING_COMPANIONS = [
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]

REQUIRED_SHARED_REALITY_GAPS = [
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]

REQUIRED_SHARED_REPLAY_ROUTES = [
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]

EXPECTED_CHECKSUM_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
]

EXPECTED_PAYLOAD_CASE_LABELS = ["64B", "1501B"]
EXPECTED_FAST_PATH_CASE_LABELS = ["IPV4_20B", "IPV4_24B", "IPV4_60B"]
EXPECTED_PERF_CASES = [
    {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
    {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
]
EXPECTED_LINUX_STYLE_RERUN_ROUTES = [
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]

SELF_TEST_CASE_COUNT = 5


class ValidationError(RuntimeError):
    """Raised when the checksum packet drifts from the expected review surface."""


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
                f"missing expected checksum packet marker in {path.as_posix()}: {snippet}"
            )


def require_manifest_item(items: list[object], expected: str, field: str) -> None:
    if expected not in items:
        raise ValidationError(f"{field} contains {expected}")


def require_manifest_items(items: object, expected_items: list[str], field: str) -> None:
    if not isinstance(items, list):
        raise ValidationError(f"{field} list")
    for item in expected_items:
        require_manifest_item(items, item, field)


def find_helper_row(manifest: dict[str, object], key: str, manifest_path: Path) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"{manifest_path.as_posix()}: helpers list")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"{manifest_path.as_posix()}: helpers contains {key} row")


def require_exact(value: object, expected: object, field: str) -> None:
    if value != expected:
        raise ValidationError(f"{field} exact match")


def validate_checksum_helper_row(
    helper: dict[str, object],
    field_prefix: str,
    *,
    require_checker_surfaces: bool,
    require_perf_cases: bool,
) -> None:
    expected_fields = {
        "roadmap_anchor": "lib/checksum.c",
        "zig_helper": "lib/checksum.zig",
        "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    }
    for key, expected in expected_fields.items():
        if helper.get(key) != expected:
            raise ValidationError(f"{field_prefix}.{key}={expected}")

    require_exact(
        helper.get("fixture_surfaces"),
        ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
        f"{field_prefix}.fixture_surfaces",
    )
    require_exact(
        helper.get("still_missing_direct_companions"),
        EXPECTED_CHECKSUM_MISSING_COMPANIONS,
        f"{field_prefix}.still_missing_direct_companions",
    )

    if require_checker_surfaces:
        require_exact(
            helper.get("checker_surfaces"),
            EXPECTED_CHECKSUM_CHECKER_SURFACES,
            f"{field_prefix}.checker_surfaces",
        )

    perf = helper.get("current_perf_evidence")
    if not isinstance(perf, dict):
        raise ValidationError(f"{field_prefix}.current_perf_evidence object")

    require_exact(
        perf.get("payload_case_labels"),
        EXPECTED_PAYLOAD_CASE_LABELS,
        f"{field_prefix}.current_perf_evidence.payload_case_labels",
    )
    require_exact(
        perf.get("ipv4_fast_path_case_labels"),
        EXPECTED_FAST_PATH_CASE_LABELS,
        f"{field_prefix}.current_perf_evidence.ipv4_fast_path_case_labels",
    )
    require_manifest_items(
        perf.get("linux_style_rerun_routes"),
        EXPECTED_LINUX_STYLE_RERUN_ROUTES,
        f"{field_prefix}.current_perf_evidence.linux_style_rerun_routes",
    )
    if require_perf_cases:
        require_exact(
            perf.get("cases"),
            EXPECTED_PERF_CASES,
            f"{field_prefix}.current_perf_evidence.cases",
        )


def validate_evidence_manifest(repo_root: Path) -> None:
    manifest_path = repo_root / EVIDENCE_MANIFEST_PATH
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {manifest_path.as_posix()}: {exc}") from exc

    if manifest.get("packet") != "phase6-helper-evidence":
        raise ValidationError(f"{EVIDENCE_MANIFEST_PATH.as_posix()}: packet=phase6-helper-evidence")

    require_manifest_items(
        manifest.get("current_direct_readback_companions"),
        REQUIRED_EVIDENCE_DIRECT_COMPANIONS,
        f"{EVIDENCE_MANIFEST_PATH.as_posix()}: current_direct_readback_companions",
    )
    require_manifest_items(
        manifest.get("public_tree_backed_shared_companions"),
        EXPECTED_PUBLIC_TREE_COMPANIONS,
        f"{EVIDENCE_MANIFEST_PATH.as_posix()}: public_tree_backed_shared_companions",
    )
    require_manifest_items(
        manifest.get("current_repo_reality_gaps"),
        REQUIRED_SHARED_REALITY_GAPS,
        f"{EVIDENCE_MANIFEST_PATH.as_posix()}: current_repo_reality_gaps",
    )
    require_manifest_items(
        manifest.get("current_shared_replay_inventory"),
        REQUIRED_SHARED_REPLAY_ROUTES,
        f"{EVIDENCE_MANIFEST_PATH.as_posix()}: current_shared_replay_inventory",
    )

    checksum = find_helper_row(manifest, "checksum", manifest_path)
    validate_checksum_helper_row(
        checksum,
        f"{EVIDENCE_MANIFEST_PATH.as_posix()}: checksum",
        require_checker_surfaces=True,
        require_perf_cases=False,
    )


def validate_parity_manifest(repo_root: Path) -> None:
    manifest_path = repo_root / PARITY_MANIFEST_PATH
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {manifest_path.as_posix()}: {exc}") from exc

    if manifest.get("packet") != "phase6-helper-parity":
        raise ValidationError(f"{PARITY_MANIFEST_PATH.as_posix()}: packet=phase6-helper-parity")

    require_manifest_items(
        manifest.get("shared_direct_evidence"),
        REQUIRED_PARITY_DIRECT_EVIDENCE,
        f"{PARITY_MANIFEST_PATH.as_posix()}: shared_direct_evidence",
    )
    require_manifest_items(
        manifest.get("public_tree_backed_shared_companions"),
        EXPECTED_PUBLIC_TREE_COMPANIONS,
        f"{PARITY_MANIFEST_PATH.as_posix()}: public_tree_backed_shared_companions",
    )
    require_exact(
        manifest.get("shared_follow_through_gaps"),
        [],
        f"{PARITY_MANIFEST_PATH.as_posix()}: shared_follow_through_gaps",
    )

    checksum = find_helper_row(manifest, "checksum", manifest_path)
    validate_checksum_helper_row(
        checksum,
        f"{PARITY_MANIFEST_PATH.as_posix()}: checksum",
        require_checker_surfaces=False,
        require_perf_cases=True,
    )


def validate(repo_root: Path) -> None:
    for path in REQUIRED_FILES:
        if not (repo_root / path).is_file():
            raise ValidationError(f"missing required file: {path.as_posix()}")
    for path, snippets in REQUIRED_SNIPPETS.items():
        require_snippets(repo_root / path, snippets)
    validate_evidence_manifest(repo_root)
    validate_parity_manifest(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for path, snippets in REQUIRED_SNIPPETS.items():
        write(root / path, "\n".join(snippets) + "\n")

    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-evidence",
                "current_direct_readback_companions": REQUIRED_EVIDENCE_DIRECT_COMPANIONS,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
                "helpers": [
                    {"key": "base64"},
                    {"key": "bsearch"},
                    {
                        "key": "checksum",
                        "roadmap_anchor": "lib/checksum.c",
                        "zig_helper": "lib/checksum.zig",
                        "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
                        "fixture_surfaces": ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
                        "checker_surfaces": EXPECTED_CHECKSUM_CHECKER_SURFACES,
                        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
                        "current_review_posture": "direct-helper-readback-restored",
                        "still_missing_direct_companions": EXPECTED_CHECKSUM_MISSING_COMPANIONS,
                        "current_perf_evidence": {
                            "payload_case_labels": EXPECTED_PAYLOAD_CASE_LABELS,
                            "ipv4_fast_path_case_labels": EXPECTED_FAST_PATH_CASE_LABELS,
                            "linux_style_rerun_routes": EXPECTED_LINUX_STYLE_RERUN_ROUTES,
                        },
                    },
                    {"key": "hexdump"},
                ],
                "current_repo_reality_gaps": REQUIRED_SHARED_REALITY_GAPS,
                "current_shared_replay_inventory": REQUIRED_SHARED_REPLAY_ROUTES,
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
                "shared_direct_evidence": REQUIRED_PARITY_DIRECT_EVIDENCE,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
                "helpers": [
                    {"key": "base64"},
                    {"key": "bsearch"},
                    {
                        "key": "checksum",
                        "roadmap_anchor": "lib/checksum.c",
                        "zig_helper": "lib/checksum.zig",
                        "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
                        "fixture_surfaces": ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
                        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
                        "current_review_posture": "direct-helper-readback-restored",
                        "still_missing_direct_companions": EXPECTED_CHECKSUM_MISSING_COMPANIONS,
                        "current_perf_evidence": {
                            "cases": EXPECTED_PERF_CASES,
                            "payload_case_labels": EXPECTED_PAYLOAD_CASE_LABELS,
                            "ipv4_fast_path_case_labels": EXPECTED_FAST_PATH_CASE_LABELS,
                            "linux_style_rerun_routes": EXPECTED_LINUX_STYLE_RERUN_ROUTES,
                        },
                    },
                    {"key": "hexdump"},
                ],
                "shared_follow_through_gaps": [],
            },
            indent=2,
        )
        + "\n",
    )


def mutate_and_expect_failure(root: Path, path: Path, old: str, new: str, expected: str) -> None:
    original = read_text(path)
    write(path, original.replace(old, new, 1))
    try:
        validate(root)
    except ValidationError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r}, got {str(exc)!r}") from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases = [
            (
                root / HELPER_TEST_PATH,
                'test "phase 6 checksum pseudo-header helpers match direct reference accumulation" {\n',
                "",
                "missing expected checksum packet marker",
            ),
            (
                root / PERF_PATH,
                '.{ .label = "IPV4_60B", .len = 60, .iterations = 250_000, .max_slowdown_pct = 100,\n',
                "",
                "missing expected checksum packet marker",
            ),
            (
                root / EVIDENCE_MANIFEST_PATH,
                '"current_review_posture": "direct-helper-readback-restored"',
                '"current_review_posture": "blocked_helper_packet_missing"',
                "checksum.current_review_posture=direct-helper-readback-restored",
            ),
            (
                root / EVIDENCE_MANIFEST_PATH,
                '"make -C zigux phase6-checksum-perf-matrix-test"',
                '"make -C zigux phase6-checksum-fast-matrix-test"',
                "checksum.current_perf_evidence.linux_style_rerun_routes contains make -C zigux phase6-checksum-perf-matrix-test",
            ),
            (
                root / PARITY_MANIFEST_PATH,
                '"IPV4_60B"',
                '"IPV4_61B"',
                "checksum.current_perf_evidence.ipv4_fast_path_case_labels exact match",
            ),
        ]
        for path, old, new, expected in cases:
            mutate_and_expect_failure(root, path, old, new, expected)

    print("PHASE6_CHECKSUM_PACKET_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


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
        print(f"PHASE6_CHECKSUM_PACKET=fail: {exc}")
        return 1
    print("PHASE6_CHECKSUM_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())