# Dataset notes

- The target is 10 images per class (200 total) as a small bootstrap set, not a sufficient final training corpus.
- For a meaningful classifier, target at least 200–500 diverse images per class, preferably more, with variation in camera angle, lighting, backgrounds, serving vessels, and vendors.
- Keep a clean test set from different image sources or capture sessions.
- Class 19 contains non-food objects for rejection experiments; it should not be mixed into ordinary food classification without a carefully designed open-set evaluation.
- The downloaded images need human review. Search engines and Commons text metadata can return mislabeled or ambiguous images.
- Nutrition estimates should come from a separate verified nutrition table; image embeddings alone do not estimate calories.
