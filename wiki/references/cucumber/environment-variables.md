---
title: "Environment Variables"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/Environment variables.md"
created: "2026-06-21"
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
Cucumber uses [environment variables](https://en.wikipedia.org/wiki/Environment_variable) to enable certain features, such as publishing [Cucumber Reports](https://reports.cucumber.io/).

There are many different ways to define environment variables, depending on your environment. This guide describes how to define the `CUCUMBER_PUBLISH_TOKEN` environment variable with value `some-secret-token`.

For security reasons you should *not* define environment variables containing secrets globally.

For MacOS and Linux users this means you should *not* define them in `~/.bashrc`, `~/.bash_profile`, `~/.zshrc`, `/etc.profile` or similar.

For Windows users this means you should *not* define them via System/Control Panel or `setx.exe`.

## Terminal

If you are using a terminal to run Cucumber, you should define environment variables in the same terminal.

This also applies to terminals embedded in an editor such as Visual Studio Code or IntelliJ IDEA.

### Windows

```shell
setx /M CUCUMBER_PUBLISH_TOKEN "some-secret-token"
```

### Bash / Zsh

```shell
export CUCUMBER_PUBLISH_TOKEN=some-secret-token
```

## Editor / IDE

If you are using an editor or IDE to run Cucumber via a menu or shortcut, you should define environment variables in the editor.

If you are using a terminal embedded in the IDE, see the [Terminal](#terminal) section above.

### IntelliJ IDEA / WebStorm / RubyMine

Click the *Run/Debug Configuration* dropdown in the toolbar:

![Run/Debug Configuration](https://cucumber.io/assets/images/run-debug-configuration-2f61f825bf9a8d3b9b56c3699125dbd4.png)

Click on the *Environment Variables* field.

![Environment Variabled Field](https://cucumber.io/assets/images/environment-variables-field-269a504e7593a3a1e32abadead65017c.png)

Enter the environment variable and its value into the dialog.

![Run/Debug Configuration](https://cucumber.io/assets/images/enter-environment-variable-cbc7c27c19106fb89cb2a6ad39f09213.png)

### Other editors

Check the documentation for your editor, or help us improving this documentation by editing this page (link at the bottom of the page).

## Continuous Integration Servers

Every Continuous Integration server has a different mechanism for defining environment variables. Please consult the documentation for your CI server about how to do this.