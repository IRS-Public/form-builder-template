"""Prune the features the answers turned off, then leave a repo that is ready to build.

Cookiecutter renders every file in the template and then runs this. Deleting here rather than
wrapping each file in a Jinja conditional keeps the templates readable as the files they will
become — a Makefile full of Jinja tags is a Makefile nobody can check by eye.

Note that this script is itself rendered as a Jinja template before it runs, which is why the
answers arrive as literals below and why nothing here may contain a Jinja delimiter, comments
included.
"""

import os
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
FACT_GRAPH_PATH = "{{ cookiecutter.fact_graph_path }}"
FORM_BUILDER_PATH = "{{ cookiecutter.form_builder_path }}"
TAXPERT_PATH = "{{ cookiecutter.taxpert_path }}"
INCLUDE_ALL_SCREENS = "{{ cookiecutter.include_all_screens }}" == "yes"
INCLUDE_SCENARIO_MODE = "{{ cookiecutter.include_scenario_mode }}" == "yes"
INCLUDE_TAXPERT_WORKSPACE = "{{ cookiecutter.include_taxpert_workspace }}" == "yes"
INCLUDE_FACT_EXPLORER = "{{ cookiecutter.include_fact_explorer }}" == "yes"
INCLUDE_DOCKER = "{{ cookiecutter.include_docker }}" == "yes"

# `cookiecutter form-builder-template` writes into `<invocation cwd>/<repo_name>` by default, so typing
# that from *inside* form-builder-template/ itself — a natural habit, "cd into the tool, then run it" —
# nests the new app inside the template instead of beside it. Cookiecutter creates the project
# directory before any hook runs, so there is no earlier point to intercept this; catch it here and
# move the app up one level instead.
#
# The check is deliberately narrower than "the parent is named form-builder-template": the parent must
# itself BE a cookiecutter template (a cookiecutter.json next to a hooks/ directory), so an explicit
# `--output-dir` pointed somewhere else on purpose — even a directory that happens to share the name
# — is left alone.
if (ROOT.parent / "cookiecutter.json").is_file() and (ROOT.parent / "hooks").is_dir():
    CORRECTED = ROOT.parent.parent / REPO_NAME
    if CORRECTED.exists():
        sys.exit(
            f"error: generated {REPO_NAME} inside the template by mistake, and can't move it to "
            f"{CORRECTED} to fix that — something is already there. Remove it, or re-run with a "
            "different repo_name."
        )
    shutil.move(str(ROOT), str(CORRECTED))
    os.chdir(CORRECTED)
    ROOT = CORRECTED
    print(f"note: moved {REPO_NAME} out of the template, to {ROOT}", file=sys.stderr)

RESOURCES = ROOT / "src" / "main" / "resources" / APP_ID


def drop(*paths):
    for path in paths:
        target = ROOT / path
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def strip_flag(flag):
    """Remove a build flag from every `sbt run` line that carries one.

    The flags decide what the generated site *contains*, not something a person toggles afterwards,
    so an app that said no to a feature should not keep a dev target that switches it on.

    Two files, not one: the Makefile's targets and the Docker watcher's `command:`. They are the
    same dev server reached two ways, and a flag left in only one of them means the app behaves
    differently depending on whether it was started natively or in a container - the kind of
    difference nobody thinks to check.
    """
    for name in ("Makefile", "docker-compose.override.yml"):
        target = ROOT / name
        if target.exists():
            target.write_text(target.read_text().replace(" " + flag, ""))


def drop_blocks(path, *needles):
    """Delete every blank-line-separated block of `path` that mentions any of `needles`.

    Blocks rather than lines because everything worth deleting here comes with the comment that
    explains it, and a line-level filter would leave the comment behind describing something that is
    no longer there. It works on the Makefile and on CSS alike: in both, a blank line is what separates
    one self-contained thing from the next.
    """
    target = ROOT / path
    blocks = target.read_text().split("\n\n")
    kept = [b for b in blocks if not any(n in b for n in needles)]
    target.write_text("\n\n".join(kept))


def drop_lines(path, *needles):
    """Delete every individual line of `path` containing any of `needles`."""
    target = ROOT / path
    kept = [
        ln
        for ln in target.read_text().splitlines(keepends=True)
        if not any(n in ln for n in needles)
    ]
    target.write_text("".join(kept))


def replace_in(path, *pairs):
    """Apply literal (old, new) substitutions to `path`."""
    target = ROOT / path
    text = target.read_text()
    for old, new in pairs:
        text = text.replace(old, new)
    target.write_text(text)


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
    # A "no" here drops taxpert entirely — the dependency, not just the surfaces it draws.
    #
    # That is newly true. taxpert used to carry the theme and the flow runtime as well as the
    # workspace, so every app needed the package whatever it answered here, and this block could only
    # strip --auditMode and delete a few registration files. Both of those now ship inside the
    # `gov.irs::form-builder` jar and are extracted by the generator (see FormBuilderAssets.scala), so what
    # is left in taxpert is exactly the optional part: the global nav, the audit panel, the tool dock.
    #
    # So this deletes the npm dependency, the two make targets that vendor and verify it, the
    # stylesheet imports, and the mount fragments. A generated app that says no has no `package.json`
    # at its root, no `node_modules` to install there, and no reference to taxpert anywhere.
    strip_flag("--auditMode")
    drop(
        # The app's registration of the workspace: its nav taxonomy, its endpoints, the outcomes the
        # tracker follows, and the fact-graph adapter those need.
        RESOURCES / "templates" / "fragments" / "taxpert-config.html",
        RESOURCES / "website-static" / "taxpert.config.json",
        RESOURCES / "website-static" / "js" / "taxpert",
        # The mount points. The scaffold ships an empty default for each, so their absence is not an
        # error — head.html/page.html/all-screens.html simply replace them with nothing.
        RESOURCES / "templates" / "fragments" / "workspace-head.html",
        RESOURCES / "templates" / "fragments" / "workspace-enable.html",
        RESOURCES / "templates" / "fragments" / "workspace-all-screens.html",
        # This file exists only to declare the taxpert dependency — the app has no bundler, and the
        # linting tools live in the resources package.json instead.
        "package.json",
    )
    # The two make targets that mirror taxpert into vendor/ and check it has not drifted, plus the
    # variables they read. Blocks, so each target's explanatory comment goes with it.
    drop_blocks(
        "Makefile",
        "copy-shared-ui:",
        "check-shared-ui:",
        "SHARED_UI_SRC",
    )
    replace_in(
        "Makefile",
        # Every target that vendored taxpert ahead of a build: dev, dev-one-question, dev-author,
        # debug, site, and bootstrap's one-shot line.
        (" copy-shared-ui", ""),
        # `ci` ran the drift check.
        ("\t$(MAKE) check-shared-ui\n", ""),
        # There is no root package.json left to install.
        ("\tnpm install\n", ""),
        (
            "\t@# fact-graph and form-builder are resolved through the local Ivy cache, taxpert through a file:\n"
            "\t@# npm dependency. All three come from local checkouts rather than a remote, and none is\n"
            "\t@# guaranteed to sit beside this repo (see fact_graph_path / form_builder_path / taxpert_path in\n"
            "\t@# cookiecutter.json) — a fresh clone has to build them once before it can build itself.\n",
            "\t@# fact-graph and form-builder are resolved through the local Ivy cache. Both come from local\n"
            "\t@# checkouts rather than a remote, and neither is guaranteed to sit beside this repo (see\n"
            "\t@# fact_graph_path / form_builder_path in cookiecutter.json) — a fresh clone has to build them\n"
            "\t@# once before it can build itself.\n",
        ),
    )
    # The workspace's own stylesheets, and the one app-side stylesheet that only the workspace can
    # switch on: `.display-conditions` is a class taxpert's display-options.js adds to <body>, so
    # without taxpert every rule in display-conditions.css is unreachable. The theme import is
    # form-builder's and stays.
    drop_blocks(
        RESOURCES / "website-static" / "styles" / "main.css",
        "vendor/taxpert",
        "utilities/display-conditions.css",
    )
    drop(RESOURCES / "website-static" / "styles" / "utilities")
    # The Docker build's equivalent of `make copy-shared-ui`, and the CI job's checkout of the
    # package. Both would fail outright without a ../taxpert beside this repo, so neither can be left
    # behind as a harmless leftover.
    if INCLUDE_DOCKER:
        drop_blocks("Dockerfile", "vendor/taxpert")
        drop_lines(".dockerignore", "website-static/vendor/taxpert/")
        # The watcher's bind mount over that same vendored path. It is its own blank-line-delimited
        # block in the compose file precisely so it can be lifted out with its comment; a mount of a
        # sibling that is not there fails the whole `docker compose up`, so this is not optional.
        drop_blocks("docker-compose.override.yml", "vendor/taxpert")
        # The `taxpert:` entry under each service's `additional_contexts:` — a build context pointed
        # at a library this app no longer depends on would fail `docker compose build` outright.
        drop_lines("docker-compose.yml", "taxpert:")
        drop_lines("docker-compose.override.yml", "taxpert:")
        # The matching line in the Dockerfile header's `docker build` example.
        drop_lines("Dockerfile", "--build-context taxpert=")
    replace_in(
        ".github/workflows/ci.yml",
        (
            "      - uses: actions/checkout@v4\n"
            "        with:\n"
            "          repository: your-org/taxpert\n"
            "          path: taxpert\n",
            "",
        ),
    )
    if INCLUDE_ALL_SCREENS:
        # Browse All / Path Mode is one page owned in two places: the markup is the scaffold's, but
        # everything that dresses it — the section headers, the screen cards, the two layout modes —
        # is the workspace's. Without taxpert the page still generates and still lists every screen;
        # it just arrives with only the theme's styling on it. Dropping the import is what keeps it
        # from being a stylesheet that 404s. See the note printed at the end of this script.
        drop_lines(
            RESOURCES / "website-static" / "styles" / "all-screens.css",
            "vendor/taxpert",
        )
        replace_in(
            RESOURCES / "website-static" / "styles" / "all-screens.css",
            (
                "   the workspace's. Add your own rules below the import; they win by ordinary cascade order, the\n"
                "   same shape as main.css over theme.css. */\n",
                "   the workspace's — and this app was generated without it, so that import is gone and the page\n"
                "   arrives with only the theme on it. Add your own rules here, or adopt taxpert to get the\n"
                "   toolbar and the layout modes back. */\n",
            ),
        )
    drop_lines(".gitignore", "vendor/taxpert/")
    replace_in(
        ".gitignore",
        (
            "# build — and none of them is a source. Edit the package, not the mirror; `make check-shared-ui`\n"
            "# fails the build if the taxpert mirror drifts.\n",
            "# build — and none of them is a source.\n",
        ),
    )

if not INCLUDE_FACT_EXPLORER:
    # Two files and nothing else, because Fact Explorer is a *reader*. It needs the Form Builder Graph
    # the --formBuilderGraph flag emits, and a descriptor telling it where this app lives; it needs no
    # dependency, no asset and no markup here. So saying no removes exactly those two things.
    #
    # Note this is independent of the Taxpert workspace. Fact Explorer reads the graph, the fact
    # dictionary and the engine bundle — all of them the scaffold's, none of them the workspace's —
    # so fact-explorer=yes / workspace=no is a legitimate combination and is left working.
    strip_flag("--formBuilderGraph")
    drop("fact-explorer.app.json")
    drop_blocks("Makefile", "fact-explorer:")

if not INCLUDE_DOCKER:
    drop(
        "Dockerfile",
        "nginx.conf",
        ".dockerignore",
        "docker-compose.yml",
        "docker-compose.override.yml",
    )
    # And the make targets that wrap them, so `make help` never lists a command that cannot work.
    drop_blocks("Makefile", "docker compose")

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
  tool dock), and so without any dependency on the taxpert package at all — there is no root
  package.json, and nothing to check out beside this repo but fact-graph and form-builder. Answering the
  two questions in the flow is what proves the flow and fact graph are wired; there is no Outcome
  tracker here to watch it settle.

  The theme and the flow runtime are unaffected: both ship inside the form-builder jar and are extracted
  into resources/vendor/form-builder/ on every build.
"""
)

if INCLUDE_DOCKER:
    # The way in for someone who has not installed a JDK, sbt or node - which is most people the
    # first time they open a generated repo. Worth naming here rather than leaving in a compose file
    # nobody opens until something is already wrong.
    NEXT_STEPS += """
  Or skip the local toolchain entirely: `make up` builds the sibling libraries, generates the site
  and serves it, and leaves a `sbt ~run` watcher regenerating it on every edit. Same URL, same
  flags as `make dev`; refresh the browser after a change.
"""

if INCLUDE_FACT_EXPLORER:
    # Discovery, not registration. The hook deliberately writes nothing outside the project it
    # generates: cookiecutter runs it with cwd inside this repo and promises nothing about what is
    # above, so appending to a Fact Explorer's app list would silently create or mutate a stray file
    # for anyone generating outside the monorepo. The emitted fact-explorer.app.json is the
    # registration, and build-registry.mjs finds it — so all that is left to do here is say so.
    NEXT_STEPS += """
  This app ships a fact-explorer.app.json, so Fact Explorer finds it once the repo sits in the apps
  directory it scans — taxpert/apps, or wherever FORM_BUILDER_APPS_DIR points. To see the flow and
  fact dictionary as a graph:

      make fact-explorer
      ln -s "$PWD" /path/to/taxpert/apps/          # once
      cd /path/to/taxpert/packages/fact-explorer && npm run build-registry && npm run dev
"""

# One consequence worth saying out loud rather than leaving to be discovered in the browser.
if INCLUDE_ALL_SCREENS and not INCLUDE_TAXPERT_WORKSPACE:
    NEXT_STEPS += """
  Note: Browse All lists every screen, but its toolbar and its two layout modes are the workspace's,
  so on this app the page arrives with only the theme's styling. styles/all-screens.css says so too.
"""

# The library paths, as answered — not assumed to be siblings. Printed back so a non-default
# answer (a path elsewhere on disk, or a monorepo layout like this one) is visible immediately
# rather than discovered the first time `make bootstrap` fails to find one.
LIB_PATHS = [("fact-graph", FACT_GRAPH_PATH), ("form-builder", FORM_BUILDER_PATH)]
if INCLUDE_TAXPERT_WORKSPACE:
    LIB_PATHS.append(("taxpert", TAXPERT_PATH))
libs_summary = ", ".join(f"{name} at {path}" for name, path in LIB_PATHS)

print(
    """
  {name} is ready in ./{repo}

  It depends on {libs}, resolved from this app's own directory. Those paths came from this app's
  cookiecutter answers (fact_graph_path / form_builder_path{taxpert_var} in cookiecutter.json) rather
  than an assumption that the libraries sit beside it — if one of them moves, the Makefile{docker_var}
  is where to update the path.

      cd {repo}
      make bootstrap        # publish the libraries, vendor their assets
      make dev              # http://localhost:{port}/app/{segment}/
{next_steps}""".format(
        name=PROJECT_NAME,
        repo=REPO_NAME,
        libs=libs_summary,
        taxpert_var=" / taxpert_path" if INCLUDE_TAXPERT_WORKSPACE else "",
        docker_var=" (and docker-compose.yml, if you use it)" if INCLUDE_DOCKER else "",
        port=DEV_PORT,
        segment=URL_SEGMENT,
        next_steps=NEXT_STEPS,
    )
)
