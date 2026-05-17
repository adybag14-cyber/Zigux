#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-libbpf-bridge-status.py"
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"

REQUIRED_FILES = (
    MANIFEST_PATH,
    SURVEY_PATH,
    TEST_PATH,
)

EXPECTED_SEGMENT_STATUSES = {
    "fdinfo-map-info-helpers": "ready_next",
    "map-reuse-compatibility": "starter_landed",
    "file-path-and-handle-bridge": "deferred_high_risk",
}

REQUIRED_SURVEY_MARKERS = (
    "map-reuse-compatibility",
    "fdinfo-map-info-helpers",
    "file-path-and-handle-bridge",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_manifest(root: Path) -> dict:
    return json.loads(read_text(root, MANIFEST_PATH))


def validate(root: Path) -> list[str]:
    problems: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    manifest = read_manifest(root)
    segments = manifest.get("segments")
    if not isinstance(segments, list):
        problems.append("invalid-manifest:segments")
        return problems

    statuses_by_slug: dict[str, str] = {}
    for segment in segments:
        if not isinstance(segment, dict):
            problems.append("invalid-manifest:segment-entry")
            continue
        slug = segment.get("slug")
        status = segment.get("status")
        if isinstance(slug, str) and isinstance(status, str):
            statuses_by_slug[slug] = status

    for slug, expected_status in EXPECTED_SEGMENT_STATUSES.items():
        actual_status = statuses_by_slug.get(slug)
        if actual_status is None:
            problems.append(f"missing-segment:{slug}")
            continue
        if actual_status != expected_status:
            problems.append(
                f"unexpected-status:{slug}:expected={expected_status}:actual={actual_status}"
            )

    survey_text = read_text(root, SURVEY_PATH)
    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey_text:
            problems.append(f"missing-marker:{SURVEY_PATH}:{marker}")

    return problems


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    write_text(
        root,
        MANIFEST_PATH,
        json.dumps(
            {
                "segments": [
                    {
                        "slug": "fdinfo-map-info-helpers",
                        "status": "ready_next",
                    },
                    {
                        "slug": "map-reuse-compatibility",
                        "status": "starter_landed",
                    },
                    {
                        "slug": "file-path-and-handle-bridge",
                        "status": "deferred_high_risk",
                    },
                ]
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_text(
        root,
        SURVEY_PATH,
        "\n".join(REQUIRED_SURVEY_MARKERS) + "\n",
    )
    write_text(root, TEST_PATH, 'test "phase 8 libbpf segment manifest records the current helper-first catalog" {}\n')


def assert_missing_case(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    text = read_text(root, rel_path)
    if old not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{old}")
    (root / rel_path).write_text(text.replace(old, new, 1), encoding="utf-8")
    problems = validate(root)
    if expected not in problems:
        raise SystemExit(f"self-test-mismatch:{expected}:{problems}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_bridge_status_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = validate(baseline_root)
        if baseline:
            raise SystemExit(f"self-test-baseline-failed:{baseline}")

        wrong_status_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, wrong_status_root)
        assert_missing_case(
            wrong_status_root,
            MANIFEST_PATH,
            '"status": "starter_landed"',
            '"status": "ready_next"',
            "unexpected-status:map-reuse-compatibility:expected=starter_landed:actual=ready_next",
        )
        cases += 1

        missing_segment_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_segment_root)
        manifest = read_manifest(missing_segment_root)
        manifest["segments"] = [
            segment
            for segment in manifest["segments"]
            if segment["slug"] != "file-path-and-handle-bridge"
        ]
        write_text(
            missing_segment_root,
            MANIFEST_PATH,
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )
        missing_segment_problems = validate(missing_segment_root)
        expected_missing_segment = "missing-segment:file-path-and-handle-bridge"
        if expected_missing_segment not in missing_segment_problems:
            raise SystemExit(
                f"self-test-missing-segment-mismatch:{missing_segment_problems}"
            )
        cases += 1

        missing_marker_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_marker_root)
        assert_missing_case(
            missing_marker_root,
            SURVEY_PATH,
            "map-reuse-compatibility",
            "map reuse compatibility",
            f"missing-marker:{SURVEY_PATH}:map-reuse-compatibility",
        )
        cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / TEST_PATH).unlink()
        missing_file_problems = validate(missing_file_root)
        expected_missing_file = f"missing-file:{TEST_PATH}"
        if expected_missing_file not in missing_file_problems:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_file_problems}")
        cases += 1

    print("PHASE8_LIBBPF_BRIDGE_STATUS_SELF_TEST=pass")
    print(f"PHASE8_LIBBPF_BRIDGE_STATUS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_LIBBPF_BRIDGE_STATUS=fail")
        print("PHASE8_LIBBPF_BRIDGE_STATUS_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_LIBBPF_BRIDGE_STATUS_PROBLEMS_END")
        return 1

    print("PHASE8_LIBBPF_BRIDGE_STATUS=pass")
    print(f"PHASE8_LIBBPF_BRIDGE_STATUS_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
