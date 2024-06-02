from injecty import InjectyContext

from xsd2json_schemey.converter import ElementConverterABC
from xsd2json_schemey.converter.boolean_converter import BooleanConverter
from xsd2json_schemey.converter.enumeration_converter import EnumerationConverter
from xsd2json_schemey.finder import TypeElementFinderABC
from xsd2json_schemey.finder.include_finder import IncludeFinder
from xsd2json_schemey.finder.type_element_finder import TypeElementFinder

priority = 100


def configure(context: InjectyContext) -> None:
    context.register_impls(TypeElementFinderABC, [TypeElementFinder, IncludeFinder])
    context.register_impls(
        ElementConverterABC, [BooleanConverter, EnumerationConverter, NumberConverter]
    )
