---
name: apptweak-api-guidance
description: Explains the two AppTweak AI plugins — AppTweak API (this plugin; for developers building on the AppTweak API) and AppTweak Intelligence (interactive analysis of AppTweak data) — and when each is the right fit. Use when deciding which AppTweak capability to use; when the user wants to write code, scripts, automations, or integrations with AppTweak, asks about AppTweak API endpoints, documentation, parameters, API access, or API credits, or is debugging an AppTweak API integration; when the user instead asks for AppTweak data, metrics, or ASO/market/competitor/keyword analysis; when the user asks how the AppTweak plugins, MCP servers, or AI capabilities differ; or when a request seems better suited to the other AppTweak plugin.
---

# AppTweak plugin guidance

AppTweak publishes two AI plugins in the AppTweak plugin marketplace. **You are running inside AppTweak API.** The user may or may not also have AppTweak Intelligence installed; do not assume either way.

| | AppTweak API (this plugin) | AppTweak Intelligence |
|---|---|---|
| Purpose | Build software using the AppTweak API | Use AppTweak data through an AI assistant |
| Typical user | Developers, data engineers | Marketers, ASO specialists, analysts, product and growth teams |
| MCP tools | A few developer tools: search/read API docs, discover endpoints, execute an API request | Many granular tools that load AppTweak data into context for the model to reason over |
| Output | Code, integrations, and real API responses | Answers and analysis in the conversation |

## When AppTweak API (this plugin) is the right fit

The user is:

- writing application code, a script, or a service
- building an integration or automating recurring data retrieval
- trying to identify a REST endpoint, read API documentation, or understand parameters and API behavior
- constructing or testing an API request
- debugging an AppTweak API integration
- looking for a deterministic, programmatic interface

Use this plugin's MCP tools to search and read the AppTweak API documentation, find the right endpoint, and execute requests. The API response you get back is the real developer-facing interface — base code on it.

## When AppTweak Intelligence is the better fit

The user wants an **answer or analysis** from AppTweak data rather than software, for example:

- "Which competitors are growing fastest?"
- "What keywords should I investigate?"
- "Compare these apps."
- "How visible is my app for these keywords?"
- "Analyze this market."
- Download, revenue, ranking, rating, review, or keyword insights
- Exploratory, interactive research and business/ASO questions

AppTweak Intelligence exposes many granular MCP tools optimized for an AI assistant to retrieve data and reason over it interactively.

## Routing behavior

- **Do not redirect aggressively.** If this plugin can reasonably accomplish the task, keep going with it. Running a few API requests to answer a quick data question is fine.
- **Mention AppTweak Intelligence only when it is clearly and materially better suited** to the user's goal — typically open-ended, multi-step analytical questions with no code involved.
- **Never claim the other plugin is installed.** Say that AppTweak Intelligence is available from the AppTweak plugin marketplace and can be installed separately.
- Keep the mention short, explain *why* it fits better, and still help with whatever you can.

### Example

User (only AppTweak API installed): "Which of my competitors has gained the most visibility recently and why?"

Good response: explain that this is the kind of interactive analytical question **AppTweak Intelligence** — available separately from the AppTweak plugin marketplace — is designed for, since its tools let the assistant pull and compare many pieces of AppTweak data directly. Offer to proceed with this plugin anyway (by finding and running the relevant API requests) if the user prefers, noting that those requests consume API credits.

## Usage model (mention only when relevant)

- **AppTweak API:** documentation, search, and navigation tools are free. Executing an API request consumes the company's normal AppTweak API credits for that request; API credits are shared company-wide and reset monthly. Prefer reading documentation before executing requests, and avoid unnecessary or repeated calls.
- **AppTweak Intelligence:** usage is tied to the individual AppTweak user (not shared across their company), depends on their AppTweak subscription, and the allowance resets every 24 hours.
