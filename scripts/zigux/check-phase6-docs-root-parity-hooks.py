#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/check-phase6-docs-root-parity-hooks.py",
    "Documentation/zigux/README.md",
]

DOCS_ROOT_EXACT_ONCE_MARKERS = [
    "`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, and `Documentation/zigux/phase6-helper-parity-catalog.md` are the current shared notes for the bounded `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig` leaf-helper packet.",
    "`python3 scripts/zigux/validate-phase6.py`, `make -C zigux phase6-validate`, and `make -C zigux phase6` are the published validator-first shared replay path for the current Phase 6 helper tranche.",
    "`python3 scripts/zigux/check-phase6-base64-c-parity.py`, `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and `python3 scripts/zigux/check-phase6-hexdump-c-parity.py` are the shipped external C-vs-Zig review hooks for the bounded base64, bsearch, checksum, and hexdump portability surfaces.",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    docs_root = read_text(root, "Documentation/zigux/README.md")
    missing_markers: list[str] = []
    for marker in DOCS_ROOT_EXACT_ONCE_MARKERS:
        count = docs_root.count(marker)
        if count != 1:
            missing_markers.append(f"docs_root_exact_once:{count}:{marker}")
    return [], missing_markers


def write_fixture(root: Path) -> None:
    for rel_path in FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == "Documentation/zigux/README.md":
            path.write_text("\n".join(DOCS_ROOT_EXACT_ONCE_MARKERS) + "\n", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase6-docs-root-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase6-docs-root-self-test:{label}:expected_missing_marker:{expected}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_docs_root_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase6-docs-root-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        docs_root_path = root / "Documentation/zigux/README.md"
        original_docs_root = docs_root_path.read_text(encoding="utf-8")

        docs_root_path.write_text(
            original_docs_root.replace(DOCS_ROOT_EXACT_ONCE_MARKERS[2], "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_external_parity_sentence",
            root,
            f"docs_root_exact_once:0:{DOCS_ROOT_EXACT_ONCE_MARKERS[2]}",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")

        docs_root_path.write_text(
            original_docs_root + DOCS_ROOT_EXACT_ONCE_MARKERS[2] + "\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "duplicate_external_parity_sentence",
            root,
            f"docs_root_exact_once:2:{DOCS_ROOT_EXACT_ONCE_MARKERS[2]}",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")

        docs_root_path.write_text(
            original_docs_root + DOCS_ROOT_EXACT_ONCE_MARKERS[1] + "\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "duplicate_validator_first_sentence",
            root,
            f"docs_root_exact_once:2:{DOCS_ROOT_EXACT_ONCE_MARKERS[1]}",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")

        docs_root_path.write_text(
            original_docs_root.replace(DOCS_ROOT_EXACT_ONCE_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_shared_notes_sentence",
            root,
            f"docs_root_exact_once:0:{DOCS_ROOT_EXACT_ONCE_MARKERS[0]}",
        )

    print("PHASE6_DOCS_ROOT_PARITY_HOOKS_SELF_TEST=pass")
    print("PHASE6_DOCS_ROOT_PARITY_HOOKS_SELF_TEST_CASE_COUNT=5")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE6_DOCS_ROOT_PARITY_HOOKS=fail")
    print("MISSING_PHASE6_DOCS_ROOT_PARITY_HOOK_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE6_DOCS_ROOT_PARITY_HOOK_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE6_DOCS_ROOT_PARITY_HOOKS=fail")
    print("MISSING_PHASE6_DOCS_ROOT_PARITY_HOOK_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE6_DOCS_ROOT_PARITY_HOOK_MARKERS_END")
    sys.exit(1)

print("PHASE6_DOCS_ROOT_PARITY_HOOKS=pass")
print(f"PHASE6_DOCS_ROOT_PARITY_HOOK_FILE_COUNT={len(FILES)}")
print(f"PHASE6_DOCS_ROOT_PARITY_HOOK_MARKER_COUNT={len(DOCS_ROOT_EXACT_ONCE_MARKERS)}")
