# Notification Officer

Notification Officer is a notification 
service designed to receive events
from external platforms and deliver 
notifications to users.

The current implementation 
focuses on Twitch EventSub.

## Current architecture

The current notification pipeline:

Twitch EventSub
- EventSubWebhookService
- NotificationPublisher
- Redis Stream
- NotificationWorker
- HandlerRegistry
- TwitchHandler
- Log

## Implemented
- Instagram

### Twitch EventSub

- Twitch webhook signature verification.
- `notification` message processing.
- `revocation` message handling.
- `webhook_callback_verification` 
with `challenge` response.
- Conversion of Twitch events into 
`NotificationMessage`.

Supported events:

- `stream.online`
- `stream.offline`
- `channel.update`

### Redis

- Redis connector abstraction.
- Redis Streams publisher.
- Consumer group initialization.
- Redis Streams consumer.
- Message acknowledgement.
- Pending message reclaiming 
with `XAUTOCLAIM`.
- Redis-specific exceptions.

### Notification Worker

- Platform-based `HandlerRegistry`.
- `NotificationWorker` for notification 
processing.
- `WorkerFactory` for worker creation.
- `WorkerRunner` for worker lifecycle 
management.
- Graceful shutdown using `asyncio.Event`.
- Worker recreation after Redis 
connection errors.
- Pending message reclaiming after 
worker recreation.

### Twitch Handler

Twitch events are validated 
using Pydantic models.

Invalid payloads are 
converted into `PermanentNotificationError`.

The handler currently 
logs processed events.

## Testing

The project contains unit and integration 
tests covering:

- Twitch EventSub webhook processing.
- Notification publishing.
- Twitch event handling.
- Pydantic payload validation.
- Redis Streams.
- Notification Worker.
- Worker restart and pending 
message reclaiming.
- Application lifecycle.
- End-to-end Twitch notification pipeline.

## Current Status

The Twitch notification pipeline is 
implemented from webhook reception
to event processing.

Telegram notification delivery 
is planned for a future stage.

## Installation

1. Clone the repository

```bash
git clone https://github.com/Andreykaproger/notification-officer.git 
cd notification-officer
```

2. Install `uv`
```bash
pip install uv
```

3. Copy variables from `.env.example` 
to your `.env` and fill in the required 
values

4. Build the containers
```bash
make build
```

5. Start the application
```bash
make up
```




