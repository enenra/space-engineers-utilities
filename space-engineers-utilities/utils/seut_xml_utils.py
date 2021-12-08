import os

import xml.etree.ElementTree as ET
import xml.dom.minidom


def get_relevant_sbc(path: str, sbc_type: str, container_name: str, subtype_id: str) -> list:
    """Returns the relevant element of an existing entry, if found."""

    last_sbc = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if not name.endswith(".sbc"):
                continue
            with open(os.path.join(path, name)) as f:
                lines = f.read()
                if '<' + sbc_type + '>' in lines:
                    entries_start = lines.find('<' + sbc_type + '>') + len('<' + sbc_type + '>')
                    entries_end = lines.find('</' + sbc_type + '>')
                    entries = lines[entries_start:entries_end]
                    last_sbc =  [os.path.join(path, name), lines]

                    if '<SubtypeId>' + subtype_id + '</SubtypeId>' in entries:
                        start = entries.find('<SubtypeId>' + subtype_id + '</SubtypeId>')
                        start = entries[:start].rfind('<' + container_name)
                        end = start + entries[start:].find('</' + container_name + '>') + len('</' + container_name + '>')
                        return [os.path.join(path, name), lines, entries_start + start, entries_end + end]
                        
    if last_sbc != []:
        return [last_sbc[0], last_sbc[1], None, None]
    else:
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


def update_subelement(lines: str, name: str, value, attrib: str = None) -> str:
    """Updates an existing subelements to a new value."""

    entry = get_subelement(lines, name, attrib)

    if attrib is not None:
        entry_updated = f"<{name} name=\"{attrib}\">{str(value)}</{name}>"
    else:
        entry_updated = f"<{name}>{str(value)}</{name}>"

    return lines.replace(str(entry), str(entry_updated))


def update_add_optional_subelement(parent, name: str, value, update_sbc: bool, lines: str) -> str:
    """Updates or adds an optional subelement depending on the parameters given."""

    if update_sbc:
        if get_subelement(lines, name) == -1:
            return lines.replace('</Definition>', '<' + name + '>' + str(value) + '</' + name + '>\n</Definition>')
        else:
            return update_subelement(lines, name, str(value))
    else:
        return add_subelement(parent, name, str(value))


def get_subelement(lines: str, name: str, attrib: str = None):
    """Returns the specified subelement. -1 if not found."""
    
    if attrib is not None and f"<{name} name=\"{attrib}\">" in lines:
        start = lines.find(f"<{name} name=\"{attrib}\">")
        end = start + lines[start:].find(f"</{name}>") + len(f"</{name}>")
        return lines[start:end]

    elif f"<{name}>" in lines:
        start = lines.find(f"<{name}>")
        end = start + lines[start:].find(f"</{name}>") + len(f"</{name}>")
        return lines[start:end]

    elif f"<{name} " in lines:
        start = lines.find(f"<{name} ")
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

    return lines.replace(str(entry), entry_updated)


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


def format_entry(lines: str, depth: int = 0) -> str:
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