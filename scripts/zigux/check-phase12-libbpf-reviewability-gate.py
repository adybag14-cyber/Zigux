#!/usr/bin/env python3
"""Fail closed on the Phase 12 libbpf snapshot reviewability gate evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent.parent.parent if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SNAPSHOT_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")
REVIEWABILITY_PATH = Path("zigux/tests/phase12_libbpf_reviewability.zig")

EXPECTED_EVIDENCE = (
    "primary snapshot replay parses surveyed_commit and asserts it is a lowercase "
    "40-character hex SHA"
)
SELF_TEST_CASE_COUNT = 7


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def is_hex_sha(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 40:
        return False
    return all(ch in "0123456789abcdef" for ch in value)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_missing(root: Path) -> list[str]:
    missing: list[str] = []
    snapshot_path = root / SNAPSHOT_PATH
    reviewability_path = root / REVIEWABILITY_PATH

    if not snapshot_path.exists():
        return [f"missing_file:{SNAPSHOT_PATH.as_posix()}"]
    if not reviewability_path.exists():
        return [f"missing_file:{REVIEWABILITY_PATH.as_posix()}"]

    packet = load_json(snapshot_path)
    verification = packet.get("verification_evidence")
    if not isinstance(verification, dict):
        return ["snapshot:verification_evidence:shape"]

    gate = verification.get("reviewability_gate")
    if not isinstance(gate, dict):
        return ["snapshot:verification_evidence:reviewability_gate:shape"]

    if gate.get("path") != REVIEWABILITY_PATH.as_posix():
        missing.append(
            "snapshot:verification_evidence:reviewability_gate:path:"
            f"{REVIEWABILITY_PATH.as_posix()}"
        )

    gate_blob = gate.get("blob_sha")
    if not is_hex_sha(gate_blob):
        missing.append("snapshot:verification_evidence:reviewability_gate:blob_sha")
    elif gate_blob != git_blob_sha(reviewability_path):
        missing.append("snapshot:verification_evidence:reviewability_gate:blob_sha:mismatch")

    if gate.get("evidence") != EXPECTED_EVIDENCE:
        missing.append("snapshot:verification_evidence:reviewability_gate:evidence")

    reviewability_text = reviewability_path.read_text(encoding="utf-8")
    for marker in (
        'test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact"',
        "try std.testing.expect(isHexSha(fixture.surveyed_commit));",
        "try std.testing.expectEqualStrings(expected_path, file_entry.path);",
    ):
        if marker not in reviewability_text:
            missing.append(f"reviewability_gate:missing_marker:{marker}")

    return missing


def write_fixture(root: Path) -> None:
    reviewability_path = root / REVIEWABILITY_PATH
    reviewability_path.parent.mkdir(parents=True, exist_ok=True)
    reviewability_path.write_text(
        "\n".join(
            [
                'test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact" {',
                "    try std.testing.expect(isHexSha(fixture.surveyed_commit));",
                "    try std.testing.expectEqualStrings(expected_path, file_entry.path);",
                "}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot = {
        "verification_evidence": {
            "reviewability_gate": {
                "checked_at_utc": "2026-05-29T18:55:00Z",
                "path": REVIEWABILITY_PATH.as_posix(),
                "blob_sha": git_blob_sha(reviewability_path),
                "evidence": EXPECTED_EVIDENCE,
            }
        }
    }
    snapshot_path = root / SNAPSHOT_PATH
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


def expect_case(root: Path, expected: str, case: str) -> None:
    missing = collect_missing(root)
    if expected not in missing:
        raise SystemExit(f"phase12-libbpf-reviewability-gate:self-test:{case}:{missing}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_reviewability_gate_") as tmp:
        root = Path(tmp)
        write_fixture(root)
        if collect_missing(root) != []:
            raise SystemExit("phase12-libbpf-reviewability-gate:self-test:clean_fixture")

        packet = load_json(root / SNAPSHOT_PATH)
        packet["verification_evidence"].pop("reviewability_gate")
        (root / SNAPSHOT_PATH).write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:shape", "missing_gate")
        write_fixture(root)

        packet = load_json(root / SNAPSHOT_PATH)
        packet["verification_evidence"]["reviewability_gate"]["path"] = "zigux/tests/other.zig"
        (root / SNAPSHOT_PATH).write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        expect_case(
            root,
            "snapshot:verification_evidence:reviewability_gate:path:"
            f"{REVIEWABILITY_PATH.as_posix()}",
            "gate_path",
        )
        write_fixture(root)

        packet = load_json(root / SNAPSHOT_PATH)
        packet["verification_evidence"]["reviewability_gate"]["blob_sha"] = "not-a-sha"
        (root / SNAPSHOT_PATH).write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:blob_sha", "gate_blob_shape")
        write_fixture(root)

        packet = load_json(root / SNAPSHOT_PATH)
        packet["verification_evidence"]["reviewability_gate"]["blob_sha"] = "1" * 40
        (root / SNAPSHOT_PATH).write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:blob_sha:mismatch", "gate_blob_mismatch")
        write_fixture(root)

        packet = load_json(root / SNAPSHOT_PATH)
        packet["verification_evidence"]["reviewability_gate"]["evidence"] = "stale wording"
        (root / SNAPSHOT_PATH).write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:evidence", "gate_evidence")
        write_fixture(root)

        (root / REVIEWABILITY_PATH).write_text("missing markers\n", encoding="utf-8")
        expect_case(
            root,
            'reviewability_gate:missing_marker:test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact"',
            "reviewability_marker",
        )

    print("PHASE12_LIBBPF_REVIEWABILITY_GATE_SELF_TEST=pass")
    print(f"PHASE12_LIBBPF_REVIEWABILITY_GATE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 12 libbpf snapshot reviewability gate evidence."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = collect_missing(args.root)
    if missing:
        print("PHASE12_LIBBPF_REVIEWABILITY_GATE=fail")
        print("PHASE12_LIBBPF_REVIEWABILITY_GATE_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_REVIEWABILITY_GATE_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_REVIEWABILITY_GATE=pass")
    print(f"PHASE12_LIBBPF_REVIEWABILITY_GATE_PATH={REVIEWABILITY_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
