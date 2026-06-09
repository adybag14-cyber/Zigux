const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ControlPlaneExpectation = struct {
    marker: []const u8,
};

const expected_control_plane = [_]ControlPlaneExpectation{
    .{
        .marker = "    branches: [ master ]",
    },
    .{
        .marker = "  pull_request:",
    },
    .{
        .marker = "  workflow_dispatch:",
    },
    .{
        .marker = "  contents: read",
    },
    .{
        .marker = "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    },
    .{
        .marker = "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    },
    .{
        .marker = "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    },
};

test "workflow control-plane markers stay before bootstrap job" {
    const allocator = std.testing.allocator;
    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
    defer allocator.free(workflow);

    try expectOrderedControlPlane(workflow);
}

test "workflow keeps master exact-head runs uncancelled" {
    const sample =
        \\name: zigux-bootstrap
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\  workflow_dispatch:
        \\permissions:
        \\  contents: read
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\concurrency:
        \\  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
        \\  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}
        \\jobs:
        \\  bootstrap:
    ;

    try expectOrderedControlPlane(sample);
}

test "workflow control-plane rejects missing or unsafe markers" {
    const missing_permission =
        \\name: zigux-bootstrap
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\  workflow_dispatch:
        \\permissions:
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\concurrency:
        \\  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
        \\  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}
        \\jobs:
        \\  bootstrap:
    ;
    try std.testing.expectError(error.MissingControlPlaneMarker, expectOrderedControlPlane(missing_permission));

    const unsafe_cancel =
        \\name: zigux-bootstrap
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\  workflow_dispatch:
        \\permissions:
        \\  contents: read
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\concurrency:
        \\  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
        \\  cancel-in-progress: true
        \\jobs:
        \\  bootstrap:
    ;
    try std.testing.expectError(error.MissingControlPlaneMarker, expectOrderedControlPlane(unsafe_cancel));

    const marker_after_jobs =
        \\name: zigux-bootstrap
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\  workflow_dispatch:
        \\permissions:
        \\  contents: read
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\concurrency:
        \\  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
        \\jobs:
        \\  bootstrap:
        \\  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}
    ;
    try std.testing.expectError(error.ControlPlaneAfterJobs, expectOrderedControlPlane(marker_after_jobs));
}

fn expectOrderedControlPlane(workflow: []const u8) !void {
    const jobs_index = std.mem.indexOf(u8, workflow, "\njobs:") orelse return error.MissingJobsBlock;
    var previous_index: usize = 0;

    inline for (expected_control_plane) |expectation| {
        const marker_index = std.mem.indexOf(u8, workflow, expectation.marker) orelse {
            return error.MissingControlPlaneMarker;
        };
        if (marker_index > jobs_index) {
            return error.ControlPlaneAfterJobs;
        }
        if (marker_index < previous_index) {
            return error.ControlPlaneOutOfOrder;
        }
        previous_index = marker_index;
    }
}
