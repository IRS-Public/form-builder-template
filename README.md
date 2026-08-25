# Form Builder Template

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that generates a new, multi-language
questionnaire application built on [Fact Graph](https://github.com/IRS-Public/form-builder) and
[Form Builder](https://github.com/IRS-Public/form-builder) Scala libraries. Form Builder Template deliberately generates a lightweight application. It assumes you want to model
complex business logic with the Fact Graph, including but not limited to a tax code, without building your own rules engine,
presentation layer, navigation, internationalization, or styling components to meet Section 508 compliance. Applications generated with this template include the flow parser, site generators, Thymeleaf engine, node templates, locales,
browser theme, flow runtime and (optionally) a web-GUI to update presentation and business logic, all out of the box.

See the [onboarding guide](docs/ONBOARDING.md) to get started with a new Form Builder application. See [Form Builder 
Examples](https://github.com/IRS-Public/form-builder-examples) for example applications built using this template. To understand the difference between Taxpert, Form Builder and the Fact Graph, see [this doc](https://github.com/IRS-Public/taxpert/blob/main/docs/adr/taxpert-form-builder-fact-graph.md).

## Where this fits

| Component | What it is |
|---|---|
| [`fact-graph`](https://github.com/IRS-Public/fact-graph) | `gov.irs::factgraph`, the rules engine. Cross-compiled: a JVM jar this library builds against, and a Scala.js bundle the browser runs. |
| `form-builder` | `gov.irs::form-builder`, the presentation generator: parsers, the Thymeleaf engine, node templates, locales, RELAX NG schemas, the theme, the flow runtime, and Author Mode. |
| [`taxpert`](https://github.com/IRS-Public/taxpert) | The workspace UI (`taxpert` on npm, in that repo's `packages/ui`): global nav, audit panel, tool panels. Optional, and an application can ship without it. That repo's `packages/fact-explorer` is a React and Vite SPA that visualizes any Form Builder app's flow and facts as a graph, reading the JSON this library emits under `--formBuilderGraph`. |
| [`form-builder-template`](https://github.com/IRS-Public/form-builder-template) | A cookiecutter template that generates a new Form Builder app, with optional extensions like Taxpert. |
| [`form-builder-examples`](https://github.com/IRS-Public/form-builder-examples) | Reference applications built on the libraries above. |

Taxpert and other extensions such as Author Mode, Fact Explorer, and Docker are optional. An
application generated with `include_taxpert_workspace=no` has no dependency on Taxpert at all, and
still gets the theme and the flow runtime, both of which ship inside the form-builder jar.


# Contributing
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
>
> Artificial Intelligence was used in generating portions of this codebase.


# Authorities

Legal foundations for this work include:
- Source Code Harmonization And Reuse in Information Technology Act" of 2024, Public Law 118 - 187
- OMB Memorandum M-16-21, “Federal Source Code Policy: Achieving Efficiency, Transparency, and Innovation through 
Reusable and Open Source Software,” August 8, 2016
- Federal Acquisition Regulation (FAR) Part 27 – Patents, Data, and Copyrights
- Digital Government Strategy: “Digital Government: Building a 21st Century Platform to Better Serve the American 
People,” May 23, 2012
- Federal Information Technology Acquisition Reform Act (FITARA), December 2014 (National Defense Authorization Act 
for Fiscal Year 2015, Title VIII, Subtitle D)
- E-Government Act of 2002, Public Law 107-347
- Clinger-Cohen Act of 1996, Public Law 104-106
