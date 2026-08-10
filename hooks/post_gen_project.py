"""Prune the features the answers turned off, then leave a repo that is ready to build.

Cookiecutter renders every file in the template and then runs this. Deleting here rather than
wrapping each file in a Jinja conditional keeps the templates readable as the files they will
become — a Makefile full of Jinja tags is a Makefile nobody can check by eye.

Note that this script is itself rendered as a Jinja template before it runs, which is why the
answers arrive as literals below and why nothing here may contain a Jinja delimiter, comments
included.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()

PROJECT_NAME = "{{ cookiecutter.project_name }}"
REPO_NAME = "{{ cookiecutter.repo_name }}"
APP_ID = "{{ cookiecutter.app_id }}"
URL_SEGMENT = "{{ cookiecutter.url_segment }}"
DEV_PORT = "{{ cookiecutter.dev_port }}"
INCLUDE_ALL_SCREENS = "{{ cookiecutter.include_all_screens }}" == "yes"
INCLUDE_SCENARIO_MODE = "{{ cookiecutter.include_scenario_mode }}" == "yes"
INCLUDE_TAXPERT_WORKSPACE = "{{ cookiecutter.include_taxpert_workspace }}" == "yes"
INCLUDE_DOCKER = "{{ cookiecutter.include_docker }}" == "yes"

RESOURCES = ROOT / "src" / "main" / "resources" / APP_ID


def drop(*paths):
    for path in paths:
        target = ROOT / path
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def strip_flag(flag):
    """Remove a build flag from every `sbt run` line in the Makefile.

    The flags decide what the generated site *contains*, not something a person toggles afterwards,
    so an app that said no to a feature should not keep a dev target that switches it on.
    """
    makefile = ROOT / "Makefile"
    makefile.write_text(makefile.read_text().replace(" " + flag, ""))


if not INCLUDE_SCENARIO_MODE:
    strip_flag("--scenarioMode")
    drop(RESOURCES / "scenarios")

if not INCLUDE_ALL_SCREENS:
    strip_flag("--allScreens")
    # And everything that pointed at the page that is no longer generated. Left in, the menu would
    # offer two destinations that 404 — worse than a shorter menu, which is a legitimate taxonomy:
    # the workspace's nav is the host's to define, not the library's.
    #
    # Two edits, not one: the menu entries are whole lines, but the same two ids also appear inside
    # the `destinations` arrays below them, where dropping the line would take a tool with it.
    fragment = RESOURCES / "templates" / "fragments" / "taxpert-config.html"
    gone = ("'browse-all'", "'path-mode'")
    kept = []
    for line in fragment.read_text().splitlines(keepends=True):
        if any("id: " + name in line for name in gone):
            continue
        for name in gone:
            line = line.replace(", " + name, "")
        kept.append(line)
    fragment.write_text("".join(kept))
    # The page's own assets, which nothing else links.
    drop(
        RESOURCES / "website-static" / "js" / "all-screens-bootstrap.js",
        RESOURCES / "website-static" / "styles" / "all-screens.css",
    )

if not INCLUDE_TAXPERT_WORKSPACE:
    # taxpert itself stays a dependency either way — it also carries the flow runtime and the
    # theme, which every Formative app renders with. What a "no" here drops is the *workspace*:
    # the global nav, the audit panel and the tool dock that --auditMode builds into the page, plus
    # this app's own registration of it (its nav taxonomy, its endpoints, the outcomes the tracker
    # follows). Dropping the app's fragment falls through to the scaffold's empty default, which
    # still calls configure() with the app id and endpoints the flow runtime itself relies on — an
    # unconfigured host is a working app with a contentless workspace, not a broken one.
    strip_flag("--auditMode")
    drop(
        RESOURCES / "templates" / "fragments" / "taxpert-config.html",
        RESOURCES / "website-static" / "taxpert.config.json",
        RESOURCES / "website-static" / "js" / "taxpert",
    )

if not INCLUDE_DOCKER:
    drop("Dockerfile", "nginx.conf", ".dockerignore")

for script in (ROOT / "scripts").glob("*.sh"):
    script.chmod(0o755)

# A repo, not a directory of files: `make diff-out` compares against a git history, and the first
# thing anyone does here is commit anyway. Failure is not fatal — git may be absent, and the
# generated app is perfectly usable without it.
try:
    subprocess.run(["git", "init", "--quiet", "--initial-branch=main"], check=True, cwd=ROOT)
    subprocess.run(["git", "add", "--all"], check=True, cwd=ROOT)
except (OSError, subprocess.CalledProcessError) as error:
    print("note: skipped `git init` (" + str(error) + ")", file=sys.stderr)

NEXT_STEPS = (
    """
  Then open the nav's Tools button. The Outcome tracker already follows /qualifies, so answering
  the two questions in the flow moves it from a part-drawn ring to a spoken outcome — that one
  path proves flow, fact graph, registration and workspace are all wired.
"""
    if INCLUDE_TAXPERT_WORKSPACE
    else """
  This app was generated without the Taxpert workspace (no --auditMode, no nav, no audit panel or
  tool dock) — answering the two questions in the flow is what proves the flow and fact graph are
  wired; there is no Outcome tracker here to watch it settle.
"""
)

print(
    """
  {name} is ready in ./{repo}

  It expects three sibling checkouts — fact-graph, formative and taxpert — so put it beside them
  and run:

      cd {repo}
      make bootstrap        # publish the libraries, vendor their assets
      make dev              # http://localhost:{port}/app/{segment}/
{next_steps}""".format(
        name=PROJECT_NAME, repo=REPO_NAME, port=DEV_PORT, segment=URL_SEGMENT, next_steps=NEXT_STEPS
    )
)
