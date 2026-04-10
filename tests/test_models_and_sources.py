import unittest

from image_downloader.models import ImageCandidate
from image_downloader.sources.base import BaseSource


class DummySource(BaseSource):
    def collect(self, keyword, limit=None):
        return [
            ImageCandidate(
                source="dummy",
                keyword=keyword,
                image_url="https://img.example.com/cat.jpg",
                page_url="https://example.com/cat",
                thumbnail_url="https://img.example.com/cat-thumb.jpg",
                title="cat",
                width=800,
                height=600,
                content_type="image/jpeg",
                source_rank=1,
                metadata={"origin": "dummy"},
            )
        ]


class TestModelsAndSources(unittest.TestCase):
    def test_image_candidate_preserves_plan_fields(self):
        candidate = ImageCandidate(
            source="bing",
            keyword="cat",
            image_url="https://img.example.com/cat.jpg",
            page_url="https://www.bing.com/images/search?q=cat",
            thumbnail_url="https://img.example.com/thumb.jpg",
            title="cat title",
            width=800,
            height=600,
            content_type="image/jpeg",
            source_rank=3,
            metadata={"id": "abc"},
        )

        self.assertEqual(candidate.source, "bing")
        self.assertEqual(candidate.keyword, "cat")
        self.assertEqual(candidate.image_url, "https://img.example.com/cat.jpg")
        self.assertEqual(candidate.page_url, "https://www.bing.com/images/search?q=cat")
        self.assertEqual(candidate.thumbnail_url, "https://img.example.com/thumb.jpg")
        self.assertEqual(candidate.title, "cat title")
        self.assertEqual(candidate.width, 800)
        self.assertEqual(candidate.height, 600)
        self.assertEqual(candidate.content_type, "image/jpeg")
        self.assertEqual(candidate.source_rank, 3)
        self.assertEqual(candidate.metadata, {"id": "abc"})

    def test_dummy_source_collect_returns_image_candidate(self):
        candidates = DummySource().collect("cat", limit=1)

        self.assertEqual(len(candidates), 1)
        self.assertIsInstance(candidates[0], ImageCandidate)
        self.assertEqual(candidates[0].keyword, "cat")
        self.assertEqual(candidates[0].source, "dummy")


if __name__ == "__main__":
    unittest.main()
