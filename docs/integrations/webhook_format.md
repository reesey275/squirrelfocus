# Webhook Format for Integrations

Integrations send data to SquirrelFocus using webhooks. Each integration
issues an HTTP POST request to the configured URL. The request body must
be JSON encoded and include the following fields:

- `source`: a short identifier such as `github`.
- `event`: the event type that triggered the webhook.
- `payload`: a nested object containing event details.

Example payload:

```json
{
  "source": "github",
  "event": "push",
  "payload": {
    "repository": "squirrelfocus",
    "pusher": "octocat"
  }
}
```

Integrations may add extra fields as needed, but the three keys above must
always be present. The server validates them before processing the request.
