---
title: Go JWT (golang-jwt v5)
category: references
tags: [go, jwt, auth, library]
sources: [_raw/golang-jwt-v5.3.1-README.md, _raw/golang-jwt-v5.3.1-Migration.md, _raw/golang-jwt-v5.3.1-Examples.md]
summary: Biblioteca Go para JSON Web Tokens (RFC 7519). Suporta HMAC, RSA, ECDSA, Ed25519. v5 traz Claims refatorado e ParserOptions.
provenance:
  extracted: 0.80
  inferred: 0.15
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: 2026-06-16
tier: supporting
created: 2026-06-16T00:00:00Z
updated: 2026-06-16T00:00:00Z
---

# Go JWT (golang-jwt v5)

> Biblioteca Go para JSON Web Tokens (RFC 7519). Sucessora do `dgrijalva/jwt-go`, mantida por um time dedicado de OSS. v5.3.1, production-ready, 15k+ importers.

## Overview

Implementação Go de JWT com parsing, validação, geração e assinatura de tokens. Algoritmos: **HMAC-SHA** (HS256/384/512), **RSA** (RS256/384/512), **RSA-PSS** (PS256/384/512), **ECDSA** (ES256/384/512), **Ed25519** (EdDSA).

```sh
go get -u github.com/golang-jwt/jwt/v5
```

```go
import "github.com/golang-jwt/jwt/v5"
```

## Estrutura do Token

Um JWT é composto por 3 partes separadas por `.`:

| Parte | Conteúdo | Descrição |
|-------|----------|-----------|
| Header | JSON Base64url | `alg` (algoritmo), `kid` (key ID) |
| Claims | JSON Base64url | Dados (RFC 7519 registered + custom claims) |
| Signature | Bytes Base64url | Assinatura criptográfica |

## Quick Examples

### Criar e assinar token (HMAC)

```go
token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
    "foo": "bar",
    "nbf": time.Date(2015, 10, 10, 12, 0, 0, 0, time.UTC).Unix(),
})
tokenString, err := token.SignedString([]byte("AllYourBase"))
```

### Parse e validar token (HMAC)

```go
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (any, error) {
    return []byte("AllYourBase"), nil
}, jwt.WithValidMethods([]string{jwt.SigningMethodHS256.Alg()}))

if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
    fmt.Println(claims["foo"])
}
```

### Custom claims com RegisteredClaims

```go
type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

claims := MyCustomClaims{
    Foo: "bar",
    RegisteredClaims: jwt.RegisteredClaims{
        ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
        Issuer:    "test",
    },
}
token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
ss, err := token.SignedString(mySigningKey)
```

### Extrair JWT de HTTP request

```go
import "github.com/golang-jwt/jwt/v5/request"

token, err := request.ParseFromRequest(r,
    request.AuthorizationHeaderExtractor,
    func(token *jwt.Token) (any, error) {
        return []byte("AllYourBase"), nil
    },
    jwt.WithValidMethods([]string{"HS256"}),
)
```

Extractors alternativos: `request.OAuth2Extractor`, `request.HeaderExtractor{"X-Auth-Token"}`, `request.ArgumentExtractor{"token"}`, `&request.MultiExtractor{...}`.

## Migration v4 → v5 (Breaking Changes)

v5 é **não backward-compatible**. Principais mudanças:

| O que | v4 | v5 |
|-------|----|----|
| Import path | `.../v4` | `.../v5` |
| `Claims` interface | `Valid() error` | Getters (`GetExpirationTime()`, `GetIssuer()`, etc.) |
| `StandardClaims` | Deprecated | Removido → usar `RegisteredClaims` |
| Validação custom | Override `Valid()` | Implementar `ClaimsValidator.Validate()` (roda **após** validação padrão) |
| `iat` check | On por padrão | Off → usar `WithIssuedAt()` |
| `Token.Signature` | `string` (base64) | `[]byte` (decodado) |
| `DecodeSegment`/`EncodeSegment` | Funções globais | Métodos de `Parser`/`Token` |

**Novo fluxo de validação (v5):**

```go
// v4 — chamada direta
err := claims.Valid()

// v5 — validator standalone (sem parser)
v := jwt.NewValidator(jwt.WithLeeway(5*time.Second))
err := v.Validate(myClaims)
```

**Custom validation seguro:**

```go
type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

var _ jwt.ClaimsValidator = (*MyCustomClaims)(nil)

func (m MyCustomClaims) Validate() error {
    if m.Foo != "bar" {
        return errors.New("must be foobar")
    }
    return nil
}
```

## Segurança

- **Sempre valide o `alg`** com `WithValidMethods` para prevenir algorithm confusion attacks. ^[inferred]
- **HMAC keys:** use `crypto/rand`, não strings ASCII. 
- **`alg=none`:** só aceito com `jwt.UnsafeAllowNoneSignatureType` como key (proteção contra unsecured JWTs).
- **Go mínimo:** 1.15+ para evitar issue de segurança em `crypto/elliptic`.

## Extensões

Suporte a KMS e assinatura externa:

| Extensão | Propósito |
|----------|-----------|
| GCP | Google Cloud KMS, AppEngine, IAM |
| AWS | AWS KMS signing |
| JWKS | RFC 7517 JWKS como `jwt.Keyfunc` |
| TPM | Trusted Platform Module |

Implemente `SigningMethod` + `RegisterSigningMethod` para métodos customizados.

## Ver Também

- [[references/go-jwt-api-reference|Go JWT API Reference]] — API completa (tipos, funções, erros, ParserOptions)
- [[references/42-api-specification|42 API Specification]] — OAuth2 e autenticação da API 42
- [[references/go-error-handling|Go Error Handling]] — Padrão `errors.Is` usado nos erros do JWT
