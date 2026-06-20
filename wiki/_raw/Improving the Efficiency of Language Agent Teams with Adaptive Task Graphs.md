---
title: "Improving the Efficiency of Language Agent Teams with Adaptive Task Graphs"
source: "https://arxiv.org/html/2605.06320v1"
author:
published:
created: 2026-06-19
description:
tags:
  - "clippings"
---
Elizabeth Mieczkowski <sup>1</sup>  Alexander Ku <sup>1</sup>  Tiwalayo Eisape <sup>1</sup>  Dilip Arumugam <sup>1</sup>  
John Matters <sup>1</sup>  Katherine M. Collins <sup>1,2,3</sup>  Ilia Sucholutsky <sup>4</sup>  Thomas L. Griffiths <sup>1</sup>  
<sup>1</sup> Princeton University     <sup>2</sup> University of Cambridge     <sup>3</sup> MIT     <sup>4</sup> New York University  
Code: [https://github.com/emieczkowski/latte](https://github.com/emieczkowski/latte)

###### Abstract

Large language models (LLMs) are increasingly deployed in teams, yet existing coordination approaches often occupy two extremes. Highly structured methods rely on fixed roles, pipelines, or task decompositions assigned a priori. In contrast, fully unstructured teams enable adaptability and exploration but suffer from inefficiencies such as error propagation, inter-agent conflicts, and wasted resources (measured in time, tokens, or file operations). We introduce Language Agent Teams for Task Evolution (LATTE), a framework for coordinating LLM teams inspired by distributed systems, where processors must operate under partial observability and communication constraints. In LATTE, a team of agents collaboratively construct and maintain a shared, evolving coordination graph which encodes sub-task dependencies, individual agent assignment, and the current state of sub-task progress. This protocol maintains consistency while empowering agents to dynamically allocate work, adapt coordination, and discover new tasks. Across multiple collaborative tasks and a variety of base models, we demonstrate how LATTE reduces token usage, wall-clock time, communication, and coordination failures (e.g. file conflicts and redundant outputs) while matching or exceeding the accuracy of standard designs including MetaGPT, decentralized teams, top-down Leader-Worker hierarchies, and static decompositions.

## 1 Introduction

Collaboration can empower groups to achieve tremendous feats [^50] [^20], but it comes with substantial coordination costs. In complex domains such as software development, distributing work across a team can outperform even the most skilled programmer [^9] [^54], but also incurs substantial overhead [^6]. What happens when one collaborator modifies a core function that others depend on? In what order should interdependent tasks be executed? How should work be allocated when team members differ in speed or reliability? And how can teams prevent local errors from cascading through the system? In practice, these challenges arise routinely, including concurrent edit conflicts [^15], super-linear communication overhead [^6], dependency misalignment [^7] [^32], delays from distribution [^21], heterogeneous productivity [^45], and stragglers [^10]. Collaboration can dramatically amplify capability, but only when coordination is effectively managed.

Recent work has shown that LLM teams can improve accuracy and problem-solving by distributing tasks, roles, and context across multiple agents [^2] [^5] [^29] [^49] [^56] [^61], demonstrating emergent coordination [^38]. Despite these successes, the design of LLM teams remains fundamentally limited. Modern LLMs derive much of their power from their ability to flexibly adapt to new contexts and tasks [^13]. In contrast, most existing LLM team architectures impose rigid coordination structures, assigning fixed roles or pre-specifying task decompositions prior to execution [^22] [^40]. We argue that constraining LLM teams in this way limits their capacity for dynamic adaptation [^42] and introduces fragility, whereby failures or hallucinations in the Lead propagate downstream [^24].

Unstructured or decentralized LLM teams are more flexible [^31], yet face their own challenges. Without coordination scaffolding, agents frequently overwrite one another, produce inconsistent or incorrect outputs, and erroneously report task completion [^35] [^46]. These failures worsen when tasks must be performed sequentially, where adding agents to a team leads to over-communication and performance degradation [^26] [^35]. Self-coordinating teams often cannot outperform single expert models [^37] and are unable to overcome failures propagated by individual agents [^3]. This suggests a fundamental tension in designing LLM teams: structure is needed to improve coordination and inter-agent consistency, but over-specification suppresses the adaptability that makes LLMs powerful.

To resolve this tension, we propose LATTE (Language Agent Teams for Task Evolution), a formal orchestration framework for LLM teams to explicitly represent and adapt their own coordination during execution (Figure 1). Drawing inspiration from distributed systems — where protocols enable reliable task scheduling under partial information and dynamic conditions [^1] [^34] [^55] — agents operating within the LATTE framework construct and maintain a shared, evolving coordination task graph. In this graph, nodes represent subtasks that agents are assigned to, edges encode completion dependencies between subtasks, and a set of graph mutation operators allow the team to restructure coordination as execution unfolds. This graph serves as an evolving record of task decomposition, progress, roles, and active effort. Each agent proposes updates to the graph based on local context, which are reviewed and merged by a single agent. This division of labor reduces bottlenecks and single-points-of-failure that arise with hierarchical designs, provides explicit mechanisms for monitoring stragglers, and naturally serializes updates to prevent divergent local views or inconsistencies. The resulting framework preserves coherence and efficiency without sacrificing the capacity for emergent, context-sensitive adaptation.

![Refer to caption](https://arxiv.org/html/2605.06320v1/x1.png)

Figure 1: LATTE. Most existing LLM team designs are either highly structured (a. pipeline systems; b. Leader-Worker hierarchies) or unstructured (c. decentralized teams). (d) LATTE provides teams with a dynamic coordination graph that they collectively maintain and adapt. For example, in a data analysis task, the Lead initializes G 0 G\_{0} and assigns Worker 1 to preprocess. As Worker 1 learns about the data, it spawns parallel subtasks on the frontier ( Discover ) which the Lead then ASSIGN s to Workers 2 and 3. As this process continues, the Lead can Release stragglers and Close completed subtasks while Workers Claim frontier tasks proactively to avoid idleness. The shared graph serializes coordination decisions while preserving parallelism.

Our contributions are as follows:

1. A formal orchestration framework for LLM teams via dynamic task graphs: We define a set of graph mutation operators (Discover, Assign, Claim, Complete, Release, Close, and Verify) with explicit preconditions, postconditions, and invariant-preservation guarantees which culminate in a rigorous execution protocol for multi-agent LLM coordination. We demonstrate that the graph structure induces desirable runtime properties such as maximal parallelism via frontier nodes.
2. A hybrid centralized-decentralized model: We introduce a two-tier coordination model in which worker agents propose structural modifications to the graph and a lead orchestrator accepts or rejects them, preserving global consistency while enabling local adaptability. This division of labor is grounded in a probabilistic account of task decomposition.
3. LLM team interpretability: LATTE externalizes coordination during task execution, providing ways to interpret and audit team behavior. Our evaluation provides a suite of coordination metrics (overwrite rate, concurrent conflicts, wasted characters, idle rounds, and straggler tail latency) that address a systematic gap in how multi-agent LLM systems are benchmarked.
4. Empirical validation: LATTE consistently reduces token consumption, wall-clock time, inter-agent messages, file overwrites, consistency conflicts, and total output all while achieving higher accuracy than alternatively-structured and widely-used LLM team implementations.

Together, these results suggest that explicit coordination structures maintained by agents themselves are a viable path towards LLM teams that are simultaneously more efficient, interpretable, and adaptive.

## 2 Related Work

Prior work on LLM team coordination clusters around three patterns. Static systems like MetaGPT and ChatDev assign fixed functional roles and task structures before execution begins [^22] [^40]. While this simplifies scheduling, static assignments may struggle when new dependencies emerge or workloads shift mid-execution. Hierarchical or centralized frameworks such as HuggingGPT and recent meta-agent approaches use a lead agent to plan, dispatch, and synthesize work across subordinates [^47] [^28]. Centralization can enforce consistency but creates bottlenecks and single points of failure, which are especially acute in LLM teams where the Lead may hallucinate, crash, or fail to consolidate distributed progress [^46]. Decentralized teams avoid bottlenecks by letting agents operate autonomously, improve diversity, and distribute long contexts across agents [^14] [^29]. However, agents operating on local views of task state can produce conflicting or redundant outputs, and scaling the number of agents can degrade performance, particularly in tasks requiring sequential reasoning, expert agent assignment, or consistency [^26] [^37] [^35].

Task graphs from distributed computing offer a natural improvement to task decomposition and assignment: nodes represent tasks, edges encode precedence constraints, and schedulers assign work across processors efficiently [^51] [^36]. Classic schedulers like HEFT compute globally optimized assignments before execution; dynamic variants and work-stealing approaches such as NABBIT assign tasks online as they become available [^25] [^1]. However, these systems assume well-defined tasks and explicit control mechanisms. Extending task graphs to LLM teams requires supporting agents that autonomously discover, modify, and claim tasks in natural language. To our knowledge, LATTE is the first framework to bridge this gap: LLM teams jointly construct, maintain, and revise a shared task graph as an online, dynamic coordination structure during execution. We provide an extended discussion of related work in Appendix A1.

## 3 LATTE: Language Agent Teams for Task Evolution

We establish four key desiderata for a structured LLM team execution framework motivated by the limitations of prior architectures.

D1. Hybrid coordination: To avoid the bottlenecks of fully centralized systems and the inconsistency of fully decentralized ones, coordination should be hybrid. Decisions affecting shared state (e.g., graph updates or artifacts) must be centrally mediated, while task execution should be opportunistic to allow for parallel progress.

D2. Adaptive scaling: The framework should deploy agents efficiently, dynamically activating agents based on the current workload while maximizing parallelism when dependencies allow.

D3. Fault tolerance and monitoring: Because agents may stall, hallucinate, or produce null outputs, the system must support active monitoring and dynamic reallocation to detect and reassign tasks from unresponsive agents. It should also support auditing, where agents can proactively identify and flag high-uncertainty outputs that warrant additional quality control.

D4. Context scoping: To prevent memory overload and confusion, each agent should receive a scoped context. Workers should see only their local subtask, while the Lead’s view is restricted to the coordination graph rather than the full execution history.

### 3.1 Dynamic coordination graph

The set of agents $\mathcal{A}=\{\ell\}\cup\mathcal{W}$ in a LATTE team belong to one of two types: a Lead $\ell$ responsible for maintaining coordination structure and a set of Workers $\mathcal{W}$ responsible for executing assigned subtasks. Coordination proceeds through a shared dynamic coordination graph that explicitly tracks task progress, agent assignments, and shared state as execution unfolds.

###### Definition 1 (Dynamic Coordination Graph).

A *dynamic coordination graph* $G_{t}$ at round $t\in\{1,\ldots,T\}$ is a directed acyclic graph $G_{t}=(V_{t},\,E_{t},\,\lambda_{t})$. Here, $V_{t}$ is a finite set of nodes, each corresponding to a subtask. $E_{t}\subseteq V_{t}\times V_{t}$ is the set of dependency edges between subtasks such that $(u,v)\in E_{t}$ implies that subtask $v$ cannot begin until $u$ is complete. $\lambda_{t}:V_{t}\to(\mathcal{A}\cup\{\bot\})\times S$ assigns each node an agent and a status, where $\bot$ denotes unassigned and $S:=\{\texttt{pending},\ \texttt{assigned},\ \texttt{in\_progress},\ \texttt{done},\ \texttt{verified}\}$.

A strength of the coordination graph is encoding opportunities for parallelism during task execution.

###### Definition 2 (Frontier).

The *frontier* $F_{t}\subseteq V_{t}$ at round $t$ is the set of pending nodes with no unsatisfied dependencies: $F_{t}:=\{v\in V_{t}\mid\text{status}(v)=\texttt{pending}\text{ and }\forall(u,v)\in E_{t},\text{status}(u)=\texttt{done}\}.$

$F_{t}$ determines which subtasks are immediately executable, and thus corresponds to the number of Workers that can proceed in parallel at $t$.

### 3.2 Graph mutation operators

The asymmetry in information between Lead and Workers directly determines operator permissions. Worker $w_{i}$, reasoning from local trace $d_{t}^{(i)}$ about its subtask $v$, has sufficient information to propose local changes, such as discovering new subtasks encountered during execution (Discover) and certifying its subtask’s completion (Complete). It lacks visibility beyond $v$, preventing safe and holistic evaluation of proposals with graph-wide consequences, such as forcing completion of nodes whose downstream effects it cannot observe (Close). The Lead $\ell$ maintains global visibility into $G_{t}$ and exclusively controls operators with graph-wide consequences, such as Release to reassign stalled work and Verify to intercept errors.

Unlike the other operators, task acquisition need not be centralized. Rather than requiring $\ell$ to Assign every subtask, idle Workers may proactively claim available work directly from $v\in F_{t}$ via Claim($v$). This mirrors work-stealing or self-scheduling principles in distributed computing [^39] [^1], where fast processors claim ready tasks from a shared queue rather than waiting on a central scheduler, reducing overhead and improving wall-clock time. Concurrent claims on the same $v\in F_{t}$ are resolved by the orchestrator, preserving serialization without centralizing acquisition.

| Operator | Caller | Output |
| --- | --- | --- |
| $\textsc{Discover}(v,\text{deps})$ | $\ell,w$ | Add pending node $v$ with deps |
| $\textsc{Assign}(v,w)$ | $\ell$ | Assign pending $v$ to Worker $w$ |
| $\textsc{Claim}(v)$ | $w$ | Worker $w$ claims node $v$ |
| $\textsc{Complete}(v)$ | $w$ | Mark $v$ as finished by its $w$ |
| $\textsc{Release}(v)$ | $\ell$ | Return $v$ to pending |
| $\textsc{Close}(v)$ | $\ell$ | Force-complete $v$ |
| $\textsc{Verify}(v)$ | $\ell$ | Spawn verification for $v$ |

Table 1: Graph mutation operators.

Accordingly, LATTE provides a set of graph mutation operators with explicit preconditions, postconditions, and invariant-preservation guarantees (Table 1, Appendix A3). Unlike prior multi-agent LLM frameworks, where coordination contracts are implicit in role prompts, LATTE makes these contracts explicit and verifiable for every operator.

DAG invariance. All operators preserve the DAG invariant on $G_{t}$. Discover is the only operator that adds edges to $G_{t}$, and its precondition $v\notin V_{t}$ guarantees no self-loops. Additionally, requiring deps $\subseteq V_{t}$ with the resulting graph acyclic ensures no cycles are introduced. All remaining operators modify only $\lambda_{t}$ and leave $(V_{t},E_{t})$ unchanged.

Probabilistic motivation. This Leader-Worker division of labor can also be interpreted through a probabilistic lens, viewing the dynamic evolution of the task graph as an approximate posterior inference problem. To enable context scoping, LATTE decouples the graph updating process into proposal (by the Workers) and evaluation (by the Lead), which is conceptually grounded in sampling procedures such as Metropolis-Hastings. Further details of this motivation can be found in Appendix A2.

### 3.3 LATTE execution

The full execution protocol is described in Algorithm A4.5. LATTE proceeds in two phases: a preliminary planning phase followed by an iterative execution loop over the dynamically evolving coordination graph. During planning, $\ell$ is given the task description and initializes $G_{0}$ by proposing an initial decomposition of the problem via Discover operations. During execution, at each round $t=1,...,T$, agents are selectively dispatched to operate on the current graph $G_{t}$. Each round consists of five steps: (1) heartbeat monitoring (i.e., periodic liveness checks) to flag stragglers or stalled Workers to $\ell$; (2) frontier identification to compute $F_{t}$, the queue of available tasks; (3) dispatching for agents that are in-progress, assigned to new frontier tasks, and $\ell$ when necessary; (4) parallel execution of all selected agents; and (5) termination, which returns all task outputs and $G_{t}$.

### 3.4 Coordination properties

The LATTE protocol equips LLM teams with the structural tools to satisfy the four design desiderata (D1-D4) introduced in Section 3.1.

D1. Hybrid coordination: To balance consistency with adaptability, the Lead $\ell$ maintains exclusive control over operators with graph-wide consequences (Assign, Verify, Close), while Workers $w$ operate autonomously within their local scope. Crucially, LATTE enables self-scheduling: idle Workers may invoke Claim($v$) for any $v\in F_{t}$, allowing for opportunistic execution that reduces Lead overhead and improves wall-clock time [^39]. All structural updates to $G_{t}$ are serialized, preventing race conditions and inconsistencies to shared state.

D2. Adaptive scaling: At each round $t$, the number of Workers dispatched by LATTE equals $\min(|F_{t}|,|\mathcal{W}|)$. This ensures maximal parallelism given $G_{t}$; no valid protocol can dispatch more Workers at $t$ without violating a dependency constraint. Agents are activated only when there is available work, eliminating idle computation.

D3. Fault tolerance and monitoring: The heartbeat mechanism flags Workers that have been assigned but remain inactive for $H$ rounds, surfacing potential stalls to $\ell$ before they block progress. Upon detecting a straggler, $\ell$ may invoke Release($v$) to return the task to a pending state, making it available for immediate re-assignment or self-scheduling. In addition, rather than mandating an expensive review of every subtask, LATTE supports emergent verification. The Verify operator is invoked selectively by $\ell$ on nodes judged to be high-risk or high-uncertainty. This allows the rigor of quality control to scale dynamically with the complexity of the task graph.

D4. Context scoping: To mitigate context accumulation and token exhaustion, Workers receive only the description of their assigned subtask and its direct predecessors. The Lead receives $G_{t}$ and agent messages but does not ingest individual Workers’ full execution traces. These constraints bound the context each agent must attend to, reducing reasoning errors caused by irrelevant information.

## 4 Experiments

We evaluate LATTE against several existing multi-agent frameworks across three newly-designed collaborative domains: exploratory data analysis, debugging, and code generation. These domains were chosen to stress-test different coordination properties (parallelism, consistency, and adaptability). Experimental settings and prompt designs are provided in Appendices A4 and A5. Full task specifications and evaluation criteria are provided in Appendix A6.

Each task rewarded different combinations of the coordination properties above:

Task 1: Exploratory Data Analysis. Agents performed exploratory analysis on an opaque dataset, requiring preprocessing, analysis, visualizations, and synthesis of findings. Correctness was evaluated by a private test suite checking whether agents correctly identified planted data properties.

Task 2: Debugging. Agents debugged an existing repository against a test suite, requiring iterative test execution and code modification. This task rewards both parallelism (independent bugs can be diagnosed simultaneously) and consistency (some functions can only be verified after dependencies are fixed). We placed several bugs in a signal-processing library, and success required teams to pass all tests in a given suite.

Task 3: Library Extension. Agents extended a Python text-processing library by completing two existing classes and building six new modules from stubs. The task has natural sequential dependencies, parallel modules, and a final integration step. Correctness was evaluated by a private test suite after completion. Unlike Tasks 1 and 2, the required functions are fully known in advance.

![Refer to caption](https://arxiv.org/html/2605.06320v1/x2.png)

Figure 2: Efficiency-accuracy tradeoff. A) LATTE achieves greater efficiency than alternative frameworks. We measure expected cost (total tokens or wall-clock time weighted by trial completion rate) to account for runs in which teams fail to terminate. B) LATTE achieves higher task success with lower token consumption (normalized across tasks) on the accuracy-vs-token-cost Pareto frontier.

We evaluate the performance of LATTE against four baseline team structures. We test Leader-Worker hierarchies, where a single Lead synthesizes and assigns tasks to four Workers; MetaGPT [^22], representative of pipeline-based LLM teams with different roles (Product Manager, Architect, Project Manager, Engineer, QA Engineer); decentralized teams with 5 peer agents; and a static task graph ablation, in which the Lead initializes assignments based on its prior $G_{0}$ and agents cannot update the graph after planning. We maintained a team size of $N=5$ to benchmark against MetaGPT. For each team structure, we tested two frontier base models: Claude Sonnet 4-6 (Anthropic; claude-sonnet-4-6) and GPT-5.2 (OpenAI; gpt-5.2). We ran 10 trials per condition for a total of 300 trials (5 conditions × 2 models × 3 tasks × 10 repetitions). Full implementation details are provided in Appendix A4 and A5.

## 5 Results

### 5.1 LATTE achieves higher accuracy and efficiency than existing LLM teams

Table 2: Accuracy, token usage, and wall-clock time across successful trials per task ($\pm$ SEM).

<table><thead><tr><th></th><th></th><th>LATTE</th><th>Leader-Worker</th><th>Decentralized</th><th>Static</th><th>MetaGPT</th></tr></thead><tbody><tr><th rowspan="4">Acc. (%)</th><th>Agg.</th><td><math><semantics><mrow><mn>80</mn> <mo>±</mo> <mn>4</mn></mrow> <annotation>80\pm 4</annotation></semantics></math></td><td><math><semantics><mrow><mn>70</mn> <mo>±</mo> <mn>5</mn></mrow> <annotation>70\pm 5</annotation></semantics></math></td><td><math><semantics><mrow><mn>74</mn> <mo>±</mo> <mn>4</mn></mrow> <annotation>74\pm 4</annotation></semantics></math></td><td><math><semantics><mrow><mn>58</mn> <mo>±</mo> <mn>5</mn></mrow> <annotation>58\pm 5</annotation></semantics></math></td><td><math><semantics><mrow><mn>34</mn> <mo>±</mo> <mn>7</mn></mrow> <annotation>34\pm 7</annotation></semantics></math></td></tr><tr><th>Data Analysis</th><td><math><semantics><mrow><mn>96</mn> <mo>±</mo> <mn>1</mn></mrow> <annotation>96\pm 1</annotation></semantics></math></td><td><math><semantics><mrow><mn>94</mn> <mo>±</mo> <mn>1</mn></mrow> <annotation>94\pm 1</annotation></semantics></math></td><td><math><semantics><mrow><mn>93</mn> <mo>±</mo> <mn>2</mn></mrow> <annotation>93\pm 2</annotation></semantics></math></td><td><math><semantics><mrow><mn>88</mn> <mo>±</mo> <mn>3</mn></mrow> <annotation>88\pm 3</annotation></semantics></math></td><td><math><semantics><mrow><mn>75</mn> <mo>±</mo> <mn>2</mn></mrow> <annotation>75\pm 2</annotation></semantics></math></td></tr><tr><th>Debug</th><td><math><semantics><mrow><mn>100</mn> <mo>±</mo> <mn>0</mn></mrow> <annotation>100\pm 0</annotation></semantics></math></td><td><math><semantics><mrow><mn>90</mn> <mo>±</mo> <mn>7</mn></mrow> <annotation>90\pm 7</annotation></semantics></math></td><td><math><semantics><mrow><mn>100</mn> <mo>±</mo> <mn>0</mn></mrow> <annotation>100\pm 0</annotation></semantics></math></td><td><math><semantics><mrow><mn>44</mn> <mo>±</mo> <mn>13</mn></mrow> <annotation>44\pm 13</annotation></semantics></math></td><td><math><semantics><mrow><mn>32</mn> <mo>±</mo> <mn>11</mn></mrow> <annotation>32\pm 11</annotation></semantics></math></td></tr><tr><th>Library Ext.</th><td><math><semantics><mrow><mn>40</mn> <mo>±</mo> <mn>2</mn></mrow> <annotation>40\pm 2</annotation></semantics></math></td><td><math><semantics><mrow><mn>23</mn> <mo>±</mo> <mn>2</mn></mrow> <annotation>23\pm 2</annotation></semantics></math></td><td><math><semantics><mrow><mn>27</mn> <mo>±</mo> <mn>2</mn></mrow> <annotation>27\pm 2</annotation></semantics></math></td><td><math><semantics><mrow><mn>40</mn> <mo>±</mo> <mn>2</mn></mrow> <annotation>40\pm 2</annotation></semantics></math></td><td><math><semantics><mrow><mn>6</mn> <mo>±</mo> <mn>4</mn></mrow> <annotation>6\pm 4</annotation></semantics></math></td></tr><tr><th rowspan="4">Tokens (K)</th><th>Agg.</th><td><math><semantics><mrow><mn>148</mn> <mo>±</mo> <mn>14</mn></mrow> <annotation>148\pm 14</annotation></semantics></math></td><td><math><semantics><mrow><mn>379</mn> <mo>±</mo> <mn>51</mn></mrow> <annotation>379\pm 51</annotation></semantics></math></td><td><math><semantics><mrow><mn>419</mn> <mo>±</mo> <mn>47</mn></mrow> <annotation>419\pm 47</annotation></semantics></math></td><td><math><semantics><mrow><mn>297</mn> <mo>±</mo> <mn>40</mn></mrow> <annotation>297\pm 40</annotation></semantics></math></td><td><math><semantics><mrow><mn>397</mn> <mo>±</mo> <mn>59</mn></mrow> <annotation>397\pm 59</annotation></semantics></math></td></tr><tr><th>Data Analysis</th><td><math><semantics><mrow><mn>122</mn> <mo>±</mo> <mn>13</mn></mrow> <annotation>122\pm 13</annotation></semantics></math></td><td><math><semantics><mrow><mn>257</mn> <mo>±</mo> <mn>60</mn></mrow> <annotation>257\pm 60</annotation></semantics></math></td><td><math><semantics><mrow><mn>271</mn> <mo>±</mo> <mn>60</mn></mrow> <annotation>271\pm 60</annotation></semantics></math></td><td><math><semantics><mrow><mn>403</mn> <mo>±</mo> <mn>93</mn></mrow> <annotation>403\pm 93</annotation></semantics></math></td><td><math><semantics><mrow><mn>390</mn> <mo>±</mo> <mn>61</mn></mrow> <annotation>390\pm 61</annotation></semantics></math></td></tr><tr><th>Debug</th><td><math><semantics><mrow><mn>227</mn> <mo>±</mo> <mn>33</mn></mrow> <annotation>227\pm 33</annotation></semantics></math></td><td><math><semantics><mrow><mn>642</mn> <mo>±</mo> <mn>103</mn></mrow> <annotation>642\pm 103</annotation></semantics></math></td><td><math><semantics><mrow><mn>792</mn> <mo>±</mo> <mn>73</mn></mrow> <annotation>792\pm 73</annotation></semantics></math></td><td><math><semantics><mrow><mn>286</mn> <mo>±</mo> <mn>36</mn></mrow> <annotation>286\pm 36</annotation></semantics></math></td><td><math><semantics><mrow><mn>236</mn> <mo>±</mo> <mn>41</mn></mrow> <annotation>236\pm 41</annotation></semantics></math></td></tr><tr><th>Library Ext.</th><td><math><semantics><mrow><mn>98</mn> <mo>±</mo> <mn>9</mn></mrow> <annotation>98\pm 9</annotation></semantics></math></td><td><math><semantics><mrow><mn>169</mn> <mo>±</mo> <mn>17</mn></mrow> <annotation>169\pm 17</annotation></semantics></math></td><td><math><semantics><mrow><mn>194</mn> <mo>±</mo> <mn>25</mn></mrow> <annotation>194\pm 25</annotation></semantics></math></td><td><math><semantics><mrow><mn>140</mn> <mo>±</mo> <mn>12</mn></mrow> <annotation>140\pm 12</annotation></semantics></math></td><td><math><semantics><mrow><mn>707</mn> <mo>±</mo> <mn>188</mn></mrow> <annotation>707\pm 188</annotation></semantics></math></td></tr><tr><th rowspan="4">Wall-clock (m)</th><th>Agg.</th><td><math><semantics><mrow><mn>3.5</mn> <mo>±</mo> <mn>0.3</mn></mrow> <annotation>3.5\pm 0.3</annotation></semantics></math></td><td><math><semantics><mrow><mn>5.9</mn> <mo>±</mo> <mn>0.6</mn></mrow> <annotation>5.9\pm 0.6</annotation></semantics></math></td><td><math><semantics><mrow><mn>3.7</mn> <mo>±</mo> <mn>0.3</mn></mrow> <annotation>3.7\pm 0.3</annotation></semantics></math></td><td><math><semantics><mrow><mn>6.0</mn> <mo>±</mo> <mn>0.6</mn></mrow> <annotation>6.0\pm 0.6</annotation></semantics></math></td><td><math><semantics><mrow><mn>11.5</mn> <mo>±</mo> <mn>1.2</mn></mrow> <annotation>11.5\pm 1.2</annotation></semantics></math></td></tr><tr><th>Data Analysis</th><td><math><semantics><mrow><mn>3.2</mn> <mo>±</mo> <mn>0.3</mn></mrow> <annotation>3.2\pm 0.3</annotation></semantics></math></td><td><math><semantics><mrow><mn>4.9</mn> <mo>±</mo> <mn>0.9</mn></mrow> <annotation>4.9\pm 0.9</annotation></semantics></math></td><td><math><semantics><mrow><mn>2.9</mn> <mo>±</mo> <mn>0.5</mn></mrow> <annotation>2.9\pm 0.5</annotation></semantics></math></td><td><math><semantics><mrow><mn>6.2</mn> <mo>±</mo> <mn>0.6</mn></mrow> <annotation>6.2\pm 0.6</annotation></semantics></math></td><td><math><semantics><mrow><mn>8.7</mn> <mo>±</mo> <mn>1.7</mn></mrow> <annotation>8.7\pm 1.7</annotation></semantics></math></td></tr><tr><th>Debug</th><td><math><semantics><mrow><mn>5.3</mn> <mo>±</mo> <mn>0.6</mn></mrow> <annotation>5.3\pm 0.6</annotation></semantics></math></td><td><math><semantics><mrow><mn>9.1</mn> <mo>±</mo> <mn>1.2</mn></mrow> <annotation>9.1\pm 1.2</annotation></semantics></math></td><td><math><semantics><mrow><mn>6.1</mn> <mo>±</mo> <mn>0.4</mn></mrow> <annotation>6.1\pm 0.4</annotation></semantics></math></td><td><math><semantics><mrow><mn>6.2</mn> <mo>±</mo> <mn>0.6</mn></mrow> <annotation>6.2\pm 0.6</annotation></semantics></math></td><td><math><semantics><mrow><mn>8.7</mn> <mo>±</mo> <mn>1.7</mn></mrow> <annotation>8.7\pm 1.7</annotation></semantics></math></td></tr><tr><th>Library Ext.</th><td><math><semantics><mrow><mn>2.1</mn> <mo>±</mo> <mn>0.2</mn></mrow> <annotation>2.1\pm 0.2</annotation></semantics></math></td><td><math><semantics><mrow><mn>3.6</mn> <mo>±</mo> <mn>0.3</mn></mrow> <annotation>3.6\pm 0.3</annotation></semantics></math></td><td><math><semantics><mrow><mn>2.2</mn> <mo>±</mo> <mn>0.2</mn></mrow> <annotation>2.2\pm 0.2</annotation></semantics></math></td><td><math><semantics><mrow><mn>3.4</mn> <mo>±</mo> <mn>0.3</mn></mrow> <annotation>3.4\pm 0.3</annotation></semantics></math></td><td><math><semantics><mrow><mn>18.9</mn> <mo>±</mo> <mn>3.4</mn></mrow> <annotation>18.9\pm 3.4</annotation></semantics></math></td></tr></tbody></table>

Across tasks and base models, LATTE consistently achieves a superior accuracy–efficiency tradeoff, Pareto-dominating existing LLM team structures (Fig. 2; Table 2).

Computational cost. Using one-sided Mann-Whitney U tests on normalized, pooled costs across all tasks and models, LATTE achieves a mean token cost of $47.5\%$, nearly half that of the next-best method, the static graph ablation ($M=86.9\%$, $p<0.01$). All other baselines are also more expensive: MetaGPT ($M=228.7\%$, $p<0.01$), Leader-Worker ($M=104.2\%$, $p<0.01$), and decentralized ($M=120.9\%$, $p<0.01$).

Wall-clock time. LATTE ($M=66.7\%$) is faster than static graphs ($M=110.7\%$, $p<0.01$), MetaGPT ($M=289.0\%$, $p<0.01$), and Leader–Worker teams ($M=105.7\%\%$, $p<0.01$). Decentralized teams also have a higher mean latency than LATTE, though the difference is not statistically significant ($M=69.3\%$, $p=0.34$).

Task accuracy. LATTE achieves the overall highest task accuracy ($79.7\%$), surpassing static graphs ($57.6\%$, $p<0.01$), fixed pipelines (MetaGPT; $33.9\%$, $p<0.01$), Leader-Worker teams ($70.1\%$, $p=0.04$), and decentralized teams ($73.9\%$, $p=0.16$). Consistent with our probabilistic motivation, LATTE achieves comparable accuracy to the static ablation on Task 3 (using substantially less wall-clock time and fewer tokens) but much greater accuracy on Tasks 1–2. When task structure is known in advance, the initial graph $G_{0}$ can be well-specified, leaving fewer subtasks for LATTE to dynamically discover.

### 5.2 LLM teams successfully utilize dynamic coordination graphs via LATTE

Figure 3 demonstrates that LLM teams successfully utilize the full expressive power of the LATTE protocol to manage task complexity. Discover is the most frequent operator, confirming that teams actively expand their coordination graphs as new requirements emerge. The Lead effectively delegates via Assign, yet the high success rate of Worker-initiated Claim operations suggests that decentralized self-scheduling significantly reduces coordination bottlenecks. Notably, LATTE teams exhibit emergent fault tolerance through the selective use of recovery operators. The Lead invoked Release in 36% of trials to reassign straggling tasks. Similarly, Verify was invoked in 19% of trials, demonstrating that the Lead can trigger verification when deemed necessary. Specifically, Leads triggered Verify more often in high-uncertainty, challenging trials, where teams took an average of 18.1 rounds to pass tests. In contrast, trials that completed successfully in 8.1 rounds on average contained no verification events. These behaviors are particularly encouraging as they indicate LATTE’s capacity for autonomous fault tolerance, monitoring, and strategic resource allocation.

Crucially, these patterns are only observable because LATTE externalizes emergent coordination, providing concrete ways to interpret and audit team behavior. The evolving task graph makes otherwise hidden decisions directly observable. For example, Figure 3C demonstrates how team structure and progress evolve over time. In a Leader-Worker or decentralized team, mechanisms like selective verification would be invisible or buried in the message logs rather than recorded as explicit and structured coordination decisions.

### 5.3 LATTE induces better coordination

Beyond aggregate performance, we report finer-grained coordination metrics to address a fundamental gap in evaluating teams: overwrites, concurrent writes, communication overhead, and wasted outputs are rarely measured in prior work, yet directly capture how often agents waste resources and interfere.

![Refer to caption](https://arxiv.org/html/2605.06320v1/x3.png)

Figure 3: LLM teams successfully utilize LATTE. A) LATTE teams emergently call all graph operators across rounds, demonstrating full utilization of the coordination toolkit. B) Dynamic coordination graphs grow larger than static ones over time. This reflects richer and more fine-grained understanding of which subtasks need to be executed, offering more opportunities for Workers to be deployed. In contrast, a smaller static graph represents a fixed, underspecified coordination structure that cannot adapt to task demands. C) A representative example of how a coordination graph evolves across rounds using GPT-5.2. As agents add edges and dependencies, the graph encodes emergent assignments and progress. Because coordination is represented explicitly, team behaviors can be tracked, interpreted, and diagnosed over time, a key advantage over black-box multi-agent systems.

LATTE decreases inter-agent conflicts. In collaborative tasks with a shared state, agents may overwrite completed work, simultaneously edit the same text, or redundantly duplicate effort. Each conflict carries distinct costs in wasted tokens, corrupted state, and downstream debugging. LATTE mitigates these failure modes through explicit task assignment and dependency tracking, ensuring agents operate on disjoint subtasks in a well-defined order (Fig. 4A-C). The reductions are substantial. LATTE agents overwrite each other $4.3\times$ per trial on average, versus $22.8\times$ in Leader-Worker teams ($p<0.01$) and $35.4\times$ in decentralized ($p<0.01$): a $5.3\times$ and $8.2\times$ reduction respectively. Concurrent writes to the same function follow the same pattern: $1.0\times$ per trial versus $8.5\times$ in Leader-Worker ($p<0.01$) and $11.5\times$ in decentralized ($p<0.01$). These conflicts compound into wasted output. LATTE produces 5,236 discarded characters per trial on average, compared to 45,436 in Leader–Worker ($p<0.01$) and 78,062 in decentralized ($p<0.01$), corresponding to more than 40,000 and 70,000 extra characters of output that never appear in the final product.

LATTE reduces costly communication. Communication overhead is also a meaningful cost in LLM teams. Agents tend to send excessive messages, consuming unnecessary tokens, introducing latency, and interrupting teammates with irrelevant information [^35] [^59] [^8]. LATTE constrains this by making communication purposeful (Fig. 4D). Workers message the Lead only when blocked, needing clarification, or signaling dependencies for another agent. This structure produces measurably less communication. LATTE agents send $20.4$ inter-agent messages per task, compared to $31.4$ in Leader–Worker teams ($p=0.04$) and $34.8$ in decentralized teams ($p<0.01$). LATTE agents also exchange leaner messages, with $42{,}484$ characters sent versus $50{,}073$ in Leader-Worker teams ($p<0.01$) and $60{,}394$ in decentralized teams ($p<0.01$). These results show that LATTE reduces unnecessary communication and limits context accumulation per agent.

LATTE selectively activates agents, reducing idle computation. LATTE restricts participation to $F_{t}$, activating agents only when pending work exists. On average, agents are active for only $48.7\%$ of rounds while maintaining high task performance (Fig. 4E). By contrast, decentralized teams activate all agents every round regardless of demand, inflating computation and communication costs. Leader-Worker teams fall in between, deploying agents for $80\%$ of rounds.

LATTE mitigates stragglers. Finally, a key challenge in static systems are stragglers: agents that take disproportionately long to complete assigned tasks [^11] [^35]. LATTE addresses this by monitoring node execution time and sending a heartbeat to the Lead when a threshold is exceeded, giving the Lead the option to Release and reassign the task, or Workers the option to self-claim it. Release is invoked in $36\%$ of runs, confirming that straggler mitigation emerges in practice. The impact on completion time is substantial. LATTE teams complete assigned nodes in 39.2s on average versus 75.6s for static teams ($p<0.01$), and this gap widens at the tail: at the 95th percentile, 130s versus 294s for static teams (a $2.3\times$ reduction), showing this mechanism effectively prevents stragglers from blocking task completion.

## 6 Conclusion

![Refer to caption](https://arxiv.org/html/2605.06320v1/x4.png)

Figure 4: LATTE improves coordination. (A) Overwrites: agents overwriting a prior agent’s work in a later round. (B) Concurrent writes: two agents simultaneously writing to the same function. (C) Wasted output: characters written that do not appear in the final output. (D) Communication overhead: number and volume of messages exchanged. (E) Inactivity: proportion of rounds with an agent suppressed. LATTE reduces A–D and increases E.

Inspired by task graphs and scheduling protocols in distributed systems, LATTE enables LLM teams to dynamically explore and solve problems while maintaining consistency and efficiency. Across settings, LATTE exhibits consistent gains in token and time efficiency, conflict resolution, and coordination quality while preserving the flexibility for agents to explore and refine solutions as tasks evolve. More broadly, LATTE challenges a core assumption in prior frameworks that coordination structure must be imposed by the system architect. Instead, allowing agents to maintain and revise their own coordination structure online empowers teams to adapt to evidence accumulated during execution. These results establish explicit, agent-maintained coordination as a principle for building LLM teams that are simultaneously more efficient, reliable, and adaptive. By reducing token consumption and wall-clock time, LATTE directly cuts the computational (and thereby financial) cost associated with LLM teams, conserving resources that would otherwise be spent on redundant communication and unresolved conflicts.

Limitations. Several limitations point to promising directions for future work. First, LATTE introduces planning overhead from graph initialization which may outweigh its benefits on short or simple tasks where a single agent would suffice. A deeper analysis of this overhead is provided in Appendix A6.3. Second, our evaluation focuses on domains with natural subtask boundaries such as coding. The current operator set could be extended to support less structured forms of task discovery and decomposition, enabling LATTE to tackle a broader range of open-ended reasoning tasks in future work. Third, we fix team size to benchmark fairly against baselines such as MetaGPT, leaving the question of how LATTE scales to future work. Fourth, LATTE teams demonstrate an emergent ability to identify where verification is needed, invoking Verify selectively rather than applying blanket review mechanisms to all agent outputs [^23]. Understanding and strengthening these emergent verification mechanisms is a particularly promising direction, as targeted quality control may be key to reliable LLM team performance at scale. Finally, future work should explore fine-tuning or reinforcement learning on coordination outcomes, allowing teams to learn better graph constructions, task assignments, and communication protocols over time.

Code Availability. An implementation of LATTE is available at [https://github.com/emieczkowski/latte](https://github.com/emieczkowski/latte).

## Acknowledgments

This work was supported by the National Defense Science and Engineering Graduate (NDSEG) Fellowship Program to EM, and ONR MURI N00014-24-1-2748 to DA and TG.

## References

## Appendix

## Appendix A1 Related Work

### A1.1 LLM teams

LLMs are increasingly deployed in multi-agent teams. In some settings, these teams outperform individual models by improving diversity and distributing long contexts across many agents [^61] [^29] [^5] [^14]. As a result of these emergent cooperative abilities, LLM teams have achieved desirable results in domains such as scientific discovery [^49] [^60] and software engineering [^22] [^40]. Despite these successes, coordination remains a critical challenge. As multiple agents interact and contribute to a shared task, ensuring consistent, non-redundant, and well-structured collaboration becomes exceedingly difficult. Recent work has shown that scaling the number of agents does not reliably improve performance, and can in fact degrade results depending on task structure and agent heterogeneity [^26] [^37] [^57] [^43]. In particular, performance deteriorates in settings requiring sequential reasoning or consistent shared states like software repositories [^35]. Unstructured interaction can further Lead to failures such as hallucinated responsibilities, misinformation, and adversarial behavior among agents [^46].

To overcome these challenges, various frameworks aim to improve team performance with explicitly structured task assignment and interaction. One common approach is to impose role-based and hierarchical decompositions. Systems like MetaGPT assign fixed functional roles (e.g., Product Manager, Engineer) to agents performing collaborative software tasks [^22], while ChatDev similarly adopts a fixed hierarchy with role-conditioned specialization [^40]. Frameworks such as HuggingGPT [^47] similarly use an LLM controller to plan and dispatch heterogeneous expert models against a fixed task taxonomy, but do not adapt the underlying decomposition during execution. More recent approaches introduce feedback-driven re-planning, where a meta-agent iteratively updates plans [^28].

In single-agent settings, reasoning and planning can be structured as chains, graphs, or trees over intermediate steps, or as decompositions into simpler subproblems whose solutions feed forward, improving compositionality and generalization beyond the prompted exemplars [^53] [^58] [^4] [^62].

### A1.2 Task graphs and coordination protocols

Recent work identifies parallels between LLM teams and distributed computing systems. Agents with limited local information contend for shared resources, fail without warning, retry, race, and must produce a coherent shared output; notably, this is the exact regime distributed-computing engineers have spent decades modeling [^11] [^33] [^36]. In both settings, critical tradeoffs arise between different coordination structures [^52]. First, fully centralized architectures can avoid consistency conflicts by designating one Lead to assign tasks and serialize updates, but create bottlenecks and single-points-of-failure. Fully decentralized approaches are more scalable and robust, but agents operating independently on local views of task state can produce conflicting or redundant outputs. Second, static approaches commit to a fixed task assignment up front, which simplifies global scheduling but requires complete task visibility in advance. Thus, static assignments cannot adapt when tasks fail, new dependencies emerge, or workloads shift. Alternatively, dynamic approaches assign tasks online as they become available but require mechanisms to maintain consistency as the task evolves.

Task graphs are used in distributed systems (as well as in reinforcement learning and planning [^12] [^16]) to formalize this coordination problem. Nodes represent tasks, edges encode precedence dependencies, and the objective is to schedule tasks to processors efficiently [^55] [^51]. Classic scheduling algorithms such as HEFT operate at the centralized, static end of both axes, computing a globally optimized assignment before execution begins [^51]. Dynamic variants move along the second axis by making assignments online as tasks and dependencies become known [^25]. Approaches like NABBIT enable both some decentralization and dynamic allocation using a shared task pool and work-stealing, so processors can autonomously claim ready tasks without a central Leader [^1]. Learning-based schedulers such as Decima further adapt policies to workload structure at runtime [^34], combining dynamic assignment with learned coordination. Ray similarly operationalizes online task-graph scheduling at scale through a sharded control store and bottom-up distributed scheduler, supporting dynamic task graphs whose structure is not known in advance [^36]. Yet Ray’s dynamism is in execution scheduling, not task specification: nodes are well-typed remote functions and actor methods registered in advance, and the graph evolves only as those primitives are invoked at runtime. These approaches assume well-defined tasks and explicit control mechanisms, rather than agents that can flexibly and autonomously discover and modify tasks in natural language. These same assumptions persist even when porting over the concept of task graphs to hierarchical decision-making agents [^12] [^16].

## Appendix A2 Probabilistic Motivation

To motivate the division of labor between Lead and Workers, we develop a probabilistic account of team coordination as posterior inference over task graphs. Since the Lead and Worker agents have varying degrees of visibility, the costs associated with individual steps or rounds of this posterior inference varies between agents. Whereas (approximate) Bayesian inference is commensurate with *thinking*, thinking while balancing the costs of inference induces a higher-level problem of *thinking about how to think* or meta-reasoning [^44] [^19] [^17]. We motivate LATTE as encapsulating a meta-reasoning approach to efficiently deploying team-wide computational resources towards the Bayesian inference problem of identifying the best task decomposition conditioned upon all observed data [^41] [^48] [^27].

The inference problem. Let $G_{t}$ denote the team’s current task decomposition at round $t$, or a hypothesis about how the global task should be decomposed and assigned. We treat the space of valid DAGs as a hypothesis space, and model the team’s goal as posterior inference: to find $G_{t}$ that maximizes $P(G_{t}\mid D_{t})$, where $D_{t}$ denotes all evidence accumulated in round $t$ (e.g., execution logs, completed outputs, messages, and environment feedback). By Bayes’ theorem we have that

$$
\displaystyle P(G_{t}\mid D_{t})=\frac{P(D_{t}\mid G_{t})P(G_{t})}{P(D_{t})}.
$$

The marginal likelihood $P(D_{t})=\sum_{G}P(D_{t}|G)P(G)$ requires summing over the space of all valid task graphs, which is combinatorially intractable. Additionally, the likelihood $P(D_{t}|G)$ has no closed form, as $D_{t}$ is comprised of outputs in natural language or execution traces whose probabilities cannot be evaluated directly.

MCMC as a tractable alternative. Markov chain Monte Carlo offers a standard approach to posterior inference that sidesteps computing $P(D_{t})$. Rather than evaluating the posterior directly, we construct a Markov chain over task graphs whose stationary distribution is $P(G_{t}|D_{t})$. At each step, a proposal $G^{\prime}$ is generated and accepted with probability:

$$
\displaystyle A(G_{t}\to G^{\prime}_{t}\mid D_{t})
$$
 
$$
\displaystyle=\min\left(1,\frac{P(D_{t}\mid G^{\prime}_{t})\,P(G^{\prime}_{t})\,Q(G_{t}\mid G^{\prime}_{t},D_{t})}{P(D_{t}\mid G_{t})\,P(G_{t})\,Q(G^{\prime}_{t}\mid G_{t},D_{t})}\right)
$$

where $Q(G^{\prime}_{t}\mid G_{t},D_{t})$ is the proposal distribution. Because $P(D_{t})$ appears in both numerator and denominator, it cancels exactly, making evaluation of the acceptance ratio feasible without computing the marginal likelihood.

Leader-Worker decomposition as meta-reasoning. The remaining challenge is constructing a proposal distribution $Q$ that is both tractable and expressive. Observe that one approach would be to take the Lead $\ell$, who has full visibility over the past interactions of all Worker agents $D_{t}$, and charge them with identifying a new proposal $G^{\prime}_{t}$; without regard for the costs of inference, this approach might seem promising. However, this strategy places the onus upon a single agent (in this work, a single LLM) to process a considerable volume of information stored in the full history $D_{t}$ before proceeding to reason over an exponentially large hypothesis space, both of which degrade LLM response reliability [^30].

Rather than placing all the burdens of inference upon the Lead’s shoulders, an alternative and more cost-effective approach would be to empower the individual Worker agents $w_{i}$. In particular, one could obtain a new task decomposition $G^{\prime}_{t,i}$ from each Worker $w_{i}$. From there, one quick option for obtaining a new task decomposition is via simple merging of all Workers’ proposals: $G^{\prime}_{t}=\texttt{merge}(G^{\prime}_{t,1},G^{\prime}_{t,2},\ldots)$. Alternatively, each new proposal could be treated as a point estimate in a particle filter and one could simply be chosen uniformly at random. Notably, this type of approach sits at the opposite extreme of the previous Leader-centric approach, where the costs of inference are reduced down to processing the individual local histories of each Worker $d_{t}^{(i)}\subset D_{t}$. Unfortunately, as each one lacks global visibility, no one Worker agent is well poised to understand whether or not their proposals actually enhance global task performance for the entire team.

While the preceding approaches either maximize or sacrifice inference quality and considerably increased or reduced cost, LATTE can obtain a more-efficient solution to the meta-reasoning problem and better balance the quality-cost trade-offs of inference by exploiting the structure of $G_{t}$. Specifically, we will assign each Worker $w_{i}$ to a local subtask $g_{t}^{(i)}\subset G_{t}$ and accumulates a local execution trace $d_{t}^{(i)}\subset D_{t}$. Worker $w_{i}$ proposes a local update by sampling:

$$
\displaystyle g^{(i)\prime}_{t}\sim Q(\cdot\mid g^{(i)}_{t},\,d^{(i)}_{t})
$$

Confining the proposal to $g^{(i)}_{t}$ keeps each Worker’s task tractable since $w_{i}$ attends to its local trace $d^{(i)}_{t}$ rather than the full history $D_{t}$. The candidate global decomposition for round $t$ is then the union of local updates across all Workers $G^{\prime}_{t}=\bigcup_{i}g^{(i)\prime}_{t}$.

The Lead $\ell$ maintains global visibility of $G_{t}$ and evaluates the acceptance ratio, either commiting $G_{t+1}=G^{\prime}_{t}$ or retaining $G_{t+1}=G_{t}$. Thus, Workers have sufficient local information to propose structural changes within their own scope, while the Lead has the global view needed to evaluate whether a proposal improves the overall decomposition. Critically, this mirrors the Metropolis-Hastings acceptance step [^18], where the evaluator need only approximate the ratio of unnormalized likelihoods $P(D_{t}\mid G^{\prime}_{t})P(G^{\prime}_{t})/P(D_{t}\mid G_{t})P(G_{t})$ (e.g. a comparison between two specific graphs) rather than integrating over the full hypothesis space; crucially, however, we do not claim that LATTE agents necessarily compute this ratio explicitly. Moreover, LATTE incurs a marginal increase in cost — for the Lead to assess the benefits of a proposed local update — beyond the purely local Worker update approach outlined above while capitalizing on the global visibility of the Lead to maintain high-quality inference. Overall, this framing provides a normative account of why the division of labor in LATTE is well-founded and what behaviors the associated LLMs are approximating. We formalize this division of labor as a set of graph mutation operators in the next section.

## Appendix A3 Graph Mutation Operators

We define seven operators that mutate the task graph; each is invoked by the Lead $\ell$, a Worker $w$, or both. $F_{t}$ denotes the set of nodes whose dependencies are fully satisfied at time $t$.

$\textsc{Discover}(v,\text{deps})$ $(\ell,w)$

Requires $v\notin V_{t}$, $\text{deps}\subseteq V_{t}$, and that adding $v$ preserves acyclicity.  
Adds $v$ to $V_{t}$, inserts edges from each dependency to $v$ in $E_{t}$, and initializes  
$\lambda_{t}(v)\leftarrow(\bot,\texttt{pending})$.

$\textsc{Assign}(v,w)$ $(\ell)$

Requires $\text{status}(v)=\texttt{pending}$ and $w\in\mathcal{W}$.  
Sets $\lambda_{t}(v)\leftarrow(w,\texttt{assigned})$.

$\textsc{Claim}(v)$ $(w)$

Requires $v\in F_{t}$ and $\text{agent}(v)\in\{\bot,w\}$.  
Sets $\lambda_{t}(v)\leftarrow(w,\texttt{in\_progress})$.

$\textsc{Complete}(v)$ $(w)$

Requires $\text{status}(v)=\texttt{in\_progress}$ and $\text{agent}(v)=w$.  
Sets $\lambda_{t}(v)\leftarrow(w,\texttt{done})$.

$\textsc{Release}(v)$ $(\ell)$

Requires $\text{status}(v)\in\{\texttt{assigned},\texttt{in\_progress}\}$.  
Resets $\lambda_{t}(v)\leftarrow(\bot,\texttt{pending})$.

$\textsc{Close}(v)$ $(\ell)$

Requires $\text{status}(v)\in\{\texttt{assigned},\texttt{in\_progress}\}$.  
Sets $\lambda_{t}(v)\leftarrow(\text{agent}(v),\texttt{done})$ without requiring the Worker to signal completion.

$\textsc{Verify}(v)$ $(\ell)$

Requires $\text{status}(v)=\texttt{done}$ and $v_{\text{ver}}\notin V_{t}$.  
Adds a verification node $v_{\text{ver}}$ to $V_{t}$, inserts the edge $(v,v_{\text{ver}})$ into $E_{t}$, and  
initializes $\lambda_{t}(v_{\text{ver}})\leftarrow(\bot,\texttt{pending})$.

## Appendix A4 LATTE Implementation

### A4.1 Team composition

Each run consists of one Lead (Lead) and $N$ Worker agents (named Dev1 through DevN; $N=4$ in all experiments). All agents run the same underlying model with the same sampling parameters.

Lead agent. The Lead runs an isolated planning phase before execution begins. Given the natural-language task description, it has up to 5 turns to produce the initial task graph (nodes + dependency edges) via <discover\_task> actions. During execution the Lead monitors progress, issues <assign\_task> and <release\_task> directives, and can mutate the graph (add nodes, close stale ones). Its context window is capped at the last 10 messages.

Worker agents. Workers receive task assignments from the Lead and implement them. They can emit <claim\_task>, <complete\_task>, and <discover\_task> to propose adding new subtasks to the graph. Their context window is capped at the last 20 messages.

Concurrency. All agents run concurrently within a round — the orchestrator steps the Lead first, then dispatches Workers in parallel, collecting their responses before advancing to the next round.

### A4.2 Lead prompt

You are a senior software engineer leading a team of developers working collaboratively on coding tasks.

Responsibilities:

1. Understand the overall project goals and requirements
2. Break down work and strategically assign tasks to team members
3. Monitor progress and coordinate the team
4. Help unblock teammates when they face issues
5. Review work for quality and consistency
6. Synthesize results and ensure successful project completion

Work efficiently and delegate appropriately. Trust your teammates to handle their assignments, but provide guidance when needed. Keep communication clear and actionable.

Parallelism:

Teammates can self-assign from the ready queue — they do not need to wait for you. Your job is to keep the graph correct and handle failures, not to manually dispatch every task.

That said, proactively assign tasks when you know a specific agent is the right fit (e.g. after unblocking a straggler, after a verification completes). When several tasks are ready, assign them all at once, one per available agent.

However, be deliberate about what runs in parallel. Avoid assigning two agents to tasks that write to the same function simultaneously. A good rule: tasks that work on distinct functions or files can run in parallel; tasks that both modify the same shared data should be sequenced.

When possible, build a wide graph, not a deep one. Only use ‘dependencies’ to express real implementation ordering (i.e. “I can’t start B until A’s output exists”). Don’t chain tasks sequentially just for safety — if two tasks touch different functions or files, they can run in parallel with no ‘dependencies‘ between them.

With this structure, the moment task-analyze completes, all three implementation tasks become ready in parallel.

Available Actions:

Do NOT edit files yourself — focus on directing your team and verifying their work.

1. Assign a task to a teammate:
	```
	<assign_task id="task-1" to="AgentName" />
	```
2. Broadcast a message to all teammates (use this to coordinate work):
	```
	<broadcast>Your message here</broadcast>
	```
3. Run a Python script and see its output:
	```
	<run_script path="script.py" />
	```
4. Request status from agents:
	```
	<request_status />
	```
5. Run tests:
	```
	<run_tests />
	```
6. Graph updates. The task graph is a living document. Use <discover\_task> to add new tasks whenever: (a) A teammate reports that tests are still failing after completing their task, (b) you notice a dependency was missed or a prior task produced incorrect output, (c) the project needs a verification or integration pass that wasn’t planned upfront.
	Example: if Dev2 finishes implementing a function but broadcasts that tests are still red, add a fix task immediately rather than waiting:
	```
	<discover_task id="fix-index" title="Fix index() API bug"
	    dependencies="task-2">
	    Run <run_tests /> to see failures, fix search_lib.py,
	    confirm all tests pass.
	</discover_task>
	```
	The index function was implemented with dict input but the tests pass a list.
7. If a task is high-stakes — it is upstream of many other tasks, or its output is hard to validate later — you can request a verification pass by a second agent:
	```
	<verify_task id="task-X" />
	```
	This inserts a lightweight review task into the graph that must complete before downstream tasks proceed. The verifying agent will check correctness and fix any issues.
8. Straggler mitigation. If a teammate has been assigned a task for several rounds without completing it, they may be stuck. Use this action to release the task back to pending so it can be reassigned:
	```
	<release_task id="task-X" />
	```
	This clears the current owner and resets the task to pending. Then reassign it with
	```
	<assign_task id="task-X" to="DevY" />
	```
	either to a different agent or the same one with clearer instructions. Broadcast a message explaining what the agent should do differently before reassigning.
9. If the test suite is passing but tasks are still marked "assigned" or "in\_progress" (e.g. a teammate completed the work but forgot to emit <complete\_task>), you can close them directly:
	```
	<close_task id="task-X" />
	```
	Only use this after confirming with <run\_tests /> that tests pass. This is the right action when: all tests are green, a task’s work is clearly done in the codebase, and the owning agent is no longer making progress on it.

### A4.3 Worker prompt

You are a skilled software engineer working as part of a development team.

Responsibilities:

1. Work on tasks assigned to you by the Lead.
2. Write clean, well-documented code.
3. To read an existing file’s contents directly, use:
	```
	<read_file path="math_utils.py" />
	```
	This returns the file contents immediately — no script needed. Always prefer this over writing a helper script to print a file.
	To execute a script and see its output, use:
	```
	<run_script path="script.py" />
	```
	This runs the file and returns stdout/stderr to you. Use this to verify your code works before marking a task complete.
	> Important: `<run_script>` takes a.py filename only — it is not a shell. Do not pass shell commands like ls, head, or python3 script.py. To list files, write a short Python script first with `<edit_file>`, then run it with `<run_script>`. Example:
	```
	<edit_file path="check_files.py">
	import os; print(os.listdir(’.’))
	</edit_file>
	<run_script path="check_files.py" />
	```
4. Use `<run_tests />` to run the test suite and check your work.
	> Important: Do not mark a task complete if `<run_tests />` is still failing. If you finish your implementation and tests are still red, use `<discover_task>` to add a follow-up fix task rather than marking done and moving on. This keeps the problem visible to the whole team.
5. Communicate with the team Lead when blocked or in need of clarification.
6. Complete tasks thoroughly before moving to the next one.

Be proactive, collaborative, and detail-oriented. Focus on producing high-quality work.

Discovering New Tasks

Use `<discover_task>` whenever you uncover work that isn’t already in the task list. When possible, build a wide graph, not a deep one. Only use dependencies to express real implementation ordering (i.e., “I cannot start B until A’s output exists”).

```
<discover_task id="new-task-id" title="Short title"
dependencies="only-if-truly-required">
  Clear description of what needs to be done and why.
</discover_task>
```

### A4.4 Parameters

Sampling. All agents use a temperature of $0.7$ and a maximum output length of $4{,}096$ tokens per call.

Round limits. LATTE teams (and baseline teams) were given $40$ rounds total to complete each task. They could complete tasks more quickly by marking tasks as complete (either through the Lead or Workers in a decentralized team). Success was then evaluated based on if their implementations passed the given task’s test suite.

Heartbeat monitoring. We set $H=4$ for all experiments with LATTE. If a Worker was stuck on their subtask implementation for more than 4 rounds without emitting any action, the Lead was notified and prompted to intervene.

Claim tie-breaking. Worker agents were allowed to self-claim tasks from $F_{t}$ if idle. Concurrent claims were addressed via FIFO by processing order; when multiple Workers claim the same task in the same round, the orchestrator processes agents sequentially and the first claim processed wins, while subsequent claimants get an error message and must re-poll.

API retry. Anthropic and OpenAI requests rely on their respective SDK retry logic. No per-call wall-clock timeout was set.

### A4.5 LATTE Execution Protocol

Algorithm 1 LATTE Execution

Task description $\tau$, agents $\mathcal{A}=\{\ell\}\cup\mathcal{W}$, max rounds $T$, heartbeat threshold $H$

Final task graph $G_{T}$

Phase 0: Planning

$G_{0}\leftarrow\ell.\textsc{Discover}(\tau)$ $\triangleright$ Leader initializes coordination graph

Phase 1: Execution

for $t=1$ to $T$ do

 // 1. Heartbeat monitoring

  Flag to $\ell$ any $w\in\mathcal{W}$ with no actions in $H$ consecutive rounds

 // 2. Frontier identification

   $F_{t}\leftarrow\{v\in G_{t}:\textsc{Status}(v)=\texttt{pending},\ \forall u\in\textsc{Deps}(v):\ \textsc{Status}(u)=\texttt{done}\}$

 // 3. Agent dispatching

  Re-engage busy Workers that have received new context since last round

  Assign idle Workers to tasks in $F_{t}$, at most one Worker per task

  Invoke $\ell$ if $G_{t}$ has changed, a heartbeat was flagged, or $\ell$ has been idle for $H$ rounds

 // 4. Parallel execution

  All selected agents act in parallel:

    $\ell$ receives full graph $G_{t}$; Workers receive assigned task or $F_{t}$

   Each agent emits actions $\subseteq$ {Discover, Claim, Complete}

   $G_{t}\leftarrow\textsc{Apply}(G_{t-1},\ \text{all emitted actions})$

 // 5. Termination check

  if $\forall v\in G_{t}:\ \textsc{Status}(v)=\texttt{done}$ then

   return $G_{t}$

  end if

end for

return $G_{T}$

## Appendix A5 Baseline implementations

### A5.1 MetaGPT

We use the original paper-release codebase of MetaGPT [^22], corresponding to the version publicly available at the time of the ICLR 2024 submission (commit tag v0.1, authored April–August 2023) because it faithfully instantiates the fixed Standard Operating Procedure (SOP) described in the paper.

Pipeline. MetaGPT structures collaboration as a fixed, sequential SOP over five role-conditioned agents:

1. ProductManager (Alice) translates the task description into a Product Requirements Document (PRD), user stories, and a competitive analysis.
2. Architect (Bob) receives the PRD and produces a system design document, including the Python package name, file structure, and API specifications.
3. ProjectManager (Eve) reads the system design and issues a task list to the Engineer.
4. Engineer (Alex, $\texttt{n\_borg}=1$) implements the assigned files sequentially, one file per action, emitting code blocks to shared memory.
5. QaEngineer (Edward, $\texttt{test\_round\_allowed}=5$) watches for Engineer output and iterates a write-test $\to$ run-code $\to$ debug-error loop up to the allowed round count.

Agents communicate exclusively through a shared publish-subscribe message bus: each role watches a fixed set of upstream action types and acts only when a matching message arrives. The task decomposition, which files to write, what each contains, and in what order, is determined entirely during the planning phases (steps 1–3) and cannot be revised during execution.

Parameters. All agents use the same model and sampling parameters as the LATTE and baseline runs described in Appendix A4. Each MetaGPT run is allocated n\_round $=40$ total team rounds to match the other team conditions. The QaEngineer is initialized with test\_round\_allowed $=5$, matching the upper bound of debug-and-fix cycles in the original paper.

*Mismatch between SOP outputs and task evaluation.* Because each role in the sequential pipeline operates on the prior role’s output rather than the shared task environment, artifacts accumulate in locations determined by the Architect’s upfront design rather than by where the task expects them. More broadly, because the task decomposition is committed before any code is executed, the Engineer cannot discover latent task structure such as which functions share internal helpers, which bugs are actually present in a given file, or which data columns carry the signal of interest. On nonstationary tasks where the correct decomposition only becomes apparent during execution, the upfront plan is systematically misspecified, and the SOP provides no mechanism to revise it.

### A5.2 Leader-Worker Hierarchies

Leader-Worker teams were implemented using a lightweight orchestrator with no task-graph infrastructure. Agents could edit files, run scripts, run tests, and broadcast messages to teammates. Unlike the graph-based conditions, there was no planning phase and no task state. Coordination relied entirely on the Lead broadcasting directions and teammates editing files in response.

At the start of each round the orchestrator appended the latest test output to every agent’s context window. The Lead then ran first, followed by all $N$ teammates in parallel. After each round the orchestrator ran the test suite internally to detect success. A run was marked successful when all tests passed and the Lead certified task completion.

#### Lead prompt

You are a senior software engineer leading a team of developers working collaboratively on coding tasks.

Responsibilities:

1. Understand the overall project goals and requirements
2. Break down work and strategically assign tasks to team members
3. Monitor progress and coordinate the team
4. Help unblock teammates when they face issues
5. Review work for quality and consistency
6. Synthesize results and ensure successful project completion

Work efficiently and delegate appropriately. Trust your teammates to handle their assignments, but provide guidance when needed. Keep communication clear and actionable.

Available Actions:

Do NOT edit files yourself — focus on directing your team and verifying their work.

1. Broadcast a message to all teammates (use this to coordinate work):
	```
	<broadcast>Your message here</broadcast>
	```
2. Run a Python script and see its output:
	```
	<run_script path="script.py" />
	```

#### Worker prompt

You are a skilled software engineer working as part of a development team.

Responsibilities:

1. Work on tasks assigned to you by the Lead.
2. Write clean, well-documented code.
3. To read an existing file’s contents directly, use:
	```
	<read_file path="math_utils.py" />
	```
	This returns the file contents immediately — no script needed. Always prefer this over writing a helper script to print a file.
	To execute a script and see its output, use:
	```
	<run_script path="script.py" />
	```
	This runs the file and returns stdout/stderr to you. Use this to verify your code works before marking a task complete.
	> Important: `<run_script>` takes a.py filename only — it is not a shell. Do not pass shell commands like ls, head, or python3 script.py. To list files, write a short Python script first with `<edit_file>`, then run it with `<run_script>`. Example:
	```
	<edit_file path="check_files.py">
	import os; print(os.listdir(’.’))
	</edit_file>
	<run_script path="check_files.py" />
	```
4. Use `<run_tests />` to run the test suite and check your work.
	> Important: Do not mark a task complete if `<run_tests />` is still failing.
5. Communicate with the team lead when blocked or in need of clarification.
6. Complete tasks thoroughly before moving to the next one.

Be proactive, collaborative, and detail-oriented. Focus on producing high-quality work.

### A5.3 Decentralized Teams

Decentralized teams used the same lightweight orchestrator and action vocabulary as the Leader-Worker condition, but with no designated Leader. To hold agent count constant across conditions, we instantiated $N{+}1$ symmetric peer agents (matching the $1$ Lead $+N$ Worker headcount of the other conditions). All agents ran in parallel every round with no sequential ordering; coordination relied solely on broadcast messages. As in the Leader-Worker condition, the latest test output was appended to every agent’s context at the start of each round, and success was detected by running the test suite internally and any agent marking task completion.

#### Peer prompt

You are a skilled software engineer working as part of a development team.

Responsibilities:

1. Work on your tasks efficiently and effectively
2. Write clean, well-documented code
3. To read an existing file’s contents directly, use:
	```
	<read_file path="math_utils.py" />
	```
	This returns the file contents immediately — no script needed. Always prefer this over writing a helper script to print a file.
	To execute a script and see its output, use:
	```
	<run_script path="script.py" />
	```
	This runs the file and returns stdout/stderr to you. Use this to verify your code works before marking a task complete.
	> Important: `<run_script>` takes a.py filename only — it is not a shell. Do not pass shell commands like ls, head, or python3 script.py. To list files, write a short Python script first with `<edit_file>`, then run it with `<run_script>`. Example:
	```
	<edit_file path="check_files.py">
	import os; print(os.listdir(’.’))
	</edit_file>
	<run_script path="check_files.py" />
	```
4. Use `<run_tests />` to run the test suite and check your work.
5. Communicate with your teammates as needed.
6. Complete tasks thoroughly before moving to the next one.

Be proactive, collaborative, and detail-oriented. Focus on producing high-quality work.

### A5.4 Static Graph Ablation

The static condition used the same graph-based orchestrator as the dynamic condition, but with task discovery and reassignment disabled after the planning phase. During planning, the Lead received a prompt instructing it to emit a complete task graph upfront, specifying every task and its dependencies before execution began. Once planning concluded, the graph was frozen: mid-run task discovery (discover\_task), straggler release (release\_task), verification insertion (verify\_task), and automatic fix-task injection on test failure were all disabled at the orchestrator level. Teammates could not self-assign; the Lead was responsible for assigning every task at the start of execution via assign\_task. All $N$ teammates were dispatched every round regardless of task availability. If a teammate failed to complete an assigned task, no recovery mechanism was available.

### A5.5 Lead prompt

You are a senior software engineer leading a team of developers working collaboratively on coding tasks.

Responsibilities

1. Understand the overall project goals and requirements
2. Break down work and strategically assign tasks to team members upfront
3. Monitor progress and answer questions from teammates
4. Synthesize results and ensure successful project completion

Work efficiently and delegate appropriately. Trust your teammates to handle their assignments.

Parallelism

Teammates do not self-assign — you must assign every task. Assign all ready tasks at the start, distributing work evenly across available agents.

Be deliberate about what runs in parallel. Avoid assigning two agents to tasks that write to the same function simultaneously. A good rule: tasks that work on distinct functions or files can run in parallel; tasks that both modify the same shared data should be sequenced.

When possible, build a wide graph, not a deep one. Only use ‘dependencies’ to express real implementation ordering (i.e. “I can’t start B until A’s output exists”). Don’t chain tasks sequentially just for safety — if two tasks touch different functions or files, they can run in parallel with no ‘dependencies‘ between them. With this structure, the moment task-analyze completes, all three implementation tasks become ready in parallel.

Available Actions

Do NOT edit files yourself — focus on directing your team and verifying their work.

1. Assign a task to a teammate:
	```
	<assign_task id="task-1" to="AgentName" />
	```
2. Broadcast a message to all teammates (use this to coordinate work):
	```
	<broadcast>Your message here</broadcast>
	```
3. Run a Python script and see its output:
	```
	<run_script path="script.py" />
	```
4. Request status from agents:
	```
	<request_status />
	```
5. Run tests:
	```
	<run_tests />
	```
6. Fixed plan. The task decomposition and assignments are fixed at the start. Once tasks are assigned, they run to completion without reassignment or modification. Your job is to: (a) Assign all tasks upfront based on the task graph and agent availability. (b) Answer teammates’ questions via broadcast if they get stuck. (c) Run tests at the end to confirm completion.
	You cannot release tasks, reassign workers, or insert new tasks once execution has begun. If a teammate fails to complete a task, the team absorbs that outcome — do not attempt to recover by reassigning.

### A5.6 Worker prompt

You are a skilled software engineer working as part of a development team.

Responsibilities

1. Work on tasks assigned to you by the Lead.
2. Write clean, well-documented code.
3. To read an existing file’s contents directly, use:
	```
	<read_file path="math_utils.py" />
	```
	This returns the file contents immediately — no script needed. Always prefer this over writing a helper script to print a file.
	To execute a script and see its output, use:
	```
	<run_script path="script.py" />
	```
	This runs the file and returns stdout/stderr to you. Use this to verify your code works before marking a task complete.
	> Important: `<run_script>` takes a.py filename only — it is not a shell. Do not pass shell commands like ls, head, or python3 script.py. To list files, write a short Python script first with `<edit_file>`, then run it with `<run_script>`. Example:
	```
	<edit_file path="check_files.py">
	import os; print(os.listdir(’.’))
	</edit_file>
	<run_script path="check_files.py" />
	```
4. Use `<run_tests />` to run the test suite and check your work.
	> Important: Do not mark a task complete if `<run_tests />` is still failing. If you finish your implementation and tests are still red, use `<discover_task>` to add a follow-up fix task rather than marking done and moving on. This keeps the problem visible to the whole team.
5. Communicate with the team lead when blocked or in need of clarification.
6. Complete tasks thoroughly before moving to the next one.

Be proactive, collaborative, and detail-oriented. Focus on producing high-quality work.

## Appendix A6 Experiments

### A6.1 Setup

Task 1: Exploratory data analysis Identifying meaningful patterns in a dataset is inherently time-consuming and open-ended. The process begins with preprocessing and filtering, which can be handled by a single agent. Subsequently, multiple agents can explore the data in parallel along diverse directions (e.g., characterizing distributions, identifying outliers, generating visualizations). A final agent can then aggregate and synthesizes these findings. Importantly, purely static task decompositions are likely to be suboptimal because the underlying structure of the data and promising directions only emerge during analysis.

We first simulated a tabular HR dataset containing 400 employee records with eight deliberately opaque column names and no data dictionary. Three ground-truth properties were planted in the data: (1) employee satisfaction score is the dominant churn predictor, (2) salary follows a bimodal distribution reflecting two workforce tiers, and (3) churn rate varies substantially by department. Agents were tasked with producing three interdependent artifacts: a config.py establishing the shared column-name mapping and feature schema (the foundation all downstream scripts must import), a structured findings.json with quantitative supporting evidence across five analytic categories (distributions, relationships, subgroup effects, outliers, and missing data), and a written summary.txt narrative of at least 100 words. Correctness is evaluated by a private test suite that checks whether the true churn column was identified, whether the column–feature classification matches the data types, and whether each of the three planted properties appears in the findings with correct directional claims.

Task 2: Debugging Debugging is another task which is inherently nonstationary; agents must run tests, read outputs, change the code to solve potentially multiple errors, and repeat the process until the problems are solved. It also rewards both parallelism and consistency, since multiple agents can simultaneously diagnose independent errors, yet some errors require changes to composite functions that can only be verified after dependencies are fixed. In Task 2, we planted 8 bugs (1 per function) in a Python signal-processing library covering a range of common numerical mistakes, such as a $+1$ in the normalization denominator or inequality errors. Unlike Task 1, in which performance was evaluated after the agents marked task completion, the team had access to the full test suite. Success required all tests in the public test suite to pass.

Task 3: Library extension Finally, code generation is a task that is inherently time consuming; teams of agents can improve performance by working in parallel to generate independent parts of a codebase. In this task, agents were given a partially implemented Python text-processing library with three working files: a Document class, Tokenizer class, and utils module. They must extend the existing classes and build six new modules from stub files: sentiment.py, keywords.py, summarizer.py, similarity.py, formatter.py, and pipeline.py. Each stage of generation required different numbers of agents: two existing classes must be extended first, which only required two agents to change; then, the new modules could be generated independently in parallel, and finally only one agent needed to integrate everything into the final pipeline. Agents were encouraged to write their own tests, and correctness was determined after they mark test completion by a private test suite which tests common outputs and edge cases.

### A6.2 Trials

For each base model, we ran a total of 150 trials (3 tasks, 5 team structures, 10 repetitions). For Claude Sonnet 4-6, this amounted to 2,136 API cells, 40.7M input tokens, and 8.5M output tokens (approximately $250). For GPT 5.2, this amounted to 4,582 API calls, 83.1M input tokens, 14M output tokens (approximately $260).

### A6.3 Planning Overhead Analysis

LATTE’s adaptivity introduces two components of orchestration cost. First, an initial planning phase in which the Lead seeds the task graph: dynamic conditions seed a mean of 3.8 ($\pm 2.0$) nodes in 14.5s, compared to 8.3 ($\pm 1.8$) in 16.7s for static, which front-loads the full decomposition. Second, in-execution orchestration: the Lead remains active in, on average, 30.8% of of execution rounds under dynamic versus 14.8% for static, adding a mean of 0.9 extra lead-active rounds per run.

While these are real costs, they do not outweigh the benefits that LATTE provides to teams for dynamic and complex tasks. Across all tasks and models, dynamic conditions complete in a mean of 9.8 rounds and 148K tokens, compared to 15.9 rounds and 297K tokens for static. Thus, each extra lead-active round of dynamic overhead yields approximately six fewer total rounds of Worker execution.

[^1]: K. Agrawal, C. E. Leiserson, and J. Sukha (2010) Executing task graphs using work-stealing. In 2010 IEEE International Symposium on Parallel & Distributed Processing (IPDPS), pp. 1–12. Cited by: §A1.2, §1, §2, §3.2.

[^2]: Anthropic (2025-06) How we built our multi-agent research system. Note: [https://www.anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) Anthropic Engineering Blog Cited by: §1.

[^3]: F. Berdoz, L. Rugli, and R. Wattenhofer (2026) Can AI agents agree?. arXiv preprint arXiv:2603.01213. Cited by: §1.

[^4]: M. Besta, N. Blach, A. Kubicek, R. Gerstenberger, M. Podstawski, L. Gianinazzi, J. Gajda, T. Lehmann, H. Niewiadomski, P. Nyczyk, et al. (2024) Graph of thoughts: Solving elaborate problems with Large Language Models. Proceedings of the AAAI Conference on Artificial Intelligence 38 (16), pp. 17682–17690. External Links: [Document](https://dx.doi.org/10.1609/aaai.v38i16.29720) Cited by: §A1.1.

[^5]: A. Bhattacharyya, A. Borah, Y. K. Singla, R. R. Shah, C. Chen, and B. Krishnamurthy (2026) Social agents: collective intelligence improves LLM predictions. In The Fourteenth International Conference on Learning Representations, Cited by: §A1.1, §1.

[^6]: F. P. Brooks (1975) The mythical man-month: essays on software engineering. Addison-Wesley, Reading, MA. External Links: ISBN 0-201-00650-2 Cited by: §1.

[^7]: M. Cataldo, J. D. Herbsleb, and K. M. Carley (2008) Socio-technical congruence: a framework for assessing the impact of technical and work dependencies on software development productivity. In Proceedings of the Second ACM-IEEE International Symposium on Empirical Software Engineering and Measurement (ESEM), Kaiserslautern, Germany, pp. 2–11. External Links: [Document](https://dx.doi.org/10.1145/1414004.1414008) Cited by: §1.

[^8]: M. Cemri, M. Z. Pan, S. Yang, L. A. Agrawal, B. Chopra, R. Tiwari, K. Keutzer, A. Parameswaran, D. Klein, K. Ramchandran, et al. (2025) Why do multi-agent LLM systems fail?. arXiv preprint arXiv:2503.13657. Cited by: §5.3.

[^9]: M. E. Conway (1968-04) How do committees invent?. Datamation 14 (4), pp. 28–31. Cited by: §1.

[^10]: J. Dean and L. A. Barroso (2013) The tail at scale. Communications of the ACM 56 (2), pp. 74–80. External Links: [Document](https://dx.doi.org/10.1145/2408776.2408794) Cited by: §1.

[^11]: J. Dean and S. Ghemawat (2008-01) MapReduce: simplified data processing on large clusters. Communications of the ACM 51 (1), pp. 107–113. External Links: [Document](https://dx.doi.org/10.1145/1327452.1327492) Cited by: §A1.2, §5.3.

[^12]: T. G. Dietterich (2000) Hierarchical reinforcement learning with the MAXQ value function decomposition. Journal of Artificial Intelligence Research 13, pp. 227–303. Cited by: §A1.2.

[^13]: Q. Dong, L. Li, D. Dai, C. Zheng, J. Ma, R. Li, H. Xia, J. Xu, Z. Wu, B. Chang, et al. (2024) A survey on in-context learning. In Proceedings of the 2024 conference on empirical methods in natural language processing, pp. 1107–1128. Cited by: §1.

[^14]: Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch (2024) Improving factuality and reasoning in language models through multiagent debate. In Forty-first International Conference on Machine Learning, Cited by: §A1.1, §2.

[^15]: G. Ghiotto, L. Murta, M. Barros, and A. van der Hoek (2020) On the nature of merge conflicts: a study of 2,731 open source Java projects hosted by GitHub. IEEE Transactions on Software Engineering 46 (8), pp. 892–915. External Links: [Document](https://dx.doi.org/10.1109/TSE.2018.2871083) Cited by: §1.

[^16]: N. Gopalan, M. Littman, J. MacGlashan, S. Squire, S. Tellex, J. Winder, and L. Wong (2017) Planning with abstract Markov decision processes. In Proceedings of the International Conference on Automated Planning and Scheduling, Vol. 27, pp. 480–488. Cited by: §A1.2.

[^17]: T. L. Griffiths, F. Callaway, M. B. Chang, E. Grant, P. M. Krueger, and F. Lieder (2019) Doing more with less: meta-reasoning and meta-learning in humans and machines. Current Opinion in Behavioral Sciences 29, pp. 24–30. Cited by: Appendix A2.

[^18]: W. K. Hastings (1970) Monte Carlo sampling methods using Markov chains and their applications. Biometrika 57 (1), pp. 97–109. External Links: [Document](https://dx.doi.org/10.1093/biomet/57.1.97) Cited by: Appendix A2.

[^19]: N. Hay, S. Russell, D. Tolpin, and S. E. Shimony (2012) Selecting computations: theory and applications. In Proceedings of the Twenty-Eighth Conference on Uncertainty in Artificial Intelligence, pp. 346–355. Cited by: Appendix A2.

[^20]: J. Henrich (2015) The secret of our success: how culture is driving human evolution, domesticating our species, and making us smarter. Princeton University Press, Princeton, NJ. External Links: ISBN 9780691166858 Cited by: §1.

[^21]: J. D. Herbsleb and A. Mockus (2003) An empirical study of speed and communication in globally distributed software development. IEEE Transactions on Software Engineering 29 (6), pp. 481–494. External Links: [Document](https://dx.doi.org/10.1109/TSE.2003.1205177) Cited by: §1.

[^22]: S. Hong, M. Zhuge, J. Chen, X. Zheng, Y. Cheng, J. Wang, C. Zhang, Z. Wang, S. K. S. Yau, Z. Lin, et al. (2023) MetaGPT: Meta programming for a multi-agent collaborative framework. In The Twelfth International Conference on Learning Representations, Cited by: §A1.1, §A1.1, §A5.1, §1, §2, §4.

[^23]: J. Huang, J. Zhou, T. Jin, X. Zhou, Z. Chen, W. Wang, Y. Yuan, M. R. Lyu, and M. Sap (2024) On the resilience of LLM-based multi-agent collaboration with faulty agents. arXiv preprint arXiv:2408.00989. Cited by: §6.

[^24]: Y. Jo and C. Park (2025) Byzantine-robust decentralized coordination of LLM agents. arXiv preprint arXiv:2507.14928. Cited by: §1.

[^25]: T. Johnson (1993) A concurrent dynamic task graph. In 1993 International Conference on Parallel Processing-ICPP’93, Vol. 2, pp. 223–230. Cited by: §A1.2, §2.

[^26]: Y. Kim, K. Gu, C. Park, C. Park, S. Schmidgall, A. A. Heydari, Y. Yan, Z. Zhang, Y. Zhuang, M. Malhotra, et al. (2025) Towards a science of scaling agent systems. arXiv preprint arXiv:2512.08296. Cited by: §A1.1, §1, §2.

[^27]: S. T. Langlois, O. Akoroda, E. Carrillo, J. W. Herrmann, S. Azarm, H. Xu, and M. Otte (2020) Metareasoning structures, problems, and modes for multiagent systems: a survey. IEEE Access 8, pp. 183080–183089. Cited by: Appendix A2.

[^28]: A. Li, Y. Xie, S. Li, F. Tsung, B. Ding, and Y. Li (2025) Agent-oriented planning in multi-agent systems. In The Thirteenth International Conference on Learning Representations, Cited by: §A1.1, §2.

[^29]: J. Li, Q. Zhang, Y. Yu, Q. Fu, and D. Ye (2024) More agents is all you need. arXiv preprint arXiv:2402.05120. Cited by: §A1.1, §1, §2.

[^30]: N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, and P. Liang (2024) Lost in the middle: how language models use long contexts. Transactions of the Association for Computational Linguistics 12, pp. 157–173. Cited by: Appendix A2.

[^31]: S. Liu, T. Chen, R. Amiri, and C. Amato (2026) Learning decentralized LLM collaboration with multi-agent actor critic. arXiv preprint arXiv:2601.21972. Cited by: §1.

[^32]: A. MacCormack, C. Baldwin, and J. Rusnak (2012) Exploring the duality between product and organizational architectures: a test of the “mirroring” hypothesis. Research Policy 41 (8), pp. 1309–1324. External Links: [Document](https://dx.doi.org/10.1016/j.respol.2012.04.011) Cited by: §1.

[^33]: G. Malewicz, M. H. Austern, A. J. C. Bik, J. C. Dehnert, I. Horn, N. Leiser, and G. Czajkowski (2010) Pregel: a system for large-scale graph processing. In Proceedings of the 2010 ACM SIGMOD International Conference on Management of Data (SIGMOD ’10), Indianapolis, Indiana, USA, pp. 135–146. External Links: [Document](https://dx.doi.org/10.1145/1807167.1807184) Cited by: §A1.2.

[^34]: H. Mao, M. Schwarzkopf, S. B. Venkatakrishnan, Z. Meng, and M. Alizadeh (2019) Learning scheduling algorithms for data processing clusters. In Proceedings of the ACM Special Interest Group on Data Communication (SIGCOMM), pp. 270–288. External Links: [Document](https://dx.doi.org/10.1145/3341302.3342080) Cited by: §A1.2, §1.

[^35]: E. Mieczkowski, K. M. Collins, I. Sucholutsky, N. Vélez, and T. L. Griffiths (2026) Language model teams as distributed systems. arXiv preprint arXiv:2603.12229. Cited by: §A1.1, §1, §2, §5.3, §5.3.

[^36]: P. Moritz, R. Nishihara, S. Wang, A. Tumanov, R. Liaw, E. Liang, M. Elibol, Z. Yang, W. Paul, M. I. Jordan, and I. Stoica (2018) Ray: a distributed framework for emerging AI applications. In 13th USENIX Symposium on Operating Systems Design and Implementation (OSDI 18), pp. 561–577. Cited by: §A1.2, §A1.2, §2.

[^37]: A. Pappu, B. El, H. Cao, C. di Nolfo, Y. Sun, M. Cao, and J. Zou (2026) Multi-agent teams hold experts back. arXiv preprint arXiv:2602.01011. Cited by: §A1.1, §1, §2.

[^38]: J. S. Park, J. C. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein (2023) Generative agents: interactive simulacra of human behavior. In Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology, External Links: [Document](https://dx.doi.org/10.1145/3586183.3606763) Cited by: §1.

[^39]: C. D. Polychronopoulos and D. J. Kuck (1987-12) Guided self-scheduling: a practical scheduling scheme for parallel supercomputers. IEEE Transactions on Computers C-36 (12), pp. 1425–1439. External Links: [Document](https://dx.doi.org/10.1109/TC.1987.5009495) Cited by: §3.2, §3.4.

[^40]: C. Qian, W. Liu, H. Liu, N. Chen, Y. Dang, J. Li, C. Yang, W. Chen, Y. Su, X. Cong, et al. (2024) Chatdev: communicative agents for software development. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics, pp. 15174–15186. Cited by: §A1.1, §A1.1, §1, §2.

[^41]: A. Raja and V. Lesser (2007) A framework for meta-level control in multi-agent systems. Autonomous Agents and Multi-Agent Systems 15 (2), pp. 147–196. Cited by: Appendix A2.

[^42]: C. Riedl (2025) Emergent coordination in multi-agent language models. arXiv preprint arXiv:2510.05174. Cited by: §1.

[^43]: M. Rizvi-Martel, S. Bhattamishra, N. Rathi, G. Rabusseau, and M. Hahn (2025) Benefits and limitations of communication in multi-agent reasoning. arXiv preprint arXiv:2510.13903. Cited by: §A1.1.

[^44]: S. Russell and E. Wefald (1991) Principles of metareasoning. Artificial Intelligence 49 (1-3), pp. 361–395. Cited by: Appendix A2.

[^45]: H. Sackman, W. J. Erikson, and E. E. Grant (1968) Exploratory experimental studies comparing online and offline programming performance. Communications of the ACM 11 (1), pp. 3–11. External Links: [Document](https://dx.doi.org/10.1145/362851.362858) Cited by: §1.

[^46]: N. Shapira, C. Wendler, A. Yen, G. Sarti, K. Pal, O. Floody, A. Belfki, A. Loftus, A. R. Jannali, N. Prakash, et al. (2026) Agents of chaos. arXiv preprint arXiv:2602.20021. Cited by: §A1.1, §1, §2.

[^47]: Y. Shen, K. Song, X. Tan, D. Li, W. Lu, and Y. Zhuang (2023) HuggingGPT: solving AI tasks with ChatGPT and its friends in Hugging Face. In Advances in Neural Information Processing Systems 36 (NeurIPS 2023), Cited by: §A1.1, §2.

[^48]: J. Sleight and E. Durfee (2014) Multiagent metareasoning through organizational design. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 28. Cited by: Appendix A2.

[^49]: K. Swanson, W. Wu, N. L. Bulaong, J. E. Pak, and J. Zou (2025) The virtual lab of AI agents designs new SARS-CoV-2 nanobodies. Nature 646 (8085), pp. 716–723. Cited by: §A1.1, §1.

[^50]: M. Tomasello, M. Carpenter, J. Call, T. Behne, and H. Moll (2005) Understanding and sharing intentions: the origins of cultural cognition. Behavioral and Brain Sciences 28 (5), pp. 675–691. Cited by: §1.

[^51]: H. Topcuoglu, S. Hariri, and M. Wu (2002) Performance-effective and low-complexity task scheduling for heterogeneous computing. IEEE Transactions on Parallel and Distributed Systems 13 (3), pp. 260–274. Cited by: §A1.2, §2.

[^52]: M. Van Steen and A. S. Tanenbaum (2023) Distributed systems. distributed-systems.net. Cited by: §A1.2.

[^53]: J. Wei, X. Wang, D. Schuurmans, M. Bosma, F. Xia, E. Chi, Q. V. Le, D. Zhou, et al. (2022) Chain-of-thought prompting elicits reasoning in large language models. Advances in Neural Information Processing Systems 35, pp. 24824–24837. Cited by: §A1.1.

[^54]: L. Williams, R. R. Kessler, W. Cunningham, and R. Jeffries (2000) Strengthening the case for pair programming. IEEE Software 17 (4), pp. 19–25. Cited by: §1.

[^55]: S. Woo, S. Yang, S. Kim, and T. Han (1997) Task scheduling in distributed computing systems with a genetic algorithm. In Proceedings High Performance Computing on the Information Superhighway. HPC Asia’97, pp. 301–305. Cited by: §A1.2, §1.

[^56]: Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, et al. (2024) Autogen: Enabling next-gen LLM applications via multi-agent conversations. In First Conference on Language Modeling, Cited by: §1.

[^57]: Y. Yang, C. Qu, M. Wen, L. Shi, Y. Wen, W. Zhang, A. Wierman, and S. Gu (2026) Understanding agent scaling in LLM-based multi-agent systems via diversity. arXiv preprint arXiv:2602.03794. Cited by: §A1.1.

[^58]: S. Yao, D. Yu, J. Zhao, I. Shafran, T. Griffiths, Y. Cao, and K. Narasimhan (2023) Tree of thoughts: deliberate problem solving with large language models. Advances in Neural Information Processing Systems 36, pp. 11809–11822. Cited by: §A1.1.

[^59]: G. Zhang, Y. Yue, Z. Li, S. Yun, G. Wan, K. Wang, D. Cheng, J. X. Yu, and T. Chen (2024) Cut the crap: an economical communication pipeline for LLM-based multi-agent systems. arXiv preprint arXiv:2410.02506. Cited by: §5.3.

[^60]: T. J. Zhang, W. Jiang, Y. Yang, S. Lu, B. Schölkopf, and Z. Jin (2026) Position: Science is collaborative—LLM for science should be too. In ICLR 2026 Workshop on Foundation Models for Science: Real-World Impact, Note: Oral Cited by: §A1.1.

[^61]: Y. Zhang, R. Sun, Y. Chen, T. Pfister, R. Zhang, and S. Arik (2024) Chain of agents: Large language models collaborating on long-context tasks. Advances in Neural Information Processing Systems 37, pp. 132208–132237. Cited by: §A1.1, §1.

[^62]: D. Zhou, N. Schärli, L. Hou, J. Wei, N. Scales, X. Wang, D. Schuurmans, C. Cui, O. Bousquet, Q. V. Le, and E. H. Chi (2023) Least-to-most prompting enables complex reasoning in large language models. In The Eleventh International Conference on Learning Representations, Cited by: §A1.1.