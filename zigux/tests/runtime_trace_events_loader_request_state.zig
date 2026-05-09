const std = @import("std");
const runtime_trace_events_loader = @import("runtime_trace_events_loader");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");
const runtime_loader = @import("runtime_loader");

test "phase 9 trace-events companion replay rejects non-prepared shared requests before local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    _ = try shared_request.requestRuntimeLoad();

    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        shared_request.plan,
    ));

    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        shared_request.plan,
    ));
}
