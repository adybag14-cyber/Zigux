#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the current Phase 14 release-boundary packet.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"
CHECKER_PATH = "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
DOCS_ROOT_CHECKER_PATH = "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
PHASE14_SECTION_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"
ROADMAP_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "net/core/skbuff.c",
    "kernel/rcu/tree.c",
]
FREEZE_IN_C_ANCHORS = [
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
]
STUDY_ONLY_ANCHORS = [
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
]
EXPECTED_COMPILE_SHARDS = [
    {
        "label": "phase14-workqueue-bridge-tests",
        "root_source": "phase14_workqueue_bridge.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-workqueue-reviewability-tests",
        "root_source": "phase14_workqueue_reviewability.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-skbuff-bridge-tests",
        "root_source": "phase14_skbuff_bridge.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-ring-buffer-survey-tests",
        "root_source": "phase14_ring_buffer_survey.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-rcu-tree-survey-tests",
        "root_source": "phase14_rcu_tree_survey.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-end-to-end-smoke-tests",
        "root_source": "phase14_end_to_end_smoke_survey.zig",
        "coverage": "focused_and_full_bundle",
    },
]
RELEASE_BOUNDARY_MARKERS = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-workqueue-reviewability-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "bounded-internal sequencing guard: only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain eligible",
    "combined shared replay entrypoint: `make -C zigux phase14`",
    "wrapper-backed full-bundle replay: `make -C zigux phase14-test`",
    "`kernel/rcu/tree.c`: remains blocked from active delivery",
    "`net/core/skbuff.c`: remains blocked from active delivery",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
]
SURVEY_EXACT_COUNT_MARKERS = [
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "PHASE14_TEST_ENTRYPOINT=make -C zigux phase14-test",
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14",
    "PHASE14_ANCHOR_PACKET_COUNT=4",
]
MANIFEST_REQUIRED_SURFACES = [
    DOCS_ROOT_CHECKER_PATH,
    CHECKER_PATH,
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/validate-phase14.py",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    active = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            active = True
        elif active and stripped.startswith("## "):
            break
        if active:
            collected.append(line)
    if not collected:
        return None
    return "\n".join(collected) + "\n"


def extract_bullets(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    active = False
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            active = True
            continue
        if not active:
            continue
        if bullets and stripped and not stripped.startswith("- "):
            break
        if stripped.startswith("- "):
            bullets.append(stripped[2:])
    return bullets


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def check_manifest(errors: list[str], root: Path) -> None:
    path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(root).as_posix()}")
        return
    try:
        manifest = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {path.relative_to(root).as_posix()}: {exc}")
        return
    surfaces = manifest.get("shared_smoke_surfaces")
    if not isinstance(surfaces, list):
        errors.append("phase14 shared_smoke_surfaces payload is not a list")
        return
    for surface in MANIFEST_REQUIRED_SURFACES:
        count = surfaces.count(surface)
        if count != 1:
            errors.append(
                f"phase14 shared_smoke_surfaces drift for {surface} (expected 1, found {count})"
            )
    productization = manifest.get("productization")
    if not isinstance(productization, dict):
        errors.append("phase14 manifest productization payload is not an object")
    else:
        if productization.get("status_bucket") != "study_only":
            errors.append("phase14 manifest status_bucket drifted from study_only")
        if productization.get("rollback_owner") != "Repo Tooling Pod":
            errors.append("phase14 manifest rollback_owner drifted from Repo Tooling Pod")
    anchor_packets = manifest.get("anchor_packets")
    if not isinstance(anchor_packets, list) or len(anchor_packets) != 4:
        errors.append("phase14 manifest anchor_packets drifted from the expected four-entry packet")
    compile_shards = manifest.get("compile_shards")
    if compile_shards != EXPECTED_COMPILE_SHARDS:
        errors.append("phase14 manifest compile_shards drifted from the expected shared matrix")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    release_path = root / "Documentation/zigux/phase14-release-boundary-survey.md"
    survey_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    freeze_map_path = root / "Documentation/zigux/freeze-map.md"
    roadmap_path = root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
    for path in (release_path, survey_path, freeze_map_path, roadmap_path):
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(root).as_posix()}")
    if errors:
        return errors

    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")

    release_text = read_text(release_path)
    survey_text = read_text(survey_path)
    freeze_map_text = read_text(freeze_map_path)
    roadmap_text = read_text(roadmap_path)

    require_exact_count(
        errors,
        release_path.relative_to(root).as_posix(),
        release_text,
        RELEASE_BOUNDARY_MARKERS,
    )
    require_exact_count(
        errors,
        survey_path.relative_to(root).as_posix(),
        survey_text,
        SURVEY_EXACT_COUNT_MARKERS,
    )

    phase14_section = extract_section(roadmap_text, PHASE14_SECTION_HEADING)
    if phase14_section is None:
        errors.append("missing Phase 14 roadmap section in zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
    else:
        anchors = extract_bullets(phase14_section, "Primary Linux anchors:")
        if anchors != ROADMAP_ANCHORS:
            errors.append("roadmap Phase 14 anchor list drifted from the shared smoke packet")

    freeze_anchors = extract_bullets(freeze_map_text, "## Freeze In C Initially")
    if freeze_anchors != FREEZE_IN_C_ANCHORS:
        errors.append("freeze-map freeze-in-C anchors drifted from the expected four-entry set")
    study_anchors = extract_bullets(freeze_map_text, "## Study / Boundary Only")
    if study_anchors != STUDY_ONLY_ANCHORS:
        errors.append("freeze-map study-only anchors drifted from the expected two-entry set")

    check_manifest(errors, root)
    return errors


def good_release_boundary_text() -> str:
    return "\n".join(f"- `{marker}`" if marker.startswith("PHASE14_") else f"- {marker}" for marker in RELEASE_BOUNDARY_MARKERS) + "\n"


def good_survey_text() -> str:
    return "\n".join(f"- `{marker}`" for marker in SURVEY_EXACT_COUNT_MARKERS) + "\n"


def good_freeze_map_text() -> str:
    return "\n".join(
        [
            "# Freeze Map",
            "",
            "## Freeze In C Initially",
            *[f"- {item}" for item in FREEZE_IN_C_ANCHORS],
            "",
            "## Study / Boundary Only",
            *[f"- {item}" for item in STUDY_ONLY_ANCHORS],
            "",
        ]
    )


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "## Phase 3: ABI and Interop Substrate",
            "Primary Linux anchors:",
            "- rust/exports.c",
            "",
            PHASE14_SECTION_HEADING,
            "Primary Linux anchors:",
            *[f"- {item}" for item in ROADMAP_ANCHORS],
            "",
        ]
    )


def good_manifest_text() -> str:
    return (
        json.dumps(
            {
                "productization": {
                    "status_bucket": "study_only",
                    "rollback_owner": "Repo Tooling Pod",
                },
                "shared_smoke_surfaces": MANIFEST_REQUIRED_SURFACES,
                "anchor_packets": [{}, {}, {}, {}],
                "compile_shards": EXPECTED_COMPILE_SHARDS,
            },
            indent=2,
        )
        + "\n"
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        current_checker_path = Path(__file__)
        original_source = read_text(current_checker_path)

        write_text(root / "Documentation/zigux/phase14-release-boundary-survey.md", good_release_boundary_text())
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", good_survey_text())
        write_text(root / "Documentation/zigux/freeze-map.md", good_freeze_map_text())
        write_text(root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", good_roadmap_text())
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", good_manifest_text())

        if errors := check(root):
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        write_text(
            root / "Documentation/zigux/phase14-release-boundary-survey.md",
            good_release_boundary_text().replace("- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`\n", "", 1),
        )
        if not any("PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0" in error for error in check(root)):
            print("self-test expected missing active-delivery marker failure", file=sys.stderr)
            return 1
        write_text(root / "Documentation/zigux/phase14-release-boundary-survey.md", good_release_boundary_text())

        write_text(
            root / "Documentation/zigux/phase14-release-boundary-survey.md",
            good_release_boundary_text().replace(
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n",
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n",
                1,
            ),
        )
        if not any("PHASE14_SHARED_SMOKE_GATE_COUNT=1" in error for error in check(root)):
            print("self-test expected duplicate shared-smoke gate marker failure", file=sys.stderr)
            return 1
        write_text(root / "Documentation/zigux/phase14-release-boundary-survey.md", good_release_boundary_text())

        write_text(
            root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
            good_survey_text().replace("- `PHASE14_TEST_ENTRYPOINT=make -C zigux phase14-test`\n", "", 1),
        )
        if not any("PHASE14_TEST_ENTRYPOINT=make -C zigux phase14-test" in error for error in check(root)):
            print("self-test expected missing survey test-entrypoint failure", file=sys.stderr)
            return 1
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", good_survey_text())

        write_text(
            root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
            good_survey_text().replace("- `PHASE14_ANCHOR_PACKET_COUNT=4`\n", "", 1),
        )
        if not any("PHASE14_ANCHOR_PACKET_COUNT=4" in error for error in check(root)):
            print("self-test expected missing survey anchor-count failure", file=sys.stderr)
            return 1
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", good_survey_text())

        write_text(
            root / "Documentation/zigux/freeze-map.md",
            good_freeze_map_text().replace("- `kernel/trace/ring_buffer.c`\n", "", 1),
        )
        if not any("freeze-map study-only anchors drifted" in error for error in check(root)):
            print("self-test expected freeze-map study-only drift failure", file=sys.stderr)
            return 1
        write_text(root / "Documentation/zigux/freeze-map.md", good_freeze_map_text())

        write_text(
            root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
            good_roadmap_text().replace("- net/core/skbuff.c\n", "", 1),
        )
        if not any("roadmap Phase 14 anchor list drifted" in error for error in check(root)):
            print("self-test expected roadmap anchor drift failure", file=sys.stderr)
            return 1
        write_text(root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", good_roadmap_text())

        write_text(
            root / "zigux/tests/phase14_end_to_end_smoke_manifest.json",
            json.dumps({"shared_smoke_surfaces": []}, indent=2) + "\n",
        )
        if not any(
            f"phase14 shared_smoke_surfaces drift for {CHECKER_PATH} (expected 1, found 0)"
            in error
            for error in check(root)
        ):
            print("self-test expected manifest surface drift failure", file=sys.stderr)
            return 1
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", good_manifest_text())

        manifest = json.loads(good_manifest_text())
        manifest["compile_shards"] = EXPECTED_COMPILE_SHARDS[:-1]
        write_text(
            root / "zigux/tests/phase14_end_to_end_smoke_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        if "phase14 manifest compile_shards drifted from the expected shared matrix" not in check(root):
            print("self-test expected compile-shard matrix drift failure", file=sys.stderr)
            return 1
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", good_manifest_text())

        write_text(
            current_checker_path,
            original_source.replace(MARKER, "PHASE14_CHECK_PACKET=broken_marker"),
        )
        if "checker marker missing from checker source" not in check(root):
            print("self-test expected checker-source marker failure", file=sys.stderr)
            write_text(current_checker_path, original_source)
            return 1
        write_text(current_checker_path, original_source)

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=9")
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

    print("phase14 release-boundary exact counts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
