#!/usr/bin/env python3
"""Guard the current Phase 6 base64 fixture-backed packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

EXPECTED_SLICE_SNIPPETS = [
    "- helper-local corpus checker: `scripts/zigux/check-phase6-base64-corpus-determinism.py`",
    "- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 18 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`",
    "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
]

EXPECTED_FIXTURE_SURFACES = ["zigux/tests/fixtures/phase6_base64_vectors.zig"]
EXPECTED_CHECKER_SURFACES = ["scripts/zigux/check-phase6-base64-corpus-determinism.py"]
EXPECTED_MISSING_COMPANIONS = [
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
]
EXPECTED_PERF_EVIDENCE = {
    "case_labels": [
        "STD_PAD",
        "STD_NO_PAD",
        "URLSAFE_PAD",
        "URLSAFE_NO_PAD",
        "IMAP_PAD",
        "IMAP_NO_PAD",
    ],
    "iterations": 12000,
    "max_encode_slowdown_pct": 150,
    "max_decode_slowdown_pct": 325,
    "linux_style_rerun_routes": [
        "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
        "make -C zigux phase6-base64-perf",
        "make -C zigux phase6-perf",
    ],
}
SELF_TEST_CASES = 8


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
            raise ValidationError(f"missing expected base64 packet marker in {path.as_posix()}: {snippet}")


def find_helper(manifest: dict[str, object], key: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("helpers list missing")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper entry: {key}")


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SLICE_PATH, EXPECTED_SLICE_SNIPPETS)

    evidence = find_helper(read_json(repo_root / EVIDENCE_MANIFEST_PATH), "base64")
    parity = find_helper(read_json(repo_root / PARITY_MANIFEST_PATH), "base64")

    if evidence.get("fixture_surfaces") != EXPECTED_FIXTURE_SURFACES:
        raise ValidationError("base64 evidence fixture surface drift")
    if evidence.get("checker_surfaces") != EXPECTED_CHECKER_SURFACES:
        raise ValidationError("base64 evidence checker surface drift")
    if evidence.get("still_missing_direct_companions") != EXPECTED_MISSING_COMPANIONS:
        raise ValidationError("base64 evidence missing-companion drift")
    if evidence.get("slice_note") != "Documentation/zigux/phase6-base64-slice.md":
        raise ValidationError("base64 evidence slice-note drift")

    if parity.get("fixture_surfaces") != EXPECTED_FIXTURE_SURFACES:
        raise ValidationError("base64 parity fixture surface drift")
    if parity.get("checker_surfaces") != EXPECTED_CHECKER_SURFACES:
        raise ValidationError("base64 parity checker surface drift")
    if parity.get("still_missing_direct_companions") != EXPECTED_MISSING_COMPANIONS:
        raise ValidationError("base64 parity missing-companion drift")
    if parity.get("slice_note") != "Documentation/zigux/phase6-base64-slice.md":
        raise ValidationError("base64 parity slice-note drift")
    if parity.get("current_perf_evidence") != EXPECTED_PERF_EVIDENCE:
        raise ValidationError("base64 parity perf-evidence drift")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SLICE_PATH, "\n".join(["# Phase 6 Base64 Slice", *EXPECTED_SLICE_SNIPPETS]) + "\n")
    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "helpers": [
                    {
                        "key": "base64",
                        "fixture_surfaces": EXPECTED_FIXTURE_SURFACES,
                        "checker_surfaces": EXPECTED_CHECKER_SURFACES,
                        "still_missing_direct_companions": EXPECTED_MISSING_COMPANIONS,
                        "slice_note": "Documentation/zigux/phase6-base64-slice.md",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / PARITY_MANIFEST_PATH,
        json.dumps(
            {
                "helpers": [
                    {
                        "key": "base64",
                        "fixture_surfaces": EXPECTED_FIXTURE_SURFACES,
                        "checker_surfaces": EXPECTED_CHECKER_SURFACES,
                        "still_missing_direct_companions": EXPECTED_MISSING_COMPANIONS,
                        "slice_note": "Documentation/zigux/phase6-base64-slice.md",
                        "current_perf_evidence": EXPECTED_PERF_EVIDENCE,
                    }
                ]
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = read_text(path)
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path.as_posix()}: {old}")
    write(path, original.replace(old, new, 1))
    try:
        validate(root)
    except ValidationError:
        return
    finally:
        write(path, original)
    raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_base64_fixture_packet_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        expect_failure(root, SLICE_PATH, EXPECTED_SLICE_SNIPPETS[0], "- helper-local corpus checker: `scripts/zigux/check-phase6-base64-fixture-proof.py`")
        expect_failure(root, SLICE_PATH, EXPECTED_SLICE_SNIPPETS[1], "- exact fixture-owned corpus counts on current `master`: 21 standard encode cases only")
        expect_failure(root, EVIDENCE_MANIFEST_PATH, '"scripts/zigux/check-phase6-base64-corpus-determinism.py"', '"scripts/zigux/check-phase6-base64-corpus-proof.py"')
        expect_failure(root, EVIDENCE_MANIFEST_PATH, '"zigux/tests/fixtures/phase6_base64_c_harness.c"', '"zigux/tests/fixtures/phase6_base64_alt_harness.c"')
        expect_failure(root, PARITY_MANIFEST_PATH, '"zigux/tests/fixtures/phase6_base64_vectors.zig"', '"zigux/tests/fixtures/phase6_base64_vectors_v2.zig"')
        expect_failure(root, PARITY_MANIFEST_PATH, '"iterations": 12000', '"iterations": 9000')
        expect_failure(root, PARITY_MANIFEST_PATH, '"max_decode_slowdown_pct": 325', '"max_decode_slowdown_pct": 250')
        expect_failure(root, PARITY_MANIFEST_PATH, '"make -C zigux phase6-perf"', '"make -C zigux phase6-base64-test"')

    print("PHASE6_BASE64_FIXTURE_PACKET_SELF_TEST=pass")
    print(f"PHASE6_BASE64_FIXTURE_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASES}")


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
        print(f"PHASE6_BASE64_FIXTURE_PACKET=fail: {exc}")
        return 1

    print("PHASE6_BASE64_FIXTURE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
