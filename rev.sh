# /bin/bash

# git init

git config --global user.email "kumar@rivan.in"
git config --global user.name "naga-phani0"

# git remote add origin https://github.com/naga-phani0/temp-now.git #add file name temp-now

# git revert --no-edit HEAD

# git reset --hard
git reset --soft HEAD^

git add .

git commit -m 'Sucessfully reverted'

git push origin main
