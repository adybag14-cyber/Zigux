const std = @import("std");

const validator_path = "scripts/zigux/validate-phase1-closure.py";

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, validator_path, allocator, .limited(1024 * 1024));
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingNeedle;
    const rest = haystack[first + needle.len ..];
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, rest, needle));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeNeedle;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterNeedle;
    try std.testing.expect(before_index < after_index);
}

test "phase1 closure validator prints collected failures before returning failure" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContainsOnce(validator,
        \\    failures = collect_failures(repo_root(args.root))
    );
    try expectContainsOnce(validator,
        \\    if failures:
    );
    try expectContainsOnce(validator,
        \\        for failure in failures:
    );
    try expectContainsOnce(validator,
        \\            print(failure)
    );
    try expectContainsOnce(validator,
        \\        return 1
    );

    try expectOrdered(validator,
        \\    if failures:
    ,
        \\    print("PHASE1_CLOSURE_VALIDATION=pass")
    );
    try expectOrdered(validator,
        \\            print(failure)
    ,
        \\        return 1
    );
}

test "phase1 closure validator keeps pass markers out of the failure branch" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    const failure_branch_start = std.mem.indexOf(u8, validator,
        \\    if failures:
    ) orelse return error.MissingFailureBranch;
    const pass_marker = std.mem.indexOf(u8, validator,
        \\    print("PHASE1_CLOSURE_VALIDATION=pass")
    ) orelse return error.MissingPassMarker;
    const mode_marker = std.mem.indexOf(u8, validator,
        \\    print("PHASE1_CLOSURE_MODE=current-master-safe")
    ) orelse return error.MissingModeMarker;
    const failure_branch = validator[failure_branch_start..pass_marker];

    try expectContainsOnce(validator,
        \\    print("PHASE1_CLOSURE_VALIDATION=pass")
    );
    try expectContainsOnce(validator,
        \\    print("PHASE1_CLOSURE_MODE=current-master-safe")
    );
    try std.testing.expect(mode_marker > pass_marker);
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, failure_branch, "PHASE1_CLOSURE_VALIDATION=pass"));
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, failure_branch, "PHASE1_CLOSURE_MODE=current-master-safe"));
}

test "phase1 closure validator dispatches self-test before fail-closed validation" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContainsOnce(validator,
        \\    if args.self_test:
    );
    try expectContainsOnce(validator,
        \\        return run_self_test()
    );
    try expectOrdered(validator,
        \\    if args.self_test:
    ,
        \\    failures = collect_failures(repo_root(args.root))
    );
}
