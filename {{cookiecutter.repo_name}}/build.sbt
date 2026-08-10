ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / scalaVersion := "3.7.2"

// Set default class for "run"
Compile / mainClass := Some("{{ cookiecutter.scala_package }}.main")

// Prevent additional compilation when the generated locale file is created. `regenerate` writes
// flow_en.yaml back into src/main/resources on every run, and without this an `sbt ~run` loop
// re-triggers itself forever.
Compile / unmanagedResources / excludeFilter := (Compile / unmanagedResources / excludeFilter).value || "flow_en.yaml"

scalafmtConfig := file(".scalafmt.conf")

lazy val root = (project in file("."))
  .settings(
    name := "{{ cookiecutter.repo_name }}",

    // The scaffold: parser, generators, Thymeleaf engine, node templates, chrome locales.
    // Everything it is built on — thymeleaf, jsoup, circe, os-lib, scala-xml, factgraph — arrives
    // transitively, so this is the only line that ever needs to name a version.
    libraryDependencies += "gov.irs" %% "formative" % "{{ cookiecutter.formative_version }}",

    libraryDependencies += "org.scalatest" %% "scalatest" % "3.2.19" % Test,
    )
