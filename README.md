<div style="display: flex; align-items: center;">
  <img src="io.png" alt="Icon" style="width: 1em; height: 1em; margin-right: 0.5em;" />
  <h1 style="margin: 0;">AgentCourt: Simulating Court with Adversarial Evolvable Lawyer Agents</h1>
</div>

![Demonstration GIF](AgentCourt.gif)

[Paper Link: AgentCourt: Simulating Court with Adversarial Evolvable Lawyer Agents](https://arxiv.org/abs/2408.08089)

You can watch the voice-over video demonstration on Bilibili, at the following address:

[https://www.bilibili.com/video/BV1aXpUe3E6A?t=2323.7](https://www.bilibili.com/video/BV1aXpUe3E6A?t=2323.7)
## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Research Highlights](#research-highlights)
4. [Installation](#installation)
5. [Download Data](#download-data)
6. [Training](#training)
7. [Test](#test)
8. [Evaluation](#evaluation)
9. [Code Availability](#code-availability)
10. [Contributing](#contributing)
11. [Citation](#citation)
12. [Contact](#contact)

## Overview

AgentCourt is an innovative simulation system designed to replicate the entire courtroom process using autonomous agents driven by large language models (LLMs). This project aims to enable lawyer agents to learn and improve their legal skills through extensive courtroom process simulations.

## Key Features

- **Full Courtroom Simulation**: Includes judge, plaintiff's lawyer, defense lawyer, and other participants as autonomous agents.
- **Adversarial Evolutionary Approach**: Lawyer agents learn and evolve through simulated legal cases.
- **LLM-Driven Agents**: Utilizes advanced language models to power agent interactions and decision-making.
- **Continuous Learning**: Agents accumulate experience from simulated court cases based on real-world knowledge.

## Research Highlights

- Simulated 1000 adversarial legal cases (equivalent to a decade of real-world experience).
- Evolved lawyer agents showed consistent improvement in handling legal tasks.
- Professional lawyers evaluated the simulations, confirming advancements in:
  - Cognitive agility
  - Professional knowledge
  - Logical rigor

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Download Data

The dataset used in this project is available on Hugging Face:
[AgentCourt Dataset](https://huggingface.co/datasets/youzi517/AgentCourt)

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

## Code Availability

**Note:** The code for this project is currently being organized and refined. We expect to upload it to this repository within the next week. Please check back soon for updates. We appreciate your patience and interest in our work.

## Contributing

We welcome contributions to the AgentCourt project. Please read our contributing guidelines before submitting pull requests.


## Citation

If you use AgentCourt in your research, please cite our paper:

```
@misc{chen2024agentcourtsimulatingcourtadversarial,
      title={AgentCourt: Simulating Court with Adversarial Evolvable Lawyer Agents}, 
      author={Guhong Chen and Liyang Fan and Zihan Gong and Nan Xie and Zixuan Li and Ziqiang Liu and Chengming Li and Qiang Qu and Shiwen Ni and Min Yang},
      year={2024},
      eprint={2408.08089},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2408.08089}, 
}
```

## Contact

For questions and feedback, please open an issue on this GitHub repository.

---

This project is part of ongoing research in LLM-driven agent technology for legal scenarios. We're excited to see how it can advance the field of AI in law.
