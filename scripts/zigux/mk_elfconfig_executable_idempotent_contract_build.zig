const std = @import("std");

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const truncated_prefix = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 };
const not_elf_ident = [_]u8{
    0x00, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf32_with_hidden_failure_tail = elf32_ident ++ not_elf_ident ++ truncated_prefix;
const not_elf_with_hidden_success_tail = not_elf_ident ++ elf64_ident;

const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";
const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
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
        "mk-elfconfig-executable-idempotent-contract",
        "Verify repeated mk_elfconfig executable runs keep stdin, stdout, and stderr isolated",
    );

    addRunCase(b, contract, mk_elfconfig, "first-elf32", &elf32_ident, elf32_define, "", 0);
    addRunCase(b, contract, mk_elfconfig, "repeat-elf32", &elf32_ident, elf32_define, "", 0);
    addRunCase(b, contract, mk_elfconfig, "first-elf64", &elf64_ident, elf64_define, "", 0);
    addRunCase(b, contract, mk_elfconfig, "repeat-elf64", &elf64_ident, elf64_define, "", 0);
    addRunCase(b, contract, mk_elfconfig, "first-truncated", &truncated_prefix, "", truncated_text, 1);
    addRunCase(b, contract, mk_elfconfig, "repeat-truncated", &truncated_prefix, "", truncated_text, 1);
    addRunCase(b, contract, mk_elfconfig, "first-not-elf", &not_elf_ident, "", not_elf_text, 1);
    addRunCase(b, contract, mk_elfconfig, "repeat-not-elf", &not_elf_ident, "", not_elf_text, 1);
    addRunCase(b, contract, mk_elfconfig, "first-invalid-class", &invalid_class_ident, "", "", 1);
    addRunCase(b, contract, mk_elfconfig, "repeat-invalid-class", &invalid_class_ident, "", "", 1);
    addRunCase(b, contract, mk_elfconfig, "success-after-failures", &elf64_ident, elf64_define, "", 0);
    addRunCase(b, contract, mk_elfconfig, "failure-after-success", &not_elf_ident, "", not_elf_text, 1);
    addRunCase(b, contract, mk_elfconfig, "first-ident-authority-success", &elf32_with_hidden_failure_tail, elf32_define, "", 0);
    addRunCase(b, contract, mk_elfconfig, "first-ident-authority-failure", &not_elf_with_hidden_success_tail, "", not_elf_text, 1);

    const test_step = b.step("test", "Run mk_elfconfig executable idempotence contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

fn addRunCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    stdin_bytes: []const u8,
    stdout_text: []const u8,
    stderr_text: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = stdout_text });
    run.addCheck(.{ .expect_stderr_exact = stderr_text });
    run.expectExitCode(exit_code);
    contract.dependOn(&run.step);
}

test "idempotence fixtures keep fixed ident boundaries" {
    try std.testing.expectEqual(@as(usize, 16), elf32_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 8), truncated_prefix.len);
    try std.testing.expectEqual(@as(usize, 16), not_elf_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_ident.len);
    try std.testing.expectEqual(@as(usize, 40), elf32_with_hidden_failure_tail.len);
    try std.testing.expectEqual(@as(usize, 32), not_elf_with_hidden_success_tail.len);
}
