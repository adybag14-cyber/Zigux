#!/usr/bin/env python3
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
    "primary snapshot replay parses surveyed_commit and asserts it is a "
    "lowercase 40-character hex SHA"
)
REVIEWABILITY_MARKERS = {
    "test_name": 'test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact"',
    "surveyed_commit_field": "surveyed_commit: []const u8,",
    "surveyed_commit_assertion": "try std.testing.expect(isHexSha(fixture.surveyed_commit));",
    "snapshot_fixture_path": SNAPSHOT_PATH.as_posix(),
    "snapshot_checker_blob_assertion": "277554397ab1a236c71f1dac9061ffe4cfbeaf67",
}
SELF_TEST_CASE_COUNT = 7


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_hex_sha(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 40:
        return False
    return all(ch in "0123456789abcdef" for ch in value)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def collect_missing(root: Path) -> list[str]:
    snapshot_path = root / SNAPSHOT_PATH
    reviewability_path = root / REVIEWABILITY_PATH
    missing: list[str] = []

    if not snapshot_path.exists():
        return [f"missing_file:{SNAPSHOT_PATH.as_posix()}"]
    if not reviewability_path.exists():
        missing.append(f"missing_file:{REVIEWABILITY_PATH.as_posix()}")
        return missing

    snapshot = load_json(snapshot_path)
    verification_evidence = snapshot.get("verification_evidence")
    if not isinstance(verification_evidence, dict):
        missing.append("snapshot:verification_evidence:shape")
        return missing

    reviewability_gate = verification_evidence.get("reviewability_gate")
    if not isinstance(reviewability_gate, dict):
        missing.append("snapshot:verification_evidence:reviewability_gate:shape")
        return missing

    if reviewability_gate.get("path") != REVIEWABILITY_PATH.as_posix():
        missing.append(
            "snapshot:verification_evidence:reviewability_gate:path:"
            f"{REVIEWABILITY_PATH.as_posix()}"
        )

    blob_sha = reviewability_gate.get("blob_sha")
    if not is_hex_sha(blob_sha):
        missing.append("snapshot:verification_evidence:reviewability_gate:blob_sha")
    elif blob_sha != git_blob_sha(reviewability_path):
        missing.append("snapshot:verification_evidence:reviewability_gate:blob_sha:mismatch")

    if reviewability_gate.get("evidence") != EXPECTED_EVIDENCE:
        missing.append("snapshot:verification_evidence:reviewability_gate:evidence")

    reviewability_text = reviewability_path.read_text(encoding="utf-8")
    for label, marker in REVIEWABILITY_MARKERS.items():
        if marker not in reviewability_text:
            missing.append(f"reviewability_gate:{label}")

    return missing


def write_fixture_tree(root: Path) -> None:
    reviewability_path = root / REVIEWABILITY_PATH
    reviewability_path.parent.mkdir(parents=True, exist_ok=True)
    reviewability_path.write_text(
        "\n".join(
            [
                'test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact" {',
                "    surveyed_commit: []const u8,",
                "    try std.testing.expect(isHexSha(fixture.surveyed_commit));",
                f'    _ = "{SNAPSHOT_PATH.as_posix()}";',
                '    _ = "277554397ab1a236c71f1dac9061ffe4cfbeaf67";',
                "}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot_path = root / SNAPSHOT_PATH
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(
            {
                "verification_evidence": {
                    "reviewability_gate": {
                        "path": REVIEWABILITY_PATH.as_posix(),
                        "blob_sha": git_blob_sha(reviewability_path),
                        "evidence": EXPECTED_EVIDENCE,
                    }
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def expect_case(root: Path, expected: str, case_name: str) -> None:
    missing = collect_missing(root)
    if expected not in missing:
        raise SystemExit(f"phase12-libbpf-reviewability-gate:self-test:{case_name}:{missing}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_reviewability_gate_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        if collect_missing(root) != []:
            raise SystemExit("phase12-libbpf-reviewability-gate:self-test:clean_fixture")

        (root / SNAPSHOT_PATH).unlink()
        expect_case(root, f"missing_file:{SNAPSHOT_PATH.as_posix()}", "missing_snapshot")
        write_fixture_tree(root)

        snapshot = load_json(root / SNAPSHOT_PATH)
        del snapshot["verification_evidence"]["reviewability_gate"]
        (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:shape", "gate_shape")
        write_fixture_tree(root)

        snapshot = load_json(root / SNAPSHOT_PATH)
        snapshot["verification_evidence"]["reviewability_gate"]["path"] = "zigux/tests/phase12_libbpf_other.zig"
        (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_case(
            root,
            f"snapshot:verification_evidence:reviewability_gate:path:{REVIEWABILITY_PATH.as_posix()}",
            "gate_path",
        )
        write_fixture_tree(root)

        snapshot = load_json(root / SNAPSHOT_PATH)
        snapshot["verification_evidence"]["reviewability_gate"]["blob_sha"] = "short-sha"
        (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:blob_sha", "gate_blob_sha")
        write_fixture_tree(root)

        snapshot = load_json(root / SNAPSHOT_PATH)
        snapshot["verification_evidence"]["reviewability_gate"]["blob_sha"] = f"{'0' * 40}"
        (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:blob_sha:mismatch", "gate_blob_sha_mismatch")
        write_fixture_tree(root)

        snapshot = load_json(root / SNAPSHOT_PATH)
        snapshot["verification_evidence"]["reviewability_gate"]["evidence"] = "surveyed_commit is present"
        (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_case(root, "snapshot:verification_evidence:reviewability_gate:evidence", "gate_evidence")
        write_fixture_tree(root)

        reviewability_text = (root / REVIEWABILITY_PATH).read_text(encoding="utf-8")
        (root / REVIEWABILITY_PATH).write_text(
            reviewability_text.replace(
                "    try std.testing.expect(isHexSha(fixture.surveyed_commit));\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_case(root, "reviewability_gate:surveyed_commit_assertion", "surveyed_commit_assertion")

    print("PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT_SELF_TEST=pass")
    print(f"PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 12 libbpf snapshot reviewability-gate evidence drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = collect_missing(args.root)
    if missing:
        print("PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT=pass")
    print(f"PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT_MARKER_COUNT={len(REVIEWABILITY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
