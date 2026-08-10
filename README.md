# formative-template

A [cookiecutter](https://cookiecutter.readthedocs.io/) that emits a new **Formative app**: a
multi-language static questionnaire built on `gov.irs::formative` and the `taxpert` workspace.

What it generates is deliberately *thin*. The parser, the generators, the Thymeleaf engine, the 30
node templates, the chrome locales and Author Mode all belong to the library; a new app gets its
flow, its facts, its locales, its brand CSS and a ~40-line `Main.scala`.

> **This template does not copy the generator, and that is the point.** The two apps in this
> monorepo had forked it between them — 23 of one app's 28 Scala files shared a basename with the
> other's, differing mostly by their `package` line. A template that copied the generator would have
> made that fork #3. Everything genuinely per-app is a *registration* instead: a custom node type, a
> custom input type, an overridden template, an overridden locale key.

## Use it

```bash
pipx install cookiecutter        # or: pip install cookiecutter
cookiecutter formative-template
```

The generated app expects the three libraries checked out beside it:

```
parent/
├── fact-graph/
├── formative/
├── taxpert/
└── hello-tax/          ← generated
    make bootstrap && make dev
```

Then `http://localhost:3010/app/hello-tax/`.

## The questions

| Variable | Default | Notes |
|---|---|---|
| `project_name` | `My Tax Tool` | the human name; everything else is derived from it |
| `repo_name` | slug of the name | the directory and the sbt project |
| `app_id` | = `repo_name` | the resource directory under `src/main/resources` |
| `url_segment` | = `repo_name` | the site is served from `/app/<url_segment>` |
| `scala_package` | `gov.irs.<appid>` | |
| `brand` | = `project_name` | shown in the nav and the page title |
| `storage_prefix` | = `app_id` | namespaces every browser storage key the workspace writes |
| `dev_port` | `3010` | |
| `formative_version`, `factgraph_version` | `…-SNAPSHOT` | swap for a released version once these are published |
| `include_all_screens` | `yes` | the generated page that lists every screen at once |
| `include_scenario_mode` | `yes` | saved fact graphs, loadable from the Scenario modal |
| `include_taxpert_workspace` | `yes` | the global nav, audit panel and tool dock (`--auditMode`); `taxpert` stays a dependency either way for its flow runtime and theme |
| `include_docker` | `yes` | `Dockerfile` + `nginx.conf` for a prod-like static image |

**`repo_name`, `app_id`, `url_segment` and `storage_prefix` are independent on purpose**, even
though one answer sets all four. credit-assistant is the proof they have to be: it lives in
`credit-assistant/`, keeps its resources under `credit-assistant/`, and serves from `/app/eitc`.

Two apps generated with different `storage_prefix` values can be served from the same origin without
sharing a fact graph, a watchlist or a panel layout.

## What the starter content is for

It is chosen to **exercise every seam**, not to be minimal — a template whose output does nothing
teaches nothing about what to do next:

- **Two flow pages** with an enum, a boolean and a dollar question, a `<hint>`, an `<fg-show>`, a
  `<modal-dialog>` opened by a `<modal-link>`, conditional visibility (`if-true`) and a knockout
  alert.
- **Eight facts** across two files: an enum and its options, an `IsComplete` gate, a `Switch` that
  turns the chosen year into an `Int`, a `Dollar` constant, two writables, and two derived facts —
  a comparison and the conjunction over it.
- **One determination** in the workspace, over `/qualifies`, with its inputs decomposed into two
  sections. Answering the flow visibly moves the Outcome tracker's ring from part-drawn to a spoken
  outcome, which is the single assertion that proves flow → fact graph → registration → workspace
  are all wired.
- **Two tests**: the flow parses with every fact path resolving, and the determination is right —
  including the case where it is *incomplete* rather than false.

Delete the domain and keep the shapes.

## Layout

```
formative-template/
├── cookiecutter.json
├── hooks/post_gen_project.py        prune unselected features, chmod scripts, git init
└── {{cookiecutter.repo_name}}/      the app
```

`post_gen_project.py` does the pruning rather than wrapping each file in `{% if %}`, so the templates
stay readable as the files they will become — a Makefile full of Jinja conditionals is a Makefile
nobody can check by eye.
