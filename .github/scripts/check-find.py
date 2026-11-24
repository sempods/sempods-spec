"""Check the Find examples as RDF datasets and as OpenAPI response bodies."""
from pathlib import Path
import unittest

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from pyld import jsonld
from rdflib import BNode, Dataset, Graph, Literal, Namespace, RDF, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[2]
CASES = yaml.safe_load((ROOT / 'examples/find/responses.yaml').read_text())
API = yaml.safe_load((ROOT / 'openapi/sempods-core.yaml').read_text())
POD = Namespace('https://pod.example/')
SCHEMA = Namespace('https://schema.org/')
LINK = URIRef('https://schema.sempods.org/findResult')
DOC = POD['articles/42']
A, B = (POD['_system/contexts/' + label] for label in ('A', 'B'))
STORE = Dataset().parse(data=CASES['pod'], format='nquads')


def jsonld_to_nquads(document):
    return jsonld.to_rdf(document, {'format': 'application/n-quads', 'processingMode': 'json-ld-1.1'})


def read_pair(pair):
    return (Dataset().parse(data=jsonld_to_nquads(pair['jsonld']), format='nquads'),
            Dataset().parse(data=pair['nquads'], format='nquads'))


def union(dataset):
    graph = Graph()
    for s, p, o, _ in dataset.quads():
        graph.add((s, p, o))
    return graph


def quad_graph(dataset):
    # Comparing named graphs separately loses the identity of a blank node shared across them.
    graph = Graph()
    for s, p, o, g in dataset.quads():
        quad = BNode()
        graph.add((quad, RDF.subject, s))
        graph.add((quad, RDF.predicate, p))
        graph.add((quad, RDF.object, o))
        if g != dataset.default_graph.identifier:
            graph.add((quad, URIRef('urn:fixture:graph'), g))
    return graph


def response(name, mode='grouped'):
    return Dataset().parse(data=CASES[name][mode]['nquads'], format='nquads')


def selected_contexts(case):
    readable = set(map(URIRef, case.get('readable', [A, B])))
    requested = case['request'].get('contexts', readable)
    return readable.intersection(map(URIRef, requested))


def api_schema(schema):
    return Draft202012Validator(dict(schema, components=API['components']),
                                format_checker=FormatChecker(formats=['iri']))


class FindResponses(unittest.TestCase):
    def test_paired_representations(self):
        response_ref = '#/components/responses/FindGraph'
        for method in ('get', 'post'):
            operation = API['paths']['/_system/find'][method]
            self.assertEqual(operation['responses']['200']['$ref'], response_ref)
        media = API['components']['responses']['FindGraph']['content']
        wire = api_schema(media['application/ld+json']['schema'])
        grouped = api_schema({'$ref': '#/components/schemas/FindContextGraphs'})
        for name, case in CASES.items():
            if name in ('pod', 'anonymous-group'):
                continue
            with self.subTest(name=name):
                for mode in ('flat', 'grouped'):
                    pair = case[mode]
                    wire.validate(pair['jsonld'])
                    left, right = read_pair(pair)
                    self.assertTrue(isomorphic(quad_graph(left), quad_graph(right)), mode)
                    if mode == 'grouped':
                        grouped.validate(pair['jsonld'])
                        self.assertEqual(len(right.default_graph), 0)
                        self.check_placement(right, selected_contexts(case))
                    else:
                        self.assertTrue(all(g == right.default_graph.identifier for *_, g in right.quads()))
                self.assertTrue(isomorphic(union(response(name)), response(name, 'flat').default_graph))

    def check_placement(self, dataset, allowed):
        stored, answer = union(STORE), union(dataset)
        for s, p, o, context in dataset.quads():
            self.assertIn(context, allowed)
            source = STORE.graph(context)
            if (s, p, o) in stored:
                self.assertIn((s, p, o), source)
            elif p == LINK:
                self.assertIsInstance(o, BNode)
                self.assertIn((s, None, None), source)
            else:
                self.assertIsInstance(s, BNode)
                hit = answer.value(predicate=LINK, object=s, any=False)
                self.assertIsInstance(hit, URIRef)
                self.assertIn((hit, None, None), source)

    def test_plain_hit(self):
        graph = response('plain').graph(A)
        self.assertEqual(set(graph), {(DOC, RDF.type, SCHEMA.Article)})
        multi = response('plain-array').graph(A)
        self.assertEqual(set(multi.subjects(RDF.type, SCHEMA.Article)), {DOC, POD['articles/43']})
        self.assertFalse(list(multi.triples((None, LINK, None))))

    def test_bare_link(self):
        self.assertEqual(CASES['bare']['request']['type'], [str(SCHEMA.Article)])
        self.assertIn((DOC, RDF.type, SCHEMA.Article), STORE.graph(A))
        self.assertIn((DOC, SCHEMA.name, Literal('Harbour map')), STORE.graph(A))
        graph = response('bare').graph(A)
        self.assertEqual(len(graph), 1)
        self.assertIsInstance(graph.value(DOC, LINK), BNode)

    def test_id_only_node_contributes_no_hit_statement(self):
        node = {'@id': str(DOC)}
        for mode, document in (
            ('flat', [node]),
            ('grouped', [{'@id': str(A), '@graph': [node]}]),
        ):
            with self.subTest(mode=mode):
                self.assertEqual(jsonld_to_nquads(document).strip(), '')

    def test_hits_with_both_one_or_neither_descriptive_fact(self):
        case = CASES['optional-description']
        self.assertEqual(selected_contexts(case), {A})
        source = STORE.graph(A)
        answer = response('optional-description').graph(A)
        expected = {
            POD['atlas/book']: {RDF.type, SCHEMA.name},
            POD['atlas/page']: {RDF.type},
            POD['atlas/key']: {SCHEMA.name},
            POD['atlas/draft']: set(),
        }
        matching = {s for s, p, o in source if p in (SCHEMA.name, SCHEMA.description)
                    and case['request']['text'] in str(o).lower()}
        self.assertEqual(matching, set(expected))
        self.assertEqual(set(answer.subjects()), matching)
        for hit, facts in expected.items():
            with self.subTest(hit=hit):
                for graph in (source, answer):
                    self.assertEqual(set(graph.predicates(hit)) & {RDF.type, SCHEMA.name}, facts)
        self.assertIn((POD['atlas/draft'], SCHEMA.description, Literal('Draft for an atlas')), answer)

    def test_known_match(self):
        data = response('known-match')
        self.assertIn((DOC, RDF.type, SCHEMA.Article), data.graph(A))
        graph = data.graph(B)
        observation = graph.value(DOC, LINK)
        self.assertIsInstance(observation, BNode)
        self.assertEqual(graph.value(observation, SCHEMA.text), STORE.graph(B).value(DOC, SCHEMA.description))
        self.assertFalse(list(data.graph(A).objects(DOC, LINK)))

    def test_a_linked_topic_can_match_as_a_subject_in_its_own_context(self):
        topic = POD['topics/climate']
        self.assertIn((DOC, SCHEMA.about, topic), STORE.graph(A))
        self.assertNotIn((topic, None, None), STORE.graph(A))
        self.assertIn((topic, SCHEMA.name, Literal('Climate change')), STORE.graph(B))
        for name, contexts, expected_hits in (
            ('article-via-topic', {A}, {DOC}),
            ('article-and-topic', {A, B}, {DOC, topic}),
        ):
            with self.subTest(name=name):
                self.assertEqual(selected_contexts(CASES[name]), contexts)
                answer = union(response(name))
                self.assertIn((DOC, SCHEMA.about, topic), answer)
                self.assertEqual((topic, None, None) in answer, topic in expected_hits)
                self.assertEqual(set(answer.subjects(LINK, None)), expected_hits)

    def test_repeated_and_split_observations(self):
        for name in ('repeated', 'split'):
            with self.subTest(name=name):
                data = response(name)
                observation = data.graph(A).value(DOC, LINK)
                self.assertIsInstance(observation, BNode)
                self.assertEqual(data.graph(B).value(observation, SCHEMA.text), Literal('Harbour lantern'))
                self.assertEqual(list(data.graph(B).objects(DOC, LINK)), [observation] if name == 'repeated' else [])
                self.assertFalse(list(data.graph(A).objects(observation, SCHEMA.text)))

    def test_independent_observations_at_limit_one(self):
        case = CASES['independent']
        self.assertEqual(case['request']['limit'], 1)
        lists = {URIRef(context): list(map(URIRef, hits)) for context, hits in case['rankedLists'].items()}
        self.assertEqual(set(lists), selected_contexts(case))
        self.assertEqual(set(lists[A]).intersection(lists[B]), {DOC})
        data = response('independent')
        observations = []
        for context, position in ((A, 2), (B, 7)):
            matching = {subject for subject, predicate, value in STORE.graph(context)
                        if predicate in (SCHEMA.name, SCHEMA.description)
                        and case['request']['text'] in str(value).lower()}
            self.assertCountEqual(lists[context], matching)
            self.assertEqual(lists[context].index(DOC) + 1, position)
            graph = data.graph(context)
            self.assertEqual(set(graph.subjects(LINK, None)), {DOC})
            [observation] = graph.objects(DOC, LINK)
            self.assertIsInstance(observation, BNode)
            self.assertEqual(graph.value(observation, SCHEMA.position), Literal(position))
            observations.append(observation)
        self.assertNotEqual(*observations)

    def test_selected_evidence(self):
        for name in ('match-only-in-B', 'match-also-in-A', 'empty-selection'):
            with self.subTest(name=name):
                case = CASES[name]
                request = case['request']
                selected = selected_contexts(case)
                self.assertEqual(selected, set() if name == 'empty-selection' else {A})
                self.assertIn(request['text'], str(STORE.graph(B).value(DOC, SCHEMA.description)).lower())
                evidence = {o for context in selected
                            for _, p, o in STORE.graph(context).triples((DOC, None, None))
                            if p in (SCHEMA.name, SCHEMA.description) and request['text'] in str(o).lower()}
                graph = union(response(name))
                if name == 'match-also-in-A':
                    self.assertEqual(evidence, {Literal('Harbour map')})
                    self.assertEqual(set(graph.objects(None, SCHEMA.text)), evidence)
                    self.assertIn((DOC, SCHEMA.name, Literal('Harbour map')), graph)
                    self.assertNotIn(Literal('Harbour lantern'), set(graph.objects()))
                else:
                    self.assertFalse(evidence)
                    self.assertEqual(len(graph), 0)

    def test_stored_vocabulary_keeps_its_source(self):
        data = response('stored-vocabulary')
        fact = (DOC, LINK, POD['notes/saved'])
        self.assertIn(fact, STORE.graph(A))
        self.assertIn(fact, data.graph(A))
        self.assertTrue(list(data.graph(B).triples((DOC, None, None))))
        self.assertNotIn(fact, data.graph(B))

    def test_default_graph_wrapper_and_anonymous_graph(self):
        case = CASES['anonymous-group']
        flat, invalid = case['flat'], case['invalid']
        wire = api_schema(API['components']['responses']['FindGraph']['content']['application/ld+json']['schema'])
        grouped = api_schema({'$ref': '#/components/schemas/FindContextGraphs'})
        wire.validate(flat['jsonld'])
        self.assertFalse(grouped.is_valid(flat['jsonld']))
        self.assertFalse(wire.is_valid(invalid['jsonld']))
        named_pair = CASES['bare']['grouped']
        named = named_pair['jsonld']
        self.assertEqual(named, flat['jsonld'] | {'@id': str(A)})
        single_node = named | {'@graph': named['@graph'][0]}
        for document in (named, [named], single_node, [single_node]):
            grouped.validate(document)
            wire.validate(document)
            left, right = read_pair({'jsonld': document, 'nquads': named_pair['nquads']})
            self.assertTrue(isomorphic(quad_graph(left), quad_graph(right)))
        bare = response('bare', 'flat').default_graph
        for mode, pair in (('flat', flat), ('invalid', invalid)):
            with self.subTest(mode=mode):
                left, right = read_pair(pair)
                self.assertTrue(isomorphic(quad_graph(left), quad_graph(right)))
                self.assertTrue(isomorphic(union(left), bare))
                [(_, _, observation, graph)] = left.quads()
                self.assertIsInstance(observation, BNode)
                if mode == 'flat':
                    self.assertEqual(graph, left.default_graph.identifier)
                else:
                    self.assertIsInstance(graph, BNode)
                    self.assertNotEqual(graph, observation)
                    self.assertNotIn(graph, selected_contexts(case))


if __name__ == '__main__':
    unittest.main()
