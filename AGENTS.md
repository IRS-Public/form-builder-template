# AGENTS.md: form-builder-template

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that generates a new Form Builder
application. Nothing is built in this repository. It holds the questions, the files as they will be
rendered, and one post-generation hook that prunes whatever the answers turned off.

[docs/ONBOARDING.md](docs/ONBOARDING.md) is the authoritative reference for the questions, what each
answer changes, and where the libraries resolve from. Read it before making a change. Setup and run
instructions for a generated application live in one place for the whole ecosystem, the
[QUICKSTART.md](https://github.com/IRS-Public/taxpert/blob/main/QUICKSTART.md) in the taxpert
repository, so do not add them here.

## Where this fits

| Repository | What it is |
|---|---|
| [fact-graph](https://github.com/IRS-Public/fact-graph) | `gov.irs::factgraph`, the rules engine. |
| [form-builder](https://github.com/IRS-Public/form-builder) | `gov.irs::form-builder`, the scaffold. Parsers, generators, node templates, chrome locales, the theme, the flow runtime, Author Mode. |
| [taxpert](https://github.com/IRS-Public/taxpert) | The optional workspace UI and its companion services. |
| **form-builder-template** (here) | Generates an application over those libraries. |
| [form-builder-examples](https://github.com/IRS-Public/form-builder-examples) | The two reference applications. |

## Deciding where a change belongs

A generated application holds the thin remainder: its Flow XML, its Fact Dictionary, its locales,
its brand CSS, and a `Main.scala` of about 40 lines. Everything else belongs to a library.

| The change is about | It goes in |
|---|---|
| starter content, the questions a new application begins with, the shape of the generated repository | here |
| how any Flow XML becomes HTML: the parser, a generator, a node template, a chrome string, the theme, the flow runtime, Author Mode | `form-builder` |
| the workspace: nav, audit panel, tool panels, Fact Explorer, the assistant service | `taxpert` |

Before adding machinery to `{{cookiecutter.repo_name}}/`, check whether every generated application
would want it. If so, it is a library change, and the template should only register the result.
Registration is the mechanism in each case. A node template is overridden by dropping a same-named
file into the application's `templates/`, a chrome string by declaring that key in its
`locales/en.yaml`, and a custom node or input type by registering it on the `FormBuilderApp` in
`Main.scala`.

## Layout

| Path | What it is |
|---|---|
| `cookiecutter.json` | The questions, their defaults, the derived values (`__package_path`, `__js_name`), and `_copy_without_render` |
| `hooks/post_gen_project.py` | Renders first, then prunes. All of the conditional logic lives here |
| `{{cookiecutter.repo_name}}/` | The application as it will be generated: `build.sbt`, `Makefile`, `src/main/scala/.../Main.scala`, `src/main/resources/{{cookiecutter.app_id}}/{flow,facts,locales,templates,scenarios,website-static}/`, Docker files, CI workflow |
| `docs/ONBOARDING.md` | The questions, what each answer changes, the generated layout, gotchas |

## How the conditionals work

Cookiecutter renders every file, and then the hook deletes what the answers turned off. Pruning
after the fact keeps each template readable as the file it will become, which wrapping every file
in a Jinja conditional would not. The hook's helpers are `strip_flag`, `drop`, `drop_blocks`
(blank-line separated, so a comment is removed along with the thing it explains), `drop_lines`, and
`replace_in`.

| A `no` to | Removes |
|---|---|
| `include_scenario_mode` | The `--scenarioMode` flag and the `scenarios/` directory |
| `include_all_screens` | The `--allScreens` flag, the `browse-all` and `path-mode` entries in the workspace config fragment, and the page's own `all-screens-bootstrap.js` and `all-screens.css` |
| `include_taxpert_workspace` | The `--auditMode` flag, the root `package.json` (whose only content is the `taxpert` dependency), the `copy-shared-ui` and `check-shared-ui` targets, the workspace stylesheet imports, `styles/utilities/`, the four mount fragments, `taxpert.config.json`, and the Docker and CI references |
| `include_fact_explorer` | The `--formBuilderGraph` flag, `fact-explorer.app.json`, and the `make fact-explorer` target |
| `include_docker` | `Dockerfile`, `nginx.conf`, `.dockerignore`, both compose files, and the stack targets |

A `no` to `include_taxpert_workspace` drops the dependency along with the surfaces it draws. The
generated application then has no root `package.json`, nothing to install there, and no reference
to the package anywhere. It still gets the theme and the flow runtime, because both ship inside the
`gov.irs::form-builder` jar. That property is worth protecting. A change that makes taxpert
load-bearing again belongs in a different repository.

`include_fact_explorer` and `include_taxpert_workspace` are independent, and both combinations are
supported.

## Testing a change

There is no test suite here. Generate an application and build it:

```bash
cookiecutter . --output-dir /tmp/fbt-check --no-input
cd /tmp/fbt-check/my-tax-tool
make bootstrap
make ci
```

`make bootstrap` publishes `gov.irs::factgraph` and `gov.irs::form-builder` from local checkouts
into `~/.ivy2/local` and installs the npm dependencies. Both library paths are answers
(`fact_graph_path`, `form_builder_path`), and each defaults to a sibling checkout.

Then repeat with the answers your change affects. Two are worth covering every time:
`include_taxpert_workspace=no`, which is the combination most easily broken, and
`include_all_screens=yes` with `include_taxpert_workspace=no`, where Browse All still lists every
screen but arrives with only the theme's styling on it. The hook prints a note about the second.

## Gotchas

- **`hooks/post_gen_project.py` is itself rendered as a Jinja template before it runs.** Nothing in
  it may contain a Jinja delimiter, comments included. That is why the answers arrive as literals
  at the top of the file.
- **A new build flag must not be a prefix of an existing one.** `strip_flag` is a bare string
  replace, so a `--scenario` alongside `--scenarioMode` would leave `Mode` behind in every
  `sbt run` line.
- **`strip_flag` has to reach both the `Makefile` and `docker-compose.override.yml`.** They are the
  same dev server started two ways. A flag left in only one of them means the application behaves
  differently depending on whether it was started natively or in a container.
- **Removing a feature means removing everything that pointed at it.** A menu entry whose page is
  no longer generated is a 404. A compose bind mount or build context aimed at an absent sibling
  fails `docker compose up` outright.
- **The hook writes nothing outside the project it generates**, with one deliberate exception. It
  moves the application up one level if it was created inside the template by mistake, and that
  check requires the parent to hold both a `cookiecutter.json` and a `hooks/` directory, so an
  explicit `--output-dir` elsewhere is never second-guessed.
- **Both RELAX NG schemas belong to the generated application.** They are copied from
  form-builder's seeds, and the application owns them from that point on, because an application
  that registers a custom node type has to widen its own grammar. Keep `make validate-xml` running
  against them. In the codebase this template came from, the flow half of that target was declared
  and never run, and the schema drifted years out of agreement with the flow it described.
- **`locales/flow_*.yaml` in a generated application is generated.** Authored text lives in the
  flow XML.
- **`make diff-out` needs a commit to compare against.** The hook stages everything and commits
  nothing, so there is no `main` until you make the first commit.
- **Neither Scala library is published to a remote registry.** Both resolve from `~/.ivy2/local`,
  which is why the generated `build.sbt` carries no `resolvers +=` line and no credentials.
- **Editing form-builder or fact-graph does not reach a running container.** Both are resolved from
  the image's own Ivy cache rather than a bind mount, so `make rebuild` is what picks up a change.
