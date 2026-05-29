const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const shared_validator_path = "scripts/zigux/validate-phase2.py";
const closure_validator_path = "scripts/zigux/validate-phase2-closure.py";

const shared_validator_command = "python3 scripts/zigux/validate-phase2.py";
const closure_validator_command = "python3 scripts/zigux/validate-phase2-closure.py";
const validator_pair_line = "PHASE2_CLOSURE_VALIDATORS=" ++ shared_validator_command ++ "," ++ closure_validator_command;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var remaining = haystack;
    while (std.mem.indexOf(u8, remaining, needle)) |offset| {
        count += 1;
        remaining = remaining[offset + needle.len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "phase2 closure note keeps the validator pair explicit" {
    const allocator = std.testing.allocator;
    const closure_note = try readFile(allocator, closure_note_path);
    defer allocator.free(closure_note);

    try expectContains(closure_note, "`PHASE2_STATUS=parked`");
    try expectContains(closure_note, "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try expectContains(closure_note, "shared validator pair: `" ++ shared_validator_command ++ "` and `" ++ closure_validator_command ++ "`");
    try expectContains(closure_note, "`" ++ validator_pair_line ++ "`");
    try expectExactCount(closure_note, validator_pair_line, 1);
}

test "closure validator script derives the same pair line" {
    const allocator = std.testing.allocator;
    const closure_validator = try readFile(allocator, closure_validator_path);
    defer allocator.free(closure_validator);

    try expectContains(closure_validator, "PHASE2_VALIDATE_REL = Path(\"scripts/zigux/validate-phase2.py\")");
    try expectContains(closure_validator, "PHASE2_CLOSURE_VALIDATE_REL = Path(\"scripts/zigux/validate-phase2-closure.py\")");
    try expectContains(closure_validator, "VALIDATOR_COMMANDS = (");
    try expectContains(closure_validator, "\"" ++ shared_validator_command ++ "\",");
    try expectContains(closure_validator, "\"" ++ closure_validator_command ++ "\",");
    try expectContains(closure_validator, "expected_validator_line = \"PHASE2_CLOSURE_VALIDATORS=\" + \",\".join(VALIDATOR_COMMANDS)");
    try expectContains(closure_validator, "*VALIDATOR_COMMANDS,");
}

test "shared validator requires the closure validator surface" {
    const allocator = std.testing.allocator;
    const shared_validator = try readFile(allocator, shared_validator_path);
    defer allocator.free(shared_validator);

    try expectContains(shared_validator, "\"" ++ closure_note_path ++ "\"");
    try expectContains(shared_validator, "\"" ++ closure_validator_path ++ "\"");
    try expectContains(shared_validator, "\"run: " ++ shared_validator_command ++ "\"");
    try expectContains(shared_validator, "PHASE2_AGGREGATE_ROUTE = \"phase2\"");
}
