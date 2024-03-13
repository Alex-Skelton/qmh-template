from unittest.mock import patch
from workers.template_worker import TemplateWorker


def test_start_method():
    worker = TemplateWorker("test_worker", {}, False)
    worker.start()
    assert worker.active is True


def test_shutdown_method_sends_shutdown_message():
    with patch('workers.template_worker.TemplateWorker.send_message') as mock_send:
        queues = {"test_queue": "mock_queue_object"}  # Simulate having a queue object
        worker = TemplateWorker("test_worker", queues)
        worker.shutdown()
        assert worker.alive is False
        mock_send.assert_called_once_with("mock_queue_object", "shutdown")