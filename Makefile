update:
	git add .
	git commit -m "update"
	git push

push:
	git push
create:
	echo "# englium_mailer" >> README.md
	git init
	git add .
	git commit -m "first commit"
	git branch -M main
	git remote add origin https://github.com/Fugguri/englium_mailer.git
	git push -u origin main