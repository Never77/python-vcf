from enum import Enum


class KindType(str, Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"
    ORG = "org"
    LOCATION = "location"
