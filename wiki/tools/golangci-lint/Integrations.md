---
title: "Integrations"
source: "https://golangci.github.io/legacy-v1-doc/welcome/integrations/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, integrations]
---
## Table of Contents

## Editor Integration

### Go for Visual Studio Code.

Recommended settings for VS Code are:

```
"go.lintTool": "golangci-lint",
"go.lintFlags": [
  "--fast"
]
```

Using it in an editor without `--fast` can freeze your editor. Golangci-lint automatically discovers `.golangci.yml` config for edited file: you don't need to configure it in VS Code settings.

### Sublime Text

There is a [plugin](https://github.com/SublimeLinter/SublimeLinter-golangcilint) for SublimeLinter.

### GoLand

How to configure:

- Install [plugin](https://plugins.jetbrains.com/plugin/12496-go-linter).
- Add [File Watcher](https://www.jetbrains.com/help/go/settings-tools-file-watchers.html) using existing `golangci-lint` template.
- If your version of GoLand does not have the `golangci-lint` [File Watcher](https://www.jetbrains.com/help/go/settings-tools-file-watchers.html) template you can configure your own and use arguments `run --disable=typecheck $FileDir$`.

### GNU Emacs

There are available plugins:

- [Spacemacs](https://github.com/syl20bnr/spacemacs/blob/develop/layers/+lang/go/README.org#linting)
- [Flycheck checker](https://github.com/weijiangan/flycheck-golangci-lint)

### Vim

The following plugins support `golangci-lint`:

- [vim-go](https://github.com/fatih/vim-go)
- [ALE](https://github.com/w0rp/ale)

### LSP Server

- [golangci-lint-langserver](https://github.com/nametake/golangci-lint-langserver) (NeoVim, Vim, Emacs,...)

## Shell Completion

`golangci-lint` can generate Bash, fish, PowerShell, and Zsh completion files.

See the instructions on `golangci-lint completion <YOUR_SHELL> --help` (replace `<YOUR_SHELL>` with your favorite one).

Bash & macOS

There are two versions of `bash-completion`, v1 and v2. V1 is for Bash 3.2 (which is the default on macOS), and v2 is for Bash 4.1+.

The `golangci-lint` completion script doesn’t work correctly with bash-completion v1 and Bash 3.2. It requires bash-completion v2 and Bash 4.1+.

Thus, to be able to correctly use `golangci-lint` completion on macOS, you have to install and use Bash 4.1+ ([instructions](https://itnext.io/upgrading-bash-on-macos-7138bd1066ba)).

The following instructions assume that you use Bash 4.1+ (that is, any Bash version of 4.1 or newer).

Install `bash-completion v2`:

```
brew install bash-completion@2
echo 'export BASH_COMPLETION_COMPAT_DIR="/usr/local/etc/bash_completion.d"' >>~/.bashrc
echo '[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"' >>~/.bashrc
exec bash # reload and replace (if it was updated) shell
type _init_completion && echo "completion is OK" # verify that bash-completion v2 is correctly installed
```

Add `golangci-lint` bash completion:

```
echo 'source <(golangci-lint completion bash)' >>~/.bashrc
source ~/.bashrc
```

## CI Integration

Check out our [documentation for CI integrations](https://golangci.github.io/legacy-v1-doc/welcome/install#ci-installation).

[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/welcome/integrations.mdx)