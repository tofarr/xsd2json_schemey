from copy import deepcopy
from typing import Optional
from xml.etree.ElementTree import Element

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import (
    SchemaConverter,
    AttrConverterFactoryABC,
    AttrConverterABC,
)


class ExtendSimpleTypeConverterFactory(AttrConverterFactoryABC):

    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[AttrConverterABC]:
        if type_element.tag != f"{SCHEMA}simpleType":
            return
        restriction = type_element.find(f"{SCHEMA}restriction")
        if restriction is None:
            return
        base = restriction.attrib.get("base")
        if base is None or base.startswith("xsd:"):
            return

        type_element = deepcopy(type_element)
        base_type = schema_converter.type_elements[base]
        base_restriction = deepcopy(base_type.find(f"{SCHEMA}restriction"))
        base_restriction.extend(deepcopy(e) for e in restriction)
        type_element.remove(type_element.find(f"{SCHEMA}restriction"))
        type_element.append(base_restriction)
        result = schema_converter.create_attr_converter(type_element)
        return result
