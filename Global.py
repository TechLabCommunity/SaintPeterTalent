import xml.etree.ElementTree as ET

PATH_CONFIG = './config.xml'

def get_value_config(fromroot, key):
    return ET.parse(PATH_CONFIG).getroot().find(fromroot).find(key).text
