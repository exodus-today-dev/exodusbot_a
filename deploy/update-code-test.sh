cd /var/www/exodusbot/

git status
git stash
git checkout staging
git pull origin staging
git stash apply

sudo supervisorctl restart exodusbot

