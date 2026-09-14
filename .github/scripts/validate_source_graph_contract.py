#!/usr/bin/env python3
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'catalog/schema/source-graph.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
D = 'sha256:' + 'a' * 64


def frontend(language, implementation, extensions):
    return {
        'language': language,
        'implementation': implementation,
        'version': 'fixture-1',
        'extensions': extensions,
        'capabilities': [
            {'capability': 'parse', 'support': 'supported', 'note': None},
            {'capability': 'imports', 'support': 'supported', 'note': None},
            {'capability': 'packages', 'support': 'partial', 'note': 'fixture capability'},
        ],
    }


def graph(language='typescript', implementation='oxc', extensions=None):
    extensions = extensions or ['ts', 'tsx']
    return {
        'format_version': 1,
        'kind': 'source-graph',
        'source_digest': D,
        'frontends': [frontend(language, implementation, extensions)],
        'nodes': [
            {'id': 'file:src/main', 'path': 'src/main.ts', 'language': language, 'kind': 'file', 'generated': False, 'metadata': {}},
            {'id': 'file:src/service', 'path': 'src/service.ts', 'language': language, 'kind': 'file', 'generated': False, 'metadata': {}},
        ],
        'edges': [
            {'from': 'file:src/main', 'to': 'file:src/service', 'kind': 'runtime', 'resolution': 'local', 'specifier': './service', 'line': 1}
        ],
        'coverage': {'files_discovered': 2, 'files_parsed': 2, 'files_failed': 0, 'edges_resolved': 1, 'edges_unresolved': 0, 'complete': True},
        'not_checked': ['compiler-grade type semantics'],
    }


for language, implementation, extensions in [
    ('typescript', 'oxc', ['ts', 'tsx']),
    ('python', 'fixture-python', ['py']),
    ('rust', 'fixture-rust', ['rs']),
    ('go', 'fixture-go', ['go']),
]:
    value = graph(language, implementation, extensions)
    value['nodes'][0]['path'] = f'src/main.{extensions[0]}'
    value['nodes'][1]['path'] = f'src/service.{extensions[0]}'
    VALIDATOR.validate(value)

for mutation in ['wrong-version', 'unknown-kind', 'invalid-resolution', 'negative-coverage']:
    value = graph()
    if mutation == 'wrong-version':
        value['format_version'] = 2
    elif mutation == 'unknown-kind':
        value['edges'][0]['kind'] = 'magic'
    elif mutation == 'invalid-resolution':
        value['edges'][0]['resolution'] = 'guessed'
    else:
        value['coverage']['files_failed'] = -1
    assert not VALIDATOR.is_valid(value), mutation

# Schema cannot prove graph referential integrity or truthful coverage; semantic consumers must.
print('Source Graph v1 schema and cross-language fixtures passed')
