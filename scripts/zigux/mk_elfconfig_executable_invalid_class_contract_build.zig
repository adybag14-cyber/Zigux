const std = @import("std");

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_zero_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 0, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_three_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_255_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 255, 1, 1, 0,
    0,    0,   0,   0,   0,   0, 0, 0,
};
const non_elf_ident = [_]u8{
    0x00, 'E', 'L', 'F', 3, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
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
        "mk-elfconfig-executable-invalid-class-contract",
        "Verify mk_elfconfig executable invalid ELF class handling stays silent",
    );

    addCase(b, contract, mk_elfconfig, "invalid-class-zero", &invalid_class_zero_ident, "", "", 1);
    addCase(b, contract, mk_elfconfig, "invalid-class-three", &invalid_class_three_ident, "", "", 1);
    addCase(b, contract, mk_elfconfig, "invalid-class-255", &invalid_class_255_ident, "", "", 1);
    addCase(b, contract, mk_elfconfig, "elf32-success-control", &elf32_ident, elf32_define, "", 0);
    addCase(b, contract, mk_elfconfig, "elf64-success-control", &elf64_ident, elf64_define, "", 0);
    addCase(b, contract, mk_elfconfig, "non-elf-error-control", &non_elf_ident, "", not_elf_text, 1);

    const test_step = b.step("test", "Run mk_elfconfig executable invalid class contract");
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

test "invalid class contract fixtures stay exact headers" {
    try std.testing.expectEqual(@as(usize, 16), invalid_class_zero_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_three_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_255_ident.len);
    try std.testing.expectEqual(@as(u8, 0), invalid_class_zero_ident[4]);
    try std.testing.expectEqual(@as(u8, 3), invalid_class_three_ident[4]);
    try std.testing.expectEqual(@as(u8, 255), invalid_class_255_ident[4]);
    try std.testing.expectEqual(@as(usize, 16), elf32_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 16), non_elf_ident.len);
    try std.testing.expectEqual(@as(u8, 1), elf32_ident[4]);
    try std.testing.expectEqual(@as(u8, 2), elf64_ident[4]);
    try std.testing.expectEqual(@as(u8, 0x00), non_elf_ident[0]);
}
