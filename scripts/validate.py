#!/usr/bin/env python3
"""Validate the AppTweak plugin marketplace.

Checks that the canonical Agent Plugins 1.0 packages under plugins/ are
well-formed and that every vendor adapter (marketplace catalogs, Claude
manifests) stays in sync with them. Standard library only; no network.

Usage: python3 scripts/validate.py
Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"

# Hosts that AppTweak MCP servers may live on. A typo in a URL fails here.
ALLOWED_MCP_HOSTS = {"app.apptweak.com"}

# Marketplace catalogs, one per client ecosystem.
MARKETPLACES = {
    "openai": ROOT / ".agents/plugins/marketplace.json",
    "claude": ROOT / ".claude-plugin/marketplace.json",
    "cursor": ROOT / ".cursor-plugin/marketplace.json",
    "copilot": ROOT / ".github/plugin/marketplace.json",
}
MARKETPLACE_NAME = "apptweak"

# Allowed keys, from the pinned schemas in scripts/schemas/ and the Agent Skills spec.
PLUGIN_KEYS = {"$schema", "name", "version", "description", "author", "homepage",
               "repository", "license", "keywords", "extensions"}
AUTHOR_KEYS = {"name", "email", "url"}
SKILL_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

PLUGIN_NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME_RE = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

# Metadata that the Claude adapter duplicates and must keep identical.
CLAUDE_SYNCED_KEYS = ("name", "version", "description", "author", "homepage",
                      "repository", "keywords")

SECRET_PATTERNS = [
    (re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{8,}"), "bearer token"),
    (re.compile(r"(?i)\"authorization\"\s*:"), "Authorization header"),
    (re.compile(r"(?i)\"[^\"]*(api[_-]?key|token|secret|password)[^\"]*\"\s*:\s*\"[^\"]+\""),
     "credential-like field with a value"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "OpenAI-style secret key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
]
SKIP_DIRS = {".git", "context", "__pycache__", "node_modules"}
TEXT_SUFFIXES = {".json", ".md", ".yml", ".yaml", ".py", ".svg", ".txt", ".toml"}

errors: list[str] = []


def error(where: Path | str, message: str) -> None:
    where = where.relative_to(ROOT) if isinstance(where, Path) else where
    errors.append(f"{where}: {message}")


def iter_files():
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        error(path, "file is missing")
    except json.JSONDecodeError as exc:
        error(path, f"invalid JSON: {exc}")
    return None


def check_relative_path(plugin_dir: Path, value: str, where: Path, field: str) -> None:
    if not value.startswith("./"):
        error(where, f"{field} must be a ./-relative path, got {value!r}")
        return
    target = (plugin_dir / value).resolve()
    if plugin_dir.resolve() not in (target, *target.parents):
        error(where, f"{field} escapes the plugin root: {value!r}")
    elif not target.exists():
        error(where, f"{field} points to a missing file: {value!r}")


def check_interface_paths(plugin_dir: Path, manifest: Path, interface: dict) -> None:
    for field in ("logo", "composerIcon"):
        if field in interface:
            check_relative_path(plugin_dir, interface[field], manifest, f"interface.{field}")
    for i, shot in enumerate(interface.get("screenshots", [])):
        check_relative_path(plugin_dir, shot, manifest, f"interface.screenshots[{i}]")


def check_canonical_plugin(plugin_dir: Path) -> dict | None:
    path = plugin_dir / "plugin.json"
    manifest = load_json(path)
    if not isinstance(manifest, dict):
        return None
    if manifest.get("$schema") != PLUGIN_SCHEMA:
        error(path, f"$schema must be {PLUGIN_SCHEMA}")
    for key in sorted(set(manifest) - PLUGIN_KEYS):
        error(path, f"unknown top-level key {key!r} (Agent Plugins 1.0 manifests are closed)")
    name = manifest.get("name")
    if name != plugin_dir.name:
        error(path, f"name {name!r} must match directory name {plugin_dir.name!r}")
    if not isinstance(name, str) or len(name) > 64 or not PLUGIN_NAME_RE.match(name):
        error(path, f"name {name!r} is not a valid Agent Plugins name")
    for key in ("version", "description"):
        if not isinstance(manifest.get(key), str) or not manifest[key]:
            error(path, f"{key} is required by this repository")
    author = manifest.get("author", {})
    if not isinstance(author, dict) or set(author) - AUTHOR_KEYS:
        error(path, "author must be an object with only name/email/url")
    extensions = manifest.get("extensions", {})
    if not isinstance(extensions, dict) or not all(isinstance(v, dict) for v in extensions.values()):
        error(path, "extensions must map namespaces to objects")
    else:
        openai = extensions.get("com.openai", {})
        if "apps" in openai:
            check_relative_path(plugin_dir, openai["apps"], path, "extensions.com.openai.apps")
        check_interface_paths(plugin_dir, path, openai.get("interface", {}))
    return manifest


def check_mcp_servers(path: Path, servers) -> dict[str, str]:
    """Validate a mcpServers map and return {server name: url}."""
    urls: dict[str, str] = {}
    if not isinstance(servers, dict) or not servers:
        error(path, "mcpServers must be a non-empty object")
        return urls
    for server_name, server in servers.items():
        where = f"mcpServers.{server_name}"
        if not isinstance(server, dict):
            error(path, f"{where} must be an object")
            continue
        if "headers" in server:
            error(path, f"{where} must not declare headers; auth is handled by the client")
        url = server.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_MCP_HOSTS:
            error(path, f"{where}.url {url!r} must be https on {sorted(ALLOWED_MCP_HOSTS)}")
        urls[server_name] = url
    return urls


def check_canonical_mcp(plugin_dir: Path) -> dict[str, str]:
    path = plugin_dir / "mcp.json"
    config = load_json(path)
    if not isinstance(config, dict):
        return {}
    if config.get("$schema") != MCP_SCHEMA:
        error(path, f"$schema must be {MCP_SCHEMA}")
    for key in sorted(set(config) - {"$schema", "mcpServers"}):
        error(path, f"unknown top-level key {key!r}")
    servers = config.get("mcpServers")
    urls = check_mcp_servers(path, servers)
    for server_name, server in (servers or {}).items():
        if isinstance(server, dict):
            if server.get("type") != "streamable-http":
                error(path, f"mcpServers.{server_name}.type must be 'streamable-http'")
            for key in sorted(set(server) - {"type", "url", "headers"}):
                error(path, f"mcpServers.{server_name} has unknown key {key!r}")
    if len(urls) != 1:
        error(path, "each AppTweak plugin must declare exactly one MCP server")
    if plugin_dir.name not in urls:
        error(path, f"MCP server should be named after the plugin ({plugin_dir.name!r})")
    return urls


def check_claude_adapter(plugin_dir: Path, canonical: dict, mcp_urls: dict[str, str]) -> None:
    path = plugin_dir / ".claude-plugin/plugin.json"
    adapter = load_json(path)
    if not isinstance(adapter, dict):
        return
    for key in CLAUDE_SYNCED_KEYS:
        if adapter.get(key) != canonical.get(key):
            error(path, f"{key} differs from canonical plugin.json")
    display = canonical.get("extensions", {}).get("com.openai", {}).get("interface", {}).get("displayName")
    if display and adapter.get("displayName") != display:
        error(path, "displayName differs from extensions.com.openai.interface.displayName")
    if adapter.get("mcpServers") != "./mcp.json":
        error(path, "mcpServers must be './mcp.json' so Claude reuses the canonical MCP config")

    # Optional fallback file; Claude Code also auto-loads it.
    legacy = plugin_dir / ".mcp.json"
    if legacy.exists():
        config = load_json(legacy)
        if isinstance(config, dict):
            legacy_urls = check_mcp_servers(legacy, config.get("mcpServers"))
            if legacy_urls != mcp_urls:
                error(legacy, f"servers {legacy_urls} differ from mcp.json {mcp_urls}")


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        error(path, "missing YAML frontmatter")
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue  # nested values (e.g. metadata) are not inspected
        key, sep, value = line.partition(":")
        if not sep:
            error(path, f"unparseable frontmatter line: {line!r}")
            continue
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def check_skills(plugin_dir: Path, seen: dict[str, Path]) -> None:
    skills_dir = plugin_dir / "skills"
    expected = f"{plugin_dir.name}-guidance"
    if not (skills_dir / expected / "SKILL.md").is_file():
        error(plugin_dir, f"missing required skill skills/{expected}/SKILL.md")
    for skill_dir in sorted(p for p in skills_dir.glob("*") if p.is_dir()):
        path = skill_dir / "SKILL.md"
        if not path.is_file():
            error(skill_dir, "skill directory has no SKILL.md")
            continue
        fields = parse_frontmatter(path)
        if fields is None:
            continue
        for key in sorted(set(fields) - SKILL_KEYS):
            error(path, f"frontmatter key {key!r} is not in the Agent Skills spec")
        name = fields.get("name", "")
        if name != skill_dir.name:
            error(path, f"name {name!r} must match directory name {skill_dir.name!r}")
        if len(name) > 64 or not SKILL_NAME_RE.match(name):
            error(path, f"name {name!r} is not a valid Agent Skills name")
        if not 1 <= len(fields.get("description", "")) <= 1024:
            error(path, "description must be 1-1024 characters")
        if name in seen:
            error(path, f"skill name {name!r} collides with {seen[name].relative_to(ROOT)}")
        seen[name] = path


def check_marketplaces(plugins: dict[str, dict]) -> None:
    expected = set(plugins)
    for client, path in MARKETPLACES.items():
        catalog = load_json(path)
        if not isinstance(catalog, dict):
            continue
        if catalog.get("name") != MARKETPLACE_NAME:
            error(path, f"marketplace name must be {MARKETPLACE_NAME!r}")
        entries = catalog.get("plugins", [])
        names = [e.get("name") for e in entries]
        if len(names) != len(set(names)):
            error(path, "duplicate plugin entries")
        if set(names) != expected:
            error(path, f"lists {sorted(names)} but plugins/ contains {sorted(expected)}")
        for entry in entries:
            name = entry.get("name")
            source = entry.get("source")
            if isinstance(source, dict):
                source = source.get("path")
            if not isinstance(source, str):
                error(path, f"{name}: unsupported source {entry.get('source')!r}")
                continue
            if (ROOT / source).resolve() != (PLUGINS_DIR / str(name)).resolve():
                error(path, f"{name}: source {source!r} must point to plugins/{name}")
            logo = entry.get("logo")
            if isinstance(logo, str) and not urlparse(logo).scheme:
                logo_path = (ROOT / logo).resolve()
                plugin_root = (PLUGINS_DIR / str(name)).resolve()
                if plugin_root not in logo_path.parents or not logo_path.is_file():
                    error(path, f"{name}: logo {logo!r} must be an existing file inside plugins/{name}")
            canonical = plugins.get(name)
            if canonical is None:
                continue
            for key in ("version", "description"):
                if key in entry and entry[key] != canonical.get(key):
                    error(path, f"{name}: {key} differs from canonical plugin.json")
            if "keywords" in entry and entry["keywords"] != canonical.get("keywords"):
                error(path, f"{name}: keywords differ from canonical plugin.json")
            if client == "openai":
                policy = entry.get("policy", {})
                if not {"installation", "authentication"} <= set(policy) or "category" not in entry:
                    error(path, f"{name}: OpenAI entries need policy.installation, "
                                "policy.authentication and category")
                interface = canonical.get("extensions", {}).get("com.openai", {}).get("interface", {})
                if interface.get("category") not in (None, entry.get("category")):
                    error(path, f"{name}: category differs from extensions.com.openai.interface")


def check_secrets() -> None:
    for path in iter_files():
        if path.suffix not in TEXT_SUFFIXES or path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                error(f"{path.relative_to(ROOT)}:{line}", f"possible secret ({label})")


def main() -> int:
    for path in iter_files():
        if path.suffix == ".json":
            load_json(path)

    plugins: dict[str, dict] = {}
    seen_skills: dict[str, Path] = {}
    plugin_dirs = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())
    if not plugin_dirs:
        error(PLUGINS_DIR, "no plugins found")
    for plugin_dir in plugin_dirs:
        canonical = check_canonical_plugin(plugin_dir)
        mcp_urls = check_canonical_mcp(plugin_dir)
        if canonical is not None:
            plugins[plugin_dir.name] = canonical
            check_claude_adapter(plugin_dir, canonical, mcp_urls)
        check_skills(plugin_dir, seen_skills)

    check_marketplaces(plugins)
    check_secrets()

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for message in errors:
            print(f"  - {message}")
        return 1
    print(f"OK: {len(plugins)} plugin(s), {len(seen_skills)} skill(s), "
          f"{len(MARKETPLACES)} marketplace catalog(s) in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
