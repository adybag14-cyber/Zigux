#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=tests_readme_smoke_summary

Fail-closed checker for the current tests-root summary of the shared Phase 14
smoke packet.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=tests_readme_smoke_summary"
TESTS_README_PATH = Path("zigux/tests/README.md")
TESTS_README_PACKET_ANCHOR = "  * `zigux/tests/phase14_build.zig`"
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
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
        require_lines_after_anchor(
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
        ]
    ) + "\n"


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
        write_text(root / TESTS_README_PATH, good_tests_readme_text())

        if errors := check(root, source_text=MARKER):
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

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

        expect_contains(
            check(root, source_text="PHASE14_CHECK_PACKET=broken_marker"),
            "checker marker missing from checker source",
            "self-test expected checker-source marker failure",
        )

    print("PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass")
    print("PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT=14")
    print(
        "PHASE14_TESTS_README_SMOKE_SUMMARY_PACKET_LINE_COUNT="
        f"{len(TESTS_README_AFTER_ANCHOR_LINES)}"
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
