#!/usr/bin/env python3
import unittest
from urllib.parse import unquote
from validate_public_surface import unapproved_references

BASE = 'agentic-harness-agents'
SYNTHETIC = 'agentic' + '-harness' + '-synthetic-consumer'


def archive(version='{version}'):
    return BASE + '-v' + version + '.zip'


class PublicArchiveNames(unittest.TestCase):
    def test_build_template_and_versioned_zip(self):
        for version in ['{version}', '1.2.3', '0.5.0-beta.1', '1.0.0-rc.2']:
            for suffix in ['', '.sha256']:
                self.assertFalse(unapproved_references('dist/' + archive(version) + suffix))

    def test_fstring_source_line(self):
        self.assertFalse(unapproved_references('archive = dist / f"' + archive() + '"'))

    def test_archive_is_not_a_repository_name(self):
        for prefix in ['https://github.com/synthetic/', 'https://api.github.com/repos/synthetic/']:
            self.assertTrue(unapproved_references(prefix + archive('1.2.3')))

    def test_approved_repository_release_url(self):
        url = 'https://github.com/synthetic/' + BASE + '/releases/download/v1.2.3/' + archive('1.2.3')
        self.assertFalse(unapproved_references(url))

    def test_incomplete_or_unknown_filename_is_not_accepted(self):
        for name in [BASE + '-v', BASE + '-vfuture.zip', archive('1.2.3') + '.git', SYNTHETIC + '-v1.2.3.zip']:
            self.assertTrue(unapproved_references(name))

    def test_neighboring_unapproved_reference_remains_visible(self):
        self.assertTrue(unapproved_references(archive() + ' ' + SYNTHETIC))

    def test_case_percent_encoding_and_git_urls(self):
        self.assertFalse(unapproved_references(unquote(archive('1.2.3').upper().replace('-', '%2D'))))
        self.assertFalse(unapproved_references('https://github.com/synthetic/' + BASE + '.git'))
        self.assertTrue(unapproved_references(unquote('https://github.com/synthetic/' + SYNTHETIC.replace('-', '%2D'))))

    def test_existing_plain_repository_names_stay_restricted(self):
        for name in ['agentic-harness', BASE, 'agentic-harness-cli']:
            self.assertFalse(unapproved_references(name))
        self.assertTrue(unapproved_references(SYNTHETIC))


if __name__ == '__main__':
    unittest.main()
