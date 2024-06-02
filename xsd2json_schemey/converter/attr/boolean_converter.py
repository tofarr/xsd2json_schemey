from dataclasses import dataclass, field
from typing import Optional
from xml.etree.ElementTree import Element

from marshy.types import ExternalItemType, ExternalType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import (
    SchemaConverter,
    AttrConverterABC,
    AttrConverterFactoryABC,
)
from xsd2json_schemey.converter.description import add_description


@dataclass
class BooleanConverter(AttrConverterABC):
    json_schema: ExternalItemType = field(default_factory=lambda: {"type": "boolean"})

    def to_xml_attr(self, json_value: ExternalType) -> str:
        if json_value is not None:
            return str(json_value)

    def from_xml_attr(self, xml_value: str) -> ExternalType:
        if xml_value is not None:
            return bool(xml_value)


class BooleanConverterFactory(AttrConverterFactoryABC):

    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[BooleanConverter]:
        if type_element.tag != f"{SCHEMA}simpleType":
            return
        restriction = type_element.find(f"{SCHEMA}restriction")
        if restriction is None or restriction.attrib.get("base") != "xsd:boolean":
            return
        result = BooleanConverter()
        add_description(type_element, result.json_schema)
        return result
