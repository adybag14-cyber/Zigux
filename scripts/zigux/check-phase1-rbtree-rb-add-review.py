#!/usr/bin/env python3
"""Guard the Phase 1 rbtree rb_add() review anchor against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

HELPER_REL = Path("tools/lib/rbtree.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

ORDERED_ALIAS_TEST = 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"'
RB_ADD_DECL = "pub fn rb_add(node: *Node, root: *Root, less: LessFn) void {"
RB_ADD_FORWARD = "add(node, root, less);"
RB_ADD_TEST_CALL = "rb_add(&alias_entry.node, &alias_root, less);"


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    try:
        helper_text = load_text(root, HELPER_REL)
    except FileNotFoundError:
        return [f"missing:{HELPER_REL}"]

    try:
        manifest = json.loads(load_text(root, MANIFEST_REL))
    except FileNotFoundError:
        return [f"missing:{MANIFEST_REL}"]
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    for marker in (RB_ADD_DECL, RB_ADD_FORWARD, ORDERED_ALIAS_TEST, RB_ADD_TEST_CALL):
        count = helper_text.count(marker)
        if count != 1:
            failures.append(f"helper_marker:{marker}:count={count}")

    if helper_text.find(RB_ADD_DECL) > helper_text.find("pub fn addCached"):
        failures.append("helper_marker:rb_add_not_adjacent_before_addCached")

    try:
        rbtree_packet = manifest["review_anchors"]["tools/lib/rbtree.zig"]
    except (KeyError, TypeError):
        failures.append("manifest:rbtree_review_anchor_packet_missing")
    else:
        ordered_anchor = rbtree_packet.get("ordered_alias_anchor") if isinstance(rbtree_packet, dict) else None
        helper_anchors = rbtree_packet.get("helper_test_anchors") if isinstance(rbtree_packet, dict) else None
        if ordered_anchor != ORDERED_ALIAS_TEST:
            failures.append("manifest:ordered_alias_anchor_drift")
        if not isinstance(helper_anchors, list) or helper_anchors.count(ORDERED_ALIAS_TEST) != 1:
            failures.append("manifest:helper_test_anchors_missing_ordered_alias_anchor")

    return failures


def write_fixture(root: Path) -> None:
    (root / HELPER_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / HELPER_REL).write_text(
        "pub fn add(node: *Node, root: *Root, less: LessFn) void {\n"
        "    _ = node;\n"
        "    _ = root;\n"
        "    _ = less;\n"
        "}\n\n"
        f"{RB_ADD_DECL}\n"
        f"    {RB_ADD_FORWARD}\n"
        "}\n\n"
        "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {\n"
        "    _ = node;\n"
        "    _ = root;\n"
        "    _ = less;\n"
        "    return null;\n"
        "}\n\n"
        f"{ORDERED_ALIAS_TEST} {{\n"
        f"    {RB_ADD_TEST_CALL}\n"
        "}\n",
        encoding="utf-8",
    )
    (root / MANIFEST_REL).write_text(
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/rbtree.zig": {
                        "helper_test_anchors": [ORDERED_ALIAS_TEST],
                        "ordered_alias_anchor": ORDERED_ALIAS_TEST,
                    }
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    cases = (
        ("baseline", None),
        ("missing_decl", lambda text: text.replace(RB_ADD_DECL + "\n", "", 1)),
        ("missing_forward", lambda text: text.replace("    " + RB_ADD_FORWARD + "\n", "", 1)),
        ("missing_test_call", lambda text: text.replace("    " + RB_ADD_TEST_CALL + "\n", "", 1)),
        ("stale_manifest_anchor", None),
    )

    for name, mutate_helper in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-rb-add-{name}-") as tmp:
            root = Path(tmp)
            write_fixture(root)
            if mutate_helper is not None:
                path = root / HELPER_REL
                path.write_text(mutate_helper(path.read_text(encoding="utf-8")), encoding="utf-8")
            if name == "stale_manifest_anchor":
                manifest_path = root / MANIFEST_REL
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["review_anchors"]["tools/lib/rbtree.zig"]["ordered_alias_anchor"] = "stale ordered alias"
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print(f"PHASE1_RBTREE_RB_ADD_REVIEW_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_RB_ADD_REVIEW_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_RB_ADD_REVIEW=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
