from dataclasses import dataclass, field
from typing import List, Optional, Iterator
from xml.etree.ElementTree import Element

from marshy import ExternalType
from marshy.types import ExternalItemType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import TypeConverterABC, TypeConverterFactoryABC, SchemaConverter, ConverterException
from xsd2json_schemey.converter.type_converter.array_converter import ArrayConverter
from xsd2json_schemey.converter.type_converter.child_converter import ChildConverter
from xsd2json_schemey.converter.type_converter.object_converter import ObjectConverter
from xsd2json_schemey.util import to_snake_case

@dataclass
class SequenceConverter(TypeConverterABC):
    json_schema: ExternalItemType
    child_converters: List[ChildConverter] = field(default_factory=list)

    def to_xml(self, json_value: ExternalType, target: Element):
        if json_value is None:
            return
        if not isinstance(json_value, dict):
            raise ConverterException(f"wrong_type:{json_value}")
        for child_converter in self.child_converters:
            items = json_value.get(child_converter.json_attr_name)
            if items is None:
                continue
            for item in items:
                item_element = Element(child_converter.tag_name)
                child_converter.type_converter.to_xml(item, item_element)

    def from_xml(self, xml_value: Element) -> ExternalType:
        if xml_value is None:
            return
        result = []
        for child_element in xml_value:
            child_converter = next(c for c in self.child_converters if c.tag_name == child_element.tag)
            result.append(child_converter.type_converter.from_xml(child_element))
        return result


class SequenceConverterFactory(TypeConverterFactoryABC):
    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[TypeConverterABC]:
        complex_type = type_element.find(f".//{SCHEMA}complexType")
        if complex_type is None:
            return
        sequence = complex_type.find(f".//{SCHEMA}sequence")
        if sequence is None:
            return
        child_converters = list(
            child_converters_for_sequence(sequence, schema_converter)
        )

        if is_array(child_converters):
            # Is there more than 1 element?
            # Does the overall sequence element have a max occurs?
            # Do elements within the sequence have a max occurs?
            # So JsonSchema isn't really specific enough to say: 5 x then 3 y. In this case we need an object with arrays
            json_schema = {
                "type": "array",
                "items": child_converters[0].type_converter.json_schema
            }
            return ArrayConverter(json_schema, child_converters[0].tag_name, child_converters[0].type_converter)
        else:
            json_schema = {
                "type": "object",
                "properties": {
                    c.json_attr_name: {
                        "type": "array",
                        "items": c.type_converter.json_schema
                    }
                    for c in child_converters
                },
                "additionalProperties": False,
                "required": [
                    c.json_attr_name for c in child_converters if c.min_occurs == 1
                ],
            }
            return SequenceConverter(json_schema, child_converters)


def child_converters_for_sequence(
    sequence: Element, schema_converter: SchemaConverter
) -> Iterator[ChildConverter]:
    for element in sequence.find(f".//{SCHEMA}element"):
        name = element.attrib["name"]
        yield ChildConverter(
            tag_name=name,
            json_attr_name=to_snake_case(name),
            type_converter=schema_converter.create_element_converter(element),
            min_occurs=occurs(element, "minOccurs", 1),
            max_occurs=occurs(element, "maxOccurs", 1),
        )


def occurs(element: Element, key: str, default_value: Optional[int] = None) -> Optional[int]:
    value = element.attrib.get(key)
    if value is None:
        return default_value
    if value == "unbounded":
        return
    return int(value)


def is_array(child_converters: List[ChildConverter]) -> bool:
    for child_converter in child_converters:
        if child_converter.max_occurs > 1:
            return True
    return False
