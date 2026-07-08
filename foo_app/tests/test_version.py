import json
import logging
import pathlib
import tempfile

from django.core.cache import cache
from django.test import SimpleTestCase as TestCase
from django.test.utils import override_settings


log = logging.getLogger(__name__)
TestCase.maxDiff = 1000

VERSION_TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'version-test-cache',
    }
}


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

    @override_settings(CACHES=VERSION_TEST_CACHES)
    def test_version_response_caches_git_info_only(self) -> None:
        """
        Checks that version data is cached while request-specific response data is fresh.
        """
        cache.clear()
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                base_dir = pathlib.Path(tmpdirname)
                git_dir = base_dir / '.git'
                branch_dir = git_dir / 'refs' / 'heads'
                branch_dir.mkdir(parents=True)
                (git_dir / 'HEAD').write_text('ref: refs/heads/main\n')
                commit_file = branch_dir / 'main'
                commit_file.write_text('abc123\n')

                with override_settings(BASE_DIR=base_dir):
                    first_response = self.client.get('/version/', REMOTE_ADDR='1.1.1.1')
                    commit_file.write_text('def456\n')
                    second_response = self.client.get('/version/', REMOTE_ADDR='2.2.2.2')
        finally:
            cache.clear()

        first_content = json.loads(first_response.content)
        second_content = json.loads(second_response.content)
        log.debug(f'first_content, ``{first_content}``; second_content, ``{second_content}``')
        self.assertEqual('main abc123', first_content['response']['version'])
        self.assertEqual('main abc123', second_content['response']['version'])
        self.assertEqual('1.1.1.1', first_content['response']['ip'])
        self.assertEqual('2.2.2.2', second_content['response']['ip'])
