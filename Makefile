PSFILES := $(patsubst %.txt,%.ps,$(wildcard *.txt))
IMGFILES := $(patsubst %.txt,%.png,$(wildcard *.txt))

all: each summary.ps

each: $(PSFILES)

summary.ps: $(PSFILES)
	./scheduler.py summary

img: $(PSFILES) $(IMGFILES)

%.ps: %.txt
	./scheduler.py "$<" "$@"

%.png: %.ps
	./process.sh "$<" "$@"

clean:
	rm -f *.ps *.png *.pyc

distclean: clean
	rm -f *.txt scheduler.zip

dist: distclean
	@echo "Packaging as a ZIP"
	git archive --format=zip --prefix="scheduler/" HEAD > scheduler.zip

