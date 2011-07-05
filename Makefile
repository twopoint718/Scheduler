PSFILES := $(patsubst %.txt,%.ps,$(wildcard *.txt))
IMGFILES := $(patsubst %.txt,%.png,$(wildcard *.txt))
PYFILES := $(wildcard *.py)

all:
	./scheduler.py

clean:
	rm -rf *.ps *.png *.pyc htmlcov __pycache__ .coverage

distclean: clean
	rm -f *.txt scheduler.zip

dist: distclean
	@echo "Packaging as a ZIP"
	git archive --format=zip --prefix="scheduler/" HEAD > scheduler.zip

coverage: $(PYFILES)
	coverage run --omit pyparsing.py test_scheduler.py
	coverage html
	@echo "Open htmlcov/index.html to view test coverage"

test: $(PYFILES)
	./test_scheduler.py