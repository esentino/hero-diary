from enum import Enum, auto

BASE_CAPACITY = 10
BASE_SPEED_OF_TRAVEL = 1
LOCATION_ROAD_TOWN = 4
LOCATION_KILLING_FIELDS = 3
LOCATION_ROAD_KILLING_FIELDS = 2
LOCATION_TOWN = 1
LUCK_MULTIPLIER = 0.1
SPEED_OF_TRAVEL_MULTIPLIER = 0.1
LIST_OF_ITEMS = [
    "Soap",
    "Branch",
    "Rock",
    "Rope",
    "Glasses",
    "Skin",
    "Head & Shoulders",
    "Bat",
]
LIST_OF_MONSTER = [
    "Dragon",
    "ButterFly",
    "Village Idiot",
    "Rabbit",
    "Wolf",
    "Big Bad Wolf",
    "Small Bad Wolf",
]


class ActionType(Enum):
    SELL_ITEM = auto()
    BUY_EQUIPMENT = auto()
    TRAVEL_TO_KILLING_FIELD = auto()
    KILLING_FIELD = auto()
    KILL_MONSTER = auto()
    TRAVEL_TO_TOWN = auto()
    TOWN = auto()


ACTION_SPEED = {
    ActionType.SELL_ITEM: 1,
    ActionType.BUY_EQUIPMENT: 1,
    ActionType.TRAVEL_TO_KILLING_FIELD: 1,
    ActionType.KILLING_FIELD: 60,
    ActionType.KILL_MONSTER: 5,
    ActionType.TRAVEL_TO_TOWN: 1,
    ActionType.TOWN: 60,
}
