PYTHON=python
PYGPLUGIN_DIR ?= .
PYGPLUGIN_TS=$(PYGPLUGIN_DIR)/.pyg-plugin.ts
PYGPLUGIN_NAME=cilkhilite
PYGPLUGIN_FILES=$(shell ls $(PYGPLUGIN_DIR)/$(PYGPLUGIN_NAME)/*.py)

.PHONY : all_pygplugin clean_pygplugin remake_pygplugin

all_pygplugin : $(PYGPLUGIN_TS)

clean_pygplugin :
	rm -rf $(PYGPLUGIN_TS) $(PYGPLUGIN_DIR)/*~ $(PYGPLUGIN_DIR)/$(PYGPLUGIN_NAME)/*~ \
	$(PYGPLUGIN_DIR)/build $(PYGPLUGIN_DIR)/dist $(PYGPLUGIN_DIR)/pycilk.egg-info

$(PYGPLUGIN_TS) : $(PYGPLUGIN_DIR)/setup.py $(PYGPLUGIN_FILES)
	@command -v pygmentize >/dev/null 2>&1 && \
	pygmentize -V | \
	perl -n -e'/^Pygments\sversion\s(\d+\.\d+)/ && $$1 >= 1.6 or die "Please install Pygments version >= 1.6";' && \
	cd $(PYGPLUGIN_DIR) && $(PYTHON) setup.py build && $(PYTHON) setup.py install --user && cd - && \
	touch $@

remake_pygplugin :
	@command -v pygmentize >/dev/null 2>&1 && \
	pygmentize -V | \
	perl -n -e'/^Pygments\sversion\s(\d+\.\d+)/ && $$1 >= 1.6 or die "Please install Pygments version >= 1.6";' && \
	cd $(PYGPLUGIN_DIR) && $(PYTHON) setup.py build && $(PYTHON) setup.py install --user && cd - && \
	touch $(PYGPLUGIN_TS)
