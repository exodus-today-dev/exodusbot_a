cd /var/www/exodusbot/

git status
git stash
git checkout master
git pull origin master
git stash apply

sudo supervisorctl restart exodusbot

