#!/usr/bin/env python3
"""Guard Phase 1 rbtree cached-leftmost paths against perf-gate drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/rbtree.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

EXPECTED_HELPER_MARKERS = (
    "pub const RootCached = struct {",
    "leftmost: ?*Node = null,",
    "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
)

EXPECTED_SMOKE_MARKERS = (
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
)

CACHED_FUNCTION_RULES = {
    "insertColorCached": {
        "signature": "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
        "required": ("root.leftmost = node;", "insertColor(node, &root.root);"),
        "forbidden": ("first(", "minimum(", "while (root", "while (root.root"),
    },
    "addCached": {
        "signature": "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
        "required": ("var leftmost = true;", "leftmost = false;", "return if (leftmost) node else null;"),
        "forbidden": ("first(", "minimum(", "root.leftmost = first", "root.leftmost = minimum"),
    },
    "findAddCached": {
        "signature": "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
        "required": ("var leftmost = true;", "leftmost = false;", "insertColorCached(node, root, leftmost);"),
        "forbidden": ("first(", "minimum(", "root.leftmost = first", "root.leftmost = minimum"),
    },
    "eraseCached": {
        "signature": "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
        "required": ("if (root.leftmost == node) {", "const leftmost = next(node);", "root.leftmost = leftmost;", "return leftmost;"),
        "forbidden": ("root.leftmost = first", "root.leftmost = minimum", "minimum(root", "first(&root.root"),
    },
    "replaceNodeCached": {
        "signature": "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
        "required": ("if (root.leftmost == victim) {", "root.leftmost = new;", "replaceNode(victim, new, &root.root);"),
        "forbidden": ("root.leftmost = first", "root.leftmost = minimum", "minimum(root", "first(&root.root"),
    },
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def function_body(text: str, signature: str) -> str | None:
    start = text.find(signature)
    if start < 0:
        return None
    brace = text.find("{", start)
    if brace < 0:
        return None
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (HELPER_REL, SMOKE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    smoke_text = load_text(root, SMOKE_REL)

    for marker in EXPECTED_HELPER_MARKERS:
        failures.extend(require_once(helper_text, f"helper_marker:{marker}", marker))
    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_once(smoke_text, f"smoke_marker:{marker}", marker))

    for name, rule in CACHED_FUNCTION_RULES.items():
        body = function_body(helper_text, rule["signature"])
        if body is None:
            failures.append(f"cached_function:{name}:missing_or_unbalanced")
            continue
        for marker in rule["required"]:
            if marker not in body:
                failures.append(f"cached_function:{name}:missing_required:{marker}")
        for marker in rule["forbidden"]:
            if marker in body:
                failures.append(f"cached_function:{name}:forbidden_scan_marker:{marker}")

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_helper() -> str:
    return """pub const RootCached = struct {
    leftmost: ?*Node = null,
};
pub fn insertColor(node: *Node, root: *Root) void { _ = node; _ = root; }
pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {
    if (leftmost) {
        root.leftmost = node;
    }
    insertColor(node, &root.root);
}
pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {
    var leftmost = true;
    while (link.*) |current| {
        if (less(node, current)) {} else { leftmost = false; }
    }
    insertColorCached(node, root, leftmost);
    return if (leftmost) node else null;
}
pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {
    var leftmost = true;
    while (link.*) |current| {
        if (cmp(node, current) < 0) {} else { leftmost = false; }
    }
    insertColorCached(node, root, leftmost);
    return null;
}
pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {
    if (root.leftmost == node) {
        const leftmost = next(node);
        root.leftmost = leftmost;
        erase(node, &root.root);
        return leftmost;
    }
    erase(node, &root.root);
    return null;
}
pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {
    if (root.leftmost == victim) {
        root.leftmost = new;
    }
    replaceNode(victim, new, &root.root);
}
"""


def sample_smoke() -> str:
    return "\n".join(EXPECTED_SMOKE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, sample_helper())
    write_file(root, SMOKE_REL, sample_smoke())


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str | None]] = [("success", None, None)]
    cases.extend((f"helper_missing_{idx}", HELPER_REL.as_posix(), marker) for idx, marker in enumerate(EXPECTED_HELPER_MARKERS))
    cases.extend((f"smoke_missing_{idx}", SMOKE_REL.as_posix(), marker) for idx, marker in enumerate(EXPECTED_SMOKE_MARKERS))
    cases.extend(
        (
            f"cached_forbidden_{name}",
            HELPER_REL.as_posix(),
            next(iter(rule["required"])),
        )
        for name, rule in CACHED_FUNCTION_RULES.items()
    )
    cases.append(("cached_scan_regression", HELPER_REL.as_posix(), "root.leftmost = new;"))

    for name, relative_path, marker in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-rbtree-cached-perf-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if marker is not None and relative_path is not None:
                path = root / relative_path
                text = path.read_text(encoding="utf-8")
                if name == "cached_scan_regression":
                    text = text.replace(marker, "root.leftmost = first(&root.root);")
                else:
                    text = text.replace(marker, "", 1)
                path.write_text(text, encoding="utf-8")
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print(f"phase1-rbtree-cached-perf-gate:self-test:ok:{len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in negative coverage tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("phase1-rbtree-cached-perf-gate:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
