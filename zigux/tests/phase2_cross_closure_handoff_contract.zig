const std = @import("std");

const CrossTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
    route: []const u8,
};

const CrossFixture = struct {
    phase: []const u8,
    status: []const u8,
    route: []const u8,
    archive_target_scope: []const []const u8,
    cross_targets: []const CrossTarget,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countContains(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

test "phase 2 cross fixture keeps the current closure handoff target split" {
    const fixture_json = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 8 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(CrossFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings("make -C zigux phase2-cross", fixture.route);
    try std.testing.expectEqual(@as(usize, 1), fixture.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", fixture.archive_target_scope[0]);
    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);

    try std.testing.expectEqualStrings("x86_64-linux", fixture.cross_targets[0].target);
    try std.testing.expectEqualStrings("pinned bootstrap archive", fixture.cross_targets[0].review_status);
    try std.testing.expectEqualStrings("archive_required", fixture.cross_targets[0].validation_mode);
    try std.testing.expectEqualStrings("make -C zigux phase2-cross", fixture.cross_targets[0].route);

    try std.testing.expectEqualStrings("aarch64-linux", fixture.cross_targets[1].target);
    try std.testing.expectEqualStrings("route contract only", fixture.cross_targets[1].review_status);
    try std.testing.expectEqualStrings("route_contract_only", fixture.cross_targets[1].validation_mode);
    try std.testing.expectEqualStrings("make -C zigux phase2-cross", fixture.cross_targets[1].route);

    try expectNotContains(fixture_json, "riscv64-linux");
}

test "phase 2 closure note keeps cross matrix in shared tooling and route packets" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 64 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "`scripts/zigux/check-phase2-cross.py`");
    try expectContains(closure_note, "`zigux/tests/fixtures/phase2_cross_targets.json`");
    try expectContains(closure_note, "python3 scripts/zigux/check-phase2-cross.py");
    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(closure_note, "make -C zigux phase2-cross");
    try expectNotContains(closure_note, "cross-route repo-reality gap");
    try expectNotContains(closure_note, "riscv64-linux");
}

test "bootstrap note treats the direct cross packet as current evidence" {
    const bootstrap_note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 96 * 1024);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(bootstrap_note, "`scripts/zigux/check-phase2-cross.py`");
    try expectContains(bootstrap_note, "`scripts/zigux/check-phase2-cross-selftest-alignment.py`");
    try expectContains(bootstrap_note, "`zigux/tests/fixtures/phase2_cross_targets.json`");
    try expectContains(bootstrap_note, "pinned `x86_64-linux` `archive_required` lane");
    try expectContains(bootstrap_note, "`aarch64-linux` `route_contract_only` lane");
    try expectContains(bootstrap_note, "returned cross packet as present evidence instead of a repo-reality gap");
    try expectContains(bootstrap_note, "No current repo-reality gaps remain inside the bounded toolchain");
    try expectNotContains(bootstrap_note, "riscv64-linux");
}

test "aggregate phase 2 validator still requires the direct cross handoff files" {
    const validator = try readRepoFile("scripts/zigux/validate-phase2.py", 128 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "\"scripts/zigux/check-phase2-cross.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\"");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_cross_targets.json\"");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-cross.py --self-test\"");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-cross.py\"");
    try expectContains(validator, "\"run: make -C zigux {route}\"");
    try std.testing.expectEqual(@as(usize, 1), countContains(validator, "\"zigux/tests/fixtures/phase2_cross_targets.json\""));
}
