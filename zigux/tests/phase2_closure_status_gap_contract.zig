const std = @import("std");

const FileSet = struct {
    closure: []const u8,
    validator: []const u8,
    manifest: []const u8,
    makefile: []const u8,
    workflow: []const u8,

    fn load(allocator: std.mem.Allocator) !FileSet {
        return .{
            .closure = try readFile(allocator, "Documentation/zigux/phase2-closure.md"),
            .validator = try readFile(allocator, "scripts/zigux/validate-phase2-closure.py"),
            .manifest = try readFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json"),
            .makefile = try readFile(allocator, "zigux/Makefile"),
            .workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml"),
        };
    }

    fn deinit(self: FileSet, allocator: std.mem.Allocator) void {
        allocator.free(self.closure);
        allocator.free(self.validator);
        allocator.free(self.manifest);
        allocator.free(self.makefile);
        allocator.free(self.workflow);
    }
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "Phase 2 closure keeps parked status and validator authority explicit" {
    const allocator = std.testing.allocator;
    const files = try FileSet.load(allocator);
    defer files.deinit(allocator);

    try requireContains(files.closure, "`PHASE2_STATUS=parked`");
    try requireContains(files.closure, "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try requireContains(files.closure, "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`");
    try requireContains(files.closure, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try requireContains(files.closure, "`PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`");

    try requireContains(files.validator, "VALIDATOR_COMMANDS = (");
    try requireContains(files.validator, "\"python3 scripts/zigux/validate-phase2.py\"");
    try requireContains(files.validator, "\"python3 scripts/zigux/validate-phase2-closure.py\"");
    try requireContains(files.validator, "PHASE2_CLOSURE_VALIDATION=pass");
    try requireContains(files.validator, "PHASE2_CLOSURE_STATUS=parked");
    try requireContains(files.validator, "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure");
    try requireContains(files.validator, "PHASE2_CLOSURE_REMAINING_GAPS=");
}

test "Phase 2 closure keeps repo-reality gap split narrow and manifest gaps closed" {
    const allocator = std.testing.allocator;
    const files = try FileSet.load(allocator);
    defer files.deinit(allocator);

    try requireContains(files.closure, "`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`");
    try requireContains(files.closure, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
    try requireContains(files.closure, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try requireContains(files.closure, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try requireContains(files.closure, "helper-local explicit-override roster remains broader by design");
    try requireContains(files.closure, "add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again");

    try requireContains(files.manifest, "\"repo_reality_gaps\": []");
    try std.testing.expect(std.mem.indexOf(u8, files.manifest, "scripts/kconfig/conf.c") == null);
    try std.testing.expect(std.mem.indexOf(u8, files.manifest, "scripts/kconfig/confdata.c") == null);
}

test "Phase 2 closure status is wired through make and workflow after Phase 2 routes" {
    const allocator = std.testing.allocator;
    const files = try FileSet.load(allocator);
    defer files.deinit(allocator);

    try requireContains(files.makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try requireContains(files.makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try requireContains(files.makefile, "phase2: phase2-validate");
    try requireExactCount(files.makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py", 1);

    try requireBefore(files.workflow, "Run current Phase 2 aggregate make route", "Validate current Phase 2 tool packet");
    try requireBefore(files.workflow, "Validate current Phase 2 tool packet", "Self-test current Phase 2 closure validator");
    try requireBefore(files.workflow, "Self-test current Phase 2 closure validator", "Check current Phase 2 closure packet");
    try requireContains(files.workflow, "run: make -C zigux phase2");
    try requireContains(files.workflow, "run: python3 scripts/zigux/validate-phase2.py");
    try requireContains(files.workflow, "run: python3 scripts/zigux/validate-phase2-closure.py --self-test");
    try requireContains(files.workflow, "run: python3 scripts/zigux/validate-phase2-closure.py");
}
