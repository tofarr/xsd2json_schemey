from dataclasses import dataclass, field
from typing import Optional
from xml.etree.ElementTree import Element

from marshy import ExternalType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import (
    AttrConverterABC,
    SchemaConverter,
    TypeConverterABC,
    TypeConverterFactoryABC,
)
from xsd2json_schemey.converter.attr.string_converter import StringConverter


@dataclass
class SimpleTypeConverter(TypeConverterABC):
    text_converter: AttrConverterABC = field(default_factory=StringConverter)

    def to_xml(self, json_value: ExternalType, target: Element):
        if json_value is None:
            return
        target.text = self.text_converter.to_xml_attr(json_value)

    def from_xml(self, xml_value: Optional[Element]) -> ExternalType:
        if xml_value is not None:
            result = self.text_converter.from_xml_attr(xml_value.text)
            return result

    @property
    def json_schema(self):
        return self.text_converter.json_schema


class SimpleTypeConverterFactory(TypeConverterFactoryABC):
    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[TypeConverterABC]:
        if type_element.tag != f"{SCHEMA}simpleType":
            return

        text_converter = schema_converter.create_attr_converter(type_element)
        result = SimpleTypeConverter(text_converter)
        return result
