---
applyTo: "custom_components/openmotics/coordinator/**/*.py"
---

# Instructions for AI Agent: OpenMotics Integration Development

## Context

When working within the `rensongroup/home-assistant` repository, pay special attention to the data orchestration layer,
primarily located in `coordinator.py`. This integration supports both cloud-based and local-network communication with
OpenMotics/Renson systems.

## Coordinator Implementation

The integration uses the `OpenMoticsDataUpdateCoordinator` to manage data fetching. Whenever you are reading, modifying,
or generating code related to entity updates, you **must** account for the underlying API client being used.

### Underlying Difference

While the coordinator interface is consistent, **the underlying API clients differ:**

- **The `_omclient` property:** The coordinator initializes an `_omclient` tailored for either the Renson/OpenMotics
  REST Cloud API (`OpenMoticsCloud`) or local gateway communication (`LocalGateway`).

## Guidelines for Code Generation

When generating code (such as adding new entities, creating tests, or modifying data fetching logic), you must adhere to
the following rules:

1. **Identify the Target Architecture:** Before writing code, determine if the entity or feature you are working on is
   intended for the Cloud integration, the Local integration, or both.
2. **Handle `_omclient` Methods Carefully:** Do not assume that a method available on the Cloud `_omclient` is available
   on the Local `_omclient`, or vice-versa. Always verify the respective client's SDK methods.
3. **Data Parsing:** Because the underlying `_omclient`s fetch data from different sources (Cloud API vs. Local
   Gateway), the JSON payload or object structure returned by `coordinator.data` might differ. Your data extraction
   logic inside entity classes (e.g., inside `@property def state(self):`) must handle the data structure specific to
   the coordinator variant being passed to it.
4. **Testing & Mocking:** When generating `pytest` code, ensure you mock the correct `_omclient`. If testing a local
   setup, mock the local client; if testing cloud, mock the cloud client. Do not mix their return values.

### Example Scenario

If you are asked to implement a new `sensor.py` that reads the temperature:

- Check if the sensor is receiving data from the Cloud or Local coordinator.
- Ensure that when the sensor looks up `self.coordinator.data`, it references the correct dictionary keys associated
  with that specific `_omclient`'s payload.
