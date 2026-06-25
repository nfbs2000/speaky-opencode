#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


BOOK_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = Path(os.environ.get("OPENCODE_BOOK_SOURCE_ROOT", BOOK_ROOT / "src"))
REPO_URL = "https://github.com/nfbs2000/speaky-opencode"
LATEST_REF = "dev"


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


EDITION_REF = os.environ.get("OPENCODE_BOOK_EDITION_REF") or git_output("rev-parse", "HEAD")
EDITION_LABEL = EDITION_REF[:10]
CURRENT_SOURCE_ROOT = "packages/opencode/src"
SURFACE_SOURCE_ROOTS = (
    CURRENT_SOURCE_ROOT,
    "packages/core/src",
    "packages/tui/src",
    "packages/app/src",
    "packages/desktop/src",
    "packages/server/src",
    "packages/plugin/src",
    "packages/sdk/js/src",
    "packages/web/src/content/docs",
)


@dataclass(frozen=True)
class TocEntry:
    title: str
    source_path: Path
    output_path: Path
    part: str


@dataclass(frozen=True)
class ResolvedSource:
    path: str
    kind: str
    original: str


def should_skip_repo_path(path: Path) -> bool:
    parts = set(path.parts)
    return bool(
        {".git", "target", "node_modules", ".venv", ".ruff_cache"} & parts
        or path.as_posix().startswith("course/book-opencode/")
    )


def repo_inventory() -> tuple[set[str], set[str]]:
    files: set[str] = set()
    dirs: set[str] = set()
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT)
        if should_skip_repo_path(rel):
            continue
        rel_posix = rel.as_posix()
        if path.is_dir():
            dirs.add(rel_posix)
        elif path.is_file():
            files.add(rel_posix)
    return files, dirs


REPO_FILES, REPO_DIRS = repo_inventory()


def parse_summary() -> list[TocEntry]:
    summary_path = SRC_ROOT / "SUMMARY.md"
    current_part = "시작"
    entries: list[TocEntry] = []
    item_re = re.compile(r"^\s*(?:-\s+)?\[([^\]]+)\]\(([^)]+)\)")
    for line in summary_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and not line.startswith("# 목차"):
            current_part = line[2:].strip()
            continue
        match = item_re.match(line)
        if not match:
            continue
        title, href = match.groups()
        source_rel = Path(href.removeprefix("./"))
        if source_rel.name == "SUMMARY.md":
            continue
        output_rel = source_rel.with_suffix(".html")
        entries.append(TocEntry(title=title, source_path=source_rel, output_path=output_rel, part=current_part))
    return entries


def source_like(token: str) -> bool:
    if len(token) > 180 or " " in token and "/" not in token:
        return False
    if token.startswith(("http://", "https://", "ws://", "@")):
        return False
    if token in {"item/*", "item.*", "thread/goal/*", "session/*", "tool/*"}:
        return False
    source_prefixes = (
        ".github/",
        ".opencode/",
        "assets/",
        "bin/",
        "docs/",
        "github/",
        "infra/",
        "packages/",
        "script/",
        "scripts/",
        "sdks/",
        "specs/",
        "src/",
        "agent/",
        "background/",
        "bus/",
        "cli/",
        "command/",
        "config/",
        "control-plane/",
        "global/",
        "lsp/",
        "mcp/",
        "patch/",
        "permission/",
        "plugin/",
        "project/",
        "provider/",
        "routes/",
        "server/",
        "session/",
        "share/",
        "skill/",
        "snapshot/",
        "storage/",
        "sync/",
        "tool/",
        "worktree/",
        "test/",
    )
    source_suffixes = (
        ".rs",
        ".ts",
        ".tsx",
        ".js",
        ".mjs",
        ".cjs",
        ".md",
        ".mdx",
        ".txt",
        ".toml",
        ".sql",
        ".json",
        ".jsonc",
        ".jsonl",
        ".yml",
        ".yaml",
        ".bzl",
        ".bazel",
        ".lock",
    )
    return token.startswith(source_prefixes) or token.endswith(source_suffixes) or "*" in token


def append_index_candidates(candidates: list[str], value: str) -> None:
    if value.endswith((".ts", ".tsx", ".js", ".mjs", ".cjs", ".md", ".mdx", ".txt", ".json", ".jsonc")):
        return
    candidates.extend(
        [
            f"{value}.ts",
            f"{value}.tsx",
            f"{value}.md",
            f"{value}.mdx",
            f"{value}/index.ts",
            f"{value}/index.tsx",
            f"{value}/index.md",
            f"{value}/README.md",
        ]
    )


def add_surface_candidates(candidates: list[str], normalized: str) -> None:
    for root in SURFACE_SOURCE_ROOTS:
        candidates.append(f"{root}/{normalized}")
        append_index_candidates(candidates, f"{root}/{normalized}")


def add_refactor_candidates(candidates: list[str], normalized: str) -> None:
    aliases = {
        "packages/opencode/src/bus/bus-event.ts": "packages/core/src/event.ts",
        "packages/opencode/src/bus/index.ts": "packages/opencode/src/bus/global.ts",
        "packages/opencode/src/cli/cmd/tui/plugin/api.tsx": "packages/tui/src/plugin/api.ts",
        "packages/opencode/src/cli/cmd/tui/plugin/internal.ts": "packages/tui/src/plugin/adapters.tsx",
        "packages/opencode/src/cli/cmd/tui/plugin/runtime.ts": "packages/tui/src/plugin/runtime.tsx",
        "packages/opencode/src/config/provider.ts": "packages/core/src/config/provider.ts",
        "packages/opencode/src/config/mcp.ts": "packages/core/src/config/mcp.ts",
        "packages/opencode/src/config/permission.ts": "packages/core/src/permission.ts",
        "packages/opencode/src/config/skills.ts": "packages/core/src/config/plugin/skill.ts",
        "packages/opencode/src/control-plane/adaptors.ts": "packages/opencode/src/control-plane/adapters/index.ts",
        "packages/opencode/src/effect/observability.ts": "packages/core/src/observability.ts",
        "packages/opencode/src/global/index.ts": "packages/core/src/global.ts",
        "packages/opencode/src/permission/schema.ts": "packages/core/src/permission.ts",
        "packages/opencode/src/project/instance.ts": "packages/opencode/src/project/instance-runtime.ts",
        "packages/opencode/src/project/project.sql.ts": "packages/core/src/project/sql.ts",
        "packages/opencode/src/provider/models.ts": "packages/core/src/model.ts",
        "packages/opencode/src/provider/schema.ts": "packages/core/src/provider.ts",
        "packages/opencode/src/provider/sdk/copilot/index.ts": "packages/core/src/github-copilot/copilot-provider.ts",
        "packages/opencode/src/control-plane/workspace.sql.ts": "packages/core/src/control-plane/workspace.sql.ts",
        "packages/opencode/src/server/fence.ts": "packages/opencode/src/server/shared/fence.ts",
        "packages/opencode/src/server/routes/global.ts": "packages/opencode/src/server/routes/instance/httpapi/groups/global.ts",
        "packages/opencode/src/server/routes/instance/index.ts": "packages/opencode/src/server/routes/instance/httpapi/server.ts",
        "packages/opencode/src/server/routes/instance/trace.ts": "packages/opencode/src/server/routes/instance/httpapi/groups/event.ts",
        "packages/opencode/src/server/routes/control/workspace.ts": "packages/opencode/src/server/routes/instance/httpapi/groups/control-plane.ts",
        "packages/opencode/src/server/workspace.ts": "packages/opencode/src/control-plane/workspace.ts",
        "packages/opencode/src/session/session.sql.ts": "packages/core/src/session/sql.ts",
        "packages/opencode/src/share/index.ts": "packages/opencode/src/share/session.ts",
        "packages/opencode/src/share/share.sql.ts": "packages/core/src/session/sql.ts",
        "packages/opencode/src/storage/db.ts": "packages/core/src/database/database.ts",
        "packages/opencode/src/storage/json-migration.ts": "packages/core/src/data-migration.sql.ts",
        "packages/opencode/src/storage/schema.sql.ts": "packages/core/src/database/schema.sql.ts",
        "packages/opencode/src/sync/index.ts": "packages/opencode/src/sync/README.md",
        "packages/opencode/src/tool/bash.ts": "packages/opencode/src/tool/shell.ts",
        "packages/opencode/src/provider/sdk/copilot": "packages/core/src/github-copilot",
        "packages/desktop/src/entry.tsx": "packages/desktop/src/renderer/index.tsx",
        "packages/desktop/src/index.tsx": "packages/desktop/src/renderer/index.tsx",
        "packages/desktop-electron-live/electron/services/opencode-bridge.ts": "packages/desktop/src/main/server.ts",
        "specs/tui-plugins.md": "specs/tui-package.md",
        "src/v2/index.ts": "packages/sdk/js/src/v2/index.ts",
        "deno.json": "packages/opencode/parsers-config.ts",
        "registry.ts": "packages/opencode/src/tool/registry.ts",
        "project.sql.ts": "packages/core/src/project/sql.ts",
        "project.ts": "packages/core/src/project.ts",
        "message-v2.ts": "packages/core/src/session/message.ts",
        "compaction.ts": "packages/core/src/session/compaction.ts",
        "overflow.ts": "packages/opencode/src/session/overflow.ts",
        "transform.ts": "packages/opencode/src/provider/transform.ts",
        "run.ts": "packages/opencode/src/cli/cmd/run.ts",
        "serve.ts": "packages/opencode/src/cli/cmd/serve.ts",
        "instance.ts": "packages/opencode/src/project/instance-runtime.ts",
        "bootstrap.ts": "packages/opencode/src/project/bootstrap.ts",
        "storage/db.ts": "packages/core/src/database/database.ts",
        "share-next.ts": "packages/opencode/src/share/share-next.ts",
        "share.sql.ts": "packages/core/src/session/sql.ts",
        "server/routes/instance/session.ts": "packages/opencode/src/server/routes/instance/httpapi/groups/session.ts",
    }
    if normalized in aliases:
        candidates.append(aliases[normalized])

    if normalized.startswith("src/"):
        suffix = normalized.removeprefix("src/")
        candidates.append(f"{CURRENT_SOURCE_ROOT}/{suffix}")
        append_index_candidates(candidates, f"{CURRENT_SOURCE_ROOT}/{suffix}")
        return

    tui_old = "packages/opencode/src/cli/cmd/tui"
    if normalized == tui_old:
        candidates.extend(["packages/opencode/src/cli/cmd/tui.ts", "packages/tui/src"])
    if normalized.startswith(f"{tui_old}/"):
        suffix = normalized.removeprefix(f"{tui_old}/")
        candidates.append(f"packages/tui/src/{suffix}")
        append_index_candidates(candidates, f"packages/tui/src/{suffix}")

    if "/adaptors" in normalized:
        candidates.append(normalized.replace("/adaptors", "/adapters"))
    if normalized.startswith("packages/opencode/src/control-plane/adaptors/"):
        suffix = normalized.removeprefix("packages/opencode/src/control-plane/adaptors/")
        candidates.append(f"packages/opencode/src/control-plane/adapters/{suffix}")

    route_prefix = "packages/opencode/src/server/routes/instance/"
    if normalized.startswith(route_prefix):
        suffix = normalized.removeprefix(route_prefix)
        candidates.append(f"packages/opencode/src/server/routes/instance/httpapi/{suffix}")
        candidates.append(f"packages/opencode/src/server/routes/instance/httpapi/groups/{suffix}")
        candidates.append(f"packages/opencode/src/server/routes/instance/httpapi/handlers/{suffix}")

    if normalized.startswith("packages/opencode/src/session/prompt/"):
        filename = normalized.rsplit("/", 1)[-1]
        candidates.append(f"packages/opencode/src/agent/prompt/{filename}")
        candidates.append(f"packages/opencode/src/session/runner/{filename.removesuffix('.txt')}.ts")

    if normalized.endswith(".txt") and "/" not in normalized:
        candidates.append(f"packages/opencode/src/session/prompt/{normalized}")
        candidates.append(f"packages/opencode/src/agent/prompt/{normalized}")
        candidates.append(f"packages/opencode/src/tool/{normalized}")

    if normalized.startswith("packages/desktop-electron/"):
        suffix = normalized.removeprefix("packages/desktop-electron/")
        candidates.append(f"packages/desktop/{suffix}")
    if normalized == "packages/desktop-electron":
        candidates.append("packages/desktop")
    if normalized.startswith("packages/desktop-electron-live/electron/services/"):
        filename = normalized.rsplit("/", 1)[-1]
        candidates.append(f"packages/desktop/src/main/{filename.replace('opencode-', '').replace('sidecar', 'sidecar')}")

    if normalized.startswith("gen/"):
        suffix = normalized.removeprefix("gen/")
        candidates.append(f"packages/sdk/js/src/{suffix}")
        candidates.append(f"packages/sdk/js/src/gen/{suffix}")
        candidates.append(f"packages/sdk/js/src/v2/{suffix}")

    if normalized.startswith("specs/effect/"):
        suffix = normalized.removeprefix("specs/effect/")
        candidates.append(f"packages/opencode/specs/effect/{suffix}")

    provider_copilot_prefix = "packages/opencode/src/provider/sdk/copilot"
    if normalized.startswith(f"{provider_copilot_prefix}/"):
        suffix = normalized.removeprefix(f"{provider_copilot_prefix}/")
        candidates.append(f"packages/core/src/github-copilot/{suffix}")


def source_suffixes_for_exact_match() -> tuple[str, ...]:
    return (
        ".ts",
        ".tsx",
        ".js",
        ".mjs",
        ".cjs",
        ".md",
        ".mdx",
        ".txt",
        ".json",
        ".jsonc",
        ".toml",
        ".yaml",
        ".yml",
    )


def normalize_source_token(token: str) -> str | None:
    value = token.strip().strip(".,;:)")
    if not source_like(value):
        return None
    value = value.removeprefix("./")
    value = value.strip("'\"")
    if value.endswith("/..."):
        value = value[: -len("/...")]
    if value.endswith("/**"):
        value = value[: -len("/**")]
    if "*" in value:
        prefix = value[: value.find("*")].rstrip("/")
        value = prefix.rsplit("/", 1)[0] if "/" in prefix else prefix
    if value.endswith("/"):
        value = value.rstrip("/")
    if not value or value.startswith("/"):
        return None
    return value


def resolve_source(token: str) -> ResolvedSource | None:
    normalized = normalize_source_token(token)
    if normalized is None:
        return None

    candidates = [normalized]
    append_index_candidates(candidates, normalized)
    add_refactor_candidates(candidates, normalized)
    if not normalized.startswith(("packages/", ".opencode/", ".github/", "github/", "infra/", "script/", "sdks/", "specs/")):
        add_surface_candidates(candidates, normalized)

    if normalized.endswith(source_suffixes_for_exact_match()):
        base = normalized.rsplit(".", 1)[0]
        append_index_candidates(candidates, base)
        if not base.startswith(("packages/", ".opencode/", ".github/", "github/", "infra/", "script/", "sdks/", "specs/")):
            add_surface_candidates(candidates, base)

    for candidate in dict.fromkeys(candidates):
        if candidate in REPO_FILES:
            return ResolvedSource(path=candidate, kind="blob", original=normalized)
        if candidate in REPO_DIRS:
            return ResolvedSource(path=candidate, kind="tree", original=normalized)
    return None


def github_url(path: str, ref: str, kind: str = "blob") -> str:
    quoted = quote(path, safe="/")
    return f"{REPO_URL}/{kind}/{ref}/{quoted}"


def relative_href(current: Path, target: Path) -> str:
    current_dir = current.parent if current.name else current
    href = os.path.relpath(target.as_posix(), current_dir.as_posix() or ".")
    return href.replace(os.sep, "/")


def slug(value: str, fallback: str) -> str:
    base = re.sub(r"<[^>]+>", "", value)
    base = re.sub(r"`([^`]+)`", r"\1", base)
    base = re.sub(r"[^0-9A-Za-z가-힣_-]+", "-", base).strip("-").lower()
    return base or fallback


class MarkdownRenderer:
    def __init__(self, current_output: Path):
        self.current_output = current_output
        self.refs: dict[str, ResolvedSource] = {}
        self.corrections: dict[str, ResolvedSource] = {}
        self.unresolved: set[str] = set()
        self.heading_count = 0

    def render_inline(self, text: str) -> str:
        placeholders: list[tuple[str, str]] = []

        def code_repl(match: re.Match[str]) -> str:
            token = f"@@CODE{len(placeholders)}@@"
            placeholders.append((token, self.render_code_span(match.group(1))))
            return token

        without_code = re.sub(r"`([^`\n]+)`", code_repl, text)
        escaped = html.escape(without_code)
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)

        def link_repl(match: re.Match[str]) -> str:
            label = match.group(1)
            href = html.unescape(match.group(2))
            href = self.rewrite_markdown_href(href)
            return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

        escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, escaped)
        for token, rendered in placeholders:
            escaped = escaped.replace(token, rendered)
        return escaped

    def rewrite_markdown_href(self, href: str) -> str:
        if href.startswith(("./", "../")) and href.endswith(".md"):
            href_path = (self.current_output.parent / href).with_suffix(".html")
            return href_path.as_posix()
        return href

    def render_code_span(self, code: str) -> str:
        escaped = html.escape(code)
        resolved = resolve_source(code)
        if resolved:
            self.refs[resolved.path] = resolved
            if resolved.original != resolved.path:
                self.corrections[resolved.original] = resolved
            href = github_url(resolved.path, LATEST_REF, resolved.kind)
            return f'<a class="source-code" href="{html.escape(href, quote=True)}"><code>{escaped}</code></a>'
        if normalize_source_token(code) is not None:
            self.unresolved.add(code)
        return f"<code>{escaped}</code>"

    def is_block_start(self, line: str, next_line: str | None) -> bool:
        stripped = line.strip()
        return bool(
            stripped.startswith("```")
            or re.match(r"^#{1,6}\s+", stripped)
            or stripped.startswith(">")
            or re.match(r"^\s*[-*]\s+", line)
            or re.match(r"^\s*\d+\.\s+", line)
            or stripped == "---"
            or (stripped.startswith("|") and next_line and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", next_line))
        )

    def render(self, markdown: str) -> tuple[str, str]:
        lines = markdown.splitlines()
        output: list[str] = []
        page_title = "Untitled"
        skipped_first_h1 = False
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue

            if stripped.startswith("```"):
                language = stripped[3:].strip()
                code_lines: list[str] = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1
                code = "\n".join(code_lines)
                if language == "mermaid":
                    output.append(f'<div class="diagram"><pre class="mermaid">{html.escape(code)}</pre></div>')
                else:
                    lang_class = f' class="language-{html.escape(language)}"' if language else ""
                    output.append(f'<pre class="code-block"><code{lang_class}>{html.escape(code)}</code></pre>')
                continue

            heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if heading:
                level = len(heading.group(1))
                raw_title = heading.group(2).strip()
                if level == 1 and not skipped_first_h1:
                    page_title = re.sub(r"`([^`]+)`", r"\1", raw_title)
                    skipped_first_h1 = True
                    i += 1
                    continue
                self.heading_count += 1
                heading_id = slug(raw_title, f"section-{self.heading_count}")
                output.append(
                    f'<h{level} id="{html.escape(heading_id, quote=True)}">{self.render_inline(raw_title)}</h{level}>'
                )
                i += 1
                continue

            if stripped == "---":
                output.append("<hr />")
                i += 1
                continue

            if stripped.startswith(">"):
                quote_lines: list[str] = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote_lines.append(lines[i].strip().removeprefix(">").strip())
                    i += 1
                output.append(f'<blockquote><p>{" ".join(self.render_inline(line) for line in quote_lines)}</p></blockquote>')
                continue

            if stripped.startswith("|") and i + 1 < len(lines):
                separator = lines[i + 1].strip()
                if re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", separator):
                    table_lines: list[str] = []
                    while i < len(lines) and lines[i].strip().startswith("|"):
                        table_lines.append(lines[i].strip())
                        i += 1
                    output.append(self.render_table(table_lines))
                    continue

            if re.match(r"^\s*[-*]\s+", line):
                items: list[str] = []
                while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                    items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip())
                    i += 1
                output.append("<ul>" + "".join(f"<li>{self.render_inline(item)}</li>" for item in items) + "</ul>")
                continue

            if re.match(r"^\s*\d+\.\s+", line):
                items = []
                while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                    items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip())
                    i += 1
                output.append("<ol>" + "".join(f"<li>{self.render_inline(item)}</li>" for item in items) + "</ol>")
                continue

            paragraph: list[str] = [stripped]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_next = lines[i + 1] if i + 1 < len(lines) else None
                if not next_line.strip() or self.is_block_start(next_line, next_next):
                    break
                paragraph.append(next_line.strip())
                i += 1
            output.append(f"<p>{self.render_inline(' '.join(paragraph))}</p>")

        return "\n".join(output), page_title

    def render_table(self, rows: list[str]) -> str:
        parsed = [self.parse_table_row(row) for row in rows]
        header = parsed[0]
        body = parsed[2:]
        header_html = "".join(f"<th>{self.render_inline(cell)}</th>" for cell in header)
        body_html = []
        for row in body:
            cells = "".join(f"<td>{self.render_inline(cell)}</td>" for cell in row)
            body_html.append(f"<tr>{cells}</tr>")
        return f'<div class="table-wrap"><table><thead><tr>{header_html}</tr></thead><tbody>{"".join(body_html)}</tbody></table></div>'

    def parse_table_row(self, row: str) -> list[str]:
        row = row.strip().strip("|")
        return [cell.strip() for cell in row.split("|")]


def render_sidebar(entries: list[TocEntry], current: Path) -> str:
    groups: list[tuple[str, list[TocEntry]]] = []
    for entry in entries:
        if not groups or groups[-1][0] != entry.part:
            groups.append((entry.part, []))
        groups[-1][1].append(entry)

    parts_html = []
    for part, part_entries in groups:
        links = []
        for entry in part_entries:
            active = " active" if entry.output_path == current else ""
            href = relative_href(current, entry.output_path)
            links.append(f'<a class="toc-link{active}" href="{html.escape(href, quote=True)}">{html.escape(entry.title)}</a>')
        parts_html.append(
            f'<section class="toc-section"><h2>{html.escape(part)}</h2><div class="toc-links">{"".join(links)}</div></section>'
        )

    home_active = " active" if current == Path("index.html") else ""
    return f"""
<aside class="sidebar" aria-label="책 목차">
  <div class="brand">
    <p class="eyebrow">OpenCode Source Book</p>
    <a class="brand-title" href="{html.escape(relative_href(current, Path("index.html")), quote=True)}">OpenCode 에이전트 하니스 해부</a>
    <p class="brand-subtitle">책의 경계·상태·제어면 관점을 유지하되 현재 fork의 실제 소스 참조를 함께 제공합니다.</p>
  </div>
  <nav class="toc-nav">
    <a class="toc-link{home_active}" href="{html.escape(relative_href(current, Path("index.html")), quote=True)}">목차</a>
    {"".join(parts_html)}
  </nav>
  <div class="meta-panel">
    <p>Fork: <a href="{REPO_URL}">nfbs2000/speaky-opencode</a></p>
    <p>Latest source: <a href="{REPO_URL}/tree/{LATEST_REF}">{LATEST_REF}</a></p>
    <p>Edition snapshot: <a href="{REPO_URL}/tree/{EDITION_REF}">{EDITION_LABEL}</a></p>
  </div>
</aside>
"""


def page_shell(title: str, current: Path, body: str, entries: list[TocEntry]) -> str:
    css_href = relative_href(current, Path("assets/styles.css"))
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(title)} | OpenCode 에이전트 하니스 해부</title>
    <meta name="description" content="OpenCode 포크를 현재 소스와 함께 읽는 한국어 온라인 책" />
    <link rel="stylesheet" href="{html.escape(css_href, quote=True)}" />
  </head>
  <body>
    <div class="layout">
{render_sidebar(entries, current)}
      <main class="content">{body}</main>
    </div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{
        startOnLoad: true,
        theme: "base",
        themeVariables: {{
          background: "#fffefa",
          primaryColor: "#eef1ee",
          primaryTextColor: "#191817",
          primaryBorderColor: "#d9d1c3",
          lineColor: "#1f6f8b",
          secondaryColor: "#e9f1ee",
          tertiaryColor: "#f7efe5",
          fontFamily: "Inter, system-ui, sans-serif"
        }}
      }});
    </script>
  </body>
</html>
"""


def fork_correction_note() -> str:
    return f"""
<section class="fork-note">
  <h2>현재 fork 기준 보정</h2>
  <p>이 온라인판은 원고의 관점과 장 구성을 유지하지만, 현재 <code>speaky-opencode</code> 포크의 리팩터링을 기준으로 소스 경로를 보정합니다. 원고의 오래된 <code>src/...</code> 참조는 가능한 경우 <code>{CURRENT_SOURCE_ROOT}/...</code>로 해석합니다.</p>
  <p>현재 fork는 core runtime을 <code>packages/opencode/src/</code>에 두고, TUI는 <code>packages/tui/src/</code>, 웹 앱은 <code>packages/app/src/</code>, 데스크톱은 <code>packages/desktop/src/</code>, HTTP surface는 <code>packages/server/src/</code>와 <code>packages/opencode/src/server/routes/instance/httpapi/</code>에 나누어 둡니다.</p>
</section>
"""


def source_reference_section(renderer: MarkdownRenderer) -> str:
    resolved = sorted(renderer.refs.values(), key=lambda ref: ref.path)
    unresolved = sorted(renderer.unresolved)
    corrections = sorted(renderer.corrections.values(), key=lambda ref: (ref.original, ref.path))
    if not resolved and not unresolved and not corrections:
        return ""

    resolved_rows = []
    for ref in resolved:
        latest = github_url(ref.path, LATEST_REF, ref.kind)
        edition = github_url(ref.path, EDITION_REF, ref.kind)
        resolved_rows.append(
            "<tr>"
            f"<td><code>{html.escape(ref.path)}</code></td>"
            f'<td><a href="{html.escape(latest, quote=True)}">Latest</a></td>'
            f'<td><a href="{html.escape(edition, quote=True)}">Edition</a></td>'
            "</tr>"
        )

    unresolved_rows = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in unresolved)
    unresolved_html = (
        f"""
<details class="unresolved-refs">
  <summary>현재 fork에서 찾지 못한 참조 {len(unresolved)}개</summary>
  <p>이 경로들은 원고에 있지만 현재 <code>nfbs2000/speaky-opencode</code> snapshot에는 없어서 404 링크를 만들지 않았습니다.</p>
  <ul>{unresolved_rows}</ul>
</details>
"""
        if unresolved
        else ""
    )

    resolved_html = (
        f"""
<div class="table-wrap source-table">
  <table>
    <thead><tr><th>경로</th><th>Latest</th><th>Edition</th></tr></thead>
    <tbody>{"".join(resolved_rows)}</tbody>
  </table>
</div>
"""
        if resolved_rows
        else ""
    )

    correction_rows = []
    for ref in corrections:
        latest = github_url(ref.path, LATEST_REF, ref.kind)
        correction_rows.append(
            "<tr>"
            f"<td><code>{html.escape(ref.original)}</code></td>"
            f"<td><code>{html.escape(ref.path)}</code></td>"
            f'<td><a href="{html.escape(latest, quote=True)}">Latest</a></td>'
            "</tr>"
        )
    corrections_html = (
        f"""
<div class="table-wrap source-table">
  <table>
    <thead><tr><th>원고 경로</th><th>현재 fork 경로</th><th>링크</th></tr></thead>
    <tbody>{"".join(correction_rows)}</tbody>
  </table>
</div>
"""
        if correction_rows
        else ""
    )

    return f"""
<section class="source-references" id="source-references">
  <h2>이 장의 실제 소스 참조</h2>
  <p>본문의 코드 경로 중 현재 fork에 존재하는 항목만 실제 GitHub 소스로 연결했습니다. <code>Latest</code>는 <code>{LATEST_REF}</code>, <code>Edition</code>은 이 온라인판 생성 시점의 snapshot입니다.</p>
  {corrections_html}
  {resolved_html}
  {unresolved_html}
</section>
"""


def chapter_nav(entries: list[TocEntry], entry: TocEntry) -> str:
    index = entries.index(entry)
    prev_entry = entries[index - 1] if index > 0 else None
    next_entry = entries[index + 1] if index + 1 < len(entries) else None
    prev_html = (
        f'<a class="nav-card" href="{html.escape(relative_href(entry.output_path, prev_entry.output_path), quote=True)}"><span>이전</span><strong>{html.escape(prev_entry.title)}</strong></a>'
        if prev_entry
        else '<span class="nav-card disabled"><span>이전</span><strong>없음</strong></span>'
    )
    next_html = (
        f'<a class="nav-card" href="{html.escape(relative_href(entry.output_path, next_entry.output_path), quote=True)}"><span>다음</span><strong>{html.escape(next_entry.title)}</strong></a>'
        if next_entry
        else '<span class="nav-card disabled"><span>다음</span><strong>없음</strong></span>'
    )
    return f'<nav class="chapter-nav" aria-label="장 이동">{prev_html}{next_html}</nav>'


def render_chapter(entries: list[TocEntry], entry: TocEntry) -> None:
    markdown = (SRC_ROOT / entry.source_path).read_text(encoding="utf-8")
    renderer = MarkdownRenderer(entry.output_path)
    rendered, title = renderer.render(markdown)
    title = title if title != "Untitled" else entry.title
    body = f"""
<article class="book-page">
  <header class="chapter-header">
    <p class="eyebrow">{html.escape(entry.part)}</p>
    <h1>{html.escape(title)}</h1>
    <p class="chapter-meta">온라인판은 책의 질문과 해석 순서를 유지하면서 현재 fork의 실제 소스 경로와 링크를 함께 제공합니다.</p>
  </header>
  {fork_correction_note()}
  <div class="markdown-body">{rendered}</div>
  {source_reference_section(renderer)}
  {chapter_nav(entries, entry)}
</article>
"""
    output_path = BOOK_ROOT / entry.output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page_shell(title, entry.output_path, body, entries), encoding="utf-8")


def render_index(entries: list[TocEntry]) -> None:
    groups: list[tuple[str, list[TocEntry]]] = []
    for entry in entries:
        if not groups or groups[-1][0] != entry.part:
            groups.append((entry.part, []))
        groups[-1][1].append(entry)

    group_html = []
    for part, part_entries in groups:
        chapter_cards = []
        for entry in part_entries:
            href = relative_href(Path("index.html"), entry.output_path)
            chapter_cards.append(
                f'<a class="toc-card" href="{html.escape(href, quote=True)}"><span>{html.escape(part)}</span><strong>{html.escape(entry.title)}</strong></a>'
            )
        group_html.append(f'<section class="toc-group"><h2>{html.escape(part)}</h2><div class="toc-card-grid">{"".join(chapter_cards)}</div></section>')

    first_chapter = next((entry for entry in entries if "1장:" in entry.title), entries[0])
    body = f"""
<article class="cover-page">
  <header class="cover-hero">
    <p class="eyebrow">OpenCode Source Book</p>
    <h1>OpenCode 에이전트 하니스 해부</h1>
    <p>책의 경계·상태·제어면 관점은 유지하되, 현재 <code>speaky-opencode</code> 포크의 패키지 구조와 실제 소스 경로를 반영한 온라인판입니다.</p>
    <div class="cover-actions">
      <a class="primary-link" href="{html.escape(relative_href(Path("index.html"), first_chapter.output_path), quote=True)}">1장부터 읽기</a>
      <a class="secondary-link" href="{REPO_URL}">fork 소스 보기</a>
    </div>
  </header>
  <section class="edition-panel">
    <h2>온라인판 기준</h2>
    <p><strong>Latest</strong> 링크는 <code>{LATEST_REF}</code>를, <strong>Edition</strong> 링크는 <code>{EDITION_LABEL}</code> snapshot을 가리킵니다.</p>
    <p>원고 source는 이 repo의 <code>course/book-opencode/src</code> 아래에 포함되어 있고, 오래된 <code>src/...</code> 경로는 현재 <code>{CURRENT_SOURCE_ROOT}/...</code> 계층으로 보정됩니다.</p>
  </section>
  {fork_correction_note()}
  <section class="full-toc" id="toc">
    <h2>목차</h2>
    {"".join(group_html)}
  </section>
</article>
"""
    (BOOK_ROOT / "index.html").write_text(page_shell("목차", Path("index.html"), body, entries), encoding="utf-8")


def clean_generated() -> None:
    for html_file in BOOK_ROOT.glob("*.html"):
        html_file.unlink()
    for child in BOOK_ROOT.iterdir():
        if child.is_dir() and (child.name.startswith("part") or child.name == "appendix"):
            shutil.rmtree(child)


def main() -> None:
    if not SRC_ROOT.exists():
        raise SystemExit(f"source root not found: {SRC_ROOT}")
    entries = parse_summary()
    clean_generated()
    render_index(entries)
    for entry in entries:
        render_chapter(entries, entry)
    print(f"generated {len(entries) + 1} pages from {SRC_ROOT}")


if __name__ == "__main__":
    main()
