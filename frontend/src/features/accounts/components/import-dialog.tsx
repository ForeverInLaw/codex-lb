import { useState } from "react";
import type { FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { AccountBatchImportResponse } from "@/features/accounts/schemas";

type ImportMode = "single" | "batch";

export type ImportDialogProps = {
  open: boolean;
  busy: boolean;
  error: string | null;
  onOpenChange: (open: boolean) => void;
  onImport: (file: File) => Promise<void>;
  onBatchImport: (files: File[]) => Promise<AccountBatchImportResponse>;
};

export function ImportDialog({
  open,
  busy,
  error,
  onOpenChange,
  onImport,
  onBatchImport,
}: ImportDialogProps) {
  const [mode, setMode] = useState<ImportMode>("single");
  const [file, setFile] = useState<File | null>(null);
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [batchSummary, setBatchSummary] = useState<AccountBatchImportResponse | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (mode === "single") {
      if (!file) {
        return;
      }
      await onImport(file);
      onOpenChange(false);
      setFile(null);
      setBatchSummary(null);
      return;
    }
    if (batchFiles.length === 0) {
      return;
    }
    const summary = await onBatchImport(batchFiles);
    setBatchSummary(summary);
  };

  const canSubmit = mode === "single" ? !!file : batchFiles.length > 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Import accounts</DialogTitle>
          <DialogDescription>Upload account JSON credentials.</DialogDescription>
        </DialogHeader>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-2">
            <Button
              type="button"
              variant={mode === "single" ? "default" : "outline"}
              onClick={() => setMode("single")}
            >
              Single
            </Button>
            <Button
              type="button"
              variant={mode === "batch" ? "default" : "outline"}
              onClick={() => setMode("batch")}
            >
              Batch
            </Button>
          </div>

          <div className="space-y-2">
            {mode === "single" ? (
              <>
                <Label htmlFor="auth-json-file">File</Label>
                <Input
                  id="auth-json-file"
                  type="file"
                  accept="application/json,.json"
                  onChange={(event) => {
                    setFile(event.target.files?.[0] ?? null);
                    setBatchSummary(null);
                  }}
                />
              </>
            ) : (
              <>
                <Label htmlFor="accounts-json-files">Files</Label>
                <Input
                  id="accounts-json-files"
                  type="file"
                  accept="application/json,.json"
                  multiple
                  onChange={(event) => {
                    setBatchFiles(Array.from(event.target.files ?? []));
                    setBatchSummary(null);
                  }}
                />
              </>
            )}
          </div>

          {error ? (
            <p className="rounded-md border border-destructive/30 bg-destructive/10 px-2 py-1 text-xs text-destructive">
              {error}
            </p>
          ) : null}

          {batchSummary ? <BatchImportSummary summary={batchSummary} /> : null}

          <DialogFooter>
            <Button type="submit" disabled={busy || !canSubmit}>
              Import
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function BatchImportSummary({ summary }: { summary: AccountBatchImportResponse }) {
  const visibleResults = summary.results.slice(0, 6);
  return (
    <div className="rounded-md border bg-muted/30 p-3 text-sm">
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <div className="text-lg font-semibold text-foreground">{summary.imported}</div>
          <div className="text-xs text-muted-foreground">Imported</div>
        </div>
        <div>
          <div className="text-lg font-semibold text-foreground">{summary.skipped}</div>
          <div className="text-xs text-muted-foreground">Skipped</div>
        </div>
        <div>
          <div className="text-lg font-semibold text-foreground">{summary.failed}</div>
          <div className="text-xs text-muted-foreground">Failed</div>
        </div>
      </div>
      {visibleResults.length > 0 ? (
        <div className="mt-3 max-h-32 space-y-1 overflow-auto text-xs">
          {visibleResults.map((result) => (
            <div
              key={`${result.sourceFilename}-${result.index}-${result.status}`}
              className="flex items-center justify-between gap-3 rounded bg-background px-2 py-1"
            >
              <span className="min-w-0 truncate">
                {result.sourceFilename} #{result.index + 1}
              </span>
              <span className="shrink-0 text-muted-foreground">
                {result.status === "failed" ? result.error : result.email}
              </span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
