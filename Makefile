documentation:
	cd docs && make html
	cd docs/build/html && git add -A && git commit -m 'updates'
	cd docs/build/html && git push origin gh-pages
