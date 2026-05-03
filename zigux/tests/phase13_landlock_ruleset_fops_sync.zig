const std = @import("std");
const syscalls = @import("landlock_syscalls");

test "phase13 landlock ruleset fd creation plan stays synchronized with explicit ruleset fops" {
    const creation = try syscalls.SyscallsHelperLab.planCreateRulesetFd(.{});
    const release = syscalls.SyscallsHelperLab.planRulesetFops(.release);
    const read = syscalls.SyscallsHelperLab.planRulesetFops(.read);
    const write = syscalls.SyscallsHelperLab.planRulesetFops(.write);

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", creation.anchor);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", release.anchor);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", read.anchor);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", write.anchor);

    try std.testing.expect(creation.installs_release_handler);
    try std.testing.expect(creation.release_handler_puts_ruleset);
    try std.testing.expect(creation.installs_dummy_read_handler);
    try std.testing.expect(creation.installs_dummy_write_handler);

    try std.testing.expectEqual(@as(u32, 0), release.enables_mode);
    try std.testing.expect(release.drops_ruleset_reference);
    try std.testing.expect(release.returns_zero);
    try std.testing.expect(!release.returns_einval);

    try std.testing.expectEqual(syscalls.fmode_can_read, read.enables_mode);
    try std.testing.expect(!read.drops_ruleset_reference);
    try std.testing.expect(!read.returns_zero);
    try std.testing.expect(read.returns_einval);

    try std.testing.expectEqual(syscalls.fmode_can_write, write.enables_mode);
    try std.testing.expect(!write.drops_ruleset_reference);
    try std.testing.expect(!write.returns_zero);
    try std.testing.expect(write.returns_einval);

    try std.testing.expectEqual(creation.installs_release_handler, release.drops_ruleset_reference);
    try std.testing.expectEqual(creation.release_handler_puts_ruleset, release.drops_ruleset_reference);
    try std.testing.expectEqual(creation.installs_dummy_read_handler, read.enables_mode == syscalls.fmode_can_read and read.returns_einval);
    try std.testing.expectEqual(creation.installs_dummy_write_handler, write.enables_mode == syscalls.fmode_can_write and write.returns_einval);
}

test "phase13 landlock ruleset fops sync guard stays wired into the shared phase13 build" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase13_landlock_ruleset_fops_sync.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase13-landlock-ruleset-fops-sync-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase13_landlock_ruleset_fops_sync_module.addImport(\"landlock_syscalls\", landlock_syscalls_module);") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "test_step.dependOn(&run_phase13_landlock_ruleset_fops_sync_tests.step);") != null);
}
