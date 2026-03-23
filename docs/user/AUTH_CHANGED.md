> [!WARNING]\
> <strong> Action Required: Please migrate to Renson authentication. The OpenMotics login is deprecated and will
> <strong> soon be removed. You will need to update your client_id and client_secret. </br>

We’re updating how you sign in! Renson is replacing the old OpenMotics login system with a more secure Microsoft-based
authentication process.

This page will help you migrate to the new Microsoft-based authentication.

> [!NOTE]\
> If you are using a Local Gateway, you can skip this page. These updates only affect Cloud-based accounts.

## Getting a new client_id.

Login to [cloud.renson.eu](https://cloud.renson.eu/)

![login](/docs/pictures/login.cloud.renson.eu.png)

Remember to use your e-mail address as login.

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

![user07](/docs/pictures/user07.png)

You can now delete the old credentials.

## Update your credentials.

Adjust the integration:

1. Go to **Settings** → **Devices & Services**
2. Click **Openmotics**

![reauth01](/docs/pictures/reauth01.png)

![reauth02](/docs/pictures/reauth02.png)

3. Click **Reconfigure**

![reauth03](/docs/pictures/reauth03.png)

4. Fill in the new client_id and client_secret

![reauth04](/docs/pictures/reauth04.png)

That's it.

## Next Steps

- Report issues at [GitHub Issues](https://github.com/rensongroup/home-assistant/issues)

## Support

For help and discussion:

- [GitHub Discussions](https://github.com/rensongroup/home-assistant/discussions)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
