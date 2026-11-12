How to install and start to work with this package
1. Create venv: python -m venv venv
2. Activate venv: 
    a. ctrl + shift + P
    b. Select Python:Select Interpretor
    c. Select venv in your workspace
3. Install this package: pip install -e .


To clean up everything 
1. git reset --hard HEAD
2. git clean -fdx

NOTE: git clean DELETES UNTRACKED FILES. DONT DO THIS BY ACCIDENT.


To go to an older version to re-create the plots
1. git checkout `<hash>`
2. Run main.py and custom_graphs.py
3. git checkout main


To create an easilty sharable bundle use the following code in powershell
`
Get-ChildItem -Recurse -File -Include *.py, *.js, *.html, *.css, *.md, *.sql, *.toml | 
    Where-Object { $_.FullName -notmatch '[\\/](node_modules|\.git|venv)[\\/]' } | 
    ForEach-Object { "=== $($_.FullName) ==="; Get-Content $_.FullName -Raw; "`n" } | 
    Out-File -Encoding utf8 project_bundle.txt
    
    `


TODO
- Add logging
- Add unittests
- build exp_date_template
