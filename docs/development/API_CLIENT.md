# API Client

**External Repsotory:** `https://github.com/rensongroup/pyhaopenmotics`

Handles all communication with external APIs or devices. Implements:

- Async HTTP requests using `aiohttp`
- Connection management and timeouts
- Authentication handling
- Error translation to custom exceptions

**Key classes:** `OpenMoticsCloud` or `LocalGateway`

If you are modifying the pyhaopenmotics codebase, use the manifest.json file to link your local version for testing.
This avoids the need for incremental version releases during development:

replace this: ``json "requirements": [
"pyhaopenmotics@https://github.com/rensongroup/pyhaopenmotics/archive/refs/tags/0.0.11.tar.gz" ]

```

with

``json
"requirements": [
  "pyhaopenmotics@git+https://github.com/rensongroup/pyhaopenmotics.git@main#pyhaopenmotics==0.0.12"
]
```

## Schema Validation

JSON schema files are available in `/schemas/json/`:

- `manifest_schema.json` — Validates `manifest.json`

Consult the relevant schema when editing JSON files to ensure correct structure.
