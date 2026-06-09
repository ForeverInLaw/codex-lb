from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.auth import AuthFile, AuthTokens


class BatchImportParseError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class BatchImportFile:
    filename: str
    raw: bytes


@dataclass(frozen=True, slots=True)
class BatchImportEntry:
    source_filename: str
    index: int
    auth: AuthFile
    fallback_email: str | None = None
    fallback_account_id: str | None = None
    fallback_plan_type: str | None = None
    fallback_workspace_id: str | None = None
    fallback_workspace_label: str | None = None
    fallback_seat_type: str | None = None


@dataclass(frozen=True, slots=True)
class BatchImportEntryFailure:
    source_filename: str
    index: int
    error: str


@dataclass(frozen=True, slots=True)
class BatchImportParseResult:
    entries: list[BatchImportEntry]
    failures: list[BatchImportEntryFailure]


class _EnvelopeCredentials(BaseModel):
    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
    id_token: str | None = None
    chatgpt_account_id: str | None = None
    organization_id: str | None = None
    plan_type: str | None = None


class _EnvelopeAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    type: str
    credentials: _EnvelopeCredentials


class _EnvelopeFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    accounts: list[_EnvelopeAccount] = Field(min_length=1)
    exported_at: datetime | None = None


class _FlatCodexAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: str
    email: str
    access_token: str
    refresh_token: str
    id_token: str | None = None
    account_id: str | None = None
    last_refresh: datetime | None = None
    saved_at: datetime | None = None


def parse_batch_import_files(files: list[BatchImportFile]) -> BatchImportParseResult:
    entries: list[BatchImportEntry] = []
    failures: list[BatchImportEntryFailure] = []
    for file in files:
        try:
            parsed = json.loads(file.raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            failures.append(BatchImportEntryFailure(file.filename, 0, "Invalid JSON file"))
            continue
        file_result = _parse_file(file.filename, parsed)
        entries.extend(file_result.entries)
        failures.extend(file_result.failures)
    if not entries:
        raise BatchImportParseError("No supported account entries found")
    return BatchImportParseResult(entries=entries, failures=failures)


def _parse_file(filename: str, parsed: Any) -> BatchImportParseResult:
    if isinstance(parsed, dict) and isinstance(parsed.get("accounts"), list):
        return _parse_envelope(filename, parsed)
    if isinstance(parsed, dict):
        auth_entry = _parse_auth_file_entry(filename, parsed)
        if auth_entry is not None:
            return BatchImportParseResult(entries=[auth_entry], failures=[])
        entry = _parse_flat_entry(filename, 0, parsed)
        return BatchImportParseResult(
            entries=[entry] if entry else [],
            failures=[] if entry else [_unsupported(filename, 0)],
        )
    if isinstance(parsed, list):
        entries: list[BatchImportEntry] = []
        failures: list[BatchImportEntryFailure] = []
        for index, item in enumerate(parsed):
            if not isinstance(item, dict):
                failures.append(BatchImportEntryFailure(filename, index, "Account entry must be an object"))
                continue
            entry = _parse_flat_entry(filename, index, item)
            if entry is None:
                failures.append(_unsupported(filename, index))
            else:
                entries.append(entry)
        return BatchImportParseResult(entries=entries, failures=failures)
    return BatchImportParseResult(entries=[], failures=[_unsupported(filename, 0)])


def _parse_auth_file_entry(filename: str, parsed: dict[str, Any]) -> BatchImportEntry | None:
    try:
        auth = AuthFile.model_validate(parsed)
    except ValidationError:
        return None
    return BatchImportEntry(source_filename=filename, index=0, auth=auth)


def _parse_envelope(filename: str, parsed: dict[str, Any]) -> BatchImportParseResult:
    try:
        envelope = _EnvelopeFile.model_validate(parsed)
    except ValidationError as exc:
        return BatchImportParseResult(
            entries=[],
            failures=[BatchImportEntryFailure(filename, 0, _validation_message(exc))],
        )

    entries: list[BatchImportEntry] = []
    failures: list[BatchImportEntryFailure] = []
    for index, account in enumerate(envelope.accounts):
        if account.type.lower() != "oauth":
            failures.append(BatchImportEntryFailure(filename, index, "Only oauth envelope accounts are supported"))
            continue
        credentials = account.credentials
        entries.append(
            BatchImportEntry(
                source_filename=filename,
                index=index,
                auth=_auth_file(
                    access_token=credentials.access_token,
                    refresh_token=credentials.refresh_token,
                    id_token=credentials.id_token,
                    account_id=credentials.chatgpt_account_id,
                    last_refresh=envelope.exported_at,
                ),
                fallback_email=account.name,
                fallback_account_id=credentials.chatgpt_account_id,
                fallback_plan_type=credentials.plan_type,
                fallback_workspace_id=_clean(credentials.organization_id),
            )
        )
    return BatchImportParseResult(entries=entries, failures=failures)


def _parse_flat_entry(filename: str, index: int, parsed: dict[str, Any]) -> BatchImportEntry | None:
    try:
        account = _FlatCodexAccount.model_validate(parsed)
    except ValidationError:
        return None
    if account.type.lower() != "codex":
        return None
    return BatchImportEntry(
        source_filename=filename,
        index=index,
        auth=_auth_file(
            access_token=account.access_token,
            refresh_token=account.refresh_token,
            id_token=account.id_token,
            account_id=account.account_id,
            last_refresh=account.last_refresh or account.saved_at,
        ),
        fallback_email=account.email,
        fallback_account_id=account.account_id,
    )


def _auth_file(
    *,
    access_token: str,
    refresh_token: str,
    id_token: str | None,
    account_id: str | None,
    last_refresh: datetime | None,
) -> AuthFile:
    return AuthFile(
        tokens=AuthTokens(
            idToken=id_token or "",
            accessToken=access_token,
            refreshToken=refresh_token,
            accountId=account_id,
        ),
        lastRefreshAt=last_refresh,
    )


def _unsupported(filename: str, index: int) -> BatchImportEntryFailure:
    return BatchImportEntryFailure(filename, index, "Unsupported account import format")


def _validation_message(exc: ValidationError) -> str:
    first = exc.errors()[0] if exc.errors() else None
    if not first:
        return "Invalid account entry"
    location = ".".join(str(part) for part in first.get("loc", ()))
    message = str(first.get("msg", "Invalid account entry"))
    return f"{location}: {message}" if location else message


def _clean(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None
