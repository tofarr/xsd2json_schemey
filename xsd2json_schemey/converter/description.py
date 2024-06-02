from typing import Optional
from xml.etree.ElementTree import Element

from marshy.types import ExternalItemType

from xsd2json_schemey import SCHEMA


def get_description(element: Element) -> Optional[str]:
    documentation = element.find(f".//{SCHEMA}documentation")
    if documentation is None:
        return
    description = documentation.find(f".//Description")
    if description:
        return (description.text or "").strip()
    return (documentation.text or "").strip()


def add_description(element: Element, result: ExternalItemType):
    description = get_description(element)
    if description is not None:
        result["description"] = description
