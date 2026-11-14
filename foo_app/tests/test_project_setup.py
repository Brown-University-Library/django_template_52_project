import tempfile
import tomllib
from pathlib import Path

from django.test import SimpleTestCase

from update_project_and_app_references import OLD_APP_NAME, OLD_PROJECT_NAME, REPO_PROJECT_NAME, run_updater

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPDATER_NAME = 'update_project_and_app_references.py'


class ProjectSetupTest(SimpleTestCase):
    def test_customizes_project_metadata_links_and_app(self) -> None:
        """
        Checks that a sample checkout uses the new names and preserves non-template content.
        """
        for project_name, package_name in [('sample_project', 'sample-project'), ('Sample__Project', 'sample-project')]:
            with self.subTest(project_name=project_name), tempfile.TemporaryDirectory() as temporary_directory:
                parent = Path(temporary_directory)
                target = parent / REPO_PROJECT_NAME
                ## build sample files so this test also works after the real template is renamed
                sample_files = {
                    'pyproject.toml': f'[project]\nname = "{REPO_PROJECT_NAME}"\nreadme = "README.md"\n',
                    'uv.lock': (
                        f'[[package]]\nname = "{REPO_PROJECT_NAME.replace("_", "-")}"\nsource = {{ virtual = "." }}\n'
                    ),
                    'README.md': f'https://github.com/Brown-University-Library/{REPO_PROJECT_NAME}/actions/workflows/ci_tests.yaml\n',
                    'AGENTS.md': f'Application code is in {OLD_APP_NAME}/.\n',
                    'config/settings.py': f'PROJECT_NAME = "{REPO_PROJECT_NAME}"\n',
                    'config/urls.py': f'from {OLD_APP_NAME} import views\n',
                    'config/dotenv_example_file.txt': (
                        f'README_URL="https://github.com/birkin/{REPO_PROJECT_NAME}/blob/main/README.md"\n'
                        f'LOG_PATH="../logs/{OLD_PROJECT_NAME}.log"\n'
                    ),
                    f'{OLD_APP_NAME}/{OLD_APP_NAME}_templates/info.html': '<p>Hello</p>\n',
                    f'{OLD_APP_NAME}/static/{OLD_APP_NAME}/css/styles.css': 'body { color: black; }\n',
                    UPDATER_NAME: (PROJECT_ROOT / UPDATER_NAME).read_text(encoding='utf-8'),
                }
                for filename, content in sample_files.items():
                    destination = target / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(content, encoding='utf-8')
                git_directory = target / '.git'
                git_directory.mkdir()
                (git_directory / 'HEAD').write_text('ref: refs/heads/main\n', encoding='utf-8')
                binary_content = b'\xff\xfe' + REPO_PROJECT_NAME.encode('utf-8')
                (target / 'image.bin').write_bytes(binary_content)

                run_updater(target, project_name, 'sample_app')

                renamed = parent / project_name
                self.assertFalse(target.exists())
                self.assertFalse((renamed / '.git').exists())
                self.assertTrue((renamed / 'sample_app/sample_app_templates/info.html').is_file())
                self.assertTrue((renamed / 'sample_app/static/sample_app/css/styles.css').is_file())
                self.assertEqual(binary_content, (renamed / 'image.bin').read_bytes())
                self.assertEqual((PROJECT_ROOT / UPDATER_NAME).read_bytes(), (renamed / UPDATER_NAME).read_bytes())

                metadata = tomllib.loads((renamed / 'pyproject.toml').read_text(encoding='utf-8'))
                self.assertEqual(project_name, metadata['project']['name'])
                self.assertEqual('README.md', metadata['project']['readme'])
                lock = tomllib.loads((renamed / 'uv.lock').read_text(encoding='utf-8'))
                project_packages = [package for package in lock['package'] if package['source'] == {'virtual': '.'}]
                self.assertEqual([package_name], [package['name'] for package in project_packages])

                for filename in (
                    'pyproject.toml',
                    'uv.lock',
                    'README.md',
                    'AGENTS.md',
                    'config/settings.py',
                    'config/dotenv_example_file.txt',
                    'config/urls.py',
                ):
                    text = (renamed / filename).read_text(encoding='utf-8')
                    for old_name in (REPO_PROJECT_NAME, REPO_PROJECT_NAME.replace('_', '-'), OLD_PROJECT_NAME, OLD_APP_NAME):
                        self.assertNotIn(old_name, text, filename)

                readme = (renamed / 'README.md').read_text(encoding='utf-8')
                self.assertIn(f'https://github.com/Brown-University-Library/{project_name}/', readme)
                dotenv_example = (renamed / 'config/dotenv_example_file.txt').read_text(encoding='utf-8')
                self.assertIn(f'https://github.com/birkin/{project_name}/blob/main/README.md', dotenv_example)
