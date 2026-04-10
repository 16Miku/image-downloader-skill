from image_downloader.models import ImageCandidate


class BaseSource:
    name = "base"

    def collect(self, keyword: str, limit: int | None = None) -> list[ImageCandidate]:
        raise NotImplementedError("Sources must implement collect()")
