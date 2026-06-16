# golang-jwt v5.3.1 — Migration Guide

> From `MIGRATION_GUIDE.md` at `github.com/golang-jwt/jwt/v5@v5.3.1`

---

## v4.x → v5.0.0

Version v5 contains a major rework of core functionalities: support for several validation options, a re-design of the `Claims` interface, and reworked error handling.

### Import Path

```
// old
"github.com/golang-jwt/jwt/v4"

// new
"github.com/golang-jwt/jwt/v5"
```

For most users, changing the import path *should* suffice, but the public API was intentionally changed and cleaned. Existing programs might need updates.

---

### 1. Parsing and Validation Options

A new `Validator` struct handles claims validation. Several `ParserOption` functions can be appended to `Parse` functions to fine-tune validation.

| Change | Detail |
|--------|--------|
| **New:** `WithLeeway` | Specify clock skew tolerance for time-based claims (`exp`, `nbf`). |
| **Changed:** `iat` not checked by default | `iat` is OPTIONAL and purely informational per RFC 7519. Use `WithIssuedAt` to enable checking. |
| **New:** `WithAudience`, `WithSubject`, `WithIssuer` | Check for expected `aud`, `sub` and `iss` claims. |
| **New:** `WithStrictDecoding`, `WithPaddingAllowed` | Base64 strict encoding and padding parsing. Both disabled by default. |

```go
// v4 — no leeway, no audience/issuer checks
token, err := jwt.Parse(tokenString, keyFunc)

// v5 — with leeway, audience check, and method whitelist
token, err := jwt.Parse(tokenString, keyFunc,
    jwt.WithLeeway(5*time.Second),
    jwt.WithAudience("my-app"),
    jwt.WithValidMethods([]string{"RS256", "HS256"}),
)
```

---

### 2. `Claims` Interface Restructured

#### The Problem (v4)

Previously, the claims interface required `Valid() error`. This caused:
- Duplicate validation code across claim types (struct, map, etc.)
- Not semantically close to what "claims" really are (key/value pairs with meaning)

#### The Solution (v5)

The `Claims` interface now represents a list of **getters** for values with specific semantic meaning:

```go
// v5 Claims interface
type Claims interface {
    GetExpirationTime() (*NumericDate, error)
    GetIssuedAt() (*NumericDate, error)
    GetNotBefore() (*NumericDate, error)
    GetIssuer() (string, error)
    GetSubject() (string, error)
    GetAudience() (ClaimStrings, error)
}
```

Validation logic is completely decoupled from the underlying storage (struct, map, database).

**Migration for `Valid()` calls:**

```go
// v4 — direct call on claims
err := claims.Valid()

// v5 — use standalone validator
v := jwt.NewValidator(jwt.WithLeeway(5*time.Second))
err := v.Validate(myClaims)
```

#### `StandardClaims` Removed

`StandardClaims` (deprecated in v4) is **removed** in v5. Use `RegisteredClaims` instead.

```go
// v4
type MyClaims struct {
    jwt.StandardClaims
    Name string `json:"name"`
}

// v5
type MyClaims struct {
    jwt.RegisteredClaims
    Name string `json:"name"`
}
```

---

### 3. Application-Specific Validation: `ClaimsValidator`

Previously, users could override `Valid()` in custom claims for application-specific logic — but this was dangerous (easy to accidentally disable standard validation).

**v5 solution:** `ClaimsValidator` interface. If your claims implement `Validate() error`, it is executed **in addition to** standard validation. It cannot disable standard validation.

```go
// v4 — dangerous: could accidentally skip standard checks
func (m MyCustomClaims) Valid() error {
    if m.Foo != "bar" {
        return errors.New("must be foobar")
    }
    return nil // Standard validation? Never called!
}

// v5 — safe: runs AFTER standard validation
type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

func (m MyCustomClaims) Validate() error {
    if m.Foo != "bar" {
        return errors.New("must be foobar")
    }
    return nil
}
```

---

### 4. `Token` and `Parser` Changes

#### `DecodeSegment` / `EncodeSegment` Moved

Previously global functions are now methods on `Parser` and `Token`:

```go
// v4 — global functions
jwt.DecodeSegment(seg)
jwt.EncodeSegment(seg)

// v5 — methods
parser.DecodeSegment(seg)
token.EncodeSegment(seg)
```

#### `Token.Signature` Type Changed

```go
// v4
type Token struct {
    Signature string  // base64 encoded
}

// v5
type Token struct {
    Signature []byte  // decoded (consistent with Header and Claims)
}
```

#### Signing Method `Sign`/`Verify` Signatures

Signing methods now operate on decoded `[]byte` instead of base64-encoded `string`:

```go
// v4
type SigningMethod interface {
    Verify(signingString string, signature string, key interface{}) error
    Sign(signingString string, key interface{}) (string, error)
}

// v5
type SigningMethod interface {
    Verify(signingString string, sig []byte, key any) error
    Sign(signingString string, key any) ([]byte, error)
}
```

> Most users won't be affected. Only those directly accessing `Signature` or writing custom signing methods.

---

### Summary of Breaking Changes (v4 → v5)

| What | v4 | v5 |
|------|----|----|
| Import path | `.../v4` | `.../v5` |
| `Claims` interface | `Valid() error` | Getters (`GetExpirationTime()`, etc.) |
| `StandardClaims` | Deprecated | Removed → use `RegisteredClaims` |
| Custom validation | Override `Valid()` | Implement `ClaimsValidator.Validate()` |
| `iat` check | On by default | Off by default → use `WithIssuedAt` |
| `Token.Signature` | `string` (base64) | `[]byte` (decoded) |
| `DecodeSegment`/`EncodeSegment` | Global functions | `Parser`/`Token` methods |
| `SigningMethod.Sign/Verify` | `string` params | `[]byte` params |
| `keyFunc` param type | `interface{}` | `any` |
| `keyFunc` return | `interface{}` | `any` or `VerificationKeySet` |

---

## v3.x → v4.0.0

### Import Path

```
// old
"github.com/dgrijalva/jwt-go"
// or
"github.com/golang-jwt/jwt"

// new
"github.com/golang-jwt/jwt/v4"
```

Replace all occurrences and run:

```sh
go get github.com/golang-jwt/jwt/v4
go mod tidy
```
