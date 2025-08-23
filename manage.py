## <https://peps.python.org/pep-0723/> recently adopted python standard.
## Allows, for development, to run the app via `uv run ./manage.py runserver`, with no venv.
# /// script
# requires-python = "~=3.8.0"
# dependencies = [
#     "django~=4.2.0",
#     "python-dotenv~=1.0.0",
#     "requests~=2.27.0",
#     "trio~=0.26.0",
#     "urllib3~=1.26.0",
# ]
# ///

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

import django  # for the "in case you're curious about versions" code


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    ## in case you're curious about versions -- feel free to comment out
    if os.environ.get('RUN_MAIN') != 'true':
        major, minor, micro = sys.version_info[:3]
        print(f'using python version, ``{major}.{minor}.{micro}``')
        print(f'using django version, ``{django.get_version()}``')

    main()
