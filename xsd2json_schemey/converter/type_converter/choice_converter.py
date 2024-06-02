from dataclasses import dataclass, field
from typing import List, Optional
from xml.etree.ElementTree import Element

from marshy import ExternalType
from marshy.types import ExternalItemType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import TypeConverterABC, TypeConverterFactoryABC, SchemaConverter, ConverterException
from xsd2json_schemey.converter.type_converter.child_converter import ChildConverter
from xsd2json_schemey.converter.type_converter.sequence_converter import child_converters_for_sequence


@dataclass
class ChoiceConverter(TypeConverterABC):
    json_schema: ExternalItemType
    child_converters: List[ChildConverter] = field(default_factory=list)

    def to_xml(self, json_value: ExternalType, target: Element):
        if json_value is None:
            return
        if not isinstance(json_value, dict) or len(json_value) != 1:
            raise ConverterException(f"wrong_type:{json_value}")
        json_attr_name = next(iter(json_value.keys()))
        for child_converter in self.child_converters:
            if child_converter.json_attr_name == json_attr_name:
                child_value = json_value[json_attr_name]
                child_element = Element(child_converter.tag_name)
                return child_converter.type_converter.to_xml(child_value, child_element)
        raise ConverterException(f"unknown_type:{json_attr_name}")

    def from_xml(self, xml_value: Element) -> ExternalType:
        if xml_value is None:
            return
        if len(xml_value) != 1:
            raise ConverterException(f"wrong_type:{xml_value}")
        child_element = next(iter(xml_value))
        child_converter = next(c for c in self.child_converters if c.tag_name == child_element.tag)
        return child_converter.type_converter.from_xml(child_element)


class ChoiceConverterFactory(TypeConverterFactoryABC):
    def create(self, type_element: Element, schema_converter: SchemaConverter) -> Optional[TypeConverterABC]:
        complex_type = type_element.find(f".//{SCHEMA}complexType")
        if complex_type is None:
            return
        sequence = complex_type.find(f".//{SCHEMA}choice")
        if sequence is None:
            return
        child_converters = list(
            child_converters_for_sequence(sequence, schema_converter)
        )
        # Any of with type...
        json_schema = {
            "anyOf": [c.type_converter.json_schema for c in child_converters]
        }
        return ChoiceConverter(json_schema, child_converters)
