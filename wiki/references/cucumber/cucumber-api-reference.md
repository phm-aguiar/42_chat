---
title: "Cucumber API Reference"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/Cucumber reference.md"
created: "2026-06-21"
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
Cucumber can be used to implement automated tests based on scenarios described in your Gherkin feature files.

## Step arguments

In the example given in [step definitions](https://cucumber.io/docs/cucumber/step-definitions), Cucumber extracts the text `48` from the step, converts it to an `int` and passes it as an argument to the method.

The number of parameters in the method has to match the number of capture groups in the expression. (If there is a mismatch, Cucumber will throw an error).

## Data tables

Data tables from Gherkin can be accessed by using the `DataTable` object as the last parameter in a step definition.

- Java
- Kotlin
- Scala
- JavaScript

Depending on the table shape, the following collections can be also used as the last parameter in a step definition. This conversion is done by Cucumber.

```java
List<List<String>> table
List<Map<String, String>> table
Map<String, String> table
Map<String, List<String>> table
Map<String, Map<String, String>> table
```

In addition to collections of `String`, `Integer`, `Float`, `BigInteger` and `BigDecimal`. `Byte`, `Short`, `Long` and `Double` are also supported by Cucumber. By registering a data table type it is also possible to support other types. See [cucumber-jvm data-table-type](https://github.com/cucumber/cucumber-jvm/tree/main/cucumber-java#data-table-type) for more.

The simplest way to pass a list of strings to a step definition is to use a data table:

```markdown
Given the following animals:
| cow   |
| horse |
| sheep |
```

- Java
- Kotlin
- Scala
- JavaScript

Declare the argument as a `List<String>` but don't define any capture group in the expression.

Annotated method style:

```java
@Given("the following animals:")
public void the_following_animals(List<String> animals) {
}
```

In this case, the `DataTable` is automatically flattened to a list of strings by Cucumber (using `DataTable.asList(String.class)`) before invoking the step definition.

## Steps

A step is analogous to a method call or function invocation.

For example:

```markdown
Given I have 93 cucumbers in my belly
```

In this step, you're "calling" the above step definition with one argument: the value `93`.

Steps are declared in your `*.feature` files.

### Matching steps

1. Cucumber matches a step against a step definition's `Regexp`
2. Cucumber gathers any capture groups or variables
3. Cucumber passes them to the step definition's method and executes it

Recall that step definitions start with a [preposition](https://www.merriam-webster.com/dictionary/given) or an [adverb](https://www.merriam-webster.com/dictionary/when) (**`Given`**, **`When`**, **`Then`**, **`And`**, **`But`**).

All step definitions are loaded (and defined) before Cucumber starts to execute the plain text in the feature file.

Once execution begins, for each step, Cucumber will look for a registered step definition with a matching `Regexp`. If it finds one, it will execute it, passing all capture groups and variables from the Regexp as arguments to the method.

The specific preposition/adverb used has **no** significance when Cucumber is registering or looking up step definitions.

Also, check out [multiline step arguments](https://cucumber.io/docs/gherkin/reference#step-arguments) for more info on how to pass entire tables or bigger strings to your step definitions.

### Step results

Each step can have one of the following results:

#### Success

When Cucumber finds a matching step definition it will execute it. If the block in the step definition doesn't raise an error, the step is marked as successful (green). Anything you `return` from a step definition has no significance whatsoever.

#### Undefined

When Cucumber can't find a matching step definition, the step gets marked as undefined (yellow), and all subsequent steps in the scenario are skipped.

#### Pending

When a step definition's method invokes the `pending` method, the step is marked as pending (yellow, as with `undefined` ones), indicating that you have work to do.

#### Failed Steps

When a step definition's method is executed and raises an error, the step is marked as failed (red). What you return from a step definition has no significance whatsoever.

Returning `null`, `false` or some other falsy value in your programming language will **not** cause a step definition to fail.

#### Skipped

Steps that follow `undefined`, `pending`, or `failed` steps are never executed, even if there is a matching step definition. These steps are marked as skipped (cyan).

#### Ambiguous

Step definitions have to be unique for Cucumber to know what to execute. If more than one step definition is matched for the same step, Cucucmber can't resolve the ambiguity on its own. The behaviour varies a bit between implementations:

## Hooks

Hooks are blocks of code that can run at various points in the Cucumber execution cycle. They are typically used for setup and teardown of the environment before and after each scenario.

Where a hook is defined has no impact on what scenarios or steps it is run for. If you want more fine-grained control, you can use [conditional hooks](#conditional-hooks).

### Scenario hooks

Scenario hooks run for every scenario.

#### Before

`Before` hooks run before the first step of each scenario.

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@Before
public void doSomethingBefore() {
}
```

Lambda style:

```java
Before(() -> {
});
```

> [!-success] -success
> Think twice before you use `Before`
> 
> Whatever happens in a `Before` hook is invisible to people who only read the features. You should consider using a [background](https://cucumber.io/docs/gherkin/reference#background) as a more explicit alternative, especially if the setup should be readable by non-technical people. Only use a `Before` hook for low-level logic such as starting a browser or deleting data from a database.

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

You can specify an explicit order for hooks if you need to.

Annotated method style:

```java
@Before(order = 10)
public void doSomething(){
    // Do something before each scenario
}
```

Lambda style:

```java
Before(10, () -> {
    // Do something before each scenario
});
```

#### After

`After` hooks run after the last step of each scenario, even when the step result is `failed`, `undefined`, `pending`, or `skipped`.

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@After
public void doSomethingAfter(Scenario scenario){
    // Do something after after scenario
}
```

Lambda style:

```java
After((Scenario scenario) -> {
});
```

The `scenario` parameter is optional. If you use it, you can inspect the status of the scenario.

For example, you can take a screenshot for failed scenarios and embed them in Cucumber's report(s); see the [browser automation page](https://cucumber.io/docs/guides/browser-automation/#screenshot-on-failure) for an example on how to do so.

#### Around

> [!-info] -info
> Ruby only
> 
> This section is only applicable to the Ruby implementation of Cucumber.

`Around` hooks will run "around" a scenario. This can be used to wrap the execution of a scenario in a block. The `Around` hook receives a `Scenario` object and a block (`Proc`) object. The scenario will be executed when you invoke `block.call`.

The following example will cause scenarios tagged with `@fast` to fail if the execution takes longer than 0.5 seconds:

```ruby
Around('@fast') do |scenario, block|
  Timeout.timeout(0.5) do
    block.call
  end
end
```

### Step hooks

Step hooks are invoked before and after a step. The hooks have "invoke around" semantics, meaning that if a `BeforeStep` hook is executed the `AfterStep` hooks will also be executed regardless of the result of the step. If a step did not pass, the following step and its hooks will be skipped.

#### BeforeStep

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@BeforeStep
public void doSomethingBeforeStep(Scenario scenario){
}
```

Lambda style:

```java
BeforeStep((Scenario scenario) -> {

});
```

#### AfterStep

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@AfterStep
public void doSomethingAfterStep(Scenario scenario){
}
```

Lambda style:

```java
AfterStep((Scenario scenario) -> {
});
```

### Conditional hooks

Hooks can be conditionally selected for execution based on the tags of the scenario. To run a particular hook only for certain scenarios, you can associate a hook with a [tag expression](#tag-expressions).

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@After("@browser and not @headless")
public void doSomethingAfter(Scenario scenario){
}
```

Lambda style:

```java
After("@browser and not @headless", (Scenario scenario) -> {
});
```

See more documentation on [tags](#tags).

### Global hooks

Global hooks will run once before any scenario is run or after all scenarios have been run.

#### BeforeAll

Each `BeforeAll` hook will run before any scenario is run.

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@BeforeAll
public static void beforeAll() {
    // Runs before all scenarios
}
```

#### AfterAll

Each `AfterAll` hook will run after all scenarios have been executed.

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Annotated method style:

```java
@AfterAll
public static void afterAll() {
    // Runs after all scenarios
}
```

### InstallPlugin

> [!-info] -info
> Ruby only
> 
> This section is only applicable to the Ruby implementation of Cucumber.

You may provide an `InstallPlugin` hook that will be run after Cucumber has been configured. The block you provide will be passed on to Cucumber's configuration (an instance of `Cucumber::Cli::Configuration`), and a wrapper to some cucumber internals as a registry.

```ruby
InstallPlugin do |config, registry|
  puts "Features dwell in #{config.feature_dirs}"
end
```

This hook will run *only once*: after support has been loaded, and before any features are loaded.

You can use this hook to extend Cucumber. For example, you could affect how features are loaded, or register custom formatters programmatically. [cucumber-wire](https://github.com/cucumber/cucumber-ruby-wire) is a good example of how to use InstallPlugin and what a Cucumber plugin can do.

Tags are a great way to organise your features and scenarios.

They can be used for two purposes:

- [Running a subset of scenarios](#running-a-subset-of-scenarios)
- [Restricting hooks to a subset of scenarios](#conditional-hooks)

Consider the following example:

```markdown
@billing
Feature: Verify billing

  @important
  Scenario: Missing product description
    Given hello

  Scenario: Several products
    Given hello
```

A feature or scenario can have as many tags as you like. Separate them with spaces:

```markdown
@billing @bicker @annoy
Feature: Verify billing
```

Tags can be placed above the following Gherkin elements:

- `Feature`
- `Rule`
- `Scenario`
- `Scenario Outline`
- `Examples`

In `Scenario Outline`, you can use tags on different sets of examples like below:

```markdown
Scenario Outline: Steps will run conditionally if tagged
  Given user is logged in
  When user clicks <link>
  Then user will be logged out

  @mobile
  Examples:
    | link                  |
    | logout link on mobile |

  @desktop
  Examples:
    | link                   |
    | logout link on desktop |
```

It is *not* possible to place tags above `Background` or steps (`Given`, `When`, `Then`, `And` and `But`).

### Tag inheritance

Tags are inherited by child elements. So, tags that are placed above a `Feature` will be inherited by `Rule`, `Scenario`, `Scenario Outline`, or `Examples`. And similarly tags that are placed above a `Scenario Outline` will be inherited by `Examples`.

### Running a subset of scenarios

You can tell Cucumber to only run scenarios with a particular tag:

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

For JUnit 5 see the [cucumber-junit-platform-engine documentation](https://github.com/cucumber/cucumber-jvm/tree/main/cucumber-junit-platform-engine#tags)

For JUnit 4 and TestNG using a JVM system property:

```shell
mvn test -Dcucumber.filter.tags="@smoke and @fast"
```

Or an environment variable:

```shell
# Linux / OS X:
CUCUMBER_FILTER_TAGS="@smoke and @fast" mvn test

# Windows:
set CUCUMBER_FILTER_TAGS="@smoke and @fast"
mvn test
```

Or annotating your JUnit 4/TestNG runner class:

```java
@CucumberOptions(tags = "@smoke and @fast")
```

### Ignoring a subset of scenarios

You can tell Cucumber to ignore scenarios with a particular tag:

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

By annotating your JUnit 4/TestNG runner class:

```java
@CucumberOptions(tags = "not @smoke")
```

> [!-success] -success
> Filtering by line
> 
> Another way to run a subset of scenarios is to use the `file.feature:line` pattern or the `--scenario` option.

### Tag expressions

A tag expression is an *infix boolean expression*. Below are some examples:

| Expression | Description |
| --- | --- |
| `@fast` | Scenarios tagged with `@fast` |
| `@wip and not @slow` | Scenarios tagged with `@wip` that aren't also tagged with `@slow` |
| `@smoke and @fast` | Scenarios tagged with both `@smoke` and `@fast` |
| `@gui or @database` | Scenarios tagged with either `@gui` or `@database` |

For even more advanced tag expressions you can use parenthesis for clarity, or to change operator precedence:

```markdown
(@smoke or @ui) and (not @slow)
```

### Using tags for documentation

Your imagination is the only limitation when it comes to using tags for documentation.

#### Link to other documents

Tags can refer to IDs in external systems such as requirement management tools, issue trackers or test management tools:

```markdown
@BJ-x98.77 @BJ-z12.33
Feature: Convert transaction
```

You can use a custom Cucumber reporting plugin that will turn tags into links pointing to documents in your external tool.

#### Development process

Another creative way to use tags is to keep track of where in the development process a certain feature is:

```markdown
@qa_ready
Feature: Index projects
```

### @wip

> [!-info] -info
> Rails only
> 
> This section is only applicable to the Rails implementation of Cucumber.

As distributed, Cucumber-Rails builds a Rake task that recognizes the `@wip` tag. However, any string may be used as a tag and any scenario or entire feature can have multiple tags associated with it.

The default profile contained in the distributed `config/cucumber.yml` contains these lines:

```yaml
<%
.  .  .
std_opts = "--format #{ENV['CUCUMBER_FORMAT'] || 'progress'} --strict --tags ~@wip"
%>
default: <%= std_opts %> features
.  .  .
```

Note the trailing option `--tags ~@wip`. Cucumber provides for negating tags by prefacing the `--tags` argument with a tilde character (**`~`**). This tells Cucumber to not process features and scenarios with this tag. If you do not specify a different profile (`cucumber -p profilename`), then the default profile will be used. If the default profile is used, then the `--tags ~@wip` will cause Cucumber to skip any scenario with this tag. This will override the `--tags=@authen` option passed in the command line, and so you will see this:

```shell
cucumber --tags=@authentication
Using the default profile...

0 scenarios
0 steps
0m0.000s
```

Since version 0.6.0, one can no longer overcome this default setting by adding the `--tags=@wip` to the Cucumber argument list on the command line, because now all `--tags` options are combined with "and" logic. Thus, the combination of `--tags @wip` **and** `--tags ~@wip` fails everywhere.

You either must create a special profile in `config/cucumber.yml` to deal with this, or alter the default profile to suit your needs.

The `@wip` tags are a special case. If any scenario tagged as `@wip` passes all of its steps without error, and the `--wip` option is also passed, Cucumber reports the run as failing (because Scenarios that are marked as a work in progress are not *supposed* to pass!)

Note as well that the `--strict` and `--wip` options are mutually exclusive.

The number of occurrences of a particular tag in your features may be controlled by appending a colon followed by a number to the end of the tag name passed to the `--tags` option, like so:

```shell
cucumber --tags=@wip:3 features/log\*
```

The existence of more than the specified number of occurrences of that tag in all the features that are exercised during a particular Cucumber run will produce a warning message. If the `--strict` option is passed as well, as is the case with the default profile, then instead of a warning the run will fail.

Limiting the number of occurrences is commonly used in conjunction with the `@wip` tag to restrict the number of unspecified scenarios to manageable levels. Those following [Kanban](https://en.wikipedia.org/wiki/kanban) or [Lean Software Development](https://en.wikipedia.org/wiki/Lean_software_development) based methodologies will find this useful.

## Running Cucumber

It is possible to [configure](https://cucumber.io/docs/cucumber/configuration) how Cucumber should run features.

### From the command line

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

The *Command-Line Interface Runner (CLI Runner)* is an executable Java class that can be run from the command-line.

```markdown
java io.cucumber.core.cli.Main
```

Note that you will need to add the `cucumber-core` jar and all of its transitive dependencies to your classpath, in addition to the location of your compiled.class files. You can find these jars in [Maven Central](https://mvnrepository.com/repos/central).

You will also need to provide the CLI with your step definitions via the `--glue` option followed by its package name, and the filepath of your feature file(s).

For example:

```shell
java -cp "path/to/each/jar:path/to/compiled/.class/files" io.cucumber.core.cli.Main /path/to/your/feature/files --glue hellocucumber --glue anotherpackage
```

Alternatively if you are using a Maven project, you can run the CLI using the [Exec Maven](https://www.mojohaus.org/exec-maven-plugin/) plugin:

```shell
mvn exec:java                                  \
    -Dexec.classpathScope=test                 \
    -Dexec.mainClass=io.cucumber.core.cli.Main \
    -Dexec.args="/path/to/your/feature/files --glue hellocucumber --glue anotherpackage"
```

You can also run features using a [build tool](https://cucumber.io/docs/tools#build-tools) or an [IDE](https://cucumber.io/docs/tools#ides).

### With test runners

#### JUnit 5 (for JVM)

See the [cucumber-junit-platform-engine documentation](https://github.com/cucumber/cucumber-jvm/tree/main/cucumber-junit-platform-engine#configuration-options) for more information.

#### JUnit 4 (for JVM)

To use JUnit to execute Cucumber scenarios add the `cucumber-junit` dependency to your pom.

```xml
<dependencies>
  [...]
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-junit</artifactId>
        <version>${cucumber.version}</version>
        <scope>test</scope>
    </dependency>
  [...]
</dependencies>
```

Note that `cucumber-junit` is based on JUnit 4. If you're using JUnit 5, use the [cucumber-junit-platform-engine](https://github.com/cucumber/cucumber-jvm/tree/main/cucumber-junit-platform-engine) or include `junit-vintage-engine` dependency, as well. For more information, please refer to [JUnit 5 documentation](https://junit.org/junit5/docs/current/user-guide/#migrating-from-junit4-running)

Create an empty class that uses the Cucumber JUnit runner:

- Java
- Kotlin
- Scala

```java
package com.example;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
@CucumberOptions()
public class RunCucumberTest {
}
```

This will execute all scenarios in same package as the runner, by default glue code is also assumed to be in the same package.

The `@CucumberOptions` annotation can be used to provide [additional configuration](#list-configuration-options) to the runner.

##### Using plugins

For example if you want to tell Cucumber to use the two formatter plugins `pretty` and `html`, you can specify it like this:

```java
@CucumberOptions(plugin = {"pretty", "html:target/cucumber.html"})
```

Or if you want to tell Cucumber to print code snippets for missing step definitions use the `summary` plugin, you can specify it like this:

```java
@CucumberOptions(plugin = {"pretty", "summary"}, snippets = SnippetType.CAMELCASE)
```

The default option for `snippets` is `UNDERSCORE`. This settings can be used to specify the way code snippets will be created by Cucumber.

##### Performing a dry-run

For example if you want to check whether all feature file steps have corresponding step definitions, you can specify it like this:

```java
@CucumberOptions(dryRun=true)
```

The default option for `dryRun` is `false`.

##### Formatting console output

For example if you want console output from Cucumber in a readable format, you can specify it like this:

```java
@CucumberOptions(monochrome=true)
```

The default option for `monochrome` is `false`.

##### Select scenarios using tags

For example if you want to tell Cucumber to only run the scenarios specified with specific tags, you can specify it like this:

```java
@CucumberOptions(tags = "@foo and not @bar")
```

##### Specify an object factory

For example if you are using Cucumber with a DI framework and want to use a custom object factory, you can specify it like this:

```java
@CucumberOptions(objectFactory = FooFactory.class)
```

The default option for `objectFactory` is to use the default object factory. Additional information about using custom object factories can be found [here](https://cucumber.io/docs/cucumber/state/#the-cucumber-object-factory)

There are additional options available in the `@CucumberOptions` annotation.

Usually, the test class will be empty. You can, however, specify several JUnit rules.

> [!-warning] -warning
> JUnit annotations
> 
> Cucumber supports JUnits `@ClassRule`, `@BeforeClass` and `@AfterClass` annotations. These will be executed before and after all scenarios. Using them is not recommended, as it limits the portability between different runners; they may not execute correctly when using the command line, [IntelliJ IDEA](https://www.jetbrains.com/help/idea/cucumber.html) or [Cucumber-Eclipse](https://github.com/cucumber/cucumber-eclipse). Instead, it is recommended to use Cucumber's `Before` and `After` [hooks](#hooks).

The Cucumber runner acts like a suite of a JUnit tests. As such other JUnit features such as Categories, Custom JUnit Listeners and Reporters can all be expected to work.

For more information on JUnit, see the [JUnit website](https://www.junit.org/)

### Options

Cucumber provides several options that can be passed via the command-line or other mechanisms.

- Java
- Kotlin
- Scala
- JavaScript
- Ruby

Pass the `--help` option to print out all the available configuration options:

```shell
java io.cucumber.core.cli.Main --help
```

Cucumber will in order of precedence parse properties from system properties, environment variables and the `cucumber.properties` file.

Note that options provided by `@CucumberOptions` take precedence over the properties file and CLI arguments take precedence over all.

Note that the `cucumber-junit-platform-engine` is provided with properties by the Junit Platform rather than Cucumber. See [junit-platform-engine Configuration Options](https://github.com/cucumber/cucumber-jvm/tree/main/cucumber-junit-platform-engine#configuration-options) for more information.

For example, if you are using Maven and want to run a subset of scenarios tagged with `@smoke`:

```shell
mvn test -Dcucumber.filter.tags="@smoke"
```

Supported properties are:

```markdown
cucumber.ansi-colors.disabled=  # true or false. default: false
cucumber.execution.dry-run=     # true or false. default: false
cucumber.execution.limit=       # number of scenarios to execute (CLI only).
cucumber.execution.order=       # lexical, reverse, random or random:[seed] (CLI only). default: lexical
cucumber.execution.wip=         # true or false. default: false.
cucumber.features=              # comma separated paths to feature files. example: path/to/example.feature, path/to/other.feature
cucumber.filter.name=           # regex. example: .*Hello.*
cucumber.filter.tags=           # tag expression. example: @smoke and not @slow
cucumber.glue=                  # comma separated package names. example: com.example.glue
cucumber.plugin=                # comma separated plugin strings. example: pretty, json:path/to/report.json
cucumber.object-factory=        # object factory class name. example: com.example.MyObjectFactory
cucumber.snippet-type=          # underscore or camelcase. default: underscore
```

Note that the filter options `cucumber.filter.name` and `cucumber.filter.tags` are combined using an `and` operation. In other words, both expressions need to match.