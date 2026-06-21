---
title: "Upgrading Cucumber"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/Upgrading  Cucumber.md"
created: "2026-06-21"
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
We add new features to Cucumber periodically. This means you may want to upgrade to a newer version to take advantage of these new features, as well as any bug fixes.

## Versioning

Cucumber follows the [SemVer](http://semver.org/) specification for release numbers. Essentially, this means that:

- If only the right-hand (patch) number in the release changes, you don't need to worry.
- If the middle number (minor) number in the release changes, you don't need to worry.
- If the left-hand (major) number changes, you can expect that things might break.

## Release

You can read the history file to learn about the changes in every release, and see advice on upgrading across major versions where applicable:

- Cucumber-JVM
- Cucumber-JVM-Scala
- Cucumber-JS
- Cucumber-Ruby
	- Changelog [https://github.com/cucumber/cucumber-ruby/blob/main/CHANGELOG.md](https://github.com/cucumber/cucumber-ruby/blob/main/CHANGELOG.md)