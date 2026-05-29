const std = @import("std");

const Validator = struct {
    path: []const u8,
    command: []const u8,
    workflow_step: []const u8,
};

const validators = [_]Validator{
    .{
        .path = "scripts/zigux/validate-phase2.py",
        .command = "python3 scripts/zigux/validate-phase2.py",
        .workflow_step = "Validate current Phase 2 tool packet",
    },
    .{
        .path = "scripts/zigux/validate-phase2-closure.py",
        .command = "python3 scripts/zigux/validate-phase2-closure.py",
        .workflow_step = "Check current Phase 2 closure packet",
    },
};

const validate_make_route = "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep";
const aggregate_make_route = "phase2: phase2-validate";

const validate_makefile_commands = [_][]const u8{
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
};

const workflow_tail = [_][]const u8{
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase2-closure.py",
};

const manifest_validators = [_][]const u8{
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
};

const manifest_make_wrappers = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

fn contains(haystack: []const []const u8, needle: []const u8) bool {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn indexOf(haystack: []const []const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |item, index| {
        if (std.mem.eql(u8, item, needle)) return index;
    }
    return null;
}

test "Phase 2 validate route keeps validator pair explicit" {
    try std.testing.expectEqual(@as(usize, 2), validators.len);
    try std.testing.expectEqualStrings(
        "scripts/zigux/validate-phase2.py",
        validators[0].path,
    );
    try std.testing.expectEqualStrings(
        "scripts/zigux/validate-phase2-closure.py",
        validators[1].path,
    );

    for (validators) |validator| {
        try std.testing.expect(contains(&manifest_validators, validator.path));
    }
}

test "Phase 2 validate make route stays after required tool routes" {
    try std.testing.expect(std.mem.startsWith(u8, validate_make_route, "phase2-validate:"));
    for (manifest_make_wrappers[0..6]) |required_route| {
        const route_name = required_route["make -C zigux ".len..];
        try std.testing.expect(std.mem.indexOf(u8, validate_make_route, route_name) != null);
    }

    try std.testing.expect(std.mem.endsWith(u8, aggregate_make_route, "phase2-validate"));
    try std.testing.expect(contains(&manifest_make_wrappers, "make -C zigux phase2-validate"));
    try std.testing.expect(contains(&manifest_make_wrappers, "make -C zigux phase2"));
}

test "Phase 2 validate make recipe runs manifest and closure checks" {
    try std.testing.expectEqual(@as(usize, 5), validate_makefile_commands.len);
    try std.testing.expect(contains(&validate_makefile_commands, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test"));
    try std.testing.expect(contains(&validate_makefile_commands, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py"));
    try std.testing.expect(contains(&validate_makefile_commands, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test"));
    try std.testing.expect(contains(&validate_makefile_commands, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py"));
    try std.testing.expect(contains(&validate_makefile_commands, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py"));
}

test "Phase 2 workflow runs validate route before direct validator checks" {
    const validate_route = indexOf(&workflow_tail, "run: make -C zigux phase2-validate") orelse return error.MissingValidateRoute;
    const aggregate_route = indexOf(&workflow_tail, "run: make -C zigux phase2") orelse return error.MissingAggregateRoute;
    const packet_validator = indexOf(&workflow_tail, "run: python3 scripts/zigux/validate-phase2.py") orelse return error.MissingPacketValidator;
    const closure_self_test = indexOf(&workflow_tail, "run: python3 scripts/zigux/validate-phase2-closure.py --self-test") orelse return error.MissingClosureSelfTest;
    const closure_validator = indexOf(&workflow_tail, "run: python3 scripts/zigux/validate-phase2-closure.py") orelse return error.MissingClosureValidator;

    try std.testing.expect(validate_route < aggregate_route);
    try std.testing.expect(aggregate_route < packet_validator);
    try std.testing.expect(packet_validator < closure_self_test);
    try std.testing.expect(closure_self_test < closure_validator);
}

test "Phase 2 closure validator command remains paired with manifest surface" {
    for (validators) |validator| {
        try std.testing.expect(std.mem.startsWith(u8, validator.command, "python3 "));
        try std.testing.expect(std.mem.endsWith(u8, validator.command, validator.path));
        try std.testing.expect(validator.workflow_step.len > 0);
    }

    try std.testing.expectEqualStrings(
        "python3 scripts/zigux/validate-phase2.py",
        validators[0].command,
    );
    try std.testing.expectEqualStrings(
        "python3 scripts/zigux/validate-phase2-closure.py",
        validators[1].command,
    );
}
