### Installation
1. Windows Setup Steps
	1. Install Python (if not already): Download Python for Windows
	2. Open Command Prompt, navigate to the project folder
	3. Run: setup.bat
	4. Script will:
		1. Create virtual environment: venv\
		2. Activate the environment
		3. Install dependencies from requirements.txt
2. Mac/Linux Setup Steps
	1. Install Python (if not already)
	2. Open Terminal, navigate to the project folder
	3. Run: 
       1. chmod +x setup.sh
       2. ./setup.sh
	4. Script will:
		1. Create virtual environment: venv/
		2. Activate the environment
        3. Install dependencies from requirements.txt

### Test Execution
1. Run in single test class using Terminal. 
   2. Command:   pytest --envfile=.env.uat -s tests/safety/risk_forecast/smoke/test_weekly_risk_summary.py
3. Run all test classes inside any test folder like smoke or regression 
   4. Command:  pytest --envfile=.env.uat2one -s tests/safety/risk_forecast/smoke/
2. To run only smoke suite tagged tests like only smoke test cases in entire project
   3. Command: pytest --envfile=.env.uat -m smoke
4. Adding new line for sample commit