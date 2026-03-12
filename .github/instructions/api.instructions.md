---
applyTo: "custom_components/**/coordinator.py"
---

# API and Coordinator Instructions

**Applies to:** coordinator implementation files

## Three-Layer Architecture (CRITICAL)

**Entities → Coordinator → API Client** - Never skip layers

- **Entities:** Read `coordinator.data` only, never call API
- **Coordinator:** Calls API, transforms data, handles errors/timing
- **API Client:** HTTP communication, auth, exception translation

The API Client is an external package: [PyHAOpenmotics](https://github.com/rensongroup/pyhaopenmotics)

## Exception Hierarchy (REQUIRED)

Defined in `pyhaopenmotics/__init__.py`:

- `OpenMoticsError` (Base)
- `OpenMoticsConnectionSslError` (SSL errors)
- `OpenMoticsConnectionError` (Network, HTTP errors)
- `OpenMoticsConnectionTimeoutError` (timeout errors)
- `AuthenticationError` (401, 403, invalid credentials)

**Mapping:** HTTP 401/403 → Auth, HTTP 429 → RateLimit, Timeout/ClientError → Communication

## Coordinator Exception Mapping

Map API exceptions to Home Assistant exceptions in `_async_update_data()`:

| API Exception         | Coordinator Exception          | Home Assistant Behavior |
| --------------------- | ------------------------------ | ----------------------- |
| `AuthenticationError` | `ConfigEntryAuthFailed`        | Triggers reauth flow    |
| `CommunicationError`  | `UpdateFailed("message")`      | Retry with backoff      |
| `RateLimitError`      | `UpdateFailed(retry_after=60)` | Wait before retry       |

**Import from:** `homeassistant.exceptions.ConfigEntryAuthFailed`,
`homeassistant.helpers.update_coordinator.UpdateFailed`

**Logging:** Pass error message to exception constructor. **Do NOT log** setup/update failures manually - HA handles it
automatically. Normal operation logging (debug/info) is still appropriate.

See [Integration Setup Failures](https://developers.home-assistant.io/docs/integration_setup_failures).

## Data Transformation (Coordinator Responsibility)

**Pattern:** `_async_update_data()` fetches raw API data, transforms to simple dict for entities

**Goal:** Entities read `coordinator.data["<entity>"]`

Possible entity types: `sensors`, `switches`, `lights`, `climate`, etc. `

## Update Interval

**Set in coordinator:** `super().__init__(hass, LOGGER, name="...", update_interval=timedelta(seconds=30))`

**Guidelines:** Environmental sensors (30-60s), Energy (10-30s), Status (60-300s), Slow data (5-15min)

## Context-Based Fetching (Optional)

**Only when:** API has separate endpoints and fetching all is expensive

**Pattern:** `self.async_contexts()` returns active entities, conditionally fetch based on entity types

**Default:** Simpler to fetch all data unless performance issue

## Common Mistakes

**❌ Don't:**

- Create `aiohttp.ClientSession()` in API client
- Call API directly from entities
- Catch `TimeoutError`/`ClientError` in coordinator (base class handles)
- Return transformed data from API client
- Implement retry logic in API client (coordinator does this)

**✅ Do:**

- Accept session parameter
- Translate all exceptions to integration-specific types
- Transform data in coordinator
- Use specific exception types for different failures
- Let coordinator handle retries and timing

## Reference

[Home Assistant: Fetching Data](https://developers.home-assistant.io/docs/integration_fetching_data)
