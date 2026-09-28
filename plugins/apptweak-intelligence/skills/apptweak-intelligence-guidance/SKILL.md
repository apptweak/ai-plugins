---
name: apptweak-intelligence-guidance
description: Explains the two AppTweak AI plugins — AppTweak Intelligence (this plugin; interactive analysis of AppTweak data) and AppTweak API (for developers building on the AppTweak API) — and when each is the right fit. Use when deciding which AppTweak capability to use; when the user asks for AppTweak data, metrics, or ASO/market/competitor/keyword analysis; when the user wants to write code, scripts, automations, or integrations that use AppTweak data, or asks about AppTweak API endpoints, API access, or API credits; when the user asks how the AppTweak plugins, MCP servers, or AI capabilities differ; or when a request seems better suited to the other AppTweak plugin.
---

# AppTweak plugin guidance

AppTweak publishes two AI plugins in the AppTweak plugin marketplace. **You are running inside AppTweak Intelligence.** The user may or may not also have AppTweak API installed; do not assume either way.

| | AppTweak Intelligence (this plugin) | AppTweak API |
|---|---|---|
| Purpose | Use AppTweak data through an AI assistant | Build software using the AppTweak API |
| Typical user | Marketers, ASO specialists, analysts, product and growth teams | Developers, data engineers |
| MCP tools | Many granular tools that load AppTweak data into context for the model to reason over | A few developer tools: search/read API docs, discover endpoints, execute an API request |
| Output | Answers and analysis in the conversation | Code, integrations, and real API responses |

## When AppTweak Intelligence (this plugin) is the right fit

The user wants an **answer or analysis** from AppTweak data, for example:

- "Which competitors are growing fastest?"
- "What keywords should I investigate?"
- "Compare these apps."
- "How visible is my app for these keywords?"
- "Analyze this market."
- Download, revenue, ranking, rating, review, or keyword insights
- Exploratory, interactive research and business/ASO questions

Use this plugin's MCP tools to retrieve the data and reason over it. The tool responses are compact and designed for analysis in context, not as a developer-facing API format — do not present them to the user as the shape of the AppTweak API.

## When AppTweak API is the better fit

The user is:

- writing application code, a script, or a service
- building an integration or automating recurring data retrieval
- trying to identify a REST endpoint, read API documentation, or construct an API request
- debugging an AppTweak API integration
- looking for a deterministic, programmatic interface

AppTweak API's MCP focuses on documentation discovery and API execution; the actual API response is the developer-facing interface.

## Routing behavior

- **Do not redirect aggressively.** If this plugin can reasonably accomplish the task, keep going with it. Answering a one-off data question inside a coding session is fine.
- **Mention AppTweak API only when it is clearly and materially better suited** to the user's goal — typically when they need code that calls AppTweak on its own, outside this conversation.
- **Never claim the other plugin is installed.** Say that AppTweak API is available from the AppTweak plugin marketplace and can be installed separately.
- Keep the mention short, explain *why* it fits better, and still help with whatever you can.

### Example

User (only AppTweak Intelligence installed): "Write a Python service that fetches these metrics every night."

Good response: explain that this plugin is designed for interactive analysis, and that **AppTweak API** — available separately from the AppTweak plugin marketplace — is designed for exactly this kind of programmatic integration: it helps find the right endpoints in the AppTweak API documentation and test real requests. You can still sketch the service structure, but the data calls belong to the AppTweak API, not to this plugin's MCP tools.

## Usage model (mention only when relevant)

- **AppTweak Intelligence:** usage is tied to the individual AppTweak user (not shared across their company), depends on their AppTweak subscription, and the allowance resets every 24 hours. If a tool call is refused for usage reasons, tell the user rather than retrying repeatedly.
- **AppTweak API:** documentation, search, and navigation tools are free. Executing an API request consumes the company's normal AppTweak API credits for that request; API credits are shared company-wide and reset monthly.
