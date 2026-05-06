#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=docs_root_smoke_summary

Fail-closed checker for the docs-root summary of the shared Phase 14 smoke packet.
This companion checker keeps `Documentation/zigux/README.md` aligned with the
current study-only replay route, the shipped shared-smoke note surfaces, and the
manifest-backed checker inventory.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=docs_root_smoke_summary"
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
MAKEFILE_PATH = "zigux/Makefile"
MANIFEST_PATH = "zigux/tests/phase14_end_to_end_smoke_manifest.json"
CHECKER_PATH = "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
REQUIRED_MARKERS = [
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge.zig",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_survey.zig",
    "zigux/tests/phase14_rcu_tree_survey.zig",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/Makefile",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    docs_root_path = root / DOCS_ROOT_PATH
    if not docs_root_path.exists():
        return [f"missing file: {DOCS_ROOT_PATH}"]

    text = read_text(docs_root_path)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing marker in {DOCS_ROOT_PATH}: {marker}")

    smoke_survey_path = root / SMOKE_SURVEY_PATH
    if not smoke_survey_path.exists():
        errors.append(f"missing file: {SMOKE_SURVEY_PATH}")
    else:
        smoke_text = read_text(smoke_survey_path)
        if CHECKER_PATH not in smoke_text:
            errors.append(f"missing marker in {SMOKE_SURVEY_PATH}: {CHECKER_PATH}")

    makefile_path = root / MAKEFILE_PATH
    if not makefile_path.exists():
        errors.append(f"missing file: {MAKEFILE_PATH}")
    else:
        makefile_text = read_text(makefile_path)
        if CHECKER_PATH not in makefile_text:
            errors.append(f"missing marker in {MAKEFILE_PATH}: {CHECKER_PATH}")

    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        errors.append(f"missing file: {MANIFEST_PATH}")
    else:
        manifest = json.loads(read_text(manifest_path))
        surface_found = False
        for surface in manifest.get("surfaces", []):
            if not isinstance(surface, dict):
                continue
            if surface.get("path") == CHECKER_PATH and surface.get("required_marker") == MARKER:
                surface_found = True
                break
        if not surface_found:
            errors.append(
                "missing docs-root smoke-summary checker surface in zigux/tests/phase14_end_to_end_smoke_manifest.json"
            )

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        good_text = "\n".join(REQUIRED_MARKERS) + "\n"
        write_text(root / DOCS_ROOT_PATH, good_text)
        write_text(root / SMOKE_SURVEY_PATH, f"{CHECKER_PATH}\nmake -C zigux phase14-validate\n")
        write_text(root / MAKEFILE_PATH, f"phase14-validate:\n\tpython3 {CHECKER_PATH}\n")
        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "surfaces": [
                        {
                            "path": CHECKER_PATH,
                            "required_marker": MARKER,
                        }
                    ]
                },
                indent=2,
            ) + "\n",
        )

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken_path = root / DOCS_ROOT_PATH
        broken_path.write_text(
            good_text.replace(
                "scripts/zigux/check-phase14-release-boundary-exact-counts.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/README.md: "
            "scripts/zigux/check-phase14-release-boundary-exact-counts.py" in error
            for error in errors
        ):
            print(
                "self-test expected failure when the release-boundary checker marker drifted",
                file=sys.stderr,
            )
            return 1
        write_text(root / DOCS_ROOT_PATH, good_text)

        broken_smoke_path = root / SMOKE_SURVEY_PATH
        broken_smoke_path.write_text("make -C zigux phase14-validate\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any(
            f"missing marker in {SMOKE_SURVEY_PATH}: {CHECKER_PATH}" in error
            for error in errors
        ):
            print(
                "self-test expected failure when the shared smoke survey lost the docs-root checker marker",
                file=sys.stderr,
            )
            return 1
        write_text(root / SMOKE_SURVEY_PATH, f"{CHECKER_PATH}\nmake -C zigux phase14-validate\n")

        broken_makefile_path = root / MAKEFILE_PATH
        broken_makefile_path.write_text(
            "phase14-validate:\n\tpython3 scripts/zigux/validate-phase14.py\n",
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            f"missing marker in {MAKEFILE_PATH}: {CHECKER_PATH}" in error
            for error in errors
        ):
            print(
                "self-test expected failure when the Makefile lost the docs-root checker route",
                file=sys.stderr,
            )
            return 1
        write_text(root / MAKEFILE_PATH, f"phase14-validate:\n\tpython3 {CHECKER_PATH}\n")

        broken_manifest_path = root / MANIFEST_PATH
        broken_manifest_path.write_text(json.dumps({"surfaces": []}, indent=2) + "\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any(
            "missing docs-root smoke-summary checker surface" in error for error in errors
        ):
            print(
                "self-test expected failure when the manifest lost the docs-root checker surface",
                file=sys.stderr,
            )
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase14 docs-root smoke summary validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
