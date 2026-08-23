# form-builder-template

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that generates a new Form Builder
application: a multi-language static questionnaire built on
[`gov.irs::form-builder`](https://github.com/IRS-Public/form-builder), the Scala library that turns
Flow XML plus a Fact Dictionary into a site.

What it emits is deliberately thin. The flow parser, the site generators, the Thymeleaf engine, the
node templates, the chrome locales, the browser theme, the flow runtime and Author Mode all belong
to the library. A generated application gets its own flow XML, its fact dictionary, its locales, its
brand CSS, and a `Main.scala` of about 40 lines. Everything genuinely per-application is expressed
as a registration on that `Main.scala`, such as a custom node type, a custom input type, an
overridden template, or an overridden locale key.

## Where this fits

| Repository | What it provides |
|---|---|
| [form-builder](https://github.com/IRS-Public/form-builder) | `gov.irs::form-builder`, the library every generated app is built on. Required. |
| [fact-graph](https://github.com/IRS-Public/fact-graph) | `gov.irs::factgraph`, the fact evaluation engine, as a JVM jar and a Scala.js browser bundle. Required, and pulled in transitively by form-builder. |
| [taxpert](https://github.com/IRS-Public/taxpert) | `packages/ui`, the optional workspace UI (global nav, audit panel, tool panels), and `packages/fact-explorer`, the graph viewer. |
| The Form Builder examples repository | Two worked applications, `credit-assistant` and `tax-withholding-estimator`, if you would rather read a finished one. |

Form Builder is required, because without it there is no application. Taxpert is optional. An
application generated with `include_taxpert_workspace=no` has no dependency on it at all, and still
gets the theme and the flow runtime, both of which ship inside the form-builder jar.

### Contributing
Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

This codebase is dedicated to the public domain under the [Creative Commons Zero v1.0 Universal](LICENSE.md) license (CC0 1.0).

## Legal Disclaimer: Public Repository Access

> This repository contains draft and under-development source code. It is made available to the public solely for transparency, collaboration, and research purposes.
>
> **No Endorsement or Warranty**
>
> IRS does not endorse, maintain, or guarantee the accuracy, completeness, or functionality of the code in this repository. The IRS assumes no responsibility or liability for any use of the code by external parties, including individuals, developers, or organizations. This includes, but is not limited to, any tax consequences, computation errors, data loss, or other outcomes resulting from the use or modification of this code.
>
> Use of the code in this repository is at your own risk. This repository is not intended for production use or public consumption as a finalized product.

## Requirements

Running the template needs only cookiecutter. Building the app it generates needs the rest.

| Requirement | Why |
|---|---|
| `cookiecutter` | Runs this template. `pipx install cookiecutter`, or `pip install cookiecutter`. |
| JDK 21 and sbt | The generated app is a Scala 3.7.2 sbt project, pinned to sbt 1.11.4 in `project/build.properties`. |
| Node 22 | npm supplies the vendored USWDS distribution and the ESLint / html-validate tooling. |
| `xmllint` | Used by `make validate-xml` and `make format`. `libxml2-utils` on Debian or Ubuntu. |
| A `fact-graph` checkout | See below. |
| A `form-builder` checkout | See below. |

### Resolving the two Scala libraries

The generated `build.sbt` declares one dependency, `gov.irs %% "form-builder"`, and no resolvers.
So both `gov.irs::form-builder` and the `gov.irs::factgraph` it pulls in transitively are resolved
from the local Ivy cache at `~/.ivy2/local`, which is already first in sbt's default resolver chain.
Getting them there means publishing each once from a checkout:

```bash
git clone https://github.com/IRS-Public/fact-graph.git
cd fact-graph && sbt compile fastOptJS publishLocal

git clone https://github.com/IRS-Public/form-builder.git
cd form-builder && sbt publishLocal
```

`make bootstrap` in the generated app runs the equivalent of both, so in practice you clone the two
repositories and then let the Makefile do it.

There is no shortcut to look for. Neither library is published to a remote artifact registry —
not `gov.irs::factgraph` 3.1.0-SNAPSHOT, and not `gov.irs::form-builder` — so publishing locally
from a checkout is the only way to get either one. That is also why the generated `build.sbt`
carries no `resolvers +=` line and no credentials: there is no registry to point sbt at, and
nothing to authenticate against.

`fact-graph` also supplies the Scala.js browser bundle. `make copy-fg` looks for it at
`<fact_graph_path>/js/target/scala-3.3.6/factgraph-fastopt/main.mjs`, which is what `sbt fastOptJS`
produces, and skips with a message rather than failing if it is not there.

## Quickstart

```bash
cookiecutter form-builder-template
```

Answer the prompts, then:

```bash
cd my-tax-tool
make bootstrap    # publish the libraries, install npm deps, vendor their assets
make dev          # http://localhost:3010/app/my-tax-tool/
```

The generated app lands in whichever directory you ran `cookiecutter` from, in a directory named by
your `repo_name` answer. Running it from inside `form-builder-template/` itself would nest the new
app inside the template, since cookiecutter's default output directory is `.`. The post-generation
hook detects that one case and moves the app up a level. An explicit `--output-dir` is left alone.

## The questions

| Variable | Default | What it controls |
|---|---|---|
| `project_name` | `My Tax Tool` | The human-readable name. Every other default derives from it. |
| `repo_name` | `project_name` lowercased, spaces to hyphens | The generated directory and the sbt project name. |
| `app_id` | same as `repo_name` | The resource directory under `src/main/resources`, and the classpath prefix this app's own templates resolve from. |
| `url_segment` | same as `repo_name` | The site is served from `/app/<url_segment>`. |
| `scala_package` | `gov.irs.<app_id with hyphens removed>` | The package for `Main.scala` and the tests. |
| `brand` | same as `project_name` | Shown in the dev server banner and used in page titles. |
| `storage_prefix` | same as `app_id` | Namespaces every browser storage key the site writes. |
| `dev_port` | `3010` | The dev server port, the `PORT` variable in the Makefile, and the published Docker port. |
| `form_builder_version` | `0.1.0-SNAPSHOT` | The `gov.irs::form-builder` version in `build.sbt`. |
| `factgraph_version` | `3.1.0-SNAPSHOT` | Names the vendored Scala.js bundle. The `-SNAPSHOT` suffix is stripped, giving `factgraph-3.1.0.js`. |
| `fact_graph_path` | `../fact-graph` | Where that checkout lives, resolved from the generated app's own directory. |
| `form_builder_path` | `../form-builder` | Same. |
| `taxpert_path` | `../taxpert/packages/ui` | Same. The workspace package inside the taxpert repository, rather than the repository root. Unused when the workspace is left out. |
| `include_all_screens` | `yes` | The Browse All page that lists every screen at once, and Path Mode. |
| `include_scenario_mode` | `yes` | Saved fact graphs under `scenarios/`, loadable from the Scenario modal. |
| `include_taxpert_workspace` | `yes` | The global nav, the audit panel and the tool dock. |
| `include_fact_explorer` | `yes` | A `fact-explorer.app.json` and the build flag that emits the graph Fact Explorer reads. |
| `include_docker` | `yes` | `Dockerfile`, `nginx.conf`, the two compose files, and the make targets that wrap them. |

The five `include_` options each accept `yes` or `no`, with `yes` first and therefore the default.

Three more keys in `cookiecutter.json` are not asked. `__package_path` is `scala_package` with dots
turned into slashes, and names the Scala source directories. `__js_name` is `app_id` in camelCase,
and names the symbols exported from `website-static/js/taxpert/`. `_copy_without_render` keeps the
starter images out of Jinja rendering.

`repo_name`, `app_id`, `url_segment` and `storage_prefix` are independent variables even though one
answer sets all four, and real applications do diverge. `credit-assistant` lives in a directory of
that name, keeps its resources under `credit-assistant/`, and serves from `/app/eitc`. Two apps
generated with different `storage_prefix` values can be served from one origin without sharing a
fact graph, a watchlist or a panel layout.

## What each `include_` answer changes

`hooks/post_gen_project.py` renders every file first and then deletes what the answers turned off.
Pruning after the fact rather than wrapping each file in a Jinja conditional keeps the templates
readable as the files they will become.

| Answer | `no` removes |
|---|---|
| `include_scenario_mode` | The `--scenarioMode` flag from every `sbt run` line, and the `scenarios/` directory. |
| `include_all_screens` | The `--allScreens` flag, the `browse-all` and `path-mode` entries from the workspace config fragment, and the page's own `all-screens-bootstrap.js` and `all-screens.css`. |
| `include_taxpert_workspace` | The `--auditMode` flag, the root `package.json` (whose only content is the `taxpert` dependency), the `copy-shared-ui` and `check-shared-ui` make targets, the workspace stylesheet imports in `main.css`, `styles/utilities/`, the four mount fragments, `taxpert.config.json`, the `website-static/js/taxpert/` registration, the Docker and CI references to the package, and the matching `.gitignore` and `.dockerignore` entries. |
| `include_fact_explorer` | The `--formBuilderGraph` flag, `fact-explorer.app.json`, and the `make fact-explorer` target. |
| `include_docker` | `Dockerfile`, `nginx.conf`, `.dockerignore`, both compose files, and the `up` / `down` / `logs` / `ps` / `rebuild` targets. |

A `no` to `include_taxpert_workspace` drops the `taxpert` dependency itself along with the surfaces
it draws. The generated app has no root `package.json`, no `node_modules` to install there, and no
reference to the package anywhere. The theme and the flow runtime are unaffected, because both ship
inside the `gov.irs::form-builder` jar and are extracted into `resources/vendor/form-builder/` on
every build.

`include_fact_explorer` and `include_taxpert_workspace` are independent. Fact Explorer reads the
Form Builder Graph, the fact dictionary and the engine bundle, all of which belong to the library, so
`fact-explorer=yes` with `workspace=no` is a supported combination.

One combination has a visible consequence, and the hook prints a note about it. With
`include_all_screens=yes` and `include_taxpert_workspace=no`, Browse All still lists every screen,
but its toolbar and its two layout modes belong to the workspace, so the page arrives with only the
theme's styling on it.

## What else the hook does

Beyond the pruning above, `hooks/post_gen_project.py`:

- Moves the generated app up one level if it was created inside the template directory by mistake.
  The check requires the parent to hold both a `cookiecutter.json` and a `hooks/` directory, so an
  explicit `--output-dir` elsewhere is never second-guessed.
- Makes every `scripts/*.sh` executable.
- Runs `git init --initial-branch=main` and `git add --all`, leaving you on a `main` branch with
  everything staged and nothing committed. Failure here is not fatal, and it prints a note instead.
- Prints the next steps, the resolved library paths, and any consequence of the answers you gave.

The hook writes nothing outside the project it generates.

## Where the libraries live

`fact_graph_path`, `form_builder_path` and `taxpert_path` are build-time paths resolved from the
generated app's own directory. Each defaults to a sibling checkout, and each can be any relative or
absolute path, independently of the others.

```
parent/
├── fact-graph/
├── form-builder/
├── taxpert/
│   └── packages/ui/    the workspace package, only with include_taxpert_workspace=yes
└── my-tax-tool/        generated, with the three defaults above
```

Those answers are threaded into the generated `Makefile`, the root `package.json` (as the `taxpert`
`file:` dependency), `Dockerfile`, `docker-compose.yml` and `docker-compose.override.yml` (as named
`additional_contexts`). The CI workflow describes the same checkouts from the runner's vantage point
rather than the app's, so if you move a library off the sibling layout you have to keep
`.github/workflows/ci.yml` in step by hand.

The generated workflow also checks out `your-org/fact-graph`, `your-org/form-builder` and
`your-org/taxpert` by name. Repoint those at wherever the repositories actually live before CI can
pass.

## Layout

```
form-builder-template/
├── cookiecutter.json                 the questions and the three derived keys
├── hooks/post_gen_project.py         prune unselected features, chmod scripts, git init
├── CONTRIBUTING.md
├── LICENSE.md
└── {{cookiecutter.repo_name}}/       the app itself, rendered as Jinja
```

And the app that comes out of it, with every option set to `yes`:

```
my-tax-tool/
├── build.sbt                         one dependency: gov.irs::form-builder
├── project/                          sbt version and the scalafmt plugin
├── Makefile                          dev, site, test, ci, the copy-* mirrors, docker
├── package.json                      the `taxpert` file: dependency, and nothing else
├── .scalafmt.conf
├── README.md                         the generated app's own README
├── .github/workflows/ci.yml          publish the libraries, then `make test` and `make ci`
├── Dockerfile                        three stages: publish the libraries, generate, serve with nginx
├── nginx.conf
├── docker-compose.yml                the prod-like stack
├── docker-compose.override.yml       the dev overlay: nginx plus an `sbt ~run` watcher
├── .dockerignore
├── scripts/diff-out.sh               build `main` in a worktree and diff the two out/ trees
├── fact-explorer.app.json            this app, as Fact Explorer discovers it
├── src/main/scala/<package>/Main.scala
├── src/main/resources/<app_id>/
│   ├── flow/                         index.xml, two page modules, and FlowConfig.rng
│   ├── facts/                        constants.xml, taxpayer.xml, and FactDictionaryModule.rng
│   ├── locales/                      en.yaml, es.yaml, and the generated flow_en/flow_es.yaml
│   ├── templates/fragments/          the four workspace mount points
│   ├── scenarios/                    empty, for saved fact graphs
│   ├── website-static/               styles, js, img, and the vendored mirrors
│   ├── package.json                  USWDS, plus the ESLint and html-validate tooling
│   ├── eslint.config.js
│   └── htmlvalidate.json
└── src/test/scala/<package>/         FlowSpec and EligibilitySpec
```

## What the starter content is for

The starter flow and facts exercise every seam rather than being minimal, so a freshly generated app
demonstrates each mechanism you are likely to need.

- **Two flow pages**, one per module, with an enum, a boolean and a dollar question, a `<hint>`, an
  `<fg-show>`, a `<modal-dialog>` opened by a `<modal-link>`, conditional visibility through
  `if-true`, an info alert and a knockout alert.
- **Nine facts** across two files: an enum's options and the writable enum that picks from them, an
  `IsComplete` gate, a `Switch` that turns the chosen year into an `Int`, a `Dollar` constant, two
  more writables, and two derived facts.
- **One determination** registered with the workspace, over `/qualifies`, with its inputs decomposed
  into two sections. Answering the flow moves the Outcome tracker's ring from part-drawn to a spoken
  outcome, which is one assertion that flow, fact graph, registration and workspace are all wired.
- **Two test suites**: `FlowSpec` asserts the flow parses with every fact path resolving and every
  route unique, and `EligibilitySpec` asserts the determination is right in three cases, including
  the one where it is incomplete rather than false.

When you start on your own product, replace the domain content and keep these shapes.

## Seeing the generated app in Fact Explorer

With `include_fact_explorer=yes` the repository ships a `fact-explorer.app.json`, and that file is
the registration. Fact Explorer lives in the [taxpert](https://github.com/IRS-Public/taxpert)
repository at `packages/fact-explorer`. Its `build-registry` script globs
`<apps dir>/*/fact-explorer.app.json`, where the apps directory is `FORM_BUILDER_APPS_DIR`, or
`<taxpert repo>/apps` by default. Putting the repository there, as a clone or a symlink, is the whole
of the wiring. There is no list to edit.

```bash
cd my-tax-tool && make fact-explorer
ln -s "$PWD" /path/to/taxpert/apps/          # once
cd /path/to/taxpert/packages/fact-explorer
npm run build-registry && npm run dev
# then open http://localhost:5180/fact-explorer/my-tax-tool
```

## Gotchas

- **A new build flag must not be a prefix of an existing one.** The hook removes a flag from the
  generated `Makefile` and `docker-compose.override.yml` with a plain string replace, so adding a
  `--scenario` flag alongside `--scenarioMode` would leave `Mode` behind in every `sbt run` line.
- **`make diff-out` needs commits.** The hook stages everything and commits nothing, so the script
  has no `main` to compare against until you make the first commit.
- **The Docker build needs the sibling paths spelled out** when you invoke `docker build` directly.
  `docker compose` passes them from `additional_contexts`. A bare `docker build` needs three
  `--build-context` flags, which the `Dockerfile` header shows.
- **Editing form-builder or fact-graph does not reach a running container.** Both are resolved from
  the image's own Ivy cache rather than a bind mount, so `make rebuild` is what picks up a change.
