#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / ".github/workflows/zigux-bootstrap.yml").exists() and (
            candidate / "Documentation/zigux/phase12-release-readiness-survey.md"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
DOCS_SANITY_CHECKER_PATH = "scripts/zigux/check-phase12-bootstrap-docs-sanity.py"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    SURVEY_PATH,
    DOCS_SANITY_CHECKER_PATH,
    BUILD_ONLY_CHECKER_PATH,
]

WORKFLOW_STEP_NAMES = [
    "Checkout",
    "Setup Python",
    "Setup pinned Zig toolchain",
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy packet",
    "Check current pinned Zig archive packet",
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
    "Run current Phase 2 toolchain make route",
    "Validate current Phase 2 tool packet",
    "Check current Phase 4 artifact-diff validator replay packet",
    "Validate Phase 10 checker-backed review packet",
    "Run Phase 10 helper tests",
    "Self-test current Phase 11 HVC cleanup current-head checker",
    "Check current Phase 11 HVC cleanup current-head packet",
    "Run current Phase 11 HVC cleanup packet proof",
    "Self-test current Phase 12 build-only surface checker",
    "Check current Phase 12 build-only surface",
    "Self-test current Phase 12 release-readiness packet checker",
    "Check current Phase 12 release-readiness packet",
    "Validate current Phase 12 support bundle",
    "Run current Phase 12 smoke packet",
    "Run current Phase 12 shared test packet",
    "Run current Phase 12 throughput-parity anchor",
]

WORKFLOW_COMMAND_MARKERS = [
    "# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.",
    "  push:\n    branches: [ master ]\n  pull_request:\n",
    "workflow_dispatch:",
    "group: ${{ format('{0}-{1}', github.workflow, github.ref) }}",
    "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    "if try_local_archive; then",
    'curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
    'echo "$extract_root" >> "$GITHUB_PATH"',
    '"$zig_path" version',
    'if [ "${#scripts[@]}" -eq 0 ]; then',
    'python3 -m py_compile "${scripts[@]}"',
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
    "make -C zigux phase2-toolchain",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "python3 scripts/zigux/validate-phase12.py",
    "make -C zigux phase12-smoke",
    "make -C zigux phase12-test",
    "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
]

WORKFLOW_EXACT_LINES = [
    '          echo "$extract_root" >> "$GITHUB_PATH"',
    '          "$zig_path" version',
    '          if [ "${#scripts[@]}" -eq 0 ]; then',
    '          python3 -m py_compile "${scripts[@]}"',
    "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test",
    "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test",
    "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
    "        run: make -C zigux phase2-toolchain",
    "        run: python3 scripts/zigux/validate-phase12.py",
    "        run: make -C zigux phase12-smoke",
    "        run: make -C zigux phase12-test",
]

WORKFLOW_REQUIRED_PULL_REQUEST_PATHS = [
    "      - 'Documentation/zigux/**'",
    "      - 'scripts/zigux/**'",
    "      - '.github/workflows/zigux-bootstrap.yml'",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "  push:\n    branches: [ master ]\n    paths:",
    "python3 - <<'PY2'",
    "ZIGUX_BOOTSTRAP_SANITY=pass",
]

SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "shared-summary lane owner: `pmo-release`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
]


def validate_workflow(workflow_text: str) -> list[str]:
    failures: list[str] = []
    positions: list[int] = []
    workflow_lines = workflow_text.splitlines()

    for step_name in WORKFLOW_STEP_NAMES:
        marker = f"- name: {step_name}"
        actual = workflow_text.count(marker)
        if actual == 0:
            failures.append(f"workflow_step:{step_name}")
            continue
        if actual != 1:
            failures.append(f"workflow_step_duplicate:{step_name}:actual={actual}")
        positions.append(workflow_text.find(marker))

    if positions and positions != sorted(positions):
        failures.append("workflow_order:bootstrap-step-order")

    for marker in WORKFLOW_COMMAND_MARKERS:
        if marker not in workflow_text:
            failures.append(f"workflow_marker:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden_marker:{marker}")

    for line in WORKFLOW_EXACT_LINES:
        actual = workflow_lines.count(line)
        if actual != 1:
            failures.append(
                f"workflow_exact_line:{line.strip()}:expected=1:actual={actual}"
            )

    pull_request_marker = "  pull_request:\n    paths:\n"
    pull_request_start = workflow_text.find(pull_request_marker)
    workflow_dispatch_start = workflow_text.find("\n  workflow_dispatch:\n")
    if pull_request_start == -1 or workflow_dispatch_start == -1:
        failures.append("workflow_pull_request_paths:block")
    else:
        pull_request_block = workflow_text[
            pull_request_start : workflow_dispatch_start + 1
        ]
        for marker in WORKFLOW_REQUIRED_PULL_REQUEST_PATHS:
            if marker not in pull_request_block:
                failures.append(f"workflow_pull_request_path:{marker}")

    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    workflow_path = root / WORKFLOW_PATH
    if workflow_path.exists():
        workflow_text = workflow_path.read_text(encoding="utf-8")
        failures.extend(validate_workflow(workflow_text))

    survey_path = root / SURVEY_PATH
    if survey_path.exists():
        survey_text = survey_path.read_text(encoding="utf-8")
        for marker in SURVEY_MARKERS:
            if marker not in survey_text:
                failures.append(f"survey:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_workflow() -> str:
    return """name: zigux-bootstrap
# Keep this lane tied to files that the current checkout actually contains.
# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'Documentation/zigux/**'
      - 'scripts/zigux/**'
      - '.github/workflows/zigux-bootstrap.yml'
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

concurrency:
  group: ${{ format('{0}-{1}', github.workflow, github.ref) }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
        with:
          fetch-depth: 1
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'
      - name: Setup pinned Zig toolchain
        run: |
          set -euxo pipefail
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
            echo using repo archive
          fi
          if try_local_archive; then
            echo local archive ok
          fi
          curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"
          python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org'
          echo "$extract_root" >> "$GITHUB_PATH"
          "$zig_path" version
      - name: Compile current scripts
        run: |
          set -euxo pipefail
          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
          if [ "${#scripts[@]}" -eq 0 ]; then
            echo 'no Python scripts found under scripts/zigux' >&2
            exit 1
          fi
          python3 -m py_compile "${scripts[@]}"
      - name: Self-test current Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
      - name: Check current Zig toolchain policy packet
        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
      - name: Check current pinned Zig archive packet
        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
      - name: Self-test current Phase 12 bootstrap docs sanity checker
        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test
      - name: Check current Phase 12 docs-root sanity markers
        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py
      - name: Self-test current Phase 12 bootstrap lane checker
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test
      - name: Check current Phase 12 bootstrap lane shape
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py
      - name: Run current Phase 2 toolchain make route
        run: make -C zigux phase2-toolchain
      - name: Validate current Phase 2 tool packet
        run: python3 scripts/zigux/validate-phase2.py
      - name: Check current Phase 4 artifact-diff validator replay packet
        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py
      - name: Validate Phase 10 checker-backed review packet
        run: make -C zigux phase10-validate
      - name: Run Phase 10 helper tests
        run: make -C zigux phase10-test
      - name: Self-test current Phase 11 HVC cleanup current-head checker
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test
      - name: Check current Phase 11 HVC cleanup current-head packet
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py
      - name: Run current Phase 11 HVC cleanup packet proof
        run: zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig
      - name: Self-test current Phase 12 build-only surface checker
        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
      - name: Check current Phase 12 build-only surface
        run: python3 scripts/zigux/check-build-only-phase12-surface.py
      - name: Self-test current Phase 12 release-readiness packet checker
        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
      - name: Check current Phase 12 release-readiness packet
        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py
      - name: Validate current Phase 12 support bundle
        run: python3 scripts/zigux/validate-phase12.py
      - name: Run current Phase 12 smoke packet
        run: make -C zigux phase12-smoke
      - name: Run current Phase 12 shared test packet
        run: make -C zigux phase12-test
      - name: Run current Phase 12 throughput-parity anchor
        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig
"""


def minimal_survey() -> str:
    return """# Phase 12 Release Readiness Survey

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `pmo-release`
- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / WORKFLOW_PATH, minimal_workflow())
    write_text(root / SURVEY_PATH, minimal_survey())
    write_text(root / DOCS_SANITY_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write_text(root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-lane-shape-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / DOCS_SANITY_CHECKER_PATH).unlink()
        expect_failure(base, f"missing_file:{DOCS_SANITY_CHECKER_PATH}")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            'workflow_marker:repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "if try_local_archive; then\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_marker:if try_local_archive; then")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            'workflow_marker:python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                '          echo "$extract_root" >> "$GITHUB_PATH"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            'workflow_exact_line:echo "$extract_root" >> "$GITHUB_PATH":expected=1:actual=0',
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                '          python3 -m py_compile "${scripts[@]}"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            'workflow_exact_line:python3 -m py_compile "${scripts[@]}":expected=1:actual=0',
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Run current Phase 2 toolchain make route\n        run: make -C zigux phase2-toolchain\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Run current Phase 2 toolchain make route")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Validate current Phase 12 support bundle\n        run: python3 scripts/zigux/validate-phase12.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Validate current Phase 12 support bundle")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Run current Phase 12 throughput-parity anchor\n        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Run current Phase 12 throughput-parity anchor")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py\n",
                "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py\n        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_exact_line:run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py:expected=1:actual=2",
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "  push:\n    branches: [ master ]\n  pull_request:\n",
                "  push:\n    branches: [ master ]\n    paths:\n      - '.github/workflows/zigux-bootstrap.yml'\n  pull_request:\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_forbidden_marker:  push:\n    branches: [ master ]\n    paths:",
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - 'Documentation/zigux/**'\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_pull_request_path:      - 'Documentation/zigux/**'")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_text = workflow_path.read_text(encoding="utf-8")
        docs_block = (
            "      - name: Self-test current Phase 12 bootstrap docs sanity checker\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test\n"
            "      - name: Check current Phase 12 docs-root sanity markers\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py\n"
        )
        swapped_block = (
            "      - name: Check current Phase 12 docs-root sanity markers\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py\n"
            "      - name: Self-test current Phase 12 bootstrap docs sanity checker\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test\n"
        )
        workflow_path.write_text(
            workflow_text.replace(docs_block, swapped_block, 1),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_order:bootstrap-step-order")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Check current Zig toolchain policy packet\n        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n",
                "      - name: Check current Zig toolchain policy packet\n        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n      - name: Check current Zig toolchain policy packet\n        run: python3 scripts/zigux/check-zig-toolchain.py --self-test\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_step_duplicate:Check current Zig toolchain policy packet:actual=2",
        )

        write_fixture_tree(base)
        survey_path = base / SURVEY_PATH
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "- `PHASE12_RELEASE_CLOSED=no`\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, "survey:`PHASE12_RELEASE_CLOSED=no`")

        print("PHASE12_BOOTSTRAP_LANE_SHAPE_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_LANE_SHAPE_SELF_TEST_CASE_COUNT=13")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 bootstrap workflow lane so the "
            "workflow keeps its shipped current-master tail and the dedicated "
            "docs-sanity checks reviewable."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_BOOTSTRAP_LANE_SHAPE=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_BOOTSTRAP_LANE_SHAPE=pass")
    print(f"PHASE12_BOOTSTRAP_LANE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_BOOTSTRAP_LANE_MARKER_COUNT="
        f"{len(WORKFLOW_STEP_NAMES) + len(WORKFLOW_COMMAND_MARKERS) + len(WORKFLOW_EXACT_LINES) + len(SURVEY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
