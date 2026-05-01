#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

RBTREE_SOURCE_REL = Path("tools/lib/rbtree.zig")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

RBTREE_SUMMARY = (
    "Committed C-backed parity coverage includes ordered forward and reverse traversal plus "
    "replaceNode, eraseInit, postorder traversal, and detached-node state checks, while "
    "Linux-style rb_* alias parity remains explicitly out of scope for this closed Phase 1 tranche."
)
RBTREE_ALIAS_GAP_NOTE = (
    "Linux-style rb_* alias surface parity is still missing for the already-ported entry points, "
    "and that remaining surface stays explicitly out of scope for the closed Phase 1 tranche until "
    "a later bounded repair lands."
)
RBTREE_ALIAS_GAP_CLOSURE_MARKER = (
    "PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* "
    "alias parity for the already-ported entry points, and that remaining surface stays explicitly "
    "out of scope until a later bounded repair lands"
)
RBTREE_ALIAS_GAP_GATE = (
    "PHASE1_RBTREE_ALIAS_GAP_GATE=phase1 closure validation fails closed if tools/lib/rbtree.zig "
    "grows Linux-style rb_* aliases before the closed helper tranche is deliberately reopened"
)
RBTREE_UNEXPECTED_ALIAS_MARKERS = [
    "pub fn rb_insert_color(",
    "pub fn rb_erase(",
    "pub fn rb_erase_init(",
    "pub fn rb_first(",
    "pub fn rb_last(",
    "pub fn rb_next(",
    "pub fn rb_prev(",
    "pub fn rb_first_postorder(",
    "pub fn rb_next_postorder(",
    "pub fn rb_replace_node(",
    "pub fn rb_first_cached(",
    "pub fn rb_insert_color_cached(",
    "pub fn rb_erase_cached(",
    "pub fn rb_replace_node_cached(",
    "pub fn rb_add_cached(",
    "pub fn rb_add(",
    "pub fn rb_find_add(",
    "pub fn rb_find(",
    "pub fn rb_find_first(",
    "pub fn rb_next_match(",
]


def fail(block: str, items: list[str]) -> None:
    print("PHASE1_RBTREE_ALIAS_GAP_VALIDATION=fail")
    print(f"{block}_START")
    for item in items:
        print(item)
    print(f"{block}_END")
    raise SystemExit(1)


def validate_tree(root: Path) -> list[str]:
    missing: list[str] = []

    for rel in (RBTREE_SOURCE_REL, CLOSURE_REL, MANIFEST_REL):
        if not (root / rel).exists():
            missing.append(f"file:{rel}")
    if missing:
        return missing

    closure = (root / CLOSURE_REL).read_text(encoding="utf-8")
    if RBTREE_ALIAS_GAP_CLOSURE_MARKER not in closure:
        missing.append(f"closure:{RBTREE_ALIAS_GAP_CLOSURE_MARKER}")
    if RBTREE_ALIAS_GAP_GATE not in closure:
        missing.append(f"closure:{RBTREE_ALIAS_GAP_GATE}")

    manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
    review = manifest.get("helper_review_notes", {}).get("tools/lib/rbtree.zig", {})
    if review.get("summary") != RBTREE_SUMMARY:
        missing.append("manifest:tools/lib/rbtree.zig.summary")
    if review.get("alias_gap_note") != RBTREE_ALIAS_GAP_NOTE:
        missing.append("manifest:tools/lib/rbtree.zig.alias_gap_note")

    rbtree_source = (root / RBTREE_SOURCE_REL).read_text(encoding="utf-8")
    for marker in RBTREE_UNEXPECTED_ALIAS_MARKERS:
        if marker in rbtree_source:
            missing.append(f"source:unexpected_alias:{marker}")

    return missing


def expect_failure(root: Path, expected: str, label: str) -> None:
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "zigux" / "check-phase1-rbtree-alias-gap.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        raise SystemExit(f"self-test:{label}:unexpected_pass")
    if expected not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "none"
        raise SystemExit(f"self-test:{label}:missing_expected:{expected}:actual:{actual}")


def write_fixture_tree(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux" / "tests" / "fixtures").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "lib").mkdir(parents=True, exist_ok=True)

    (root / "scripts" / "zigux" / "check-phase1-rbtree-alias-gap.py").write_text(
        Path(__file__).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (root / CLOSURE_REL).write_text(
        "\n".join(
            [
                RBTREE_ALIAS_GAP_CLOSURE_MARKER,
                RBTREE_ALIAS_GAP_GATE,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / MANIFEST_REL).write_text(
        json.dumps(
            {
                "helper_review_notes": {
                    "tools/lib/rbtree.zig": {
                        "summary": RBTREE_SUMMARY,
                        "alias_gap_note": RBTREE_ALIAS_GAP_NOTE,
                    }
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / RBTREE_SOURCE_REL).write_text(
        "pub fn first(root: *const Root) ?*Node { _ = root; return null; }\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_rbtree_alias_gap_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)

        baseline = validate_tree(root)
        if baseline:
            raise SystemExit(f"self-test:baseline_failed:{','.join(baseline)}")

        closure_path = root / CLOSURE_REL
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(original_closure.replace(RBTREE_ALIAS_GAP_CLOSURE_MARKER + "\n", "", 1), encoding="utf-8")
        expect_failure(root, f"closure:{RBTREE_ALIAS_GAP_CLOSURE_MARKER}", "missing_closure_note")
        closure_path.write_text(original_closure, encoding="utf-8")

        manifest_path = root / MANIFEST_REL
        original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        mutated_manifest = json.loads(json.dumps(original_manifest))
        mutated_manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["summary"] = ""
        manifest_path.write_text(json.dumps(mutated_manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "manifest:tools/lib/rbtree.zig.summary", "missing_summary")
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")

        source_path = root / RBTREE_SOURCE_REL
        source_path.write_text(
            source_path.read_text(encoding="utf-8") + "pub fn rb_first(root: *const Root) ?*Node { return first(root); }\n",
            encoding="utf-8",
        )
        expect_failure(root, "source:unexpected_alias:pub fn rb_first(", "unexpected_alias")

    print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=pass")
    print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST_CASE_COUNT=3")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())

    missing = validate_tree(ROOT)
    if missing:
        fail("MISSING_PHASE1_RBTREE_ALIAS_GAP_MARKERS", missing)

    print("PHASE1_RBTREE_ALIAS_GAP_VALIDATION=pass")
    print("PHASE1_RBTREE_ALIAS_GAP_REQUIRED_FILE_COUNT=3")
    print(f"PHASE1_RBTREE_ALIAS_GAP_REQUIRED_ALIAS_COUNT={len(RBTREE_UNEXPECTED_ALIAS_MARKERS)}")
