from django import test

from . import shortcuts


class NotificationTest(test.TestCase):
    fixtures = ["default"]

    def test_notification_queue(self):
        shortcuts.queue(owner="test-user")
