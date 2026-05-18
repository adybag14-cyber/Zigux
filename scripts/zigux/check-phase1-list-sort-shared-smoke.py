#!/usr/bin/env python3
"""Guard the current Phase 1 list_sort shared-smoke witness against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

REQUIRED_EXACT_LINES = {
    "list_sort_import": 'const list_sort = @import("list_sort");',
    "smoke_entry_struct": "const ListSortSmokeEntry = struct {",
    "smoke_entry_node": "    node: list_sort.ListHead = .{},",
    "smoke_decl_check": '    try std.testing.expect(@hasDecl(list_sort, "listSort"));',
    "list_head": "    var list_head: list_sort.ListHead = .{};",
    "list_entry_0": "        .{ .key = 2, .ordinal = 0 },",
    "list_entry_1": "        .{ .key = 1, .ordinal = 1 },",
    "list_entry_2": "        .{ .key = 3, .ordinal = 2 },",
    "list_entry_3": "        .{ .key = 1, .ordinal = 3 },",
    "list_entry_4": "        .{ .key = 3, .ordinal = 4 },",
    "list_cmp_less": "            if (lhs.key < rhs.key) return -1;",
    "list_cmp_greater": "            if (lhs.key > rhs.key) return 1;",
    "list_add_tail": "        list_sort.listAddTail(&entry.node, &list_head);",
    "list_sort_call": "    list_sort.listSort(null, &list_head, list_cmp);",
    "list_sorted_keys": "    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, sorted_keys[0..sorted_count]);",
    "list_sorted_ordinals": "    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, sorted_ordinals[0..sorted_count]);",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    smoke_path = root / SMOKE_REL
    if not smoke_path.exists():
        return [f"missing_file:{SMOKE_REL.as_posix()}"]

    text = load_text(root, SMOKE_REL)
    failures: list[str] = []
    for label, line in REQUIRED_EXACT_LINES.items():
        failures.extend(require_exact_line(text, f"{SMOKE_REL.as_posix()}:{label}", line))
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_smoke_text() -> str:
    lines = "\n".join(REQUIRED_EXACT_LINES.values())
    return f"// sample\n{lines}\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, SMOKE_REL, sample_smoke_text())


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str]] = [("success", None, "none")]

    for label, line in REQUIRED_EXACT_LINES.items():
        cases.append((f"missing_{label}", line, "remove"))
        cases.append((f"duplicate_{label}", line, "duplicate"))

    for name, line, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-list-sort-smoke-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if line is not None:
                text = (root / SMOKE_REL).read_text(encoding="utf-8")
                if operation == "remove":
                    (root / SMOKE_REL).write_text(text.replace(line + "\n", "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    (root / SMOKE_REL).write_text(
                        text.replace(line, line + "\n" + line, 1),
                        encoding="utf-8",
                    )

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
                continue

            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-list-sort-shared-smoke:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
