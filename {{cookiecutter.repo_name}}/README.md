# {{ cookiecutter.project_name }}

A multi-language static questionnaire, built as a Form Builder application. Flow XML describes the
questions, a fact dictionary describes the tax facts behind them, and `gov.irs::form-builder` turns
the two into a site: every page, in every language, as plain HTML under `./out`.

This repository holds the domain. The flow, the facts, the locales, the brand styling, and a
`Main.scala` of about 40 lines. Everything else comes from the libraries below.

Serves from `/app/{{ cookiecutter.url_segment }}`.

## What this is built on

| Library | Where | What it gives you |
|---|---|---|
| `gov.irs::factgraph` | `{{ cookiecutter.fact_graph_path }}` | The fact evaluation engine, as a JVM jar and a Scala.js browser bundle. |
| `gov.irs::form-builder` | `{{ cookiecutter.form_builder_path }}` | The scaffold: flow parser, site generators, Thymeleaf engine, node templates, chrome locales, the theme and the browser flow runtime. |
{%- if cookiecutter.include_taxpert_workspace == 'yes' %}
| `taxpert` | `{{ cookiecutter.taxpert_path }}` | The workspace laid over the running app: global nav, audit panel, and the Inspect / Outcome tracker / Watchlist tool panels. Optional, and this app was generated with it. |
{%- endif %}

Each is resolved from a local checkout rather than a remote, so this app expects each at the path
above. Those are the answers it was generated with, resolved from this app's own directory rather
than assumed to be siblings. If a library moves, update the path in the `Makefile`{% if cookiecutter.include_taxpert_workspace == 'yes' %}, `package.json`{% endif %}{% if cookiecutter.include_docker == 'yes' %},
`Dockerfile`, `docker-compose.yml`, `docker-compose.override.yml`{% endif %} and the checkout `path:`s in
`.github/workflows/ci.yml`.

The default layout, and the one CI assumes:

```
parent/
├── fact-graph/
├── form-builder/
{%- if cookiecutter.include_taxpert_workspace == 'yes' %}
├── taxpert/
│   └── packages/ui/    the workspace package this app depends on
{%- endif %}
└── {{ cookiecutter.repo_name }}/
```
{% if cookiecutter.include_taxpert_workspace != 'yes' %}
This app was generated without the Taxpert workspace, so there is no nav, no audit panel and no tool
dock, and no npm dependency on the `taxpert` package at all. The theme and the flow runtime are
unaffected: both ship inside the `form-builder` jar and are extracted into
`resources/vendor/form-builder/` on every build.
{% endif %}
## Requirements

JDK 21, sbt, Node 22, and `xmllint` for the XML validators (`libxml2-utils` on Debian or Ubuntu).

`build.sbt` names one dependency, `gov.irs %% "form-builder"`, and declares no resolvers. Both that
library and the `gov.irs::factgraph` it pulls in transitively are resolved from the local Ivy cache
at `~/.ivy2/local`, so each has to be published there once from its checkout. `make bootstrap` does
that for you. Note that `gov.irs::factgraph` is published to no remote repository, and
`gov.irs::form-builder` is published to GitHub Packages, which requires a token even to read, so a
local publish is the path of least resistance either way.

## Getting started

```bash
make bootstrap    # once: publish the libraries, install deps, vendor their assets
make dev          # http://localhost:{{ cookiecutter.dev_port }}/app/{{ cookiecutter.url_segment }}/
```
{% if cookiecutter.include_docker == 'yes' %}
Or skip the local toolchain entirely with `make up`, which builds the libraries, generates the site,
serves it, and leaves an `sbt ~run` watcher regenerating on every edit. Same URL, same flags.
{% endif %}
`make help` lists every target. The ones you will use:

| Target | What it does |
|---|---|
| `make dev` | Dev server with the developer surfaces this app was generated with, watching for changes. |
| `make dev-author` | The same, plus Author Mode: edit flow text and fact values from the browser, backed by a local API on port 3004. |
| `make dev-one-question` | The same, split into one question per screen. |
| `make debug` | The same, with a JVM debug port on 5005. |
| `make site` | The production build into `./out`. No flags, so the flow and nothing else. |
| `make test` | ScalaTest, plus a scalafmt check. `make test-watch` for the watching version. |
| `make format` | Format the Scala, the fact XML and the JavaScript. |
| `make ci` | Build, then every validator in turn. `make ci-setup` installs what the validators need. |
| `make clean` | Delete `target/`, `project/*/target/` and `out/`. |
| `make diff-out` | Build `main` in a throwaway worktree and diff the two `out/` trees. Use it for any change meant to be output-neutral. |
{%- if cookiecutter.include_fact_explorer == 'yes' %}
| `make fact-explorer` | Build with `--formBuilderGraph` and print this app's Fact Explorer URL. |
{%- endif %}
{%- if cookiecutter.include_docker == 'yes' %}
| `make up` / `down` / `logs` / `ps` / `rebuild` | The Docker stack. `rebuild` is the escape hatch for a stale sibling library. |
{%- endif %}

The `copy-fg`{% if cookiecutter.include_taxpert_workspace == 'yes' %}, `copy-shared-ui`{% endif %} and `copy-uswds` targets regenerate the vendored mirrors under
`website-static/vendor/`. Every build target runs them first, so you rarely call one by hand.

## Where things go

At the root of the repository:

```
build.sbt                       one dependency, and the mainClass for `sbt run`
Makefile                        every command above
project/                        the sbt version and the scalafmt plugin
scripts/diff-out.sh             what `make diff-out` runs
.github/workflows/ci.yml        checks out and publishes the libraries, then runs `make test` and `make ci`
{%- if cookiecutter.include_taxpert_workspace == 'yes' %}
package.json                    the `taxpert` file: dependency, and nothing else
{%- endif %}
{%- if cookiecutter.include_fact_explorer == 'yes' %}
fact-explorer.app.json          this app, as Fact Explorer discovers it
{%- endif %}
{%- if cookiecutter.include_docker == 'yes' %}
Dockerfile                      three stages: publish the libraries, generate the site, serve it
nginx.conf                      the runtime web server, over the generator's ./out
docker-compose.yml              the prod-like stack
docker-compose.override.yml     the dev overlay: nginx plus an `sbt ~run` watcher
{%- endif %}
```

And the app itself:

```
src/main/scala/{{ cookiecutter.__package_path }}/Main.scala
    the FormBuilderApp value and one call to FormBuilder.run. The whole Scala surface.

src/test/scala/{{ cookiecutter.__package_path }}/
    FlowSpec and EligibilitySpec.

src/main/resources/{{ cookiecutter.app_id }}/
├── flow/           the questionnaire. index.xml names the modules, and each <page> is a directory
├── facts/          the fact dictionary, merged across files
├── locales/        this app's strings. flow_*.yaml are GENERATED from the flow, so never edit them
├── templates/      only what this app overrides. Everything else comes from the scaffold
{%- if cookiecutter.include_scenario_mode == 'yes' %}
├── scenarios/      saved fact graphs the Scenario modal offers
{%- endif %}
├── package.json    USWDS, plus the ESLint and html-validate tooling the validators use
└── website-static/ served verbatim at /resources: styles, js, img, and the vendored mirrors
```

### Flow XML

`flow/index.xml` names each module with `<module src="…"/>`, and the scaffold splices them together
before parsing. A `<page route="…">` becomes a directory in the built site, and routes must be
unique across the whole flow. Inside a page you have `<section>`, `<fg-set path="/someFact">` with a
`<question>` and an `<input type="…">`, `<fg-alert>`, `<fg-detail>`, `<fg-collection>`,
`<modal-dialog>` with `<modal-link>`, and ordinary HTML for anything that is just prose.

Authored text lives here rather than in a locale file. Every question, hint and alert heading is
extracted into `locales/flow_en.yaml` on every build.

### Facts

`facts/*.xml` hold the `<Fact path="…">` definitions: `<Writable>` for something a taxpayer answers,
`<Derived>` for something computed from other facts. Every file in the directory is loaded
alphabetically and merged into one dictionary, and on a duplicate path the last definition wins.

The facts are validated against `facts/FactDictionaryModule.rng`, and the flow against
`flow/FlowConfig.rng`. Both schemas belong to this app, so widen them when you widen the flow.

A fact path in the flow that does not resolve in the dictionary fails the build, and `FlowSpec` is
what catches it.

### Locales

`locales/en.yaml` and `locales/es.yaml` carry this app's own words, layered over the chrome strings
the scaffold ships. Lookup is app first, then the library, then the generated flow locale, so
declaring a key the scaffold also has overrides it without copying the rest.
{%- if cookiecutter.include_all_screens == 'yes' %}

One key per flow module lives under `all-screens.section.*`, and supplies the section headings on the
Browse All listing. A module with no heading renders as the key itself.
{%- endif %}

`locales/flow_en.yaml` and `locales/flow_es.yaml` are generated from the flow XML. Translate into
`flow_es.yaml`, whose human translations are preserved when it is re-synced. Editing `flow_en.yaml`
by hand loses the edit at the next build.

### Brand CSS

`website-static/styles/main.css` imports USWDS, then the Form Builder theme, then this app's own
`components/brand.css`. Put your overrides in `brand.css` or below the theme import, where they win
by ordinary cascade order. Do not fork a theme file to change one value.
{% if cookiecutter.include_taxpert_workspace == 'yes' %}
### The workspace mounts

`templates/fragments/` holds four fragments the library ships empty and this app fills in:
`workspace-head.html` (the stylesheets and element modules), `workspace-enable.html` (the call that
turns the workspace on), `workspace-all-screens.html` (the screens toolbar), and
`taxpert-config.html` (the nav taxonomy, the determinations, the endpoints). Only these fragments
name a path inside `vendor/taxpert/`, which is what keeps the library free of any reference to a
package an app can drop.

The code those fragments call, meaning the fact-graph port and the fact paths the outcomes are
built from, lives in `website-static/js/taxpert/{{ cookiecutter.app_id }}-graph.js`. The split is
there because labels go through Thymeleaf and are resolved per locale at build time, while
`website-static/` is served verbatim and never passes through Thymeleaf. A string written there
would be English in the Spanish build.
{% endif %}
## Three rules to follow

1. **Authored text goes in the flow XML.** `locales/flow_*.yaml` are build outputs.
2. **Never hand-edit anything under `website-static/vendor/`.** Every directory in there is a
   generated mirror with exactly one writer: `make copy-uswds` for USWDS, `make copy-fg` for the
   Scala.js fact graph,{% if cookiecutter.include_taxpert_workspace == 'yes' %} `make copy-shared-ui` for taxpert,{% endif %} and the scaffold itself for
   `vendor/form-builder/`, which it extracts from its own jar as it generates the site.{% if cookiecutter.include_taxpert_workspace == 'yes' %}
   `make check-shared-ui` fails the build if the taxpert mirror drifts.{% endif %}
3. **Override rather than fork.** Change a node template by dropping a same-named file into
   `templates/nodes/`, since app templates resolve ahead of the library's. Change a chrome string by
   declaring that key in `locales/en.yaml`.

## Adding a question

1. Add the fact to `facts/`.
2. Add an `<fg-set path="/yourFact">` to the right page in `flow/`, with a `<question>` and an
   `<input type="…">`.
3. Run `make validate-xml`.
4. Add a case to `src/test/scala/{{ cookiecutter.__package_path }}/EligibilitySpec.scala` if it
   changes a determination.

## Extending the scaffold

Two seams, both registrations on the `FormBuilderApp` in `Main.scala` rather than edits to the
library:

- **`nodeTypes`** maps a flow element the scaffold has never heard of to a `FlowNodeParser`. Put the
  element's Thymeleaf template in `templates/nodes/`, and widen `flow/FlowConfig.rng` to allow it.
{%- if cookiecutter.include_fact_explorer == 'yes' %}
  Mirror the tag name in `customFlowTags` in `fact-explorer.app.json`, or Fact Explorer rejects it.
{%- endif %}
- **`inputTypes`** maps an `<input type="…">` value to an `InputParser`. Registering an existing name
  replaces the built-in rather than adding a second one.

Both maps merge over the built-ins, so either one can also replace something the library provides.

## Deciding where a change goes

| The change is about… | It belongs in |
|---|---|
| A question, a rule, a threshold, a word a taxpayer reads | this repository |
| How any Flow XML becomes HTML: the parser, a generator, a node template, a chrome string, the theme, the flow runtime | `{{ cookiecutter.form_builder_path }}` |
{%- if cookiecutter.include_taxpert_workspace == 'yes' %}
| The workspace: nav, audit panel, Inspect / Outcome tracker / Watchlist | `{{ cookiecutter.taxpert_path }}` |
{%- endif %}

A change in a library needs `sbt test publishLocal` (or `npm test`) there, and then a `make ci` in
every app built on it. A second app is what catches an assumption that only holds for the first.

## Gotchas

- **An incomplete fact has no value at all.** A derived fact over an unanswered input returns `None`
  rather than `false`. Code that collapses the two will tell a taxpayer they do not qualify when the
  honest answer is that we have not asked yet. `EligibilitySpec`'s third case is the pattern to copy.
- **`make validate-templates`** rejects HTML comments inside inline `<script>` blocks. They are legal
  in a classic script and a syntax error in a module, and nothing else in the build catches it.
- **Both RELAX NG schemas are yours.** `make validate-xml` runs the facts half and the flow half, and
  a schema that is never widened alongside the flow it describes quietly drifts out of agreement
  with it.
- **`make diff-out` needs a commit on `main`.** A freshly generated repository has everything staged
  and nothing committed, so make the first commit before expecting a diff.
- **`.github/workflows/ci.yml` checks out the libraries by name** from `your-org/…` placeholders.
  Repoint them at the real repositories before CI can pass.
