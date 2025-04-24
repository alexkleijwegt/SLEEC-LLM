import os
import glob
import threading
import time
import subprocess
import ttkbootstrap as tb
from ttkbootstrap import ttk
from tkinter import BooleanVar, StringVar
from tkinter.scrolledtext import ScrolledText
import PyPDF2
from openai import OpenAI

# Set the filepath for refines.exe on Windows. On Linux this is not required as Refines can be called from anywhere.
refines_exe_path = r"C:\Program Files\FDR\bin\refines.exe"

def load_files():
    # Pre-loads the files that are expected to be used.
    sleec_files = glob.glob(os.path.join(os.getcwd(), "*.sleec"))
    assertions_files = glob.glob(os.path.join(os.getcwd(), "src-gen", "*-assertions.csp"))
    system_files = glob.glob(os.path.join(os.getcwd(), "*.rct"))
    verification_file = os.path.join(os.getcwd(), "csp-gen", "timed", "verification_assertions.csp")
    verification_files = [verification_file] if os.path.exists(verification_file) else []
    return sleec_files, assertions_files, verification_files, system_files

def load_prompt_supplements():
    # Loads the prompt supplements from the LLM Resources folder
    base_dir = os.path.join(os.getcwd(), "LLM Resources")
    if not os.path.exists(base_dir):
        return [], []
    sleec_spec_file = os.path.join(base_dir, "SLEEC Spec.pdf")
    if os.path.exists(sleec_spec_file):
        sleec_spec_list = [sleec_spec_file]
    else:
        sleec_spec_list = []
    agent_spec_files = []
    for f in os.listdir(base_dir):
        full_path = os.path.join(base_dir, f)
        if os.path.isfile(full_path) and f != "SLEEC Spec.pdf":
            agent_spec_files.append(full_path)
    return sleec_spec_list, agent_spec_files

def read_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
    except Exception as e:
        return "Error reading PDF file: " + str(e)

def update_dropdowns():
    global sleec_files, assertions_files, verification_files, system_files
    sleec_files, assertions_files, verification_files, system_files = load_files()
    sleec_selector["values"] = [os.path.basename(f) for f in sleec_files]
    assertions_selector["values"] = [os.path.basename(f) for f in assertions_files]
    verification_selector["values"] = [os.path.basename(f) for f in verification_files]
    system_selector["values"] = [os.path.basename(f) for f in system_files]
    if sleec_files:
        sleec_selector.current(0)
        read_sleec_file()
    if assertions_files:
        assertions_selector.current(0)
        select_assertions_file()
    if verification_files:
        verification_selector.current(0)
        select_verification_file()
    if system_files:
        system_names = [os.path.basename(f) for f in system_files]
        if "system.rct" in system_names:
            system_selector.current(system_names.index("system.rct"))
        else:
            system_selector.current(0)
        read_system_file()
    update_prompt_supplements_section()

def update_prompt_supplements_section():
    global prompt_sleec_files, prompt_agent_files
    global prompt_sleec_selector, prompt_sleec_entry, prompt_agent_selector, prompt_agent_entry
    prompt_sleec_files, prompt_agent_files = load_prompt_supplements()
    prompt_sleec_selector["values"] = [os.path.basename(f) for f in prompt_sleec_files]
    if prompt_sleec_files:
        prompt_sleec_selector.current(0)
        select_prompt_sleec_file()
    else:
        prompt_sleec_entry.config(state="normal")
        prompt_sleec_entry.delete(0, "end")
        prompt_sleec_entry.insert(0, "")
        prompt_sleec_entry.config(state="readonly")
    prompt_agent_selector["values"] = [os.path.basename(f) for f in prompt_agent_files]
    if prompt_agent_files:
        prompt_agent_selector.current(0)
        select_prompt_agent_file()
    else:
        prompt_agent_entry.config(state="normal")
        prompt_agent_entry.delete(0, "end")
        prompt_agent_entry.insert(0, "")
        prompt_agent_entry.config(state="readonly")

def read_sleec_file():
    selected_index = sleec_selector.current()
    if selected_index != -1:
        selected_file = sleec_files[selected_index]
        try:
            with open(selected_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = "Error reading file: " + str(e)
        sleec_textbox.delete("1.0", "end")
        sleec_textbox.insert("end", content)

def read_system_file():
    selected_index = system_selector.current()
    if selected_index != -1:
        selected_file = system_files[selected_index]
        try:
            with open(selected_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = "Error reading file: " + str(e)
        system_textbox.delete("1.0", "end")
        system_textbox.insert("end", content)

def select_assertions_file():
    selected_index = assertions_selector.current()
    if selected_index != -1:
        selected_file = assertions_files[selected_index]
        rel_path = "/" + os.path.relpath(selected_file, os.getcwd())
        assertions_textbox.config(state="normal")
        assertions_textbox.delete(0, "end")
        assertions_textbox.insert(0, rel_path)
        assertions_textbox.config(state="readonly")

def select_verification_file():
    selected_index = verification_selector.current()
    if selected_index != -1:
        selected_file = verification_files[selected_index]
        rel_path = "/" + os.path.relpath(selected_file, os.getcwd())
        verification_textbox.config(state="normal")
        verification_textbox.delete(0, "end")
        verification_textbox.insert(0, rel_path)
        verification_textbox.config(state="readonly")

def select_prompt_sleec_file():
    global prompt_sleec_selector, prompt_sleec_entry
    selected_index = prompt_sleec_selector.current()
    if selected_index != -1:
        file_path = prompt_sleec_files[selected_index]
        rel_path = os.path.join("LLM Resources", os.path.basename(file_path))
        prompt_sleec_entry.config(state="normal")
        prompt_sleec_entry.delete(0, "end")
        prompt_sleec_entry.insert(0, rel_path)
        prompt_sleec_entry.config(state="readonly")

def select_prompt_agent_file():
    global prompt_agent_selector, prompt_agent_entry
    selected_index = prompt_agent_selector.current()
    if selected_index != -1:
        file_path = prompt_agent_files[selected_index]
        rel_path = os.path.join("LLM Resources", os.path.basename(file_path))
        prompt_agent_entry.config(state="normal")
        prompt_agent_entry.delete(0, "end")
        prompt_agent_entry.insert(0, rel_path)
        prompt_agent_entry.config(state="readonly")

def update_analysis_text():
    if rule_rule_var.get() and model_rule_var.get():
        analysis_text.set("Analysing both Rule-Rule Conflicts and Model-Rule Conflicts")
    elif rule_rule_var.get():
        analysis_text.set("Analysing Rule-Rule Conflicts")
    elif model_rule_var.get():
        analysis_text.set("Analysing Model-Rule Conflicts")
    else:
        analysis_text.set("Select an analysis option")

def build_prompt():
    spinner.start()
    status_var.set("Building Prompt...")

    # Currently only set to process rule-rule errors, model-rule errors will have to be implemented later.
    if rule_rule_var.get() and not model_rule_var.get():
        # Get SLEEC Spec text from PDF
        sleec_spec_text = ""
        if prompt_sleec_files:
            sleec_spec_text = read_pdf(prompt_sleec_files[0])
        
        # Get SLEEC ruleset from selected SLEEC file
        sleec_ruleset = ""
        s_index = sleec_selector.current()
        if s_index != -1:
            try:
                with open(sleec_files[s_index], "r", encoding="utf-8") as f:
                    sleec_ruleset = f.read()
            except Exception as e:
                sleec_ruleset = "Error reading SLEEC file: " + str(e)
        
        # Get Assertions file output using the refines command. Automatic Windows/Linux detecttion ensures the correct command is used.
        assertions_output = ""
        a_index = assertions_selector.current()
        if a_index != -1:
            assertions_full_path = assertions_files[a_index]
            try:
                if os.name == "nt":
                    env = os.environ.copy()
                    env["LC_ALL"] = "C"
                    refines_dir = os.path.dirname(refines_exe_path)
                    current_dir = os.getcwd()
                    os.chdir(refines_dir)
                    command = [os.path.basename(refines_exe_path), "--quiet", assertions_full_path]
                    result = subprocess.run(command, capture_output=True, text=True, env=env)
                    assertions_output = result.stdout.strip() if result.returncode == 0 else "Error: " + result.stderr.strip()
                    os.chdir(current_dir)
                else:
                    command = ["refines", "--quiet", assertions_full_path]
                    assertions_output = subprocess.check_output(command, universal_newlines=True).strip()
            except Exception as e:
                assertions_output = "Error running refines: " + str(e)
        
        # Get Agent Specification text from PDF
        agent_text = ""
        if prompt_agent_files:
            agent_text = read_pdf(prompt_agent_files[0])
        
        # Build the final prompt using the provided template.
        final_prompt = (
    f"Sleec-TK is a toolkit for the specification, validation and verification of social, legal, ethical, empathetic and cultural requirements for autonomous agents and AI systems. "
    f"You can see a full breakdown of the SLEEC application in the attached Sleec document: {sleec_spec_text}.\n\n"
    f"The SLEEC tool runs a verification in the FDR4 software. In this, the sleec rules are verified against each other to check for inconsistencies and redundancies.\n\n"
    f"Any issues discovered in the verification are outputted. These are denoted as 'failed' assertions and, if applicable, counterexample trace(s) are generated for each failed assertion.\n\n"
    f"The users responsible for understanding and working with these outputs are often non-technical and therefore struggle to understand the mathematical outputs generated by the SLEEC tool. "
    f"Your role is to translate any failed assertions into plain English to assist these users in fixing issues in their set of requirements. You will also be providing a resolution suggestion to assist the user in fixing the issue.\n\n"
    f"Your responses will utilise pre-defined templates depending on the issue found. Let's look at the Rule-Rule inconsistencies (conflicts and redundancies), how they will be presented and the desired output formats for them.\n\n"
    f"Rule-Rule Inconsistencies:\n\n"
    f"Each rule is checked against each other rule for both conflicts and redundancies. The SLEEC tool will output all checks that it completes, but only rules denoted with 'Result: Failed' will need to be analysed. "
    f"Rule conflicts will produce one or more counterexample traces which will need to be analysed by you. Rule redundancies will not produce a trace but the output will notify you of the existence of a redundancy between two rules.\n\n"
    f"Conflicting rules will be outputted by the SLEEC tool in the following format:\n\n"
    f"\"SLEEC[Name of rule 1][Name of rule 2]\n"
    f"\tLog:\n"
    f"\t\tResult: Failed\n"
    f"\t\t...\n"
    f"\t\t...\n"
    f"\t\tCounterexample: {{Mathematical counterexample string here}}\"\n\n"
    f"Each failed assertion may have multiple counterexample traces. When generating your response consider all counterexample traces to ensure your analysis catches all possible errors and also your proposed resolution fixes all listed counterexamples. "
    f"For each of the rule combinations that fail, you must complete the following template:\n\n"
    f"Conflicting Rule ({{Rule conflict out of total number of conflicting rules, i.e. \"1 of 3\", and the next analysis generated would be \"2 of 3\" etc.}}): {{\n"
    f"\tError: {{\n"
    f"\t\tRule Name: {{Name of rule combination e.g. SLEECRule1Rule2}}\n"
    f"\t\tRule 1: {{name of Rule 1}}\n"
    f"\t\tRule 2: {{name of Rule 2}}\n"
    f"\t\tScenario: {{a brief description of the scenario when these rules would come into effect}}\n"
    f"\t\tCategory: {{based on information such as the wider scenario, the specific SLEEC rules and the generated counter examples, categorise the error. Examples of categories may include divergence, timing and event/ measure names.}}\n"
    f"\t\tJustification: {{your justification for why the error exists}}\n"
    f"\t}},\n"
    f"\tResolution: {{\n"
    f"\t\tSuggestion 1: {{using one, or a combination of the following options: 'add rule', 'remove rule', 'modify rule' and 'combine rules', suggest a change to the SLEEC code that would resolve the error. These rules must be displayed in the format: \n"
    f"\t\t\tAdd Rule: \"ADD RULE: RuleN when X then Y\"\n"
    f"\t\t\tRemove Rule: \"REMOVE RULE: RuleN\"\n"
    f"\t\t\tModify Rule: \"MODIFY RULE: RuleN -> RuleM when X then Y\"\n"
    f"\t\t\tCombine Rules: \"COMBINE RULES: RuleA AND RuleB -> RuleC when X then Y\"\n"
    f"\n"
    f"\t\t\tIf multiple options are chosen, the format should follow:\n"
    f"\t\t\t\"Option1 AND Option2 ... AND OptionN\" where Option1 - OptionN are in the formats described above.\n"
    f"\n"
    f"\t\t\tAny additions, removals, modifications, or combinations of rules must stay within the scope of the agent and not require actions or measures outside of the capability of the system. "
    f"Where possible the changes should make use of existing rules and measures first, only creating new events and measures when absolutely necessary. "
    f"New rules generated must also follow the SLEEC syntax. You are allowed to use any SLEEC features such as 'within' for timed actions, 'unless' for extra checks etc.}}\n"
    f"\n"
    f"\t\tJustification: {{your justification for why suggestion 1 would resolve the error}}\n\n"
    f"\t\tSuggestion 2: {{using the same format as above, if applicable, suggest another resolution that could solve the problem. Make this suggestion distinct from the first suggestion.}}\n"
    f"\t\tJustification: {{your justification for why suggestion 2 would resolve the error}}\n"
    f"\t}}\n"
    f"}}\n\n"
    f"Redundant rules will be outputted by the SLEEC tool in the following format:\n\n"
    f"\"not [Name of rule 1]_wrt_[Name of rule 2]\n"
    f"\tLog:\n"
    f"\t\tResult: Failed\n"
    f"\t\t...\n"
    f"\t\t...\"\n\n"
    f"In this context 'wrt' means 'with reference to'. Unlike the rule conflicts, no counterexample traces are generated for redundant rules. For each of the redundancies found you must complete the following template:\n\n"
    f"Redundant Rules ({{Rule redundancy out of total number of redundant rules, i.e. \"1 of 3\", and the next analysis generated would be \"2 of 3\" etc.}}): {{\n"
    f"\tError: {{\n"
    f"\t\tRule Name: {{Name of rule combination e.g. Rule1_wrt_Rule2}}\n"
    f"\t\tRule 1: {{name of Rule 1}}\n"
    f"\t\tRule 2: {{name of Rule 2}}\n"
    f"\t\tScenario: {{a brief description of the scenario when these rules would come into effect}}\n"
    f"\t\tJustification: {{your justification for why the rules are redundant}}\n"
    f"\t}},\n"
    f"\tResolution: {{\n"
    f"\t\tSuggestion 1: {{using one, or a combination of the following options: 'add rule', 'remove rule', 'modify rule' and 'combine rules', suggest a change to the SLEEC code that would resolve the error. These rules must be displayed in the format: \n"
    f"\t\t\tAdd Rule: \"ADD RULE: RuleN when X then Y\"\n"
    f"\t\t\tRemove Rule: \"REMOVE RULE: RuleN\"\n"
    f"\t\t\tModify Rule: \"MODIFY RULE: RuleN -> RuleM when X then Y\"\n"
    f"\t\t\tCombine Rules: \"COMBINE RULES: RuleA AND RuleB -> RuleC when X then Y\"\n"
    f"\n"
    f"\t\t\tIf multiple options are chosen, the format should follow:\n"
    f"\t\t\t\"Option1 AND Option2 ... AND OptionN\" where Option1 - OptionN are in the formats described above.\n"
    f"\n"
    f"\t\t\tAny additions, removals, modifications, or combinations of rules must stay within the scope of the agent and not require actions or measures outside of the capability of the system. "
    f"Where possible the changes should make use of existing rules and measures first, only creating new events and measures when absolutely necessary. "
    f"New rules generated must also follow the SLEEC syntax. You are allowed to use any SLEEC features such as 'within' for timed actions, 'unless' for extra checks etc.}}\n"
    f"\n"
    f"\t\tJustification: {{your justification for why suggestion 1 would resolve the error}}\n\n"
    f"\t\tSuggestion 2: {{using the same format as above, if applicable, suggest another resolution that could solve the problem. Make this suggestion distinct from the first suggestion.}}\n"
    f"\t\tJustification: {{your justification for why suggestion 2 would resolve the error}}\n"
    f"\t}}\n"
    f"}}\n\n"
    f"I will now provide two example outputs, one for a set of conflicting rules, and one for a set of redundant rules. "
    f"When providing your answers, please answer in a similar style and to a similar level of detail to the examples provided. "
    f"Both the conflict and redundancy are based on the same set of SLEEC rules provided here:\n\n"
    f"Example SLEEC Rules:\n\n"
    f"def_start\n"
    f"  event StartLunchTime\n"
    f"  event InformUser\n"
    f"  event DetectUserFallen\n"
    f"  event CallSupport\n"
    f"  event IdentifySafePath\n"
    f"  event SoundWarning\n"
    f"  event Wait\n"
    f"  measure noSafePath:boolean\n"
    f"  measure waiting:boolean\n"
    f"  measure praying:boolean\n"
    f"  measure timeSinceLastMeal:numeric\n"
    f"  measure personAssent:boolean\n"
    f"  measure emergencyLevel: scale(E1,E2,E3,E4,E5)\n"
    f"  measure personStressLevel: scale(low,moderate,high)\n"
    f"  constant MAX_TIME=8\n"
    f"def_end\n\n"
    f"rule_start\n"
    f"  Rule1 when StartLunchTime then InformUser within 5 minutes \n"
    f"        unless praying\n"
    f"        unless timeSinceLastMeal>=MAX_TIME\n\n"
    f"  Rule2 when DetectUserFallen then CallSupport within 2 minutes\n"
    f"        unless not personAssent\n"
    f"        unless emergencyLevel>=E4 then CallSupport\n\n"
    f"  Rule3 when IdentifySafePath and noSafePath and not waiting then SoundWarning\n"
    f"        unless personStressLevel>=moderate then Wait\n\n"
    f"  Rule4 when DetectUserFallen and emergencyLevel<E2 then not CallSupport within 3 minutes\n\n"
    f"  Rule5 when DetectUserFallen and emergencyLevel<E2 then not CallSupport within 2 minutes\n\n"
    f"  Rule6 when SoundWarning then CallSupport within 2 minutes\n"
    f"\tunless emergencyLevel>=E3 then CallSupport\n"
    f"rule_end\n\n"
    f"Let's analyse a set of conflicting rules first.\n\n"
    f"Failed assertion:\n\n"
    f"SLEECRule2Rule4 :[deadlock free]:\n"
    f"    Log:\n"
    f"        Result: Failed\n"
    f"        Visited States: 820\n"
    f"        Visited Transitions: 1,542\n"
    f"        Visited Plys: 127\n"
    f"        Estimated Total Storage: 201MB\n"
    f"        Counterexample (Deadlock Counterexample)\n"
    f"            Machine Debug:\n"
    f"                SLEECRule2Rule4 (Failure Behaviour):\n"
    f"                    Trace: <DetectUserFallen, τ, personAssent.true,\n"
    f"                    emergencyLevel.E1, emergencyLevel.E1, τ, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, tock, tock, tock,\n"
    f"                    tock, tock, tock, tock, tock, tock, tock, τ>\n"
    f"                    Min Acceptance: {{}}\n\n"
    f"Example interpretation of this:\n\n"
    f"Conflicting Rules (1 of 1): {{\n"
    f"\tError: {{\n"
    f"\t\tRule Name: SLEECRule2Rule4\n"
    f"\t\tRule 1: Rule2\n"
    f"\t\tRule 2: Rule4\n"
    f"\t\tScenario: These rules come into effect when a user has fallen. The rules dictate when and if to call support based upon wether the user assents to support being called, and the users emergency level.\n"
    f"\t\tCategory: Deadlock due to timing\n"
    f"\t\tJustification: In this scenario a user has fallen and assents to support being called. The user is of emergency level 1. In this case, Rule2 is asking for support to be called within 2 minutes (As the user has assented, and not of emergency level greater than or equal to E4). "
    f"For a user of emergency level 1 (or more specifically, less than 2 as the rule states), Rule4 is asking for support to not be called for 3 minutes. Therefore these rules conflict as Rule2 is asking for support to be called within 2 minutes, and Rule4 is asking for support to not be called within 3 minutes, thus creating a deadlock due to timing.\n"
    f"\t}},\n"
    f"\tResolution: {{\n"
    f"\t\tSuggestion: REMOVE Rule: Rule4\n\n"
    f"\t\tJustification: Rule4 inhibts any user of emergencyLevel1 from getting support when they have fallen which could be unsafe as they may require assistance. If this is intentional, consider adding an 'unless emergencyLevel=E1 then not CallSupport' clause to Rule2 so that no timing deadlock is created.\n"
    f"\t}}\n"
    f"}}\n\n"
    f"Now let's look at a deadlock example from the same ruleset:\n\n"
    f"Failed assertion:\n\n"
    f"not Rule5_wrt_Rule4 [T= Rule4_wrt_Rule5:\n"
    f"    Log:\n"
    f"        Result: Failed\n"
    f"        Visited States: 1,104\n"
    f"        Visited Transitions: 1,859\n"
    f"        Visited Plys: 365\n"
    f"        Estimated Total Storage: 201MB\n\n"
    f"Example interpretation of this:\n\n"
    f"Redundant Rules (1 of 1): {{\n"
    f"\tError: {{\n"
    f"\t\tRule Name: Rule5_wrt_Rule4\n"
    f"\t\tRule 1: Rule4\n"
    f"\t\tRule 2: Rule5\n"
    f"\t\tScenario: Both of these rules come into effect when a user has fallen but is of emergencyLevel<E1.\n"
    f"\t\tJustification: These rules are redundant, as they are both requesting the same action (not CallSupport) but with different timeframes. In Rule4 support cannot be called within 3 minutes, whereas in rule 5 support cannot be called within 2 minutes. "
    f"If support is not called within 3 minutes, logically it cannot have been called within 2 either, therefore Rule5 is redundant here.\n"
    f"\t}},\n"
    f"\tResolution: {{\n"
    f"\t\tSuggestion: REMOVE RULE: Rule5\n\n"
    f"\t\tJustification: Rule5 is redundant here as not call support within 3 minutes (As suggested in Rule4), you also cannot call support within 2 minutes. As they both apply to the exact same scenario, rule5 is redundant here and can simply be removed.\n"
    f"\t}}\n"
    f"}}\n\n"
    f"You must now analyse the following SLEEC ruleset and the resulting output from the verification tool to generate your responses for EACH and EVERY failed assertion. Please start your response with the following header:\n"
    f"Total Rule Issues Discovered: {{a single integer of the total number of conflicting rules and redudant rules found in the ruleset}} | Conflicts: {{a single integer of the amount of conflicting rules found in the ruleset}} | Redundancies: {{a single integer of redundant rules found in the ruleset}}\n"
    f"The number of total issues should be equal to the sum of conflicts and redundancies, and also match the number of rule-rule conflicts outputted underneath.\n\n"
    f"Remember to use the specified templates and that any assertion with 'Result: Passed' can be ignored. Please make sure to correctly title conflicting and redundant rules in your responses. Your response should contain no extra words outside of the template, however please use dashes (e.g. \"-----------\") to create spacers between each rule-rule conflict template.\n\n"
    f"SLEEC Ruleset:\n\n{sleec_ruleset}\n\n"
    f"Verification output:\n\n{assertions_output}\n\n"
    f"To assist in this, I have also provided a PDF with some more infomation as to the details and abilities of the agent behind this ruleset: {agent_text}"
)


        
        status_var.set("Forwarding Prompt to LLM ...")
        try:
            client = OpenAI(api_key="REPLACE THIS TEXT WITH YOUR OPENAI API KEY")
            completion = client.chat.completions.create(
                model=gpt_model_selector.get(),
                messages=[{"role": "user", "content": final_prompt}]
            )
            llm_response = completion.choices[0].message.content.strip()
        except Exception as e:
            llm_response = f"Error calling OpenAI: {e}"
    
        llm_response_textbox.delete("1.0", "end")
        llm_response_textbox.insert("end", llm_response)
    
    else:
        placeholder = (
            "Placeholder: Analysis for Model-Rule conflicts and/or combined conflicts will be implemented later."
        )
        llm_response_textbox.delete("1.0", "end")
        llm_response_textbox.insert("end", placeholder)
    
    spinner.stop()
    status_var.set("Analysis Complete.")
    analysis_text.set("Analysis Generated")

def start_analysis_thread():
    threading.Thread(target=build_prompt, daemon=True).start()

# User Interface. Quickly modify the style with ttkbootstrap themes. Currently using 'united'.
root = tb.Window(themename="united")
root.title("SLEEC Ruleset Analysis Tool")
root.geometry("1400x800")

# File selection section
file_selection_frame = ttk.Frame(root, padding=10, borderwidth=2, relief="ridge")
file_selection_frame.pack(side="left", anchor="nw", fill="y", padx=10, pady=10)
ttk.Label(file_selection_frame, text="File Selector", bootstyle="primary").pack(pady=5)

# SLEEC file section
sleec_frame = ttk.Frame(file_selection_frame)
sleec_frame.pack(fill="x", pady=5)
ttk.Label(sleec_frame, text="SLEEC Ruleset:", bootstyle="info").pack()
sleec_selector = ttk.Combobox(sleec_frame, width=30, state="readonly")
sleec_selector.pack(pady=5)
sleec_selector.bind("<<ComboboxSelected>>", lambda e: read_sleec_file())
sleec_textbox = ScrolledText(sleec_frame, wrap="word", height=10, width=50)
sleec_textbox.pack(pady=5)

# Assertions file section
assertions_frame = ttk.Frame(file_selection_frame)
assertions_frame.pack(fill="x", pady=5)
ttk.Label(assertions_frame, text="Generated Assertions:", bootstyle="info").pack()
assertions_selector = ttk.Combobox(assertions_frame, width=30, state="readonly")
assertions_selector.pack(pady=5)
assertions_selector.bind("<<ComboboxSelected>>", lambda e: select_assertions_file())
assertions_textbox = ttk.Entry(assertions_frame, width=50, state="readonly")
assertions_textbox.pack(pady=5)

# Verification file section
verification_frame = ttk.Frame(file_selection_frame)
verification_frame.pack(fill="x", pady=5)
ttk.Label(verification_frame, text="Verification Assertions:", bootstyle="info").pack()
verification_selector = ttk.Combobox(verification_frame, width=30, state="readonly")
verification_selector.pack(pady=5)
verification_selector.bind("<<ComboboxSelected>>", lambda e: select_verification_file())
verification_textbox = ttk.Entry(verification_frame, width=50, state="readonly")
verification_textbox.pack(pady=5)

# System file section
system_frame = ttk.Frame(file_selection_frame)
system_frame.pack(fill="x", pady=5)
ttk.Label(system_frame, text="System Model:", bootstyle="info").pack()
system_selector = ttk.Combobox(system_frame, width=30, state="readonly")
system_selector.pack(pady=5)
system_selector.bind("<<ComboboxSelected>>", lambda e: read_system_file())
system_textbox = ScrolledText(system_frame, wrap="word", height=10, width=50)
system_textbox.pack(pady=5)

# Right side main content section
right_side_frame = ttk.Frame(root)
right_side_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Top right container section
top_right_container = ttk.Frame(right_side_frame)
top_right_container.pack(fill="x", pady=5)

# Prompt supplements section
prompt_supplements_frame = ttk.Frame(top_right_container, padding=10, borderwidth=2, relief="ridge")
prompt_supplements_frame.pack(side="left", fill="both", expand=True, padx=5)
ttk.Label(prompt_supplements_frame, text="Prompt supplements", bootstyle="primary").pack(pady=5)

# SLEEC specification
ttk.Label(prompt_supplements_frame, text="SLEEC Specification", bootstyle="info").pack()
prompt_sleec_selector = ttk.Combobox(prompt_supplements_frame, width=30, state="readonly")
prompt_sleec_selector.pack(pady=5)
prompt_sleec_selector.bind("<<ComboboxSelected>>", lambda e: select_prompt_sleec_file())
prompt_sleec_entry = ttk.Entry(prompt_supplements_frame, width=50, state="readonly")
prompt_sleec_entry.pack(pady=5)

# Agent specification
ttk.Label(prompt_supplements_frame, text="Agent Specification", bootstyle="info").pack(pady=5)
prompt_agent_selector = ttk.Combobox(prompt_supplements_frame, width=30, state="readonly")
prompt_agent_selector.pack(pady=5)
prompt_agent_selector.bind("<<ComboboxSelected>>", lambda e: select_prompt_agent_file())
prompt_agent_entry = ttk.Entry(prompt_supplements_frame, width=50, state="readonly")
prompt_agent_entry.pack(pady=5)

# Model selector section
model_selector_frame = ttk.Frame(top_right_container, padding=10, borderwidth=2, relief="ridge")
model_selector_frame.pack(side="right", fill="both", expand=True, padx=5)
ttk.Label(model_selector_frame, text="Model Selector", bootstyle="primary").pack(pady=5)

# GPT model dropdown
ttk.Label(model_selector_frame, text="GPT Model:", bootstyle="info").pack()
ttk.Label(model_selector_frame, text="Recommended: o3-mini", bootstyle="info", font=("TkDefaultFont", 8,"bold", "italic")).pack()
gpt_model_selector = ttk.Combobox(model_selector_frame, width=30, state="readonly")
gpt_model_selector["values"] = ["o3-mini", "o1", "o1-mini", "gpt-4o", "gpt-4.5-preview"]
gpt_model_selector.current(0)
gpt_model_selector.pack(pady=5)

# Frame for side by side rule-rule and mode-rule checkboxes
checkbox_frame = ttk.Frame(model_selector_frame)
checkbox_frame.pack(pady=5)
rule_rule_var = BooleanVar()
model_rule_var = BooleanVar()
rule_rule_checkbox = ttk.Checkbutton(checkbox_frame, text="Analyse Rule-Rule Conflicts", variable=rule_rule_var, command=update_analysis_text)
rule_rule_checkbox.pack(side="left", padx=10)
model_rule_checkbox = ttk.Checkbutton(checkbox_frame, text="Analyse Model-Rule Conflicts", variable=model_rule_var, command=update_analysis_text)
model_rule_checkbox.pack(side="left", padx=10)

# Analysis status
analysis_text = StringVar(value="Select an analysis option")
analysis_textbox = ttk.Entry(model_selector_frame, width=60, state="readonly", textvariable=analysis_text)
analysis_textbox.pack(pady=10)

# Start Analysis button
analysis_button = ttk.Button(model_selector_frame, text="Pass to LLM for Analysis", command=start_analysis_thread)
analysis_button.pack(pady=5)

# Progress bar and status label under analysis button
spinner = ttk.Progressbar(model_selector_frame, mode="indeterminate", length=200)
spinner.pack(pady=5)
status_var = StringVar(value="Idle")
status_label = ttk.Label(model_selector_frame, textvariable=status_var, bootstyle="info")
status_label.pack(pady=5)

# LLM response section
llm_response_frame = ttk.Frame(right_side_frame, padding=10, borderwidth=2, relief="ridge")
llm_response_frame.pack(fill="both", expand=True, padx=5, pady=5)
ttk.Label(llm_response_frame, text="SLEEC Validation Report", bootstyle="info").pack(pady=5)
llm_response_textbox = ScrolledText(llm_response_frame, wrap="word", height=20, width=70)
llm_response_textbox.pack(pady=5, fill="both", expand=True)

update_dropdowns()
root.mainloop()

