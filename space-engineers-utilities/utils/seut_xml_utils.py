import os

import xml.etree.ElementTree as ET
import xml.dom.minidom


def get_relevant_sbc(path: str, sbc_type: str, subtype_id: str):
    """Returns the relevant element of an existing entry, if found."""

    cubeblock_match = None

    for path, subdirs, files in os.walk(path):
        for name in files:
            if not name.endswith(".sbc"):
                continue
            with open(os.path.join(path, name)) as f:
                lines = f.read()
                if '<' + sbc_type + '>' in lines:
                    if '<SubtypeId>' + subtype_id + '</SubtypeId>' in lines:

                        tree = ET.parse(os.path.join(path, name))
                        root = tree.getroot()

                        if root.tag == "Definitions":
                            for cubeblocks in root:
                                for definition in cubeblocks:
                                    for id in definition:
                                        for entry in id:
                                            if entry.tag == 'SubtypeId':
                                                if entry.text == subtype_id:
                                                    cubeblock_match = definition
                                                    break

                                return [os.path.join(path, name), root, cubeblock_match]


def add_subelement(parent, name: str, value=None, override=False):
    """Adds a subelement to XML definition."""

    ignore_dupes = ['MountPoint']
    
    if not name in ignore_dupes:
        for elem in parent:
            if elem.tag == name:
                if override and value is not None:
                    elem.text = str(value)
                    return elem
                else:
                    return elem

    if value is None:
        return ET.SubElement(parent, name)
    else:
        subelement = ET.SubElement(parent, name)
        subelement.text = str(value)
        return subelement


def add_attrib(element, name: str, value, override=False):
    """Adds an attribute to an element."""
    
    for elem in element:
        if elem.attrib == name:
            if override and value is not None:
                return elem.set(name, str(value))
            else:
                return elem

    return element.set(name, str(value))