# LaTeX Makefile v1.0 -- https://scaron.info/blog/makefiles-for-latex.html

ALL=$(wildcard *.tex text/*.tex figures/svg/*.svg figures/tex/*.tex)
MAIN=main.tex
LATEX=rubber --pdf
SHELL=/bin/zsh

FIGURES_SVG=$(wildcard figures/svg/*.svg)
FIGURES_TEX=$(wildcard figures/tex/*.tex)

FIGURES_PDF=$(wildcard figures/pdf/*.pdf)
FIGURES_PNG=$(wildcard figures/png/*.png)

CLEAN_EXTRA=$(shell find . -type f -name '*.aux' -o -name '*.dvi' -o -name '*.log')

all: $(FIGURES_PDF) $(FIGURES_PNG)
	$(LATEX) $(MAIN)                # main run
	bibtex $(MAIN:.tex=)            # bibliography
	# makeglossaries $(MAIN:.tex=)    # list of abbreviations, nomenclature
	$(LATEX) $(MAIN)                # incremental run

clean:
	rubber --clean $(MAIN)
	rm -f $(CLEAN_EXTRA)

# figures/pdf/%.pdf: figures/svg/%.svg
# 	inkscape -C -z --file=$< --export-pdf=$@

figures/pdf/%.pdf: figures/tex/%.tex
	$(LATEX) --into $(dir $@) $<

figures_prepare: $(FIGURES_TEX)
	$(LATEX) --into=figures/pdf/ $?

watch:  ## Recompile on any update of LaTeX or SVG sources
	@while [ 1 ]; do;          \
        inotifywait $(ALL);    \
        sleep 0.01;            \
        make all;              \
        echo "\n----------\n"; \
        done

help:  # http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -P '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
.PHONY: help
