#!/usr/bin/env python3
import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
PHASE2_NOTES_PATH = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
THIRD_PARTY_README_PATH = Path("third_party/README.md")

TOOLCHAIN_SELF_TEST = "python3 scripts/zigux/check-zig-toolchain.py --self-test"
TOOLCHAIN_POLICY_ONLY = "python3 scripts/zigux/check-zig-toolchain.py --policy-only"
TOOLCHAIN_ARCHIVE_ONLY = "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"
TOOLCHAIN_ARCHIVE_REPLAY = (
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux"
)

REQUIRED_MARKERS: dict[Path, list[str]] = {
    WORKFLOW_PATH: [
        "- name: Self-test current Zig toolchain checker",
        f"run: {TOOLCHAIN_SELF_TEST}",
        "- name: Check current Zig toolchain policy packet",
        f"run: {TOOLCHAIN_POLICY_ONLY}",
        "- name: Check current pinned Zig archive packet",
        f"run: {TOOLCHAIN_ARCHIVE_ONLY}",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/check-zig-toolchain.py`",
        f"`{TOOLCHAIN_SELF_TEST}`",
        f"`{TOOLCHAIN_POLICY_ONLY}`",
        f"`{TOOLCHAIN_ARCHIVE_ONLY}`",
    ],
    PHASE2_NOTES_PATH: [
        "`scripts/zigux/check-zig-toolchain.py`",
        f"`{TOOLCHAIN_SELF_TEST}`",
        f"`{TOOLCHAIN_POLICY_ONLY}`",
        f"`{TOOLCHAIN_ARCHIVE_ONLY}`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-zig-toolchain.py`",
        f"`{TOOLCHAIN_SELF_TEST}`",
        f"`{TOOLCHAIN_POLICY_ONLY}`",
        f"`{TOOLCHAIN_ARCHIVE_ONLY}`",
        f"`{TOOLCHAIN_ARCHIVE_REPLAY}`",
    ],
    TESTS_README_PATH: [
        "`scripts/zigux/check-zig-toolchain.py`",
        f"`{TOOLCHAIN_SELF_TEST}`",
        f"`{TOOLCHAIN_POLICY_ONLY}`",
        f"`{TOOLCHAIN_ARCHIVE_ONLY}`",
        f"`{TOOLCHAIN_ARCHIVE_REPLAY}`",
    ],
    THIRD_PARTY_README_PATH: [
        "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
        f"`{TOOLCHAIN_ARCHIVE_REPLAY}`",
        "`zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`",
    ],
}


def find_missing_markers(text: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def read_required_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required path: {relative_path}") from exc


def evaluate_packet(root: Path) -> dict[Path, list[str]]:
    missing: dict[Path, list[str]] = {}
    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_required_text(root, relative_path)
        missing_markers = find_missing_markers(text, markers)
        if missing_markers:
            missing[relative_path] = missing_markers
    return missing


def write_sample_root(root: Path) -> None:
    samples = {
        WORKFLOW_PATH: "\n".join(
            [
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Zig toolchain checker",
                f"        run: {TOOLCHAIN_SELF_TEST}",
                "      - name: Check current Zig toolchain policy packet",
                f"        run: {TOOLCHAIN_POLICY_ONLY}",
                "      - name: Check current pinned Zig archive packet",
                f"        run: {TOOLCHAIN_ARCHIVE_ONLY}",
                "",
            ]
        ),
        SCRIPTS_README_PATH: "\n".join(
            [
                "# scripts/zigux",
                f"- `scripts/zigux/check-zig-toolchain.py`",
                f"- `{TOOLCHAIN_SELF_TEST}`",
                f"- `{TOOLCHAIN_POLICY_ONLY}`",
                f"- `{TOOLCHAIN_ARCHIVE_ONLY}`",
                "",
            ]
        ),
        PHASE2_NOTES_PATH: "\n".join(
            [
                "# Phase 2 Toolchain Bootstrap Notes",
                f"- `scripts/zigux/check-zig-toolchain.py`",
                f"- `{TOOLCHAIN_SELF_TEST}`",
                f"- `{TOOLCHAIN_POLICY_ONLY}`",
                f"- `{TOOLCHAIN_ARCHIVE_ONLY}`",
                "",
            ]
        ),
        REVIEW_CHECKLIST_PATH: "\n".join(
            [
                "# Zigux Review Checklist",
                f"- `scripts/zigux/check-zig-toolchain.py`",
                f"- `{TOOLCHAIN_SELF_TEST}`",
                f"- `{TOOLCHAIN_POLICY_ONLY}`",
                f"- `{TOOLCHAIN_ARCHIVE_ONLY}`",
                f"- `{TOOLCHAIN_ARCHIVE_REPLAY}`",
                "",
            ]
        ),
        TESTS_README_PATH: "\n".join(
            [
                "# zigux/tests",
                f"- `scripts/zigux/check-zig-toolchain.py`",
                f"- `{TOOLCHAIN_SELF_TEST}`",
                f"- `{TOOLCHAIN_POLICY_ONLY}`",
                f"- `{TOOLCHAIN_ARCHIVE_ONLY}`",
                f"- `{TOOLCHAIN_ARCHIVE_REPLAY}`",
                "",
            ]
        ),
        THIRD_PARTY_README_PATH: "\n".join(
            [
                "# Zigux third-party archives",
                "- `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                f"- `{TOOLCHAIN_ARCHIVE_REPLAY}`",
                "- `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`",
                "",
            ]
        ),
    }

    for relative_path, content in samples.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_equal(actual, expected) -> None:
        nonlocal case_count
        assert actual == expected
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_checker_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        expect_equal(evaluate_packet(root), {})

        workflow_path = root / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(TOOLCHAIN_POLICY_ONLY, "python3 missing.py"),
            encoding="utf-8",
        )
        expect_equal(
            evaluate_packet(root),
            {WORKFLOW_PATH: [f"run: {TOOLCHAIN_POLICY_ONLY}"]},
        )

        write_sample_root(root)
        third_party_path = root / THIRD_PARTY_README_PATH
        third_party_path.write_text(
            third_party_path.read_text(encoding="utf-8").replace(
                "`zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`",
                "`duplicate-archive`",
            ),
            encoding="utf-8",
        )
        expect_equal(
            evaluate_packet(root),
            {THIRD_PARTY_README_PATH: ["`zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`"]},
        )

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 2 check-zig-toolchain reminder packet drifts."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect. Defaults to the current Zigux root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local validation.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker packet tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        missing = evaluate_packet(args.root)
    except ValueError as exc:
        print("PHASE2_TOOLCHAIN_CHECKER_PACKET=invalid")
        print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_ROOT={args.root}")
        print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_NOTE={exc}")
        return 1

    if missing:
        print("PHASE2_TOOLCHAIN_CHECKER_PACKET=fail")
        print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_ROOT={args.root}")
        for relative_path, markers in missing.items():
            key = (
                str(relative_path)
                .upper()
                .replace("/", "_")
                .replace(".", "_")
                .replace("-", "_")
            )
            print(f"MISSING_{key}_MARKERS")
            for marker in markers:
                print(marker)
        return 1

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_ROOT={args.root}")
    print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_WORKFLOW_MARKER_COUNT={len(REQUIRED_MARKERS[WORKFLOW_PATH])}")
    print("PHASE2_TOOLCHAIN_CHECKER_PACKET_SHARED_COMMAND_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
