#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=docs_root_smoke_summary

Fail-closed checker for the current docs-root summary of the shared Phase 14
smoke packet.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=docs_root_smoke_summary"
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
CORE_TRACEABILITY_PATH = Path("Documentation/zigux/phase14-core-boundary-traceability.md")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
CHECKER_PATH = "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
ROLLBACK_CHECKER_PATH = "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
RELEASE_BOUNDARY_CHECKER_PATH = "scripts/zigux/check-phase14-release-boundary-exact-counts.py"

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_skbuff_bridge.zig",
    "zigux/tests/phase14_ring_buffer_survey.zig",
    "zigux/tests/phase14_rcu_tree_survey.zig",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]

DOCS_ROOT_EXACT_COUNT_MARKERS = [
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-test",
]

SMOKE_SURVEY_MARKERS = [
    CHECKER_PATH,
    ROLLBACK_CHECKER_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
    "scripts/zigux/validate-phase14.py",
    "PHASE14_ANCHOR_PACKET_COUNT=4",
    "phase14-workqueue-reviewability-tests",
    "phase14-end-to-end-smoke-tests",
    "phase14_workqueue_reviewability.zig",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-test",
    "make -C zigux phase14",
]

SMOKE_SURVEY_EXACT_COUNT_MARKERS = [
    CHECKER_PATH,
    ROLLBACK_CHECKER_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
    "PHASE14_ANCHOR_PACKET_COUNT=4",
]

CORE_TRACEABILITY_MARKERS = [
    "manifest: `zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "survey note: `Documentation/zigux/phase14-workqueue-bridge-survey.md`",
    "lane key: `P14-L01`",
    "surveyed commit: `007f00d0c6b6b430bfbb2110555544cc5faefe8b`",
    "ready-next gap: `phase14-workqueue-pending-bit-audit`",
    "blocked gap: `phase14-workqueue-live-execution-blocker`",
    "full-bundle reviewability replay: `zigux/tests/phase14_workqueue_reviewability.zig`",
    "focused smoke shard: `make -C zigux phase14-smoke`",
    "shared full replay: `make -C zigux phase14-test`",
]

CORE_TRACEABILITY_EXACT_LINE_MARKERS = [
    "  * lane key: `P14-L01`",
    "  * surveyed commit: `007f00d0c6b6b430bfbb2110555544cc5faefe8b`",
    "  * ready-next gap: `phase14-workqueue-pending-bit-audit`",
    "  * blocked gap: `phase14-workqueue-live-execution-blocker`",
]

MAKEFILE_MARKERS = [
    "scripts/zigux/validate-phase14.py",
    CHECKER_PATH,
    ROLLBACK_CHECKER_PATH,
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    RELEASE_BOUNDARY_CHECKER_PATH,
]

MAKEFILE_EXACT_COUNT_MARKERS = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {CHECKER_PATH} --self-test",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {CHECKER_PATH}",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {ROLLBACK_CHECKER_PATH} --self-test",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {ROLLBACK_CHECKER_PATH}",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {RELEASE_BOUNDARY_CHECKER_PATH} --self-test",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {RELEASE_BOUNDARY_CHECKER_PATH}",
]

MANIFEST_REQUIRED_SURFACES = [
    CHECKER_PATH,
    ROLLBACK_CHECKER_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
    "scripts/zigux/validate-phase14.py",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_present(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing marker in {rel_path}: {marker}")


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def require_exact_line_count(
    errors: list[str], rel_path: str, text: str, markers: list[str]
) -> None:
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def check_manifest(errors: list[str], root: Path) -> None:
    path = root / MANIFEST_PATH
    if not path.exists():
        errors.append(f"missing file: {MANIFEST_PATH.as_posix()}")
        return
    try:
        manifest = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {MANIFEST_PATH.as_posix()}: {exc}")
        return
    surfaces = manifest.get("shared_smoke_surfaces")
    if not isinstance(surfaces, list):
        errors.append("phase14 shared_smoke_surfaces payload is not a list")
        return
    for surface in MANIFEST_REQUIRED_SURFACES:
        count = surfaces.count(surface)
        if count != 1:
            errors.append(
                "phase14 shared_smoke_surfaces drift for "
                f"{surface} (expected 1, found {count})"
            )


def check_text_file(
    errors: list[str],
    root: Path,
    rel_path: Path,
    markers: list[str],
    exact_count_markers: list[str],
    *,
    exact_line_match: bool = False,
) -> None:
    path = root / rel_path
    if not path.exists():
        errors.append(f"missing file: {rel_path.as_posix()}")
        return
    text = read_text(path)
    require_present(errors, rel_path.as_posix(), text, markers)
    if exact_line_match:
        require_exact_line_count(errors, rel_path.as_posix(), text, exact_count_markers)
    else:
        require_exact_count(errors, rel_path.as_posix(), text, exact_count_markers)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")
    check_text_file(
        errors,
        root,
        DOCS_ROOT_PATH,
        DOCS_ROOT_MARKERS,
        DOCS_ROOT_EXACT_COUNT_MARKERS,
    )
    check_text_file(
        errors,
        root,
        SMOKE_SURVEY_PATH,
        SMOKE_SURVEY_MARKERS,
        SMOKE_SURVEY_EXACT_COUNT_MARKERS,
    )
    check_text_file(
        errors,
        root,
        CORE_TRACEABILITY_PATH,
        CORE_TRACEABILITY_MARKERS,
        CORE_TRACEABILITY_EXACT_LINE_MARKERS,
        exact_line_match=True,
    )
    check_text_file(
        errors,
        root,
        MAKEFILE_PATH,
        MAKEFILE_MARKERS,
        MAKEFILE_EXACT_COUNT_MARKERS,
        exact_line_match=True,
    )
    check_manifest(errors, root)
    return errors


def good_docs_root_text() -> str:
    return "\n".join(f"- `{marker}`" for marker in DOCS_ROOT_MARKERS) + "\n"


def good_smoke_survey_text() -> str:
    return "\n".join(
        [
            f"- `{CHECKER_PATH}`",
            f"- `{ROLLBACK_CHECKER_PATH}`",
            f"- `{RELEASE_BOUNDARY_CHECKER_PATH}`",
            "- `scripts/zigux/validate-phase14.py`",
            "- `PHASE14_ANCHOR_PACKET_COUNT=4`",
            "- `phase14-workqueue-reviewability-tests`",
            "- `phase14-end-to-end-smoke-tests`",
            "- `phase14_workqueue_reviewability.zig`",
            "- `make -C zigux phase14-validate`",
            "- `make -C zigux phase14-smoke`",
            "- `make -C zigux phase14-test`",
            "- `make -C zigux phase14`",
        ]
    ) + "\n"


def good_core_traceability_text() -> str:
    return "\n".join(
        [
            "# Phase 14 Core Boundary Traceability",
            "## Current repo evidence",
            "### Workqueue",
            "  * manifest: `zigux/tests/phase14_workqueue_bridge_manifest.json`",
            "  * survey note: `Documentation/zigux/phase14-workqueue-bridge-survey.md`",
            "  * lane key: `P14-L01`",
            "  * surveyed commit: `007f00d0c6b6b430bfbb2110555544cc5faefe8b`",
            "  * ready-next gap: `phase14-workqueue-pending-bit-audit`",
            "  * blocked gap: `phase14-workqueue-live-execution-blocker`",
            "## Shared replay contract",
            "  * full-bundle reviewability replay: `zigux/tests/phase14_workqueue_reviewability.zig`",
            "  * focused smoke shard: `make -C zigux phase14-smoke`",
            "  * shared full replay: `make -C zigux phase14-test`",
        ]
    ) + "\n"


def good_makefile_text() -> str:
    return "\n".join(
        [
            "phase14-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {CHECKER_PATH} --self-test",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {CHECKER_PATH}",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {ROLLBACK_CHECKER_PATH} --self-test",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {ROLLBACK_CHECKER_PATH}",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {RELEASE_BOUNDARY_CHECKER_PATH} --self-test",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {RELEASE_BOUNDARY_CHECKER_PATH}",
        ]
    ) + "\n"


def good_manifest_text() -> str:
    return (
        json.dumps(
            {
                "shared_smoke_surfaces": MANIFEST_REQUIRED_SURFACES,
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

        write_text(root / DOCS_ROOT_PATH, good_docs_root_text())
        write_text(root / SMOKE_SURVEY_PATH, good_smoke_survey_text())
        write_text(root / CORE_TRACEABILITY_PATH, good_core_traceability_text())
        write_text(root / MAKEFILE_PATH, good_makefile_text())
        write_text(root / MANIFEST_PATH, good_manifest_text())

        if errors := check(root):
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        write_text(
            root / DOCS_ROOT_PATH,
            good_docs_root_text().replace(
                "- `Documentation/zigux/phase14-core-boundary-traceability.md`\n",
                "",
                1,
            ),
        )
        if not any(
            "missing marker in Documentation/zigux/README.md: Documentation/zigux/phase14-core-boundary-traceability.md"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected missing docs-root traceability marker failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / DOCS_ROOT_PATH, good_docs_root_text())

        write_text(
            root / DOCS_ROOT_PATH,
            good_docs_root_text().replace(
                "- `zigux/tests/phase14_end_to_end_smoke_manifest.json`\n",
                "",
                1,
            ),
        )
        if not any(
            "missing marker in Documentation/zigux/README.md: zigux/tests/phase14_end_to_end_smoke_manifest.json"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected missing docs-root smoke-manifest marker failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / DOCS_ROOT_PATH, good_docs_root_text())

        write_text(
            root / DOCS_ROOT_PATH,
            good_docs_root_text().replace("- `make -C zigux phase14-test`\n", "", 1),
        )
        if not any(
            "missing marker in Documentation/zigux/README.md: make -C zigux phase14-test"
            in error
            for error in check(root)
        ):
            print("self-test expected missing docs-root test-route failure", file=sys.stderr)
            return 1
        write_text(root / DOCS_ROOT_PATH, good_docs_root_text())

        write_text(
            root / DOCS_ROOT_PATH,
            good_docs_root_text().replace(
                "- `make -C zigux phase14-smoke`\n",
                "- `make -C zigux phase14-smoke`\n- `make -C zigux phase14-smoke`\n",
                1,
            ),
        )
        if not any(
            "marker count drift in Documentation/zigux/README.md: make -C zigux phase14-smoke (expected 1, found 2)"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected duplicate docs-root smoke-route failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / DOCS_ROOT_PATH, good_docs_root_text())

        write_text(
            root / DOCS_ROOT_PATH,
            good_docs_root_text().replace(
                "- `make -C zigux phase14-test`\n",
                "- `make -C zigux phase14-test`\n- `make -C zigux phase14-test`\n",
                1,
            ),
        )
        if not any(
            "marker count drift in Documentation/zigux/README.md: make -C zigux phase14-test (expected 1, found 2)"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected duplicate docs-root test-route failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / DOCS_ROOT_PATH, good_docs_root_text())

        write_text(
            root / SMOKE_SURVEY_PATH,
            good_smoke_survey_text().replace(
                f"- `{CHECKER_PATH}`\n",
                f"- `{CHECKER_PATH}`\n- `{CHECKER_PATH}`\n",
                1,
            ),
        )
        if not any(
            f"marker count drift in {SMOKE_SURVEY_PATH.as_posix()}: {CHECKER_PATH} (expected 1, found 2)"
            in error
            for error in check(root)
        ):
            print("self-test expected duplicate smoke-survey checker marker failure", file=sys.stderr)
            return 1
        write_text(root / SMOKE_SURVEY_PATH, good_smoke_survey_text())

        write_text(
            root / SMOKE_SURVEY_PATH,
            good_smoke_survey_text().replace("- `make -C zigux phase14-test`\n", "", 1),
        )
        if not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: make -C zigux phase14-test"
            in error
            for error in check(root)
        ):
            print("self-test expected missing smoke-survey test-route failure", file=sys.stderr)
            return 1
        write_text(root / SMOKE_SURVEY_PATH, good_smoke_survey_text())

        write_text(
            root / CORE_TRACEABILITY_PATH,
            good_core_traceability_text().replace(
                "  * ready-next gap: `phase14-workqueue-pending-bit-audit`\n",
                "",
                1,
            ),
        )
        if not any(
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: ready-next gap: `phase14-workqueue-pending-bit-audit`"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected missing traceability ready-next marker failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / CORE_TRACEABILITY_PATH, good_core_traceability_text())

        write_text(
            root / CORE_TRACEABILITY_PATH,
            good_core_traceability_text().replace(
                "  * ready-next gap: `phase14-workqueue-pending-bit-audit`\n",
                "  * ready-next gap: `phase14-workqueue-pending-bit-audit`\n  * ready-next gap: `phase14-workqueue-pending-bit-audit`\n",
                1,
            ),
        )
        if not any(
            "marker count drift in Documentation/zigux/phase14-core-boundary-traceability.md:   * ready-next gap: `phase14-workqueue-pending-bit-audit` (expected 1, found 2)"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected duplicate traceability ready-next line failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / CORE_TRACEABILITY_PATH, good_core_traceability_text())

        write_text(
            root / MAKEFILE_PATH,
            good_makefile_text().replace(
                f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {CHECKER_PATH} --self-test\n",
                "",
                1,
            ),
        )
        if not any(
            f"marker count drift in {MAKEFILE_PATH.as_posix()}: \tcd $(ZIGUX_ROOT) && $(PYTHON) {CHECKER_PATH} --self-test"
            in error
            for error in check(root)
        ):
            print("self-test expected missing makefile self-test route failure", file=sys.stderr)
            return 1
        write_text(root / MAKEFILE_PATH, good_makefile_text())

        write_text(
            root / MAKEFILE_PATH,
            good_makefile_text().replace(
                f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {ROLLBACK_CHECKER_PATH} --self-test\n",
                "",
                1,
            ),
        )
        if not any(
            f"marker count drift in {MAKEFILE_PATH.as_posix()}: \tcd $(ZIGUX_ROOT) && $(PYTHON) {ROLLBACK_CHECKER_PATH} --self-test"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected missing rollback makefile self-test route failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / MAKEFILE_PATH, good_makefile_text())

        write_text(
            root / MAKEFILE_PATH,
            good_makefile_text().replace(
                f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {RELEASE_BOUNDARY_CHECKER_PATH} --self-test\n",
                "",
                1,
            ),
        )
        if not any(
            f"marker count drift in {MAKEFILE_PATH.as_posix()}: \tcd $(ZIGUX_ROOT) && $(PYTHON) {RELEASE_BOUNDARY_CHECKER_PATH} --self-test"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected missing sibling makefile self-test route failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / MAKEFILE_PATH, good_makefile_text())

        write_text(root / MANIFEST_PATH, "{\n")
        if not any(
            error.startswith(f"invalid json in {MANIFEST_PATH.as_posix()}:")
            for error in check(root)
        ):
            print("self-test expected invalid manifest json failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps({"shared_smoke_surfaces": []}, indent=2) + "\n",
        )
        if not any(
            f"phase14 shared_smoke_surfaces drift for {CHECKER_PATH} (expected 1, found 0)"
            in error
            for error in check(root)
        ):
            print("self-test expected missing manifest checker surface failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "shared_smoke_surfaces": [
                        CHECKER_PATH,
                        ROLLBACK_CHECKER_PATH,
                        "scripts/zigux/validate-phase14.py",
                    ]
                },
                indent=2,
            )
            + "\n",
        )
        if not any(
            f"phase14 shared_smoke_surfaces drift for {RELEASE_BOUNDARY_CHECKER_PATH} (expected 1, found 0)"
            in error
            for error in check(root)
        ):
            print(
                "self-test expected missing release-boundary checker surface failure",
                file=sys.stderr,
            )
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            current_checker_path,
            original_source.replace(MARKER, "PHASE14_CHECK_PACKET=broken_marker"),
        )
        if "checker marker missing from checker source" not in check(root):
            print("self-test expected checker-source marker failure", file=sys.stderr)
            write_text(current_checker_path, original_source)
            return 1
        write_text(current_checker_path, original_source)

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST=pass")
    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT=16")
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
