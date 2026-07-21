from django.core.exceptions import ValidationError
import xml.etree.ElementTree as ET


def validate_svg_xml(value):
    """Basic validation that value is valid XML with <svg> root."""
    try:
        tree = ET.fromstring(value.strip())
        if tree.tag != 'svg':
            raise ValidationError('Please check svg value')
    except ET.ParseError as e:
        raise ValidationError(f'Invalid XML: {e}')