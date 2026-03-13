## Renson Smart Living (OpenMotics) Home Assistant integration

[![GitHub Release][releases-shield]][releases] [![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs] ![Project Maintenance][maintenance-shield]

<!--
Uncomment and customize these badges if you want to use them:

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![Discord][discord-shield]][discord]
-->

**✨ Develop in the cloud:** Want to contribute or customize this integration? Open it directly in GitHub Codespaces -
no local setup required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/woutercoppens/home-assistant-test?quickstart=1)

## Introduction

This custom component is developed for controlling an [OpenMotics](https://renson.net/nl-be/producten/smart-living)
platform by using the pyHAopenmotics sdk.

## Minimum Requirements

Requires a minimum of HA 2025.12. This is needed to support the new functionality and changes to config flow. Requires
the new pyHAopenmotics v0.0.11 (or newer) sdk.

## ✨ Features

- **Easy Setup**: Simple configuration through the UI - no YAML required
- **Smart Control**: Adjust light brightness, fan speed, target humidity, etc
- **Diagnostic Info**: View filter life, runtime hours, and device statistics
- **Reconfigurable**: Change credentials anytime without removing the integration
- **Options Flow**: Adjust settings like update interval after setup

**This integration will set up the following platforms.**

| Platform  | Description                                         |
| --------- | --------------------------------------------------- |
| `climate` | Temperature control                                 |
| `switch`  | LED display controls and others                     |
| `cover`   | Open and close blinds                               |
| `light`   | Control your lights (on/off, brightness, ...)       |
| `sensor`  | Air quality index (AQI), Temperature, Humidity, ... |
| `scene`   | Activate a scene                                    |

## 🚀 HOW TO INSTALL

See [GETTING_STARTED.md](/docs/user/GETTING_STARTED.md)

## Troubleshooting

### Authentication Issues

#### Reauthentication

If your credentials expire or change, Home Assistant will automatically prompt you to reauthenticate:

1. Go to **Settings** → **Devices & Services**
2. Look for **"Action Required"** or **"Configuration Required"** message on the integration
3. Click **"Reconfigure"** or follow the prompt
4. Enter your updated credentials
5. Click Submit

The integration will automatically resume normal operation with the new credentials.

#### Manual Credential Update

You can also update credentials at any time without waiting for an error:

1. Go to **Settings** → **Devices & Services**
2. Find **OpenMotics Home Assistant integration Beta**
3. Click the **3 dots menu** → **Reconfigure**
4. Enter new credentials
5. Click Submit

### Enable Debug Logging

To enable debug logging for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.openmotics: debug
```

### Common Issues

#### Authentication Errors

If you receive authentication errors:

1. Verify your username and password are correct
2. Check that your account has the necessary permissions
3. Wait for the automatic reauthentication prompt, or manually reconfigure
4. Check the API Connection binary sensor for status

#### Device Not Responding

If your device is not responding:

1. Check your network connection
2. Verify the device is powered on
3. Check the integration diagnostics (Settings → Devices & Services → OpenMotics → 3 dots → Download diagnostics)

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

### 🛠️ Development Setup

Want to contribute or customize this integration? You have two options:

#### Cloud Development (Recommended)

The easiest way to get started - develop directly in your browser with GitHub Codespaces:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/woutercoppens/home-assistant-test?quickstart=1)

- ✅ Zero local setup required
- ✅ Pre-configured development environment
- ✅ Home Assistant included for testing
- ✅ 60 hours/month free for personal accounts

#### Local Development

Prefer working on your machine? You'll need:

- Docker Desktop
- VS Code with the
  [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Then:

1. Clone this repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted

Both options give you the same fully-configured development environment with Home Assistant, Python 3.13, and all
necessary tools.

---

## 🤖 AI-Assisted Development

> **ℹ️ Transparency Notice**
>
> This integration was developed with assistance from AI coding agents (GitHub Copilot, Claude, and others). While the
> codebase follows Home Assistant Core standards, AI-generated code may not be reviewed or tested to the same extent as
> manually written code.
>
> AI tools were used to:
>
> - Generate boilerplate code following Home Assistant patterns
> - Implement standard integration features (config flow, coordinator, entities)
> - Ensure code quality and type safety
> - Write documentation and comments
>
> Please be aware that AI-assisted development may result in unexpected behavior or edge cases that haven't been
> thoroughly tested. If you encounter any issues, please [open an issue](../../issues) on GitHub.
>
> _Note: This section can be removed or modified if AI assistance was not used in your integration's development._

---

## 📄 License

This project is licensed under the AGPLv3 License - see the [LICENSE.md](LICENSE.md) file for details

---

Special thanks to @woutercoppens for making this plugin and donating it to Renson.

**Made with ❤️ by [@woutercoppens][user_profile]**

---

# Run, Play

**_Run, Play_** and let us know if there are any bugs, enhancements etc via the github issues system

This plugin is a community effort and OpenMotics cannot give any warranties even though you can report any issues and
we'll help as much as possible. Pull requests are always welcome.

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/rensongroup/home-assistant.svg?style=for-the-badge
[commits]: https://github.com/rensongroup/home-assistant/commits/master
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/rensongroup/home-assistant.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40woutercoppens-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/wrensongroup/home-assistant.svg?style=for-the-badge
[releases]: https://github.com/rensongroup/home-assistant/releases
[user_profile]: https://github.com/woutercoppens
