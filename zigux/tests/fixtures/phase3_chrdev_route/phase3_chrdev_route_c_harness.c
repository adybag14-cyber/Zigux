#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void write_summary(FILE *out, const struct zigux_chrdev_route_summary *summary)
{
    fprintf(out,
        "{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"flags\":%u}",
        summary->major,
        summary->target_minor,
        summary->selected_count,
        summary->resolved_index,
        summary->resolved_dev,
        summary->granted_mode,
        summary->entry_ops,
        summary->data_ops,
        summary->exit_ops,
        summary->blocked_ops,
        summary->flags);
}

int main(void)
{
    const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
    const struct zigux_chrdev_route_view routable_view =
        zigux_chrdev_route_view_from_bits(words, 240, 32, 8, 6, 2,
                          ZIGUX_IDA_POLICY_FIRST_FIT, 34,
                          ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                          ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                          ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                              ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE);
    const struct zigux_chrdev_route_view blocked_view =
        zigux_chrdev_route_view_from_bits(words, 240, 32, 8, 8, 2,
                          ZIGUX_IDA_POLICY_LAST_FIT, 37,
                          ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                          ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                          ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                              ZIGUX_CHRDEV_FOP_WRITE);
    const struct zigux_chrdev_route_view denied_view =
        zigux_chrdev_route_view_from_bits(words, 240, 32, 8, 8, 2,
                          ZIGUX_IDA_POLICY_LAST_FIT, 37,
                          ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                          ZIGUX_CHRDEV_MODE_READ,
                          ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                              ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE);
    const struct zigux_chrdev_route_view miss_view =
        zigux_chrdev_route_view_from_bits(words, 240, 32, 8, 8, 2,
                          ZIGUX_IDA_POLICY_LAST_FIT, 35,
                          ZIGUX_CHRDEV_MODE_READ,
                          ZIGUX_CHRDEV_MODE_READ,
                          ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                              ZIGUX_CHRDEV_FOP_READ);
    const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
    const struct zigux_chrdev_route_view exhausted_view =
        zigux_chrdev_route_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
                          ZIGUX_IDA_POLICY_FIRST_FIT, 20,
                          ZIGUX_CHRDEV_MODE_READ,
                          ZIGUX_CHRDEV_MODE_READ,
                          ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                              ZIGUX_CHRDEV_FOP_READ);
    const struct zigux_chrdev_route_view empty_view = {
        .bits_addr = 0,
        .major = 240,
        .first_minor = 0,
        .minor_count = 0,
        .max_scan = 0,
        .request_count = 2,
        .policy = ZIGUX_IDA_POLICY_FIRST_FIT,
        .target_minor = 0,
        .requested_mode = ZIGUX_CHRDEV_MODE_READ,
        .supported_mode = ZIGUX_CHRDEV_MODE_READ,
        .available_ops = ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                 ZIGUX_CHRDEV_FOP_READ,
        .reserved = 0,
    };

    fputs("{\"constants\":{\"chrdev_route_flag_truncated\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_TRUNCATED);
    fputs(",\"chrdev_route_flag_found\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_FOUND);
    fputs(",\"chrdev_route_flag_exhausted\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_EXHAUSTED);
    fputs(",\"chrdev_route_flag_hit\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_HIT);
    fputs(",\"chrdev_route_flag_permitted\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_PERMITTED);
    fputs(",\"chrdev_route_flag_denied\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_DENIED);
    fputs(",\"chrdev_route_flag_routable\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_ROUTABLE);
    fputs(",\"chrdev_route_flag_blocked\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_FLAG_BLOCKED);
    fputs(",\"chrdev_route_index_none\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_ROUTE_INDEX_NONE);

    fputs("},\"routable\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_route_summary summary =
            zigux_chrdev_route_summarize(&routable_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"blocked\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_route_summary summary =
            zigux_chrdev_route_summarize(&blocked_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"denied\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_route_summary summary =
            zigux_chrdev_route_summarize(&denied_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"miss\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_route_summary summary =
            zigux_chrdev_route_summarize(&miss_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"exhausted\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_route_summary summary =
            zigux_chrdev_route_summarize(&exhausted_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"empty\":{\"is_valid\":", stdout);
    fputs(zigux_chrdev_route_view_valid(&empty_view) ? "true" : "false", stdout);
    fputs(",\"summary\":", stdout);
    {
        const struct zigux_chrdev_route_summary summary =
            zigux_chrdev_route_summarize(&empty_view);
        write_summary(stdout, &summary);
    }

    fputs("}}\n", stdout);
    return 0;
}
