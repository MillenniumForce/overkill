from overkill.servers.worker import Worker


def test_instantiation():
    """Test the instantiation of a new worker"""
    w = Worker("test")
    w.start()
    w.stop()
