const std = @import("std");

const short_empty = [_]u8{};
const short_magic_1 = [_]u8{0x7f};
const short_magic_2 = [_]u8{ 0x7f, 'E' };
const short_magic_3 = [_]u8{ 0x7f, 'E', 'L' };
const short_full_magic_with_class = [_]u8{ 0x7f, 'E', 'L', 'F', 1 };
const exact_elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};

const truncated_text = "Error: input truncated\n";
const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const mk_elfconfig = b.addExecutable(.{
        .name = "mk_elfconfig",
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const contract = b.step(
        "mk-elfconfig-executable-short-magic-contract",
        "Verify mk_elfconfig executable treats short ELF magic prefixes as truncated input",
    );

    addTruncatedCase(b, contract, mk_elfconfig, "empty-stdin", &short_empty);
    addTruncatedCase(b, contract, mk_elfconfig, "short-magic-byte-1", &short_magic_1);
    addTruncatedCase(b, contract, mk_elfconfig, "short-magic-byte-2", &short_magic_2);
    addTruncatedCase(b, contract, mk_elfconfig, "short-magic-byte-3", &short_magic_3);
    addTruncatedCase(b, contract, mk_elfconfig, "full-magic-with-class-only", &short_full_magic_with_class);
    addSuccessCase(b, contract, mk_elfconfig, "exact-elf32-positive-control", &exact_elf32_ident);

    const test_step = b.step("test", "Run mk_elfconfig executable short magic contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

fn addTruncatedCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    stdin_bytes: []const u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = "" });
    run.addCheck(.{ .expect_stderr_exact = truncated_text });
    run.expectExitCode(1);
    contract.dependOn(&run.step);
}

fn addSuccessCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    stdin_bytes: []const u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = elf32_define });
    run.addCheck(.{ .expect_stderr_exact = "" });
    run.expectExitCode(0);
    contract.dependOn(&run.step);
}

test "short magic fixtures cover every executable truncation prefix" {
    try std.testing.expectEqual(@as(usize, 0), short_empty.len);
    try std.testing.expectEqual(@as(usize, 1), short_magic_1.len);
    try std.testing.expectEqual(@as(usize, 2), short_magic_2.len);
    try std.testing.expectEqual(@as(usize, 3), short_magic_3.len);
    try std.testing.expectEqual(@as(usize, 5), short_full_magic_with_class.len);
    try std.testing.expectEqual(@as(usize, 16), exact_elf32_ident.len);
}
