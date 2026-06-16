# golang-jwt v5.3.1 — API Reference

> **Package:** `github.com/golang-jwt/jwt/v5`
> **Import:** `"github.com/golang-jwt/jwt/v5"`

---

## Constants

```go
const UnsafeAllowNoneSignatureType unsafeNoneMagicConstant = "none signing method allowed"
```

## Variables

### Global Settings

```go
var MarshalSingleStringAsArray = true
```
Modifies the behavior of `ClaimStrings.MarshalJSON`. If `true` (default), always serializes as an array even with one element. If `false`, a single-element slice serializes as a single string.

```go
var TimePrecision = time.Second
```
Sets the precision of times and dates within this library. Affects time comparisons (expiry, etc.) and serialization. Default is seconds for backward compatibility.

### None Signing

```go
var NoneSignatureTypeDisallowedError error
var SigningMethodNone *signingMethodNone
```
`SigningMethodNone` implements the `none` signing method. Required by the spec, but you should probably never use it.

---

## Functions

### `GetAlgorithms()`
```go
func GetAlgorithms() (algs []string)
```
Returns a list of all registered `"alg"` names.

### `Parse()`
```go
func Parse(tokenString string, keyFunc Keyfunc, options ...ParserOption) (*Token, error)
```
Parses, validates, verifies the signature and returns the parsed token. `keyFunc` receives the parsed token and should return the cryptographic key. Strongly encouraged to use `WithValidMethods` to validate the `alg` claim matches the expected algorithm.

> See: https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/

### `ParseWithClaims()`
```go
func ParseWithClaims(tokenString string, claims Claims, keyFunc Keyfunc, options ...ParserOption) (*Token, error)
```
Shortcut for `NewParser().ParseWithClaims()`.

**Important:** If you provide a custom claim implementation that embeds standard claims (e.g., `RegisteredClaims`), ensure you either embed a non-pointer version or allocate proper memory for it — otherwise you might hit a panic.

### `RegisterSigningMethod()`
```go
func RegisterSigningMethod(alg string, f func() SigningMethod)
```
Registers the `"alg"` name and a factory function for a signing method. Typically done during `init()`.

### PEM Parsing Functions

```go
func ParseRSAPrivateKeyFromPEM(key []byte) (*rsa.PrivateKey, error)
func ParseRSAPublicKeyFromPEM(key []byte) (*rsa.PublicKey, error)
func ParseECPrivateKeyFromPEM(key []byte) (*ecdsa.PrivateKey, error)
func ParseECPublicKeyFromPEM(key []byte) (*ecdsa.PublicKey, error)
func ParseEdPrivateKeyFromPEM(key []byte) (crypto.PrivateKey, error)
func ParseEdPublicKeyFromPEM(key []byte) (crypto.PublicKey, error)
```

```go
// Deprecated: uses x509.DecryptPEMBlock (RFC 1423, insecure by design)
func ParseRSAPrivateKeyFromPEMWithPassword(key []byte, password string) (*rsa.PrivateKey, error)
```

---

## Error Variables

```go
var (
    ErrInvalidKey                = errors.New("key is invalid")
    ErrInvalidKeyType            = errors.New("key is of invalid type")
    ErrHashUnavailable           = errors.New("the requested hash function is unavailable")
    ErrTokenMalformed            = errors.New("token is malformed")
    ErrTokenUnverifiable         = errors.New("token is unverifiable")
    ErrTokenSignatureInvalid     = errors.New("token signature is invalid")
    ErrTokenRequiredClaimMissing = errors.New("token is missing required claim")
    ErrTokenInvalidAudience      = errors.New("token has invalid audience")
    ErrTokenExpired              = errors.New("token is expired")
    ErrTokenUsedBeforeIssued     = errors.New("token used before issued")
    ErrTokenInvalidIssuer        = errors.New("token has invalid issuer")
    ErrTokenInvalidSubject       = errors.New("token has invalid subject")
    ErrTokenNotValidYet          = errors.New("token is not valid yet")
    ErrTokenInvalidId            = errors.New("token has invalid id")
    ErrTokenInvalidClaims        = errors.New("token has invalid claims")
    ErrInvalidType               = errors.New("invalid type for claim")
)

// RSA-specific
var (
    ErrKeyMustBePEMEncoded  = errors.New("invalid key: Key must be a PEM encoded PKCS1 or PKCS8 key")
    ErrNotRSAPrivateKey     = errors.New("key is not a valid RSA private key")
    ErrNotRSAPublicKey      = errors.New("key is not a valid RSA public key")
)

// ECDSA-specific
var (
    ErrECDSAVerification = errors.New("crypto/ecdsa: verification error")
    ErrNotECPublicKey    = errors.New("key is not a valid ECDSA public key")
    ErrNotECPrivateKey   = errors.New("key is not a valid ECDSA private key")
)

// Ed25519-specific
var (
    ErrEd25519Verification = errors.New("ed25519: verification error")
    ErrNotEdPrivateKey     = errors.New("key is not a valid Ed25519 private key")
    ErrNotEdPublicKey      = errors.New("key is not a valid Ed25519 public key")
)

// HMAC-specific
var ErrSignatureInvalid = errors.New("signature is invalid")
```

---

## Types

### `Token` (main struct)

```go
type Token struct {
    Raw       string         // Raw token string. Populated by Parse.
    Method    SigningMethod  // Signing method used or to be used
    Header    map[string]any // First segment of the token in decoded form
    Claims    Claims         // Second segment of the token in decoded form
    Signature []byte         // Third segment in decoded form. Populated by Parse or Sign.
    Valid     bool           // Whether the token is valid. Populated by Parse.
}
```

#### Constructor Functions

```go
func New(method SigningMethod, opts ...TokenOption) *Token
```
Creates a new Token with the specified signing method and empty claims.

```go
func NewWithClaims(method SigningMethod, claims Claims, opts ...TokenOption) *Token
```
Creates a new Token with the specified signing method and claims.

#### Methods

```go
func (t *Token) SignedString(key any) (string, error)
```
Creates and returns a complete, signed JWT string. Signs using the token's `SigningMethod`.

See [signing methods and key types](https://golang-jwt.github.io/jwt/usage/signing_methods/#signing-methods-and-key-types) for key type requirements per algorithm.

```go
func (t *Token) SigningString() (string, error)
```
Generates the signing string. This is the most expensive part — unless you need this for something special, use `SignedString`.

```go
func (*Token) EncodeSegment(seg []byte) string
```
Encodes a JWT-specific base64url encoding with padding stripped.

### `TokenOption`
```go
type TokenOption func(*Token)
```
Reserved type for forward compatibility with token creation options.

---

### `Claims` (interface)

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
Represents any form of a JWT Claims Set per [RFC 7519 §4](https://datatracker.ietf.org/doc/html/rfc7519#section-4). Required getters for: `exp`, `iat`, `nbf`, `iss`, `sub`, `aud`.

### `ClaimsValidator` (interface)

```go
type ClaimsValidator interface {
    Claims
    Validate() error
}
```
For custom claims that need additional application-specific validation. The `Validate` function is executed **in addition to** regular claims validation — it cannot disable standard validation.

```go
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

### `RegisteredClaims` (struct)

```go
type RegisteredClaims struct {
    Issuer    string        `json:"iss,omitempty"` // RFC 7519 §4.1.1
    Subject   string        `json:"sub,omitempty"` // RFC 7519 §4.1.2
    Audience  ClaimStrings  `json:"aud,omitempty"` // RFC 7519 §4.1.3
    ExpiresAt *NumericDate  `json:"exp,omitempty"` // RFC 7519 §4.1.4
    NotBefore *NumericDate  `json:"nbf,omitempty"` // RFC 7519 §4.1.5
    IssuedAt  *NumericDate  `json:"iat,omitempty"` // RFC 7519 §4.1.6
    ID        string        `json:"jti,omitempty"` // RFC 7519 §4.1.7
}
```
Structured version of JWT Claims Set, restricted to Registered Claim Names. Implements the `Claims` interface. Can be used standalone, but typically **embedded** in a user-defined claim type.

### `MapClaims` (type)

```go
type MapClaims map[string]any
```
Claims type using `map[string]any` for JSON decoding. This is the **default** claims type if you don't supply one. Implements the `Claims` interface.

### `ClaimStrings`

```go
type ClaimStrings []string
```
A `[]string` that can be serialized from either a JSON string or a JSON array. Necessary because the `"aud"` claim can be either a single string or an array.

```go
func (s ClaimStrings) MarshalJSON() (b []byte, err error)
func (s *ClaimStrings) UnmarshalJSON(data []byte) (err error)
```

### `NumericDate`

```go
type NumericDate struct {
    time.Time
}
```
Represents a JSON numeric date value per [RFC 7519 §2](https://datatracker.ietf.org/doc/html/rfc7519#section-2).

```go
func NewNumericDate(t time.Time) *NumericDate
```
Constructs a new `NumericDate`, truncating the timestamp to `TimePrecision`.

```go
func (date NumericDate) MarshalJSON() (b []byte, err error)
func (date *NumericDate) UnmarshalJSON(b []byte) (err error)
```

---

### `Keyfunc`

```go
type Keyfunc func(*Token) (any, error)
```
Callback function used by `Parse` methods to supply the key for verification. Receives the parsed but **unverified** Token. Allows using Header properties (e.g., `kid`) to identify which key to use.

The returned `any` may be a single key or a `VerificationKeySet` containing multiple keys.

### `VerificationKey`

```go
type VerificationKey interface {
    crypto.PublicKey | []uint8
}
```
Represents a public or secret key for verifying a token's signature.

### `VerificationKeySet`

```go
type VerificationKeySet struct {
    Keys []VerificationKey
}
```
A set of public or secret keys used by the parser to verify a token.

---

### `Parser`

```go
type Parser struct {
    // Has unexported fields.
}
```

```go
func NewParser(options ...ParserOption) *Parser
```

#### Methods

```go
func (p *Parser) Parse(tokenString string, keyFunc Keyfunc) (*Token, error)
```
Parses, validates, verifies the signature and returns the parsed token.

```go
func (p *Parser) ParseWithClaims(tokenString string, claims Claims, keyFunc Keyfunc) (*Token, error)
```
Like `Parse`, but supplies a default Claims object. Allows callers to use their own type (not just `MapClaims`).

```go
func (p *Parser) ParseUnverified(tokenString string, claims Claims) (token *Token, parts []string, err error)
```
Parses the token but **does not validate the signature**.

> ⚠️ **WARNING:** Only use this if you know the signature is valid (already checked elsewhere) and you only need to extract values.

```go
func (p *Parser) DecodeSegment(seg string) ([]byte, error)
```
Decodes JWT-specific base64url encoding. Respects parser options like `WithStrictDecoding` and `WithPaddingAllowed`.

---

### `Validator`

```go
type Validator struct {
    // Has unexported fields.
}
```
Core of the validation API. Automatically used by `Parser` during parsing.

```go
func NewValidator(opts ...ParserOption) *Validator
```
Creates a standalone validator. **Note:** Under normal circumstances, explicitly creating a validator is not needed — use `Parser` methods instead. The `Validator` only checks claim *validity* (expiration, etc.), **not** signature verification.

```go
func (v *Validator) Validate(claims Claims) error
```
Validates the given claims. Also runs custom validation via `ClaimsValidator` if implemented. Does **NOT** perform signature verification.

---

### `ParserOption` (functional options)

```go
type ParserOption func(*Parser)
```
Functional-style options that modify parser behavior.

#### Available Options

| Option | Signature | Description |
|--------|-----------|-------------|
| `WithValidMethods` | `func(methods []string) ParserOption` | Whitelist allowed `alg` values. **Heavily encouraged** to prevent algorithm confusion attacks. |
| `WithLeeway` | `func(leeway time.Duration) ParserOption` | Clock skew tolerance for time-based claims (`exp`, `nbf`, `iat`). |
| `WithIssuer` | `func(iss string) ParserOption` | Require specific `iss` claim. Fails if missing or different. |
| `WithSubject` | `func(sub string) ParserOption` | Require specific `sub` claim. Fails if missing or different. |
| `WithAudience` | `func(aud ...string) ParserOption` | Require any of the specified `aud` values. Fails if none match or claim is missing. |
| `WithAllAudiences` | `func(aud ...string) ParserOption` | Require **all** specified `aud` values. Deduplicates internally. |
| `WithExpirationRequired` | `func() ParserOption` | Make `exp` claim required (optional by default). |
| `WithNotBeforeRequired` | `func() ParserOption` | Make `nbf` claim required (optional by default). |
| `WithIssuedAt` | `func() ParserOption` | Enable `iat` verification (disabled by default; `iat` is informational per RFC). |
| `WithTimeFunc` | `func(f func() time.Time) ParserOption` | Custom time function (primary use-case: testing). For clock skew, use `WithLeeway`. |
| `WithJSONNumber` | `func() ParserOption` | Configure JSON parser with `UseNumber`. |
| `WithStrictDecoding` | `func() ParserOption` | Strict base64 decoding (trailing padding bits must be zero per RFC 4648 §3.5). |
| `WithPaddingAllowed` | `func() ParserOption` | Allow base64 padding in tokens (non-standard, but some IdPs issue these). |
| `WithoutClaimsValidation` | `func() ParserOption` | Disable claims validation entirely. ⚠️ Only if you know exactly what you're doing. |

---

### `SigningMethod` (interface)

```go
type SigningMethod interface {
    Verify(signingString string, sig []byte, key any) error // Returns nil if signature is valid
    Sign(signingString string, key any) ([]byte, error)     // Returns signature or error
    Alg() string                                            // Returns the alg identifier (e.g. "HS256")
}
```
Interface for adding new signing/verification methods. The signature is decoded `[]byte` (not base64).

```go
func GetSigningMethod(alg string) (method SigningMethod)
```
Retrieves a signing method from its `"alg"` string.

---

### Signing Method Implementations

#### `SigningMethodHMAC`

```go
type SigningMethodHMAC struct {
    Name string
    Hash crypto.Hash
}
```
HMAC-SHA family. Expects key type `[]byte` for both signing and verification.

> ⚠️ Do not use `[]byte` converted from a human-readable ASCII string. Use a cryptographically random key from `crypto/rand`. See [usage guide](https://golang-jwt.github.io/jwt/usage/signing_methods/).

**Predefined instances:**
```go
var SigningMethodHS256 *SigningMethodHMAC  // HMAC-SHA256
var SigningMethodHS384 *SigningMethodHMAC  // HMAC-SHA384
var SigningMethodHS512 *SigningMethodHMAC  // HMAC-SHA512
```

#### `SigningMethodRSA`

```go
type SigningMethodRSA struct {
    Name string
    Hash crypto.Hash
}
```
RSA family. Expects `*rsa.PrivateKey` for signing and `*rsa.PublicKey` for verification.

**Predefined instances:**
```go
var SigningMethodRS256 *SigningMethodRSA  // RSA-SHA256
var SigningMethodRS384 *SigningMethodRSA  // RSA-SHA384
var SigningMethodRS512 *SigningMethodRSA  // RSA-SHA512
```

#### `SigningMethodRSAPSS`

```go
type SigningMethodRSAPSS struct {
    *SigningMethodRSA
    Options       *rsa.PSSOptions
    VerifyOptions *rsa.PSSOptions  // Optional override for Verify; used for PSSSaltLengthAuto tokens
}
```
RSA-PSS family. Expects `*rsa.PrivateKey` for signing and `*rsa.PublicKey` for verification.

**Predefined instances:**
```go
var SigningMethodPS256 *SigningMethodRSAPSS  // RSAPSS-SHA256
var SigningMethodPS384 *SigningMethodRSAPSS  // RSAPSS-SHA384
var SigningMethodPS512 *SigningMethodRSAPSS  // RSAPSS-SHA512
```

#### `SigningMethodECDSA`

```go
type SigningMethodECDSA struct {
    Name      string
    Hash      crypto.Hash
    KeySize   int
    CurveBits int
}
```
ECDSA family. Expects `*ecdsa.PrivateKey` for signing and `*ecdsa.PublicKey` for verification.

**Predefined instances:**
```go
var SigningMethodES256 *SigningMethodECDSA  // ECDSA-SHA256 (P-256)
var SigningMethodES384 *SigningMethodECDSA  // ECDSA-SHA384 (P-384)
var SigningMethodES512 *SigningMethodECDSA  // ECDSA-SHA512 (P-521)
```

#### `SigningMethodEd25519`

```go
type SigningMethodEd25519 struct{}
```
EdDSA (Ed25519). Expects `ed25519.PrivateKey` for signing and `ed25519.PublicKey` for verification.

**Predefined instance:**
```go
var SigningMethodEdDSA *SigningMethodEd25519
```

---

## Sub-package: `request`

> **Import:** `"github.com/golang-jwt/jwt/v5/request"`

Utility package for extracting JWT tokens from HTTP requests.

### Variables

```go
var AuthorizationHeaderExtractor = &PostExtractionFilter{...}
// Extracts bearer token from Authorization header, stripping "Bearer " prefix.

var OAuth2Extractor = &MultiExtractor{
    AuthorizationHeaderExtractor,
    ArgumentExtractor{"access_token"},
}
// OAuth2 extractor: looks in Authorization header, then 'access_token' argument.

var ErrNoTokenInRequest = errors.New("no token present in request")
```

### Functions

```go
func ParseFromRequest(req *http.Request, extractor Extractor, keyFunc jwt.Keyfunc, options ...ParseFromRequestOption) (*jwt.Token, error)
```
Extracts and parses a JWT from an HTTP request. Behaves like `Parse` but accepts a request + extractor.

```go
// Deprecated: use ParseFromRequest with WithClaims option
func ParseFromRequestWithClaims(req *http.Request, extractor Extractor, claims jwt.Claims, keyFunc jwt.Keyfunc) (*jwt.Token, error)
```

### Types

```go
type Extractor interface {
    ExtractToken(*http.Request) (string, error)
}
```

| Extractor | Type | Description |
|-----------|------|-------------|
| `HeaderExtractor` | `[]string` | Looks at each specified header in order |
| `ArgumentExtractor` | `[]string` | Looks at request arguments (POST form or GET query) |
| `BearerExtractor` | `struct{}` | Extracts from `Authorization` header, expects `"Bearer XX"` format |
| `MultiExtractor` | `[]Extractor` | Tries extractors in order until one succeeds |
| `PostExtractionFilter` | struct wrapping Extractor + Filter | Post-processes extracted value before use |

```go
type ParseFromRequestOption func(*fromRequestParser)

func WithClaims(claims jwt.Claims) ParseFromRequestOption
func WithParser(parser *jwt.Parser) ParseFromRequestOption
```

---

## Sub-package: `test`

> **Import:** `"github.com/golang-jwt/jwt/v5/test"`

Test helpers.

```go
func LoadRSAPrivateKeyFromDisk(location string) *rsa.PrivateKey
func LoadRSAPublicKeyFromDisk(location string) *rsa.PublicKey
func LoadECPrivateKeyFromDisk(location string) crypto.PrivateKey
func LoadECPublicKeyFromDisk(location string) crypto.PublicKey
func MakeSampleToken(c jwt.Claims, method jwt.SigningMethod, key any) string
```
