from unittest.mock import MagicMock

from fief import schemas
from fief.models import Workspace
from fief.services.webhooks.models import WebhookEvent, WebhookEventType
from fief.services.webhooks.trigger import trigger_webhooks
from tests.data import TestData


def test_trigger_webhooks(
    workspace: Workspace, test_data: TestData, send_task_mock: MagicMock
):
    object = test_data["clients"]["default_tenant"]

    trigger_webhooks(
        WebhookEventType.OBJECT_CREATED,
        object,
        schemas.client.Client,
        workspace_id=workspace.id,
        send_task=send_task_mock,
    )

    send_task_mock.assert_called_once()
    assert send_task_mock.call_args[1]["workspace_id"] == str(workspace.id)

    event_json = send_task_mock.call_args[1]["event"]
    event = WebhookEvent.parse_raw(event_json)
    assert event.type == WebhookEventType.OBJECT_CREATED
    assert event.object == "Client"
    assert event.data["id"] == str(object.id)
