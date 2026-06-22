---
title: "Website architecture"
source: "https://golangci.github.io/legacy-v1-doc/contributing/website/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, website]
---
## Table of Contents

## Technology

We use [Gatsby](https://www.gatsbyjs.org/) for static site generation because sites built with it are very fast.

This framework uses React and JavaScript/TypeScript.

## Source Code

The website lives in `docs/` directory of [golangci-lint repository](https://github.com/golangci/golangci-lint).

## Theme

Initially the site is based on [@rocketseat](https://github.com/jpedroschmitz/rocketdocs) theme. Later we've merged its code into `src/@rocketseat` because we needed too much changes and [gatsby shadowing](https://www.gatsbyjs.org/docs/themes/shadowing/) doesn't allow shadowing `gatsby-node.js` or `gatsby-config.js`.

Left menu is configured in `src/config/sidebar.yml`.

## Articles

Articles are located in `src/docs/` in `*.mdx` files. [MDX](https://mdxjs.com/getting-started/gatsby) is Markdown allowing to use `React` components.

## Templating

We use templates like `{.SomeField}` inside our `mdx` files. There templates are expanded by running `make website_expand_templates` in the root of the repository. It runs script `scripts/website/expand_templates/` that rewrites `mdx` files with replaced templates.

## Hosting

We use GitHub Pages as static website hosting and CD.

GitHub deploys the website to production after merging anything to a `master` branch.

## Local Testing

Install Node.js (v20 or newer).

Run:

```
npm install --legacy-peer-deps
npm run start
```

And navigate to `http://localhost:8000` after successful Gatsby build. There is no need to restart Gatsby server almost for all changes: it supports hot reload. Also, there is no need to refresh a webpage: hot reload updates changed content on the open page.

## Website Build

To do it run:

```
go run ./scripts/website/expand_templates/
```
[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/contributing/website.mdx)