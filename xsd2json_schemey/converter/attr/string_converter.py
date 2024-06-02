from dataclasses import dataclass
from typing import Optional
from xml.etree.ElementTree import Element

from marshy.types import ExternalItemType, ExternalType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import AttrConverterABC, AttrConverterFactoryABC
from xsd2json_schemey.converter.description import add_description


@dataclass
class StringConverter(AttrConverterABC):
    json_schema: ExternalItemType

    def to_xml_attr(self, json_value: ExternalType) -> str:
        if json_value is not None:
            return str(json_value)

    def from_xml_attr(self, xml_value: str) -> ExternalType:
        if xml_value is not None:
            return str(xml_value)


class StringConverterFactory(AttrConverterFactoryABC):

    def create(
        self, type_element: Element, schema_converter: AttrConverterABC
    ) -> Optional[AttrConverterABC]:
        if type_element.tag != f"{SCHEMA}simpleType":
            return
        restriction = type_element.find(f"{SCHEMA}restriction")
        if restriction is None or restriction.attrib.get("base") != "xsd:string":
            return
        result = {"type": "string"}
        max_length = restriction.find(f"{SCHEMA}maxLength")
        if max_length:
            result["maxLength"] = int(max_length.attrib["value"])
        pattern = restriction.find(f"{SCHEMA}pattern")
        if pattern:
            result["pattern"] = pattern.attrib["value"]
        add_description(type_element, result)
        return StringConverter(result)
