const std = @import("std");

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0,
    0,    0,   0,   0,   0,    0, 0, 0,
};
const not_elf_ident = [_]u8{
    'a', 'r', 'g', 'v', 2, 1, 1, 0,
    0,   0,   0,   0,   0, 0, 0, 0,
};
const truncated_ident = "\x7fELF\x02\x01";

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";
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
        "mk-elfconfig-executable-argv-ignored-contract",
        "Verify mk_elfconfig executable ignores argv and reads stdin only",
    );

    addCase(
        b,
        contract,
        mk_elfconfig,
        "argv-ignored-elf32",
        &.{ "--class=ELFCLASS64", "not-elf", "ignored-output" },
        &elf32_ident,
        elf32_define,
        "",
        0,
    );
    addCase(
        b,
        contract,
        mk_elfconfig,
        "argv-ignored-elf64",
        &.{ "--class=ELFCLASS32", "truncated", "stderr=ignored" },
        &elf64_ident,
        elf64_define,
        "",
        0,
    );
    addCase(
        b,
        contract,
        mk_elfconfig,
        "argv-ignored-invalid-class",
        &.{ "--emit-stdout", "ELFCLASS64" },
        &invalid_class_ident,
        "",
        "",
        1,
    );
    addCase(
        b,
        contract,
        mk_elfconfig,
        "argv-ignored-not-elf",
        &.{ "\x7fELF", "ELFCLASS64" },
        &not_elf_ident,
        "",
        not_elf_text,
        1,
    );
    addCase(
        b,
        contract,
        mk_elfconfig,
        "argv-ignored-truncated",
        &.{ "--pretend-complete", "ELFCLASS32" },
        truncated_ident,
        "",
        truncated_text,
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable argv-ignored contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

fn addCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    argv: []const []const u8,
    stdin_bytes: []const u8,
    stdout_bytes: []const u8,
    stderr_bytes: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.addArgs(argv);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = stdout_bytes });
    run.addCheck(.{ .expect_stderr_exact = stderr_bytes });
    run.expectExitCode(exit_code);
    contract.dependOn(&run.step);
}

test "argv ignored fixtures keep stdin authority intentional" {
    try std.testing.expectEqual(@as(usize, 16), elf32_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_ident.len);
    try std.testing.expectEqual(@as(usize, 16), not_elf_ident.len);
    try std.testing.expectEqual(@as(usize, 6), truncated_ident.len);
    try std.testing.expectEqual(@as(u8, 1), elf32_ident[4]);
    try std.testing.expectEqual(@as(u8, 2), elf64_ident[4]);
    try std.testing.expectEqual(@as(u8, 0xff), invalid_class_ident[4]);
    try std.testing.expectEqualStrings(not_elf_text, "Error: not ELF\n");
    try std.testing.expectEqualStrings(truncated_text, "Error: input truncated\n");
}
