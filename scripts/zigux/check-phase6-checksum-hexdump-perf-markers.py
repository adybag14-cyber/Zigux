#!/usr/bin/env python3
"""Guard the current Phase 6 checksum/hexdump perf inventory markers."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")

REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "current shared helper-evidence packet",
    "shared replay inventory",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-hexdump-perf",
]

REQUIRED_TESTS_SNIPPETS = [
    "current direct-readback Phase 6 shared packet",
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "keep current Phase 6 follow-through tied to those directly readable shared reminder surfaces",
]

REQUIRED_LAST_KNOWN_REPLAYS = [
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-perf",
]

SELF_TEST_CASE_COUNT = 11


class ValidationError(RuntimeError):
    """Raised when the shared perf-marker packet drifts."""



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



def require_helper_entry(manifest: dict[str, object], key: str, replay_path: str) -> None:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helper-evidence manifest is missing helpers[]")

    for helper in helpers:
        if not isinstance(helper, dict):
            continue
        if helper.get("key") != key:
            continue
        if helper.get("dedicated_slowdown_replay") != replay_path:
            raise ValidationError(
                "phase6 helper-evidence manifest drift for "
                f"{key}: expected dedicated_slowdown_replay={replay_path}"
            )
        return

    raise ValidationError(f"phase6 helper-evidence manifest is missing helper row: {key}")



def validate_manifest(path: Path) -> None:
    try:
        manifest = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ValidationError(f"phase6 helper-evidence manifest root is not an object: {path.as_posix()}")

    if manifest.get("packet") != "phase6-helper-evidence":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")
    if (
        manifest.get("lane_scope")
        != "shared helper-evidence rows and machine-readable manifest only"
    ):
        raise ValidationError(f"unexpected lane_scope in {path.as_posix()}")

    require_helper_entry(manifest, "checksum", "zigux/tests/phase6_checksum_perf.zig")
    require_helper_entry(manifest, "hexdump", "zigux/tests/phase6_hexdump_perf.zig")

    inventory = manifest.get("last_known_shared_replay_inventory")
    if not isinstance(inventory, list):
        raise ValidationError(
            f"missing last_known_shared_replay_inventory in {path.as_posix()}"
        )

    for replay in REQUIRED_LAST_KNOWN_REPLAYS:
        if replay not in inventory:
            raise ValidationError(
                f"missing expected Phase 6 perf replay marker in {path.as_posix()}: {replay}"
            )



def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / TESTS_README_PATH, REQUIRED_TESTS_SNIPPETS)
    validate_manifest(repo_root / MANIFEST_PATH)



def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def scaffold_repo(root: Path) -> None:
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write(root / TESTS_README_PATH, "\n".join(REQUIRED_TESTS_SNIPPETS) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-evidence",
                "phase": "Phase 6",
                "lane_scope": "shared helper-evidence rows and machine-readable manifest only",
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
                "last_known_shared_replay_inventory": REQUIRED_LAST_KNOWN_REPLAYS,
            },
            indent=2,
        )
        + "\n",
    )



def expect_failure(root: Path, mutate: callable, expected_fragment: str) -> None:
    mutate()
    try:
        validate(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected {expected_fragment!r} in validation error, got {str(exc)!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")



def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        def rewrite(path: Path, old: str, new: str) -> None:
            content = path.read_text(encoding="utf-8")
            path.write_text(content.replace(old, new, 1), encoding="utf-8")

        expect_failure(
            root,
            lambda: rewrite(root / SCRIPTS_README_PATH, "shared replay inventory", ""),
            "shared replay inventory",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(root / SCRIPTS_README_PATH, "make -C zigux phase6-checksum-perf", ""),
            "make -C zigux phase6-checksum-perf",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(root / SCRIPTS_README_PATH, "make -C zigux phase6-hexdump-perf", ""),
            "make -C zigux phase6-hexdump-perf",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(
                root / TESTS_README_PATH,
                "zigux/tests/phase6_helper_evidence_manifest.json",
                "",
            ),
            "zigux/tests/phase6_helper_evidence_manifest.json",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(root / MANIFEST_PATH, "\"packet\": \"phase6-helper-evidence\"", "\"packet\": \"phase6-helper-parity\""),
            "unexpected packet id",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(root / MANIFEST_PATH, "\"phase\": \"Phase 6\"", "\"phase\": \"Phase Six\""),
            "unexpected phase id",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(
                root / MANIFEST_PATH,
                "\"lane_scope\": \"shared helper-evidence rows and machine-readable manifest only\"",
                "\"lane_scope\": \"shared helper-evidence rows only\"",
            ),
            "unexpected lane_scope",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(
                root / MANIFEST_PATH,
                "\"dedicated_slowdown_replay\": \"zigux/tests/phase6_checksum_perf.zig\"",
                "\"dedicated_slowdown_replay\": \"zigux/tests/phase6_checksum.zig\"",
            ),
            "checksum",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(
                root / MANIFEST_PATH,
                "\"dedicated_slowdown_replay\": \"zigux/tests/phase6_hexdump_perf.zig\"",
                "\"dedicated_slowdown_replay\": \"zigux/tests/phase6_hexdump.zig\"",
            ),
            "hexdump",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(
                root / MANIFEST_PATH,
                "\"make -C zigux phase6-checksum-perf\",",
                "",
            ),
            "make -C zigux phase6-checksum-perf",
        )
        cases_run += 1

        scaffold_repo(root)
        expect_failure(
            root,
            lambda: rewrite(
                root / MANIFEST_PATH,
                "\"make -C zigux phase6-hexdump-perf\"",
                "\"make -C zigux phase6-hexdump-review\"",
            ),
            "make -C zigux phase6-hexdump-perf",
        )
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=pass")
    print(
        f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST_CASE_COUNT={cases_run}"
    )



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
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
