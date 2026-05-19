#!/usr/bin/env python3
"""Guard the current Phase 6 checksum and hexdump perf-marker packet."""

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

REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "`zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-checksum-perf`",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-hexdump-perf`",
]

REQUIRED_CATALOG_SNIPPETS = [
    "checksum keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`",
    "hexdump keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`",
    "- `make -C zigux phase6-checksum-perf`",
    "- `make -C zigux phase6-hexdump-perf`",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-checksum-perf:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_EVIDENCE_REPLAYS = [
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
]

CHECKSUM_CASES = {"64B", "1501B"}
HEXDUMP_CASES = {"16B-plain-g1", "32B-ascii-g2", "16B-ascii-g4", "16B-ascii-g8"}

SELF_TEST_CASE_COUNT = 10


class ValidationError(RuntimeError):
    """Raised when the Phase 6 perf packet drifts."""


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
                f"missing expected Phase 6 perf marker in {path.as_posix()}: {snippet}"
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


def validate_evidence_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-evidence":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")

    checksum = get_helper(manifest, "checksum")
    hexdump = get_helper(manifest, "hexdump")

    if checksum.get("dedicated_slowdown_replay") != "zigux/tests/phase6_checksum_perf.zig":
        raise ValidationError("checksum dedicated_slowdown_replay drifted")
    if hexdump.get("dedicated_slowdown_replay") != "zigux/tests/phase6_hexdump_perf.zig":
        raise ValidationError("hexdump dedicated_slowdown_replay drifted")

    inventory = manifest.get("current_shared_replay_inventory")
    if not isinstance(inventory, list):
        raise ValidationError("current_shared_replay_inventory is missing")
    for replay in REQUIRED_EVIDENCE_REPLAYS:
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

    checksum = get_helper(manifest, "checksum")
    hexdump = get_helper(manifest, "hexdump")

    checksum_perf = checksum.get("current_perf_evidence")
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("checksum current_perf_evidence missing")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("hexdump current_perf_evidence missing")

    checksum_cases = checksum_perf.get("cases")
    if not isinstance(checksum_cases, list):
        raise ValidationError("checksum perf cases missing")
    checksum_labels = {
        case.get("label")
        for case in checksum_cases
        if isinstance(case, dict) and isinstance(case.get("label"), str)
    }
    if checksum_labels != CHECKSUM_CASES:
        raise ValidationError(f"checksum perf case drift: {sorted(checksum_labels)}")

    hexdump_cases = hexdump_perf.get("cases")
    if not isinstance(hexdump_cases, list):
        raise ValidationError("hexdump perf cases missing")
    hexdump_labels = {
        case.get("label")
        for case in hexdump_cases
        if isinstance(case, dict) and isinstance(case.get("label"), str)
    }
    if hexdump_labels != HEXDUMP_CASES:
        raise ValidationError(f"hexdump perf case drift: {sorted(hexdump_labels)}")

    checksum_routes = checksum_perf.get("linux_style_rerun_routes")
    hexdump_routes = hexdump_perf.get("linux_style_rerun_routes")
    if not isinstance(checksum_routes, list):
        raise ValidationError("checksum rerun routes missing")
    if not isinstance(hexdump_routes, list):
        raise ValidationError("hexdump rerun routes missing")
    if "make -C zigux phase6-checksum-perf" not in checksum_routes:
        raise ValidationError("checksum rerun route missing phase6-checksum-perf")
    if "make -C zigux phase6-hexdump-perf" not in hexdump_routes:
        raise ValidationError("hexdump rerun route missing phase6-hexdump-perf")


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    validate_evidence_manifest(repo_root / EVIDENCE_MANIFEST_PATH)
    validate_parity_manifest(repo_root / PARITY_MANIFEST_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-evidence",
                "phase": "Phase 6",
                "helpers": [
                    {
                        "key": "checksum",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
                    },
                    {
                        "key": "hexdump",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",
                    },
                ],
                "current_shared_replay_inventory": REQUIRED_EVIDENCE_REPLAYS,
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
                        "key": "checksum",
                        "current_perf_evidence": {
                            "cases": [
                                {"label": "64B"},
                                {"label": "1501B"},
                            ],
                            "linux_style_rerun_routes": [
                                "make -C zigux phase6-checksum-perf",
                                "make -C zigux phase6-perf",
                            ],
                        },
                    },
                    {
                        "key": "hexdump",
                        "current_perf_evidence": {
                            "cases": [
                                {"label": "16B-plain-g1"},
                                {"label": "32B-ascii-g2"},
                                {"label": "16B-ascii-g4"},
                                {"label": "16B-ascii-g8"},
                            ],
                            "linux_style_rerun_routes": [
                                "make -C zigux phase6-hexdump-perf",
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
                "`make -C zigux phase6-checksum-perf`",
                "`make -C zigux phase6-checksum-test`",
            ),
            "phase6-checksum-perf",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / CATALOG_PATH,
                "zigux/tests/phase6_hexdump_perf.zig",
                "zigux/tests/phase6_hexdump.zig",
            ),
            "phase6_hexdump",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / MAKEFILE_PATH,
                "phase6-hexdump-perf:",
                "phase6-hexdump-test:",
            ),
            "phase6-hexdump-perf:",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig"',
                '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum.zig"',
            ),
            "checksum dedicated_slowdown_replay drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                '"make -C zigux phase6-hexdump-perf"',
                '"make -C zigux phase6-hexdump-test"',
            ),
            "phase6-hexdump-perf",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"label": "1501B"',
                '"label": "1500B"',
            ),
            "checksum perf case drift",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"label": "32B-ascii-g2"',
                '"label": "32B-ascii-g4"',
            ),
            "hexdump perf case drift",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"make -C zigux phase6-checksum-perf"',
                '"make -C zigux phase6-checksum-test"',
            ),
            "phase6-checksum-perf",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / PARITY_MANIFEST_PATH,
                '"make -C zigux phase6-hexdump-perf"',
                '"make -C zigux phase6-hexdump-test"',
            ),
            "phase6-hexdump-perf",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: mutate_text(
                root / EVIDENCE_MANIFEST_PATH,
                '"packet": "phase6-helper-evidence"',
                '"packet": "phase6-helper-parity"',
            ),
            "unexpected packet id",
        )
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in self-test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=fail: {exc}")
        return 1

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
