#!/usr/bin/env python3
"""Validate OpenAPI documents and bounded registration/MCP contract examples.

Run from the repository root after installing openapi-requirements.txt. These
examples check the HTTP view against AUTH-008/009/011, RFC 7591 and MCP 2025-11-25
Messages/Streamable HTTP. They do not exercise a server or establish conformance.
"""
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate
import yaml


class OpenApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {
            path.stem: yaml.safe_load(path.read_text())
            for path in sorted(Path("openapi").glob("*.yaml"))
        }

    def test_documents_are_valid_openapi(self):
        self.assertTrue(self.documents, "openapi/ has no descriptions")
        for name, document in self.documents.items():
            with self.subTest(document=name):
                self.assertTrue(str(document.get("openapi", "")).startswith("3.1"))
                self.assertTrue(document.get("paths"))
                validate(document)

    def check_payloads(self, document, pointer, valid, invalid):
        # Validate the operation's actual schema, including its references. The
        # whole document stays at the root so local component references resolve.
        validator = Draft202012Validator(
            {**self.documents[document], "$ref": pointer}, format_checker=FormatChecker()
        )
        for expected, payloads in ((True, valid), (False, invalid)):
            for payload in payloads:
                with self.subTest(pointer=pointer, expected=expected, payload=payload):
                    errors = list(validator.iter_errors(payload))
                    self.assertEqual(not errors, expected, str(errors))

    def test_registration_request(self):
        self.assertIn("uri", FormatChecker().checkers, "URI format checker is not installed")
        request = {"redirect_uris": ["https://client.example/callback"],
                   "token_endpoint_auth_method": "none"}
        self.check_payloads("sempods-core",
            "#/paths/~1_system~1auth~1register/post/requestBody/content/application~1json/schema",
            valid=[request, {"redirect_uris": request["redirect_uris"]},
                   {**request, "client_name#de": "Beispiel", "extension": {"v": 1}}],
            invalid=[{}, {"token_endpoint_auth_method": "none"},
                     {**request, "redirect_uris": []},
                     {**request, "redirect_uris": "https://client.example/callback"},
                     {**request, "redirect_uris": ["/callback"]},
                     {**request, "jwks": {"keys": []}, "jwks_uri": "https://client.example/keys"}])

    def test_registered_metadata(self):
        response = {"client_id": "dyn:example",
                    "redirect_uris": ["https://client.example/callback"],
                    "token_endpoint_auth_method": "none"}
        self.check_payloads("sempods-core",
            "#/paths/~1_system~1auth~1register/post/responses/201/content/application~1json/schema",
            valid=[response, {**response, "grant_types": ["authorization_code"]},
                   {**response, "grant_types": ["authorization_code", "refresh_token"],
                    "response_types": ["code"]}, {**response, "extension": True}],
            invalid=[{}, *[{k: v for k, v in response.items() if k != missing}
                           for missing in response],
                     {**response, "client_id": "svc:example"},
                     {**response, "token_endpoint_auth_method": "client_secret_basic"},
                     *[{**response, "grant_types": grants} for grants in
                       (["client_credentials"], ["authorization_code", "client_credentials"],
                        ["implicit"], ["password"], [])],
                     {**response, "response_types": ["token"]},
                     {**response, "response_types": []}])

    def test_registration_errors(self):
        self.check_payloads("sempods-core",
            "#/paths/~1_system~1auth~1register/post/responses/400/content/application~1json/schema",
            valid=[{"error": "invalid_redirect_uri"}, {"error": "invalid_client_metadata"}],
            invalid=[{}, {"error": 123}])

    def test_mcp_client_messages(self):
        result = {"jsonrpc": "2.0", "id": 1, "result": {}}
        error = {"jsonrpc": "2.0", "id": "r1",
                 "error": {"code": -32603, "message": "Internal error"}}
        self.check_payloads("module-mcp",
            "#/paths/~1_system~1mcp/post/requestBody/content/application~1json/schema",
            valid=[result, error, {**error, "error": {**error["error"], "data": [1]}},
                   {"jsonrpc": "2.0", "method": "initialize", "id": 1},
                   {"jsonrpc": "2.0", "method": "notifications/initialized"}],
            invalid=[[result], {"jsonrpc": "2.0", "result": {}},
                     {"jsonrpc": "2.0", "error": error["error"]},
                     {**result, "error": error["error"]},
                     *[{**error, "error": value} for value in
                       ({}, {"code": -32603}, {"message": "Internal error"},
                        {"code": "-32603", "message": "Internal error"},
                        {"code": 1.5, "message": "Internal error"},
                        {"code": -32603, "message": None})],
                     *[{**result, "id": value} for value in (None, True, {}, [], 1.5)]])

    def test_mcp_server_responses(self):
        error = {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid request"}}
        result = {"jsonrpc": "2.0", "id": 1, "result": {}}
        self.check_payloads("module-mcp",
            "#/paths/~1_system~1mcp/post/responses/200/content/application~1json/schema",
            valid=[result, {**error, "id": 1}],
            invalid=[{"jsonrpc": "2.0", "result": {}},
                     {**result, "error": error["error"]},
                     {**error, "result": {}},
                     {"jsonrpc": "2.0", "id": 1, "error": {}}])
        for response in ("BadTransportRequest", "InvalidOrigin", "McpChallenge"):
            self.check_payloads("module-mcp",
                f"#/components/responses/{response}/content/application~1json/schema",
                valid=[error], invalid=[{**error, "error": {}}, result])


if __name__ == "__main__":
    unittest.main()
