import json
import logging
import pathlib
import tempfile

from django.test import SimpleTestCase as TestCase
from django.test.utils import override_settings


log = logging.getLogger(__name__)
TestCase.maxDiff = 1000


class VersionTest(TestCase):
    """
    Checks version url.
    """

    def test_version_response_uses_git_head(self) -> None:
        """
        Checks that the version response reports branch and commit data from `.git/HEAD`.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            base_dir = pathlib.Path(tmpdirname)
            git_dir = base_dir / '.git'
            branch_dir = git_dir / 'refs' / 'heads'
            branch_dir.mkdir(parents=True)
            (git_dir / 'HEAD').write_text('ref: refs/heads/main\n')
            (branch_dir / 'main').write_text('abc123\n')

            with override_settings(BASE_DIR=base_dir):
                response = self.client.get('/version/')

        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        log.debug(f'content, ``{content}``')
        self.assertEqual('main abc123', content['response']['version'])

    def test_version_response_handles_missing_git_head(self) -> None:
        """
        Checks that the version response handles a missing `.git/HEAD`.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            base_dir = pathlib.Path(tmpdirname)

            with override_settings(BASE_DIR=base_dir):
                response = self.client.get('/version/')

        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        log.debug(f'content, ``{content}``')
        self.assertEqual('branch_not_found commit_not_found', content['response']['version'])
