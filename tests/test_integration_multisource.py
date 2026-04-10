import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from image_downloader.models import ImageCandidate
from image_downloader.storage import record_download, should_skip_candidate

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from bing_image_downloader import collect_candidates_from_sources


class TestMultiSourceIntegration(unittest.TestCase):
    def test_collect_candidates_from_sources_merges_results_in_source_order(self):
        bing_source = mock.Mock()
        bing_source.name = "bing"
        bing_source.collect.return_value = [
            ImageCandidate(
                source="bing",
                keyword="cat",
                image_url="https://img.example.com/bing-1.jpg",
                page_url=None,
                thumbnail_url=None,
                title=None,
                width=None,
                height=None,
                content_type=None,
                source_rank=1,
                metadata={},
            )
        ]

        demo_source = mock.Mock()
        demo_source.name = "demo"
        demo_source.collect.return_value = [
            ImageCandidate(
                source="demo",
                keyword="cat",
                image_url="https://demo.example.com/cat/1.jpg",
                page_url=None,
                thumbnail_url=None,
                title="demo cat 1",
                width=640,
                height=480,
                content_type="image/jpeg",
                source_rank=1,
                metadata={"demo": True},
            )
        ]

        results = collect_candidates_from_sources(
            keyword="cat",
            limit=5,
            pages=2,
            sources=[bing_source, demo_source],
        )

        self.assertEqual([item.source for item in results], ["bing", "demo"])
        self.assertEqual(results[0].image_url, "https://img.example.com/bing-1.jpg")
        self.assertEqual(results[1].image_url, "https://demo.example.com/cat/1.jpg")
        bing_source.collect.assert_called_once_with("cat", limit=5, pages=2)
        demo_source.collect.assert_called_once_with("cat", limit=5, pages=2)

    def test_history_index_skips_previously_downloaded_candidate(self):
        candidate = ImageCandidate(
            source="demo",
            keyword="cat",
            image_url="https://demo.example.com/cat/1.jpg?cache=1",
            page_url="https://demo.example.com/cat/1",
            thumbnail_url=None,
            title="demo cat 1",
            width=640,
            height=480,
            content_type="image/jpeg",
            source_rank=1,
            metadata={},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            saved_path = output_dir / "001.jpg"
            saved_path.write_bytes(b"demo-image")
            record_download(candidate, saved_path, output_dir)

            duplicate = ImageCandidate(
                source="bing",
                keyword="cat",
                image_url="https://demo.example.com/cat/1.jpg?cache=2",
                page_url=None,
                thumbnail_url=None,
                title=None,
                width=None,
                height=None,
                content_type=None,
                source_rank=2,
                metadata={},
            )

            self.assertTrue(should_skip_candidate(duplicate, output_dir))


if __name__ == "__main__":
    unittest.main()
