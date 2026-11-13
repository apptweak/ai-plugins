# AppTweak API

Explore the AppTweak API documentation and execute API requests from your coding agent.

## Who it's for

This plugin is for **developers building software on the AppTweak API**: integrations, scripts, data pipelines, and automations. Your coding agent can:
- search and read the API documentation;
- find the right endpoint;
- explain parameters and API behavior;
- run real requests while you write and debug code;
- build a dashboard that pairs live AppTweak data with other sources, such as a CRM, a spreadsheet, or another API.

Just want *answers* from AppTweak data, without writing code? Use the sibling plugin [AppTweak](../apptweak/).

## What's included

| Component | Details |
|---|---|
| MCP server `apptweak-api-mcp` (AppTweak API MCP) | `https://app.apptweak.com/api/mcp` (streamable HTTP). It offers a small set of developer tools: documentation search and reading, endpoint discovery, and API request execution. |
| Skill `apptweak-api-guidance` | Explains how this plugin differs from the AppTweak plugin. It lets the assistant suggest the AppTweak plugin for purely analytical questions. |
| Skill `apptweak-dashboard-builder` | Guides the assistant through building a dashboard on live AppTweak data: it turns the request into a brief, keeps real data apart from stand-ins, reports a null result as a finding, and proves the live calls work before handing off. AppTweak calls go only through the OAuth-authenticated `apptweak-api-mcp` server. |

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

`assets/logo.png` is the final logo: the developer/API variant of the AppTweak branding. It is referenced from:
- `plugin.json` → `extensions.com.openai.interface.logo` and `composerIcon` (for OpenAI);
- `.cursor-plugin/marketplace.json` → the plugin entry's `"logo"` field (for Cursor).

To replace it, overwrite `assets/logo.png` and keep the same filename. If you rename it, update both references and run `python3 scripts/validate.py`, which checks that referenced files exist.
