from enum import Enum


class GooglePhotosMediaType(Enum):
    VIDEO = 'VIDEO'
    PHOTO = 'PHOTO'
    ALL = 'ALL_MEDIA'


class GooglePhotosFeatureType(Enum):
    NONE = 'NONE'
    FAVORITES = 'FAVORITES'
