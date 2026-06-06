const std = @import("std");

const elf32_noisy_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1,  2,   99,  255,
    17,   34,  51,  68,  85, 102, 119, 136,
};
const elf64_noisy_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2,   255, 42, 7,
    240,  222, 173, 190, 239, 1,   2,  3,
};
const invalid_class_conventional_metadata_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const non_elf_noisy_metadata_ident = [_]u8{
    0x00, 'E', 'L', 'F', 1,  2,   99,  255,
    17,   34,  51,  68,  85, 102, 119, 136,
};

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";

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
        "mk-elfconfig-executable-ident-metadata-contract",
        "Verify mk_elfconfig executable classifies only ELF magic and EI_CLASS from the ident",
    );

    addCase(b, contract, mk_elfconfig, "elf32-noisy-ident-metadata", &elf32_noisy_ident, elf32_define, "", 0);
    addCase(b, contract, mk_elfconfig, "elf64-noisy-ident-metadata", &elf64_noisy_ident, elf64_define, "", 0);
    addCase(b, contract, mk_elfconfig, "invalid-class-control", &invalid_class_conventional_metadata_ident, "", "", 1);
    addCase(b, contract, mk_elfconfig, "non-elf-noisy-metadata-control", &non_elf_noisy_metadata_ident, "", not_elf_text, 1);

    const test_step = b.step("test", "Run mk_elfconfig executable ident metadata contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

fn addCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    stdin_bytes: []const u8,
    stdout_bytes: []const u8,
    stderr_bytes: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = stdout_bytes });
    run.addCheck(.{ .expect_stderr_exact = stderr_bytes });
    run.expectExitCode(exit_code);
    contract.dependOn(&run.step);
}

test "ident metadata contract fixtures keep only byte four authoritative" {
    const elf_magic = [_]u8{ 0x7f, 'E', 'L', 'F' };

    try std.testing.expectEqual(@as(usize, 16), elf32_noisy_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_noisy_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_conventional_metadata_ident.len);
    try std.testing.expectEqual(@as(usize, 16), non_elf_noisy_metadata_ident.len);
    try std.testing.expect(std.mem.eql(u8, elf32_noisy_ident[0..4], &elf_magic));
    try std.testing.expect(std.mem.eql(u8, elf64_noisy_ident[0..4], &elf_magic));
    try std.testing.expect(std.mem.eql(u8, invalid_class_conventional_metadata_ident[0..4], &elf_magic));
    try std.testing.expect(!std.mem.eql(u8, non_elf_noisy_metadata_ident[0..4], &elf_magic));
    try std.testing.expectEqual(@as(u8, 1), elf32_noisy_ident[4]);
    try std.testing.expectEqual(@as(u8, 2), elf64_noisy_ident[4]);
    try std.testing.expectEqual(@as(u8, 3), invalid_class_conventional_metadata_ident[4]);
    try std.testing.expect(!std.mem.eql(u8, elf32_noisy_ident[5..], elf64_noisy_ident[5..]));
}
