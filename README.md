# formative-template

A [cookiecutter](https://cookiecutter.readthedocs.io/) that generates a new **Formative app**: a
multi-language static questionnaire built on [`gov.irs::formative`](../formative), the Scala library
that turns Flow XML plus a Fact Dictionary into a site.

What it emits is deliberately thin. The parser, the generators, the Thymeleaf engine, the node
templates, the chrome locales, the theme, the flow runtime and Author Mode all belong to the library.
A generated app gets its flow XML, its fact dictionary, its locales, its brand CSS and a `Main.scala`
of about 40 lines.

The template does not copy the site generator. The two apps in this monorepo had forked it between
them, 23 of one app's 28 Scala files sharing a basename with the other's, and a template that copied
the generator would have made that fork number three. Everything genuinely per-app is a registration
instead: a custom node type, a custom input type, an overridden template, an overridden locale key.

## Use it

```bash
pipx install cookiecutter        # or: pip install cookiecutter
cookiecutter formative-template
```

Answer the prompts, then:

```bash
cd my-tax-tool
make bootstrap    # publish the sibling libraries, install npm deps, vendor their assets
make dev          # http://localhost:3010/app/my-tax-tool/
```

The generated app lands beside `formative-template/`, in a directory named by your `repo_name`
answer, whichever directory you ran `cookiecutter` from. Running it from inside `formative-template/`
itself would nest the new app inside the template, since cookiecutter's default output directory is
`.`. The post-gen hook detects that one case and moves the app up a level. An explicit `--output-dir`
is left alone.

The hook also runs `git init` and `git add --all` in the generated repo, so you start on a `main`
branch with everything staged and nothing committed.

## What the generated app needs beside it

`gov.irs::factgraph`, `gov.irs::formative` and `taxpert` are not published to a remote yet, so the
generated app resolves each from a path you answer for. Each defaults to the sibling form, and each
can be any relative or absolute path, independently of the others.

```
parent/
├── fact-graph/
├── formative/
├── taxpert/            only with include_taxpert_workspace=yes
└── my-tax-tool/        generated, with the three defaults above
```

Those answers are threaded into the generated `Makefile`, the root `package.json` (the `taxpert`
`file:` dependency), `docker-compose.yml` and `docker-compose.override.yml` (as named
`additional_contexts`), and `.github/workflows/ci.yml`. The CI workflow's checkout `path:`s describe
the same checkouts from the runner's vantage point rather than the app's, so if you move a library off
the sibling layout you have to keep those in step by hand.

## The questions

| Variable | Default | What it controls |
|---|---|---|
| `project_name` | `My Tax Tool` | The human name. Everything else derives from it. |
| `repo_name` | slug of `project_name` | The generated directory and the sbt project name. |
| `app_id` | = `repo_name` | The resource directory under `src/main/resources`, and the classpath prefix the app's own templates resolve from. |
| `url_segment` | = `repo_name` | The site is served from `/app/<url_segment>`. |
| `scala_package` | `gov.irs.<appid>` | The package for `Main.scala` and the tests. Hyphens are stripped. |
| `brand` | = `project_name` | Shown in the dev server banner and used in page titles. |
| `storage_prefix` | = `app_id` | Namespaces every browser storage key the site writes. |
| `dev_port` | `3010` | The dev server port, and `PORT` in the Makefile. |
| `formative_version` | `0.1.0-SNAPSHOT` | The `gov.irs::formative` version in `build.sbt`. |
| `factgraph_version` | `3.1.0-SNAPSHOT` | Used to name the vendored Scala.js bundle, `factgraph-3.1.0.js`. |
| `fact_graph_path` | `../fact-graph` | Where that library lives, resolved from the generated app's own directory. |
| `formative_path` | `../formative` | Same. |
| `taxpert_path` | `../taxpert` | Same. Unused when the workspace is left out. |
| `include_all_screens` | `yes` | The Browse All page that lists every screen at once. |
| `include_scenario_mode` | `yes` | Saved fact graphs under `scenarios/`, loadable from the Scenario modal. |
| `include_taxpert_workspace` | `yes` | The global nav, audit panel and tool dock. |
| `include_fact_explorer` | `yes` | A `fact-explorer.app.json` and the build flag that emits the graph Fact Explorer reads. |
| `include_docker` | `yes` | `Dockerfile`, `nginx.conf`, the two compose files, and the make targets that wrap them. |

Two more keys in `cookiecutter.json` are derived rather than asked: `__package_path` (the Scala
package as a directory path) and `__js_name` (the app id in camelCase, used for the exported symbols
in `website-static/js/taxpert/`). `_copy_without_render` keeps the starter images out of Jinja.

**`repo_name`, `app_id`, `url_segment` and `storage_prefix` are independent on purpose**, even though
one answer sets all four. credit-assistant is the proof they have to be: it lives in
`credit-assistant/`, keeps its resources under `credit-assistant/`, and serves from `/app/eitc`. Two
apps generated with different `storage_prefix` values can be served from one origin without sharing a
fact graph, a watchlist or a panel layout.

## What each `include_` answer changes

`hooks/post_gen_project.py` renders every file first and then deletes what the answers turned off.
Pruning after the fact rather than wrapping each file in a Jinja conditional keeps the templates
readable as the files they will become.

| Answer | `no` removes |
|---|---|
| `include_scenario_mode` | The `--scenarioMode` flag from every `sbt run` line, and the `scenarios/` directory. |
| `include_all_screens` | The `--allScreens` flag, the `browse-all` and `path-mode` entries from the workspace config fragment, and the page's own `all-screens-bootstrap.js` and `all-screens.css`. |
| `include_taxpert_workspace` | The `--auditMode` flag, the root `package.json` (whose only content is the `taxpert` dependency), the `copy-shared-ui` and `check-shared-ui` make targets, the workspace stylesheet imports in `main.css`, the four mount fragments, `taxpert.config.json`, the `website-static/js/taxpert/` registration, the Docker and CI references to the package, and the matching `.gitignore` entries. |
| `include_fact_explorer` | The `--formativeGraph` flag, `fact-explorer.app.json`, and the `make fact-explorer` target. |
| `include_docker` | `Dockerfile`, `nginx.conf`, `.dockerignore`, both compose files, and the `up` / `down` / `logs` / `ps` / `rebuild` targets. |

A `no` to `include_taxpert_workspace` drops the `taxpert` dependency itself, along with the surfaces
it draws. The generated app has no root `package.json`, no `node_modules` to install there, and no
reference to the package anywhere. The theme and the flow runtime are unaffected, because both ship
inside the `gov.irs::formative` jar and are extracted into `resources/vendor/formative/` on every
build.

`include_fact_explorer` and `include_taxpert_workspace` are independent. Fact Explorer reads the
Formative Graph, the fact dictionary and the engine bundle, all of which are the scaffold's, so
`fact-explorer=yes` with `workspace=no` is a supported combination.

One combination has a visible consequence, and the hook prints a note about it: with
`include_all_screens=yes` and `include_taxpert_workspace=no`, Browse All still lists every screen, but
its toolbar and its two layout modes belong to the workspace, so the page arrives with only the
theme's styling on it.

## Seeing the generated app in Fact Explorer

With `include_fact_explorer=yes` the repo ships a `fact-explorer.app.json`, and that file **is** the
registration. [Fact Explorer](../fact-explorer)'s `build-registry` script globs
`../*/fact-explorer.app.json`, so putting the repo beside `fact-explorer/` is the whole of the wiring.
There is no list to edit, and the hook writes nothing outside the repo it creates.

```bash
cd my-tax-tool && make fact-explorer
cd ../fact-explorer && npm run build-registry && npm run dev
# → http://localhost:5180/fact-explorer/my-tax-tool
```

## What the starter content is for

The starter flow and facts are chosen to exercise every seam rather than to be minimal, so that a
freshly generated app demonstrates each mechanism you are likely to need.

- **Two flow pages** with an enum, a boolean and a dollar question, a `<hint>`, an `<fg-show>`, a
  `<modal-dialog>` opened by a `<modal-link>`, conditional visibility and a knockout alert.
- **Eight facts** across two files: an enum and its options, an `IsComplete` gate, a `Switch` that
  turns the chosen year into an `Int`, a `Dollar` constant, two writables, and two derived facts.
- **One determination** registered with the workspace, over `/qualifies`, with its inputs decomposed
  into two sections. Answering the flow moves the Outcome tracker's ring from part-drawn to a spoken
  outcome, which is the single assertion proving flow, fact graph, registration and workspace are all
  wired.
- **Two tests**: `FlowSpec` asserts the flow parses with every fact path resolving, and
  `EligibilitySpec` asserts the determination is right, including the case where it is incomplete
  rather than false.

When you start on your own product, replace the domain content and keep these shapes.

## Layout

```
formative-template/
├── cookiecutter.json                 the questions and the derived keys
├── hooks/post_gen_project.py         prune unselected features, chmod scripts, git init
└── {{cookiecutter.repo_name}}/       the app itself, rendered as Jinja
    ├── build.sbt                     one dependency: gov.irs::formative
    ├── Makefile                      dev, site, test, ci, the copy-* mirrors, docker
    ├── README.md                     the generated app's own README
    ├── CLAUDE.md
    ├── src/main/scala/…/Main.scala    the FormativeApp
    ├── src/main/resources/{app_id}/  flow, facts, locales, templates, website-static
    └── src/test/scala/…/             FlowSpec and EligibilitySpec
```
