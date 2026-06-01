#!/usr/bin/env python3
"""Fail-closed guard for the live Phase 11 bootstrap support packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 3 else SELF_PATH.parent

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
SHARED_CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

WORKFLOW_MARKERS = (
    "- name: Validate current Phase 11 support bundle",
    "run: make -C zigux phase11-validate",
)

MAKEFILE_MARKERS = (
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

SHARED_CONTRACT_MARKERS = (
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate` explicit together instead of reviving",
    "removed `phase11-contract`, `phase11`, `phase11-hvc-survey`,",
)

SCRIPTS_README_MARKERS = (
    "## Phase 11",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`scripts/zigux/validate-phase11.py`",
    "`make -C zigux phase11-validate`",
)

TESTS_README_MARKERS = (
    "## Phase 11 tests-root packet",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def run_check(root: Path) -> None:
    require_markers(root, WORKFLOW_PATH, "workflow", WORKFLOW_MARKERS)
    require_markers(root, MAKEFILE_PATH, "makefile", MAKEFILE_MARKERS)
    require_markers(root, SHARED_CONTRACT_PATH, "shared-contract", SHARED_CONTRACT_MARKERS)
    require_markers(root, SCRIPTS_README_PATH, "scripts-readme", SCRIPTS_README_MARKERS)
    require_markers(root, TESTS_README_PATH, "tests-readme", TESTS_README_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / WORKFLOW_PATH,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate current Phase 11 support bundle",
                "        run: make -C zigux phase11-validate",
                "",
            )
        ),
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            (
                "phase11-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                "",
            )
        ),
    )
    write(
        root / SHARED_CONTRACT_PATH,
        "\n".join(
            (
                "# Phase 11 Shared Replay Contract",
                "Keep the scripts-root reminder honest too: broader contributor-facing summaries should keep",
                "`scripts/zigux/validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`,",
                "`make -C zigux phase11-validate` explicit together instead of reviving",
                "removed `phase11-contract`, `phase11`, `phase11-hvc-survey`,",
                "",
            )
        ),
    )
    write(
        root / SCRIPTS_README_PATH,
        "\n".join(
            (
                "# scripts/zigux",
                "## Phase 11",
                "- `scripts/zigux/check-phase11-build-inventory.py`",
                "- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `make -C zigux phase11-validate`",
                "",
            )
        ),
    )
    write(
        root / TESTS_README_PATH,
        "\n".join(
            (
                "# zigux/tests",
                "## Phase 11 tests-root packet",
                "- `scripts/zigux/check-phase11-build-inventory.py`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `zigux/Makefile`",
                "- `make -C zigux phase11-validate`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "",
            )
        ),
    )


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    build_fixture(root)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_bootstrap_support_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_workflow = tmpdir / "missing_workflow"
        shutil.copytree(fixture, missing_workflow, dirs_exist_ok=True)
        write(
            missing_workflow / WORKFLOW_PATH,
            read_text(missing_workflow / WORKFLOW_PATH).replace(
                "run: make -C zigux phase11-validate",
                "run: make -C zigux phase11",
            ),
        )
        expect_failure(missing_workflow, "make -C zigux phase11-validate")
        case_count += 1

        missing_makefile = tmpdir / "missing_makefile"
        shutil.copytree(fixture, missing_makefile, dirs_exist_ok=True)
        write(
            missing_makefile / MAKEFILE_PATH,
            read_text(missing_makefile / MAKEFILE_PATH).replace(
                "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
                1,
            ),
        )
        expect_failure(missing_makefile, "phase11_hvc_targetless_unregister_gap_build.zig")
        case_count += 1

        missing_contract = tmpdir / "missing_contract"
        shutil.copytree(fixture, missing_contract, dirs_exist_ok=True)
        write(
            missing_contract / SHARED_CONTRACT_PATH,
            read_text(missing_contract / SHARED_CONTRACT_PATH).replace(
                "removed `phase11-contract`, `phase11`, `phase11-hvc-survey`,",
                "",
            ),
        )
        expect_failure(missing_contract, "removed `phase11-contract`, `phase11`, `phase11-hvc-survey`,")
        case_count += 1

        missing_scripts = tmpdir / "missing_scripts"
        shutil.copytree(fixture, missing_scripts, dirs_exist_ok=True)
        write(
            missing_scripts / SCRIPTS_README_PATH,
            read_text(missing_scripts / SCRIPTS_README_PATH).replace(
                "- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`\n",
                "",
            ),
        )
        expect_failure(missing_scripts, "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`")
        case_count += 1

        missing_tests = tmpdir / "missing_tests"
        shutil.copytree(fixture, missing_tests, dirs_exist_ok=True)
        write(
            missing_tests / TESTS_README_PATH,
            read_text(missing_tests / TESTS_README_PATH).replace(
                "- `make -C zigux phase11-validate`\n",
                "",
            ),
        )
        expect_failure(missing_tests, "`make -C zigux phase11-validate`")
        case_count += 1

        missing_file = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        (missing_file / SCRIPTS_README_PATH).unlink()
        expect_failure(missing_file, str(SCRIPTS_README_PATH))
        case_count += 1

        print("PHASE11_BOOTSTRAP_SUPPORT_PACKET_SELF_TEST=pass")
        print(f"PHASE11_BOOTSTRAP_SUPPORT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_BOOTSTRAP_SUPPORT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_BOOTSTRAP_SUPPORT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
