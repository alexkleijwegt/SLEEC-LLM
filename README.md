# SLEEC-LLM
This repository contains a python-based extension for the SLEEC-TK toolkit, providing translation of FDR's formal verification outputs (e.g. rule conflicts and redundancies) into plain English using a Large Langauge Model.

## Features

- Translates FDR4 verification outputs into natural language.
- Provides context-aware analysis of the situation that cause rule errors to occur.
- Provides multiple resolution suggestions with a structured template.
- Supports both conflicting and redundant SLEEC rule errors.
- Clean graphical user interface built with Python Tkinter & ttkbootstrap.
- Automatic detection and population of relevant files.

## Requirements

- SLEEC-TK (available from https://github.com/ScienceofComputerProgramming/SCICO-D-23-00378) and it's dependencies (Java 11 & FDR4)
- Python 3.9+
- OpenAI API Key*
- Tkinter (usually included with Python by default
- ttkbootstrap

\*Depending on how long the OpenAI account has been active & the plan the account is on, access to certain models may be limited.

## Installation

To use the program:

Ensure all of the requirement above aer installed, including the SLEEC-TK software.
Download the 'SLEEC LLM Tool.py' file and the 'LLM Resources' folder.
Place these in the top level of your folder alongside your SLEEC Ruleset. (Example below)

```
├── .settings
├── **LLM Resources**
├── src-gen
├── .project
├── ALMI.sleec
└── **SLEEC LLM Tool.py**
```
Open 'SLEEC LLM Tool.py' in a python editor of your choice. Obtain your OpenAI API Key (https://openai.com/api/) and paste this into the key section on line **423**

*Windows Only:* Ensure that the folder on line 14 points to your local refines.exe within the FDR\bin folder. This is not required on Linux systems, and the program should automatically detect the operating system being used.

Run 'SLEEC LLM Tool.py' either via the command line or an IDE such as VS Code.

## Modifications & Future Work

**ADDING NEW MODELS** 

Open AI Frequently release new and updated models. To add these, go to line **537** and add the model names to the list, i.e. 'o4'. To find out the model names required, you can use the name under the 'Model' section of the table from OpenAI here: https://platform.openai.com/docs/pricing

**MODIFING THE PROMPT**

The current prompt has been added to this repository to be read and modified. The 'Final Prompt' section on line **228** handles the prompt, so if any changes or updates are made, just replace the prompt here.

**ADDING MODEL-RULE CAPABILTIES**

Currently the tool only supports Rule-Rule errors, however the framework for Model-Rule errors has also been added. This will require the creation of a completely new prompt and can be implemented on line **435**. Currently there is just some placeholder text here which is shown when tying to run any Model-Rule analysis.

**ADDING NEW AGENT SPECIFICATIONS**

New agent specifications should be added as PDF's to the 'LLM Resources' Folder. Currently only ALMI and ASPEN have Specs written, however specifications for more autonomous agents are available at https://www.cs.toronto.edu/~sleec/index.html
