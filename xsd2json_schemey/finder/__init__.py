from __future__ import annotations
import os
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set, Optional, Union
from xml.etree.ElementTree import Element, parse

from injecty import get_instances


class TypeElementFinderException(Exception):
    pass


class TypeElementFinderABC(ABC):

    @abstractmethod
    def find_type_elements(
        self, element: Element, working_dir: Path, search: TypeElementSearch
    ):
        """Find type elements within the element given, and place them in the results dictionary given"""


@dataclass
class TypeElementSearch:
    finders: List[TypeElementFinderABC] = field(
        default_factory=lambda: get_instances(TypeElementFinderABC)
    )
    processed_paths: Set[Path] = field(default_factory=set)
    results: Dict[str, Element] = field(default_factory=dict)
    priority: int = 100

    def add_path(self, path: Union[Path, str]) -> bool:
        if isinstance(path, str):
            path = Path(path)
        path = path.absolute()
        if path in self.processed_paths:
            return False
        self.processed_paths.add(path)
        tree = parse(path)
        self.add_xml(tree.getroot(), path.parent)
        return True

    def add_xml(self, element: Element, working_dir: Optional[Path]):
        if working_dir is None:
            working_dir = os.getcwd()
        for finder in self.finders:
            finder.find_type_elements(element, working_dir, self)


def find_type_elements(path: Union[Path, str]) -> Dict[str, Element]:
    search = TypeElementSearch()
    search.add_path(path)
    return search.results
