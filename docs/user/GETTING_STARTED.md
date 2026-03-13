# Getting Started with OpenMotics Home Assistant integration

This guide will help you install and set up the OpenMotics Home Assistant integration custom integration for Home
Assistant.

## Prerequisites

- Home Assistant 2025.12.0 or newer
- HACS (Home Assistant Community Store) installed
- Network connectivity to [external service/device]

## Preparation

Before you can us this integration, you need to create a client_id and client_secret.

Login to [cloud.renson.eu](https://cloud.renson.eu/)

![login](/docs/pictures/login.cloud.renson.eu.png)

Remember to use your e-mail address as login.

Make sure your installation is at a recent firmware. Update if needed.

![firmware](/docs/pictures/update01.png)

Create an additional user

![user01](/docs/pictures/user01.png)

![user02](/docs/pictures/user02.png)

![user03](/docs/pictures/user03.png)

![user04](/docs/pictures/user04.png)

Make sure the Client type is `Confidential` and the Grant type is `Client credentials`. The Redirect URI is not used
right now and can have any value.

![user05](/docs/pictures/user05.png)

Make sure to store the client secret somewhere now, as this is the only moment where you'll be able to see it!

![user06](/docs/pictures/user06.png)

Copy the Client ID as you'll need it to configure the integration in Home Assistant.

Note: if you loose the client secret (or you didn't write it down), you'll have to delete these application credentials
and create a new one.

## Installation

### Via HACS (Recommended)

See [HACS Official Installation Guide](https://hacs.xyz/docs/installation/installation/) and install HACS. See
[Initial Configuration Guide](https://hacs.xyz/docs/configuration/basic) and complete initial configuration.

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"

![custom repository](/docs/pictures/hacs_custom_repositories.png)

5. Add this repository URL: `https://github.com/rensongroup/home-assistant`

![github](/docs/pictures/hacs_add_repository.png)

6. Set category to "Integration"
7. Click "Add"
8. Find "OpenMotics Integration" in the integration list

![install](/docs/pictures/hacs_download_repository.png)

![download](/docs/pictures/hacs_download_repository_2.png)

9. Click "Download"
10. Restart Home Assistant

![restart](/docs/pictures/hacs_pending_restart.png)

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/rensongroup/home-assistant/releases)
2. Extract the `openmotics` folder from the archive
3. Copy it to `custom_components/openmotics/` in your Home Assistant configuration directory

![configuration directory](/docs/pictures/copy_method.png)

4. Restart Home Assistant

## Initial Setup

Make sure you restart Home Assistant after the installation (in HACS).

After installation, add the integration:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "OpenMotics"

![New Integration](/docs/pictures/new_integration.png)

4. Follow the configuration steps:

### Step 1: Connection Information

Select if you want to access via the cloud or via the local gateway:

![Integration setup](/docs/pictures/integration_setup.png)

### Step 2a: Cloud integration

![Integration setup_cloud](/docs/pictures/integration_setup_cloud.png)

- **Client_id:** The client_id you created in the first step
- **Client_secret:** Your authentication token

Click **Submit** to test the connection.

### Step 2b: Local gateway integration

![Integration setup_cloud](/docs/pictures/integration_setup_local.png)

- **Host/IP Address:** The hostname or IP address of your local device (be careful with dhcp setups)
- **Name:** Your login name
- **Password:** Your password
- **Port:** Connection port (default: 443)
- **SSL Certificate:** Enable this if you have uploaded your own certificates to the gateway, otherwise leave it
  disabled.

Click **Submit** to test the connection.

That's it.

## Troubleshooting

### Connection Failed

If setup fails with connection errors:

1. Verify the host/IP address is correct and reachable
2. Check that the API key/token is valid
3. Ensure no firewall is blocking the connection
4. Check Home Assistant logs for detailed error messages

### Entities Not Updating

If entities show "Unavailable" or don't update:

1. Check that the device/service is online
2. Verify API credentials haven't expired
3. Review logs: **Settings** → **System** → **Logs**
4. Try reloading the integration

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: warning
  logs:
    custom_components.openmotics: debug
```

Add this to `configuration.yaml`, restart, and reproduce the issue. Check logs for detailed information.

## Next Steps

- Report issues at [GitHub Issues](https://github.com/rensongroup/home-assistant/issues)

## Support

For help and discussion:

- [GitHub Discussions](https://github.com/rensongroup/home-assistant/discussions)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
