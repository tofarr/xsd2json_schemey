from dataclasses import dataclass
from typing import Optional

from xsd2json_schemey.converter import TypeConverterABC


@dataclass
class ChildConverter:
    tag_name: str
    json_attr_name: str
    type_converter: TypeConverterABC
    min_occurs: Optional[int] = 1
    max_occurs: Optional[int] = 1
