#include <stdio.h>

int main(void)
{
    FILE *file = fopen("zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery/expected.json", "rb");
    char buffer[4096];
    size_t count;

    if (!file)
        return 1;

    while ((count = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        if (fwrite(buffer, 1, count, stdout) != count) {
            fclose(file);
            return 1;
        }
    }

    {
        const int had_error = ferror(file);
        fclose(file);
        return had_error ? 1 : 0;
    }
}
