---
title: Go JWT API Reference (v5.3.1)
category: references
tags: [go, jwt, api-reference, library]
sources: [_raw/golang-jwt-v5.3.1-API-Reference.md, _raw/golang-jwt-v5.3.1-Examples.md]
summary: Referência completa da API golang-jwt v5: Token, Claims, Parser, Validator, SigningMethod, ParserOptions, erros, e sub-pacotes request/test.
provenance:
  extracted: 0.85
  inferred: 0.12
  ambiguous: 0.03
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: 2026-06-16
tier: supporting
created: 2026-06-16T00:00:00Z
updated: 2026-06-16T00:00:00Z
---

# Go JWT API Reference (v5.3.1)

> Package: `github.com/golang-jwt/jwt/v5`

## Token (struct principal)

```go
type Token struct {
    Raw       string
    Method    SigningMethod
    Header    map[string]any
    Claims    Claims
    Signature []byte
    Valid     bool
}
```

**Construtores:**

```go
func New(method SigningMethod, opts ...TokenOption) *Token
func NewWithClaims(method SigningMethod, claims Claims, opts ...TokenOption) *Token
```

**Métodos:**

```go
func (t *Token) SignedString(key any) (string, error)   // Assina e retorna string JWT completa
func (t *Token) SigningString() (string, error)           // String a ser assinada (custo alto)
func (*Token) EncodeSegment(seg []byte) string           // Base64url encoding sem padding
```

## Claims (interface)

```go
type Claims interface {
    GetExpirationTime() (*NumericDate, error)
    GetIssuedAt() (*NumericDate, error)
    GetNotBefore() (*NumericDate, error)
    GetIssuer() (string, error)
    GetSubject() (string, error)
    GetAudience() (ClaimStrings, error)
}
```

A interface representa getters para claims com semântica RFC 7519. Validação é desacoplada do storage.

### RegisteredClaims (struct)

```go
type RegisteredClaims struct {
    Issuer    string        `json:"iss,omitempty"`
    Subject   string        `json:"sub,omitempty"`
    Audience  ClaimStrings  `json:"aud,omitempty"`
    ExpiresAt *NumericDate  `json:"exp,omitempty"`
    NotBefore *NumericDate  `json:"nbf,omitempty"`
    IssuedAt  *NumericDate  `json:"iat,omitempty"`
    ID        string        `json:"jti,omitempty"`
}
```

Use standalone ou **embeddado** em custom claims. Substitui `StandardClaims` (removido na v5).

### MapClaims

```go
type MapClaims map[string]any
```

Default quando nenhum tipo de claims é fornecido.

### ClaimStrings

```go
type ClaimStrings []string
```

Serializa/deserializa `aud` como string única ou array JSON. Controlado por `MarshalSingleStringAsArray` (default: `true`).

### NumericDate

```go
type NumericDate struct { time.Time }
func NewNumericDate(t time.Time) *NumericDate
```

Data numérica JSON conforme RFC 7519 §2. Trunca para `TimePrecision` (default: `time.Second`).

### ClaimsValidator (interface)

```go
type ClaimsValidator interface {
    Claims
    Validate() error
}
```

Validação custom que roda **em adição** à validação padrão — não pode desabilitá-la.

```go
var _ jwt.ClaimsValidator = (*MyCustomClaims)(nil) // compile-time check
```

## Keyfunc

```go
type Keyfunc func(*Token) (any, error)
```

Callback que recebe o token parseado (não-verificado) e retorna a chave. Use `kid` do header para selecionar a chave. Pode retornar `VerificationKeySet` com múltiplas chaves.

```go
type VerificationKey interface {
    crypto.PublicKey | []uint8
}
type VerificationKeySet struct { Keys []VerificationKey }
```

## Parser

```go
type Parser struct { /* campos não-exportados */ }
func NewParser(options ...ParserOption) *Parser
```

**Métodos:**

```go
func (p *Parser) Parse(tokenString string, keyFunc Keyfunc) (*Token, error)
func (p *Parser) ParseWithClaims(tokenString string, claims Claims, keyFunc Keyfunc) (*Token, error)
func (p *Parser) ParseUnverified(tokenString string, claims Claims) (*Token, []string, error)  // ⚠️ sem verificação
func (p *Parser) DecodeSegment(seg string) ([]byte, error)
```

### Convenience Functions

```go
func Parse(tokenString string, keyFunc Keyfunc, options ...ParserOption) (*Token, error)
func ParseWithClaims(tokenString string, claims Claims, keyFunc Keyfunc, options ...ParserOption) (*Token, error)
```

### ParserOption (tabela completa)

| Option | Assinatura | Descrição |
|--------|-----------|-----------|
| `WithValidMethods` | `func(methods []string)` | **Whitelist de `alg`.** Essencial contra algorithm confusion. |
| `WithLeeway` | `func(leeway time.Duration)` | Tolerância de clock skew para `exp`, `nbf`, `iat` |
| `WithIssuer` | `func(iss string)` | Exige `iss` específico |
| `WithSubject` | `func(sub string)` | Exige `sub` específico |
| `WithAudience` | `func(aud ...string)` | Exige **qualquer um** dos `aud` |
| `WithAllAudiences` | `func(aud ...string)` | Exige **todos** os `aud` (dedup interno) |
| `WithExpirationRequired` | `func()` | Torna `exp` obrigatório |
| `WithNotBeforeRequired` | `func()` | Torna `nbf` obrigatório |
| `WithIssuedAt` | `func()` | Habilita verificação de `iat` (off por padrão) |
| `WithTimeFunc` | `func(f func() time.Time)` | Time function custom (útil em testes) |
| `WithJSONNumber` | `func()` | Configura JSON parser com `UseNumber` |
| `WithStrictDecoding` | `func()` | Base64 strict (RFC 4648 §3.5) |
| `WithPaddingAllowed` | `func()` | Permite padding base64 (não-standard) |
| `WithoutClaimsValidation` | `func()` | ⚠️ Desabilita validação de claims |

## Validator

```go
type Validator struct { /* campos não-exportados */ }
func NewValidator(opts ...ParserOption) *Validator
func (v *Validator) Validate(claims Claims) error
```

Core da validação. Usado automaticamente pelo `Parser`. **Não verifica assinatura** — apenas validade dos claims.

Uso standalone:

```go
v := jwt.NewValidator(jwt.WithLeeway(5 * time.Second))
err := v.Validate(claims)
```

## SigningMethod (interface)

```go
type SigningMethod interface {
    Verify(signingString string, sig []byte, key any) error
    Sign(signingString string, key any) ([]byte, error)
    Alg() string
}
func GetSigningMethod(alg string) SigningMethod
func RegisterSigningMethod(alg string, f func() SigningMethod)
func GetAlgorithms() (algs []string)
```

### Tabela de Key Types por Algoritmo

| Algoritmo | `alg` | Sign Key | Verify Key |
|-----------|-------|----------|------------|
| HMAC-SHA256 | `HS256` | `[]byte` | `[]byte` |
| HMAC-SHA384 | `HS384` | `[]byte` | `[]byte` |
| HMAC-SHA512 | `HS512` | `[]byte` | `[]byte` |
| RSA-SHA256 | `RS256` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| RSA-SHA384 | `RS384` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| RSA-SHA512 | `RS512` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| RSA-PSS-SHA256 | `PS256` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| RSA-PSS-SHA384 | `PS384` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| RSA-PSS-SHA512 | `PS512` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| ECDSA-SHA256 | `ES256` | `*ecdsa.PrivateKey` | `*ecdsa.PublicKey` |
| ECDSA-SHA384 | `ES384` | `*ecdsa.PrivateKey` | `*ecdsa.PublicKey` |
| ECDSA-SHA512 | `ES512` | `*ecdsa.PrivateKey` | `*ecdsa.PublicKey` |
| Ed25519 | `EdDSA` | `ed25519.PrivateKey` | `ed25519.PublicKey` |

> ⚠️ **HMAC:** Gere chaves com `crypto/rand`, nunca strings ASCII.

### Signing Methods Predefinidos

```go
var SigningMethodHS256 *SigningMethodHMAC
var SigningMethodHS384 *SigningMethodHMAC
var SigningMethodHS512 *SigningMethodHMAC
var SigningMethodRS256 *SigningMethodRSA
var SigningMethodRS384 *SigningMethodRSA
var SigningMethodRS512 *SigningMethodRSA
var SigningMethodPS256 *SigningMethodRSAPSS   // PSS tem Options e VerifyOptions extras
var SigningMethodPS384 *SigningMethodRSAPSS
var SigningMethodPS512 *SigningMethodRSAPSS
var SigningMethodES256 *SigningMethodECDSA
var SigningMethodES384 *SigningMethodECDSA
var SigningMethodES512 *SigningMethodECDSA
var SigningMethodEdDSA *SigningMethodEd25519
```

### Custom Signing Method

```go
func init() {
    jwt.RegisterSigningMethod("CUSTOM", func() jwt.SigningMethod {
        return &MyCustomSigningMethod{}
    })
}
```

## PEM Parsing Functions

```go
func ParseRSAPrivateKeyFromPEM(key []byte) (*rsa.PrivateKey, error)
func ParseRSAPublicKeyFromPEM(key []byte) (*rsa.PublicKey, error)
func ParseECPrivateKeyFromPEM(key []byte) (*ecdsa.PrivateKey, error)
func ParseECPublicKeyFromPEM(key []byte) (*ecdsa.PublicKey, error)
func ParseEdPrivateKeyFromPEM(key []byte) (crypto.PrivateKey, error)
func ParseEdPublicKeyFromPEM(key []byte) (crypto.PublicKey, error)
// Deprecated: usa x509.DecryptPEMBlock (RFC 1423, inseguro)
func ParseRSAPrivateKeyFromPEMWithPassword(key []byte, password string) (*rsa.PrivateKey, error)
```

## Error Variables

**Erros gerais:**

```go
ErrInvalidKey, ErrInvalidKeyType, ErrHashUnavailable
ErrTokenMalformed, ErrTokenUnverifiable, ErrTokenSignatureInvalid
ErrTokenRequiredClaimMissing, ErrTokenInvalidAudience
ErrTokenExpired, ErrTokenUsedBeforeIssued, ErrTokenInvalidIssuer
ErrTokenInvalidSubject, ErrTokenNotValidYet, ErrTokenInvalidId
ErrTokenInvalidClaims, ErrInvalidType
```

**RSA:** `ErrKeyMustBePEMEncoded`, `ErrNotRSAPrivateKey`, `ErrNotRSAPublicKey`

**ECDSA:** `ErrECDSAVerification`, `ErrNotECPublicKey`, `ErrNotECPrivateKey`

**Ed25519:** `ErrEd25519Verification`, `ErrNotEdPrivateKey`, `ErrNotEdPublicKey`

**HMAC:** `ErrSignatureInvalid`

Uso idiomático — `errors.Is`:

```go
switch {
case errors.Is(err, jwt.ErrTokenExpired):
    fmt.Println("Token expired")
case errors.Is(err, jwt.ErrTokenSignatureInvalid):
    fmt.Println("Invalid signature")
}
```

## Global Settings

```go
var MarshalSingleStringAsArray = true  // aud: sempre array no JSON
var TimePrecision = time.Second         // Precisão de timestamps
const UnsafeAllowNoneSignatureType ...  // Habilita alg=none (não use)
```

## Sub-package: `request`

Import: `github.com/golang-jwt/jwt/v5/request`

```go
func ParseFromRequest(req *http.Request, extractor Extractor, keyFunc jwt.Keyfunc, options ...ParseFromRequestOption) (*jwt.Token, error)
```

**Extractors:**

| Extractor | Tipo | Descrição |
|-----------|------|-----------|
| `AuthorizationHeaderExtractor` | `*PostExtractionFilter` | `Authorization: Bearer ***` |
| `OAuth2Extractor` | `*MultiExtractor` | Header + `access_token` query param |
| `HeaderExtractor` | `[]string` | Headers custom (ex: `X-Auth-Token`) |
| `ArgumentExtractor` | `[]string` | POST form ou GET query |
| `MultiExtractor` | `[]Extractor` | Tenta em ordem até sucesso |
| `BearerExtractor` | `struct{}` | `Authorization`, espera `Bearer XX` |
| `PostExtractionFilter` | struct | Pós-processa valor extraído |

**Errors:** `ErrNoTokenInRequest`

## Sub-package: `test`

Import: `github.com/golang-jwt/jwt/v5/test`

```go
func LoadRSAPrivateKeyFromDisk(location string) *rsa.PrivateKey
func LoadRSAPublicKeyFromDisk(location string) *rsa.PublicKey
func LoadECPrivateKeyFromDisk(location string) crypto.PrivateKey
func LoadECPublicKeyFromDisk(location string) crypto.PublicKey
func MakeSampleToken(c jwt.Claims, method jwt.SigningMethod, key any) string
```

## Ver Também

- [[references/go-jwt|Go JWT Overview]] — Guia de uso com exemplos e migration v4→v5
- [[references/go-error-handling|Go Error Handling]] — `errors.Is` para erros sentinela do JWT
- [[references/42-api-specification|42 API Specification]] — OAuth2 Bearer tokens
