# Placeholder for YouTube posting (video upload + scheduling via the
# YouTube Data API v3). Needs a Google Cloud project + OAuth credentials
# before any real API calls can be made here.


def post(data):
    print(
        f"Skipping '{data.get('title', '<untitled>')}': YouTube posting isn't "
        "implemented yet. This is a placeholder for the upcoming YouTube Data "
        "API integration."
    )
