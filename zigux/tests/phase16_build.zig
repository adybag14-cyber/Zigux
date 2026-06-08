const std = @import("std");

const Helper = struct {
    name: []const u8,
    path: []const u8,
};

const helpers = [_]Helper{
    .{ .name = "ctype", .path = "../../lib/ctype.zig" },
    .{ .name = "hweight", .path = "../../lib/hweight.zig" },
    .{ .name = "find-bit", .path = "../../lib/find_bit.zig" },
    .{ .name = "list-sort", .path = "../../lib/list_sort.zig" },
    .{ .name = "bcd", .path = "../../lib/bcd.zig" },
    .{ .name = "bitrev", .path = "../../lib/bitrev.zig" },
    .{ .name = "clz-ctz", .path = "../../lib/clz_ctz.zig" },
    .{ .name = "ashldi3", .path = "../../lib/ashldi3.zig" },
    .{ .name = "ashrdi3", .path = "../../lib/ashrdi3.zig" },
    .{ .name = "lshrdi3", .path = "../../lib/lshrdi3.zig" },
    .{ .name = "cmpdi2", .path = "../../lib/cmpdi2.zig" },
    .{ .name = "ucmpdi2", .path = "../../lib/ucmpdi2.zig" },
    .{ .name = "muldi3", .path = "../../lib/muldi3.zig" },
    .{ .name = "memcat-p", .path = "../../lib/memcat_p.zig" },
    .{ .name = "linear-ranges", .path = "../../lib/linear_ranges.zig" },
    .{ .name = "glob", .path = "../../lib/glob.zig" },
    .{ .name = "errname", .path = "../../lib/errname.zig" },
    .{ .name = "uuid", .path = "../../lib/uuid.zig" },
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_step = b.step("test", "Run Phase 16 promoted lib helper tests");

    inline for (helpers) |helper| {
        const module = b.createModule(.{
            .root_source_file = b.path(helper.path),
            .target = target,
            .optimize = optimize,
        });
        const tests = b.addTest(.{
            .name = b.fmt("phase16-{s}-tests", .{helper.name}),
            .root_module = module,
        });
        const run_tests = b.addRunArtifact(tests);
        test_step.dependOn(&run_tests.step);
    }
}
