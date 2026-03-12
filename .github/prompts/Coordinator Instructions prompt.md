---
agent: "agent"
tools: ["search/codebase", "search", "problems", "runCommands", "runCommands/terminalLastCommand"]
description: "instructions for the coordinator logics"
---

# Instructions for AI Agent: OpenMotics Integration Development

## Context

When working within the `rensongroup/home-assistant` repository, pay special attention to the data orchestration layer, primarily located in `coordinator.py`. This integration supports both cloud-based and local-network communication with OpenMotics/Renson systems.

## CRITICAL: The Two Coordinator Variants

There are two distinct variants of the DataUpdateCoordinator used in this integration. Whenever you are reading, modifying, or generating code related to entity updates, you **must** account for which coordinator is being used:

1. **`OpenMoticsCloudDataUpdateCoordinator`**
2. **`OpenMoticsLocalDataUpdateCoordinator`**

### Structural Similarity vs. Underlying Difference

Both coordinators inherit from Home Assistant's `DataUpdateCoordinator` and look structurally identical in how they interface with Home Assistant entities. However, **they possess fundamentally different underlying API clients.**

* **The `_omclient` property:** Each coordinator initializes a different instance type for its `_omclient`.
  * The Cloud coordinator uses an `_omclient` tailored for the Renson/OpenMotics REST Cloud API.
  * The Local coordinator uses an `_omclient` tailored for local gateway communication (Local API).

## Guidelines for Code Generation

When generating code (such as adding new entities, creating tests, or modifying data fetching logic), you must adhere to the following rules:

1. **Identify the Target Architecture:** Before writing code, determine if the entity or feature you are working on is intended for the Cloud integration, the Local integration, or both.
2. **Handle `_omclient` Methods Carefully:** Do not assume that a method available on the Cloud `_omclient` is available on the Local `_omclient`, or vice-versa. Always verify the respective client's SDK methods.
3. **Data Parsing:** Because the underlying `_omclient`s fetch data from different sources (Cloud API vs. Local Gateway), the JSON payload or object structure returned by `coordinator.data` might differ. Your data extraction logic inside entity classes (e.g., inside `@property def state(self):`) must handle the data structure specific to the coordinator variant being passed to it.
4. **Testing & Mocking:** When generating `pytest` code, ensure you mock the correct `_omclient`. If testing a local setup, mock the local client; if testing cloud, mock the cloud client. Do not mix their return values.

### Example Scenario

If you are asked to implement a new `sensor.py` that reads the temperature:
* Check if the sensor receives `OpenMoticsCloudDataUpdateCoordinator` or `OpenMoticsLocalDataUpdateCoordinator`.
* Ensure that when the sensor looks up `self.coordinator.data`, it references the correct dictionary keys associated with that specific `_omclient`'s payload.
