# -*- coding: utf-8 -*-
# Copyright (c) 2026, num2words contributors. All Rights Reserved.

import os
import subprocess
import sys
import unittest
from decimal import Decimal, InvalidOperation
from pathlib import Path

from num2words import num2words


class StringInputParsingTest(unittest.TestCase):
    def test_farsi_indonesian_and_vietnamese_strings_match_decimal(self):
        for language in ('fa', 'id', 'vi'):
            for number in ('1', '21', '1.25', '-1'):
                with self.subTest(language=language, number=number):
                    self.assertEqual(
                        num2words(number, lang=language),
                        num2words(Decimal(number), lang=language),
                    )

    def test_language_fallback_parses_the_same_input(self):
        for language in ('fa', 'id', 'vi'):
            with self.subTest(language=language):
                self.assertEqual(
                    num2words('1.25', lang=language + '_XX'),
                    num2words(Decimal('1.25'), lang=language),
                )

    def test_language_specific_parser_is_preserved(self):
        self.assertEqual(num2words('-1', lang='bn'), num2words(1, lang='bn'))

    def test_invalid_strings_raise_the_same_decimal_error_as_english(self):
        for language in ('en', 'fa', 'id', 'vi'):
            with self.subTest(language=language):
                with self.assertRaises(InvalidOperation):
                    num2words('not a number', lang=language)

    def test_cli_uses_the_same_result_as_the_numeric_api(self):
        script = Path(__file__).resolve().parents[1] / 'bin' / 'num2words'
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONPATH'] = os.pathsep.join(
            path for path in (str(script.parent.parent), env.get('PYTHONPATH'))
            if path
        )
        for language in ('fa', 'id', 'vi'):
            for number in ('1', '21', '1.25'):
                with self.subTest(language=language, number=number):
                    result = subprocess.run(
                        [sys.executable, str(script), number, '-l', language],
                        capture_output=True, text=True, encoding='utf-8',
                        env=env, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        result.stdout,
                        num2words(Decimal(number), lang=language) + '\n',
                    )
                    self.assertEqual(result.stderr, '')
