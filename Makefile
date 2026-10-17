PYTHON ?= $(if $(wildcard work/.venv/bin/python),work/.venv/bin/python,python3)
ANIM = plugins/alevel-physics-animations/scripts/anim.py

.PHONY: test verify ppt-all render-all template dist-local scrub

test:
	$(PYTHON) -m pytest tests -q

verify: test
	$(PYTHON) scripts/verify.py
	$(PYTHON) $(ANIM) ppt-all --out work/ppt-smoke

ppt-all:
	$(PYTHON) $(ANIM) ppt-all

render-all:
	$(PYTHON) $(ANIM) render-all

template:
	$(PYTHON) $(ANIM) template

dist-local:
	$(PYTHON) scripts/dist.py --local

scrub:
	$(PYTHON) $(ANIM) scrub outputs
