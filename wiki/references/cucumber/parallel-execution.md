---
title: "Parallel Execution"
category: references
tags:
  - cucumber
  - bdd
source: "wiki/_raw/Parallel execution.md"
created: "2026-06-21"
rag_score: 0.5
updated: "2026-06-21"
lifecycle: raw
lifecycle_reason: "ingested from _raw/ Cucumber/BDD clippings"
---
> [!-info] -info
> JVM only
> 
> This page is only applicable to the JVM implementation of Cucumber.

Cucumber-JVM allows parallel execution across multiple threads since version 4.0.0.

There are several options to incorporate this built-in feature in a Cucumber project. You can do so using:

For each of these options, this tutorial will look at the project setup, configuration settings and execution commands.

## JUnit 5

Cucumber Scenarios can be executed in parallel using the **JUnit Platform**.

See the [cucumber-junit-platform-engine documentation](https://github.com/cucumber/cucumber-jvm/tree/main/cucumber-junit-platform-engine) for details.

## JUnit 4

Cucumber can be executed in parallel using **JUnit and Maven test execution plugins**. In JUnit the **feature files are run in parallel rather than scenarios**, which means **all the scenarios in a feature file will be executed by the same thread**. You can use either Maven Surefire or Failsafe plugin to execute the runners.

- Create a Maven project in your favorite IDE using the [cucumber-archetype](https://cucumber.io/docs/guides/10-minute-tutorial/#create-an-empty-cucumber-project) or by adding Cucumber dependencies to the POM as detailed [here](https://cucumber.io/docs/installation/java#maven) and Junit dependencies [here](https://cucumber.io/docs/cucumber/checking-assertions#junit).
- Create a **parallel** folder (or any other name) in `src/test/resources` path and add the two feature files (`scenarios.feature` and `scenario-outlines.feature`) inside it.
```markdown
Feature: Scenarios feature file

  Scenario: Scenario Number One
    Given Step from 'Scenario 1' in 'scenarios' feature file

  Scenario: Scenario Number Two
    Given Step from 'Scenario 2' in 'scenarios' feature file
```
```markdown
Feature: Scenario Outlines feature file

  Scenario Outline: <scen_out_row_num>
    Given Step from '<scen_out_row_num>' in 'scenario-outlines' feature file

    Examples: 
      | scen_out_row_num       |
      | Scenario Outline Row 1 |
      | Scenario Outline Row 2 |
```
- Add the **step definition class** to the `parallel` package (same name as folder above for automatic pickup by runner) in `src/test/java` folder.
```java
package parallel;

import io.cucumber.java.BeforeStep;
import io.cucumber.java.en.Given;

public class StepDefinitions {

    @Given("Step from {string} in {string} feature file")
    public void step(String scenario, String file) {
        System.out.format("Thread ID - %2d - %s from %s feature file.\n",
        Thread.currentThread().getId(), scenario,file);
    }
}
```
- Add a cucumber **runner** using the `RunWith` annotation in the `parallel` package (same name as step definition package) in the `src/test/java` folder.
```java
package parallel;

import io.cucumber.junit.Cucumber;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
public class RunCucumberTest {
}
```
- Add the **Surefire plugin configuration** to the `build` section to the `POM`.
```shell
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>2.22.0</version>
    <configuration>
        <parallel>methods</parallel>
        <useUnlimitedThreads>true</useUnlimitedThreads>
    </configuration>
</plugin>
```
- Use the Maven `install` or a suitable command to **execute** the `POM`. This should run in parallel threaded mode. You should see a result similar to below. It is important to note that **both the scenarios in the file (`scenarios.feature`) are executed by thread with ID 14**. Similarly **both the rows of the scenario outline in the file (`scenario-outlines.feature`) are executed by thread with ID 13**.
```shell
Thread ID - 13 - Scenario Outline Row 1 from scenario-outlines feature file.
Thread ID - 13 - Scenario Outline Row 2 from scenario-outlines feature file.
Thread ID - 14 - Scenario 1 from scenarios feature file.
Thread ID - 14 - Scenario 2 from scenarios feature file.
```
- To execute using a Maven **Failsafe plugin include the below configuration** in the `build` section to the `POM`. Rename the runner class to `RunCucumberIT`.
```shell
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-failsafe-plugin</artifactId>
    <version>2.22.0</version>
    <executions>
        <execution>
            <goals>
                <goal>integration-test</goal>
                <goal>verify</goal>
            </goals>
            <configuration>
                <parallel>methods</parallel>
                <useUnlimitedThreads>true</useUnlimitedThreads>
            </configuration>
        </execution>
    </executions>
</plugin>
```

To set the thread count to a **specific number** instead of `useUnlimitedThreads` use the below setting.

```shell
<configuration>
    <parallel>methods</parallel>
    <threadCount>4</threadCount>
</configuration>
```

The thread count in the above setting is **4 threads per core**. If you want this to be **4 threads across all cores** set the `perCoreThreadCount` to **false**.

```shell
<configuration>
    <parallel>methods</parallel>
    <threadCount>4</threadCount>
    <perCoreThreadCount>false</perCoreThreadCount>
</configuration>
```

In case of **multiple runners** one can also set the parallel option to `classesAndMethods` or `classes` in addition to `methods`.

```shell
<configuration>
    <parallel>classesAndMethods</parallel>
    useUnlimitedThreads>true</useUnlimitedThreads>
</configuration>
```

## TestNG

Cucumber can be executed in parallel using **TestNG and Maven test execution plugins** by setting the **dataprovider parallel option to true**. In TestNG the **scenarios and rows in a scenario outline are executed in multiple threads**. One can use either Maven Surefire or Failsafe plugin for executing the runners.

- Create a Maven project in your favorite IDE adding Cucumber dependencies to the POM as detailed [here](https://cucumber.io/docs/installation/java#maven) and TestNG dependencies [here](https://cucumber.io/docs/cucumber/checking-assertions/#testng).
- Add the two feature files (`scenarios.feature` and `scenario-outlines.feature`) and **step definition class** as described in the JUnit section.
- Add a cucumber **runner** by **extending** the `AbstractTestNGCucumberTests` class and **overriding the scenarios method** in the `parallel` package (same name as step definition package) in `src/test/java` folder. Set the **parallel option value to true** for the DataProvider annotation.
```java
package parallel;

import org.testng.annotations.DataProvider;
import io.cucumber.testng.AbstractTestNGCucumberTests;

public class RunCucumberTest extends AbstractTestNGCucumberTests{

    @Override
    @DataProvider(parallel = true)
    public Object[][] scenarios() {
        return super.scenarios();
    }
}
```
- Add the Maven **Surefire plugin configuration** to the `build` section of the `POM`.
```shell
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>2.22.0</version>
</plugin>
```
- Use the Maven `install` or a suitable command to **execute the POM**. This should run in parallel thread mode. You should see a result similar to below. The **scenarios and rows of the scenario outlines are executed in different threads**.
```shell
Thread ID - 15 - Scenario Outline Row 2 from scenario-outlines feature file.
Thread ID - 14 - Scenario Outline Row 1 from scenario-outlines feature file.
Thread ID - 16 - Scenario 1 from scenarios feature file.
Thread ID - 17 - Scenario 2 from scenarios feature file.
```
- To execute using a Maven **Failsafe plugin**, setup the `POM` as described in the JUnit section. Remove the `parallel` and `useUnlimitedThreads` settings in the `configuration` part.

The default **thread count of the dataprovider** in parallel mode is **10**. To change this the `dataproviderthreadcount` property needs to be added to the `configuration` section of the Surefire or Failsafe plugin in the `POM`.

```shell
<configuration>
    <properties>
        <property>
            <name>dataproviderthreadcount</name>
            <value>20</value>
        </property>
    </properties>
</configuration>
```

If you have **multiple runners**, set the parallel configuration to `classes` to reduce execution times. In addition the `threadCount` can be set to to the desired value or `useUnlimitedThreads` can be set to true.

```shell
<configuration>
    <parallel>classes</parallel>
    <threadCount>4</threadCount>
</configuration>
```

## CLI

The `Main` class in the `io.cucumber.core.cli` package is used to execute the feature files. You can run this class directly from the command line; in that case, there is no need to create any runner class. The usage options for this class are mentioned [here](https://github.com/cucumber/cucumber-jvm/blob/main/cucumber-core/src/main/resources/io/cucumber/core/options/USAGE.txt). The `--threads` option needs to be set to a value **greater than 1** to run in parallel. When the parallel mode is used, the scenarios and rows in a scenario outline will be run in multiple threads.

Follow the steps below to **execute the command from a terminal**.

- Add the two feature files (`scenarios.feature` and `scenario-outlines.feature`) and **step definition class** as described in the JUnit section.
- Open up a **terminal window** and navigate to the source folder of the project, in this case **parallel**.
- Compile the step definition class. Add the **path to the folder containing cucumber jars to the classpath** using the **\-cp** option.
```shell
javac -cp .;<path to cucumber jar folder>/* ./parallel/StepDefs.java
```
- Execute using the below command.
```shell
java -cp .;<path to cucumber jar folder>/* io.cucumber.core.cli.Main --threads 4 -g parallel parallel
```
- You should get a console output similar to below.
```shell
Thread ID - 11 - Scenario Outline Row 1 from scenario-outlines feature file.
Thread ID - 14 - Scenario 2 from scenarios feature file.
Thread ID - 12 - Scenario Outline Row 2 from scenario-outlines feature file.
Thread ID - 13 - Scenario 1 from scenarios feature file.
```

## Timeline formatter

For a **visual representation** of threads, add the **timeline report** using the `plugin` option of `CucumberOptions` annotation on a JUnit or TestNG runner.

```java
@CucumberOptions(plugin= {"timeline:<report folder>"})
```

In case of CLI, the below command can be used.

```shell
java -cp <classpath> io.cucumber.core.cli.Main -p timeline:<report folder> --threads <thread count> -g <steps package> <path to feature files>
```

Below is a sample report.

![Timeline report](https://cucumber.io/assets/images/parallel-timeline-report-c9379657852195048823ed910599d70e.png)