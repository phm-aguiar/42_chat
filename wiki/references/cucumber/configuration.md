---
title: "Configuration"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/Configuration  Cucumber.md"
created: "2026-06-21"
rag_score: 0.5
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
## Parameter types

Parameter types let you convert parameters from [Cucumber expressions](https://cucumber.io/docs/cucumber/cucumber-expressions) to objects.

Data table and doc string types let you convert data tables and doc strings to objects. Like step definitions, type definitions are part of the glue. When placed on the glue path Cucumber will detect them automatically.

For example, the following class registers a custom "Author" data table type:

```java
package com.example;

import io.cucumber.java.DataTableType;
import io.cucumber.java.en.Given;

import java.util.List;
import java.util.Map;

public class StepDefinitions {

    @DataTableType
            entry.get("firstName"),
            entry.get("lastName"),
            entry.get("famousBook"));
    }

    @Given("These are my favorite authors")
        // step implementation
    }
}
```

This class registers a custom "Book" type from an expression:

```java
package com.example;

import io.cucumber.java.ParameterType;
import io.cucumber.java.en.Given;

public class StepDefinitions {

    @ParameterType(".*")
    public Book book(String bookName) {
        return new Book(bookName);
    }

    @Given("{book} is my favorite book")
    public void this_is_my_favorite_book(Book book) {
        // step implementation
    }
}
```

This class registers a custom type for a doc string:

```java
package com.example;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.cucumber.java.DocStringType;
import io.cucumber.java.en.Given;

public class StepsDefinitions {

    private static ObjectMapper objectMapper = new ObjectMapper();

    @DocStringType
    public JsonNode json(String docString) throws JsonProcessingException {
        return objectMapper.readValue(docString, JsonNode.class);
    }

    @Given("Books are defined by json")
    public void books_are_defined_by_json(JsonNode books) {
        // step implementation
    }
}
```

For lambda-defined step definitions, there are `DataTableType`, `ParameterType` and `DocStringType` functions:

```java
package com.example;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.cucumber.java8.En;

import java.util.Map;

public class LambdaStepDefinitions implements En {

    private static ObjectMapper objectMapper = new ObjectMapper();

    public LambdaStepDefinitions() {

            entry.get("firstName"),
            entry.get("lastName"),
            entry.get("famousBook")
        ));

        ParameterType("book", ".*", (String bookName) -> new Book(bookName));

        DocStringType("json", (String docString) ->
            objectMapper.readValue(docString, JsonNode.class));
    }
}
```

Using the `@DefaultParameterTransformer`, `@DefaultDataTableEntryTransformer` and `@DefaultDataTableCellTransformer` annotations, it is also possible to plug in an object mapper. The object mapper (Jackson in this example) will handle the conversion of anonymous parameter types and data table entries:

```java
package com.example;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.cucumber.java.DefaultDataTableCellTransformer;
import io.cucumber.java.DefaultDataTableEntryTransformer;
import io.cucumber.java.DefaultParameterTransformer;

import java.lang.reflect.Type;

public class StepDefinitions {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @DefaultParameterTransformer
    @DefaultDataTableEntryTransformer
    @DefaultDataTableCellTransformer
    public Object transformer(Object fromValue, Type toValueType) {
        return objectMapper.convertValue(fromValue, objectMapper.constructType(toValueType));
    }
}
```

For lambda-defined step definitions, there are `DefaultParameterTransformer`, `DefaultDataTableCellTransformer` and `DefaultDataTableEntryTransformer` methods:

```java
package com.example;

import io.cucumber.java8.En;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.lang.reflect.Type;

public class LambdaStepDefinitions implements En {

    public LambdaStepDefinitions() {
        ObjectMapper objectMapper = new ObjectMapper();

        DefaultParameterTransformer((String fromValue, Type toValueType) ->
            objectMapper.convertValue(fromValue, objectMapper.constructType(toValueType)));

        DefaultDataTableCellTransformer((fromValue, toValueType) ->
            objectMapper.convertValue(fromValue, objectMapper.constructType(toValueType)));

        DefaultDataTableEntryTransformer((fromValue, toValueType) ->
            objectMapper.convertValue(fromValue, objectMapper.constructType(toValueType)));
    }
}
```

If you try to use a type that has not yet been defined, you will see an error similar to:

```shell
The parameter type "person" is not defined.
```

## Profiles

Cucumber profiles are not available on Cucumber-JVM. However, it is possible to set configuration options using [Maven profiles](https://maven.apache.org/guides/introduction/introduction-to-profiles.html)

For instance, we can configure separate profiles for scenarios which are to be run in separate environments like so:

```xml
<profiles>
    <profile>
      <id>dev</id>
        <properties>
            <cucumber.filter.tags>@dev and not @ignore</cucumber.filter.tags>
        </properties>
    </profile>
    <profile>
      <id>qa</id>
        <properties>
            <cucumber.filter.tags>@qa</cucumber.filter.tags>
        </properties>
    </profile>
</profiles>

<build>
    <plugins>
        ...
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.0.0-M4</version>
            <configuration>
                <systemPropertyVariables>
                   <cucumber.filter.tags>${cucumber.filter.tags}</cucumber.filter.tags>
                </systemPropertyVariables>
            </configuration>
        </plugin>
    </plugins>
</build>
```

To mimick similar behavior using Gradle, see the Gradle docs on [Migrating Maven profiles and properties](https://docs.gradle.org/current/userguide/migrating_from_maven.html#migmvn:profiles_and_properties).

## Environment variables

Cucumber-JVM does not support configuration with an `env` file.