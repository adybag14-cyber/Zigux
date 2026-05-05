const std = @import("std");
const workqueue_bridge = @import("workqueue_bridge");

const SurveySummary = struct {
    workqueue_c_lines: usize,
    workqueue_internal_h_lines: usize,
    test_workqueue_c_lines: usize,
    preexisting_kernel_export_shim_present: bool,
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_workqueue_bridge_present: bool,
    preexisting_phase14_workqueue_test_present: bool,
    preexisting_phase14_workqueue_manifest_present: bool,
    preexisting_phase14_workqueue_slice_note_present: bool,
    preexisting_phase14_workqueue_survey_note_present: bool,
};
const Gap = struct { id: []const u8, status: []const u8, kind: []const u8, zigux_destination: []const u8, why_now: []const u8, };
const Manifest = struct { lane_key: []const u8, phase: []const u8, surveyed_commit: []const u8, anchor: []const u8, roadmap_destinations: []const []const u8, survey_summary: SurveySummary, gaps: []const Gap, };
fn isAllowedStatus(status: []const u8) bool { return std.mem.eql(u8, status, "starter_landed") or std.mem.eql(u8, status, "ready_next") or std.mem.eql(u8, status, "blocked_on_live_concurrency"); }
fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 { var io_instance: std.Io.Threaded = .init(allocator, .{}); defer io_instance.deinit(); return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(32 * 1024)); }

test "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap" {
 const manifest_json = try readFixture(std.testing.allocator, "zigux/tests/phase14_workqueue_bridge_manifest.json"); defer std.testing.allocator.free(manifest_json);
 const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{}); defer parsed.deinit(); const manifest = parsed.value;
 try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);
 try std.testing.expectEqualStrings("Phase 14", manifest.phase);
 try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
 try std.testing.expectEqualStrings("9e278f632d6d5097cb8cfc2dc61744ae105baa8c", manifest.surveyed_commit);
 try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);
 var starter_landed_count: usize = 0; var ready_next_count: usize = 0; var blocked_count: usize = 0;
 var saw_delayed_submission = false; var saw_delayed_timer = false;
 for (manifest.gaps) |gap| {
  try std.testing.expect(isAllowedStatus(gap.status));
  if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1 else if (std.mem.eql(u8, gap.status, "ready_next")) ready_next_count += 1 else if (std.mem.eql(u8, gap.status, "blocked_on_live_concurrency")) blocked_count += 1;
  if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-submission-alias-followup")) saw_delayed_submission = true;
  if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-timer-expiry-followup")) saw_delayed_timer = true;
 }
 try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
 try std.testing.expectEqual(@as(usize, 1), ready_next_count);
 try std.testing.expectEqual(@as(usize, 1), blocked_count);
 try std.testing.expect(saw_delayed_submission);
 try std.testing.expect(saw_delayed_timer);
}

test "phase14 workqueue bridge survey note pins the lane key and surveyed commit" {
 const survey_note = try readFixture(std.testing.allocator, "Documentation/zigux/phase14-workqueue-bridge-survey.md"); defer std.testing.allocator.free(survey_note);
 try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L04") != null);
 try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=9e278f632d6d5097cb8cfc2dc61744ae105baa8c") != null);
 try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SLICE=workqueue-delayed-submission-alias-audit") != null);
 try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-delayed-submission-alias-followup") != null);
 try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-delayed-timer-expiry-followup") != null);
}

test "phase14 workqueue bridge descriptor stays at boundary-map posture" {
 const map = workqueue_bridge.WorkqueueBridgeLab.boundaryMap(); const audit = workqueue_bridge.WorkqueueBridgeLab.concurrencyAudit();
 try std.testing.expectEqual(@as(usize, 6), map.areas.len);
 try std.testing.expectEqual(@as(usize, 11), audit.checkpoints.len);
 try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "delayed_work_timer_fn()") != null);
 try std.testing.expect(std.mem.indexOf(u8, workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus(), "__queue_work()") != null);
}
