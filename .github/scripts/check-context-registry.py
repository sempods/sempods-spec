#!/usr/bin/env python3
"""Check actual Context OpenAPI examples/schemas and RDF semantics, not server conformance."""
import base64
import copy
import json
from pathlib import Path
import re
import unittest

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[2]
CORE = 'https://spec.example/openapi/sempods-core.yaml'
MODULE = 'https://spec.example/openapi/module-context-management.yaml'
SD = Namespace('http://www.w3.org/ns/sparql-service-description#')
SPS = Namespace('https://schema.sempods.org/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')

class RegistryRepresentations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = yaml.safe_load((ROOT / 'openapi/sempods-core.yaml').read_text())
        cls.module = yaml.safe_load((ROOT / 'openapi/module-context-management.yaml').read_text())
        cls.registry = Registry().with_resources((url, Resource.from_contents(doc, default_specification=DRAFT202012))
            for url, doc in ((CORE, cls.core), (MODULE, cls.module)))
        text = (ROOT / 'docs/guides/context-registry.md').read_text()
        cls.description, cls.catalogue, cls.empty = [json.loads(s) for s in re.findall(r'```json\n(.*?)\n```', text, re.S)]

    def validator(self, name):
        return Draft202012Validator({'$ref': CORE + '#/components/schemas/' + name},
            registry=self.registry, format_checker=FormatChecker())

    def graph(self, payload):
        return Graph().parse(data=json.dumps(payload), format='json-ld')

    def test_examples_validate_and_round_trip_as_default_graph_rdf(self):
        for name, payload in (('ContextDescription', self.description), ('ContextCatalogue', self.catalogue), ('ContextCatalogue', self.empty)):
            with self.subTest(name=name, payload=payload):
                self.validator(name).validate(payload)
                g = self.graph(payload)
                dataset = Dataset().parse(data=g.serialize(format='nt'), format='nquads')
                self.assertTrue(isomorphic(g, dataset.default_graph))
                self.assertTrue(isomorphic(g, self.graph(json.loads(g.serialize(format='json-ld')))))

    def test_description_identity_public_and_derived_address(self):
        g = self.graph(self.description); c = URIRef(self.description['@id'])
        self.assertEqual(set(g.objects(c, SD.name)), {c})
        self.assertEqual(set(g.objects(c, SPS.public)), {Literal(False)})
        address = str(next(g.objects(c, RDFS.seeAlso)))
        encoded = address.rsplit('/', 1)[1]
        self.assertNotIn('=', encoded)
        self.assertEqual(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)).decode(), str(c))
        for mode in ('readableContext', 'writableContext', 'manageableContext'):
            self.assertFalse(list(g.triples((None, SPS[mode], None))))

    def test_effective_modes_and_local_query_without_optional_label(self):
        c = URIRef(self.description['@id']); l = URIRef(self.catalogue['@id'])
        for modes in (('readableContext',), ('readableContext', 'writableContext'), ('readableContext', 'writableContext', 'manageableContext')):
            payload = copy.deepcopy(self.empty)
            payload[str(SD.namedGraph)] = [{'@id': str(c)}]
            for mode in modes: payload[str(SPS[mode])] = [{'@id': str(c)}]
            self.validator('ContextCatalogue').validate(payload)
            graph = self.graph(payload)
            for mode in modes: self.assertEqual(set(graph.objects(l, SPS[mode])), {c})
        trusted = self.graph(self.catalogue) + self.graph(self.description)
        query = f'SELECT ?c ?label WHERE {{ <{l}> <{SPS.writableContext}> ?c . OPTIONAL {{ ?c <{RDFS.label}> ?label }} }}'
        self.assertEqual(list(trusted.query(query)), [(c, Literal('Tasks'))])
        trusted.remove((c, RDFS.label, None))
        self.assertEqual(list(trusted.query(query)), [(c, None)])

    def test_empty_catalogue_retains_identity_and_type(self):
        self.assertEqual(len(self.graph(self.empty)), 1)
        for key in (SD.namedGraph, SPS.readableContext, SPS.writableContext, SPS.manageableContext):
            payload = copy.deepcopy(self.empty); payload[str(key)] = []
            self.validator('ContextCatalogue').validate(payload)
            self.assertTrue(isomorphic(self.graph(payload), self.graph(self.empty)))

    def test_legacy_and_malformed_payloads_are_rejected(self):
        invalid = []
        for key in ('@id', '@type', str(SD.name), str(SPS.public), str(RDFS.seeAlso)):
            payload = copy.deepcopy(self.description); del payload[key]; invalid.append(('ContextDescription', payload))
        invalid += [('ContextDescription', {'contextUri': self.description['@id']}), ('ContextCatalogue', {'contexts': [], 'writableContexts': []})]
        for key, value in ((str(SPS.public), [{'@value': 'false'}]), (str(SD.name), [{'@value': self.description['@id']}]), (str(SPS.readableContext), [{'@id': self.description['@id']}]), ('@context', {}), ('label', [{'@value': 'Tasks'}])):
            payload = copy.deepcopy(self.description); payload[key] = value; invalid.append(('ContextDescription', payload))
        payload = copy.deepcopy(self.catalogue); payload[str(SD.namedGraph)] = [self.description]; invalid.append(('ContextCatalogue', payload))
        payload = copy.deepcopy(self.catalogue); payload[str(SPS.writableContext)] = [{'@value': 'context#write'}]; invalid.append(('ContextCatalogue', payload))
        for name, payload in invalid:
            with self.subTest(name=name, payload=payload): self.assertFalse(self.validator(name).is_valid(payload))

    def test_all_success_routes_use_the_same_examples_and_schemas(self):
        for path, name, example in (('/_system/contexts', 'ContextCatalogue', self.catalogue), ('/_system/contexts/{contextPath}', 'ContextDescription', self.description)):
            op = self.core['paths'][path]['get']
            self.assertEqual(set(op['responses']['200']['content']), {'application/ld+json', 'application/n-quads'})
            content = op['responses']['200']['content']['application/ld+json']
            self.assertEqual(content['example'], example)
            self.assertEqual(content['schema']['$ref'], '#/components/schemas/' + name)
            self.assertIn({'$ref': '#/components/parameters/IfNoneMatch'}, op['parameters'])
            self.assertTrue({'200', '304', '401', '406'} <= set(op['responses']))
        put = self.module['paths']['/_system/contexts/{contextPath}']['put']
        self.assertEqual(set(put['requestBody']['content']), {'application/json'})
        self.assertFalse(put['requestBody']['required'])
        for code in ('200', '201'):
            pointer = MODULE + '#/paths/~1_system~1contexts~1{contextPath}/put/responses/' + code + '/content/application~1ld+json/schema'
            Draft202012Validator({'$ref': pointer}, registry=self.registry).validate(self.description)
            self.assertEqual(put['responses'][code]['content']['application/ld+json']['example'], self.description)
        self.assertIn('406', put['responses'])
        self.assertNotIn('304', put['responses'])
        self.assertIn('409', self.module['paths']['/_system/contexts/{contextPath}']['delete']['responses'])

    def test_explicit_datatypes_preserve_native_public_and_registry_strings(self):
        payload = copy.deepcopy(self.description)
        payload[str(SPS.public)][0]['@type'] = 'http://www.w3.org/2001/XMLSchema#boolean'
        payload[str(RDFS.label)][0]['@type'] = 'http://www.w3.org/2001/XMLSchema#string'
        self.validator('ContextDescription').validate(payload)
        self.assertEqual(set(self.graph(payload).objects(URIRef(payload['@id']), SPS.public)), {Literal(False)})

    def test_vocabulary_declares_all_summary_predicates(self):
        g = Graph().parse(ROOT / 'vocabulary/sempods.ttl', format='turtle')
        for name in ('public', 'readableContext', 'writableContext', 'manageableContext'):
            self.assertTrue(list(g.triples((SPS[name], None, None))))

if __name__ == '__main__':
    unittest.main()
