const std = @import("std");
const testing = std.testing;

const max_validator_bytes = 1024 * 1024;

fn readValidatorSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/validate-phase2-closure.py",
        allocator,
        .limited(max_validator_bytes),
    ) catch |err| switch (err) {
        error.FileNotFound => std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            "../scripts/zigux/validate-phase2-closure.py",
            allocator,
            .limited(max_validator_bytes),
        ),
        else => err,
    };
}

fn requireContains(source: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

test "closure validator keeps explicit cli entrypoint and root option" {
    const source = try readValidatorSource(testing.allocator);
    defer testing.allocator.free(source);

    try requireContains(source, "def main() -> int:");
    try requireContains(source, "if __name__ == \"__main__\":");
    try requireContains(source, "raise SystemExit(main())");
    try requireContains(source, "parser = argparse.ArgumentParser(");
    try requireContains(source, "parser.add_argument(\"--root\", type=Path, default=DEFAULT_ROOT");
    try requireContains(source, "args.root.resolve()");
}

test "closure validator keeps self-test entrypoint and case-count output" {
    const source = try readValidatorSource(testing.allocator);
    defer testing.allocator.free(source);

    try requireContains(source, "def run_self_test() -> int:");
    try requireContains(source, "parser.add_argument(\"--self-test\", action=\"store_true\"");
    try requireContains(source, "if args.self_test:");
    try requireContains(source, "return run_self_test()");
    try requireContains(source, "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass");
    try requireContains(source, "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}");
}

test "closure validator keeps current public success packet constants" {
    const source = try readValidatorSource(testing.allocator);
    defer testing.allocator.free(source);

    try requireContains(source, "PHASE2_CLOSURE_VALIDATION=pass");
    try requireContains(source, "PHASE2_CLOSURE_STATUS=parked");
    try requireContains(source, "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure");
    try requireContains(source, "PHASE2_CLOSURE_REMAINING_GAPS=");
    try requireContains(source, "PHASE2_CLOSURE_VALIDATION=fail");
}
