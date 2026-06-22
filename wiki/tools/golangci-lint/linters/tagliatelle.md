---
title: "tagliatelle"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# tagliatelle

## tagalign

Check that struct tags are well aligned.

```
linters-settings:
  tagalign:
    # Align and sort can be used together or separately.
    #
    # Whether enable align. If true, the struct tags will be aligned.
    # e.g.:
    # type FooBar struct {
    #     Bar    string \`json:"bar" validate:"required"\`
    #     FooFoo int8   \`json:"foo_foo" validate:"required"\`
    # }
    # will be formatted to:
    # type FooBar struct {
    #     Bar    string \`json:"bar"     validate:"required"\`
    #     FooFoo int8   \`json:"foo_foo" validate:"required"\`
    # }
    # Default: true.
    align: false
    # Whether enable tags sort.
    # If true, the tags will be sorted by name in ascending order.
    # e.g.: \`xml:"bar" json:"bar" validate:"required"\` -> \`json:"bar" validate:"required" xml:"bar"\`
    # Default: true
    sort: false
    # Specify the order of tags, the other tags will be sorted by name.
    # This option will be ignored if \`sort\` is false.
    # Default: []
    order:
      - json
      - yaml
      - yml
      - toml
      - mapstructure
      - binding
      - validate
    # Whether enable strict style.
    # In this style, the tags will be sorted and aligned in the dictionary order,
    # and the tags with the same name will be aligned together.
    # Note: This option will be ignored if 'align' or 'sort' is false.
    # Default: false
    strict: true
```


Checks the struct tags.

```
linters-settings:
  tagliatelle:
    # Checks the struct tag name case.
    case:
      # Defines the association between tag name and case.
      # Any struct tag name can be used.
      # Supported string cases:
      # - \`camel\`
      # - \`pascal\`
      # - \`kebab\`
      # - \`snake\`
      # - \`upperSnake\`
      # - \`goCamel\`
      # - \`goPascal\`
      # - \`goKebab\`
      # - \`goSnake\`
      # - \`upper\`
      # - \`lower\`
      # - \`header\`
      rules:
        json: camel
        yaml: camel
        xml: camel
        toml: camel
        bson: camel
        avro: snake
        mapstructure: kebab
        env: upperSnake
        envconfig: upperSnake
        whatever: snake
      # Defines the association between tag name and case.
      # Important: the \`extended-rules\` overrides \`rules\`.
      # Default: empty
      extended-rules:
        json:
          # Supported string cases:
          # - \`camel\`
          # - \`pascal\`
          # - \`kebab\`
          # - \`snake\`
          # - \`upperSnake\`
          # - \`goCamel\`
          # - \`goPascal\`
          # - \`goKebab\`
          # - \`goSnake\`
          # - \`header\`
          # - \`lower\`
          # - \`header\`
          #
          # Required
          case: camel
          # Adds 'AMQP', 'DB', 'GID', 'RTP', 'SIP', 'TS' to initialisms,
          # and removes 'LHS', 'RHS' from initialisms.
          # Default: false
          extra-initialisms: true
          # Defines initialism additions and overrides.
          # Default: empty
          initialism-overrides:
            DB: true # add a new initialism
            LHS: false # disable a default initialism.
            # ...
      # Uses the struct field name to check the name of the struct tag.
      # Default: false
      use-field-name: true
      # The field names to ignore.
      # Default: []
      ignored-fields:
        - Bar
        - Foo
      # Overrides the default/root configuration.
      # Default: []
      overrides:
        - # The package path (uses \`/\` only as a separator).
          # Required
          pkg: foo/bar
          # Default: empty or the same as the default/root configuration.
          rules:
            json: snake
            xml: pascal
          # Default: empty or the same as the default/root configuration.
          extended-rules:
          # Same options as the base \`extended-rules\`.
          # Default: false (WARNING: it doesn't follow the default/root configuration)
          use-field-name: true
          # The field names to ignore.
          # Default: [] or the same as the default/root configuration.
          ignored-fields:
            - Bar
            - Foo
          # Ignore the package (takes precedence over all other configurations).
          # Default: false
          ignore: true
```
