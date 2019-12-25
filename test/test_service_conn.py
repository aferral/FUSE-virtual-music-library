import unittest
from drive_utils import get_service

class TestServiceAPI(unittest.TestCase):

    def test_service_get(self):
        out=get_service()
        self.assertIsNotNone(out)

if __name__ == '__main__':
    unittest.main()
