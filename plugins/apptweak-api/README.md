# AppTweak API

Explore the AppTweak API documentation and execute API requests from your coding agent.

## Who it's for

This plugin is for **developers building software on the AppTweak API**: integrations, scripts, data pipelines, and automations. Your coding agent can:
- search and read the API documentation;
- find the right endpoint;
- explain parameters and API behavior;
- run real requests while you write and debug code.

Just want *answers* from AppTweak data, without writing code? Use the sibling plugin [AppTweak Intelligence](../apptweak-intelligence/).

## What's included

| Component | Details |
|---|---|
| MCP server `apptweak-api` | `https://app.apptweak.com/api/mcp` (streamable HTTP). It offers a small set of developer tools: documentation search and reading, endpoint discovery, and API request execution. |
| Skill `apptweak-api-guidance` | Explains how this plugin differs from AppTweak Intelligence. It lets the assistant suggest AppTweak Intelligence for purely analytical questions. |

**Authentication:** you sign in with your AppTweak account through your client's MCP authentication flow. **Usage:** documentation tools are free. Executing an API request consumes your company's normal AppTweak API credits, which are shared company-wide and reset monthly.

## Files

| File | Role |
|---|---|
| `plugin.json` | **Canonical.** Agent Plugins 1.0 manifest, including OpenAI presentation metadata (`extensions.com.openai`). |
| `mcp.json` | **Canonical.** The MCP server definition. |
| `skills/` | **Canonical.** Agent Skills shared by all clients. |
| `.claude-plugin/plugin.json` | **Adapter** for Claude Code. It mirrors the canonical metadata and points to `./mcp.json`. |
| `assets/` | Logo assets. |

## Logo assets

`assets/logo.png` is the final logo: the blue developer/API variant of the AppTweak branding. It is referenced from:
- `plugin.json` → `extensions.com.openai.interface.logo` and `composerIcon` (for OpenAI);
- `.cursor-plugin/marketplace.json` → the plugin entry's `"logo"` field (for Cursor).

To replace it, overwrite `assets/logo.png` and keep the same filename. If you rename it, update both references and run `python3 scripts/validate.py`, which checks that referenced files exist.
