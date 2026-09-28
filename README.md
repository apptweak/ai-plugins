# AppTweak AI Plugins

The official [AppTweak](https://www.apptweak.com) plugin marketplace for AI assistants and coding agents. Each plugin bundles **Agent Skills** with a connection to a **hosted AppTweak MCP server**, and installs from this one repository into ChatGPT/Codex, Claude Code, Cursor, and GitHub Copilot.

## Available plugins

| Plugin | Use it to | Best for |
|---|---|---|
| **AppTweak Intelligence**<br>`apptweak-intelligence` | Ask questions and analyze apps, keywords, competitors, and markets using AppTweak data. | Marketers, ASO specialists, analysts: interactive research and analysis in conversation. |
| **AppTweak API**<br>`apptweak-api` | Explore the AppTweak API documentation and execute API requests from your coding agent. | Developers: building integrations, scripts, and automations on the AppTweak API. |

**Which one should I install?** If you want *answers* from AppTweak data, install **AppTweak Intelligence**. If you want to *build software* that uses the AppTweak API, install **AppTweak API**. You can install both; each plugin knows about the other and will point you to it when it's the better fit.

## Compatibility

Every client loads the same skills and the same MCP endpoint. The table shows which marketplace file each client reads, and whether it loads the plugin natively or through a thin adapter.

| Client | Marketplace file | Plugin package | Adapter | Status |
|---|---|---|---|---|
| OpenAI Codex CLI / ChatGPT desktop | `.agents/plugins/marketplace.json` | Agent Plugins 1.0 (native) | none | Tested with Codex CLI 0.154 |
| Claude Code (also Claude.ai / Cowork) | `.claude-plugin/marketplace.json` | Claude plugin | `.claude-plugin/plugin.json` | Tested with Claude Code 2.1.283 |
| Cursor | `.cursor-plugin/marketplace.json` | Agent Plugins 1.0 (native) | none | Per Cursor docs, not yet tested |
| GitHub Copilot CLI / VS Code | `.github/plugin/marketplace.json` | Agent Plugins 1.0 (native) | none | Per GitHub docs, not yet tested |

> **ChatGPT web and mobile:** OpenAI marks plugins that bundle MCP servers as *Desktop only*. Web and mobile availability requires registering the MCP server as a ChatGPT app. That is a future publishing step.

## Installation

### OpenAI Codex CLI

```sh
codex plugin marketplace add apptweak/ai-plugins
codex plugin list                                   # browse
codex plugin add apptweak-intelligence@apptweak
codex plugin add apptweak-api@apptweak
```

You can also run `/plugins` inside Codex to browse and install interactively. Start a new session after installing.

**ChatGPT (Business/Enterprise workspaces):** a workspace admin can import this repository under **Admin → Plugins → Add → Import marketplace**.

### Claude Code

Inside a session:

```
/plugin marketplace add apptweak/ai-plugins
/plugin install apptweak-intelligence@apptweak
/plugin install apptweak-api@apptweak
```

Or from the shell:

```sh
claude plugin marketplace add apptweak/ai-plugins
claude plugin install apptweak-intelligence@apptweak
claude plugin install apptweak-api@apptweak
```

Run `/plugin` to browse. On **Claude.ai / Claude Desktop / Cowork**, go to **Customize → Plugins → Add → Add marketplace** and enter `apptweak/ai-plugins`.

### GitHub Copilot CLI

```sh
copilot plugin marketplace add apptweak/ai-plugins
copilot plugin marketplace browse apptweak
copilot plugin install apptweak-intelligence@apptweak
copilot plugin install apptweak-api@apptweak
```

### VS Code (GitHub Copilot agent plugins)

Add the marketplace to your settings, then search `@agentPlugins` in the Extensions view:

```json
"chat.plugins.marketplaces": ["apptweak/ai-plugins"]
```

### Cursor

Cursor team marketplaces are managed from the dashboard and require a Teams or Enterprise plan:

1. Open the Cursor dashboard → **Plugins & MCPs** → **Add Marketplace**.
2. Choose **Import from Repo** and select `https://github.com/apptweak/ai-plugins`.
3. Team members can then install **AppTweak Intelligence** and/or **AppTweak API** from the marketplace panel.

## Authentication

Both plugins connect to hosted AppTweak MCP servers:

| Plugin | MCP endpoint |
|---|---|
| AppTweak Intelligence | `https://app.apptweak.com/mcp` |
| AppTweak API | `https://app.apptweak.com/api/mcp` |

You sign in with your AppTweak account through your client's standard MCP authentication flow, usually the first time a tool is used. This repository contains no API keys, tokens, or other credentials, and none are needed to install.

## Usage model

- **AppTweak Intelligence:** usage is tied to the individual AppTweak user and isn't shared across your company. Your available usage depends on your AppTweak subscription, and the allowance resets every 24 hours.
- **AppTweak API:** documentation search, reading, and navigation tools are free. Executing an API request consumes your company's normal AppTweak API credits for that request. API credits are shared company-wide and reset monthly.

---

## For maintainers

### Architecture

Each plugin is defined **once**, in the [Agent Plugins 1.0](https://agent-plugins.org/specification) format. Codex, Cursor, and Copilot load that format natively. Claude Code doesn't support it yet, so it gets one thin adapter manifest that points back at the canonical files.

```
.
├── .agents/plugins/marketplace.json     ADAPTER    OpenAI Codex / ChatGPT catalog
├── .claude-plugin/marketplace.json      ADAPTER    Claude catalog
├── .cursor-plugin/marketplace.json      ADAPTER    Cursor catalog
├── .github/plugin/marketplace.json      ADAPTER    GitHub Copilot catalog
├── .github/workflows/validate.yml                  CI
├── plugins/<plugin>/
│   ├── plugin.json                      CANONICAL  identity, metadata, OpenAI presentation (extensions.com.openai)
│   ├── mcp.json                         CANONICAL  the single remote MCP server
│   ├── skills/<skill>/SKILL.md          CANONICAL  shared by every client
│   ├── .claude-plugin/plugin.json       ADAPTER    Claude manifest; reuses ./mcp.json and ./skills
│   ├── assets/                                     logos (see the plugin README)
│   └── README.md
└── scripts/
    ├── validate.py                                 drift + consistency checks (stdlib only)
    └── schemas/agent-plugins-1.0.0/                pinned official JSON schemas
```

**Rule:** edit the canonical files first, then update the adapters to match. Never treat an adapter as the source of truth. `scripts/validate.py` fails when they disagree.

What an adapter may duplicate:
- **Marketplace catalogs:** plugin name, source path, short description, and version (where the format has one).
- **`.claude-plugin/plugin.json`:** name, displayName, version, description, author, homepage, repository, and keywords. It sets `"mcpServers": "./mcp.json"`, so there is no second MCP config.
- **Skills:** never duplicated.

Files deliberately **not** included:
- **`.codex-plugin/plugin.json`:** Codex prefers a root `plugin.json` with the Agent Plugins `$schema`, and the inline `extensions.com.openai` block replaces the legacy overlay.
- **`.cursor-plugin/plugin.json`:** Cursor loads Agent Plugins natively.
- **`.mcp.json`:** Claude Code loads the canonical `mcp.json` (`streamable-http` is an accepted alias for `http`).
- **`.app.json`:** this requires a real, registered ChatGPT app ID; see the TODOs below.

### Validation

```sh
python3 scripts/validate.py
```

The validator runs locally and in CI and needs Python 3.9+ with the standard library only; it makes no network calls. It checks:
- every JSON file parses;
- all four catalogs list exactly the plugins in `plugins/`, with valid sources;
- names, versions, descriptions, and metadata agree across the canonical manifests and adapters;
- manifests use the pinned Agent Plugins 1.0.0 schemas;
- each plugin has one `streamable-http` MCP server on `app.apptweak.com`, with no headers;
- the required guidance skill exists and skill frontmatter is valid;
- skill names don't collide;
- referenced paths exist;
- the repository contains no secrets.

CI (`.github/workflows/validate.yml`) also validates `plugins/*/plugin.json` and `plugins/*/mcp.json` against the pinned official schemas with `check-jsonschema`.

Optional local checks with vendor tools:

```sh
claude plugin validate . --strict
claude plugin validate plugins/apptweak-intelligence --strict
pipx run --spec skills-ref agentskills validate plugins/apptweak-api/skills/apptweak-api-guidance
```

### Adding a plugin

1. Create `plugins/<name>/` with `plugin.json`, `mcp.json`, `skills/<name>-guidance/SKILL.md`, `.claude-plugin/plugin.json`, and `README.md`. Copy an existing plugin as a template.
2. Add an entry for it to **all four** marketplace catalogs.
3. Update the plugin table in this README and the guidance skills of the other plugins.
4. Run `python3 scripts/validate.py`.

### Releasing a change

Bump `version` in `plugins/<name>/plugin.json` using semver, mirror it in `.claude-plugin/plugin.json` and the Cursor and Copilot catalogs, then run the validator.

### Open TODOs

- **Codex catalog categories:** `Productivity` and `Coding` are provisional, because OpenAI hasn't published the list of allowed values.
- **Public ChatGPT listing:** needs a registered ChatGPT app ID for each MCP server, referenced through `.app.json`. The privacy policy and terms URLs are already set in `extensions.com.openai.interface`.
- **Cursor and Copilot:** test installation end to end.
