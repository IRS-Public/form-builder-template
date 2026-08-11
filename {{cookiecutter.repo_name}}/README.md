# {{ cookiecutter.project_name }}

A multi-language static questionnaire, built as a **Formative app**. What lives in this repository
is the domain — the flow, the fact dictionary, the locales, the brand styling — and a ~40-line
`Main.scala`. Everything else is two libraries.

Serves from `/app/{{ cookiecutter.url_segment }}`.

## What this is made of

| | Where | What it gives you |
|---|---|---|
| `gov.irs::factgraph` | `{{ cookiecutter.fact_graph_path }}` | the evaluation engine, on the JVM and in the browser |
| `gov.irs::formative` | `{{ cookiecutter.formative_path }}` | Flow XML + a Fact Dictionary → a static site: parser, generators, Thymeleaf engine, node templates, chrome locales |
| `taxpert` | `{{ cookiecutter.taxpert_path }}` | the workspace laid over the running app — global nav, audit panel, Inspect / Outcome tracker / Watchlist — plus the browser flow runtime and the theme |

None of the three is published to a remote yet, so **this app expects all three at the paths
above** — not necessarily beside it. Those are the answers this app was generated with
(`fact_graph_path` / `formative_path` / `taxpert_path` in `cookiecutter.json`); if a library moves,
update the path everywhere it is used: `Makefile`, `package.json`, `docker-compose.yml` /
`docker-compose.override.yml`, and `.github/workflows/ci.yml`'s checkout `path:`s. `make bootstrap`
builds and vendors the libraries from wherever they are; the same contract is spelled out in
`.github/workflows/ci.yml`.

The default layout — and the one CI assumes — is three sibling checkouts:

```
parent/
├── fact-graph/
├── formative/
├── taxpert/
└── {{ cookiecutter.repo_name }}/     ← you are here
```

## Getting started

```bash
make bootstrap    # once: publish the sibling libraries, vendor their assets
make dev          # http://localhost:{{ cookiecutter.dev_port }}/app/{{ cookiecutter.url_segment }}/
```

`make help` lists every target. The ones you will use:

| Target | What it does |
|---|---|
| `make dev` | dev server with the Taxpert workspace, the all-screens page and scenario mode built in |
| `make dev-author` | the same, plus Author Mode — edit the flow and facts from the browser, on port 3004 |
| `make dev-one-question` | the same, one question per screen |
| `make site` | the production build: the flow and nothing else, into `./out` |
| `make test` | ScalaTest + a scalafmt check |
| `make ci` | build, then every validator: vendored mirror, RELAX NG, HTML, JS, Scala formatting |
| `make diff-out` | build `main` in a throwaway worktree and diff the two `out/` trees |

## Where things go

```
src/main/scala/{{ cookiecutter.__package_path }}/Main.scala   the FormativeApp — the whole Scala surface
src/main/resources/{{ cookiecutter.app_id }}/
├── flow/           the questionnaire. index.xml names the modules; each <page> becomes a directory
├── facts/          the fact dictionary, merged alphabetically; last definition wins on a duplicate path
├── locales/        this app's strings. flow_*.yaml are GENERATED from the flow — never edit them
├── templates/      only what this app overrides; everything else is inherited from the scaffold
├── scenarios/      saved fact graphs the Scenario modal offers
└── website-static/ served verbatim at /resources — styles, js, img, and the vendored mirrors
```

**Three rules that will save you an afternoon:**

1. **Authored text goes in the flow XML, not in a locale file.** It is extracted to
   `locales/flow_en.yaml` on every build; translate it in `flow_es.yaml`. Editing `flow_en.yaml`
   by hand loses the edit at the next build.
2. **Never hand-edit anything under `website-static/vendor/`.** All three are generated mirrors with
   exactly one writer each (`make copy-shared-ui`, `make copy-uswds`, `make copy-fg`).
   `make check-shared-ui` fails the build if you do.
3. **Override, don't fork.** To change a node template, drop a same-named file into
   `templates/nodes/`; app templates resolve ahead of the library's. To change a chrome string,
   declare that key in `locales/en.yaml`. To change styling, add a rule below the theme import in
   `website-static/styles/main.css`.

## Adding a question

1. Add the fact to `facts/` — `<Writable>` for something a taxpayer answers, `<Derived>` for
   something computed from other facts.
2. Add an `<fg-set path="/yourFact">` to the right page in `flow/`, with a `<question>` and an
   `<input type="…">`.
3. `make validate-xml` — the flow is checked against `flow/FlowConfig.rng` and the facts against
   `facts/FactDictionaryModule.rng`. Widen the schema when you widen the flow; both files are yours.
4. Add a case to `src/test/scala/…/EligibilitySpec.scala` if it changes a determination.

## Extending the scaffold

Two seams, both registrations on the `FormativeApp` in `Main.scala` rather than edits to the
library:

- **`nodeTypes`** — a flow element the scaffold has never heard of. Write a `FlowNodeParser` here,
  put its Thymeleaf template in `templates/nodes/`, and widen `flow/FlowConfig.rng` to allow it.
- **`inputTypes`** — a new input, or a replacement for a built-in. Registering an existing name
  replaces it rather than adding a second one.

If you find yourself wanting to change something inside `{{ cookiecutter.formative_path }}` or
`{{ cookiecutter.taxpert_path }}`, that is worth doing — but do it there, and run both of the other
apps' `make ci` afterwards.
