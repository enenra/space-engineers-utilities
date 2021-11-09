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
                        start = lines[:start].rfind('<Definition')
                        end = start + lines[start:].find('</Definition>') + len('</Definition>')
                        return [os.path.join(path, name), lines, start, end]
                else:
                    return [os.path.join(path, name), lines, None, None]
    
    return [None, None, None, None]


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
    entry_updated = '<' + name + '>' + str(value) + '</' + name + '>'
    return lines.replace(entry, str(entry_updated))

def update_add_optional_subelement(parent, name: str, value, update_sbc, lines):
    if update_sbc:
        if get_subelement(lines, name) == -1:
            return lines.replace('</Definition>', '<' + name + '>' + str(value) + '</' + name + '>\n</Definition>')
        else:
            return update_subelement(lines, name, str(value))
    else:
        return add_subelement(parent, name, str(value))


def get_subelement(lines: str, name: str):
    """Returns the specified subelement. -1 if not found."""

    if '<' + name + '>' in lines:
        start = lines.find('<' + name + '>')
        end = start + lines[start:].find('</' + name + '>') + len('</' + name + '>')
        return lines[start:end]

    elif '<' + name + ' ' in lines:
        start = lines.find('<' + name + ' ')
        end = start + lines[start:].find('/>') + 2
        return lines[start:end]

    else:
        return -1


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


def convert_back_xml(element, name: str, lines_entry: str) -> str:
    """Converts a temp xml entry back and replaces it inside the larger xml entry."""

    entry = ET.tostring(element, 'utf-8')
    entry = xml.dom.minidom.parseString(entry).toprettyxml()
    entry = entry[entry.find("\n") + 1:]

    start = lines_entry.find('<' + name + '>')
    end = lines_entry.find('</' + name + '>') + len('</' + name + '>')

    return lines_entry.replace(lines_entry[start:end], entry)


def format_entry(lines: str, depth=0) -> str:
    """Formats a given xml entry to a specified depth."""

    indent = "\t"
    lines_arr = lines.splitlines()
    entry = ""

    for line in lines_arr:
        
        remove = False
        line = indent * depth + line.strip()
            
        start = line.find('<')
        end = line.rfind('>')
        
        if line.count('<') <= 0 and line.count('>') <= 0:
            if line.strip() == "":
                remove = True
        elif line[start:start+4] == '<!--' and line[end-2:end+1] == '-->':
            pass
        elif line[end-1:end+1] == '/>':
            pass
        elif line.find('<!--') != -1 and line.find('/>') != -1:
            pass
        elif line[start:start+2] == '<?' and line[end-1:end+1] == '?>':
            pass
        elif line.count('<') >= 2 and line.count('>') >= 2 and line.count('</') == 1:
            pass
        elif line[start:start+2] == '</':
            depth -= 1
            line = line[1:]
        else:
            depth += 1
        
        if line.strip() != lines_arr[-1].strip():
            line = line + "\n"
        
        if not remove:
            entry += line

    return entry