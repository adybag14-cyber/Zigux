const std = @import("std");

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const non_elf_ident = [_]u8{
    0x00, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";

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
        "mk-elfconfig-executable-truncation-boundaries-contract",
        "Verify mk_elfconfig executable truncates every stdin payload shorter than one ELF ident",
    );

    addTruncatedCase(b, contract, mk_elfconfig, "truncated-empty-stdin", "");
    addTruncatedCase(b, contract, mk_elfconfig, "truncated-one-magic-byte", elf32_ident[0..1]);
    addTruncatedCase(b, contract, mk_elfconfig, "truncated-short-magic-prefix", elf32_ident[0..3]);
    addTruncatedCase(b, contract, mk_elfconfig, "truncated-complete-magic-only", elf32_ident[0..4]);
    addTruncatedCase(b, contract, mk_elfconfig, "truncated-with-class-byte", elf64_ident[0..5]);
    addTruncatedCase(b, contract, mk_elfconfig, "truncated-non-elf-short-prefix", non_elf_ident[0..15]);
    addExactSuccessCase(b, contract, mk_elfconfig, "exact-elf32-boundary-success", &elf32_ident, elf32_define);
    addExactSuccessCase(b, contract, mk_elfconfig, "exact-elf64-boundary-success", &elf64_ident, elf64_define);

    const test_step = b.step("test", "Run mk_elfconfig executable truncation boundary contract");
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

fn addExactSuccessCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    stdin_bytes: []const u8,
    stdout_bytes: []const u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = stdout_bytes });
    run.addCheck(.{ .expect_stderr_exact = "" });
    run.expectExitCode(0);
    contract.dependOn(&run.step);
}

test "truncation boundary fixture byte lengths stay intentional" {
    try std.testing.expectEqual(@as(usize, 16), elf32_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 16), non_elf_ident.len);
    try std.testing.expectEqual(@as(usize, 0), "".len);
    try std.testing.expectEqual(@as(usize, 1), elf32_ident[0..1].len);
    try std.testing.expectEqual(@as(usize, 3), elf32_ident[0..3].len);
    try std.testing.expectEqual(@as(usize, 4), elf32_ident[0..4].len);
    try std.testing.expectEqual(@as(usize, 5), elf64_ident[0..5].len);
    try std.testing.expectEqual(@as(usize, 15), non_elf_ident[0..15].len);
}
