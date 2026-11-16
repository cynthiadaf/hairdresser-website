from app.worker import _apify_records


def test_apify_records_normalizes_carousel_media():
    records = _apify_records(
        {
            "id": "post-1",
            "childPosts": [
                {"id": "image-1", "displayUrl": "https://cdn.example/image.jpg"},
                {
                    "id": "video-1",
                    "videoUrl": "https://cdn.example/video.mp4",
                    "displayUrl": "https://cdn.example/video-thumb.jpg",
                },
            ],
        }
    )

    assert records == [
        {
            "media_id": "image-1",
            "media_type": "image",
            "source_url": "https://cdn.example/image.jpg",
            "thumbnail_url": None,
            "width": 0,
            "height": 0,
        },
        {
            "media_id": "video-1",
            "media_type": "video",
            "source_url": "https://cdn.example/video.mp4",
            "thumbnail_url": "https://cdn.example/video-thumb.jpg",
            "width": 0,
            "height": 0,
        },
    ]


def test_apify_records_skips_items_without_media_urls():
    assert _apify_records({"id": "post-1"}) == []
