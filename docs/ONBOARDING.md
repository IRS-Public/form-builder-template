# ONBOARDING

This document is the reference for the template itself: what it asks, what each answer changes, what
the generated application contains, and where it expects the libraries to be.

This guide covers how to quickstart generating an application. It does not cover how to run the application 
or leverage tools like taxpert. For that, see
[QUICKSTART.md](https://github.com/IRS-Public/taxpert/blob/main/docs/QUICKSTART.md) in the taxpert
repository, which covers prerequisites, the Docker path, the native path, and what to run after
changing a library so the change reaches everything that consumes it.

See [Form Builder Examples](https://github.com/IRS-Public/form-builder-examples) for applications
built using this template. To understand the difference between Taxpert, Form Builder and the Fact Graph, see
[this doc](https://github.com/IRS-Public/taxpert/blob/main/docs/adr/taxpert-form-builder-fact-graph.md).

## Generating an application

Running the template needs only `cookiecutter`. Building the generated application needs either
Docker or the full toolchain, both of which the QUICKSTART covers.

```bash
cd ~
git clone https://github.com/IRS-Public/fact-graph.git
git clone https://github.com/IRS-Public/form-builder.git
git clone https://github.com/IRS-Public/taxpert.git      # optional, for the workspace and Fact Explorer
git clone https://github.com/IRS-Public/form-builder-template.git      # optional, to run this template from a local checkout

cookiecutter form-builder-template   # or a path to a local checkout
```

Run cookiecutter from where you want the application to land, not from inside a checkout of this
template. The generated app goes into whichever directory you ran cookiecutter from, in a directory
named by your `repo_name` answer, and cookiecutter's default output directory is `.`. The
post-generation hook detects that one case and moves the application up a level. An explicit
`--output-dir` is left alone.

Then pick one of the two ways to run the new application. Use either the Docker path or the native
path, not both.

```bash
cd ~/my-application
make up                     # Docker: builds both libraries in the image, no local toolchain needed
```

```bash
cd ~/my-application
make bootstrap              # Native: publish both libraries and vendor their assets, once
make dev                    # then serve at http://localhost:<dev_port>/app/<url_segment>/
```

## The questions

| Variable | Default | What it controls |
|---|---|---|
| `project_name` | `My Application` | The human-readable name. Every other default derives from it. |
| `repo_name` | `project_name` lowercased, spaces to hyphens | The generated directory and the sbt project name. |
| `app_id` | same as `repo_name` | The resource directory under `src/main/resources`, and the classpath prefix this app's own templates resolve from. |
| `url_segment` | same as `repo_name` | The site is served from `/app/<url_segment>`. |
| `scala_package` | `gov.irs.<app_id with hyphens removed>` | The package for `Main.scala` and the tests. |
| `brand` | same as `project_name` | Shown in the dev server banner and used in page titles. |
| `storage_prefix` | same as `app_id` | Namespaces every browser storage key the site writes. |
| `dev_port` | `3010` | The dev server port, the `PORT` variable in the Makefile, and the published Docker port. |
| `author_port` | `3004` | The Author Mode API port. Published on `127.0.0.1` only, since it writes to your working tree. Two generated applications on one machine cannot both hold it. |
| `form_builder_version` | `0.1.0-SNAPSHOT` | The `gov.irs::form-builder` version in `build.sbt`. |
| `factgraph_version` | `3.1.0-SNAPSHOT` | Names the vendored Scala.js bundle. The `-SNAPSHOT` suffix is stripped, giving `factgraph-3.1.0.js`. |
| `fact_graph_path` | `../fact-graph` | Where that checkout lives, resolved from the generated app's own directory. |
| `form_builder_path` | `../form-builder` | Same. |
| `taxpert_repo_path` | `../taxpert` | Same. The taxpert repository root, which `unregister-explorer` and the Fact Explorer registration script write into. |
| `taxpert_path` | `<taxpert_repo_path>/packages/ui` | Derived. The workspace npm package inside that repository. Unused when the workspace is left out. |
| `include_all_screens` | `yes` | The Browse All page that lists every screen at once, and Path Mode. |
| `include_scenario_mode` | `yes` | Saved fact graphs under `scenarios/`, loadable from the Scenario modal. |
| `include_taxpert_workspace` | `yes` | The global nav, the audit panel and the tool dock. |
| `include_fact_explorer` | `yes` | A `fact-explorer.app.json` and the build flag that emits the graph Fact Explorer reads. |
| `include_docker` | `yes` | `Dockerfile`, `nginx.conf`, the two compose files, and the make targets that wrap them. |

The five `include_` options each accept `yes` or `no`, with `yes` first and therefore the default.
`repo_name`, `app_id`, `url_segment` and `storage_prefix` are independent variables even though one
answer sets all four, and real applications do diverge. For instance, `credit-assistant` lives in a directory of
that name, keeps its resources under `credit-assistant/`, and serves from `/app/eitc`. Two apps
generated with different `storage_prefix` values can be served from one origin without sharing a
fact graph, taxpert, or other layouts.


## What each `include_` answer changes

`hooks/post_gen_project.py` renders every file first and then deletes what the answers turned off.
Pruning after the fact rather than wrapping each file keeps the templates
readable as the files they will become.

| Answer | `no` removes |
|---|---|
| `include_scenario_mode` | The `--scenarioMode` flag from every `sbt run` line, and the `scenarios/` directory. |
| `include_all_screens` | The `--allScreens` flag, the `browse-all` and `path-mode` entries from the workspace config fragment, and the page's own `all-screens-bootstrap.js` and `all-screens.css`. |
| `include_taxpert_workspace` | The `--auditMode` flag, the root `package.json` (whose only content is the `taxpert` dependency), the `copy-shared-ui` and `check-shared-ui` make targets, the workspace stylesheet imports in `main.css`, `styles/utilities/`, the four mount fragments, `taxpert.config.json`, the `website-static/js/taxpert/` registration, the Docker and CI references to the package, and the matching `.gitignore` and `.dockerignore` entries. |
| `include_fact_explorer` | The `--formBuilderGraph` flag, `fact-explorer.app.json`, and the `make fact-explorer` target. |
| `include_docker` | `Dockerfile`, `nginx.conf`, `.dockerignore`, both compose files, and the `up` / `down` / `logs` / `ps` / `rebuild` / `register-explorer` / `unregister-explorer` targets. |

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
theme's styling on it. We recommend against that combination. If you want Browse All, include the
Taxpert workspace with it.

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

## Output Scaffold

The starter flow and facts exercise every integration point rather than being minimal, so a freshly generated app
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

When you start on your own product, all of this domain content can be replaced based off of your needs


## Where the libraries live

`fact_graph_path`, `form_builder_path` and `taxpert_repo_path` are build-time paths resolved from
the generated app's own directory. Each defaults to a sibling checkout, and each can be any relative
or absolute path, independently of the others. `taxpert_path` derives from `taxpert_repo_path` and
points at the workspace package inside it.

```
parent/
├── fact-graph/
├── form-builder/
├── taxpert/
│   └── packages/ui/    the workspace package, only with include_taxpert_workspace=yes
└── my-application/     generated, with the three defaults above
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
my-application/
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
├── scripts/register-with-taxpert.sh  write this app's compose fragment into the taxpert stack
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

## Seeing the generated app in Fact Explorer

With `include_fact_explorer=yes` the repository ships a `fact-explorer.app.json`, and that file is
the registration to Fact Explorer. Fact Explorer lives in the [Taxpert](https://github.com/IRS-Public/taxpert)
repository at `packages/fact-explorer`. Its `build-registry` script globs
`<apps dir>/*/fact-explorer.app.json`, where the apps directory is `FORM_BUILDER_APPS_DIR`, or
`<taxpert repo>/apps` by default.

In Docker a symlink does not work, because a bind mount carries the link rather than its target.
`make up` runs `make register-explorer`, which writes a compose fragment into the taxpert stack
instead. The [QUICKSTART.md](https://github.com/IRS-Public/taxpert/blob/main/docs/QUICKSTART.md#how-fact-explorer-finds-an-application)
covers both discovery paths.

Natively, putting the repository there as a clone or a symlink is the whole of the wiring:

```bash
cd my-application && make fact-explorer
ln -s "$PWD" /path/to/taxpert/apps/          # once
cd /path/to/taxpert/packages/fact-explorer
npm run build-registry && npm run dev
# then open http://localhost:5180/fact-explorer/my-application
```

