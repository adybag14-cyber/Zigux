#!/usr/bin/env python3
"""Guard the current Phase 13 devres DMA/scatterlist checker drift."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory


MANIFEST_PATH = Path("zigux/tests/phase13_devres_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-packet.py")

LIVE_MANIFEST_LANE_KEY = "P13-L01"
LIVE_MANIFEST_SURVEYED_COMMIT = "master-readback-2026-05-14"
LIVE_GAP_STATUSES = {
    "phase13-devres-live-dma-backed-helpers": "blocked_on_live_dma_state",
    "phase13-devres-live-scatterlist-ownership": "blocked_on_live_scatterlist_state",
}
SURVEY_MARKERS = [
    "older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift",
    "helper-only DMA/scatterlist boundary explicit",
]
STALE_CHECKER_MARKERS = [
    'MANIFEST_EXPECTED_LANE_KEY = "P13-L05"',
    'MANIFEST_EXPECTED_SURVEYED_COMMIT = "10369315cba5d146a7c6c4c6480ef9d279dc490f"',
    '"phase13-devres-live-dma-backed-helpers": "blocked_on_dma_state"',
    '"phase13-devres-live-scatterlist-ownership": "blocked_on_scatterlist_state"',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_manifest(text: str) -> list[str]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"phase13-devres-dma-boundary-gap:manifest-json:{exc.msg}"]

    issues: list[str] = []
    if manifest.get("lane_key") != LIVE_MANIFEST_LANE_KEY:
        issues.append("phase13-devres-dma-boundary-gap:live-manifest-lane-key")
    if manifest.get("surveyed_commit") != LIVE_MANIFEST_SURVEYED_COMMIT:
        issues.append("phase13-devres-dma-boundary-gap:live-manifest-surveyed-commit")

    statuses = {
        gap.get("id"): gap.get("status")
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_status in LIVE_GAP_STATUSES.items():
        if gap_id not in statuses:
            issues.append(f"phase13-devres-dma-boundary-gap:live-manifest-gap:{gap_id}")
        elif statuses[gap_id] != expected_status:
            issues.append(f"phase13-devres-dma-boundary-gap:live-manifest-gap-status:{gap_id}")
    return issues


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (MANIFEST_PATH, SURVEY_PATH, CHECKER_PATH):
        if not (root / rel).is_file():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    issues.extend(validate_manifest(read_text(root / MANIFEST_PATH)))
    issues.extend(collect_missing(read_text(root / SURVEY_PATH), SURVEY_MARKERS, "phase13-devres-dma-boundary-gap:survey"))
    issues.extend(
        collect_missing(
            read_text(root / CHECKER_PATH),
            STALE_CHECKER_MARKERS,
            "phase13-devres-dma-boundary-gap:stale-checker",
        )
    )
    return issues


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": LIVE_MANIFEST_LANE_KEY,
                "surveyed_commit": LIVE_MANIFEST_SURVEYED_COMMIT,
                "gaps": [{"id": gap_id, "status": status} for gap_id, status in LIVE_GAP_STATUSES.items()],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 13 devres Survey",
                "- the current packet now keeps a helper-only DMA/scatterlist boundary explicit too.",
                "- older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift rather than as the current checker label for this helper-first packet.",
            ]
        )
        + "\n",
    )
    write_text(
        root / CHECKER_PATH,
        "\n".join(
            [
                'MANIFEST_EXPECTED_LANE_KEY = "P13-L05"',
                'MANIFEST_EXPECTED_SURVEYED_COMMIT = "10369315cba5d146a7c6c4c6480ef9d279dc490f"',
                'MANIFEST_GAP_STATUSES = {',
                '    "phase13-devres-live-dma-backed-helpers": "blocked_on_dma_state",',
                '    "phase13-devres-live-scatterlist-ownership": "blocked_on_scatterlist_state",',
                '}',
            ]
        )
        + "\n",
    )


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        raise AssertionError(
            f"{label}: got={','.join(got) or 'none'} want={','.join(want) or 'none'}"
        )


def self_test() -> None:
    case_count = 0
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        case_count += 1
        assert_only(validate(root), [], "happy_path_failed")

        seed_fixture_tree(root)
        case_count += 1
        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "lane_key": "P13-L05",
                    "surveyed_commit": LIVE_MANIFEST_SURVEYED_COMMIT,
                    "gaps": [{"id": gap_id, "status": status} for gap_id, status in LIVE_GAP_STATUSES.items()],
                },
                indent=2,
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["phase13-devres-dma-boundary-gap:live-manifest-lane-key"],
            "lane_key_guard_failed",
        )

        seed_fixture_tree(root)
        case_count += 1
        write_text(
            root / CHECKER_PATH,
            'MANIFEST_EXPECTED_LANE_KEY = "P13-L01"\n',
        )
        assert_only(
            validate(root),
            [
                'phase13-devres-dma-boundary-gap:stale-checker:MANIFEST_EXPECTED_LANE_KEY = "P13-L05"',
                'phase13-devres-dma-boundary-gap:stale-checker:MANIFEST_EXPECTED_SURVEYED_COMMIT = "10369315cba5d146a7c6c4c6480ef9d279dc490f"',
                'phase13-devres-dma-boundary-gap:stale-checker:"phase13-devres-live-dma-backed-helpers": "blocked_on_dma_state"',
                'phase13-devres-dma-boundary-gap:stale-checker:"phase13-devres-live-scatterlist-ownership": "blocked_on_scatterlist_state"',
            ],
            "stale_checker_guard_failed",
        )

    print("PHASE13_DEVRES_DMA_BOUNDARY_GAP_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_DMA_BOUNDARY_GAP_SELF_TEST_CASES={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    issues = validate(Path(args.root))
    if issues:
        print("PHASE13_DEVRES_DMA_BOUNDARY_GAP=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE13_DEVRES_DMA_BOUNDARY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
