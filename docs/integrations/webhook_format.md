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

## Real world examples

A GitHub push event may include the commit count and repository URL:

```json
{
  "source": "github",
  "event": "push",
  "payload": {
    "repository": "acme/spaceships",
    "pusher": "octocat",
    "commits": 3,
    "html_url": "https://github.com/acme/spaceships"
  },
  "timestamp": "2023-03-10T12:34:56Z"
}
```

A Slack message could send the channel and user id:

```json
{
  "source": "slack",
  "event": "message",
  "payload": {
    "channel": "C123456",
    "user": "U222222",
    "text": "Deploy finished"
  }
}
```

### Optional fields

Integrations often supply extra metadata such as:

- `timestamp`: ISO 8601 date of the event.
- `signature`: HMAC to verify the payload.
- `org_id`: identifier for multitenant setups.

These fields are not required but may help trace or validate events.

### Authentication and security

Senders are encouraged to include a secret token or signature header with each
request. The server verifies this value to ensure the payload originates from
a trusted source. Rotate credentials periodically and use HTTPS to protect
traffic.
