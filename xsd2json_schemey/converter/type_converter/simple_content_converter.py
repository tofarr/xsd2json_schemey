from dataclasses import dataclass, field
from typing import List, Optional, Iterator
from xml.etree.ElementTree import Element

from marshy import ExternalType
from marshy.types import ExternalItemType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import TypeConverterABC, AttrConverterABC, ConverterException, \
    TypeConverterFactoryABC, SchemaConverter
from xsd2json_schemey.converter.attr.string_converter import StringConverter
from xsd2json_schemey.converter.type_converter.named_attr_converter import NamedAttrConverter


@dataclass
class SimpleContentConverter(TypeConverterABC):
    json_schema: ExternalItemType
    json_text_attr_name: str = None
    text_converter: AttrConverterABC = field(default_factory=StringConverter)
    attr_converters: List[NamedAttrConverter] = field(default_factory=list)

    def to_xml(self, json_value: ExternalType, target: Element):
        if json_value is None:
            return
        if not isinstance(json_value, dict):
            raise ConverterException(f"wrong_type:{json_value}")
        attribs_to_xml(json_value, self.attr_converters, target)
        if self.json_text_attr_name in json_value:
            text_value = json_value.get(self.json_text_attr_name)
            target.text = self.text_converter.to_xml_attr(text_value)

    def from_xml(self, xml_value: Optional[Element]) -> ExternalType:
        if xml_value is None:
            return
        result = attribs_from_xml(xml_value, self.attr_converters)
        if xml_value.text is not None:
            result[self.json_text_attr_name] = self.text_converter.from_xml_attr(xml_value.text)
        return result


def attribs_to_xml(json_value: ExternalItemType, attr_converters: List[NamedAttrConverter], target: Element):
    for attr_converter in attr_converters:
        if attr_converter.json_attr_name in json_value:
            attr_value = json_value.get(attr_converter.json_attr_name)
            attr_xml_value = attr_converter.attr_converter.to_xml_attr(attr_value)
            target.attrib[attr_converter.xml_attr_name] = attr_xml_value


def attribs_from_xml(xml_value: Element, attr_converters: List[NamedAttrConverter]) -> ExternalItemType:
    attr = xml_value.attrib
    result = {
        a.json_attr_name: a.attr_converter.from_xml_attr(attr.get(a.xml_attr_name))
        for a in attr_converters
    }
    return result


@dataclass
class SimpleContentConverterFactory(TypeConverterFactoryABC):
    json_text_attr_name: str = "value"

    def create(self, type_element: Element, schema_converter: SchemaConverter) -> Optional[TypeConverterABC]:
        if type_element.tag != f"{SCHEMA}complexType":
            return
        simple_content = type_element.find(f".//{SCHEMA}simpleContent")
        if simple_content is None:
            return
        extension = simple_content.find(f".//{SCHEMA}extension")
        if extension is None:
            return
        text_converter = schema_converter.create_named_attr_converter(extension.attrib.get("base"))
        attr_converters = list(named_attr_converters(extension, schema_converter))
        properties = {
            c.json_attr_name: c.attr_converter.json_schema
            for c in attr_converters
        }
        properties[self.json_text_attr_name] = text_converter.json_schema
        required = [
            c.json_attr_name
            for c in attr_converters if c.required
        ]
        json_schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
            "required": required
        }
        return SimpleContentConverter(json_schema, self.json_text_attr_name, text_converter, attr_converters)


def named_attr_converters(extension: Element, schema_converter: SchemaConverter) -> Iterator[NamedAttrConverter]:
    for attribute in extension.findall(f".//[{SCHEMA}attribute or {SCHEMA}attributeGroup]"):
        yield from named_attr_converter(attribute, schema_converter)


def named_attr_converter(element: Element, schema_converter: SchemaConverter) -> Iterator[NamedAttrConverter]:
    if element.tag == f"{SCHEMA}attributeGroup":
        ref = schema_converter.type_elements.get("ref")
        if ref:
            yield from named_attr_converter(ref, schema_converter)
        for child in element:
            yield from named_attr_converter(child, schema_converter)
        return
    if element.tag != f"{SCHEMA}attribute":
        return
    attrib = element.attrib
    name = attrib.get("name")
    type_ = attrib.get("type")
    required = attrib.get("use") == "required"
    if type_:
        converter = schema_converter.create_named_attr_converter(name)
    else:
        simple_type = element.find(f".//{SCHEMA}simpleType")
        converter = schema_converter.create_attr_converter(simple_type)
    yield NamedAttrConverter(name, converter, required=required)
