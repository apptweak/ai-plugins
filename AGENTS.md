# AGENTS.md

This file is for AI agents and maintainers working in this repository. Read the "For maintainers" section of `README.md` for the full architecture.

## What this repo is

This is the official AppTweak plugin marketplace (`apptweak`). It contains two plugins, `apptweak-intelligence` and `apptweak-api`. Each plugin is one **Agent Plugins 1.0** package: skills plus one remote MCP server. Four vendor catalogs expose the packages to Codex/ChatGPT, Claude, Cursor, and GitHub Copilot. The repo holds JSON and Markdown, plus one standard-library Python validator. There is no build step.

## Hard rules

- **Never modify, move, delete, or commit anything in `context/`.** It holds example marketplaces from other vendors, for reference only, and it is git-ignored.
- **Canonical files are the source of truth:** `plugins/*/plugin.json`, `plugins/*/mcp.json`, and `plugins/*/skills/**`. Everything else is an adapter that mirrors them. Change the canonical file first, then update the adapters.
- **Never duplicate skills per client.** All clients read the same `skills/<name>/SKILL.md`.
- **Never add a second MCP config** (such as `.mcp.json`) unless a client provably needs it. If you add one, it must match `mcp.json`, and the validator enforces this.
- **No secrets or `headers` in MCP configs.** Clients handle authentication through their MCP auth flow.
- **Don't invent metadata:** no support emails, ChatGPT app IDs (`.app.json`), licenses, or logos. The privacy policy and terms URLs are the official AppTweak ones already set in each `plugin.json`; don't change them without confirmation. Leave them as documented TODOs. Logos live in `plugins/<plugin>/assets/logo.png` and are provided by AppTweak.
- **Don't add frameworks, package managers, or build tooling.**
- **Run `python3 scripts/validate.py` before you finish any change.** It must print `OK`.

## Format facts (verified 2026-09)

- **Agent Plugins 1.0** (https://agent-plugins.org):
  - `plugin.json` is a closed schema. Allowed keys: `$schema`, `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `extensions`.
  - `mcp.json` needs an explicit `type`. For remote servers use `"streamable-http"`, never `"http"`.
  - The pinned schemas live in `scripts/schemas/agent-plugins-1.0.0/`.
- **Agent Skills** (https://agentskills.io):
  - Frontmatter keys: `name` (must equal the directory name), `description` (1024 characters or fewer), and optionally `license`, `compatibility`, `metadata`, `allowed-tools`.
  - Don't add client-only keys such as `disable-model-invocation`.
- **Client-specific metadata** goes under `extensions.<reverse-domain>`, for example `extensions.com.openai.interface`. The spec doesn't allow new top-level keys.
- **OpenAI `category`** must be one of the Title Case values used in OpenAI's curated catalog (github.com/openai/plugins): `Developer Tools`, `Productivity`, `Creativity`, `Communication`, `Education & Research`, `Data & Analytics`, `Finance`, `Security`, `Business & Operations`, `Scientific Research`. Keep `extensions.com.openai.interface.category` and the `.agents/plugins/marketplace.json` entry identical.
- **Claude Code** doesn't read the Agent Plugins manifest. `.claude-plugin/plugin.json` must keep `"mcpServers": "./mcp.json"`.
- **Plugin and skill names:** lowercase kebab-case. Skill names must be unique across plugins, which is why each plugin uses the `<plugin>-guidance` pattern.

## Conventions

- **Versions:** use semver, starting at `0.1.0`. On a release, bump the version in `plugin.json` and mirror it in `.claude-plugin/plugin.json` and the Cursor and Copilot catalogs.
- **Skills** are written for agents: imperative and specific, with the exact MCP tool names they depend on. Keep `SKILL.md` under about 500 lines, and put long reference material in `skills/<name>/references/`. Skills must stay client-neutral, so no client-specific install commands.
- **Cross-plugin guidance:** each plugin's `*-guidance` skill describes **both** plugins. When you add or change a plugin, update every guidance skill.
- **Docs:** update the root README plugin table and the per-plugin `README.md` whenever the user-facing behaviour changes.
- **Commits:** keep them small and focused, formatted `<plugin-name>: <change>` or `marketplace: <change>`. Don't commit unless asked.
