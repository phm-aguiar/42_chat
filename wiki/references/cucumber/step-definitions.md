---
title: "Step Definitions"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/Step definitions.md"
created: "2026-06-21"
rag_score: 0.5
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
A Step Definition is a method with an [expression](#expressions) that links it to one or more [Gherkin steps](https://cucumber.io/docs/gherkin/reference#steps). When Cucumber executes a [Gherkin step](https://cucumber.io/docs/gherkin/reference#steps) in a scenario, it will look for a matching *step definition* to execute.

To illustrate how this works, look at the following Gherkin Scenario:

```markdown
Scenario: Some cukes
  Given I have 48 cukes in my belly
```

The `I have 48 cukes in my belly` part of the step (the text following the `Given` keyword) will match the following step definition:

```java
package com.example;
import io.cucumber.java.en.Given;

public class StepDefinitions {
    @Given("I have {int} cukes in my belly")
    public void i_have_n_cukes_in_my_belly(int cukes) {
        System.out.format("Cukes: %n\n", cukes);
    }
}
```

Or, using Java8 lambdas:

```java
package com.example;
import io.cucumber.java8.En;

public class StepDefinitions implements En {
    public StepDefinitions() {
        Given("I have {int} cukes in my belly", (Integer cukes) -> {
            System.out.format("Cukes: %n\n", cukes);
        });
    }
}
```

## Expressions

A step definition's *expression* can either be a [Regular Expression](https://en.wikipedia.org/wiki/Regular_expression) or a [Cucumber Expression](https://cucumber.io/docs/cucumber/cucumber-expressions). The examples in this section use Cucumber Expressions. If you prefer to use Regular Expressions, each capture group from the match will be passed as arguments to the step definition's method.

```java
@Given("I have {int} cukes in my belly")
public void i_have_n_cukes_in_my_belly(int cukes) {
}
```

If the capture group expression is identical to one of the registered [parameter types](https://cucumber.io/docs/cucumber/cucumber-expressions#parameter-types) 's `regexp`, the captured string will be transformed before it is passed to the step definition's method. In the example above, the `cukes` argument will be an integer, because the built-in `int` parameter type's `regexp` is `\d+`.