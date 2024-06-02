from pathlib import Path
from xml.etree.ElementTree import Element

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.finder import TypeElementFinderABC, TypeElementSearch


class TypeElementFinder(TypeElementFinderABC):

    def find_type_elements(
        self, element: Element, working_dir: Path, search: TypeElementSearch
    ):
        self.find_element_of_type("simpleType", element, search)
        self.find_element_of_type("complexType", element, search)
        self.find_element_of_type("element", element, search)
        self.find_element_of_type("attributeGroup", element, search)

    def find_element_of_type(
        self, tag_name: str, parent: Element, search: TypeElementSearch
    ):
        for element in parent.findall(".//" + SCHEMA + tag_name):
            name = element.attrib.get("name")
            if name:
                search.results[name] = element
