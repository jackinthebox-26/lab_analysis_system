How to install and start to work with this package
1. Create venv: python -m venv venv
2. Activate venv: 
    a. ctrl + shift + P
    b. Select Python:Select Interpretor
    c. Select venv in your workspace
3. Install requirements: pip install -r requirements.txt


To clean up everything 
1. git reset --hard HEAD
2. git clean -fdx
NOTE: git clean DELETES UNTRACKED FILES. DONT DO THIS BY ACCIDENT.

To go to an older version to re-create the plots
1. git checkout <hash>
2. Run main.py and custom_graphs.py
3. git checkout main