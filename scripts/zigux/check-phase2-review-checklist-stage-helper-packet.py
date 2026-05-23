#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTES_PATH = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
INSTALL_VERIFY_PATH = Path("scripts/zigux/check-lane05-install-zig-archive-verification.py")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
STAGE_CONTRACT_PATH = Path("scripts/zigux/check-lane05-stage-helper-contract.py")
STAGE_SELFTEST_PATH = Path("scripts/zigux/check-lane05-stage-helper-selftest.py")

REVIEW_CHECKLIST_MARKERS = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

DOCS_README_MARKERS = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

BOOTSTRAP_NOTES_MARKERS = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

WORKFLOW_MARKERS = (
    "- name: Self-test current Lane 05 install-zig archive verification checker",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "- name: Check current Lane 05 install-zig archive verification packet",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "- name: Self-test current staged pinned Zig archive helper",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "- name: Self-test current Lane 05 stage helper contract checker",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "- name: Check current Lane 05 stage helper contract packet",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "- name: Self-test current Lane 05 stage helper selftest checker",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "- name: Check current Lane 05 stage helper selftest packet",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

INSTALL_VERIFY_MARKERS = (
    "INSTALL_ZIG = Path(\"scripts/zigux/install-zig.py\")",
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass",
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
)

STAGE_HELPER_MARKERS = (
    "THIRD_PARTY_DIR = Path(\"third_party\")",
    "duplicate-suffix archive copies",
    "STAGE_PINNED_ZIG_ARCHIVE=pass",
    "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=",
)

STAGE_CONTRACT_MARKERS = (
    "STAGE_HELPER_PATH = Path(\"scripts/zigux/stage-pinned-zig-archive.py\")",
    "LANE05_STAGE_HELPER_CONTRACT=pass",
    "LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass",
    "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=",
)

STAGE_SELFTEST_MARKERS = (
    "LANE05_STAGE_HELPER_SELFTEST=pass",
    "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
    "STAGE_HELPER_SELF_TEST_STEP = \"- name: Self-test current staged pinned Zig archive helper\"",
    "CONTRACT_SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"expected {label} `{earlier}` before `{later}`")


def check_file_markers(root: Path, relative_path: Path, markers: tuple[str, ...], label: str) -> int:
    text = read_text(root / relative_path)
    for marker in markers:
        require_marker(text, marker, label)
    return len(markers)


def check_packet(root: Path) -> dict[str, int]:
    counts = {
        "review_checklist": check_file_markers(
            root, REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS, "review-checklist stage-helper marker"
        ),
        "docs_readme": check_file_markers(root, DOCS_README_PATH, DOCS_README_MARKERS, "docs-root stage-helper marker"),
        "bootstrap_notes": check_file_markers(
            root, BOOTSTRAP_NOTES_PATH, BOOTSTRAP_NOTES_MARKERS, "bootstrap-note stage-helper marker"
        ),
        "workflow": check_file_markers(root, WORKFLOW_PATH, WORKFLOW_MARKERS, "workflow stage-helper marker"),
        "install_verify": check_file_markers(
            root, INSTALL_VERIFY_PATH, INSTALL_VERIFY_MARKERS, "install-verification marker"
        ),
        "stage_helper": check_file_markers(root, STAGE_HELPER_PATH, STAGE_HELPER_MARKERS, "stage-helper marker"),
        "stage_contract": check_file_markers(
            root, STAGE_CONTRACT_PATH, STAGE_CONTRACT_MARKERS, "stage-helper contract marker"
        ),
        "stage_selftest": check_file_markers(
            root, STAGE_SELFTEST_PATH, STAGE_SELFTEST_MARKERS, "stage-helper selftest marker"
        ),
    }

    review_text = read_text(root / REVIEW_CHECKLIST_PATH)
    require_order(
        review_text,
        "scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
        "review-checklist stage-helper path order",
    )
    require_order(
        review_text,
        "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
        "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "review-checklist stage-helper command order",
    )

    workflow_text = read_text(root / WORKFLOW_PATH)
    require_order(
        workflow_text,
        "- name: Check current Lane 05 install-zig archive verification packet",
        "- name: Self-test current staged pinned Zig archive helper",
        "workflow stage-helper order",
    )
    require_order(
        workflow_text,
        "- name: Self-test current staged pinned Zig archive helper",
        "- name: Self-test current Lane 05 stage helper contract checker",
        "workflow stage-helper order",
    )
    require_order(
        workflow_text,
        "- name: Self-test current Lane 05 stage helper contract checker",
        "- name: Check current Lane 05 stage helper contract packet",
        "workflow stage-helper order",
    )
    require_order(
        workflow_text,
        "- name: Check current Lane 05 stage helper contract packet",
        "- name: Self-test current Lane 05 stage helper selftest checker",
        "workflow stage-helper order",
    )
    require_order(
        workflow_text,
        "- name: Self-test current Lane 05 stage helper selftest checker",
        "- name: Check current Lane 05 stage helper selftest packet",
        "workflow stage-helper order",
    )
    return counts


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root / REVIEW_CHECKLIST_PATH,
        "\n".join(
            (
                "# Zigux Review Checklist",
                "",
                "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `third_party/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, `scripts/zigux/check-lane05-stage-helper-selftest.py`, and `scripts/zigux/check-phase2-kbuild-routes.py` still agree on the current directly readable Phase 2 packet?",
                "* keep `python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`, `python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`, `python3 scripts/zigux/check-lane05-stage-helper-contract.py`, `python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`, and `python3 scripts/zigux/check-lane05-stage-helper-selftest.py` explicit as the current staged repo-local archive helper packet.",
            )
        )
        + "\n",
    )
    write_text(
        root / DOCS_README_PATH,
        "\n".join(
            (
                "# Zigux Documentation",
                "* `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the staged repo-local archive helper packet explicit from the docs root.",
            )
        )
        + "\n",
    )
    write_text(
        root / BOOTSTRAP_NOTES_PATH,
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "* `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the staged repo-local archive helper packet explicit beside the local-first archive workflow.",
                "* `.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`, `python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`, `python3 scripts/zigux/check-lane05-stage-helper-contract.py`, `python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`, and `python3 scripts/zigux/check-lane05-stage-helper-selftest.py` so the staged repo-local archive helper packet stays reviewable at the same policy-driven boundary.",
            )
        )
        + "\n",
    )
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Lane 05 install-zig archive verification checker",
                "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
                "      - name: Check current Lane 05 install-zig archive verification packet",
                "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
                "      - name: Self-test current staged pinned Zig archive helper",
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
                "      - name: Self-test current Lane 05 stage helper contract checker",
                "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
                "      - name: Check current Lane 05 stage helper contract packet",
                "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
                "      - name: Self-test current Lane 05 stage helper selftest checker",
                "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
                "      - name: Check current Lane 05 stage helper selftest packet",
                "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
            )
        )
        + "\n",
    )
    write_text(
        root / INSTALL_VERIFY_PATH,
        "\n".join(
            (
                "INSTALL_ZIG = Path(\"scripts/zigux/install-zig.py\")",
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
                "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass",
                "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass",
            )
        )
        + "\n",
    )
    write_text(
        root / STAGE_HELPER_PATH,
        "\n".join(
            (
                "THIRD_PARTY_DIR = Path(\"third_party\")",
                "duplicate-suffix archive copies",
                "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=",
                "STAGE_PINNED_ZIG_ARCHIVE=pass",
                "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
            )
        )
        + "\n",
    )
    write_text(
        root / STAGE_CONTRACT_PATH,
        "\n".join(
            (
                "STAGE_HELPER_PATH = Path(\"scripts/zigux/stage-pinned-zig-archive.py\")",
                "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=",
                "LANE05_STAGE_HELPER_CONTRACT=pass",
                "LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass",
            )
        )
        + "\n",
    )
    write_text(
        root / STAGE_SELFTEST_PATH,
        "\n".join(
            (
                "STAGE_HELPER_SELF_TEST_STEP = \"- name: Self-test current staged pinned Zig archive helper\"",
                "CONTRACT_SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"",
                "LANE05_STAGE_HELPER_SELFTEST=pass",
                "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase2_review_checklist_stage_helper_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        counts = check_packet(root)
        assert counts["review_checklist"] == len(REVIEW_CHECKLIST_MARKERS)
        assert counts["workflow"] == len(WORKFLOW_MARKERS)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="phase2_review_checklist_stage_helper_fail_") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)
            mutator(root)
            try:
                check_packet(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker failure")

    expect_failure(
        lambda root: write_text(root / REVIEW_CHECKLIST_PATH, "# Zigux Review Checklist\n"),
        "review-checklist stage-helper marker",
    )
    expect_failure(
        lambda root: write_text(
            root / WORKFLOW_PATH,
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(
                "      - name: Self-test current staged pinned Zig archive helper\n",
                "",
                1,
            ),
        ),
        "workflow stage-helper marker",
    )
    expect_failure(
        lambda root: write_text(
            root / REVIEW_CHECKLIST_PATH,
            (root / REVIEW_CHECKLIST_PATH).read_text(encoding="utf-8").replace(
                "scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py",
                "scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py",
                1,
            ),
        ),
        "review-checklist stage-helper path order",
    )
    expect_failure(
        lambda root: write_text(
            root / INSTALL_VERIFY_PATH,
            (root / INSTALL_VERIFY_PATH).read_text(encoding="utf-8").replace(
                "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass\n",
                "",
                1,
            ),
        ),
        "install-verification marker",
    )
    expect_failure(
        lambda root: write_text(
            root / STAGE_SELFTEST_PATH,
            (root / STAGE_SELFTEST_PATH).read_text(encoding="utf-8").replace(
                "CONTRACT_SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"\n",
                "",
                1,
            ),
        ),
        "stage-helper selftest marker",
    )

    print("PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 review checklist keeps the staged-archive helper packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for replay validation",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        counts = check_packet(root)
    except ValueError as exc:
        print("PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET=fail")
        print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_ROOT={args.root.resolve()}")
        print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_NOTE={exc}")
        return 1

    print("PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_ROOT={root}")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_REVIEW_MARKER_COUNT={counts['review_checklist']}")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_DOCS_MARKER_COUNT={counts['docs_readme']}")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_BOOTSTRAP_MARKER_COUNT={counts['bootstrap_notes']}")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_WORKFLOW_MARKER_COUNT={counts['workflow']}")
    print(f"PHASE2_REVIEW_CHECKLIST_STAGE_HELPER_PACKET_HELPER_FILE_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())