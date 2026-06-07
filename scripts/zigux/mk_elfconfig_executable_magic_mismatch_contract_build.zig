const std = @import("std");

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const magic0_mismatch = [_]u8{
    0x00, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const magic1_mismatch = [_]u8{
    0x7f, 'X', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const magic2_mismatch = [_]u8{
    0x7f, 'E', 'X', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const magic3_mismatch = [_]u8{
    0x7f, 'E', 'L', 'X', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const magic0_mismatch_then_elf64 = magic0_mismatch ++ elf64_ident;

const not_elf_text = "Error: not ELF\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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
        "mk-elfconfig-executable-magic-mismatch-contract",
        "Verify mk_elfconfig executable rejects every full-length ELF magic-byte mismatch",
    );

    addNotElfCase(b, contract, mk_elfconfig, "mismatch-byte-0", &magic0_mismatch);
    addNotElfCase(b, contract, mk_elfconfig, "mismatch-byte-1", &magic1_mismatch);
    addNotElfCase(b, contract, mk_elfconfig, "mismatch-byte-2", &magic2_mismatch);
    addNotElfCase(b, contract, mk_elfconfig, "mismatch-byte-3", &magic3_mismatch);
    addNotElfCase(b, contract, mk_elfconfig, "mismatch-before-later-elf", &magic0_mismatch_then_elf64);
    addSuccessCase(b, contract, mk_elfconfig, "exact-elf64-positive-control", &elf64_ident);

    const test_step = b.step("test", "Run mk_elfconfig executable magic mismatch contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

fn addNotElfCase(
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
    run.addCheck(.{ .expect_stderr_exact = not_elf_text });
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
    run.addCheck(.{ .expect_stdout_exact = elf64_define });
    run.addCheck(.{ .expect_stderr_exact = "" });
    run.expectExitCode(0);
    contract.dependOn(&run.step);
}

test "magic mismatch fixtures keep the first full ident boundary" {
    try std.testing.expectEqual(@as(usize, 16), elf32_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 16), magic0_mismatch.len);
    try std.testing.expectEqual(@as(usize, 16), magic1_mismatch.len);
    try std.testing.expectEqual(@as(usize, 16), magic2_mismatch.len);
    try std.testing.expectEqual(@as(usize, 16), magic3_mismatch.len);
    try std.testing.expectEqual(@as(usize, 32), magic0_mismatch_then_elf64.len);
}
