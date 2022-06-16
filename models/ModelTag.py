import dataclasses

from models.EnumPostStatus import EnumPostStatus


@dataclasses.dataclass
class ModelTag:
    tag_id:int = 0
    label: str = ""
    is_deleted: int = 0
    created: int = 0
    modified: int = 0