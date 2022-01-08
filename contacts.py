#!/usr/bin/env python3
"""Command line tool for maintaining VCF contacts."""

from collections import defaultdict
from pathlib import Path
from typing import Mapping

CONTACTS_PATH = Path('~/pim/contacts/contacts.vcf').expanduser()

class Contact:
    """A contact."""

    def __init__(self, attrs):
        # type: (Mapping[str, set[str]]) -> None
        """Initialize a contact.

        Parameters:
            attrs: Attributes of the contact.
        """
        self.attrs = attrs

    def __getitem__(self, key):
        # type: (str) -> set[str]
        return self.attrs[key]

    def get_only(self, key):
        # type: (str) -> str
        """Get the only value of an attribute.

        Parameters:
            key (str): The attribute.

        Returns:
            str: The value.
        """
        return list(self.attrs[key])[0]

    def to_vcf(self):
        # type: () -> str
        """Convert the contact to a VCF string.

        Returns:
            str: The VCF string.
        """
        result = []
        result.append('BEGIN:VCARD')
        result.append(f'FN:{list(self.attrs["FN"])[0]}')
        result.append(f'N:{list(self.attrs["N"])[0]}')
        for val in sorted(self.attrs['NICKNAME']):
            result.append(f'NICKNAME:{val}')
        for key, vals in sorted(self.attrs.items()):
            if key in ('FN', 'N', 'NICKNAME'):
                continue
            for val in sorted(vals):
                result.append(f'{key}:{val}')
        result.append('END:VCARD')
        return '\n'.join(result)


def read_contacts(path):
    # type: (Path) -> list[Contact]
    """Read contacts.

    Parameters:
        path (Path): The path to the contacts file.

    Returns:
        list[Contact]: A list of contacts.
    """
    with path.open() as fd:
        contents = fd.read()
    contacts = []
    for record in contents.split('\n\n'):
        lines = record.splitlines()
        assert lines[0] == 'BEGIN:VCARD' and lines[-1] == 'END:VCARD'
        attrs = defaultdict(set)
        for line in lines[1:-1]:
            key, val = line.split(':', maxsplit=1)
            attrs[key].add(val)
        contacts.append(Contact(attrs))
    return contacts


def lint(contacts):
    # type: (list[Contact]) -> None
    """Check the contacts for errors.

    Parameters:
        contacts (list[Contact]): The list of contacts
    """
    existing = defaultdict(set) # type: dict[str, set[str]]
    for contact in contacts:
        # check that exactly one FN and N exist
        names_okay = True
        for attr in ('FN', 'N'):
            vals = contact[attr]
            if len(vals) == 0:
                names_okay = False
                print(f'missing {attr}: {" ".join(contact.to_vcf().splitlines())}')
            elif len(vals) > 1:
                names_okay = False
                print(f'multiple {attr}: {", ".join(sorted(vals))}')
        # check that FN and N match
        if names_okay:
            formatted_name = contact.get_only('FN')
            name = contact.get_only('N')
            names = name.split(';')
            if len(names) != 5:
                print(f'invalid N: {name}')
            recreated_name = ' '.join(names[i] for i in (1, 2, 0)).replace('  ', ' ').strip()
            if formatted_name != recreated_name:
                print(f'mismatched N and FN: {formatted_name} != {recreated_name}')
        # check for duplicate ADR, EMAIL, TEL, or URL
        for attr in ('ADR', 'EMAIL', 'TEL', 'URL'):
            for val in contact.attrs[attr]:
                val = val.strip()
                if val and val in existing[attr]:
                    print(f'duplicate {attr}: {val}')
                existing[attr].add(val)


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    contacts = read_contacts(CONTACTS_PATH)
    lint(contacts)


if __name__ == '__main__':
    main()
