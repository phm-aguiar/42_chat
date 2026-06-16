# golang-jwt v5.3.1 — Examples

> All examples from `example_test.go` and `hmac_example_test.go`
> Source: `github.com/golang-jwt/jwt/v5@v5.3.1`

---

## 1. Creating & Signing a Token (HMAC)

```go
package main

import (
    "fmt"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

func main() {
    // Create a new token with signing method and claims
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "foo": "bar",
        "nbf": time.Date(2015, 10, 10, 12, 0, 0, 0, time.UTC).Unix(),
    })

    // Sign and get the complete encoded token as a string
    tokenString, err := token.SignedString([]byte("AllYourBase"))
    fmt.Println(tokenString, err)
}
```

---

## 2. Parsing & Validating a Token (HMAC)

```go
package main

import (
    "fmt"
    "log"

    "github.com/golang-jwt/jwt/v5"
)

func main() {
    tokenString := "eyJhbG...srpU"

    // Parse takes the token string and a function for looking up the key.
    // Use 'kid' in the header to identify which key to use — the parsed
    // token (head and claims) is provided to the callback.
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (any, error) {
        // Return your secret key as []byte
        return []byte("AllYourBase"), nil
    }, jwt.WithValidMethods([]string{jwt.SigningMethodHS256.Alg()}))

    if err != nil {
        log.Fatal(err)
    }

    if claims, ok := token.Claims.(jwt.MapClaims); ok {
        fmt.Println(claims["foo"], claims["nbf"])
    }
}
```

---

## 3. Creating a Token with RegisteredClaims

```go
package main

import (
    "fmt"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

func main() {
    mySigningKey := []byte("AllYourBase")

    claims := &jwt.RegisteredClaims{
        ExpiresAt: jwt.NewNumericDate(time.Unix(1516239022, 0)),
        Issuer:    "test",
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    ss, err := token.SignedString(mySigningKey)
    fmt.Println(ss, err)
}
```

---

## 4. Creating a Token with Custom Claims (embedding RegisteredClaims)

```go
package main

import (
    "fmt"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

func main() {
    mySigningKey := []byte("AllYourBase")

    // Create claims with multiple fields populated
    claims := MyCustomClaims{
        Foo: "bar",
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            NotBefore: jwt.NewNumericDate(time.Now()),
            Issuer:    "test",
            Subject:   "somebody",
            ID:        "1",
            Audience:  []string{"somebody_else"},
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    ss, err := token.SignedString(mySigningKey)
    fmt.Println(ss, err)
}
```

---

## 5. Parsing with Custom Claims Type

```go
package main

import (
    "fmt"
    "log"

    "github.com/golang-jwt/jwt/v5"
)

type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

func main() {
    tokenString := "eyJhbG...beaA"

    token, err := jwt.ParseWithClaims(tokenString, &MyCustomClaims{}, func(token *jwt.Token) (any, error) {
        return []byte("AllYourBase"), nil
    })

    if err != nil {
        log.Fatal(err)
    }

    if claims, ok := token.Claims.(*MyCustomClaims); ok {
        fmt.Println(claims.Foo, claims.Issuer)
    } else {
        log.Fatal("unknown claims type, cannot proceed")
    }
}
```

---

## 6. Parsing with Validation Options (Leeway)

```go
package main

import (
    "fmt"
    "log"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

func main() {
    tokenString := "eyJhbG...beaA"

    // Parse with a 5-second leeway window for clock skew
    token, err := jwt.ParseWithClaims(tokenString, &MyCustomClaims{}, func(token *jwt.Token) (any, error) {
        return []byte("AllYourBase"), nil
    }, jwt.WithLeeway(5*time.Second))

    if err != nil {
        log.Fatal(err)
    }

    if claims, ok := token.Claims.(*MyCustomClaims); ok {
        fmt.Println(claims.Foo, claims.Issuer)
    } else {
        log.Fatal("unknown claims type, cannot proceed")
    }
}
```

---

## 7. Custom Claims Validation

```go
package main

import (
    "errors"
    "fmt"
    "log"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

type MyCustomClaims struct {
    Foo string `json:"foo"`
    jwt.RegisteredClaims
}

// Ensure at compile time that MyCustomClaims implements ClaimsValidator
var _ jwt.ClaimsValidator = (*MyCustomClaims)(nil)

// Validate runs additional application-specific claims validation.
// This is executed IN ADDITION to standard validation — it cannot disable it.
func (m MyCustomClaims) Validate() error {
    if m.Foo != "bar" {
        return errors.New("must be foobar")
    }
    return nil
}

func main() {
    tokenString := "eyJhbG...beaA"

    token, err := jwt.ParseWithClaims(tokenString, &MyCustomClaims{}, func(token *jwt.Token) (any, error) {
        return []byte("AllYourBase"), nil
    }, jwt.WithLeeway(5*time.Second))

    if err != nil {
        log.Fatal(err)
    }

    if claims, ok := token.Claims.(*MyCustomClaims); ok {
        fmt.Println(claims.Foo, claims.Issuer)
    } else {
        log.Fatal("unknown claims type, cannot proceed")
    }
}
```

---

## 8. Error Checking with `errors.Is`

```go
package main

import (
    "errors"
    "fmt"

    "github.com/golang-jwt/jwt/v5"
)

func main() {
    tokenString := "eyJhbG...wu_c" // expired token

    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (any, error) {
        return []byte("AllYourBase"), nil
    })

    switch {
    case token.Valid:
        fmt.Println("You look nice today")
    case errors.Is(err, jwt.ErrTokenMalformed):
        fmt.Println("That's not even a token")
    case errors.Is(err, jwt.ErrTokenSignatureInvalid):
        fmt.Println("Invalid signature")
    case errors.Is(err, jwt.ErrTokenExpired) || errors.Is(err, jwt.ErrTokenNotValidYet):
        fmt.Println("Timing is everything")
    default:
        fmt.Println("Couldn't handle this token:", err)
    }
}
```

---

## 9. Standalone Validator (without Parser)

```go
package main

import (
    "time"

    "github.com/golang-jwt/jwt/v5"
)

func main() {
    claims := &jwt.RegisteredClaims{
        ExpiresAt: jwt.NewNumericDate(time.Now().Add(-1 * time.Hour)),
    }

    // Create a standalone validator with 5-second leeway
    v := jwt.NewValidator(jwt.WithLeeway(5 * time.Second))
    err := v.Validate(claims)
    // err will be jwt.ErrTokenExpired
    _ = err
}
```

---

## 10. Extracting JWT from HTTP Request

```go
package main

import (
    "net/http"

    "github.com/golang-jwt/jwt/v5"
    "github.com/golang-jwt/jwt/v5/request"
)

func handler(w http.ResponseWriter, r *http.Request) {
    // Extract from Authorization: Bearer <token>
    token, err := request.ParseFromRequest(
        r,
        request.AuthorizationHeaderExtractor,
        func(token *jwt.Token) (any, error) {
            return []byte("AllYourBase"), nil
        },
        jwt.WithValidMethods([]string{"HS256"}),
    )

    if err != nil {
        http.Error(w, err.Error(), http.StatusUnauthorized)
        return
    }

    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        // Use claims...
    }
}
```

### Alternative Extractors

```go
// OAuth2: checks Authorization header, then access_token query param
request.OAuth2Extractor

// Custom header
request.HeaderExtractor{"X-Auth-Token"}

// Query/post form argument
request.ArgumentExtractor{"token", "jwt"}

// Multiple extractors in order
&request.MultiExtractor{
    request.HeaderExtractor{"X-Auth-Token"},
    request.ArgumentExtractor{"jwt"},
}
```

---

## 11. Registering a Custom Signing Method

```go
package main

import "github.com/golang-jwt/jwt/v5"

type MyCustomSigningMethod struct{}

func (m *MyCustomSigningMethod) Alg() string {
    return "CUSTOM"
}

func (m *MyCustomSigningMethod) Sign(signingString string, key any) ([]byte, error) {
    // Implement signing logic
    return nil, nil
}

func (m *MyCustomSigningMethod) Verify(signingString string, sig []byte, key any) error {
    // Implement verification logic
    return nil
}

func init() {
    jwt.RegisterSigningMethod("CUSTOM", func() jwt.SigningMethod {
        return &MyCustomSigningMethod{}
    })
}
```

---

## Key Type Reference per Signing Method

| Signing Method | `alg` | Sign Key Type | Verify Key Type |
|---------------|-------|---------------|-----------------|
| `SigningMethodHS256` | `HS256` | `[]byte` | `[]byte` |
| `SigningMethodHS384` | `HS384` | `[]byte` | `[]byte` |
| `SigningMethodHS512` | `HS512` | `[]byte` | `[]byte` |
| `SigningMethodRS256` | `RS256` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| `SigningMethodRS384` | `RS384` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| `SigningMethodRS512` | `RS512` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| `SigningMethodPS256` | `PS256` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| `SigningMethodPS384` | `PS384` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| `SigningMethodPS512` | `PS512` | `*rsa.PrivateKey` | `*rsa.PublicKey` |
| `SigningMethodES256` | `ES256` | `*ecdsa.PrivateKey` | `*ecdsa.PublicKey` |
| `SigningMethodES384` | `ES384` | `*ecdsa.PrivateKey` | `*ecdsa.PublicKey` |
| `SigningMethodES512` | `ES512` | `*ecdsa.PrivateKey` | `*ecdsa.PublicKey` |
| `SigningMethodEdDSA` | `EdDSA` | `ed25519.PrivateKey` | `ed25519.PublicKey` |

> ⚠️ **HMAC keys:** Do not use human-readable strings. Generate with `crypto/rand` for maximum entropy.
> See [signing methods guide](https://golang-jwt.github.io/jwt/usage/signing_methods/#signing-methods-and-key-types).
