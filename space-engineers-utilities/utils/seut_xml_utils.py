import os

import xml.etree.ElementTree as ET
import xml.dom.minidom


def get_relevant_sbc(path: str, sbc_type: str, subtype_id: str):
    """Returns the relevant element of an existing entry, if found."""

    for path, subdirs, files in os.walk(path):
        for name in files:
            if not name.endswith(".sbc"):
                continue
            with open(os.path.join(path, name)) as f:
                lines = f.read()
                if '<' + sbc_type + '>' in lines:
                    if '<SubtypeId>' + subtype_id + '</SubtypeId>' in lines:
                        
                        start = lines.find('<SubtypeId>' + subtype_id + '</SubtypeId>')
                        start = lines[:-start].rfind('<Definition')
                        end = start + lines[start:].find('</Definition>') + len('</Definition>')
                        return [os.path.join(path, name), lines, start, end]
                else:
                    return [os.path.join(path, name), lines, None, None]


def add_subelement(parent, name: str, value=None, override=False):
    """Adds a subelement to XML definition."""

    ignore_dupes = ['MountPoint', 'Model']
    
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


def update_subelement():

    return