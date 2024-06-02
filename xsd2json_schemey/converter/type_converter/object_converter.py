from dataclasses import dataclass, field
from typing import List, Optional
from xml.etree.ElementTree import Element

from marshy import ExternalType
from marshy.types import ExternalItemType

from xsd2json_schemey.converter import ConverterException, TypeConverterABC
from xsd2json_schemey.converter.type_converter.child_converter import ChildConverter
from xsd2json_schemey.converter.type_converter.named_attr_converter import (
    NamedAttrConverter,
)
from xsd2json_schemey.converter.type_converter.simple_content_converter import (
    attribs_from_xml, attribs_to_xml,
)


@dataclass
class ObjectConverter(TypeConverterABC):
    json_schema: ExternalItemType
    child_converters: List[ChildConverter] = field(default_factory=list)
    attr_converters: List[NamedAttrConverter] = field(default_factory=list)

    def to_xml(self, json_value: ExternalType, target: Element):
        if json_value is None:
            return
        if not isinstance(json_value, dict):
            raise ConverterException(f"wrong_type:{json_value}")
        attribs_to_xml(json_value, self.attr_converters, target)
        for child_converter in self.child_converters:
            if child_converter.json_attr_name in json_value:
                child_value = json_value[child_converter.json_attr_name]
                child_element = Element(child_converter.tag_name)
                child_converter.type_converter.to_xml(child_value, child_element)
                target.append(child_element)

    def from_xml(self, xml_value: Optional[Element]) -> ExternalType:
        if xml_value is None:
            return
        result = attribs_from_xml(xml_value, self.attr_converters)
        for child_element in xml_value:
            child_converter = next(c for c in self.child_converters if c.tag_name == child_element.tag)
            result[child_converter.json_attr_name] = child_converter.type_converter.from_xml(child_element)
        return result
