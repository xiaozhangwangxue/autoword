import json
import unittest

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_is_available(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('排版工厂', response.get_data(as_text=True))

    def test_process_rejects_non_docx_uploads(self):
        response = self.client.post(
            '/process_stream',
            data={'file': (__import__('io').BytesIO(b'not a document'), 'notes.txt')},
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('无有效docx文件', json.loads(response.get_data())['msg'])
