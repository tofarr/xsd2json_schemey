from pathlib import Path
from xml.etree.ElementTree import Element

from xsd2json_schemey import SCHEMA
from xsd2json_schemey.finder import TypeElementFinderABC, TypeElementSearch


class IncludeFinder(TypeElementFinderABC):

    def find_type_elements(
        self, element: Element, working_dir: Path, search: TypeElementSearch
    ):
        for element in element.findall(SCHEMA + "include"):
            path = Path(working_dir, element.attrib["schemaLocation"])
            search.add_path(path)
