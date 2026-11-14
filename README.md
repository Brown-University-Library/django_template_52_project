# purpose

[![CI tests](https://github.com/Brown-University-Library/django_template_52_project/actions/workflows/ci_tests.yaml/badge.svg)](https://github.com/Brown-University-Library/django_template_52_project/actions/workflows/ci_tests.yaml)

This is a template for new django projects -- to standardize on some nice features/practices, and to get up and running, locally, easily and quickly. It provides instructions for getting the template from GitHub, customizing it, starting the webapp, and lists a few things to try with the webapp running. Finally, it lists the nice features/practices, and also shows typical usage.

on this page...

- [local quick-start](#local-quick-start)
- [regular usage](#regular-usage)
- [database migrations](#database-migrations)
- [stuff to try](#stuff-to-try)
- [nice features/practices](#nice-featurespractices)

--- 


# local quick-start

Notes about the quick-start instructions...

- The instructions below assume:
    - a unix-like environment (ie Mac, Linux, or Windows Subsystem for Linux (WSL)). 
    - you've installed `uv` 0.13.6 or newer ([link][uv_link]), which can obtain Python 3.12.16.

- The instructions below reference `x_project_stuff`, `x_project`, and `x_app`. In all cases replace with the name of your project, like: `isbn_api_project_stuff`, `isbn_api_project`, and `isbn_api_app`.

- The `update_project_and_app_references.py` script ([link](https://github.com/Brown-University-Library/django_template_52_project/blob/main/update_project_and_app_references.py)) deletes the cloned `.git` directory (in addition to its main purpose to rename the project). Why? So you don't accidentally start building away and commit to the template repo. After this installation, creating a new git repo is one of the first things you should do.

- The same command updates the package name in `pyproject.toml` and `uv.lock`, plus the repository name in GitHub links. Links keep their existing GitHub owner; adjust that owner if your new repository lives elsewhere. The command only edits local files; it does not create a GitHub repository.

- For a new project, `uv sync --upgrade --group local` checks the package index for the newest versions allowed by `pyproject.toml`, updates `uv.lock`, and installs the local dependencies. The `~=major.minor.0` requirements allow patch updates within each chosen release series. MySQL's driver is deliberately pinned to `mysqlclient==2.2.7` for compatibility with older systems. uv selects Python 3.12.16 or later within the 3.12 series.

- The setup below applies Django's existing migrations to create the initial database tables. With the supplied example settings, this uses a local SQLite database in `../DBs/`.

```bash
## setup directories
$ mkdir ./x_project_stuff  # again, replace `x_project_stuff` with your project-stuff directory name
$ cd ./x_project_stuff/
$ mkdir ./logs
$ mkdir ./DBs

## get the project-code
$ git clone https://github.com/Brown-University-Library/django_template_52_project.git

## update project-name (line below is a single long line; clarifying in case it wraps)
$ uv run --python 3.12 ./django_template_52_project/update_project_and_app_references.py --target_dir "./django_template_52_project/" --new_project_name "x_project" --new_app_name "x_app"  # again, replace `x_project` and `x_app` with your project and app names

## setup the envar-settings
$ cd ./x_project/  # again, this will be the project-name you chose
$ cp ./config/dotenv_example_file.txt ../.env

## make the venv
$ uv sync --upgrade --group local

## create the initial database tables
$ uv run ./manage.py migrate

## run the app
$ uv run ./manage.py runserver
```

That's it!

[uv_link]: <https://docs.astral.sh/uv/getting-started/installation/>

---


# regular usage

After the above one-time setup, for ongoing development...

When setting up another checkout of an established project, run `uv sync --locked --group local` from its project-code directory to install the versions already recorded in `uv.lock` without upgrading them.

```bash
$ cd ./x_project_stuff/x_project  # again, use your stuff/project names
$ uv run ./manage.py runserver  # calling runserver this way auto-activates the venv
```

---


# database migrations

Migrations are Python files that describe changes to database tables and fields. The template app has no models yet, but Django's built-in apps supply migrations for features such as users and sessions.

Run the commands below from your project-code directory. Database commands use `DATABASES_JSON` from the outer `../.env`; the supplied example points to your local SQLite database.

After adding or changing models:

1. Run `uv run ./manage.py makemigrations x_app`, replacing `x_app` with your app name (`foo_app` in the unchanged template). This creates migration files in the app's `migrations/` directory; it does not apply database changes.
2. Review the generated files. Run `uv run ./manage.py migrate --plan` to see pending operations without applying them.
3. Run `uv run ./manage.py migrate` to apply the pending migrations to the configured database.
4. Commit the migration files, including `migrations/__init__.py`, together with the corresponding model changes. Keep the existing migration history in Git so other checkouts can apply the same changes.

After pulling code that already includes migrations, run `uv run ./manage.py migrate` to apply them. You only need `makemigrations` when creating migrations for your own model changes.

To see which migrations have been applied, run `uv run ./manage.py showmigrations`; `[X]` marks an applied migration.

See the [Django migration documentation](https://docs.djangoproject.com/en/5.2/topics/migrations/) for more detail.

---


# stuff to try

- Open a browser to <http://127.0.0.1:8000/>. That'll redirect to <http://127.0.0.1:8000/info/>. 

- Try adding `?format=json` to the info url to see the data feeding the the template.

- Try <http://127.0.0.1:8000/error_check/>. You'll see the intentionally-raised error in the browser (would result in a `404` on production), but if you want to confirm that this really would send an email, open another terminal window and type:
    ```bash
    $ uv run --python 3.12 --with aiosmtpd -m aiosmtpd -n -c aiosmtpd.handlers.Debugging --listen localhost:1026
    ```

    This runs an email server in debugging mode so that it'll print, to the console, all received emails, rather than delivering them.    

    You won't initially see anything, but if you reload the error-check url, and then check this terminal window again, you'll see the email-data that would have been sent.

- Try <http://127.0.0.1:8000/version/>. Once you `git init`, `git add --all`, and `git commit -am "initial commit"`, it'll show the branch and commit -- _very_ handy for dev and prod confirmations.

- Try `$ uv run ./run_tests.py`. The tests should pass.

- Check out the logs (`project_stuff/logs/`). The envar log-level is `DEBUG`, easily changed. On the servers that should be `INFO` or higher, and remember to rotate them, not via python's log-rotate -- but by the server's log-rotate.

Next -- well, the sky's the limit!

---


# nice features/practices

- Nothing private is in the project-repo; avoids using the `.gitignore` for security.
- Shows pattern to keep `views.py` functions short-ish, to act as manager functions (eg `views.version()`).
- Shows pattern to expose the data used by the page via adding `?format=json` (eg `views.info()`). Useful for developing the front-end and troubleshooting.
- Log-formatting shows useful stuff.
- Git branch/commit url is constructed in a way that avoids the new git `dubious ownership` error.
- Includes a couple of client-get tests that respond differentially to dev and prod settings.
- Includes a dev-only error-check url (enables confirmation that email-admins-on-error is set up correctly).
- Uses python-dotenv.
- Uses a `pyproject.toml` file to specify the python version and dependencies.
    - Uses tilde-comparators (`~=`) in the dependency specifications, to the patch-version, for stable upgrades.
    - Uses a `uv.lock` file (created from the `pyproject.toml` file), which the `uv sync` command uses to create and populate the venv.
- Demonstrates how, after the initial `uv sync`, there is no need to activate the venv to run commands.
- This starter webapp doesn't access the db much, but if it did, and you wanted to inspect the sql generated by the ORM, uncomment out the `django.db.backends` logger in `settings.py`.
- Includes a default config-file for [ruff](https://docs.astral.sh/ruff/), a fast, extensible python linter/code-formatter that can integrate with many popular code editors such as VS Code, PyCharm, and others -- or be run from the command line.
- Includes a `run_tests.py` script that runs the tests for this webapp -- compatible with github-ci.
- Includes a `ci_tests.yaml` file for github-ci.
- Includes a 'tests-passing' badge at the top of this README.md file, for convenient confirmation that the tests are passing.

---
