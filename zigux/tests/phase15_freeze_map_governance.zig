const std = @import("std");

const GovernanceRequirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const BlockerOwnership = struct {
    anchor: []const u8,
    owner: []const u8,
    phase: []const u8,
    status_bucket: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
    governance_requirements: []const GovernanceRequirement,
    blocker_ownership: []const BlockerOwnership,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 freeze-map governance manifest records the bounded governance slice" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_freeze_map_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-Y01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("9342905d34fb98d6fcd88cf2e88efed7355131d2", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocker_ownership.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.freeze_in_c_targets[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.freeze_in_c_targets[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.freeze_in_c_targets[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.freeze_in_c_targets[3]);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.study_only_targets[0]);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.study_only_targets[1]);

    for (manifest.blocker_ownership, 0..) |ownership, i| {
        try std.testing.expect(ownership.anchor.len > 0);
        try std.testing.expect(ownership.owner.len > 0);
        try std.testing.expectEqualStrings("Phase 15", ownership.phase);
        try std.testing.expectEqualStrings("freeze_in_c", ownership.status_bucket);
        try std.testing.expectEqualStrings("Phase 15 parity scorecard plus Architecture Council reopen record", ownership.validation_gate);
        try std.testing.expectEqualStrings("Architecture Council freeze-map owner", ownership.rollback_owner);
        try std.testing.expectEqualStrings(manifest.freeze_in_c_targets[i], ownership.anchor);

        for (manifest.blocker_ownership[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, ownership.anchor, other.anchor));
        }
    }

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_freeze_doc = false;
    var saw_note = false;
    var saw_build = false;
    var saw_make = false;
    var saw_closeout_sync = false;
    var saw_governance_family_alignment = false;
    var saw_blocker_ownership_sync = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase15-freeze-map-governance-doc")) {
            saw_freeze_doc = true;
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-in-C") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-freeze-map-governance-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "parity-scorecard") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-build-gate")) {
            saw_build = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-make-target")) {
            saw_make = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-stay-in-c-closeout-sync")) {
            saw_closeout_sync = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "no-silent-exception wording") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-governance-family-alignment")) {
            saw_governance_family_alignment = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "already landed") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "indefinite-C policy") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-blocker-ownership-sync")) {
            saw_blocker_ownership_sync = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "owner, validation-gate, and rollback-owner inventory") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "current long-term C-owned posture") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 7), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_freeze_doc);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_make);
    try std.testing.expect(saw_closeout_sync);
    try std.testing.expect(saw_governance_family_alignment);
    try std.testing.expect(saw_blocker_ownership_sync);
    try std.testing.expect(saw_blocker);
}

test "phase 15 freeze-map governance doc records the required gating language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Governance For Freeze-Map Changes") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "Architecture Council") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "owner, phase, status bucket, validation gate, and rollback owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "parity scorecard") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Stay-In-C Policy") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "keep the code in C and record the blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "no silent exception path") != null);
}

test "phase 15 freeze-map governance note records the current blocker posture honestly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const governance_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-freeze-map-governance.md",
        std.testing.allocator,
        .limited(20 * 1024),
    );
    defer std.testing.allocator.free(governance_note);

    try std.testing.expect(std.mem.indexOf(u8, governance_note, "PHASE15_LANE_KEY=P15-Y01") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "## Freeze-In-C Anchor Ownership Inventory") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "kernel scheduler maintainers") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "memory-management maintainers") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "RCU maintainers") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "network buffer maintainers") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Architecture Council freeze-map owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "## Current blocker posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "no bounded scheduler seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "no bounded allocator seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "published Phase 14 follow-up is still wider than the allowed RCU seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "maintenance mode") != null);
}

test "phase 15 governance manifest required terms stay aligned with the freeze map" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_freeze_map_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const governance_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-freeze-map-governance.md",
        std.testing.allocator,
        .limited(20 * 1024),
    );
    defer std.testing.allocator.free(governance_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    for (parsed.value.governance_requirements) |requirement| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len > 0);

        for (requirement.required_terms) |term| {
            try std.testing.expect(std.mem.indexOf(u8, freeze_map, term) != null);
        }
    }

    for (parsed.value.blocker_ownership) |ownership| {
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.anchor) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.validation_gate) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.rollback_owner) != null);
    }
}