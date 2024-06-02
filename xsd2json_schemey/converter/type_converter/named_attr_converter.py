from dataclasses import dataclass, field
from typing import Set, List

from marshy import ExternalType

from xsd2json_schemey.converter import AttrConverterABC
from xsd2json_schemey.util import to_snake_case


@dataclass
class NamedAttrConverter:
    xml_attr_name: str
    attr_converter: AttrConverterABC
    json_attr_name: str = None
    required: bool = False

    def __post_init__(self):
        if self.json_attr_name is None:
            self.json_attr_name = to_snake_case(self.xml_attr_name)
