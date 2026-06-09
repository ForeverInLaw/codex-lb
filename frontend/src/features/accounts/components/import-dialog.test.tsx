import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ImportDialog } from "@/features/accounts/components/import-dialog";

describe("ImportDialog", () => {
  it("submits multiple batch files and shows the batch summary", async () => {
    const user = userEvent.setup();
    const onBatchImport = vi.fn(async () => ({
      imported: 1,
      skipped: 1,
      failed: 1,
      results: [
        {
          sourceFilename: "accounts-a.json",
          index: 0,
          status: "imported" as const,
          accountId: "acc-a",
          email: "a@example.com",
          planType: "team",
        },
        {
          sourceFilename: "accounts-b.json",
          index: 0,
          status: "skipped" as const,
          accountId: "acc-b",
          email: "b@example.com",
          planType: "plus",
        },
        {
          sourceFilename: "accounts-b.json",
          index: 1,
          status: "failed" as const,
          error: "Unsupported account import format",
        },
      ],
    }));

    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={vi.fn()}
        onImport={vi.fn()}
        onBatchImport={onBatchImport}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Batch" }));
    await user.upload(screen.getByLabelText("Files"), [
      new File(["{}"], "accounts-a.json", { type: "application/json" }),
      new File(["[]"], "accounts-b.json", { type: "application/json" }),
    ]);
    await user.click(screen.getByRole("button", { name: "Import" }));

    expect(onBatchImport).toHaveBeenCalledWith([
      expect.objectContaining({ name: "accounts-a.json" }),
      expect.objectContaining({ name: "accounts-b.json" }),
    ]);
    expect(await screen.findByText("Imported")).toBeInTheDocument();
    expect(screen.getByText("Skipped")).toBeInTheDocument();
    expect(screen.getByText("Failed")).toBeInTheDocument();
    expect(screen.getByText("Unsupported account import format")).toBeInTheDocument();
  });
});
