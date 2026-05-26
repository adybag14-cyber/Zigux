#!/usr/bin/env python3
"""Guard the current Phase 6 shared replay inventory packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_EVIDENCE_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_DIRECT_COMPANION_CHECKERS = [
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
]
EXPECTED_SHARED_REPLAY_INVENTORY = [
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
    "python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]

SELF_TEST_CASE_COUNT = 10


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


def require_string_list(value: object, expected: list[str], label: str) -> None:
    if value != expected:
        raise ValidationError(f"{label} drifted")


def require_contains(values: object, expected: list[str], label: str) -> None:
    if not isinstance(values, list):
        raise ValidationError(f"{label} missing")
    for item in expected:
        if item not in values:
            raise ValidationError(f"{label} missing {item}")


def validate(repo_root: Path) -> None:
    evidence_manifest = read_json(repo_root / HELPER_EVIDENCE_MANIFEST)
    parity_manifest = read_json(repo_root / HELPER_PARITY_MANIFEST)

    if evidence_manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("helper-evidence packet drifted")
    if parity_manifest.get("packet") != EXPECTED_PARITY_PACKET:
        raise ValidationError("helper-parity packet drifted")
    if evidence_manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("helper-evidence phase drifted")
    if parity_manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("helper-parity phase drifted")
    if evidence_manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("helper-evidence surveyed_head drifted")
    if parity_manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("helper-parity surveyed_head drifted")
    if evidence_manifest.get("lane_scope") != EXPECTED_EVIDENCE_LANE_SCOPE:
        raise ValidationError("helper-evidence lane_scope drifted")
    if parity_manifest.get("lane_scope") != EXPECTED_PARITY_LANE_SCOPE:
        raise ValidationError("helper-parity lane_scope drifted")

    require_string_list(
        evidence_manifest.get("current_shared_replay_inventory"),
        EXPECTED_SHARED_REPLAY_INVENTORY,
        "current_shared_replay_inventory",
    )
    require_contains(
        evidence_manifest.get("current_direct_readback_companions"),
        EXPECTED_DIRECT_COMPANION_CHECKERS,
        "current_direct_readback_companions",
    )
    require_contains(
        parity_manifest.get("shared_direct_evidence"),
        EXPECTED_DIRECT_COMPANION_CHECKERS,
        "shared_direct_evidence",
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / HELPER_EVIDENCE_MANIFEST,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "lane_scope": EXPECTED_EVIDENCE_LANE_SCOPE,
                "current_direct_readback_companions": EXPECTED_DIRECT_COMPANION_CHECKERS,
                "current_shared_replay_inventory": EXPECTED_SHARED_REPLAY_INVENTORY,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / HELPER_PARITY_MANIFEST,
        json.dumps(
            {
                "packet": EXPECTED_PARITY_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "lane_scope": EXPECTED_PARITY_LANE_SCOPE,
                "shared_direct_evidence": EXPECTED_DIRECT_COMPANION_CHECKERS,
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(fn, fragment: str) -> None:
    try:
        fn()
    except ValidationError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {str(exc)!r}") from exc
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_shared_replay_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        def reset() -> None:
            scaffold_repo(root)

        cases_run = 0

        def expect_mutation(mutator, fragment: str) -> None:
            nonlocal cases_run
            reset()
            mutator()
            expect_failure(lambda: validate(root), fragment)
            cases_run += 1

        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "packet": "phase6-helper-parity",
                    },
                    indent=2,
                )
                + "\n",
            ),
            "helper-evidence packet drifted",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "packet": "phase6-helper-evidence",
                    },
                    indent=2,
                )
                + "\n",
            ),
            "helper-parity packet drifted",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "surveyed_head": "current-master-readback-2026-05-21",
                    },
                    indent=2,
                )
                + "\n",
            ),
            "helper-evidence surveyed_head drifted",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "lane_scope": "shared helper-parity rows only",
                    },
                    indent=2,
                )
                + "\n",
            ),
            "helper-parity lane_scope drifted",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "current_shared_replay_inventory": [
                            item
                            for item in read_json(root / HELPER_EVIDENCE_MANIFEST)[
                                "current_shared_replay_inventory"
                            ]
                            if item != "python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            ),
            "current_shared_replay_inventory drifted",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "current_shared_replay_inventory": [
                            item
                            for item in read_json(root / HELPER_EVIDENCE_MANIFEST)[
                                "current_shared_replay_inventory"
                            ]
                            if item != "python3 scripts/zigux/check-phase6-perf-threshold-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            ),
            "current_shared_replay_inventory drifted",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "current_direct_readback_companions": [
                            item
                            for item in read_json(root / HELPER_EVIDENCE_MANIFEST)[
                                "current_direct_readback_companions"
                            ]
                            if item != "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            ),
            "current_direct_readback_companions missing",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "current_direct_readback_companions": [
                            item
                            for item in read_json(root / HELPER_EVIDENCE_MANIFEST)[
                                "current_direct_readback_companions"
                            ]
                            if item != "scripts/zigux/check-phase6-perf-threshold-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            ),
            "current_direct_readback_companions missing",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "shared_direct_evidence": [
                            item
                            for item in read_json(root / HELPER_PARITY_MANIFEST)[
                                "shared_direct_evidence"
                            ]
                            if item != "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            ),
            "shared_direct_evidence missing",
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "shared_direct_evidence": [
                            item
                            for item in read_json(root / HELPER_PARITY_MANIFEST)[
                                "shared_direct_evidence"
                            ]
                            if item != "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            ),
            "shared_direct_evidence missing",
        )

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_SHARED_REPLAY_INVENTORY_SELF_TEST=pass")
    print(f"PHASE6_SHARED_REPLAY_INVENTORY_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE6_SHARED_REPLAY_INVENTORY=fail: {exc}")
        return 1

    print("PHASE6_SHARED_REPLAY_INVENTORY=pass")
    print(f"PHASE6_SHARED_REPLAY_INVENTORY_COUNT={len(EXPECTED_SHARED_REPLAY_INVENTORY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
