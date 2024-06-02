import dataclasses
from copy import deepcopy
from typing import Optional, Dict
from xml.etree.ElementTree import Element

from marshy.types import ExternalItemType

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import (
    SchemaConverter, TypeConverterABC, TypeConverterFactoryABC,
)
from xsd2json_schemey.converter.type_converter.simple_content_converter import (
    named_attr_converters
)


class ComplexContentConverterFactory(TypeConverterFactoryABC):
    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[TypeConverterABC]:
        if type_element.tag != f"{SCHEMA}complexType":
            return
        complex_content = type_element.find(f".//{SCHEMA}complexContent")
        if complex_content is None:
            return
        extension = complex_content.find(f".//{SCHEMA}extension")
        if extension is None:
            return

        base = extension.attrib.get("base")
        converter = schema_converter.create_named_element_converter(base)
        base = schema_converter.type_elements[base]
        attr_converters = list(named_attr_converters(base, schema_converter))
        extension_converters = named_attr_converters(extension, schema_converter)
        attr_converters.extend(extension_converters)

        # noinspection PyDataclass
        json_schema = deepcopy(converter.json_schema)
        properties: Dict[str, ExternalItemType] = json_schema["properties"]
        for converter in extension_converters:
            properties[converter.json_attr_name] = converter.attr_converter.json_schema
        result = dataclasses.replace(converter, json_schema=json_schema, attr_converters=attr_converters)

        return result
