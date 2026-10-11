#!/usr/bin/env python3
"""Transport-boundary tests, independent of any product evidence schema."""
import copy
import json
import unittest

import strict_json as strict


class StrictJSONTests(unittest.TestCase):
    def test_finite_json_roundtrip_and_legacy_bytes(self):
        value = {"z": [None, True, False, 0, -3, 1.25, -0.0], "a": "é\r\n🙂"}
        before = copy.deepcopy(value)
        raw = strict.dumps(value)
        self.assertEqual(raw, json.dumps(value, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=False, allow_nan=False).encode())
        self.assertEqual(strict.loads(raw), value)
        self.assertEqual(value, before)

    def test_all_nonfinite_values_rejected_at_any_depth(self):
        for number in (float("nan"), float("inf"), -float("inf")):
            for value in (number, [number], {"a": [0, {"b": number}]}):
                with self.assertRaisesRegex(strict.StrictJSONError, "^non-finite-number$"):
                    strict.dumps(value)

    def test_constants_and_overflow_rejected_on_load(self):
        for token in ("NaN", "Infinity", "-Infinity", "1e9999", "-1e9999"):
            with self.subTest(token=token):
                with self.assertRaisesRegex(strict.StrictJSONError, "^non-finite-number$"):
                    strict.loads('{"x":' + token + '}')

    def test_duplicate_keys_including_escaped_spelling_rejected(self):
        for raw in ('{"a":1,"a":1}', '{"x":{"a":0,"a":1}}',
                    r'{"a":1,"\u0061":2}'):
            with self.assertRaisesRegex(strict.StrictJSONError, "^duplicate-object-key$"):
                strict.loads(raw)

    def test_same_key_in_different_objects_allowed(self):
        self.assertEqual(strict.loads('[{"a":1},{"a":2}]'), [{"a": 1}, {"a": 2}])

    def test_non_string_object_keys_rejected(self):
        for key in (0, True, None, 1.5):
            with self.assertRaisesRegex(strict.StrictJSONError, "^non-string-object-key$"):
                strict.dumps({key: "x"})

    def test_no_implicit_custom_object_or_tuple_conversion(self):
        class CustomDict(dict):
            def items(self):
                self.fail_if_called = True
                raise AssertionError("must not invoke custom behavior")
        for value in ((1, 2), {1}, object(), b"x", CustomDict(a=1)):
            with self.assertRaisesRegex(strict.StrictJSONError, "^unsupported-json-type$"):
                strict.dumps(value)

    def test_cycles_rejected_but_shared_subtrees_allowed(self):
        value = []; value.append(value)
        with self.assertRaisesRegex(strict.StrictJSONError, "^cyclic-input$"):
            strict.dumps(value)
        mapping = {}; mapping["self"] = mapping
        with self.assertRaisesRegex(strict.StrictJSONError, "^cyclic-input$"):
            strict.dumps(mapping)
        child = [1, 2]
        self.assertEqual(strict.loads(strict.dumps([child, child])), [[1, 2], [1, 2]])

    def test_depth_boundary(self):
        value = 0
        for _ in range(strict.MAX_DEPTH):
            value = [value]
        self.assertEqual(strict.loads(strict.dumps(value)), value)
        with self.assertRaisesRegex(strict.StrictJSONError, "^depth-limit-exceeded$"):
            strict.dumps([value])

    def test_decoder_recursion_error_is_bounded_and_redacted(self):
        with self.assertRaises(strict.StrictJSONError) as error:
            strict.loads("[" * 2000 + "0" + "]" * 2000)
        self.assertIn(str(error.exception), {"invalid-json-input", "depth-limit-exceeded"})

    def test_node_boundary(self):
        self.assertTrue(strict.dumps([None] * (strict.MAX_NODES - 1)))
        with self.assertRaisesRegex(strict.StrictJSONError, "^node-limit-exceeded$"):
            strict.dumps([None] * strict.MAX_NODES)

    def test_serialized_bytes_not_character_count(self):
        raw = strict.dumps("é")
        self.assertEqual(len(raw), 4)
        self.assertEqual(strict.dumps("é", max_bytes=4), raw)
        with self.assertRaisesRegex(strict.StrictJSONError, "^size-limit-exceeded$"):
            strict.dumps("é", max_bytes=3)
        with self.assertRaisesRegex(strict.StrictJSONError, "^size-limit-exceeded$"):
            strict.loads('"é"', max_bytes=3)

    def test_escaping_is_included_in_byte_budget(self):
        self.assertEqual(strict.dumps("\n", max_bytes=4), b'"\\n"')
        with self.assertRaisesRegex(strict.StrictJSONError, "^size-limit-exceeded$"):
            strict.dumps("\n", max_bytes=3)

    def test_input_whitespace_counts_towards_byte_limit(self):
        self.assertEqual(strict.loads(" 0 ", max_bytes=3), 0)
        with self.assertRaisesRegex(strict.StrictJSONError, "^size-limit-exceeded$"):
            strict.loads("  0 ", max_bytes=3)

    def test_invalid_utf8_and_surrogates_rejected(self):
        for raw in (b'"\xff"', '"\ud800"', r'"\ud800"'):
            with self.assertRaisesRegex(strict.StrictJSONError, "^invalid-utf8$"):
                strict.loads(raw)
        self.assertEqual(strict.loads(r'"\ud83d\ude42"'), "🙂")

    def test_malformed_or_trailing_data_rejected(self):
        for raw in ('{"x":}', '0 1', '"\x00"', '{', '\ufeff{}'):
            with self.assertRaises(strict.StrictJSONError):
                strict.loads(raw)

    def test_config_and_input_type_checked(self):
        for limit in (False, 0, -1, 1.0, strict.MAX_BYTES + 1):
            with self.assertRaisesRegex(strict.StrictJSONError, "^invalid-byte-limit$"):
                strict.dumps({}, max_bytes=limit)
        for raw in (None, {}, bytearray(b'{}')):
            with self.assertRaisesRegex(strict.StrictJSONError, "^unsupported-json-input$"):
                strict.loads(raw)

    def test_errors_never_echo_duplicate_keys(self):
        with self.assertRaises(strict.StrictJSONError) as error:
            strict.loads('{"sensitive-text":1,"sensitive-text":2}')
        self.assertEqual(str(error.exception), "duplicate-object-key")


if __name__ == "__main__":
    unittest.main()
