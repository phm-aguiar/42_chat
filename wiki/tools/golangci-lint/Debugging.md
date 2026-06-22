---
title: "Debugging"
source: "https://golangci.github.io/legacy-v1-doc/contributing/debug/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, debugging]
---
You can see a verbose output of linter by using `-v` option.

```
golangci-lint run -v
```

If you would like to see more detailed logs you can use the environment variable `GL_DEBUG`. Its value is a list of debug tags.

The existing debug tags are documented in the following file: [https://github.com/golangci/golangci-lint/blob/HEAD/pkg/logutils/logutils.go](https://github.com/golangci/golangci-lint/blob/HEAD/pkg/logutils/logutils.go)

For example:

```
GL_DEBUG="loader,gocritic" golangci-lint run
```
```
GL_DEBUG="loader,env" golangci-lint run
```
[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/contributing/debug.mdx)