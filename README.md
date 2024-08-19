# AgentCourt: Simulating Court with Adversarial Evolvable Lawyer Agents

## Table of Contents

1. [Installation](#installation)
2. [Download Data](#download-data)
3. [Training](#training)
4. [Test](#test)
5. [Evaluation](#evaluation)

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Download Data

The data will be uploaded to Hugging Face soon. Please check back for updates.

## Training

To train the model, follow these steps:

1. **Modify Configuration File**: Use a convenient large model interface to modify the `example_role_config.json` file. We used ERNIE-Speed-128K. If you do not have access to an API, you can use the local model specified in our configuration file and change `llm_type` to `offline`.

2. **Run the Simulation**: Execute the following command to simulate 1000 real cases:

    ```bash
    python main.py
    ```

## Test

To perform testing:

1. **Disable Reflection and Summary**: Turn off `reflect_and_summary()` in the code.

2. **Simulate Test Data**: Replace the plaintiff and defendant with the desired agents (evolved lawyers or base model) for comparison experiments.

3. **Obtain Test Results**: Run the simulation and collect the results.

## Evaluation

### 1. Human Evaluation

We invited a team of legal experts from China to evaluate the test cases.

### 2. Automatic Evaluation

You can refer to the following link for multiple tasks to evaluate the model:

[https://github.com/open-compass/LawBench/](https://github.com/open-compass/LawBench/)

The evaluation scripts are detailed in the provided link. Combine the evolved lawyers with appropriate prompts to maximize the utilization of the three databases and achieve good performance on the automatic evaluation tasks.