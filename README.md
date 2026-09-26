\# GuardX



An automated LLM testing framework that evaluates constraint compliance, performs risk-based scoring, compares models, and detects regressions in AI responses.



\## Overview



GuardX is an LLM security auditing and evaluation framework designed to test how language models behave under controlled adversarial prompts and security constraints.



It provides a common evaluation pipeline for different LLM providers and local models, allowing their responses to be evaluated, scored, compared, and tracked across regression tests.



\## Key Features



\* \*\*Constraint compliance testing\*\* — evaluates whether model responses follow defined constraints.

\* \*\*Semantic evaluation\*\* — evaluates responses using contextual information, including the original adversarial prompt.

\* \*\*Risk-based scoring\*\* — converts detected constraint violations into observed risk measurements.

\* \*\*Model comparison\*\* — evaluates multiple models using the same test cases and constraints.

\* \*\*Regression testing\*\* — detects changes in model behavior across evaluation runs.

\* \*\*JBB dataset support\*\* — supports controlled harmful-behavior test cases.

\* \*\*Custom prompts and constraints\*\* — allows runtime security constraints to be tested.

\* \*\*Local LLM testing\*\* — supports locally running Ollama models.

\* \*\*Cloud LLM testing\*\* — supports Groq-based models.

\* \*\*Latency tracking\*\* — records model response latency.

\* \*\*Persistent results\*\* — stores evaluation results for later comparison and regression analysis.

\* \*\*Streamlit dashboard\*\* — provides an interactive interface for running and reviewing audits.



\## Architecture



```text

Test Cases / JBB Dataset

&#x20;         |

&#x20;         v

&#x20;    Model Runner

&#x20;         |

&#x20;         v

&#x20;     LLM Adapter

&#x20;      /       \\

&#x20;   Groq      Ollama

&#x20;      \\       /

&#x20;         v

&#x20;    Model Response

&#x20;         |

&#x20;         v

&#x20;Constraint Evaluation

&#x20;     /         \\

&#x20;Rule-based    Semantic

&#x20;     \\         /

&#x20;         v

&#x20;   Risk Scoring

&#x20;     /       \\

&#x20;    v         v

Comparison   Regression

&#x20;     \\       /

&#x20;      \\     /

&#x20;       v   v

&#x20;   Results Storage

&#x20;         |

&#x20;         v

&#x20;  Streamlit Dashboard

```



\## Supported Models



GuardX uses a common model interface so different LLM providers can be evaluated through the same pipeline.



Models used during development and validation include:



\### Groq



\* `openai/gpt-oss-20b`

\* `openai/gpt-oss-120b`



\### Ollama



\* `qwen2.5:0.5b`

\* `gemma3:1b`



Local Ollama testing does not require an external model API key.



\## Evaluation Workflow



For each test case, GuardX:



1\. Loads the test case and associated constraint.

2\. Sends the controlled prompt to the selected model.

3\. Captures the model response.

4\. Evaluates the response against the configured constraint.

5\. Performs semantic evaluation when required.

6\. Detects constraint violations.

7\. Calculates the observed risk.

8\. Records latency and evaluation information.

9\. Stores the result.

10\. Makes the result available for model comparison and regression testing.



\## Semantic Evaluation



GuardX's semantic evaluator uses the original adversarial prompt together with the constraint and model response.



This is important because evaluating only the constraint and response can lose the context of what the model was actually asked to do.



For JBB test cases, the original harmful-behavior prompt is retained as metadata and supplied to the semantic evaluator.



\## Risk Scoring



GuardX reports risk based on the violations detected during evaluation.



For example:



```text

Risk: 0%

Violations: 0

```



means that \*\*no violation was detected for that particular tested case under the configured evaluation pipeline\*\*.



A 0% observed risk result should not be interpreted as proof that a model is universally secure.



\## Model Comparison



GuardX can evaluate multiple models using the same test cases and constraints.



Comparison results can include:



\* Test result

\* Detected violations

\* Risk

\* Security/compliance measurement

\* Model response

\* Latency



This allows behavioral differences between models to be examined under consistent testing conditions.



\## Regression Testing



GuardX supports regression testing to identify changes in model behavior across evaluation runs.



Regression testing can help detect changes caused by:



\* model changes,

\* model-version changes,

\* prompt changes,

\* constraint changes, or

\* evaluation-pipeline changes.



\## JBB Dataset



GuardX integrates JBB harmful-behavior test cases into its evaluation pipeline.



The original adversarial prompt is retained so that semantic evaluation has access to both the request and the resulting model response.



\## Dashboard



GuardX provides a Streamlit dashboard with workflows including:



\* Single Prompt testing

\* Category Batch testing

\* Full Dataset testing

\* Custom prompts

\* Runtime constraints

\* Multi-model selection

\* Per-test results

\* Model comparison

\* Regression testing



\## Installation



Create a Python 3.12 virtual environment:



```cmd

py -3.12 -m venv .venv

```



Activate it:



```cmd

.venv\\Scripts\\activate

```



Install dependencies:



```cmd

python -m pip install -r requirements.txt

```



\### Ollama Setup



Install Ollama and pull the local models you want to test:



```cmd

ollama pull qwen2.5:0.5b

ollama pull gemma3:1b

```



Verify:



```cmd

ollama list

```



\## Running GuardX



From the repository root:



```cmd

python -m streamlit run member2\\dashboard.py

```



If Python cannot locate the project packages, run:



```cmd

set PYTHONPATH=%CD%

python -m streamlit run member2\\dashboard.py

```



\## Testing



Run the automated test suite:



```cmd

pytest -q

```



The project reached:



\*\*76 passed\*\*



during development validation.



\## Validation



GuardX was validated across both cloud-hosted and local models.



A controlled local-model smoke test evaluated the same JBB harmful-behavior case against:



| Model          | Result | Observed Risk | Violations |

| -------------- | ------ | ------------: | ---------: |

| `qwen2.5:0.5b` | PASS   |            0% |          0 |



