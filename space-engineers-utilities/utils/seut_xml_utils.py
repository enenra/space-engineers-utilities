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


def update_add_subelement(parent, name: str, value=None, update=False, lines=None):
    """Depending on the input either updates or creates a subelement."""

    if update:
        return update_subelement(lines, name, value)
    else:
        return add_subelement(parent, name, value)


def add_subelement(parent, name: str, value=None):
    """Adds a subelement to XML definition."""

    ignore_dupes = ['MountPoint', 'Model']
    
    if not name in ignore_dupes:
        for elem in parent:
            if elem.tag == name:
                if value is not None:
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


def update_subelement(lines, name: str, value):
    """Updates an existing subelements to a new value."""

    entry = get_subelement(lines, name)
    entry_updated = str(value)
    return lines.replace(entry, str(entry_updated))


def get_subelement(lines: str, name: str):
    """Returns the specified subelement. -1 if not found."""

    if '<' + name in lines:
        start = lines.find('<' + name)
        if '</' + name + '>' in lines[start:]:
            start = lines[start:].find('>') + 1
            end = start + lines[start:].find('</' + name + '>')
            return lines[start:end]
        else:
            end = start + lines[start:].find('/>') + 2
            return lines[start:end]
    else:
        return [-1]


def update_add_attrib(element, name: str, value=None, update=False, lines=None):
    """Depending on the input either updates or creates an attribute."""

    if update:
        return update_attrib(lines, element, name, value)
    else:
        return add_attrib(element, name, value)


def add_attrib(element, name: str, value):
    """Adds an attribute to an element."""
    
    for elem in element:
        if elem.attrib == name:
            if value is not None:
                return elem.set(name, str(value))
            else:
                return elem

    return element.set(name, str(value))


def update_attrib(lines, element, name: str, value):
    """Adds an attribute to an element."""

    entry = get_subelement(lines, element)
    attrib = get_attrib(entry, name)

    entry_updated = entry.replace(name + "=\"" + attrib + "\"", name + "=\"" + str(value) + "\"")

    return lines.replace(entry, entry_updated)


def get_attrib(entry: str, name: str):
    """Returns the specified attribute. -1 if not found."""

    if entry.find(name + "=\"") != -1:
        start = entry.find(name + "=\"") + len(name) + 2
        end = start + entry[start:].find("\"")
        return entry[start:end]
    else:
        return -1