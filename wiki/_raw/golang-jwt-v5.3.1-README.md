# golang-jwt v5.3.1 — README

> **Source:** `github.com/golang-jwt/jwt/v5@v5.3.1`
> **Published:** Jan 28, 2026 | **License:** MIT | **Imports:** 20 | **Imported by:** 15,146+
> **Go Reference:** https://pkg.go.dev/github.com/golang-jwt/jwt/v5

## Overview

A Go implementation of [JSON Web Tokens (RFC 7519)](https://datatracker.ietf.org/doc/html/rfc7519).

Starting with v4.0.0 this project added Go module support, maintaining backward compatibility with older `v3.x.y` tags and upstream `github.com/dgrijalva/jwt-go`. Version v5.0.0 introduces major improvements to token validation, but is **not entirely backward compatible**.

> **History:** After the original author suggested migrating the maintenance of `jwt-go`, a dedicated team of open source maintainers decided to clone the existing library into this repository. See [dgrijalva/jwt-go#462](https://github.com/dgrijalva/jwt-go/issues/462).

## Security Notices

- **Go version:** Some older Go versions have a security issue in `crypto/elliptic`. Upgrade to at least Go 1.15. See [dgrijalva/jwt-go#216](https://github.com/dgrijalva/jwt-go/issues/216).
- **Algorithm validation:** Always [validate the `alg` presented is what you expect](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/). This library requires key types to match the expected alg, but you should still verify it in your code.

## Supported Go Versions

Support is aligned with Go's [version release policy](https://golang.org/doc/devel/release#policy): a major version is supported until there are two newer major releases.

## What is a JWT?

JWT.io has [a great introduction](https://jwt.io/introduction).

A JWT is a signed JSON object commonly used for `Bearer` tokens in OAuth 2. A token consists of three parts separated by `.`:

| Part | Content | Description |
|------|---------|-------------|
| 1 | **Header** | Base64url-encoded JSON with signing algorithm (`alg`) and key ID (`kid`) |
| 2 | **Claims** | Base64url-encoded JSON with the actual data (RFC 7519 registered claims + custom claims) |
| 3 | **Signature** | Base64url-encoded cryptographic signature |

## What's in the Box?

- Parsing and verification of JWTs
- Generation and signing of JWTs
- Supported signing algorithms: **HMAC SHA**, **RSA**, **RSA-PSS**, **ECDSA**, **Ed25519**
- Hooks for adding custom signing methods (`SigningMethod` interface + `RegisterSigningMethod`)

## Installation

```sh
go get -u github.com/golang-jwt/jwt/v5
```

```go
import "github.com/golang-jwt/jwt/v5"
```

## Usage

Detailed usage guide: https://golang-jwt.github.io/jwt/usage/create/

Key examples on pkg.go.dev:
- [Parsing and validating a token (HMAC)](https://pkg.go.dev/github.com/golang-jwt/jwt/v5#example-Parse-Hmac)
- [Building and signing a token (HMAC)](https://pkg.go.dev/github.com/golang-jwt/jwt/v5#example-New-Hmac)
- [All examples](https://pkg.go.dev/github.com/golang-jwt/jwt/v5#pkg-examples)

## Compliance

Last reviewed against [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519) (May 2015) with one notable difference:

- To protect against accidental use of [Unsecured JWTs](https://datatracker.ietf.org/doc/html/rfc7519#section-6), tokens using `alg=none` are only accepted if the constant `jwt.UnsafeAllowNoneSignatureType` is provided as the key.

## Extensions

This library publishes all necessary components for adding custom signing methods or key functions. Implement the `SigningMethod` interface and register via `RegisterSigningMethod`, or provide a custom `jwt.Keyfunc`.

Common use case: integrating with 3rd-party signature providers (cloud KMS, HSMs).

| Extension | Purpose | Repository |
|-----------|---------|------------|
| GCP | Google Cloud Platform signing (AppEngine, IAM, Cloud KMS) | https://github.com/someone1/gcp-jwt-go |
| AWS | AWS Key Management Service (KMS) | https://github.com/matelang/jwt-go-aws-kms |
| JWKS | JWKS (RFC 7517) as a `jwt.Keyfunc` | https://github.com/MicahParks/keyfunc |
| TPM | Trusted Platform Module (TPM) | https://github.com/salrashid123/golang-jwt-tpm |

*Disclaimer:* Unless otherwise specified, these integrations are maintained by third parties.

## Project Status & Versioning

- **Production ready.** API is considered stable.
- Uses [Semantic Versioning 2.0.0](http://semver.org).
- Breaking changes listed in `VERSION_HISTORY.md`. See `MIGRATION_GUIDE.md` for updating your code.

## Additional Resources

- Go package docs: https://pkg.go.dev/github.com/golang-jwt/jwt/v5
- Project page: https://golang-jwt.github.io/jwt/
- CLI utility: `cmd/jwt` — useful for debugging and as an example
