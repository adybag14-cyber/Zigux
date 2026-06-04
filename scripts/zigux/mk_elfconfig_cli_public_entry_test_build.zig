const std = @import("std");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const helper_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_helper_tests = b.addRunArtifact(helper_tests);

    const cli_contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig_cli_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_cli_contract_tests = b.addRunArtifact(cli_contract_tests);

    const exe = b.addExecutable(.{
        .name = "mk_elfconfig_cli_contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const elf64_with_tail = [_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    };
    const truncated_elf_prefix = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };
    const not_elf = [_]u8{ 'Z', 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const invalid_class = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    const run_elf32 = b.addRunArtifact(exe);
    run_elf32.setStdIn(.{ .bytes = &elf32 });
    run_elf32.expectStdOutEqual(elf32_define);
    run_elf32.expectStdErrEqual("");
    run_elf32.expectExitCode(0);

    const run_elf64_tail = b.addRunArtifact(exe);
    run_elf64_tail.setStdIn(.{ .bytes = &elf64_with_tail });
    run_elf64_tail.expectStdOutEqual(elf64_define);
    run_elf64_tail.expectStdErrEqual("");
    run_elf64_tail.expectExitCode(0);

    const run_truncated = b.addRunArtifact(exe);
    run_truncated.setStdIn(.{ .bytes = &truncated_elf_prefix });
    run_truncated.expectExitCode(1);
    run_truncated.expectStdOutEqual("");
    run_truncated.expectStdErrEqual(truncated_text);

    const run_not_elf = b.addRunArtifact(exe);
    run_not_elf.setStdIn(.{ .bytes = &not_elf });
    run_not_elf.expectExitCode(1);
    run_not_elf.expectStdOutEqual("");
    run_not_elf.expectStdErrEqual(not_elf_text);

    const run_invalid_class = b.addRunArtifact(exe);
    run_invalid_class.setStdIn(.{ .bytes = &invalid_class });
    run_invalid_class.expectExitCode(1);
    run_invalid_class.expectStdOutEqual("");
    run_invalid_class.expectStdErrEqual("");

    const cli_step = b.step("mk-elfconfig-cli-public-entry-test", "Run mk_elfconfig CLI public-entry checks");
    cli_step.dependOn(&run_helper_tests.step);
    cli_step.dependOn(&run_cli_contract_tests.step);
    cli_step.dependOn(&run_elf32.step);
    cli_step.dependOn(&run_elf64_tail.step);
    cli_step.dependOn(&run_truncated.step);
    cli_step.dependOn(&run_not_elf.step);
    cli_step.dependOn(&run_invalid_class.step);

    const test_step = b.step("test", "Run mk_elfconfig CLI public-entry checks");
    test_step.dependOn(cli_step);
}
