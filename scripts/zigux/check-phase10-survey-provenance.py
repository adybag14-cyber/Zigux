#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = {
    "closure": "zigux/tests/phase10_closure_manifest.json",
    "core": "zigux/tests/phase10_virtio_core_manifest.json",
    "ring": "zigux/tests/phase10_virtio_ring_manifest.json",
    "input": "zigux/tests/phase10_virtio_input_manifest.json",
    "mmio": "zigux/tests/phase10_virtio_mmio_manifest.json",
}


def read_json(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES.values() if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    closure = read_json(root, FILES["closure"])
    missing: list[str] = []

    survey_provenance = closure.get("survey_provenance")
    if not isinstance(survey_provenance, dict):
        missing.append("closure_manifest:survey_provenance")
        return [], missing

    if survey_provenance.get("source") != "manifest_derived":
        missing.append("closure_manifest:survey_provenance:source=manifest_derived")

    lane_keys = survey_provenance.get("lane_keys")
    if not isinstance(lane_keys, dict):
        missing.append("closure_manifest:survey_provenance:lane_keys")
    surveyed_commits = survey_provenance.get("surveyed_commits")
    if not isinstance(surveyed_commits, dict):
        missing.append("closure_manifest:survey_provenance:surveyed_commits")

    if not isinstance(lane_keys, dict) or not isinstance(surveyed_commits, dict):
        return [], missing

    for lane_name in ("core", "ring", "input", "mmio"):
        manifest = read_json(root, FILES[lane_name])
        closure_lane_key = lane_keys.get(lane_name)
        manifest_lane_key = manifest.get("lane_key")
        if closure_lane_key != manifest_lane_key:
            missing.append(
                f"closure_manifest:lane_key:{lane_name}={manifest_lane_key}"
            )

        closure_commit = surveyed_commits.get(lane_name)
        manifest_commit = manifest.get("surveyed_commit")
        if closure_commit != manifest_commit:
            missing.append(
                f"closure_manifest:surveyed_commit:{lane_name}={manifest_commit}"
            )
        if not isinstance(manifest_commit, str) or not HEX40.fullmatch(manifest_commit):
            missing.append(f"{lane_name}_manifest:surveyed_commit")

    return [], missing


def write_fixture(root: Path) -> None:
    fixture = {
        "core": {
            "lane_key": "P10-L01",
            "surveyed_commit": "a" * 40,
        },
        "ring": {
            "lane_key": "P10-L07",
            "surveyed_commit": "b" * 40,
        },
        "input": {
            "lane_key": "P10-L13",
            "surveyed_commit": "c" * 40,
        },
        "mmio": {
            "lane_key": "P10-L18",
            "surveyed_commit": "d" * 40,
        },
    }
    closure = {
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": {key: value["lane_key"] for key, value in fixture.items()},
            "surveyed_commits": {
                key: value["surveyed_commit"] for key, value in fixture.items()
            },
        }
    }

    for rel_path in FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    (root / FILES["closure"]).write_text(
        json.dumps(closure, indent=2) + "\n", encoding="utf-8"
    )
    for lane_name in ("core", "ring", "input", "mmio"):
        (root / FILES[lane_name]).write_text(
            json.dumps(fixture[lane_name], indent=2) + "\n", encoding="utf-8"
        )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-survey-provenance-self-test:{label}:unexpected_missing_files:"
            + ",".join(missing_files)
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-survey-provenance-self-test:{label}:expected_missing_marker:"
            f"{expected_marker}:actual:{actual}"
        )


def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-survey-provenance-self-test:{label}:unexpected_missing_markers:"
            + ",".join(missing_markers)
        )
    if expected_file not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            f"phase10-survey-provenance-self-test:{label}:expected_missing_file:"
            f"{expected_file}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_provenance_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-survey-provenance-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        ring_manifest_path = root / FILES["ring"]
        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["lane_key"] = "P10-L08"
        ring_manifest_path.write_text(
            json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8"
        )
        expect_missing_marker(
            "ring_lane_key_mismatch",
            root,
            "closure_manifest:lane_key:ring=P10-L08",
        )
        write_fixture(root)

        closure_path = root / FILES["closure"]
        closure = json.loads(closure_path.read_text(encoding="utf-8"))
        closure["survey_provenance"]["surveyed_commits"]["input"] = "e" * 40
        closure_path.write_text(
            json.dumps(closure, indent=2) + "\n", encoding="utf-8"
        )
        expect_missing_marker(
            "input_surveyed_commit_mismatch",
            root,
            "closure_manifest:surveyed_commit:input=cccccccccccccccccccccccccccccccccccccccc",
        )
        write_fixture(root)

        closure = json.loads(closure_path.read_text(encoding="utf-8"))
        closure["survey_provenance"]["source"] = "hand_written"
        closure_path.write_text(
            json.dumps(closure, indent=2) + "\n", encoding="utf-8"
        )
        expect_missing_marker(
            "source_marker",
            root,
            "closure_manifest:survey_provenance:source=manifest_derived",
        )
        write_fixture(root)

        mmio_manifest_path = root / FILES["mmio"]
        mmio_manifest = json.loads(mmio_manifest_path.read_text(encoding="utf-8"))
        mmio_manifest["surveyed_commit"] = "not-a-sha"
        mmio_manifest_path.write_text(
            json.dumps(mmio_manifest, indent=2) + "\n", encoding="utf-8"
        )
        expect_missing_marker(
            "mmio_bad_commit",
            root,
            "mmio_manifest:surveyed_commit",
        )
        write_fixture(root)

        (root / FILES["core"]).unlink()
        expect_missing_file("core_manifest_missing", root, FILES["core"])

    print("PHASE10_SURVEY_PROVENANCE_SELF_TEST=pass")
    print("PHASE10_SURVEY_PROVENANCE_SELF_TEST_CASE_COUNT=5")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_SURVEY_PROVENANCE=fail")
    print("MISSING_PHASE10_SURVEY_PROVENANCE_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_SURVEY_PROVENANCE_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_SURVEY_PROVENANCE=fail")
    print("MISSING_PHASE10_SURVEY_PROVENANCE_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_SURVEY_PROVENANCE_MARKERS_END")
    sys.exit(1)

print("PHASE10_SURVEY_PROVENANCE=pass")
print(f"PHASE10_SURVEY_PROVENANCE_REQUIRED_FILE_COUNT={len(FILES)}")
print("PHASE10_SURVEY_PROVENANCE_REQUIRED_MARKER_COUNT=13")