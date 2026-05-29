const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms wrapper preserves version before ordered references and dump override" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "-r",
        "first.symref",
        "--reference=second.symref",
        "-T",
        "discarded.types",
        "--dump-types=final.types",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("first.symref", request.reference_files[0]);
    try testing.expectEqualStrings("second.symref", request.reference_files[1]);
    try testing.expectEqualStrings("final.types", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-r\",\"first.symref\",\"--reference=second.symref\",\"-T\",\"discarded.types\",\"--dump-types=final.types\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"first.symref\",\"second.symref\"],\"dump_types_file\":\"final.types\"}}\n",
        output.written(),
    );
}

test "genksyms wrapper preserves short versions before long references and short dump override" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "--reference",
        "alpha.symref",
        "--ref=beta.symref",
        "--dump-types",
        "old.types",
        "-Tnew.types",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("alpha.symref", request.reference_files[0]);
    try testing.expectEqualStrings("beta.symref", request.reference_files[1]);
    try testing.expectEqualStrings("new.types", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VV\",\"--reference\",\"alpha.symref\",\"--ref=beta.symref\",\"--dump-types\",\"old.types\",\"-Tnew.types\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"alpha.symref\",\"beta.symref\"],\"dump_types_file\":\"new.types\"}}\n",
        output.written(),
    );
}
