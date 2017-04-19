import pytest
from tempfile import NamedTemporaryFile
from mcwriter.utils import (serialize_dotted_path_dict,
                            serialize_new_lists_input,
                            prepare_batch_data)


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


def test_serializing_new_lists_input_csv():
    # Fake inputs
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''name,contact.address,contact.country,confirm
Robin,Foobar,Czechia,True
Max,BarBar,Slovakia,False''')
    inputs.close()
    serialized = serialize_new_lists_input(inputs.name)

    expected = [{'name': 'Robin',
                 'contact': {'address': 'Foobar',
                             'country': 'Czechia'},
                 'confirm': 'True'},
                {'name': 'Max',
                 'contact': {'address': 'BarBar',
                             'country': 'Slovakia'},
                 'confirm': 'False'}]

    assert expected[0] == serialized[0]
    assert expected[1] == serialized[1]


def test_preparing_batch_data():
    template = {
        'method': 'POST',
        'path': '/lists',
        'body': None}

    data = [{'foo':'bar', 'baz':'qux'},
            {'foo':'bar2', 'baz': 'quxx'}]

    batch_data = prepare_batch_data(template, data)

    expected = [{'method': 'POST',
                 'path': '/lists',
                 'body': {'foo':'bar', 'baz':'qux'}},
                {'method': 'POST',
                 'path': '/lists',
                 'body': {'foo':'bar2', 'baz': 'quxx'}}]
    assert batch_data == expected
