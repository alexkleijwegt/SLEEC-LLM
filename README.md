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

# Modifications & Future Work

## User Study

A user study was carried out with this version of the tool and the following area were highlighted as key points of improvement:
- The LLM struggles to generate code consistent with the syntax of the SLEEC language. Consider editing the SLEEC specification, adding a new Syntax secification, or adding detailed instruction surrounding the language to the prompt. This should make sure any generated suggestions are in-keepign with the SLEEC syntax.
- The tool appears to have a preference for suggesting the removal of rules. While ok in principle, this could lead to removal of functionality in real-world use cases. Consider refining the prompt towards modifying or adding rules, saving removal of rules as a last resort. This should prioritise preserving the systems functionality over just finding the simplest method to create a well-formed ruleset.
- Adding some highlighting to the proposed changes would make the outputs clearer to the user so they are aware of exactly what needs to change/ stay the same.

## Other areas of improvement 

**MOVE TO RESPONSES API**

ChatGPT has recently moved to the Responses API as it's main service for interacting with it's models. Currently the tool uses the ChatGPT Chat API as this was the only available API tool when the project was started. For future-proofing the tool I would recommend moving to the Responses API for future development. You can see the difference between the two API's here: https://platform.openai.com/docs/guides/responses-vs-chat-completions

This API also allows for conversations as opposed to just a single prompt and response from the ChatAPI. You could expand the existing tool with a text box users can type questions into (e.g. "Please clarify XYZ on analysis 1") and then the model would be able to provide further details.

**ADDING NEW MODELS** 

Open AI Frequently release new and updated models. To add these, go to line **537** and add the model names to the list, i.e. 'o4'. To find out the model names required, you can use the name under the 'Model' section of the table from OpenAI here: https://platform.openai.com/docs/pricing

**MODIFING THE PROMPT**

The current prompt has been added to this repository to be read and modified. The 'Final Prompt' section on line **228** handles the prompt, so if any changes or updates are made, just replace the prompt here.

**ADDING MODEL-RULE CAPABILTIES**

Currently the tool only supports Rule-Rule errors, however the framework for Model-Rule errors has also been added. This will require the creation of a completely new prompt and can be implemented on line **435**. Currently there is just some placeholder text here which is shown when tying to run any Model-Rule analysis.

**ADDING NEW AGENT SPECIFICATIONS**

New agent specifications should be added as PDF's to the 'LLM Resources' Folder. Currently only ALMI and ASPEN have Specs written, however specifications for more autonomous agents are available at https://www.cs.toronto.edu/~sleec/index.html
