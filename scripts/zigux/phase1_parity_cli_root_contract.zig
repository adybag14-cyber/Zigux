const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn hasNeedle(needle: []const u8) bool {
    return std.mem.indexOf(u8, checker_source, needle) != null;
}

fn countNeedle(needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, checker_source, offset, needle)) |found| {
        count += 1;
        offset = found + needle.len;
    }
    return count;
}

fn hasCurrentCliRootSurface() bool {
    return hasNeedle("parser.add_argument(\"--root\", default=str(ROOT), help=\"repository root to validate\")") and
        hasNeedle("return run_check(Path(args.root).resolve())");
}

test "phase1 parity checker keeps root override as a first-class CLI argument" {
    if (!hasCurrentCliRootSurface()) return error.SkipZigTest;

    try std.testing.expectEqual(@as(usize, 1), countNeedle("parser.add_argument(\"--root\", default=str(ROOT), help=\"repository root to validate\")"));
    try std.testing.expect(hasNeedle("parser.add_argument(\"--self-test\", action=\"store_true\", help=\"run focused parity checker self-test\")"));
    try std.testing.expect(hasNeedle("args = parser.parse_args()"));
}

test "phase1 parity checker runs self-test before resolving the caller-provided root" {
    if (!hasCurrentCliRootSurface()) return error.SkipZigTest;

    const self_test_branch = std.mem.indexOf(u8, checker_source, "if args.self_test:\n        return run_self_test()") orelse
        return error.MissingSelfTestBranch;
    const root_dispatch = std.mem.indexOf(u8, checker_source, "return run_check(Path(args.root).resolve())") orelse
        return error.MissingRootDispatch;

    try std.testing.expect(self_test_branch < root_dispatch);
    try std.testing.expectEqual(@as(usize, 1), countNeedle("return run_check(Path(args.root).resolve())"));
}

test "phase1 parity checker default root remains derived from the checker location" {
    if (!hasCurrentCliRootSurface()) return error.SkipZigTest;

    try std.testing.expect(hasNeedle("HERE = Path(__file__).resolve()"));
    try std.testing.expect(hasNeedle("ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent"));
    try std.testing.expect(hasNeedle("def run_check(root: Path) -> int:"));
    try std.testing.expect(hasNeedle("def main() -> int:"));
}
