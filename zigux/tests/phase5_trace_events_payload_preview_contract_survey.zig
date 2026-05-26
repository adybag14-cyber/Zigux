const std = @import("std");
const payload_preview_contract = @import("trace_events_payload_preview_contract");

const ExactCheck = struct {
    id: []const u8,
    kind: []const u8,
    expected: []const u8,
};

const manifest_json = @embedFile("phase5_trace_events_payload_preview_contract_manifest.json");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    sample_path: []const u8,
    validation_entrypoint: []const u8,
    review_prompts: []const []const u8,
    exact_checks: []const ExactCheck,
    non_goals: []const []const u8,
};

fn manifestById(manifest: Manifest, id: []const u8) ?ExactCheck {
    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, id)) return check;
    }
    return null;
}

test "phase 5 trace-events payload-preview survey manifest stays aligned with the companion packet" {
    const alloc = std.testing.allocator;
    const manifest = try std.json.parseFromSlice(Manifest, alloc, manifest_json, .{});
    defer manifest.deinit();

    try std.testing.expectEqualStrings("P5-L24", manifest.value.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.value.phase);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.value.anchor);
    try std.testing.expectEqualStrings(
        "samples/zigux/trace_events_payload_preview_contract.zig",
        manifest.value.sample_path,
    );
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase5_trace_events_payload_preview_contract_survey.zig",
        manifest.value.validation_entrypoint,
    );
    try std.testing.expectEqual(@as(usize, 6), manifest.value.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.value.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.value.non_goals.len);

    var saw_route_prompt = false;
    var saw_focus_prompt = false;
    var saw_cycle_prompt = false;
    var saw_rbtree_boundary_prompt = false;
    var saw_runtime_boundary_prompt = false;

    for (manifest.value.review_prompts) |prompt| {
        if (std.mem.indexOf(u8, prompt, "zig test samples/zigux/trace_events_payload_preview_contract.zig") != null and
            std.mem.indexOf(u8, prompt, "zig test zigux/tests/phase5_trace_events_payload_preview_contract.zig") != null and
            std.mem.indexOf(u8, prompt, "zig test zigux/tests/phase5_trace_events_payload_preview_contract_survey.zig") != null and
            std.mem.indexOf(u8, prompt, "phase5_build.zig") != null)
        {
            saw_route_prompt = true;
        }

        if (std.mem.indexOf(u8, prompt, "payload_shape,string_selection,formatted_message,conditional_event_families,function_callback_registration,ownership_and_lifetime") != null) {
            saw_focus_prompt = true;
        }

        if (std.mem.indexOf(u8, prompt, "Mother Goose") != null and
            std.mem.indexOf(u8, prompt, "One ring to rule them all") != null and
            std.mem.indexOf(u8, prompt, "zero through four elements") != null)
        {
            saw_cycle_prompt = true;
        }

        if (std.mem.indexOf(u8, prompt, "standalone helper or rbtree sample") != null) {
            saw_rbtree_boundary_prompt = true;
        }

        if (std.mem.indexOf(u8, prompt, "runtime registration or module wiring") != null) {
            saw_runtime_boundary_prompt = true;
        }
    }

    try std.testing.expect(saw_route_prompt);
    try std.testing.expect(saw_focus_prompt);
    try std.testing.expect(saw_cycle_prompt);
    try std.testing.expect(saw_rbtree_boundary_prompt);
    try std.testing.expect(saw_runtime_boundary_prompt);
}

test "phase 5 trace-events payload-preview survey exact checks stay aligned with the companion contract" {
    const alloc = std.testing.allocator;
    const manifest = try std.json.parseFromSlice(Manifest, alloc, manifest_json, .{});
    defer manifest.deinit();

    const contract = payload_preview_contract.referencePattern();

    const focus_check = manifestById(manifest.value, "focus-order") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, focus_check.expected, "payload_shape,string_selection,formatted_message,conditional_event_families,function_callback_registration,ownership_and_lifetime") != null);

    const family_check = manifestById(manifest.value, "event-family-counts") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, family_check.expected, "six main-thread event families") != null);
    try std.testing.expect(std.mem.indexOf(u8, family_check.expected, "two function-callback families") != null);
    try std.testing.expectEqual(@as(usize, 6), contract.event_family_count);
    try std.testing.expectEqual(@as(usize, 2), contract.callback_family_count);

    const gandalf_check = manifestById(manifest.value, "gandalf-preview") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, gandalf_check.expected, "selected_string_slot 2") != null);
    try std.testing.expect(std.mem.indexOf(u8, gandalf_check.expected, "payload preview 1,2") != null);
    try std.testing.expect(std.mem.indexOf(u8, gandalf_check.expected, "iter=2") != null);
    try std.testing.expectEqualStrings("Gandalf", contract.cases[2].selected_string);
    try std.testing.expectEqual(@as(usize, 2), contract.cases[2].selected_string_slot);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2 }, contract.cases[2].payload_preview[0..contract.cases[2].payload_preview_len]);

    const largest_check = manifestById(manifest.value, "largest-preview") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, largest_check.expected, "One ring to rule them all") != null);
    try std.testing.expect(std.mem.indexOf(u8, largest_check.expected, "payload preview 1,2,3,4") != null);
    try std.testing.expect(std.mem.indexOf(u8, largest_check.expected, "iter=4") != null);
    try std.testing.expectEqualStrings("One ring to rule them all", contract.cases[4].selected_string);
    try std.testing.expectEqual(@as(usize, 4), contract.cases[4].selected_string_slot);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4 }, contract.cases[4].payload_preview[0..contract.cases[4].payload_preview_len]);

    const stage_check = manifestById(manifest.value, "initialized-stage-posture") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, stage_check.expected, "initialized-stage review posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, stage_check.expected, "conditional, vararg, and relative-location path checks") != null);
    try std.testing.expect(contract.preserves_initialized_stage);
    try std.testing.expect(contract.conditional_paths_checked);
    try std.testing.expect(contract.vararg_payload_path_checked);
    try std.testing.expect(contract.relative_location_path_checked);
}
