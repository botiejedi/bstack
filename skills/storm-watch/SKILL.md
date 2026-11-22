---
name: storm-watch
description: Monitor official storm alerts with confirmed watch rules.
version: 0.1.0
author: botiejedi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Weather, Alerts, Storms, Monitoring, Safety]
    related_skills: [maps, grounded-citations]
---

# Storm Watch

Monitor severe-weather alerts using a confirmed location and watch contract. This skill supports on-demand checks and explicitly approved routines; it does not assume location, silently create alert delivery, or replace emergency services.

## When to Use

Use for:

- severe-weather, thunderstorm, tornado, flood, winter, tropical, dust, wind, or fire-weather watches;
- checking whether an official alert is active for a confirmed location;
- comparing current alerts with the last successful check;
- designing a recurring storm-watch routine after the user approves the contract.

Do not use for general climate analysis, seasonal forecasting, or an unscoped “watch the weather” request.

## Watch Contract

Confirm all fields before creating a routine:

1. **Locations:** human-readable label plus verified coordinates or official forecast zone.
2. **Timezone:** used for all displayed times and quiet-hour logic.
3. **Hazards:** exact events to include, such as tornado, severe thunderstorm, flash flood, winter storm, tropical cyclone, dust storm, high wind, or fire weather.
4. **Threshold:** event types and minimum official severity, certainty, or urgency.
5. **Cadence:** normal polling interval and whether imminent conditions justify a shorter interval.
6. **Quiet hours:** whether critical warnings may override them.
7. **Delivery:** exact platform, chat or thread, and whether all-clear or only-change messages are wanted.
8. **Escalation wording:** what counts as informational, prepare, or act-now, grounded in official instructions.

Do not infer missing values from IP address, timezone, or stale memory. Done when the contract can deterministically accept or reject an alert and route a test message.

## Source Hierarchy

For United States locations:

1. NWS active alerts and forecast endpoints at `api.weather.gov`.
2. The responsible NWS Weather Forecast Office and official alert page.
3. NOAA or specialized official centers when relevant, such as the Storm Prediction Center or National Hurricane Center.
4. State, tribal, territorial, county, or municipal emergency-management sources for local instructions.

Outside the United States, identify the official national meteorological service and local emergency authority before monitoring. Commercial or community weather sources may add context but cannot override an official alert.

The NWS API is public and no-key, but requires a descriptive `User-Agent`. Use a privacy-safe value such as `Hermes-Storm-Watch/0.1`; do not put the user's real name, address, or email in request headers.

## One-Shot Check

1. Use `terminal` to obtain the live time in the confirmed timezone.
2. If coordinates are not already confirmed, load `maps`, geocode the supplied place, show the resolved locality without exposing unnecessary precision, and obtain user confirmation before saving it.
3. For a confirmed U.S. point, request `https://api.weather.gov/points/{lat},{lon}` to obtain the responsible forecast office, grid, county or zone, and forecast links.
4. Request active alerts for the confirmed point or official zone. Use the required `User-Agent` and an appropriate GeoJSON or JSON accept header.
5. Parse only needed fields: stable alert ID, event, headline, severity, certainty, urgency, status, message type, effective, onset, expires or ends, area description, instruction, sender, and official URL.
6. Compare with the last successful state and classify each item as new, materially updated, unchanged, cancelled, or expired.
7. Query the relevant official forecast or specialist center only when it changes the user's hazard decision.
8. Update saved alert state only after every required source completed successfully. A partial run cannot advance the all-clear baseline.

Done when the output names the coverage time, official sources reached, active alerts, changes, and any unknown layer.

## Change and Deduplication Rules

- Use the official alert identifier as the primary identity.
- Treat a changed severity, certainty, urgency, instruction, affected area, onset, or expiry as material.
- Do not resend unchanged alerts unless the contract requests periodic reminders.
- Preserve cancellation and expiry as state transitions, not as new hazards.
- Collapse duplicate official representations of the same alert but retain links to authoritative updates.
- If no qualifying alert is active, say “no qualifying active alert was returned by the successfully checked sources,” not “you are safe.”

## Output Contract

Return:

1. **Coverage:** location label, timezone, checked-at time, and sources reached.
2. **Status:** new or changed qualifying alerts first.
3. **Official details:** event, severity, certainty, urgency, onset or effective time, expiry, affected area, and official instructions.
4. **Changes:** what differs from the prior successful check.
5. **Unknowns:** unavailable or partial sources.
6. **Safety boundary:** follow official emergency alerts and local authorities for immediate danger.

Keep raw API dumps and precise coordinates out of ordinary chat unless needed for diagnosis.

## Routine Creation

Create a `cronjob` only after the user explicitly confirms the complete watch contract and delivery destination.

The job prompt must be self-contained and include:

- confirmed location or official zone;
- timezone and quiet hours;
- hazard filters and thresholds;
- source hierarchy and required headers;
- state file path;
- change-only and outage behavior;
- delivery target and a successful test requirement;
- instruction to remain silent when no reportable change exists, if requested.

Do not promise delivery until a real test reaches the chosen channel. CLI-local routine output is not an external alert channel.

## Persistent Files

Store under `$HERMES_HOME/storm-watch/`:

- `watch-contract.json`: confirmed settings and delivery contract;
- `alert-state.json`: last successful official alert state;
- `source-health.json`: last success or failure per required source.

Do not save transient forecasts to personal memory. Save only stable user preferences or corrections.

## Pitfalls

- Assuming timezone identifies location.
- Treating a watch, warning, advisory, and emergency as interchangeable.
- Advancing state after a source outage.
- Repeating unchanged alerts until the channel becomes noise.
- Using a commercial forecast as the sole life-safety source.
- Interpreting a radar image beyond official text.
- Adding contact details to an API User-Agent without approval.
- Creating a routine before location, threshold, cadence, and delivery are confirmed.

## Verification

- [ ] Location and timezone are explicitly confirmed.
- [ ] NWS or the applicable official authority is reachable.
- [ ] Required fields parse without exposing unrelated data.
- [ ] New, updated, cancelled, expired, and unchanged states classify correctly.
- [ ] A failed source remains an unknown, not an all-clear.
- [ ] No routine or delivery exists without explicit confirmation.
- [ ] Any configured delivery passed a real end-to-end test.
