const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
    MarkerDuplicated,
};

const Marker = struct {
    text: []const u8,
    label: []const u8,
};

const phase9_markers = [_]Marker{
    .{
        .label = "phase9 review checklist self-test",
        .text = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    },
    .{
        .label = "phase9 build-only packet",
        .text = "python3 scripts/zigux/check-phase9-build-only-surface.py",
    },
    .{
        .label = "phase9 loader shared tests",
        .text = "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    },
    .{
        .label = "phase9 trace events sample",
        .text = "zig test samples/zigux/runtime_trace_events.zig",
    },
    .{
        .label = "phase9 survey witness",
        .text = "zig test zigux/tests/runtime_trace_events_survey.zig",
    },
};

const phase7_markers = [_]Marker{
    .{
        .label = "phase7 shared-control gap self-test",
        .text = "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    },
    .{
        .label = "phase7 shared-control gap packet",
        .text = "python3 scripts/zigux/check-phase7-shared-control-gap.py",
    },
    .{
        .label = "phase7 make-wrapper alignment self-test",
        .text = "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    },
    .{
        .label = "phase7 make-wrapper alignment packet",
        .text = "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    },
};

const phase10_markers = [_]Marker{
    .{
        .label = "phase10 bootstrap route self-test",
        .text = "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
    },
    .{
        .label = "phase10 bootstrap route packet",
        .text = "python3 scripts/zigux/check-phase10-bootstrap-route.py",
    },
    .{
        .label = "phase10 validate route",
        .text = "make -C zigux phase10-validate",
    },
    .{
        .label = "phase10 helper tests",
        .text = "make -C zigux phase10-test",
    },
};

fn markerIndex(haystack: []const u8, marker: Marker) !usize {
    var found: ?usize = null;
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        const command = if (std.mem.startsWith(u8, trimmed, "run: "))
            std.mem.trim(u8, trimmed["run: ".len..], " \t\r")
        else
            trimmed;
        if (std.mem.eql(u8, command, marker.text)) {
            if (found != null) return ContractError.MarkerDuplicated;
            found = offset;
        }
        offset += line.len + 1;
    }
    return found orelse ContractError.MissingMarker;
}

fn requireOrderedMarkers(haystack: []const u8, markers: []const Marker) !void {
    var previous: ?usize = null;
    for (markers) |marker| {
        const current = try markerIndex(haystack, marker);
        if (previous) |prev| {
            if (current <= prev) return ContractError.MarkerOutOfOrder;
        }
        previous = current;
    }
}

pub fn validateWorkflow(haystack: []const u8) !void {
    try requireOrderedMarkers(haystack, &phase9_markers);
    try requireOrderedMarkers(haystack, &phase7_markers);
    try requireOrderedMarkers(haystack, &phase10_markers);

    const phase9_tail = try markerIndex(haystack, phase9_markers[phase9_markers.len - 1]);
    const phase7_head = try markerIndex(haystack, phase7_markers[0]);
    const phase7_tail = try markerIndex(haystack, phase7_markers[phase7_markers.len - 1]);
    const phase10_head = try markerIndex(haystack, phase10_markers[0]);

    if (!(phase9_tail < phase7_head and phase7_tail < phase10_head)) {
        return ContractError.MarkerOutOfOrder;
    }
}

test "live workflow preserves phase9 to phase7 to phase10 handoff" {
    const workflow_text = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(workflow_text);
    try validateWorkflow(workflow_text);
}

test "phase10 cannot run before phase7 alignment checks finish" {
    const bad =
        phase9_markers[0].text ++ "\n" ++
        phase9_markers[1].text ++ "\n" ++
        phase9_markers[2].text ++ "\n" ++
        phase9_markers[3].text ++ "\n" ++
        phase9_markers[4].text ++ "\n" ++
        phase10_markers[0].text ++ "\n" ++
        phase7_markers[0].text ++ "\n" ++
        phase7_markers[1].text ++ "\n" ++
        phase7_markers[2].text ++ "\n" ++
        phase7_markers[3].text ++ "\n" ++
        phase10_markers[1].text ++ "\n" ++
        phase10_markers[2].text ++ "\n" ++
        phase10_markers[3].text ++ "\n";
    try std.testing.expectError(ContractError.MarkerOutOfOrder, validateWorkflow(bad));
}

test "duplicated workflow markers fail closed" {
    const duplicate =
        phase9_markers[0].text ++ "\n" ++
        phase9_markers[1].text ++ "\n" ++
        phase9_markers[1].text ++ "\n" ++
        phase9_markers[2].text ++ "\n" ++
        phase9_markers[3].text ++ "\n" ++
        phase9_markers[4].text ++ "\n" ++
        phase7_markers[0].text ++ "\n" ++
        phase7_markers[1].text ++ "\n" ++
        phase7_markers[2].text ++ "\n" ++
        phase7_markers[3].text ++ "\n" ++
        phase10_markers[0].text ++ "\n" ++
        phase10_markers[1].text ++ "\n" ++
        phase10_markers[2].text ++ "\n" ++
        phase10_markers[3].text ++ "\n";
    try std.testing.expectError(ContractError.MarkerDuplicated, validateWorkflow(duplicate));
}

test "missing phase10 validation route fails closed" {
    const bad =
        phase9_markers[0].text ++ "\n" ++
        phase9_markers[1].text ++ "\n" ++
        phase9_markers[2].text ++ "\n" ++
        phase9_markers[3].text ++ "\n" ++
        phase9_markers[4].text ++ "\n" ++
        phase7_markers[0].text ++ "\n" ++
        phase7_markers[1].text ++ "\n" ++
        phase7_markers[2].text ++ "\n" ++
        phase7_markers[3].text ++ "\n" ++
        phase10_markers[0].text ++ "\n" ++
        phase10_markers[1].text ++ "\n" ++
        phase10_markers[3].text ++ "\n";
    try std.testing.expectError(ContractError.MissingMarker, validateWorkflow(bad));
}
