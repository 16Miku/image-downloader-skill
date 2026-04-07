import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from bing_image_downloader import (
    extract_image_urls,
    guess_extension,
    download_images,
    collect_image_urls,
)


class TestBingImageDownloader(unittest.TestCase):
    def test_extract_image_urls_from_bing_html(self):
        html = '''
        <a class="iusc" m='{"murl":"https://img.example.com/a.jpg"}'></a>
        <a class="iusc" m='{"murl":"https://img.example.com/b.png"}'></a>
        <a class="iusc" m='{"murl":"https://img.example.com/a.jpg"}'></a>
        '''
        urls = extract_image_urls(html)
        self.assertEqual(urls, [
            "https://img.example.com/a.jpg",
            "https://img.example.com/b.png",
        ])

    def test_extract_image_urls_from_html_entities(self):
        html = '''
        <a class="iusc" m="{&quot;murl&quot;:&quot;https://img.example.com/c.jpg&quot;,&quot;turl&quot;:&quot;x&quot;}"></a>
        <a class="iusc" m="{&quot;murl&quot;:&quot;https://img.example.com/d.png&quot;,&quot;turl&quot;:&quot;y&quot;}"></a>
        '''
        urls = extract_image_urls(html)
        self.assertEqual(urls, [
            "https://img.example.com/c.jpg",
            "https://img.example.com/d.png",
        ])

    @mock.patch("bing_image_downloader.requests.get")
    def test_collect_image_urls_across_multiple_pages(self, mock_get):
        search_page_1 = mock.Mock()
        search_page_1.raise_for_status.return_value = None
        search_page_1.text = '''
        <a class="iusc" m='{"murl":"https://img.example.com/1.jpg"}'></a>
        <a class="iusc" m='{"murl":"https://img.example.com/2.jpg"}'></a>
        '''

        search_page_2 = mock.Mock()
        search_page_2.raise_for_status.return_value = None
        search_page_2.text = '''
        <a class="iusc" m='{"murl":"https://img.example.com/2.jpg"}'></a>
        <a class="iusc" m='{"murl":"https://img.example.com/3.jpg"}'></a>
        '''

        mock_get.side_effect = [search_page_1, search_page_2]

        urls = collect_image_urls("cat", pages=2)

        self.assertEqual(urls, [
            "https://img.example.com/1.jpg",
            "https://img.example.com/2.jpg",
            "https://img.example.com/3.jpg",
        ])
        self.assertEqual(mock_get.call_count, 2)

    @mock.patch("bing_image_downloader.requests.get")
    def test_collect_image_urls_stops_when_target_pool_reached(self, mock_get):
        search_page_1 = mock.Mock()
        search_page_1.raise_for_status.return_value = None
        search_page_1.text = '''
        <a class="iusc" m='{"murl":"https://img.example.com/1.jpg"}'></a>
        <a class="iusc" m='{"murl":"https://img.example.com/2.jpg"}'></a>
        '''

        search_page_2 = mock.Mock()
        search_page_2.raise_for_status.return_value = None
        search_page_2.text = '''
        <a class="iusc" m='{"murl":"https://img.example.com/3.jpg"}'></a>
        <a class="iusc" m='{"murl":"https://img.example.com/4.jpg"}'></a>
        '''

        search_page_3 = mock.Mock()
        search_page_3.raise_for_status.return_value = None
        search_page_3.text = '''
        <a class="iusc" m='{"murl":"https://img.example.com/5.jpg"}'></a>
        '''

        mock_get.side_effect = [search_page_1, search_page_2, search_page_3]

        urls = collect_image_urls("cat", pages=3, target_count=3)

        self.assertEqual(urls, [
            "https://img.example.com/1.jpg",
            "https://img.example.com/2.jpg",
            "https://img.example.com/3.jpg",
        ])
        self.assertEqual(mock_get.call_count, 2)

    @mock.patch("bing_image_downloader.requests.get")
    def test_download_images_stops_after_requested_count(self, mock_get):
        image_response = mock.Mock()
        image_response.raise_for_status.return_value = None
        image_response.headers = {"Content-Type": "image/jpeg"}
        image_response.iter_content.return_value = [b"abc", b"def"]
        mock_get.return_value = image_response

        urls = [
            "https://img.example.com/1.jpg",
            "https://img.example.com/2.jpg",
            "https://img.example.com/3.jpg",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            saved = download_images(urls, tmpdir, limit=2)
            self.assertEqual(len(saved), 2)
            self.assertTrue(os.path.exists(saved[0]))
            self.assertTrue(os.path.exists(saved[1]))
            self.assertTrue(saved[0].endswith("001.jpg"))
            self.assertTrue(saved[1].endswith("002.jpg"))

    @mock.patch("bing_image_downloader.requests.get")
    def test_download_images_respects_start_index(self, mock_get):
        image_response = mock.Mock()
        image_response.raise_for_status.return_value = None
        image_response.headers = {"Content-Type": "image/jpeg"}
        image_response.iter_content.return_value = [b"abc"]
        mock_get.return_value = image_response

        with tempfile.TemporaryDirectory() as tmpdir:
            saved = download_images([
                "https://img.example.com/3.jpg",
            ], tmpdir, limit=1, start_index=3)
            self.assertEqual(len(saved), 1)
            self.assertTrue(saved[0].endswith("003.jpg"))


if __name__ == "__main__":
    unittest.main()
