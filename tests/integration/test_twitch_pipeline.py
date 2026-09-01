import logging


async def test_twitch_stream_online_pipeline(
    eventsub_service,
    notification_worker,
    webhook_request_stream_online,
    caplog,
):
    caplog.set_level(logging.INFO)

    await eventsub_service.handle(webhook_request_stream_online)

    await notification_worker.process_message()

    assert "Platform: Twitch" in caplog.text
    assert "Event: Streamer Online" in caplog.text
    assert "Streamer: test" in caplog.text
    assert "Link: https://twitch.tv/test" in caplog.text


async def test_twitch_stream_offline_pipeline(
    eventsub_service,
    notification_worker,
    webhook_request_stream_offline,
    caplog,
):
    caplog.set_level(logging.INFO)

    await eventsub_service.handle(webhook_request_stream_offline)

    await notification_worker.process_message()

    assert "Platform: Twitch" in caplog.text
    assert "Event: Streamer Offline" in caplog.text
    assert "Streamer: test" in caplog.text


async def test_twitch_channel_update_pipeline(
    eventsub_service,
    notification_worker,
    webhook_request_channel_update,
    caplog,
):
    caplog.set_level(logging.INFO)

    await eventsub_service.handle(webhook_request_channel_update)

    await notification_worker.process_message()

    assert "Platform: Twitch" in caplog.text
    assert "Event: Channel Update" in caplog.text
    assert "Streamer: test" in caplog.text
    assert "Title: stream" in caplog.text
    assert "Category Name: stream" in caplog.text
