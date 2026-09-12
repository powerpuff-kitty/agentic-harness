#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path
from validate_public_surface import PUBLIC_REPOSITORIES, reference_errors, unapproved_references

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
        self.assertFalse(unapproved_references(archive('1.2.3').upper().replace('-', '%2D')))
        self.assertFalse(unapproved_references('https://github.com/synthetic/' + BASE + '.git'))
        self.assertTrue(unapproved_references('https://github.com/synthetic/' + SYNTHETIC.replace('-', '%2D')))

    def test_existing_plain_repository_names_stay_restricted(self):
        for name in PUBLIC_REPOSITORIES:
            self.assertFalse(unapproved_references(name))
        self.assertTrue(unapproved_references(SYNTHETIC))

    def test_public_attribution_period(self):
        self.assertFalse(unapproved_references('https://github.com/powerpuff-kitty/' + BASE + '.'))

    def test_sentence_and_markdown_delimiters(self):
        for repo in PUBLIC_REPOSITORIES:
            for prefix in ['https://github.com/synthetic/', 'https://api.github.com/repos/synthetic/']:
                for suffix in ['', '.', '. More text', '.\n', '.)', '."', '>', '/', '/tree/main']:
                    with self.subTest(repo=repo, suffix=suffix):
                        self.assertFalse(unapproved_references(prefix + repo + suffix))

    def test_git_url_sentence(self):
        for suffix in ['.git', '.git.', '.git. More']:
            self.assertFalse(unapproved_references('https://github.com/synthetic/' + BASE + suffix))

    def test_suffixes_and_repeated_periods_remain_forbidden(self):
        for suffix in ['-synthetic', '.synthetic', '_synthetic', '.git-synthetic', '..']:
            self.assertTrue(unapproved_references('https://github.com/synthetic/' + BASE + suffix))

    def test_dot_before_path_query_or_fragment_is_not_prose(self):
        for suffix in ['./issues', '.?tab=readme', '.#readme']:
            self.assertTrue(unapproved_references('https://github.com/synthetic/' + BASE + suffix))

    def test_archive_shaped_repository_with_punctuation_is_rejected(self):
        for suffix in ['', '.', '/tree/main']:
            self.assertTrue(unapproved_references('https://github.com/synthetic/' + archive('1.2.3') + suffix))

    def test_percent_encoded_period(self):
        prefix = 'https://github.com/synthetic/' + BASE
        self.assertFalse(unapproved_references(prefix + '%2E'))
        self.assertTrue(unapproved_references(prefix + '%2Esynthetic'))

    def test_bad_reference_after_valid_sentence(self):
        self.assertTrue(unapproved_references('https://github.com/synthetic/' + BASE + '. ' + SYNTHETIC))

    def test_attribution_through_file_scanner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for variant in ['base', 'web-app', 'backend-api', 'saas', 'monorepo', 'library-sdk']:
                path = root / variant / '.agentic/THIRD_PARTY_NOTICES.md'
                path.parent.mkdir(parents=True)
                path.write_text('Sources: https://github.com/powerpuff-kitty/agentic-harness and\n'
                                'https://github.com/powerpuff-kitty/' + BASE + '.\n', encoding='utf-8')
            self.assertEqual(reference_errors(root), [])
            (root / 'unapproved.md').write_text(SYNTHETIC, encoding='utf-8')
            errors = reference_errors(root)
            self.assertEqual(len(errors), 1)
            self.assertNotIn(SYNTHETIC, errors[0])


if __name__ == '__main__':
    unittest.main()
