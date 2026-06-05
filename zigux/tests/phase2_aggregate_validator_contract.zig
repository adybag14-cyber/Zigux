const std = @import("std");
const testing = std.testing;

const max_file_size = 1 << 22;

fn readRepoFile(allocator: std.mem.Allocator, rel_path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), rel_path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var start: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[start..], needle);
        try testing.expect(relative != null);
        start += relative.? + needle.len;
    }
}

test "aggregate phase2 validator keeps public pass fail and self-test surface explicit" {
    const allocator = testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2.py");
    defer allocator.free(validator);

    try expectContains(validator, "argparse.ArgumentParser(description=\"Validate the current Phase 2 toolchain, kbuild, kconfig, genksyms, and fixdep packet.\")");
    try expectContains(validator, "parser.add_argument(\"--root\", type=Path, default=ROOT, help=\"Repository root to inspect\")");
    try expectContains(validator, "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run built-in contract checks\")");
    try expectContains(validator, "print(\"PHASE2_VALIDATION_SELF_TEST=pass\")");
    try expectContains(validator, "print(\"PHASE2_VALIDATION=pass\")");
    try expectContains(validator, "print(\"PHASE2_VALIDATION=fail\")");
    try expectContains(validator, "PHASE2_VALIDATION_WORKFLOW_LINE_COUNT");
    try expectContains(validator, "PHASE2_VALIDATION_REQUIRED_PATH_COUNT");
    try expectContains(validator, "MISSING_WORKFLOW_LINE");
    try expectContains(validator, "DUPLICATE_WORKFLOW_LINE");
    try expectContains(validator, "MISSING_MAKEFILE_LINE");
    try expectContains(validator, "DUPLICATE_MAKEFILE_LINE");
    try expectContains(validator, "MISSING_REQUIRED_PATH");
    try expectContains(validator, "MISSING_KCONFIG_CONFDATA_REPLAY_MARKER");
    try expectContains(validator, "DUPLICATE_KCONFIG_CONFDATA_REPLAY_MARKER");
    try expectContains(validator, "MISSING_REQUIRED_ARCHIVE_SUPPORT");
    try expectContains(validator, "invalid upgrade_policy");
    try expectContains(validator, "duplicate required_make_routes entry");
}

test "aggregate validator derives route checks from the policy and guards archive fallback" {
    const allocator = testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2.py");
    defer allocator.free(validator);
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectOrdered(validator, &.{
        "DEFAULT_REQUIRED_MAKE_ROUTES = (",
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
        "PHASE2_AGGREGATE_ROUTE = \"phase2\"",
    });
    try expectContains(validator, "def load_required_make_routes(root: Path) -> tuple[str, ...]:");
    try expectContains(validator, "def expected_workflow_route_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(validator, "def expected_makefile_dynamic_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(validator, "def required_phase2_phony_line(required_make_routes: tuple[str, ...]) -> str:");
    try expectContains(validator, "def collect_archive_support_issues(root: Path) -> list[tuple[str, str]]:");
    try expectContains(validator, "canonical `adybag14-cyber/zig` release");
    try expectContains(validator, "ARCHIVE_SUPPORT_ALTERNATIVES");
    try expectContains(validator, "ARCHIVE_README_PATH");

    try expectContains(workflow, "run: python3 scripts/zigux/validate-phase2.py");
    try expectContains(workflow, "run: make -C zigux phase2-validate");
    try expectContains(workflow, "run: make -C zigux phase2");

    try expectContains(makefile, "phase2-validate:");
    try expectContains(makefile, "phase2: phase2-validate");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py");
}

test "closure note and manifest keep aggregate validator pair and make wrappers visible" {
    const allocator = testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);
    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2.py");
    defer allocator.free(validator);

    try expectContains(closure, "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`");
    try expectContains(closure, "`PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`");
    try expectContains(closure, "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`");

    try expectContains(manifest, "\"validators\": [");
    try expectOrdered(manifest, &.{
        "\"scripts/zigux/validate-phase2.py\"",
        "\"scripts/zigux/validate-phase2-closure.py\"",
    });
    try expectOrdered(manifest, &.{
        "\"make_wrappers\": [",
        "\"make -C zigux phase2-toolchain\"",
        "\"make -C zigux phase2-tools\"",
        "\"make -C zigux phase2-kconfig\"",
        "\"make -C zigux phase2-cross\"",
        "\"make -C zigux phase2-genksyms\"",
        "\"make -C zigux phase2-fixdep\"",
        "\"make -C zigux phase2-validate\"",
        "\"make -C zigux phase2\"",
    });
    try expectContains(manifest, "\"repo_reality_gaps\": []");

    try expectContains(validator, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_tool_manifest.json\"");
    try expectContains(validator, "MAKEFILE = \"zigux/Makefile\"");
    try expectContains(validator, "WORKFLOW = \".github/workflows/zigux-bootstrap.yml\"");
}

test "aggregate validator still owns broad phase2 helper and fixture roster" {
    const allocator = testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2.py");
    defer allocator.free(validator);

    try expectContains(validator, "\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(validator, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(validator, "\"scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig\"");
    try expectContains(validator, "\"scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig\"");
    try expectContains(validator, "\"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments_expected.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/fixdep/cases.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt\"");
    try expectNotContains(validator, "check-phase2-tool-manifest-packets.py");
}
