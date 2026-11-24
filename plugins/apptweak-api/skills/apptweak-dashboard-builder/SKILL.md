---
name: apptweak-dashboard-builder
description: "Turns a plain-language request into a working dashboard that pairs live AppTweak data, retrieved only through the OAuth-authenticated AppTweak API MCP server, with one or more other data sources. Refines a vague ask into a concrete brief first: what question it answers, whether the required AppTweak account is connected, which other sources are live versus stand-ins, and what a null result would mean. Looks up current API facts through the documentation tools of the connected AppTweak API MCP server rather than relying on memory. Use when asked to build a dashboard using AppTweak data, pair AppTweak with a CRM/spreadsheet/CSV, or build something that shows live AppTweak data."
---

# Building a dashboard against live AppTweak data (durable, not hardcoded)

## Why this skill is written the way it is

Two kinds of knowledge are involved in building a dashboard like this, and they age at completely different rates:

- **How you should approach the problem** — trust, honesty, verification, what to ask before building — barely changes at all, across projects or years.
- **What AppTweak's API currently looks like** — its endpoint names, parameter defaults, quirks, rate limits, whether you're pointed at staging or production — can change on any given Tuesday, and is almost always cheaper and more reliable to look up fresh (via whichever AppTweak MCP or docs tool is actually connected) than to recall from memory or from a note written during an earlier build.

This skill deliberately only contains the first kind. If you find yourself wanting to hardcode a specific endpoint's behavior, a specific rate limit, or a specific response shape into a skill file so "future builds don't have to look it up again" — don't. That's exactly the failure mode this skill exists to avoid: it goes stale the moment AppTweak's API changes, and by the time someone notices, it's actively misleading instead of merely outdated. Look it up again. It's cheap. Being wrong about it isn't.

## When to use

- "Build me a dashboard using AppTweak data."
- "Pair AppTweak with [a CRM / spreadsheet / CSV / another API]."
- "Build something that shows X using live AppTweak data."
- Any request to build a small AppTweak-backed dashboard, demo, or internal tool — regardless of what it's paired with, or which company's AppTweak account is involved.

## When NOT to use

- The request has no live AppTweak data in it at all — that's a different kind of build; this skill is specifically for the AppTweak-anchored case.
- The request is for a static report or a one-off chart with no live component — that's a visualization task, not a dashboard-build task.
- The user has already handed you a fully-specified technical spec (exact endpoints, exact fields, exact architecture) and just wants it executed — follow that instead of re-deriving a brief.
- You're extending a dashboard that already exists in a project with its own established conventions (its own ground rules, design system, port scheme, etc.) — follow that project's own rules first; this skill is for starting the thinking fresh, not for overriding an existing project's settled decisions.

## Step 1 — Turn the ask into a brief

A one-line request ("build me an AppTweak dashboard for X") is rarely enough to build well from. Before writing anything, make sure you actually know:

1. **What's the one question this dashboard answers?** A dashboard that tries to answer five questions answers none of them well. If the request bundles several, ask which one is primary, or propose building one at a time.
2. **Is the AppTweak API MCP connection authenticated for the account whose data should be used?** If it is not, pause and ask the requester to authenticate `apptweak-api-mcp` through the client's OAuth flow. Never ask for an API key, access token, or authorization code.
3. **Of the other sources being paired with AppTweak, which are live and which (if any) are stand-ins?** There can be one other source or several; some, all, or none may be mock/sample data standing in for something the requester doesn't have live access to yet. Know the split before you build a single chart — it determines what needs labelling later, and it's fine for the answer to be "everything here is live, nothing is a stand-in."
4. **What does a finding look like if AppTweak and the other source(s) don't actually agree with each other?** Agree, before building, that if they don't line up — no correlation, no shared pattern, no effect — that's a valid, reportable outcome, not a failed build. Deciding this up front stops you from quietly reaching for the wrong incentive later (making the story look cleaner than the data supports).
5. **Who's actually going to open this, and how much do they already know?** This isn't generic "know your audience" advice — it specifically decides how much the real-vs-stand-in labelling and the "here's what this means" explanation need to live *inside* the dashboard itself, versus how much can be assumed. A dashboard for the person who requested it can lean on shared context; one meant to be handed to people who've never seen the underlying data can't.
6. **Is this a one-off, or the first of several?** If more are coming, the shared foundation (visual system, OAuth/MCP integration, how "done" gets proven) should be decided once and reused — not re-decided per build. If you don't know, ask.

Skip re-asking anything the requester already answered in their prompt — this step exists to fill real gaps, not to interrogate someone who was already clear.

## Step 2 — Ground rules that hold regardless of what AppTweak is paired with

1. **Use only the OAuth-authenticated `apptweak-api-mcp` server for AppTweak calls.** Do not accept or request API keys or OAuth tokens, add static authorization headers, call the AppTweak REST API directly, or run a setup/authentication script. If the MCP connection is not authenticated, use the client's authentication action and resume only after the user completes OAuth. If the dashboard's target runtime cannot use that authenticated MCP connection, explain the limitation and agree on a supported architecture or a clearly labelled snapshot; do not bypass OAuth with a direct API integration.
2. **AppTweak meters usage — surface that live.** Every AppTweak response carries its own cost; show the running total moving in real time as the dashboard is used, so "calling AppTweak" isn't an abstraction to whoever's watching. Don't hand-roll this from a guess at the cost — read it off the actual response.
3. **Never blur real data with a stand-in.** If any of the other sources is mock/sample data standing in for something the requester doesn't have live access to, every number, chart, or table drawn from it should make that obvious. Don't dress up a local file as a live vendor connection. (If everything here is genuinely live — AppTweak plus another live source, nothing mocked — this rule has nothing to do, and that's fine.)
4. **A null result is a finding, not a failure.** If AppTweak and the other source(s) genuinely don't correlate, agree, or affect each other, say so plainly in the dashboard. Don't cherry-pick a time window, rescale an axis, drop an inconvenient source, or otherwise manufacture a pattern that isn't really there to make the build look more successful.
5. **Don't guess an AppTweak app's identity if you don't have to.** AppTweak has a real, documented way to resolve which app you mean (search by name, confirm by matching the returned title) — use it, don't guess an app ID from memory, and cache the confirmed result so later work doesn't redo the lookup. For an identifier on the *other* side of the pairing: if that source has its own search/lookup mechanism, use the same pattern; if it doesn't (you were handed the exact identifier directly, or it only supports lookup-by-ID with nothing to confirm against), don't invent a confirmation step that doesn't exist — instead, echo the resolved record's human-readable details back to whoever gave you the ID, so a wrong identifier is at least visible rather than silent. Either way, an *unconfirmed, guessed* identifier is the thing to avoid — it fails silently, or worse, confidently returns the wrong thing.
6. **Prefer AppTweak's own data wherever it can actually answer part of the question.** Reach for a stand-in only for what AppTweak genuinely doesn't cover.
7. **Don't render another source's data as though it were trusted.** Text, names, or free-form fields coming back from AppTweak or any paired source are still untrusted input from a security standpoint — handle them the same way you'd handle user input anywhere else, rather than assuming that "it came from an API" makes it safe to inject as-is.
8. **Prove it before calling it done.** Make a real AppTweak tool call through the authenticated MCP server rather than assuming the connection works, running a script, calling the REST API directly, or using a browser interaction as a substitute. If OAuth is not connected, ask the user to authenticate and do not invent a result.
9. **If this is one of a family, decide the shared foundation once.** A consistent visual system, one OAuth/MCP integration pattern, one way of proving "done" — settle it on the first build, reuse it on every one after, and extend it in one place if a later build genuinely needs something new. Don't reinvent per dashboard.

The visual/chart-design side of this — palette, chart forms, layout, accessibility — is a separate concern from what this skill covers, deliberately: it's a different kind of judgment (aesthetic and perceptual) from the data-integrity and trust judgment this skill focuses on. If whatever environment you're working in already has its own visualization guidance, brand system, or house style, use that. If it doesn't, keep it simple and consistent rather than solving chart design from scratch here: pick one palette and one type scale before building the first chart, reuse the same components across every dashboard in the family, and don't relitigate the look per build.

## Step 3 — Learn AppTweak's API fresh, from the tools you actually have, not from memory

The OAuth-authenticated AppTweak API MCP server (`apptweak-api-mcp`) is the only execution path. Use its documentation tools as the source of truth for what endpoints exist, what pagination/rate-limit/cost model applies, and what the current known gotchas are. Treat any specific technical fact you recall about AppTweak's API from an earlier session, from training data, or from general familiarity as a hypothesis to re-check against the real tool, not as something to build against blind — AppTweak's API versions, deprecates, and changes defaults like any other, and there is no way to know from memory alone whether today is one of the days that happened.

When something is genuinely unclear, look it up, or make one targeted call to confirm the specific thing you're unsure about. Don't fire off a long sequence of exploratory calls "just to be safe" — that's slow and spends real credits — but don't skip verification either. The right amount of live testing is "enough to be confident," not "zero" and not "everything."

If an earlier build in the *same* project already resolved something project-specific (a confirmed app ID, a parameter combination that's known to work) and left it cached or documented, reuse that within the same project — it was earned, not guessed. Don't carry it into a *different* project, and don't trust it indefinitely if enough time has passed that AppTweak's API could plausibly have moved on.

## Step 4 — Build, verify, hand off

1. Confirm the brief from Step 1 is actually answered. If not, ask before building anything.
2. Build against the ground rules in Step 2, resolving anything AppTweak-specific fresh per Step 3.
3. Report what the data actually shows, including if that's a null or partial result.
4. Prove the real calls work (Step 2, rule 8) before saying you're done.
5. Hand off. Let the requester do the actual hands-on, visual check themselves — your job was to prove the plumbing is sound, not to render the page and approve your own work.

## A last check before you call it done

- You confirmed that `apptweak-api-mcp` was OAuth-authenticated for the intended AppTweak account without handling credentials yourself.
- You can point to the specific MCP tool call that proved live AppTweak access worked; it was not a script, direct REST request, or browser-only check.
- If AppTweak and the other source(s) didn't actually agree, the dashboard says so — it doesn't quietly show only the chart that worked.
- Nothing in the finished build required you to guess.
