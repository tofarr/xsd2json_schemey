from dataclasses import dataclass
from typing import Optional
from xml.etree.ElementTree import Element

from marshy import ExternalType
from marshy.types import ExternalItemType

from xsd2json_schemey.converter import ConverterException, TypeConverterABC

from xsd2json_schemey.converter.type_converter.simple_content_converter import (
    attribs_from_xml, attribs_to_xml,
)


@dataclass
class ArrayConverter(TypeConverterABC):
    json_schema: ExternalItemType
    tag_name: str
    type_converter: TypeConverterABC

    def to_xml(self, json_value: ExternalType, target: Element):
        if json_value is None:
            return
        if not isinstance(json_value, list):
            raise ConverterException(f"wrong_type:{json_value}")
        for child in json_value:
            child_element = Element(self.tag_name)
            self.type_converter.to_xml(child, child_element)

    def from_xml(self, xml_value: Optional[Element]) -> ExternalType:
        if xml_value is None:
            return
        result = [
            self.type_converter.from_xml(child_element)
            for child_element in xml_value
        ]
        return result
