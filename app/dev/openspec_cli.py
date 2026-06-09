from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

VERSION = "0.1.0"
ROOT = Path("openspec")
CHANGE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

ArtifactState = Literal["complete", "ready", "blocked"]


@dataclass(frozen=True, slots=True)
class ArtifactStatus:
    id: str
    state: ArtifactState
    path: str
    description: str


class OpenSpecCliError(Exception):
    pass


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        if args.version:
            print(VERSION)
        elif args.command == "new":
            _new_change(args.kind, args.name)
        elif args.command == "status":
            _show_status(args.change, as_json=args.json)
        elif args.command == "instructions":
            _show_instructions(args.artifact, args.change, as_json=args.json)
        elif args.command == "list":
            _list_changes(as_json=args.json)
        elif args.command == "validate":
            _validate(args.target, specs=args.specs, strict=args.strict)
        elif args.command == "version":
            print(VERSION)
        else:
            parser.print_help()
    except OpenSpecCliError as exc:
        print(f"openspec: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openspec")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="Create a new OpenSpec object")
    new_parser.add_argument("kind", choices=["change"])
    new_parser.add_argument("name")

    status_parser = subparsers.add_parser("status", help="Show change artifact status")
    status_parser.add_argument("--change", required=True)
    status_parser.add_argument("--json", action="store_true")

    instructions_parser = subparsers.add_parser("instructions", help="Show artifact instructions")
    instructions_parser.add_argument("artifact", choices=["proposal", "design", "tasks", "spec"])
    instructions_parser.add_argument("--change", required=True)
    instructions_parser.add_argument("--json", action="store_true")

    list_parser = subparsers.add_parser("list", help="List active changes")
    list_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate OpenSpec files")
    validate_parser.add_argument("target", nargs="?")
    validate_parser.add_argument("--specs", action="store_true")
    validate_parser.add_argument("--strict", action="store_true")

    version_parser = subparsers.add_parser("version", help="Print version")
    version_parser.set_defaults(command="version")
    return parser


def _new_change(kind: str, name: str) -> None:
    if kind != "change":
        raise OpenSpecCliError("only 'new change <name>' is supported")
    if not CHANGE_NAME_RE.match(name):
        raise OpenSpecCliError("change name must be kebab-case")
    change_dir = _change_dir(name)
    if change_dir.exists():
        raise OpenSpecCliError(f"change already exists: {change_dir}")
    change_dir.mkdir(parents=True)
    (change_dir / ".openspec.yaml").write_text("schema: spec-driven\n", encoding="utf-8")
    print(f"Created: {change_dir.as_posix()}")


def _show_status(change: str, *, as_json: bool) -> None:
    statuses = _artifact_statuses(change)
    if as_json:
        print(json.dumps({"change": change, "artifacts": [_status_to_json(status) for status in statuses]}, indent=2))
        return
    print(f"Change: {change}")
    for status in statuses:
        print(f"- {status.id}: {status.state} ({status.path})")


def _show_instructions(artifact: str, change: str, *, as_json: bool) -> None:
    path = _artifact_path(change, artifact)
    instruction = _artifact_instruction(artifact, path)
    if as_json:
        print(json.dumps({"change": change, "artifact": artifact, "path": path, "instruction": instruction}, indent=2))
        return
    print(instruction)


def _list_changes(*, as_json: bool) -> None:
    changes_root = ROOT / "changes"
    changes = sorted(
        [path.name for path in changes_root.iterdir() if path.is_dir() and path.name != "archive"],
        key=str.casefold,
    )
    if as_json:
        print(json.dumps({"changes": changes}, indent=2))
        return
    for change in changes:
        print(change)


def _validate(target: str | None, *, specs: bool, strict: bool) -> None:
    errors: list[str] = []
    if not ROOT.exists():
        errors.append("openspec/ directory is missing")
    if specs:
        spec_paths = _spec_paths()
        if not spec_paths:
            errors.append("no spec.md files found")
        for spec_path in spec_paths:
            errors.extend(_validate_spec_file(spec_path))
    elif target:
        change_dir = _change_dir(target)
        if not change_dir.exists():
            errors.append(f"change does not exist: {target}")
        else:
            errors.extend(_validate_change(change_dir, strict=strict))
    else:
        errors.append("pass a change name or --specs")

    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    if specs:
        print("OpenSpec specs are valid")
    else:
        print(f"OpenSpec change '{target}' is valid")


def _artifact_statuses(change: str) -> list[ArtifactStatus]:
    change_dir = _change_dir(change)
    if not change_dir.exists():
        raise OpenSpecCliError(f"change does not exist: {change}")
    proposal = change_dir / "proposal.md"
    specs_dir = change_dir / "specs"
    design = change_dir / "design.md"
    tasks = change_dir / "tasks.md"
    return [
        ArtifactStatus("proposal", _file_state(proposal), proposal.as_posix(), "Proposal and impact summary"),
        ArtifactStatus(
            "spec",
            "complete" if list(specs_dir.glob("*/spec.md")) else "ready" if proposal.exists() else "blocked",
            (specs_dir / "<capability>" / "spec.md").as_posix(),
            "Delta requirements",
        ),
        ArtifactStatus(
            "design",
            _file_state(design, ready_if=proposal.exists()),
            design.as_posix(),
            "Technical design",
        ),
        ArtifactStatus(
            "tasks",
            _file_state(tasks, ready_if=proposal.exists()),
            tasks.as_posix(),
            "Implementation tasks",
        ),
    ]


def _file_state(path: Path, *, ready_if: bool = True) -> ArtifactState:
    if path.exists() and path.read_text(encoding="utf-8").strip():
        return "complete"
    return "ready" if ready_if else "blocked"


def _status_to_json(status: ArtifactStatus) -> dict[str, str]:
    return {
        "id": status.id,
        "state": status.state,
        "path": status.path,
        "description": status.description,
    }


def _artifact_path(change: str, artifact: str) -> str:
    change_dir = _change_dir(change)
    if artifact == "spec":
        return (change_dir / "specs" / "<capability>" / "spec.md").as_posix()
    return (change_dir / f"{artifact}.md").as_posix()


def _artifact_instruction(artifact: str, path: str) -> str:
    if artifact == "proposal":
        return (
            f"Write {path} with sections: ## Why, ## What Changes, ## Capabilities, ## Impact. "
            "Keep it concise and avoid implementation details that belong in design.md."
        )
    if artifact == "spec":
        return (
            f"Write {path}. Use '# <capability> Specification (Delta)', then ADDED or MODIFIED "
            "Requirements. Each '### Requirement:' needs at least one '#### Scenario:'."
        )
    if artifact == "design":
        return f"Write {path} with architecture, data flow, error handling, migration/backcompat, and test strategy."
    return f"Write {path} as a checklist of concrete implementation and verification tasks."


def _validate_change(change_dir: Path, *, strict: bool) -> list[str]:
    errors: list[str] = []
    proposal = change_dir / "proposal.md"
    if not proposal.exists() or not proposal.read_text(encoding="utf-8").strip():
        errors.append(f"{proposal.as_posix()} is missing or empty")
    spec_paths = sorted((change_dir / "specs").glob("*/spec.md"))
    if strict and not spec_paths:
        errors.append(f"{(change_dir / 'specs').as_posix()} has no delta spec.md files")
    for spec_path in spec_paths:
        errors.extend(_validate_spec_file(spec_path))
    return errors


def _validate_spec_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not text.strip():
        return [f"{path.as_posix()} is empty"]
    first_heading = next((line for line in text.splitlines() if line.strip()), "")
    if not first_heading.startswith(("# ", "## ")):
        errors.append(f"{path.as_posix()} must start with a markdown heading")
    requirement_matches = list(re.finditer(r"^### Requirement:", text, flags=re.MULTILINE))
    if not requirement_matches:
        errors.append(f"{path.as_posix()} has no '### Requirement:' sections")
        return errors
    for index, match in enumerate(requirement_matches):
        end = requirement_matches[index + 1].start() if index + 1 < len(requirement_matches) else len(text)
        section = text[match.start() : end]
        if "#### Scenario:" not in section:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path.as_posix()}:{line} requirement has no scenario")
    return errors


def _spec_paths() -> list[Path]:
    main_specs = list((ROOT / "specs").glob("*/spec.md"))
    change_specs = list((ROOT / "changes").glob("*/specs/*/spec.md"))
    return sorted(main_specs + change_specs)


def _change_dir(change: str) -> Path:
    return ROOT / "changes" / change


if __name__ == "__main__":
    if "--version" in sys.argv and len(sys.argv) == 2:
        print(VERSION)
    else:
        main()
