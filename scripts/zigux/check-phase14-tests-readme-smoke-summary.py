#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=tests_readme_smoke_summary

Fail-closed checker for the current tests-root summary of the shared Phase 14
smoke packet.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=tests_readme_smoke_summary"
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SMOKE_MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
TESTS_README_PACKET_ANCHOR = "  * `zigux/tests/phase14_build.zig`"
TESTS_README_PHASE14_PREFIX = "  * `zigux/tests/phase14_"
TESTS_README_PACKET_LINES = [
    "  * `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "  * `zigux/tests/phase14_workqueue_reviewability.zig`",
    "  * `zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "  * `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "  * `zigux/tests/phase14_ring_buffer_manifest.json`",
    "  * `zigux/tests/phase14_rcu_tree_manifest.json`",
]
TESTS_README_COMPILE_SHARD_LINES = [
    "  * `zigux/tests/phase14_ring_buffer_survey.zig`",
    "  * `zigux/tests/phase14_rcu_tree_survey.zig`",
    "  * `zigux/tests/phase14_skbuff_bridge.zig`",
    "  * `zigux/tests/phase14_workqueue_bridge.zig`",
    "  * `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
]
TESTS_README_AFTER_ANCHOR_LINES = (
    TESTS_README_PACKET_LINES + TESTS_README_COMPILE_SHARD_LINES
)
TESTS_README_ROUTE_MARKERS = [
    "make -C zigux phase14-smoke",
]
SCRIPTS_README_MARKERS = [
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
]
REQUIRED_SHARED_SMOKE_SURFACES = [
    "zigux/tests/README.md",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_workqueue_reviewability.zig",
]
REQUIRED_ANCHOR_MANIFESTS = [
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
]
EXPECTED_ANCHOR_PACKET_COUNT = len(REQUIRED_ANCHOR_MANIFESTS)
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def require_exact_line_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def require_lines_after_anchor(
    errors: list[str],
    rel_path: str,
    text: str,
    anchor_line: str,
    expected_lines: list[str],
    label: str,
) -> None:
    lines = text.splitlines()
    anchor_count = sum(1 for line in lines if line == anchor_line)
    if anchor_count != 1:
        errors.append(
            f"marker count drift in {rel_path}: {anchor_line} (expected 1, found {anchor_count})"
        )
        return
    anchor_index = lines.index(anchor_line)
    actual_lines = lines[anchor_index + 1 : anchor_index + 1 + len(expected_lines)]
    if actual_lines != expected_lines:
        errors.append(f"marker order drift in {rel_path} after anchor: {label}")


def require_no_extra_phase14_lines_after_anchor(
    errors: list[str],
    rel_path: str,
    text: str,
    anchor_line: str,
    expected_lines: list[str],
    label: str,
) -> None:
    lines = text.splitlines()
    anchor_count = sum(1 for line in lines if line == anchor_line)
    if anchor_count != 1:
        return
    anchor_index = lines.index(anchor_line)
    next_index = anchor_index + 1 + len(expected_lines)
    if next_index >= len(lines):
        return
    next_line = lines[next_index]
    if next_line.startswith(TESTS_README_PHASE14_PREFIX):
        errors.append(
            f"packet boundary drift in {rel_path} after {label}: {next_line}"
        )


def load_manifest(errors: list[str], root: Path) -> dict[str, object] | None:
    path = root / SMOKE_MANIFEST_PATH
    if not path.exists():
        errors.append(f"missing file: {SMOKE_MANIFEST_PATH.as_posix()}")
        return None
    try:
        loaded = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(
            f"json decode drift in {SMOKE_MANIFEST_PATH.as_posix()}: {exc.msg} at {exc.lineno}:{exc.colno}"
        )
        return None
    if not isinstance(loaded, dict):
        errors.append(
            f"manifest type drift in {SMOKE_MANIFEST_PATH.as_posix()}: expected object, found {type(loaded).__name__}"
        )
        return None
    return loaded


def require_manifest_alignment(errors: list[str], manifest: dict[str, object]) -> None:
    shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
    if not isinstance(shared_smoke_surfaces, list):
        errors.append(
            f"manifest shape drift in {SMOKE_MANIFEST_PATH.as_posix()}: shared_smoke_surfaces"
        )
    else:
        for surface in REQUIRED_SHARED_SMOKE_SURFACES:
            if surface not in shared_smoke_surfaces:
                errors.append(
                    f"manifest drift in {SMOKE_MANIFEST_PATH.as_posix()}: missing shared smoke surface {surface}"
                )

    anchor_packets = manifest.get("anchor_packets")
    if not isinstance(anchor_packets, list):
        errors.append(
            f"manifest shape drift in {SMOKE_MANIFEST_PATH.as_posix()}: anchor_packets"
        )
        return
    if len(anchor_packets) != EXPECTED_ANCHOR_PACKET_COUNT:
        errors.append(
            f"manifest packet count drift in {SMOKE_MANIFEST_PATH.as_posix()}: expected {EXPECTED_ANCHOR_PACKET_COUNT}, found {len(anchor_packets)}"
        )
        return

    anchor_manifest_paths = []
    for packet in anchor_packets:
        if not isinstance(packet, dict):
            errors.append(
                f"manifest shape drift in {SMOKE_MANIFEST_PATH.as_posix()}: anchor_packet"
            )
            continue
        manifest_path = packet.get("manifest_path")
        if isinstance(manifest_path, str):
            anchor_manifest_paths.append(manifest_path)
        else:
            errors.append(
                f"manifest shape drift in {SMOKE_MANIFEST_PATH.as_posix()}: anchor_packet.manifest_path"
            )
    for manifest_path in REQUIRED_ANCHOR_MANIFESTS:
        if manifest_path not in anchor_manifest_paths:
            errors.append(
                f"manifest drift in {SMOKE_MANIFEST_PATH.as_posix()}: missing anchor manifest {manifest_path}"
            )

    compile_shards = manifest.get("compile_shards")
    if compile_shards != EXPECTED_COMPILE_SHARDS:
        errors.append(
            f"manifest compile_shard drift in {SMOKE_MANIFEST_PATH.as_posix()}: expected current six-row matrix"
        )


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []

    manifest = load_manifest(errors, root)
    if manifest is not None:
        require_manifest_alignment(errors, manifest)

    scripts_readme_path = root / SCRIPTS_README_PATH
    if not scripts_readme_path.exists():
        errors.append(f"missing file: {SCRIPTS_README_PATH.as_posix()}")
    else:
        require_exact_count(
            errors,
            SCRIPTS_README_PATH.as_posix(),
            read_text(scripts_readme_path),
            SCRIPTS_README_MARKERS,
        )

    path = root / TESTS_README_PATH
    if not path.exists():
        errors.append(f"missing file: {TESTS_README_PATH.as_posix()}")
    else:
        text = read_text(path)
        require_exact_line_count(
            errors,
            TESTS_README_PATH.as_posix(),
            text,
            TESTS_README_AFTER_ANCHOR_LINES,
        )
        require_exact_count(
            errors,
            TESTS_README_PATH.as_posix(),
            text,
            TESTS_README_ROUTE_MARKERS,
        )
        require_lines_after_anchor(
            errors,
            TESTS_README_PATH.as_posix(),
            text,
            TESTS_README_PACKET_ANCHOR,
            TESTS_README_AFTER_ANCHOR_LINES,
            "phase14_smoke_packet_after_anchor",
        )
        require_no_extra_phase14_lines_after_anchor(
            errors,
            TESTS_README_PATH.as_posix(),
            text,
            TESTS_README_PACKET_ANCHOR,
            TESTS_README_AFTER_ANCHOR_LINES,
            "phase14_smoke_packet_after_anchor",
        )
    if MARKER not in (source_text if source_text is not None else read_text(Path(__file__))):
        errors.append("checker marker missing from checker source")
    return errors


def good_tests_readme_text() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            "",
            "Key entrypoints",
            TESTS_README_PACKET_ANCHOR,
            *TESTS_README_AFTER_ANCHOR_LINES,
            "  * `make -C zigux phase14-smoke`",
            "  * `zigux/tests/phase15_build.zig`",
        ]
    ) + "\n"


def good_scripts_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "Phase 14 notes",
            "- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
        ]
    ) + "\n"


def good_smoke_manifest_text() -> str:
    manifest = {
        "shared_smoke_surfaces": REQUIRED_SHARED_SMOKE_SURFACES,
        "anchor_packets": [
            {"manifest_path": path} for path in REQUIRED_ANCHOR_MANIFESTS
        ],
        "compile_shards": EXPECTED_COMPILE_SHARDS,
    }
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        print(label, file=sys.stderr)
        if errors:
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(root / TESTS_README_PATH, good_tests_readme_text())
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        if errors := check(root, source_text=MARKER):
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
                "scripts/zigux/check-phase14-tests-readme-smoke-summary-drift.py",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
            "self-test expected missing scripts-readme checker marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
                "scripts/zigux/check-phase14-tests-readme-smoke-summary.py\n"
                "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
            "self-test expected duplicate scripts-readme checker marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_workqueue_reviewability.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_workqueue_reviewability.zig",
            "self-test expected missing tests-readme packet line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_workqueue_bridge_manifest.json`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_workqueue_bridge_manifest.json",
            "self-test expected missing workqueue-bridge manifest tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_skbuff_bridge_manifest.json`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_skbuff_bridge_manifest.json",
            "self-test expected missing skbuff-bridge manifest tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_ring_buffer_survey.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_ring_buffer_survey.zig",
            "self-test expected missing ring-buffer survey tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_rcu_tree_survey.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_rcu_tree_survey.zig",
            "self-test expected missing rcu-tree survey tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_workqueue_bridge.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_workqueue_bridge.zig",
            "self-test expected missing workqueue-bridge compile-shard tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_ring_buffer_manifest.json`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_ring_buffer_manifest.json",
            "self-test expected missing ring-buffer manifest tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_rcu_tree_manifest.json`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_rcu_tree_manifest.json",
            "self-test expected missing rcu-tree manifest tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_end_to_end_smoke_manifest.json`\n",
                "  * `zigux/tests/phase14_end_to_end_smoke_manifest.json`\n"
                "  * `zigux/tests/phase14_end_to_end_smoke_manifest.json`\n",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_end_to_end_smoke_manifest.json",
            "self-test expected duplicate tests-readme packet line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_workqueue_bridge.zig`\n",
                "  * `zigux/tests/phase14_workqueue_bridge.zig`\n"
                "  * `zigux/tests/phase14_workqueue_bridge.zig`\n",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_workqueue_bridge.zig",
            "self-test expected duplicate compile-shard tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_skbuff_bridge.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_skbuff_bridge.zig",
            "self-test expected missing compile-shard tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `zigux/tests/phase14_end_to_end_smoke_survey.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "zigux/tests/phase14_end_to_end_smoke_survey.zig",
            "self-test expected missing end-to-end smoke survey tests-readme line failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `make -C zigux phase14-smoke`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "make -C zigux phase14-smoke",
            "self-test expected missing smoke-route marker failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `make -C zigux phase14-smoke`\n",
                "  * `make -C zigux phase14-smoke`\n"
                "  * `make -C zigux phase14-smoke`\n",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "make -C zigux phase14-smoke",
            "self-test expected duplicate smoke-route marker failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "\n".join(
                    [
                        TESTS_README_PACKET_ANCHOR,
                        TESTS_README_AFTER_ANCHOR_LINES[0],
                        TESTS_README_AFTER_ANCHOR_LINES[1],
                    ]
                ),
                "\n".join(
                    [
                        TESTS_README_PACKET_ANCHOR,
                        TESTS_README_AFTER_ANCHOR_LINES[1],
                        TESTS_README_AFTER_ANCHOR_LINES[0],
                    ]
                ),
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "phase14_smoke_packet_after_anchor",
            "self-test expected tests-readme packet-order failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "\n".join(
                    [
                        TESTS_README_COMPILE_SHARD_LINES[2],
                        TESTS_README_COMPILE_SHARD_LINES[3],
                    ]
                ),
                "\n".join(
                    [
                        TESTS_README_COMPILE_SHARD_LINES[3],
                        TESTS_README_COMPILE_SHARD_LINES[2],
                    ]
                ),
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "phase14_smoke_packet_after_anchor",
            "self-test expected compile-shard order failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                "  * `make -C zigux phase14-smoke`\n",
                "  * `zigux/tests/phase14_boundary_drift.zig`\n"
                "  * `make -C zigux phase14-smoke`\n",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "phase14_boundary_drift.zig",
            "self-test expected packet-boundary drift failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                f"{TESTS_README_PACKET_ANCHOR}\n",
                f"{TESTS_README_PACKET_ANCHOR}\n{TESTS_README_PACKET_ANCHOR}\n",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            TESTS_README_PACKET_ANCHOR,
            "self-test expected duplicate tests-readme anchor failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / TESTS_README_PATH,
            good_tests_readme_text().replace(
                f"{TESTS_README_PACKET_ANCHOR}\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            TESTS_README_PACKET_ANCHOR,
            "self-test expected missing tests-readme anchor failure",
        )
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        write_text(
            root / SMOKE_MANIFEST_PATH,
            good_smoke_manifest_text().replace(
                '"zigux/tests/README.md"',
                '"zigux/tests/README_drift.md"',
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "missing shared smoke surface zigux/tests/README.md",
            "self-test expected missing manifest tests-readme shared surface failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        write_text(
            root / SMOKE_MANIFEST_PATH,
            good_smoke_manifest_text().replace(
                '"zigux/tests/phase14_build.zig"',
                '"zigux/tests/phase14_build_drift.zig"',
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "missing shared smoke surface zigux/tests/phase14_build.zig",
            "self-test expected missing manifest build shared surface failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        write_text(
            root / SMOKE_MANIFEST_PATH,
            good_smoke_manifest_text().replace(
                '"zigux/tests/phase14_end_to_end_smoke_survey.zig"',
                '"zigux/tests/phase14_end_to_end_smoke_survey_drift.zig"',
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "missing shared smoke surface zigux/tests/phase14_end_to_end_smoke_survey.zig",
            "self-test expected missing manifest smoke-survey shared surface failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        write_text(
            root / SMOKE_MANIFEST_PATH,
            good_smoke_manifest_text().replace(
                '"zigux/tests/phase14_workqueue_reviewability.zig"',
                '"zigux/tests/phase14_workqueue_reviewability_drift.zig"',
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "missing shared smoke surface zigux/tests/phase14_workqueue_reviewability.zig",
            "self-test expected missing manifest shared smoke surface failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        write_text(
            root / SMOKE_MANIFEST_PATH,
            good_smoke_manifest_text().replace(
                '"zigux/tests/phase14_ring_buffer_manifest.json"',
                '"zigux/tests/phase14_ring_buffer_manifest_drift.json"',
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "missing anchor manifest zigux/tests/phase14_ring_buffer_manifest.json",
            "self-test expected missing anchor manifest failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        manifest = json.loads(good_smoke_manifest_text())
        manifest["anchor_packets"].append(
            {"manifest_path": "zigux/tests/phase14_extra_anchor_manifest.json"}
        )
        write_text(
            root / SMOKE_MANIFEST_PATH,
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )
        expect_contains(
            check(root, source_text=MARKER),
            "manifest packet count drift",
            "self-test expected anchor-packet count drift failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        manifest = json.loads(good_smoke_manifest_text())
        manifest["compile_shards"] = manifest["compile_shards"][1:]
        write_text(
            root / SMOKE_MANIFEST_PATH,
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )
        expect_contains(
            check(root, source_text=MARKER),
            "manifest compile_shard drift",
            "self-test expected missing compile-shard matrix row failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        manifest = json.loads(good_smoke_manifest_text())
        manifest["compile_shards"][-1]["coverage"] = "full_bundle_only"
        write_text(
            root / SMOKE_MANIFEST_PATH,
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )
        expect_contains(
            check(root, source_text=MARKER),
            "manifest compile_shard drift",
            "self-test expected compile-shard coverage drift failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        write_text(root / SMOKE_MANIFEST_PATH, "{\n")
        expect_contains(
            check(root, source_text=MARKER),
            "json decode drift",
            "self-test expected manifest json decode failure",
        )
        write_text(root / SMOKE_MANIFEST_PATH, good_smoke_manifest_text())

        expect_contains(
            check(root, source_text="PHASE14_CHECK_PACKET=broken_marker"),
            "checker marker missing from checker source",
            "self-test expected checker-source marker failure",
        )

    print("PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass")
    print("PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT=31")
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_PACKET_LINE_COUNT="
        f"{len(TESTS_README_AFTER_ANCHOR_LINES)}"
    )
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_MANIFEST_SHARED_SURFACE_COUNT="
        f"{len(REQUIRED_SHARED_SMOKE_SURFACES)}"
    )
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_ANCHOR_MANIFEST_COUNT="
        f"{len(REQUIRED_ANCHOR_MANIFESTS)}"
    )
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_EXPECTED_ANCHOR_PACKET_COUNT="
        f"{EXPECTED_ANCHOR_PACKET_COUNT}"
    )
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_COMPILE_SHARD_COUNT="
        f"{len(EXPECTED_COMPILE_SHARDS)}"
    )
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_ROUTE_MARKER_COUNT="
        f"{len(TESTS_README_ROUTE_MARKERS)}"
    )
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_SCRIPTS_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS)}"
    )
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

    print("phase14 tests-readme smoke summary validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
