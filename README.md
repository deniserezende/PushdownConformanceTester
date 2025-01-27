# Pushdown Conformance Tester
Developed a conformance testing tool for reactive systems with stack memory, leveraging formal methods and ioco-like relations to ensure software reliability and precision, especially in systems requiring stack-based operations. 

## Libraries Used
	•	pandas: This library facilitates the manipulation of structured data, particularly for processing state transitions during the product calculation between the fault model and implementation. It allows for efficient interaction with large datasets organized in DataFrames, making it easier to manage and verify states and transitions, which is crucial for compliance checking.
	•	deepcopy: This function creates deep copies of complex data structures, such as lists of states and transitions. It is essential to ensure that modifications to a copied structure do not affect the original state. In the `faultModel` module, `deepcopy` is frequently used to clone states and transitions from the original (fault-free) system to build the fault model while keeping the original model intact for later comparison.
	•	logging: This library records events during program execution, aiding in debugging and result analysis. It helps identify errors and track program flow, especially when dealing with multiple transitions and state interactions. In the `balancedRunChecker` module, logging assists in monitoring balanced run checks, making it easier to track progress and identify issues.
	•	streamlit: This library creates an interactive graphical interface that facilitates user interaction with the tool. The interface is designed to be simple and accessible, featuring titles, subtitles, instructions, file upload areas, action buttons, and feedback messages. Through this interface, users can provide input files, visualize verification progress, and receive compliance test results. Streamlit makes the verification process more accessible for users with less command-line experience.

 ## Environment Setup for Tool Execution
 To ensure correct execution of the tool in your local environment, follow these steps to set up either on macOS or Windows. Required libraries are installed using the pip package manager that comes with Python.
 
### Check Python and pip versions:
	•	On macOS, open Terminal and run:
	•	`python3 --version`
	•	`pip3 --version`
	•	On Windows, open Command Prompt and run:
	•	`python --version`
	•	`pip --version` If these commands return versions, Python is installed. Ensure it is version 3.9 or higher; otherwise, update it as needed.

### Install necessary libraries:
	•	On macOS, in Terminal, run:
	•	`pip3 install pandas`
	•	`pip3 install streamlit`
	•	On Windows, in Command Prompt, run:
	•	`pip install pandas`
	•	`pip install streamlit`
 
### After installing the necessary libraries, follow these steps to run the tool:
	•	Open Terminal (macOS) or Command Prompt (Windows).
	•	Navigate to the directory where `main.py` is located.
	•	Execute the following command to start the tool using Streamlit:
	•	`streamlit run main.py`

 For additional information, please refer to the PDF of my thesis.
