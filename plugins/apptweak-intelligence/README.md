# AppTweak Intelligence

Ask questions and analyze apps, keywords, competitors, and markets using AppTweak data.

## Who it's for

This plugin is for people who want to **use AppTweak data through an AI assistant**: marketers, ASO specialists, analysts, and product and growth teams. You don't need technical skills. Typical requests:
- investigate an app;
- compare competitors;
- research keywords;
- explore a market;
- answer ASO questions.

The assistant pulls the AppTweak data it needs and reasons over it for you.

Want to **build software** on the AppTweak API instead? Use the sibling plugin [AppTweak API](../apptweak-api/).

## What's included

| Component | Details |
|---|---|
| MCP server `apptweak-intelligence` | `https://app.apptweak.com/mcp` (streamable HTTP). It offers many granular tools that return compact, LLM-oriented data for analysis in context. |
| Skill `apptweak-intelligence-guidance` | Explains how this plugin differs from AppTweak API. It lets the assistant suggest AppTweak API when a request is really about writing code. |

**Authentication:** you sign in with your AppTweak account through your client's MCP authentication flow. **Usage:** it's per user, depends on your subscription, and resets every 24 hours.

## Files

| File | Role |
|---|---|
| `plugin.json` | **Canonical.** Agent Plugins 1.0 manifest, including OpenAI presentation metadata (`extensions.com.openai`). |
| `mcp.json` | **Canonical.** The MCP server definition. |
| `skills/` | **Canonical.** Agent Skills shared by all clients. |
| `.claude-plugin/plugin.json` | **Adapter** for Claude Code. It mirrors the canonical metadata and points to `./mcp.json`. |
| `assets/` | Logo assets. |

## Logo assets

`assets/logo.png` is the final logo and uses the standard AppTweak branding. It is referenced from:
- `plugin.json` → `extensions.com.openai.interface.logo` and `composerIcon` (for OpenAI);
- `.cursor-plugin/marketplace.json` → the plugin entry's `"logo"` field (for Cursor).

To replace it, overwrite `assets/logo.png` and keep the same filename. If you rename it, update both references and run `python3 scripts/validate.py`, which checks that referenced files exist.
