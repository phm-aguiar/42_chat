---
title: "10-Minute Tutorial"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/10-minute tutorial.md"
created: "2026-06-21"
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
In this quick tutorial you will learn how to:

- Install Cucumber
- Write your first scenario using the Gherkin syntax
- Write your first step definition in Java
- Run Cucumber
- Learn the basic workflow of Behaviour-Driven Development (BDD)

We'll use Cucumber to develop a small library that can figure out whether it's Friday yet.

- A basic understanding of your chosen programming language and its standard tooling
- Some experience using a terminal
- Some experience using a text editor

Before we begin, you'll need the following:

- [Java SE](https://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html)
- A build tool. You can choose between:
- \- version 3.3.1 or higher
- [IntelliJ IDEA](https://www.jetbrains.com/idea/) (which will be used in this tutorial)
- [IntelliJ IDEA Cucumber for Java plugin](https://plugins.jetbrains.com/plugin/7212-cucumber-for-java)
- [Eclipse](https://www.eclipse.org/) (a good alternative if you don't use IntelliJ IDEA)
- [Cucumber Eclipse](https://cucumber.github.io/cucumber-eclipse/)

## Create an empty Cucumber project

We'll start by creating a new project directory with the `cucumber-archetype` Maven plugin. Open a terminal, go to the directory where you want to create your project, and run the following command:

```shell
mvn archetype:generate                     \
"-DarchetypeGroupId=io.cucumber"           \
"-DarchetypeArtifactId=cucumber-archetype" \
"-DarchetypeVersion=7.34.3"                \
"-DgroupId=hellocucumber"                  \
"-DartifactId=hellocucumber"               \
"-Dpackage=hellocucumber"                  \
"-Dversion=1.0.0-SNAPSHOT"                 \
"-DinteractiveMode=false"
```

You should get something like the following result:

```shell
[INFO] Project created from Archetype in dir: [directory where you created the project]/cucumber
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```

Change into the directory that was just created by running the following command:

```shell
cd hellocucumber
```

Open the project in IntelliJ IDEA:

- **File -> Open... -> (Select the pom.xml)**
- Select **Open as Project**

You now have a small project with Cucumber installed.

## Verify your installation

To make sure everything works together correctly, let's run Cucumber.

```shell
mvn test
```

You should see something like the following:

```shell
-------------------------------------------------------
T E S T S
-------------------------------------------------------

Tests run: 0, Failures: 0, Errors: 0, Skipped: 0

Results :

Tests run: 0, Failures: 0, Errors: 0, Skipped: 0

[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```

Cucumber's output is telling us that it didn't find anything to run.

## Write a scenario

When we do Behaviour-Driven Development with Cucumber we use *concrete examples* to specify *what* we want the software to do. Scenarios are written *before* production code. They start their life as an *executable specification*. As the production code emerges, scenarios take on a role as *living documentation* and *automated tests*.

> [!-success] -success
> Example Mapping
> 
> Try running an [Example Mapping](https://cucumber.io/docs/bdd/example-mapping) workshop in your team to design examples together.

In Cucumber, an example is called a [scenario](https://cucumber.io/docs/gherkin/reference#example). Scenarios are defined in `.feature` files, which are stored in the `src/test/resources/hellocucumber` directory (or a subdirectory).

One concrete example would be that *Sunday isn't Friday*.

Create an empty file called `src/test/resources/hellocucumber/is_it_friday_yet.feature` with the following content:

```markdown
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday
    Given today is Sunday
    When I ask whether it's Friday yet
    Then I should be told "Nope"
```

The first line of this file starts with the keyword `Feature:` followed by a name. It's a good idea to use a name similar to the file name.

The second line is a brief description of the feature. Cucumber does not execute this line because it's documentation.

The fourth line, `Scenario: Sunday is not Friday` is a [scenario](https://cucumber.io/docs/gherkin/reference#example), which is a *concrete example* illustrating how the software should behave.

The last three lines starting with `Given`, `When` and `Then` are the [steps](https://cucumber.io/docs/gherkin/reference#steps) of our scenario. This is what Cucumber will execute.

## See scenario reported as undefined

Now that we have a scenario, we can ask Cucumber to execute it.

```shell
mvn test
```

Cucumber is telling us we have one `undefined` scenario and three `undefined` steps. It's also suggesting some snippets of code that we can use to *define* these steps:

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest

Scenario: Sunday isn't Friday        # hellocucumber/is_it_friday_yet.feature:4
  Given today is Sunday
  When I ask whether it's Friday yet
  Then I should be told "Nope"
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.15 s <<< FAILURE! - in hellocucumber.RunCucumberTest
[ERROR] Is it Friday yet?.Sunday isn't Friday  Time elapsed: 0.062 s  <<< ERROR!
io.cucumber.junit.platform.engine.UndefinedStepException:
The step 'today is Sunday' and 2 other step(s) are undefined.
You can implement these steps using the snippet(s) below:

@Given("today is Sunday")
public void today_is_sunday() {
    // Write code here that turns the phrase above into concrete actions
    throw new io.cucumber.java.PendingException();
}
@When("I ask whether it's Friday yet")
public void i_ask_whether_it_s_friday_yet() {
    // Write code here that turns the phrase above into concrete actions
    throw new io.cucumber.java.PendingException();
}
@Then("I should be told {string}")
public void i_should_be_told(String string) {
    // Write code here that turns the phrase above into concrete actions
    throw new io.cucumber.java.PendingException();
}
```

Copy each of the three snippets for the undefined steps and paste them into `src/test/java/hellocucumber/StepDefinitions.java`.

## See scenario reported as pending

Run Cucumber again. This time the output is a little different:

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday        # hellocucumber/is_it_friday_yet.feature:4
    Given today is Sunday              # StepDefinitions.today_is_Sunday()
      io.cucumber.java.PendingException: TODO: implement me
    at hellocucumber.StepDefinitions.today_is_Sunday(StepDefinitions.java:14)
    at ?.today is Sunday(classpath:hellocucumber/is_it_friday_yet.feature:5)

    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"       # StepDefinitions.i_should_be_told(String)

Pending scenarios:
hellocucumber/is_it_friday_yet.feature:4 # Sunday isn't Friday

1 Scenarios (1 pending)
3 Steps (2 skipped, 1 pending)
0m0.188s

io.cucumber.java.PendingException: TODO: implement me
    at hellocucumber.StepDefinitions.today_is_Sunday(StepDefinitions.java:13)
    at ?.today is Sunday(classpath:hellocucumber/is_it_friday_yet.feature:5)
```

Cucumber found our step definitions and executed them. They are currently marked as *pending*, which means we need to make them do something useful.

## See scenario reported as failing

The next step is to do what the comments in the step definitions is telling us to do:

> Write code here that turns the phrase above into concrete actions

Try to use the same words in the code as in the steps.

> [!-success] -success
> Ubiquitous language
> 
> If the words in your steps originated from conversations during an [Example Mapping](https://cucumber.io/docs/bdd/example-mapping) session, you're building a [Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html), which we believe is a great way to make your production code and tests more understandable and easier to maintain.

Change your step definition code to this:

```java
package hellocucumber;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import static org.assertj.core.api.Assertions.assertThat;

class IsItFriday {
    static String isItFriday(String today) {
        return null;
    }
}

public class StepDefinitions {
    private String today;
    private String actualAnswer;

    @Given("today is Sunday")
    public void today_is_Sunday() {
        today = "Sunday";
    }

    @When("I ask whether it's Friday yet")
    public void i_ask_whether_it_s_Friday_yet() {
        actualAnswer = IsItFriday.isItFriday(today);
    }

    @Then("I should be told {string}")
    public void i_should_be_told(String expectedAnswer) {
        assertThat(actualAnswer).isEqualTo(expectedAnswer);
    }
}
```

Run Cucumber again:

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday        # hellocucumber/is_it_friday_yet.feature:4
    Given today is Sunday              # StepDefinitions.today_is_Sunday()
    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"       # StepDefinitions.i_should_be_told(String)
      org.opentest4j.AssertionFailedError:
      expected: "Nope"
       but was: null
          at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
          at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
          at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
          at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:499)
          at io.cucumber.skeleton.StepDefinitions.I_have_cukes_in_my_belly(StepDefinitions.java:12)
          at ✽.I have 42 cukes in my belly(classpath:io/cucumber/skeleton/belly.feature:4)

Failed scenarios:
hellocucumber/is_it_friday_yet.feature:4 # Sunday isn't Friday

1 Scenarios (1 failed)
3 Steps (1 failed, 2 passed)
0m0.404s
```

That's progress! The first two steps are passing, but the last one is failing.

## See scenario reported as passing

Let's do the minimum we need to make the scenario pass. In this case, that means making our method return `Nope`:

```java
static String isItFriday(String today) {
    return "Nope";
}
```

Run Cucumber again:

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday        # hellocucumber/is_it_friday_yet.feature:4
    Given today is Sunday              # StepDefinitions.today_is_Sunday()
    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"       # StepDefinitions.i_should_be_told(String)

1 Scenarios (1 passed)
3 Steps (3 passed)
0m0.255s
```

Congratulations! You've got your first green Cucumber scenario.

## Add another failing test

The next thing to test for would be that we also get the correct result when it *is* Friday.

Update the `is_it_friday_yet.feature` file:

```markdown
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday
    Given today is Sunday
    When I ask whether it's Friday yet
    Then I should be told "Nope"

  Scenario: Friday is Friday
    Given today is Friday
    When I ask whether it's Friday yet
    Then I should be told "TGIF"
```

We'll need to add a step definition to set `today` to "Friday":

```java
@Given("today is Friday")
public void today_is_Friday() {
    today = "Friday";
}
```

When we run this test, it will fail.

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday        # hellocucumber/is_it_friday_yet.feature:4
    Given today is Sunday              # StepDefinitions.today_is_Sunday()
    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"       # StepDefinitions.i_should_be_told(String)

  Scenario: Friday is Friday           # hellocucumber/is_it_friday_yet.feature:9
    Given today is Friday              # StepDefinitions.today_is_Friday()
    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "TGIF"       # StepDefinitions.i_should_be_told(String)
      org.opentest4j.AssertionFailedError:
        expected: "TGIF"
         but was: "Nope"
            at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
            at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
            at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
            at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:499)
            at io.cucumber.skeleton.StepDefinitions.I_have_cukes_in_my_belly(StepDefinitions.java:12)
            at ✽.I have 42 cukes in my belly(classpath:io/cucumber/skeleton/belly.feature:4)

Failed scenarios:
hellocucumber/is_it_friday_yet.feature:9 # Friday is Friday

2 Scenarios (1 failed, 1 passed)
6 Steps (1 failed, 5 passed)
0m0.085s

org.opentest4j.AssertionFailedError:
  expected: "TGIF"
   but was: "Nope"
      at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
      at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
      at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
      at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:499)
      at io.cucumber.skeleton.StepDefinitions.I_have_cukes_in_my_belly(StepDefinitions.java:12)
      at ✽.I have 42 cukes in my belly(classpath:io/cucumber/skeleton/belly.feature:4)
```

That is because we haven't implemented the logic yet! Let's do that next.

## Make it pass

We should update our statement to actually evaluate whether or not `today` is equal to `"Friday"`.

```java
static String isItFriday(String today) {
    return "Friday".equals(today) ? "TGIF" : "Nope";
}
```

Run Cucumber again:

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario: Sunday isn't Friday        # hellocucumber/is_it_friday_yet.feature:4
    Given today is Sunday              # StepDefinitions.today_is_Sunday()
    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"       # StepDefinitions.i_should_be_told(String)

  Scenario: Friday is Friday           # hellocucumber/is_it_friday_yet.feature:9
    Given today is Friday              # StepDefinitions.today_is_Friday()
    When I ask whether it's Friday yet # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "TGIF"       # StepDefinitions.i_should_be_told(String)

2 Scenarios (2 passed)
6 Steps (6 passed)
0m0.255s
```

## Using variables and examples

So, we all know that there are more days in the week than just Sunday and Friday. Let's update our scenario to use variables and evaluate more possibilities. We'll use variables and examples to evaluate Friday, Sunday, and anything else!

Update the `is_it_friday_yet.feature` file. Notice how we go from `Scenario` to `Scenario Outline` when we start using multiple `Examples`.

```markdown
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario Outline: Today is or is not Friday
    Given today is "<day>"
    When I ask whether it's Friday yet
    Then I should be told "<answer>"

  Examples:
    | day            | answer |
    | Friday         | TGIF   |
    | Sunday         | Nope   |
    | anything else! | Nope   |
```

We need to replace the step definitions for `today is Sunday` and `today is Friday` with one step definition that takes the value of `<day>` as a String. Update the step definitions as follows:

```java
package hellocucumber;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import static org.assertj.core.api.Assertions.assertThat;

class IsItFriday {
    static String isItFriday(String today) {
        return "Friday".equals(today) ? "TGIF" : "Nope";
    }
}

public class Stepdefs {
    private String today;
    private String actualAnswer;

    @Given("today is {string}")
    public void today_is(String today) {
        this.today = today;
    }

    @When("I ask whether it's Friday yet")
    public void i_ask_whether_it_s_Friday_yet() {
        actualAnswer = IsItFriday.isItFriday(today);
    }

    @Then("I should be told {string}")
    public void i_should_be_told(String expectedAnswer) {
        assertThat(actualAnswer).isEqualTo(expectedAnswer);
    }
}
```

Run Cucumber again:

```shell
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running hellocucumber.RunCucumberTest
Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Scenario Outline: Today is or is not Friday # hellocucumber/is_it_friday_yet.feature:4
    Given today is "<day>"
    When I ask whether it's Friday yet
    Then I should be told "<answer>"

    Examples:

  Scenario Outline: Today is or is not Friday # hellocucumber/is_it_friday_yet.feature:11
    Given today is "Friday"                   # StepDefinitions.today_is(String)
    When I ask whether it's Friday yet        # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "TGIF"              # StepDefinitions.i_should_be_told(String)

  Scenario Outline: Today is or is not Friday # hellocucumber/is_it_friday_yet.feature:12
    Given today is "Sunday"                   # StepDefinitions.today_is(String)
    When I ask whether it's Friday yet        # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"              # StepDefinitions.i_should_be_told(String)

  Scenario Outline: Today is or is not Friday # hellocucumber/is_it_friday_yet.feature:13
    Given today is "anything else!"           # StepDefinitions.today_is(String)
    When I ask whether it's Friday yet        # StepDefinitions.i_ask_whether_it_s_Friday_yet()
    Then I should be told "Nope"              # StepDefinitions.i_should_be_told(String)

3 Scenarios (3 passed)
9 Steps (9 passed)
0m0.255s
```

## Refactoring

Now that we have working code, we should do some refactoring:

- We should move the `isItFriday` method out from the test code into production code.
- We could at some point extract helper methods from our step definition, for methods we use in several places.

## Summary

In this brief tutorial you've seen how to install Cucumber, how to follow the BDD process to develop a method, and how to use that method to evaluate multiple scenarios!