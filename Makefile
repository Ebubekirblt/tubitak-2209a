.PHONY: help check compile

help:
	@printf '%s\n' \
		'Kullanılabilir komutlar:' \
		'  make check    Repo yapısını ve Python sözdizimini kontrol eder' \
		'  make compile  Python dosyalarını derleme kontrolünden geçirir'

check:
	python3 scripts/check_repository.py

compile:
	python3 -m compileall -q aasist-source scripts
