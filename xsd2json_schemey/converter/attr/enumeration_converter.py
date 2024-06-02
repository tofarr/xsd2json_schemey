from typing import Optional
from xml.etree.ElementTree import Element

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.converter import SchemaConverter, AttrConverterFactoryABC
from xsd2json_schemey.converter.attr.string_converter import StringConverter
from xsd2json_schemey.converter.description import add_description


class EnumerationConverterFactory(AttrConverterFactoryABC):

    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[StringConverter]:
        if type_element.tag != f"{SCHEMA}simpleType":
            return
        restriction = type_element.find(f"{SCHEMA}restriction")
        if restriction is None or restriction.attrib.get("base") != "xsd:string":
            return
        values = restriction.findall(f"{SCHEMA}enumeration")
        if not values:
            return
        result = {"enum": [v.attrib["value"] for v in values]}
        add_description(type_element, result)
        return StringConverter(result)
