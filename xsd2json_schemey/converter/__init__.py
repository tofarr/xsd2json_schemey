from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List, Dict
from xml.etree.ElementTree import Element

from injecty import get_instances
from marshy.types import ExternalType, ExternalItemType


class ConverterException(Exception):
    pass


class AttrConverterABC(ABC):
    """Converter for attributes / text to / from XML"""

    json_schema: ExternalItemType

    @abstractmethod
    def to_xml_attr(self, json_value: ExternalType) -> str:
        """Convert the value given from json to an XML attribute"""

    @abstractmethod
    def from_xml_attr(self, xml_value: str) -> ExternalType:
        """Convert the value given from an XML attribute to Json"""


class AttrConverterFactoryABC(ABC):
    """Factory for converter_bak for attributes"""

    @abstractmethod
    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[AttrConverterABC]:
        """Create a converter_bak based on the element given if possible"""


class TypeConverterABC(ABC):
    """Converter for attributes / text to / from XML"""

    json_schema: ExternalItemType

    @abstractmethod
    def to_xml(self, json_value: ExternalType, target: Element):
        """Convert the value given from json to an XML element. Typically only the attributes and child elements
        are processed as part of the conversion and the tag name is not updated."""

    @abstractmethod
    def from_xml(self, xml_value: Element) -> ExternalType:
        """
        Convert the value given from an XML Element to Json. Typically only the attributes and child elements
        are processed as part of the conversion and the tag name is ignored.
        """


class TypeConverterFactoryABC(ABC):
    """Factory for converter_bak for attributes"""

    @abstractmethod
    def create(
        self, type_element: Element, schema_converter: SchemaConverter
    ) -> Optional[TypeConverterABC]:
        """Create a converter based on the element given if possible"""


@dataclass
class SchemaConverter:
    type_elements: Dict[str, Element]
    attr_factories: List[AttrConverterFactoryABC] = field(
        default_factory=lambda: get_instances(AttrConverterFactoryABC)
    )
    element_factories: List[TypeConverterFactoryABC] = field(
        default_factory=lambda: get_instances(TypeConverterFactoryABC)
    )

    def create_attr_converter(self, element: Element) -> AttrConverterABC:
        for factory in self.attr_factories:
            converter = factory.create(element, self)
            if converter is not None:
                return converter
        raise ConverterException(f"no_factory_for:{element}")

    def create_named_attr_converter(self, name: str) -> AttrConverterABC:
        return self.create_attr_converter(self.type_elements[name])

    def create_element_converter(self, element: Element) -> TypeConverterABC:
        for factory in self.element_factories:
            converter = factory.create(element, self)
            if converter is not None:
                return converter
        raise ConverterException(f"no_factory_for:{element}")

    def create_named_element_converter(self, name: str) -> TypeConverterABC:
        return self.create_element_converter(self.type_elements[name])
