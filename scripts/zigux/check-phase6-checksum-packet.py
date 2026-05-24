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
        '.{ .label = "IPV4_20B_UPDATED", .len = 20, .iterations = 600_000, .max_slowdown_pct = 100,',
        '.{ .label = "IPV4_24B", .len = 24, .iterations = 500_000, .max_slowdown_pct = 100,',
        '.{ .label = "IPV4_60B", .len = 60, .iterations = 250_000, .max_slowdown_pct = 100,',
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
    ],
    FIXTURE_PATH: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "IPV4_20B", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_20B_UPDATED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },',
    ],
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- scope: checksum helper parity and perf evidence shipped on current `master`",
        "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
        "- `tcpUdpNofold`, `tcpUdpMagic`, `tcpUdpV6Nofold`, `tcpUdpV6Magic`, `ipFastCsumIhl`, and `ipFastCsum`",
        "- an external C-vs-Zig spot check through `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, `zigux/tests/phase6_checksum_c_parity.zig`, and `zigux/tests/fixtures/phase6_checksum_c_harness.c`",
    ],
    EVIDENCE_CATALOG_PATH: [
        "### checksum",
        "- roadmap anchor: `lib/checksum.c`",
        "- Zig helper: `lib/checksum.zig`",
        "- focused helper replay: `zigux/tests/phase6_checksum.zig`",
        "- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`",
        "- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- dedicated corpus checker: `scripts/zigux/check-phase6-checksum-corpus-evidence.py`",
        "- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`",
        "and the current perf packet now keeps both the payload slowdown matrix and the `checksum.ipFastCsum` IPv4 fast-path matrix explicit",
    ],
    PARITY_CATALOG_PATH: [
        "### checksum",
        "- roadmap anchor: `lib/checksum.c`",
        "- landed Zig helper: `lib/checksum.zig`",
        "- focused helper replay: `zigux/tests/phase6_checksum.zig`",
        "- helper-evidence row: `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-corpus-evidence.py`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, and `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
        "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note",
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
        "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf",
        "$(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all",
        "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
    ],
}

EXPECTED_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]
EXPECTED_CURRENT_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
]
EXPECTED_SHARED_PARITY_EVIDENCE = [
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
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/validate-phase6.py",
]
EXPECTED_PARITY_FOLLOW_THROUGH_GAPS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
]
EXPECTED_CHECKSUM_REPLAY_ROUTES = [
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "make -C zigux phase6-perf",
]
EXPECTED_CHECKSUM_HELPER_ROW = {
    "roadmap_anchor": "lib/checksum.c",
    "zig_helper": "lib/checksum.zig",
    "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
    "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
    "direct_c_parity_replay": "zigux/tests/phase6_checksum_c_parity.zig",
    "direct_c_parity_harness": "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "fixture_surfaces": ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
    "checker_surfaces": EXPECTED_CHECKER_SURFACES,
    "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
    "current_review_posture": "direct-helper-readback-restored",
    "still_missing_direct_companions": [],
    "current_perf_evidence": {
        "cases": [
            {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
            {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
        ],
        "payload_case_labels": ["64B", "1501B"],
        "ipv4_fast_path_case_labels": ["IPV4_20B", "IPV4_20B_UPDATED", "IPV4_24B", "IPV4_60B"],
        "linux_style_rerun_routes": [
            "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-checksum-perf-matrix-test",
            "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-checksum-perf",
            "make -C zigux phase6-perf",
        ],
    },
}
SELF_TEST_CASE_COUNT = 6


class ValidationError(RuntimeError):
    pass


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


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {path.as_posix()}: {exc}") from exc


def require_contains(items: object, expected: list[str], field: str) -> None:
    if not isinstance(items, list):
        raise ValidationError(f"{field} list")
    for item in expected:
        if item not in items:
            raise ValidationError(f"{field} contains {item}")


def require_exact(value: object, expected: object, field: str) -> None:
    if value != expected:
        raise ValidationError(f"{field} exact match")


def find_helper_row(manifest: dict[str, object], key: str, path: Path) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"{path.as_posix()}: helpers list")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"{path.as_posix()}: helpers contains {key} row")


def validate_helper_row(helper: dict[str, object], field_prefix: str) -> None:
    for key, expected in EXPECTED_CHECKSUM_HELPER_ROW.items():
        if key == "current_perf_evidence":
            perf = helper.get("current_perf_evidence")
            if not isinstance(perf, dict):
                raise ValidationError(f"{field_prefix}.current_perf_evidence object")
            for perf_key, perf_expected in expected.items():
                require_exact(
                    perf.get(perf_key),
                    perf_expected,
                    f"{field_prefix}.current_perf_evidence.{perf_key}",
                )
        else:
            require_exact(helper.get(key), expected, f"{field_prefix}.{key}")


def validate_evidence_manifest(repo_root: Path) -> None:
    path = repo_root / EVIDENCE_MANIFEST_PATH
    manifest = load_json(path)
    require_exact(manifest.get("packet"), "phase6-helper-evidence", f"{path.as_posix()}: packet")
    require_exact(
        manifest.get("public_tree_backed_shared_companions"),
        [],
        f"{path.as_posix()}: public_tree_backed_shared_companions",
    )
    require_contains(
        manifest.get("current_direct_readback_companions"),
        EXPECTED_CURRENT_DIRECT_COMPANIONS,
        f"{path.as_posix()}: current_direct_readback_companions",
    )
    require_contains(
        manifest.get("current_shared_replay_inventory"),
        EXPECTED_CHECKSUM_REPLAY_ROUTES,
        f"{path.as_posix()}: current_shared_replay_inventory",
    )
    validate_helper_row(find_helper_row(manifest, "checksum", path), f"{path.as_posix()}: checksum")


def validate_parity_manifest(repo_root: Path) -> None:
    path = repo_root / PARITY_MANIFEST_PATH
    manifest = load_json(path)
    require_exact(manifest.get("packet"), "phase6-helper-parity", f"{path.as_posix()}: packet")
    require_exact(
        manifest.get("public_tree_backed_shared_companions"),
        [],
        f"{path.as_posix()}: public_tree_backed_shared_companions",
    )
    require_contains(
        manifest.get("shared_direct_evidence"),
        EXPECTED_SHARED_PARITY_EVIDENCE,
        f"{path.as_posix()}: shared_direct_evidence",
    )
    require_exact(
        manifest.get("shared_follow_through_gaps"),
        EXPECTED_PARITY_FOLLOW_THROUGH_GAPS,
        f"{path.as_posix()}: shared_follow_through_gaps",
    )
    validate_helper_row(find_helper_row(manifest, "checksum", path), f"{path.as_posix()}: checksum")


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
    path.write_text(content + "\n", encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for path, snippets in REQUIRED_SNIPPETS.items():
        write(root / path, "\n".join(snippets))

    evidence_manifest = {
        "packet": "phase6-helper-evidence",
        "current_direct_readback_companions": EXPECTED_CURRENT_DIRECT_COMPANIONS,
        "public_tree_backed_shared_companions": [],
        "helpers": [
            {"key": "base64"},
            {"key": "bsearch"},
            EXPECTED_CHECKSUM_HELPER_ROW | {"key": "checksum"},
            {"key": "hexdump"},
        ],
        "current_shared_replay_inventory": EXPECTED_CHECKSUM_REPLAY_ROUTES,
    }
    parity_manifest = {
        "packet": "phase6-helper-parity",
        "shared_direct_evidence": EXPECTED_SHARED_PARITY_EVIDENCE,
        "public_tree_backed_shared_companions": [],
        "helpers": [
            {"key": "base64"},
            {"key": "bsearch"},
            EXPECTED_CHECKSUM_HELPER_ROW | {"key": "checksum"},
            {"key": "hexdump"},
        ],
        "shared_follow_through_gaps": EXPECTED_PARITY_FOLLOW_THROUGH_GAPS,
    }
    write(root / EVIDENCE_MANIFEST_PATH, json.dumps(evidence_manifest, indent=2))
    write(root / PARITY_MANIFEST_PATH, json.dumps(parity_manifest, indent=2))


def mutate_text_and_expect_failure(root: Path, path: Path, old: str, new: str, expected: str) -> None:
    original = read_text(path)
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        validate(root)
    except ValidationError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r}, got {str(exc)!r}") from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        path.write_text(original, encoding="utf-8")


def mutate_json_and_expect_failure(root: Path, path: Path, mutate, expected: str) -> None:
    original = read_text(path)
    data = json.loads(original)
    mutate(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        validate(root)
    except ValidationError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r}, got {str(exc)!r}") from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        mutate_text_and_expect_failure(
            root,
            root / PERF_PATH,
            '.{ .label = "IPV4_20B_UPDATED", .len = 20, .iterations = 600_000, .max_slowdown_pct = 100,\n',
            "",
            "missing expected checksum packet marker",
        )
        mutate_json_and_expect_failure(
            root,
            root / EVIDENCE_MANIFEST_PATH,
            lambda data: data["helpers"][2].__setitem__("current_review_posture", "blocked_helper_packet_missing"),
            "zigux/tests/phase6_helper_evidence_manifest.json: checksum.current_review_posture exact match",
        )
        mutate_json_and_expect_failure(
            root,
            root / EVIDENCE_MANIFEST_PATH,
            lambda data: data["helpers"][2].__setitem__("still_missing_direct_companions", ["zigux/tests/phase6_checksum_c_parity.zig"]),
            "zigux/tests/phase6_helper_evidence_manifest.json: checksum.still_missing_direct_companions exact match",
        )
        mutate_json_and_expect_failure(
            root,
            root / PARITY_MANIFEST_PATH,
            lambda data: data["shared_direct_evidence"].remove("Documentation/zigux/phase6-perf-gate-survey.md"),
            "zigux/tests/phase6_helper_parity_manifest.json: shared_direct_evidence contains Documentation/zigux/phase6-perf-gate-survey.md",
        )
        mutate_json_and_expect_failure(
            root,
            root / PARITY_MANIFEST_PATH,
            lambda data: data.__setitem__("shared_follow_through_gaps", []),
            "zigux/tests/phase6_helper_parity_manifest.json: shared_follow_through_gaps exact match",
        )
        mutate_text_and_expect_failure(
            root,
            root / BUILD_PATH,
            '"phase6-checksum-perf-matrix-test",\n',
            "",
            "missing expected checksum packet marker",
        )

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
