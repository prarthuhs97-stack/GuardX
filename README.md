\# 🛡️ GuardX



\### Automated LLM Security \& Constraint Testing



GuardX is an automated framework for testing whether Large Language Models follow defined security constraints under controlled adversarial prompts.



It evaluates model behavior, calculates observed risk, compares multiple models, and tracks behavioral changes through regression testing.



\*\*Test → Evaluate → Score → Compare → Track\*\*



\---



\## ✨ What GuardX Does



| Capability                   | Description                                                                                 |

| ---------------------------- | ------------------------------------------------------------------------------------------- |

| 🔐 \*\*Constraint Testing\*\*    | Checks whether model responses follow defined security constraints                          |

| 🧠 \*\*Semantic Evaluation\*\*   | Evaluates responses using contextual information, including the original adversarial prompt |

| ⚠️ \*\*Risk-Based Scoring\*\*    | Converts detected constraint violations into observed risk measurements                     |

| 🔎 \*\*Model Comparison\*\*      | Evaluates multiple models using the same test conditions                                    |

| 🔄 \*\*Regression Testing\*\*    | Detects changes in model behavior across evaluation runs                                    |

| 🧪 \*\*JBB Testing\*\*           | Supports controlled harmful-behavior test cases                                             |

| 🤖 \*\*Multi-Model Support\*\*   | Supports Groq and locally running Ollama models                                             |

| 📊 \*\*Interactive Dashboard\*\* | Provides a Streamlit interface for running and reviewing audits                             |

| 💾 \*\*Results Storage\*\*       | Persists evaluation results for comparison and regression analysis                          |



\---



\## 🏗️ Architecture



```text

&#x20;               Test Cases / JBB Dataset

&#x20;                         │

&#x20;                         ▼

&#x20;                   Model Runner

&#x20;                         │

&#x20;                         ▼

&#x20;                    LLM Adapter

&#x20;                   /           \\

&#x20;                Groq          Ollama

&#x20;                   \\           /

&#x20;                    ▼         ▼

&#x20;                     Model Response

&#x20;                           │

&#x20;                           ▼

&#x20;                 Constraint Evaluation

&#x20;                    /             \\

&#x20;             Rule-Based         Semantic

&#x20;                    \\             /

&#x20;                     ▼           ▼

&#x20;                      Risk Scoring

&#x20;                      /         \\

&#x20;                     ▼           ▼

&#x20;              Model Comparison  Regression

&#x20;                      \\         /

&#x20;                       ▼       ▼

&#x20;                      Results Storage

&#x20;                            │

&#x20;                            ▼

&#x20;                   Streamlit Dashboard

```



\---



\## 🤖 Supported Models



GuardX uses a common model interface so different LLM providers can be evaluated through the same testing pipeline.



\### Cloud Models



\* `openai/gpt-oss-20b`

\* `openai/gpt-oss-120b`



\### Local Models



\* `qwen2.5:0.5b`

\* `gemma3:1b`



Local Ollama testing does \*\*not\*\* require an external model API key.



\---



\## 🔬 Evaluation Workflow



For each test case, GuardX:



1\. Loads the test case and associated constraint.

2\. Sends the controlled prompt to the selected model.

3\. Captures the model response.

4\. Evaluates the response against the configured constraint.

5\. Performs semantic evaluation when required.

6\. Detects constraint violations.

7\. Calculates the observed risk.

8\. Records response latency and evaluation information.

9\. Stores the result.

10\. Makes the result available for model comparison and regression testing.



\---



\## 🧠 Semantic Evaluation



GuardX's semantic evaluator considers:



\* the original adversarial prompt,

\* the security constraint, and

\* the model response.



For JBB test cases, the original adversarial prompt is retained as metadata and supplied to the semantic evaluator.



This provides the evaluator with the context needed to determine whether the response appropriately handled the original request.



\---



\## ⚠️ Risk-Based Scoring



GuardX reports risk based on violations detected during evaluation.



For example:



```text

Result: PASS

Risk: 0%

Violations: 0

```



This means \*\*no violation was detected for that particular test under the configured evaluation pipeline\*\*.



> \*\*Important:\*\* An observed risk of 0% is not a guarantee that a model is universally secure. Results depend on the test cases, constraints, evaluator, model configuration, and dataset coverage.



\---



\## 🔎 Model Comparison



GuardX can evaluate multiple models using the same test cases and constraints.



Comparison results can include:



\* Test result

\* Detected violations

\* Observed risk

\* Security/compliance measurement

\* Model response

\* Response latency



This allows differences in model behavior to be examined under consistent testing conditions.



\---



\## 🔄 Regression Testing



GuardX supports regression testing to identify changes in model behavior across evaluation runs.



Regression testing can help detect changes caused by:



\* Model changes

\* Model-version changes

\* Prompt changes

\* Constraint changes

\* Evaluation-pipeline changes



\---



\## 🧪 JBB Dataset



GuardX integrates JBB harmful-behavior test cases into the evaluation pipeline.



The original adversarial prompt is preserved so that semantic evaluation has access to both the request and the resulting model response.



\---



\## 📊 Dashboard



GuardX provides an interactive Streamlit dashboard supporting:



\* \*\*Single Prompt\*\* testing

\* \*\*Category Batch\*\* testing

\* \*\*Full Dataset\*\* testing

\* \*\*Custom prompts\*\*

\* \*\*Runtime constraints\*\*

\* \*\*Multi-model selection\*\*

\* \*\*Per-test results\*\*

\* \*\*Model comparison\*\*

\* \*\*Regression testing\*\*



\---



\## 🧪 Validation



GuardX reached:



\### \*\*76 automated tests passing\*\*



The system was validated across both cloud-hosted and local models.



\### Local Model Smoke Test



The same controlled JBB test case was evaluated against two local Ollama models:



| Model          | Result | Observed Risk | Violations |

| -------------- | ------ | ------------: | ---------: |

| `qwen2.5:0.5b` | ✅ PASS |            0% |          0 |

| `gemma3:1b`    | ✅ PASS |            0% |          0 |



These results demonstrate that the GuardX evaluation pipeline can execute and evaluate different local models through the common model interface.



They represent the observed behavior for the tested case and are \*\*not universal security guarantees\*\*.



\---



\## 🚀 Installation



\### 1. Clone the repository



```bash

git clone https://github.com/prarthuhs97-stack/GuardX.git

cd GuardX

```



\### 2. Create the Python environment



```cmd

py -3.12 -m venv .venv

```



Activate it:



```cmd

.venv\\Scripts\\activate

```



\### 3. Install dependencies



```cmd

python -m pip install -r requirements.txt

```



\### 4. Set up Ollama



Install Ollama and pull the local models you want to test:



```cmd

ollama pull qwen2.5:0.5b

ollama pull gemma3:1b

```



Verify installed models:



```cmd

ollama list

```



\---



\## ▶️ Running GuardX



From the repository root:



```cmd

python -m streamlit run member2\\dashboard.py

```



If Python cannot locate the project packages:



```cmd

set PYTHONPATH=%CD%

python -m streamlit run member2\\dashboard.py

```



\---



\## 🧪 Running Tests



Run the automated test suite:



```cmd

pytest -q

```



Current validated result:



```text

76 passed

```



\---



\## 📁 Project Structure



```text

GuardX/

│

├── app/

│   ├── constraints/

│   ├── evaluation/

│   ├── models/

│   └── ...

│

├── member2/

│   ├── dashboard.py

│   ├── datasets/

│   ├── runner/

│   ├── scoring/

│   └── ...

│

├── tests/

│

├── requirements.txt

├── pytest.ini

└── README.md

```



\---



\## 🔒 Security Scope



GuardX is designed for controlled LLM evaluation and security testing.



Use \*\*synthetic secrets and controlled test data\*\* during testing.



Do not place real:



\* passwords,

\* API keys,

\* credentials,

\* personal information, or

\* other sensitive data



into test cases.



\---



\## ⚙️ Limitations



GuardX results depend on:



\* Test-case coverage

\* Model configuration

\* Model version

\* Constraint definitions

\* Semantic evaluator behavior

\* Dataset coverage

\* Evaluation methodology



A finite test suite cannot establish that an LLM is universally safe.



\---



\## 🎯 Project Goal



GuardX aims to provide a repeatable evaluation layer for LLM security testing:



```text

&#x20;       LLM

&#x20;        │

&#x20;        ▼

&#x20;  Controlled Tests

&#x20;        │

&#x20;        ▼

&#x20;Constraint Evaluation

&#x20;        │

&#x20;        ▼

&#x20;   Risk Scoring

&#x20;        │

&#x20;    ┌───┴───┐

&#x20;    ▼       ▼

&#x20;Compare   Regression

&#x20;    │       │

&#x20;    └───┬───┘

&#x20;        ▼

&#x20;     Results

&#x20;        │

&#x20;        ▼

&#x20;    Dashboard

```



\*\*GuardX does not make an LLM secure. It provides a structured way to measure and compare observed constraint compliance under controlled testing conditions.\*\*



