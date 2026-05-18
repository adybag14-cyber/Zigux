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
PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = [
    HELPER_PATH,
    HELPER_TEST_PATH,
    PERF_PATH,
    FIXTURE_PATH,
    SLICE_PATH,
    PARITY_CATALOG_PATH,
    PERF_SURVEY_PATH,
    MANIFEST_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
]

REQUIRED_SNIPPETS = {
    HELPER_PATH: [
        "pub fn add16(sum: u16, addend: u16) u16 {",
        "pub fn sub16(sum: u16, addend: u16) u16 {",
        "pub fn tcpUdpNofold(sum: u32, saddr: u32, daddr: u32, len: u16, proto: u8) u32 {",
        "pub fn tcpUdpV6Nofold(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u32 {",
        "pub fn ipFastCsum(header: []const u8) u16 {",
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 checksum carry helpers preserve one\'s-complement replacement behavior" {',
        'test "phase 6 checksum pseudo-header helpers match direct accumulation" {',
        'test "phase 6 checksum ip fast path stays aligned with full compute for aligned headers" {',
        "checksum.add16(case.sum, case.addend)",
        "checksum.sub16(case.sum, case.addend)",
        "checksum.ipFastCsum(header)",
    ],
    PERF_PATH: [
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150',
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150',
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
    ],
    FIXTURE_PATH: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
    ],
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- scope: checksum helper parity and perf evidence already shipped on current `master`",
        "- `zigux/tests/phase6_checksum_perf.zig` keeps the helper-vs-reference slowdown gate explicit through the committed `64B` and `1501B` matrix in `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- `tcpUdpNofold`, `tcpUdpV6Nofold`, and `ipFastCsum`",
    ],
    PARITY_CATALOG_PATH: [
        "### checksum",
        "* roadmap anchor: `lib/checksum.c`",
        "* helper: `lib/checksum.zig`",
        "* focused helper replay on current `master`: `zigux/tests/phase6_checksum.zig`",
        "* dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_checksum_perf.zig`",
        "* focused checksum fixture companion on current `master`: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "* direct local focused replay route: `zig build test --build-file zigux/tests/phase6_build.zig`",
        "* direct local perf rerun route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
        "* shared route caveat: current authenticated `zigux/Makefile` readback still does not expose a committed `phase6-checksum-perf` target body, so keep Linux-style checksum perf reruns framed as follow-through rather than shipped current-`master` evidence",
    ],
    PERF_SURVEY_PATH: [
        "* checksum shared posture: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-checksum-perf` build step again",
        "* checksum wrapper caveat: current authenticated `zigux/Makefile` text still does not expose a committed `phase6-checksum-perf` target body, so Linux-style checksum perf reruns remain follow-through inventory rather than shipped current-`master` route evidence",
        "* checksum exact thresholds: `zigux/tests/phase6_checksum_perf.zig` and `zigux/tests/fixtures/phase6_checksum_vectors.zig` keep two helper-local slowdown cases, `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, each capped at `max_slowdown_pct = 150`",
    ],
    BUILD_PATH: [
        'const checksum_perf = b.addExecutable(.{',
        '.name = "phase6-checksum-perf",',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
        "checksum_perf_step.dependOn(&run_checksum_perf.step);",
    ],
}

FORBIDDEN_SNIPPETS = {
    MAKEFILE_PATH: [
        "phase6-checksum-perf:",
    ],
}

EXPECTED_MANIFEST = {
    "packet": "phase6-helper-parity",
    "shared_follow_through_gaps": [
        "Documentation/zigux/phase6-helper-parity-catalog.md",
        "Documentation/zigux/phase6-perf-gate-survey.md",
    ],
    "checksum": {
        "roadmap_anchor": "lib/checksum.c",
        "zig_helper": "lib/checksum.zig",
        "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
}

SELF_TEST_CASE_COUNT = 10


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


def require_absent(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet in content:
            raise ValidationError(
                f"unexpected stale checksum route marker in {path.as_posix()}: {snippet}"
            )


def validate_manifest(repo_root: Path) -> None:
    manifest_path = repo_root / MANIFEST_PATH
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {manifest_path.as_posix()}: {exc}") from exc

    if manifest.get("packet") != EXPECTED_MANIFEST["packet"]:
        raise ValidationError(
            "zigux/tests/phase6_helper_parity_manifest.json: packet=phase6-helper-parity"
        )

    for item in EXPECTED_MANIFEST["shared_follow_through_gaps"]:
        if item not in manifest.get("shared_follow_through_gaps", []):
            raise ValidationError(
                f"zigux/tests/phase6_helper_parity_manifest.json: shared_follow_through_gaps contains {item}"
            )

    checksum_row = next(
        (helper for helper in manifest.get("helpers", []) if helper.get("key") == "checksum"),
        None,
    )
    if checksum_row is None:
        raise ValidationError(
            "zigux/tests/phase6_helper_parity_manifest.json: helpers contains checksum row"
        )

    for key, expected in EXPECTED_MANIFEST["checksum"].items():
        if checksum_row.get(key) != expected:
            raise ValidationError(
                f"zigux/tests/phase6_helper_parity_manifest.json: checksum.{key}={expected}"
            )


def validate(repo_root: Path) -> None:
    for path in REQUIRED_FILES:
        if not (repo_root / path).is_file():
            raise ValidationError(f"missing required file: {path.as_posix()}")
    for path, snippets in REQUIRED_SNIPPETS.items():
        require_snippets(repo_root / path, snippets)
    for path, snippets in FORBIDDEN_SNIPPETS.items():
        require_absent(repo_root / path, snippets)
    validate_manifest(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for path, snippets in REQUIRED_SNIPPETS.items():
        write(root / path, "\n".join(snippets) + "\n")
    write(root / MAKEFILE_PATH, "# no phase6 checksum wrapper body here\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_MANIFEST["packet"],
                "shared_follow_through_gaps": EXPECTED_MANIFEST["shared_follow_through_gaps"],
                "helpers": [
                    {
                        "key": "checksum",
                        **EXPECTED_MANIFEST["checksum"],
                    }
                ],
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
                root / HELPER_PATH,
                "pub fn ipFastCsum(header: []const u8) u16 {\n",
                "",
                "pub fn ipFastCsum(header: []const u8) u16 {",
            ),
            (
                root / HELPER_TEST_PATH,
                "checksum.add16(case.sum, case.addend)\n",
                "",
                "checksum.add16(case.sum, case.addend)",
            ),
            (
                root / PERF_PATH,
                '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150\n',
                '.{ .label = "64B", .len = 64, .iterations = 20_000, .max_slowdown_pct = 150\n',
                "iterations = 200_000",
            ),
            (
                root / FIXTURE_PATH,
                '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },\n',
                '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 4_000, .max_slowdown_pct = 150 },\n',
                "iterations = 12_000",
            ),
            (
                root / PARITY_CATALOG_PATH,
                "* shared route caveat: current authenticated `zigux/Makefile` readback still does not expose a committed `phase6-checksum-perf` target body, so keep Linux-style checksum perf reruns framed as follow-through rather than shipped current-`master` evidence\n",
                "* direct Linux-style perf rerun route: `make -C zigux phase6-checksum-perf`\n",
                "shared route caveat",
            ),
            (
                root / PERF_SURVEY_PATH,
                "* checksum exact thresholds: `zigux/tests/phase6_checksum_perf.zig` and `zigux/tests/fixtures/phase6_checksum_vectors.zig` keep two helper-local slowdown cases, `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, each capped at `max_slowdown_pct = 150`\n",
                "* checksum exact thresholds: `zigux/tests/phase6_checksum_perf.zig` now keeps two helper-local slowdown cases, `64` at `reps = 20_000` and `1501` at `reps = 4_000`, each capped at `max_slowdown_pct = 150`\n",
                "checksum exact thresholds",
            ),
            (
                root / BUILD_PATH,
                'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");\n',
                "",
                "phase6-checksum-perf",
            ),
            (
                root / MAKEFILE_PATH,
                "# no phase6 checksum wrapper body here\n",
                "phase6-checksum-perf:\n\t@echo stale\n",
                "unexpected stale checksum route marker",
            ),
        ]
        for path, old, new, expected in cases:
            mutate_and_expect_failure(root, path, old, new, expected)

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][0]["current_review_posture"] = "blocked_helper_packet_missing"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        try:
            validate(root)
        except ValidationError as exc:
            if "checksum.current_review_posture=direct-helper-readback-restored" not in str(exc):
                raise
        else:
            raise AssertionError("expected manifest posture failure")
        scaffold_repo(root)

        (root / BUILD_PATH).unlink()
        try:
            validate(root)
        except ValidationError as exc:
            if f"missing required file: {BUILD_PATH.as_posix()}" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing file failure")

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
