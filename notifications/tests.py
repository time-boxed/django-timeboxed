from . import shortcuts

from django import test


class NotificationTest(test.TestCase):
    fixtures = ["default"]

    def test_notification_queue(self):
        shortcuts.queue(owner="test-user")
