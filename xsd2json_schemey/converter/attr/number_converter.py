from dataclasses import field, dataclass
from typing import Optional
from xml.etree.ElementTree import Element

from marshy.types import ExternalItemType, ExternalType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import (
    AttrConverterABC,
    AttrConverterFactoryABC,
    SchemaConverter,
)

from xsd2json_schemey.converter.description import add_description


@dataclass
class NumberConverter(AttrConverterABC):
    json_schema: ExternalItemType

    def to_xml_attr(self, json_value: ExternalType) -> str:
        if json_value is not None:
            return str(json_value)

    def from_xml_attr(self, xml_value: str) -> ExternalType:
        type_ = self.json_schema["type"]
        if type_ == "integer":
            return int(xml_value)
        else:
            return float(xml_value)


class NumberConverterFactory(AttrConverterFactoryABC):

    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[AttrConverterABC]:
        if type_element.tag != f"{SCHEMA}simpleType":
            return
        restriction = type_element.find(f"{SCHEMA}restriction")
        if restriction is None:
            return
        base = restriction.attrib.get("base")
        if base in ["xsd:integer", "xsd:long"]:
            result = {"type": "integer"}
        elif base == "xsd:nonNegativeInteger":
            result = {"type": "integer", "minimum": 0}
        elif base == "xsd:nonPositiveInteger":
            result = {"type": "integer", "maximum": 0}
        elif base == "xsd:positiveInteger":
            result = {"type": "integer", "exclusiveMinimum": 0}
        elif base == "xsd:negativeInteger":
            result = {"type": "integer", "exclusiveMaximum": 0}
        elif base == "xsd:decimal":
            # XSD allows specifying fraction digits, but json schema doesn't really support this
            result = {"type": "number"}
        else:
            return
        add_description(type_element, result)
        return NumberConverter(result)
