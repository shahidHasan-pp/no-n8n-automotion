from enum import Enum

class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"

class ProductCategory(str, Enum):
    SHIRT = "shirt"
    T_SHIRT = "t-shirt"
    PANT = "pant"
    JACKET = "jacket"
    HOODIE = "hoodie"
    DRESS = "dress"

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PENDING = "pending"
    SCHEDULED = "scheduled"
    FAILED = "failed"

class PostTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    HUMOROUS = "humorous"

class InsightType(str, Enum):
    PERFORMANCE = "performance"
    CONTENT = "content"
    HASHTAG = "hashtag"
    TIMING = "timing"
