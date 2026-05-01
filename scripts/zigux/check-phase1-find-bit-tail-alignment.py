#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

REQUIRED_FILE_RELS = [
    Path("Documentation/zigux/phase1-closure.md"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    Path("zigux/tests/fixtures/phase1_helpers.json"),
    Path("zigux/tests/phase1_helpers.zig"),
]

REQUIRED_FIXTURE_KEYS = [
    "tail_clamped_first",
    "tail_clamped_next",
    "tail_zero_clamped_first",
    "tail_zero_clamped_next",
    "tail_and_clamped_first",
    "tail_and_clamped_next",
    "tail_and_mixed_first",
    "tail_and_mixed_next",
]

REQUIRED_HELPER_TEST_MARKERS = [
    "fixture.find_bit.tail_clamped_first",
    "fixture.find_bit.tail_clamped_next",
    "fixture.find_bit.tail_zero_clamped_first",
    "fixture.find_bit.tail_zero_clamped_next",
    "fixture.find_bit.tail_and_clamped_first",
    "fixture.find_bit.tail_and_clamped_next",
    "fixture.find_bit.tail_and_mixed_first",
    "fixture.find_bit.tail_and_mixed_next",
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_FIND_BIT_REVIEW=find_bit baseline set, zero, shared-bit, and tail-clamped scans ignore bits beyond nbits while preserving the in-range mixed-tail match",
    "PHASE1_FIND_BIT_SET_UNIT_REVIEW=find_bit same-word set-scan start masking keeps inclusive starts honest, skips earlier same-word set matches after the search advances, and still clamps tail results to nbits",
    "PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits",
    "PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range",
]

REQUIRED_MANIFEST_SUMMARY = (
    "Committed C-backed parity coverage includes baseline set, zero, and shared-bit scans plus "
    "tail-clamped set, zero, and AND searches, including the mixed-tail case where one shared bit "
    "remains in range while another lives past nbits."
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2) + "\n")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "zigux" / "check-phase1-find-bit-tail-alignment.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, root: Path, expected: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase1-find-bit-tail:self-test:{label}:unexpected_pass")
    if expected not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "none"
        raise SystemExit(
            f"phase1-find-bit-tail:self-test:{label}:expected_missing:{expected}:actual:{actual}"
        )


def create_fixture_root(root: Path) -> None:
    write_text(
        root / "Documentation" / "zigux" / "phase1-closure.md",
        "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / "zigux" / "tests" / "phase1_helpers.zig",
        "\n".join(REQUIRED_HELPER_TEST_MARKERS) + "\n",
    )
    write_json(
        root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json",
        {
            "find_bit": {key: 1 for key in REQUIRED_FIXTURE_KEYS},
        },
    )
    write_json(
        root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json",
        {
            "phase": "Phase 1",
            "status": "closed",
            "helper_review_notes": {
                "tools/lib/find_bit.zig": {
                    "fixture": "zigux/tests/fixtures/phase1_helpers.json",
                    "summary": REQUIRED_MANIFEST_SUMMARY,
                    "evidence_keys": [f"find_bit.{key}" for key in REQUIRED_FIXTURE_KEYS],
                }
            },
        },
    )
    write_text(
        root / "scripts" / "zigux" / "check-phase1-find-bit-tail-alignment.py",
        Path(__file__).read_text(encoding="utf-8"),
    )


def validate_tree(root: Path) -> tuple[int, list[str]]:
    missing: list[str] = []

    for rel in REQUIRED_FILE_RELS:
        if not (root / rel).exists():
            missing.append(f"file:{rel.as_posix()}")

    if missing:
        return 1, missing

    closure_text = read_text(root / "Documentation" / "zigux" / "phase1-closure.md")
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            missing.append(f"closure:{marker}")

    helper_text = read_text(root / "zigux" / "tests" / "phase1_helpers.zig")
    for marker in REQUIRED_HELPER_TEST_MARKERS:
        if marker not in helper_text:
            missing.append(f"phase1_helpers:{marker}")

    fixture = json.loads(read_text(root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json"))
    find_bit = fixture.get("find_bit")
    if not isinstance(find_bit, dict):
        missing.append("fixture:find_bit:expected_object")
    else:
        for key in REQUIRED_FIXTURE_KEYS:
            if key not in find_bit:
                missing.append(f"fixture:find_bit:{key}")

    manifest = json.loads(
        read_text(root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json")
    )
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase")
    if manifest.get("status") != "closed":
        missing.append("manifest:status")
    notes = manifest.get("helper_review_notes")
    if not isinstance(notes, dict):
        missing.append("manifest:helper_review_notes")
        return 1, missing

    find_bit_note = notes.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_note, dict):
        missing.append("manifest:tools/lib/find_bit.zig")
        return 1, missing
    if find_bit_note.get("fixture") != "zigux/tests/fixtures/phase1_helpers.json":
        missing.append("manifest:find_bit.fixture")
    if find_bit_note.get("summary") != REQUIRED_MANIFEST_SUMMARY:
        missing.append("manifest:find_bit.summary")
    evidence_keys = find_bit_note.get("evidence_keys")
    if not isinstance(evidence_keys, list):
        missing.append("manifest:find_bit.evidence_keys")
    else:
        for key in [f"find_bit.{key}" for key in REQUIRED_FIXTURE_KEYS]:
            if key not in evidence_keys:
                missing.append(f"manifest:find_bit.evidence_keys:{key}")

    return (1 if missing else 0), missing


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_tail_") as tmp_dir:
        root = Path(tmp_dir)
        create_fixture_root(root)

        code, missing = validate_tree(root)
        if code != 0:
            raise SystemExit(
                "phase1-find-bit-tail:self-test:baseline_failed:" + ",".join(missing)
            )

        helper_path = root / "zigux" / "tests" / "phase1_helpers.zig"
        original_helper = read_text(helper_path)
        helper_path.write_text(
            original_helper.replace("fixture.find_bit.tail_zero_clamped_next", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "helper_marker",
            root,
            "phase1_helpers:fixture.find_bit.tail_zero_clamped_next",
        )
        helper_path.write_text(original_helper, encoding="utf-8")

        fixture_path = root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json"
        fixture = json.loads(read_text(fixture_path))
        del fixture["find_bit"]["tail_and_clamped_next"]
        write_json(fixture_path, fixture)
        expect_missing("fixture_key", root, "fixture:find_bit:tail_and_clamped_next")
        create_fixture_root(root)

        manifest_path = root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
        manifest = json.loads(read_text(manifest_path))
        manifest["helper_review_notes"]["tools/lib/find_bit.zig"]["evidence_keys"].remove(
            "find_bit.tail_and_mixed_first"
        )
        write_json(manifest_path, manifest)
        expect_missing(
            "manifest_evidence_key",
            root,
            "manifest:find_bit.evidence_keys:find_bit.tail_and_mixed_first",
        )
        create_fixture_root(root)

        closure_path = root / "Documentation" / "zigux" / "phase1-closure.md"
        original_closure = read_text(closure_path)
        closure_path.write_text(
            original_closure.replace(
                "PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "closure_marker",
            root,
            "closure:PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits",
        )

    print("PHASE1_FIND_BIT_TAIL_ALIGNMENT_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_TAIL_ALIGNMENT_SELF_TEST_CASE_COUNT=4")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())

    code, missing = validate_tree(ROOT)
    if code != 0:
        print("PHASE1_FIND_BIT_TAIL_ALIGNMENT=fail")
        print("MISSING_PHASE1_FIND_BIT_TAIL_ALIGNMENT_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FIND_BIT_TAIL_ALIGNMENT_END")
        raise SystemExit(1)

    print("PHASE1_FIND_BIT_TAIL_ALIGNMENT=pass")
    print(f"PHASE1_FIND_BIT_TAIL_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    print(
        "PHASE1_FIND_BIT_TAIL_MARKER_COUNT="
        f"{len(REQUIRED_FIXTURE_KEYS) + len(REQUIRED_HELPER_TEST_MARKERS) + len(REQUIRED_CLOSURE_MARKERS) + 3}"
    )
