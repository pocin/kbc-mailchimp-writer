import pytest
from mcwriter.utils import serialize_dotted_path_dict


def test_serializing_new_lists():
    flat = {'name': 'Robin',
            'contact.address': 'Foobar',
            'contact.country': 'Czechia',
            'confirm': True}
    expected = {
        'name': 'Robin',
        'contact': {
            'address': 'Foobar',
            'country': 'Czechia'},
        'confirm': True}
    serialized = serialize_dotted_path_dict(flat)
    assert expected == serialized
