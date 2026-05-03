#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_RBTREE_ROOT")
    if override:
        return Path(override)
    path = Path(__file__).resolve()
    return path.parents[2] if len(path.parents) >= 3 else path.parent


ROOT = repo_root()

REQUIRED_FILES = [
    "Documentation/zigux/phase1-closure.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "tools/lib/rbtree.zig",
]

RBTREE_MANIFEST_SUMMARY = (
    "Committed C-backed parity coverage includes ordered forward and reverse traversal plus "
    "replaceNode, eraseInit, postorder traversal, and detached-node state checks, while "
    "Linux-style rb_* alias parity remains explicitly out of scope for this closed Phase 1 tranche."
)
RBTREE_SHARED_PARITY_SCOPE_NOTE = (
    "The committed shared Phase 1 fixture still stops at traversal, replaceNode, eraseInit, "
    "postorder traversal, and detached-node state checks; duplicate-key search, duplicate-range "
    "iterators, and cached-root minima tracking are currently recorded as direct Zig unit coverage "
    "only in this closed tranche."
)
RBTREE_ALIAS_GAP_NOTE = (
    "Linux-style rb_* alias surface parity is still missing for the already-ported entry points, "
    "and that remaining surface stays explicitly out of scope for the closed Phase 1 tranche until "
    "a later bounded repair lands."
)

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state while Linux-style rb_* alias parity remains explicitly out of scope for this closed tranche",
    "PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* alias parity for the already-ported entry points, and that remaining surface stays explicitly out of scope until a later bounded repair lands",
    "PHASE1_RBTREE_ALIAS_GAP_GATE=phase1 closure validation fails closed if tools/lib/rbtree.zig grows Linux-style rb_* aliases before the closed helper tranche is deliberately reopened",
]

FORBIDDEN_RBTREE_SNIPPETS = [
    "pub fn rb_",
    "pub const rb_",
]


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(block: str, items: list[str]) -> int:
    print("PHASE1_RBTREE_ALIAS_GAP=fail")
    print(f"{block}_START")
    for item in items:
        print(item)
    print(f"{block}_END")
    return 1


def validate_manifest() -> list[str]:
    issues: list[str] = []
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    notes = manifest.get("helper_review_notes")
    if not isinstance(notes, dict):
        return ["phase1_manifest:helper_review_notes"]

    rbtree = notes.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree, dict):
        return ["phase1_manifest:tools/lib/rbtree.zig:expected_object"]

    if rbtree.get("summary") != RBTREE_MANIFEST_SUMMARY:
        issues.append("phase1_manifest:tools/lib/rbtree.zig:summary:mismatch")
    if rbtree.get("shared_parity_scope_note") != RBTREE_SHARED_PARITY_SCOPE_NOTE:
        issues.append("phase1_manifest:tools/lib/rbtree.zig:shared_parity_scope_note:mismatch")
    if rbtree.get("alias_gap_note") != RBTREE_ALIAS_GAP_NOTE:
        issues.append("phase1_manifest:tools/lib/rbtree.zig:alias_gap_note:mismatch")
    return issues


def validate_closure() -> list[str]:
    issues: list[str] = []
    closure = read_text("Documentation/zigux/phase1-closure.md")
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure:
            issues.append(f"phase1_closure:{marker}")
    return issues


def validate_rbtree_surface() -> list[str]:
    issues: list[str] = []
    text = read_text("tools/lib/rbtree.zig")
    for snippet in FORBIDDEN_RBTREE_SNIPPETS:
        if snippet in text:
            issues.append(f"tools/lib/rbtree.zig:forbidden_alias_surface:{snippet}")
    return issues


def main() -> int:
    missing_files = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    if missing_files:
        return fail("MISSING_PHASE1_RBTREE_ALIAS_GAP_FILES", missing_files)

    manifest_issues = validate_manifest()
    if manifest_issues:
        return fail("MISSING_PHASE1_RBTREE_ALIAS_GAP_MANIFEST_MARKERS", manifest_issues)

    closure_issues = validate_closure()
    if closure_issues:
        return fail("MISSING_PHASE1_RBTREE_ALIAS_GAP_CLOSURE_MARKERS", closure_issues)

    rbtree_issues = validate_rbtree_surface()
    if rbtree_issues:
        return fail("UNEXPECTED_PHASE1_RBTREE_ALIAS_SURFACE", rbtree_issues)

    print("PHASE1_RBTREE_ALIAS_GAP=pass")
    print(f"PHASE1_RBTREE_ALIAS_GAP_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_RBTREE_ALIAS_GAP_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + 3 + len(FORBIDDEN_RBTREE_SNIPPETS)}"
    )
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-alias-gap-") as tmp:
        root = Path(tmp)
        write(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n",
        )
        manifest = {
            "helper_review_notes": {
                "tools/lib/rbtree.zig": {
                    "summary": RBTREE_MANIFEST_SUMMARY,
                    "shared_parity_scope_note": RBTREE_SHARED_PARITY_SCOPE_NOTE,
                    "alias_gap_note": RBTREE_ALIAS_GAP_NOTE,
                }
            }
        }
        write(
            root / "zigux/tests/fixtures/phase1_helper_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        write(
            root / "tools/lib/rbtree.zig",
            "pub const Node = struct {};\npub fn iterateMatches() void {}\n",
        )

        env = dict(os.environ)
        env["ZIGUX_PHASE1_RBTREE_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code != 0:
            print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=fail")
            return 1

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            closure_text.replace(REQUIRED_CLOSURE_MARKERS[2] + "\n", "", 1),
            encoding="utf-8",
        )
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code == 0:
            print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=fail")
            return 1
        write(closure_path, "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["shared_parity_scope_note"] = "old note"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code == 0:
            print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=fail")
            return 1
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["shared_parity_scope_note"] = (
            RBTREE_SHARED_PARITY_SCOPE_NOTE
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")

        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["alias_gap_note"] = "old note"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code == 0:
            print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=fail")
            return 1
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["alias_gap_note"] = (
            RBTREE_ALIAS_GAP_NOTE
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")

        rbtree_path = root / "tools/lib/rbtree.zig"
        write(
            rbtree_path,
            "pub const Node = struct {};\npub fn rb_first() void {}\n",
        )
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code == 0:
            print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=fail")
            return 1

    print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST=pass")
    print("PHASE1_RBTREE_ALIAS_GAP_SELF_TEST_CASE_COUNT=4")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
