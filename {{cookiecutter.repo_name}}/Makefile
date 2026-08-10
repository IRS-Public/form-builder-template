PORT ?= {{ cookiecutter.dev_port }}
DEBUGGER_PORT ?= 5005
RESOURCES_DIR := ./src/main/resources/{{ cookiecutter.app_id }}
OUTPUT_DIR := ./out
HTML_VALIDATE_TARGET := ../../../../out/**/*.html

FLOW_DIR := $(RESOURCES_DIR)/flow
FLOW_CONFIG := $(FLOW_DIR)/FlowConfig.rng

FACTS_DIR := $(RESOURCES_DIR)/facts
FACTS_CONFIG := $(FACTS_DIR)/FactDictionaryModule.rng

FG_SOURCE_DIR := ../fact-graph/js/target/scala-3.3.6/factgraph-fastopt
FG_TARGET_DIR := $(RESOURCES_DIR)/website-static/vendor/fact-graph

SHARED_UI_SRC := node_modules/taxpert/src
SHARED_UI_TARGET := $(RESOURCES_DIR)/website-static/vendor/taxpert

USWDS_VERSION := 3.13.0
USWDS_SRC := $(RESOURCES_DIR)/node_modules/@uswds/uswds/dist
USWDS_TARGET := $(RESOURCES_DIR)/website-static/vendor/uswds-$(USWDS_VERSION)

help: ## Print the help documentation
	@grep -E '^[/a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## One-time setup: publish the sibling libraries and vendor their assets
	@# This app depends on three checkouts that sit beside it — fact-graph and formative through
	@# the local Ivy cache, taxpert through a file: npm dependency. Nothing is published to a
	@# remote yet, so a fresh clone has to build them once before it can build itself.
	$(MAKE) -C ../fact-graph publish
	cd ../formative && sbt publishLocal
	npm install
	npm --prefix $(RESOURCES_DIR) install
	$(MAKE) copy-fg copy-shared-ui copy-uswds

.PHONY: dev
dev: copy-fg copy-shared-ui copy-uswds ## Build and run the development server, watching for changes
	sbt -Dsmol.port=$(PORT) '~run --serve --auditMode --allScreens --scenarioMode'

.PHONY: dev-one-question
dev-one-question: copy-fg copy-shared-ui copy-uswds ## Same as `dev`, one question per screen
	sbt -Dsmol.port=$(PORT) '~run --serve --auditMode --allScreens --singleQuestionPerScreen --scenarioMode'

.PHONY: dev-author
dev-author: copy-fg copy-shared-ui copy-uswds ## Same as `dev`, with Author Mode editing enabled on port 3004
	sbt -Dsmol.port=$(PORT) -Dsmol.author.port=3004 '~run --serve --auditMode --allScreens --scenarioMode --authorMode'

.PHONY: debug
debug: copy-fg copy-shared-ui copy-uswds ## Same as `dev`, but also opens a port to attach a debugger
	sbt -Dsmol.port=$(PORT) -jvm-debug $(DEBUGGER_PORT) '~run --serve --auditMode --allScreens --scenarioMode'

.PHONY: site
site: copy-fg copy-shared-ui copy-uswds ## Build the site for production, into ./out
	@# No flags: the workspace, the all-screens page and scenario mode are developer surfaces,
	@# baked in at build time. A production build is the flow and nothing else.
	sbt run

.PHONY: copy-fg
copy-fg: ## Copy the compiled Fact Graph bundle from the sibling repository
	@# Skipped rather than fatal when the sibling has not been built: this runs ahead of every
	@# dev server and production build, and someone working on templates or locales does not
	@# need an sbt-built fact-graph sitting next door.
	@if [ -f $(FG_SOURCE_DIR)/main.mjs ]; then \
		cp $(FG_SOURCE_DIR)/main.mjs $(FG_TARGET_DIR)/factgraph-{{ cookiecutter.factgraph_version|replace('-SNAPSHOT', '') }}.js; \
		cp $(FG_SOURCE_DIR)/main.mjs.map $(FG_TARGET_DIR); \
		echo "==> copied the fact-graph bundle from $(FG_SOURCE_DIR)"; \
	else \
		echo "==> no build at $(FG_SOURCE_DIR); keeping the vendored fact-graph bundle"; \
		echo "    (run 'cd ../fact-graph && sbt fastOptJS' to refresh it)"; \
	fi

.PHONY: copy-shared-ui
copy-shared-ui: ## Regenerate the vendored taxpert mirror from node_modules
	# The vendored copy is a generated mirror of taxpert's src/ bundle dirs, each one broken down
	# into js/styles/templates (the same shape as vendor/uswds-3.13.0). This app has no bundler, so
	# templates and stylesheets load those files as plain <script type="module"> and @import.
	#
	# Wipe first so a renamed or removed source file never lingers as a stale vendored copy, and
	# copy whatever bundles src/ contains rather than naming them — adding a bundle to taxpert
	# should not need an edit here to reach the browser.
	rm -rf $(SHARED_UI_TARGET)
	mkdir -p $(SHARED_UI_TARGET)
	cp -R $(SHARED_UI_SRC)/. $(SHARED_UI_TARGET)/

.PHONY: copy-uswds
copy-uswds: ## Regenerate the vendored USWDS mirror from node_modules
	# The design system, vendored the same way as everything else this app does not author: a
	# generated, gitignored mirror with exactly one writer. Taking it from npm rather than
	# committing 16MB of it means the version lives in package.json, where dependabot can see it.
	#
	# The distributed layout is remapped rather than copied verbatim: USWDS ships CSS under
	# `dist/css/`, and every Formative page asks for `vendor/uswds-$(USWDS_VERSION)/styles/`.
	@if [ ! -d $(USWDS_SRC) ]; then \
		echo "==> $(USWDS_SRC) not found — run 'make ci-setup' (or 'make bootstrap') first"; exit 1; \
	fi
	rm -rf $(USWDS_TARGET)
	mkdir -p $(USWDS_TARGET)/styles $(USWDS_TARGET)/js
	cp $(USWDS_SRC)/css/uswds.min.css $(USWDS_TARGET)/styles/
	cp $(USWDS_SRC)/js/uswds.min.js $(USWDS_SRC)/js/uswds-init.min.js $(USWDS_TARGET)/js/
	cp -R $(USWDS_SRC)/fonts $(USWDS_SRC)/img $(USWDS_TARGET)/
	@echo "==> vendored USWDS $(USWDS_VERSION)"

.PHONY: check-shared-ui
check-shared-ui: ## Fail if the vendored mirror has drifted from taxpert's source
	@# The mirror is generated and gitignored, so a build that skipped copy-shared-ui — or a
	@# hand-edit of the mirror, which the next build silently overwrites — shows up here as a
	@# diff rather than as stale UI in the browser.
	@diff -r -x .DS_Store $(SHARED_UI_SRC) $(SHARED_UI_TARGET) \
		|| { echo "==> vendored shared UI is out of date — run 'make copy-shared-ui'"; exit 1; }
	@echo "==> vendored shared UI matches taxpert"

.PHONY: test
test: ## Run the test suite
	@# -oC prints only the tests that fail
	sbt -info 'set Test / testOptions += Tests.Argument(TestFrameworks.ScalaTest, "-oC")' test scalafmtCheckAll

.PHONY: test-watch
test-watch: ## Run and watch the tests
	sbt -info 'set Test / testOptions += Tests.Argument(TestFrameworks.ScalaTest, "-oC")' '~test'

.PHONY: format
format: ## Format the Scala, XML and JavaScript
	@# Only the fact configs are formatted automatically — the flow XML carries authored prose
	@# whose whitespace is meaningful once it reaches the page.
	find $(FACTS_DIR) -name '*.xml' | xargs -I {} xmllint --format {} --output {}
	sbt scalafmtAll
	npm --prefix $(RESOURCES_DIR) run format

.PHONY: clean
clean: ## Delete the build artifacts
	rm -rf ./target/
	find ./project -name target | xargs rm -rf
	rm -rf $(OUTPUT_DIR)

.PHONY: ci-setup
ci-setup: ## Install the validation and linting tools
	npm install
	npm --prefix $(RESOURCES_DIR) install

.PHONY: ci
ci: ## Run the CI checks locally
	$(MAKE) site
	$(MAKE) check-shared-ui
	$(MAKE) validate-xml
	$(MAKE) validate-html
	$(MAKE) validate-js
	$(MAKE) validate-scala

.PHONY: validate-xml
validate-xml: ## Validate the .xml files against their RELAX NG schemas
	find $(FACTS_DIR) -name '*.xml' | xargs xmllint --quiet --relaxng $(FACTS_CONFIG) > /dev/null
	@# Both halves. In the two apps this template was drawn from, FLOW_DIR and FLOW_CONFIG were
	@# declared and then never run, and FlowConfig.rng quietly drifted away from the flow it
	@# describes. Widen the schema when you widen the flow.
	find $(FLOW_DIR) -name '*.xml' | xargs xmllint --quiet --relaxng $(FLOW_CONFIG) > /dev/null

.PHONY: validate-html
validate-html: ## Validate the generated .html files
	npm --prefix $(RESOURCES_DIR) run html-validate -- "$(HTML_VALIDATE_TARGET)"

.PHONY: validate-js
validate-js: ## Run the JavaScript linter
	npm --prefix $(RESOURCES_DIR) run lint

.PHONY: validate-scala
validate-scala: ## Check the Scala formatting
	sbt scalafmtCheckAll

.PHONY: diff-out
diff-out: ## Diff this branch's generated site against `main`
	./scripts/diff-out.sh
