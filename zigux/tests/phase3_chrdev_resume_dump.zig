const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const chrdev_resume_plan = @import("chrdev_resume_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevResumeSummary) !void {
    try writer.writeAll("{\"major\":");
    try writer.print("{d}", .{summary.major});
    try writer.writeAll(",\"target_minor\":");
    try writer.print("{d}", .{summary.target_minor});
    try writer.writeAll(",\"selected_count\":");
    try writer.print("{d}", .{summary.selected_count});
    try writer.writeAll(",\"resolved_index\":");
    try writer.print("{d}", .{summary.resolved_index});
    try writer.writeAll(",\"resolved_dev\":");
    try writer.print("{d}", .{summary.resolved_dev});
    try writer.writeAll(",\"granted_mode\":");
    try writer.print("{d}", .{summary.granted_mode});
    try writer.writeAll(",\"io_op\":");
    try writer.print("{d}", .{summary.io_op});
    try writer.writeAll(",\"requested_bytes\":");
    try writer.print("{d}", .{summary.requested_bytes});
    try writer.writeAll(",\"start_offset\":");
    try writer.print("{d}", .{summary.start_offset});
    try writer.writeAll(",\"next_offset\":");
    try writer.print("{d}", .{summary.next_offset});
    try writer.writeAll(",\"initial_bytes_completed\":");
    try writer.print("{d}", .{summary.initial_bytes_completed});
    try writer.writeAll(",\"final_bytes_completed\":");
    try writer.print("{d}", .{summary.final_bytes_completed});
    try writer.writeAll(",\"pass_count\":");
    try writer.print("{d}", .{summary.pass_count});
    try writer.writeAll(",\"issued_bytes\":");
    try writer.print("{d}", .{summary.issued_bytes});
    try writer.writeAll(",\"remaining_bytes\":");
    try writer.print("{d}", .{summary.remaining_bytes});
    try writer.writeAll(",\"entry_ops\":");
    try writer.print("{d}", .{summary.entry_ops});
    try writer.writeAll(",\"data_ops\":");
    try writer.print("{d}", .{summary.data_ops});
    try writer.writeAll(",\"exit_ops\":");
    try writer.print("{d}", .{summary.exit_ops});
    try writer.writeAll(",\"blocked_ops\":");
    try writer.print("{d}", .{summary.blocked_ops});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{summary.flags});
    try writer.writeAll("}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [8192]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const complete_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3);
    const continuable_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 1);
    const blocked_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3);
    const denied_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2);
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = chrdev_resume_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2);
    const empty_view = abi.ChrdevResumeView{
        .bits_addr = 0,
        .major = 240,
        .first_minor = 0,
        .minor_count = 0,
        .max_scan = 0,
        .request_count = 2,
        .policy = abi.IDA_POLICY_FIRST_FIT,
        .target_minor = 0,
        .requested_mode = abi.CHRDEV_MODE_READ,
        .supported_mode = abi.CHRDEV_MODE_READ,
        .available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ,
        .io_op = abi.CHRDEV_IO_OP_READ,
        .requested_bytes = 8,
        .max_chunk_bytes = 8,
        .file_offset = 0,
        .bytes_completed = 0,
        .max_segments = 1,
        .resume_passes = 2,
        .reserved = 0,
    };

    try writer.writeAll("{\"constants\":{\"chrdev_resume_flag_truncated\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_TRUNCATED});
    try writer.writeAll(",\"chrdev_resume_flag_found\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_FOUND});
    try writer.writeAll(",\"chrdev_resume_flag_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_EXHAUSTED});
    try writer.writeAll(",\"chrdev_resume_flag_hit\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_HIT});
    try writer.writeAll(",\"chrdev_resume_flag_permitted\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_PERMITTED});
    try writer.writeAll(",\"chrdev_resume_flag_denied\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_DENIED});
    try writer.writeAll(",\"chrdev_resume_flag_routable\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_ROUTABLE});
    try writer.writeAll(",\"chrdev_resume_flag_blocked\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_BLOCKED});
    try writer.writeAll(",\"chrdev_resume_flag_dispatchable\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_DISPATCHABLE});
    try writer.writeAll(",\"chrdev_resume_flag_resumed\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_RESUMED});
    try writer.writeAll(",\"chrdev_resume_flag_continuable\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_CONTINUABLE});
    try writer.writeAll(",\"chrdev_resume_flag_completes\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_COMPLETES});
    try writer.writeAll(",\"chrdev_resume_flag_progressed\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_PROGRESSED});
    try writer.writeAll(",\"chrdev_resume_flag_stalled\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_STALLED});
    try writer.writeAll(",\"chrdev_resume_flag_complete_ok\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_FLAG_COMPLETE_OK});
    try writer.writeAll(",\"chrdev_resume_index_none\":");
    try writer.print("{d}", .{abi.CHRDEV_RESUME_INDEX_NONE});
    try writer.writeAll("},\"complete\":{\"summary\":");
    try writeSummary(writer, chrdev_resume_plan.summarize(complete_view));
    try writer.writeAll("},\"continuable\":{\"summary\":");
    try writeSummary(writer, chrdev_resume_plan.summarize(continuable_view));
    try writer.writeAll("},\"blocked\":{\"summary\":");
    try writeSummary(writer, chrdev_resume_plan.summarize(blocked_view));
    try writer.writeAll("},\"denied\":{\"summary\":");
    try writeSummary(writer, chrdev_resume_plan.summarize(denied_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, chrdev_resume_plan.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (chrdev_resume_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, chrdev_resume_plan.summarize(empty_view));
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
