# Security Overview

SquirrelFocus stores notes locally in plain text by default. Integrations
can post data to webhooks, so treat credentials with care.

The workflow relies on environment variables for secrets. Keep `.env`
files out of version control and rotate API keys when needed.

External services are optional. Limit access to only the features your
team requires.
