#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SELF_TEST_CASE_COUNT = 17

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

REQUIRED_FILES = [
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    DOCS_ROOT_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
]

REQUIRED_WORKFLOW_COUNTS = {
    "- name: Validate Phase 4 diff gates": 1,
    "run: make -C zigux phase4-validate": 1,
    "- name: Run Phase 4 diff tests": 1,
    "run: make -C zigux phase4-test": 1,
}

REQUIRED_MAKEFILE_MARKERS = [
    "phase4-validate:",
    "phase4-test:",
    "phase4-runtime-atomic64-diff:",
    "phase4-test-fsmount-survey:",
    "phase4-kprobe-example-survey:",
    "phase4-perf-baseline-survey:",
    "phase4-bitmap-diff:",
    "phase4: phase4-validate phase4-test",
]

REQUIRED_MAKEFILE_COUNTS = {
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test": 1,
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py": 1,
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig": 1,
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig": 1,
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig": 1,
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig": 1,
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig": 1,
}

REQUIRED_DOC_MARKERS = {
    DOCS_ROOT_PATH: [
        "`make -C zigux phase4-validate`",
        "`make -C zigux phase4-test`",
        "direct `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`",
        "`make -C zigux phase4-test-fsmount-survey`",
        "`make -C zigux phase4-perf-baseline-survey`",
    ],
    SCRIPTS_README_PATH: [
        "`make -C zigux phase4-validate`",
        "`make -C zigux phase4-test`",
        "`make -C zigux phase4-kprobe-example-survey`",
        "`make -C zigux phase4-test-fsmount-survey`",
        "`make -C zigux phase4-perf-baseline-survey`",
    ],
    TESTS_README_PATH: [
        "`make -C zigux phase4-validate`",
        "`make -C zigux phase4-test`",
        "`make -C zigux phase4-kprobe-example-survey`",
        "`make -C zigux phase4-test-fsmount-survey`",
        "`make -C zigux phase4-perf-baseline-survey`",
    ],
}


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_occurrences(text: str, needle: str) -> int:
    return text.count(needle)


def count_exact_line(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line == needle)


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            missing.append(f"missing_file:{relative_path.as_posix()}")

    if missing:
        return missing

    workflow_text = read_text(root, WORKFLOW_PATH)
    for needle, expected_count in REQUIRED_WORKFLOW_COUNTS.items():
        actual_count = count_occurrences(workflow_text, needle)
        if actual_count != expected_count:
            missing.append(
                f"workflow_count:{needle}:expected={expected_count}:actual={actual_count}"
            )

    makefile_text = read_text(root, MAKEFILE_PATH)
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            missing.append(f"makefile_marker:{marker}")
    for needle, expected_count in REQUIRED_MAKEFILE_COUNTS.items():
        actual_count = count_exact_line(makefile_text, needle)
        if actual_count != expected_count:
            missing.append(
                f"makefile_count:{needle}:expected={expected_count}:actual={actual_count}"
            )

    for relative_path, markers in REQUIRED_DOC_MARKERS.items():
        file_text = read_text(root, relative_path)
        for marker in markers:
            if marker not in file_text:
                missing.append(f"doc_marker:{relative_path.as_posix()}:{marker}")

    return missing


def write(root: Path, relative_path: Path, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_fixture_tree(root: Path) -> None:
    write(
        root,
        WORKFLOW_PATH,
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate Phase 4 diff gates",
                "        run: make -C zigux phase4-validate",
                "      - name: Run Phase 4 diff tests",
                "        run: make -C zigux phase4-test",
            ]
        )
        + "\n",
    )
    write(
        root,
        MAKEFILE_PATH,
        "\n".join(
            [
                "phase4-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py",
                "\tpython3 scripts/zigux/validate-phase4.py",
                "phase4-test:",
                "\tzig build test --build-file zigux/tests/phase4_build.zig --summary all",
                "phase4-runtime-atomic64-diff:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
                "phase4-test-fsmount-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "phase4-kprobe-example-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
                "phase4-perf-baseline-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
                "phase4-bitmap-diff:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
                "phase4: phase4-validate phase4-test",
            ]
        )
        + "\n",
    )
    write(
        root,
        DOCS_ROOT_PATH,
        "\n".join(
            [
                "Phase 4 notes",
                "`make -C zigux phase4-validate`",
                "`make -C zigux phase4-test`",
                "direct `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`",
                "`make -C zigux phase4-test-fsmount-survey`",
                "`make -C zigux phase4-perf-baseline-survey`",
            ]
        )
        + "\n",
    )
    shared_readme_stub = "\n".join(
        [
            "Phase 4 notes",
            "`make -C zigux phase4-validate`",
            "`make -C zigux phase4-test`",
            "`make -C zigux phase4-kprobe-example-survey`",
            "`make -C zigux phase4-test-fsmount-survey`",
            "`make -C zigux phase4-perf-baseline-survey`",
        ]
    ) + "\n"
    write(root, SCRIPTS_README_PATH, shared_readme_stub)
    write(root, TESTS_README_PATH, shared_readme_stub)


def expect_contains(items: list[str], needle: str) -> None:
    if needle not in items:
        raise AssertionError(f"missing expectation {needle}")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="phase4_workflow_counts_") as temp_dir:
            root = Path(temp_dir)
            count = 0

            build_fixture_tree(root)
            if validate(root):
                raise AssertionError(validate(root))
            count += 1

            build_fixture_tree(root)
            workflow = root / WORKFLOW_PATH
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "run: make -C zigux phase4-validate\n", "", 1
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "workflow_count:run: make -C zigux phase4-validate:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            workflow = root / WORKFLOW_PATH
            workflow.write_text(
                workflow.read_text(encoding="utf-8")
                + "      - name: Validate Phase 4 diff gates\n"
                + "        run: make -C zigux phase4-validate\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "workflow_count:- name: Validate Phase 4 diff gates:expected=1:actual=2",
            )
            count += 1

            build_fixture_tree(root)
            workflow = root / WORKFLOW_PATH
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "- name: Run Phase 4 diff tests\n", "", 1
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "workflow_count:- name: Run Phase 4 diff tests:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            workflow = root / WORKFLOW_PATH
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "run: make -C zigux phase4-test\n", "", 1
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "workflow_count:run: make -C zigux phase4-test:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            makefile.write_text(
                makefile.read_text(encoding="utf-8").replace(
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "makefile_count:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            makefile.write_text(
                makefile.read_text(encoding="utf-8")
                + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "makefile_count:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py:expected=1:actual=2",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                docs_root.read_text(encoding="utf-8").replace(
                    "direct `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "doc_marker:Documentation/zigux/README.md:direct `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                docs_root.read_text(encoding="utf-8").replace(
                    "`make -C zigux phase4-test-fsmount-survey`\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "doc_marker:Documentation/zigux/README.md:`make -C zigux phase4-test-fsmount-survey`",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                docs_root.read_text(encoding="utf-8").replace(
                    "`make -C zigux phase4-perf-baseline-survey`\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "doc_marker:Documentation/zigux/README.md:`make -C zigux phase4-perf-baseline-survey`",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text(
                scripts_readme.read_text(encoding="utf-8").replace(
                    "`make -C zigux phase4-kprobe-example-survey`\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "doc_marker:scripts/zigux/README.md:`make -C zigux phase4-kprobe-example-survey`",
            )
            count += 1

            build_fixture_tree(root)
            tests_readme = root / TESTS_README_PATH
            tests_readme.write_text(
                tests_readme.read_text(encoding="utf-8").replace(
                    "`make -C zigux phase4-perf-baseline-survey`\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "doc_marker:zigux/tests/README.md:`make -C zigux phase4-perf-baseline-survey`",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            makefile.write_text(
                makefile.read_text(encoding="utf-8").replace(
                    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "makefile_count:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            makefile.write_text(
                makefile.read_text(encoding="utf-8")
                + "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "makefile_count:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig:expected=1:actual=2",
            )
            count += 1

            build_fixture_tree(root)
            tests_readme = root / TESTS_README_PATH
            tests_readme.write_text(
                "Phase 4 notes\n`make -C zigux phase4-validate`\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "doc_marker:zigux/tests/README.md:`make -C zigux phase4-test`",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            makefile.write_text(
                makefile.read_text(encoding="utf-8").replace(
                    "phase4: phase4-validate phase4-test", "", 1
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "makefile_marker:phase4: phase4-validate phase4-test",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            makefile.write_text(
                makefile.read_text(encoding="utf-8").replace(
                    "phase4-runtime-atomic64-diff:\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "makefile_marker:phase4-runtime-atomic64-diff:",
            )
            count += 1

            if count != SELF_TEST_CASE_COUNT:
                raise AssertionError(
                    f"expected {SELF_TEST_CASE_COUNT} self-test cases, got {count}"
                )
    except AssertionError as exc:
        print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=fail")
        print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on exact Phase 4 workflow route counts."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate(ROOT)
    if missing:
        print("PHASE4_WORKFLOW_ROUTE_COUNTS=fail")
        print("PHASE4_WORKFLOW_ROUTE_COUNTS_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE4_WORKFLOW_ROUTE_COUNTS_MISSING_END")
        return 1

    print("PHASE4_WORKFLOW_ROUTE_COUNTS=pass")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT="
        f"{len(REQUIRED_WORKFLOW_COUNTS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_MAKEFILE_COUNTS) + sum(len(markers) for markers in REQUIRED_DOC_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
