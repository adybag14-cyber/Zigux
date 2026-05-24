const std = @import("std");
const genksyms = @import("genksyms");

const minimal_expected_json = @embedFile("fixtures/genksyms_bridge/minimal_expected.json");
const debug_reference_types_expected_json = @embedFile("fixtures/genksyms_bridge/debug_reference_types_expected.json");
const long_options_expected_json = @embedFile("fixtures/genksyms_bridge/long_options_expected.json");
const abbreviated_long_options_expected_json = @embedFile("fixtures/genksyms_bridge/abbreviated_long_options_expected.json");
const quiet_overrides_warning_expected_json = @embedFile("fixtures/genksyms_bridge/quiet_overrides_warning_expected.json");

fn expectRenderedBridgeMatchesFixture(actual_json: []const u8, fixture_json: []const u8) !void {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const actual_value = try std.json.parseFromSlice(std.json.Value, arena, actual_json, .{});
    const expected_value = try std.json.parseFromSlice(std.json.Value, arena, fixture_json, .{});

    var actual_output: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer actual_output.deinit();
    try std.json.Stringify.value(actual_value.value, .{}, &actual_output.writer);

    var expected_output: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer expected_output.deinit();
    try std.json.Stringify.value(expected_value.value, .{}, &expected_output.writer);

    try std.testing.expectEqualStrings(expected_output.written(), actual_output.written());
}

fn expectRequestFixture(args: []const []const u8, fixture_json: []const u8) !void {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const outcome = try genksyms.parseArgs(arena, args);

    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try expectRenderedBridgeMatchesFixture(output.written(), fixture_json);
}

test "phase2 genksyms wrapper request fixture replay matches minimal fixture" {
    try expectRequestFixture(&.{}, minimal_expected_json);
}

test "phase2 genksyms wrapper request fixture replay matches debug reference types fixture" {
    const args = [_][]const u8{
        "-d",
        "-r",
        "ref.symvers",
        "-T",
        "types.symtypes",
    };
    try expectRequestFixture(&args, debug_reference_types_expected_json);
}

test "phase2 genksyms wrapper request fixture replay matches long options fixture" {
    const args = [_][]const u8{
        "--debug",
        "--dump",
        "--reference=foo.symref",
        "--dump-types",
        "types.symtypes",
        "--preserve",
    };
    try expectRequestFixture(&args, long_options_expected_json);
}

test "phase2 genksyms wrapper request fixture replay matches abbreviated long options fixture" {
    const args = [_][]const u8{
        "--deb",
        "--warn",
        "--qui",
        "--ref=foo.symref",
        "--dump-t",
        "types.symtypes",
        "--pres",
    };
    try expectRequestFixture(&args, abbreviated_long_options_expected_json);
}

test "phase2 genksyms wrapper request fixture replay matches quiet override fixture" {
    const args = [_][]const u8{
        "--warnings",
        "--quiet",
        "--reference",
        "bar.symref",
    };
    try expectRequestFixture(&args, quiet_overrides_warning_expected_json);
}
