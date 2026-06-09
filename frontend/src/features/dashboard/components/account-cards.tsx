import { Users } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { AccountCard, type AccountCardProps } from "@/features/dashboard/components/account-card";
import type { AccountSummary } from "@/features/dashboard/schemas";

const ACCOUNT_CARD_VISIBLE_ROWS = 2;
// Account cards can grow when the optional email row is rendered.
const ACCOUNT_CARD_ROW_HEIGHT_REM = 11.5;
const ACCOUNT_CARD_ROW_GAP_REM = 1;
const ACCOUNT_CARD_RENDER_LIMIT = 24;
const ACCOUNT_CARD_ANIMATION_STAGGER_LIMIT = 12;

export type AccountCardsProps = {
  accounts: AccountSummary[];
  onAction?: AccountCardProps["onAction"];
};

export function AccountCards({ accounts, onAction }: AccountCardsProps) {
  if (accounts.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="No accounts connected yet"
        description="Import or authenticate an account to get started."
      />
    );
  }

  const visibleAccounts = accounts.slice(0, ACCOUNT_CARD_RENDER_LIMIT);
  const isBounded = visibleAccounts.length < accounts.length;

  return (
    <div className="space-y-2">
      <div
        data-testid="dashboard-account-cards"
        className="grid gap-4 overflow-y-auto pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:grid-cols-2 lg:grid-cols-3"
        style={{
          maxHeight: `calc(${ACCOUNT_CARD_VISIBLE_ROWS} * ${ACCOUNT_CARD_ROW_HEIGHT_REM}rem + ${(ACCOUNT_CARD_VISIBLE_ROWS - 1) * ACCOUNT_CARD_ROW_GAP_REM}rem)`,
        }}
      >
        {visibleAccounts.map((account, index) => (
          <div
            key={account.accountId}
            className="animate-fade-in-up"
            style={{ animationDelay: `${Math.min(index, ACCOUNT_CARD_ANIMATION_STAGGER_LIMIT) * 40}ms` }}
          >
            <AccountCard
              account={account}
              showAccountId={account.isEmailDuplicate === true}
              onAction={onAction}
            />
          </div>
        ))}
      </div>
      {isBounded ? (
        <div className="rounded-md border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
          Showing {visibleAccounts.length} of {accounts.length} accounts
        </div>
      ) : null}
    </div>
  );
}
