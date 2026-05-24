#!/usr/bin/env python3
"""Guard the current Phase 6 checksum/hexdump evidence rerun routes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PHASE = "Phase 6"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-24"
EXPECTED_CHECKSUM_ROUTES = [
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_ROUTES = [
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
SELF_TEST_CASE_COUNT = 6


class ValidationError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, object]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return parsed


def get_helper(manifest: dict[str, object], key: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("helpers list missing")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper row: {key}")


def require_routes(helper: dict[str, object], key: str, expected_routes: list[str]) -> None:
    perf = helper.get("current_perf_evidence")
    if not isinstance(perf, dict):
        raise ValidationError(f"{key} current_perf_evidence missing")
    routes = perf.get("linux_style_rerun_routes")
    if routes != expected_routes:
        raise ValidationError(f"{key} evidence rerun routes drifted")


def validate(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase6 helper-evidence packet drifted")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 helper-evidence phase drifted")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("phase6 helper-evidence surveyed_head drifted")
    require_routes(get_helper(manifest, "checksum"), "checksum", EXPECTED_CHECKSUM_ROUTES)
    require_routes(get_helper(manifest, "hexdump"), "hexdump", EXPECTED_HEXDUMP_ROUTES)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "helpers": [
                    {
                        "key": "checksum",
                        "current_perf_evidence": {
                            "linux_style_rerun_routes": EXPECTED_CHECKSUM_ROUTES,
                        },
                    },
                    {
                        "key": "hexdump",
                        "current_perf_evidence": {
                            "linux_style_rerun_routes": EXPECTED_HEXDUMP_ROUTES,
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def rewrite_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def expect_failure(root: Path, mutate, expected_fragment: str) -> None:
    mutate()
    try:
        validate(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r} in {str(exc)!r}") from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_checksum_hexdump_routes_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0

        expect_failure(
            root,
            lambda: rewrite_json(root / MANIFEST_PATH, lambda data: data.update({"surveyed_head": "current-master-readback-2026-05-21"})),
            "surveyed_head drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: rewrite_json(root / MANIFEST_PATH, lambda data: data["helpers"][0]["current_perf_evidence"].update({"linux_style_rerun_routes": EXPECTED_CHECKSUM_ROUTES[:-1]})),
            "checksum evidence rerun routes drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: rewrite_json(root / MANIFEST_PATH, lambda data: data["helpers"][0]["current_perf_evidence"].update({"linux_style_rerun_routes": EXPECTED_CHECKSUM_ROUTES[:-1] + ["make -C zigux phase6-checksum-test"]})),
            "checksum evidence rerun routes drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: rewrite_json(root / MANIFEST_PATH, lambda data: data["helpers"][1]["current_perf_evidence"].update({"linux_style_rerun_routes": EXPECTED_HEXDUMP_ROUTES[:-1]})),
            "hexdump evidence rerun routes drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: rewrite_json(root / MANIFEST_PATH, lambda data: data["helpers"][1]["current_perf_evidence"].update({"linux_style_rerun_routes": EXPECTED_HEXDUMP_ROUTES[:-1] + ["make -C zigux phase6-hexdump-test"]})),
            "hexdump evidence rerun routes drifted",
        )
        cases_run += 1
        scaffold_repo(root)

        expect_failure(
            root,
            lambda: rewrite_json(root / MANIFEST_PATH, lambda data: data["helpers"].pop()),
            "missing helper row: hexdump",
        )
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_CHECKSUM_HEXDUMP_EVIDENCE_RERUN_ROUTES_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_EVIDENCE_RERUN_ROUTES_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE6_CHECKSUM_HEXDUMP_EVIDENCE_RERUN_ROUTES=fail: {exc}")
        return 1
    print("PHASE6_CHECKSUM_HEXDUMP_EVIDENCE_RERUN_ROUTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
