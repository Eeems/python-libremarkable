VERSION := $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
PATH := "/opt/bin:/opt/sbin:/home/root/.local/bin:/opt/bin:/opt/sbin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"

EVDEV_VERSION := $(shell grep evdev requirements.txt)
OBJ := $(shell find libremarkable -type f) pyproject.toml requirements.txt

define INSTALL_SCRIPT
export PATH=${PATH}
if ! type opkg &> /dev/null; then
    echo "Opkg not found, please install toltec"
    exit 1
fi
if ! type pip &> /dev/null; then
    opkg update
    opkg install python3-pip
fi
if ! python -c 'import PIL' &> /dev/null; then
    opkg update
    opkg install python3-pillow
fi
buildtools(){
    pip install wheel
    opkg update
    opkg install \
        automake \
        binutils \
        busybox \
        cmake \
        gawk \
        gcc \
        icu \
        ldd \
        libintl-full \
        libopenssl \
        libtool-bin \
        make \
        patchelf \
        python3-dev \
        python3-setuptools \
        sed \
        tar
    if ! [ -f /opt/include/linux/input.h ]; then
        /opt/bin/busybox wget -qO- "$$(/opt/bin/busybox sed -Ene \
          's|^src/gz[[:space:]]entware[[:space:]]https?([[:graph:]]+)|http\1/include/include.tar.gz|p' \
          /opt/etc/opkg.conf)" | /opt/bin/busybox tar x -vzC /opt/include
    fi
}
if ! python -c 'import evdev' &> /dev/null; then
    buildtools
    cd /tmp
    pip download --no-binary ':all:' "${EVDEV_VERSION}"
    tar -xf evdev-*.tar.gz
    cd evdev-*/
    python -u <<EOF
import os
with open('evdev/genecodes.py', 'r') as f:
    lines = f.readlines()

if "#include <linux/input-event-codes.h>\\n" not in lines:
    lines.insert(lines.index("#include <Python.h>\\n"), "#include <linux/input-event-codes.h>\\n")

with open('evdev/genecodes.py', 'w') as f:
    f.writelines(lines)
EOF
    C_INCLUDE_PATH=/opt/include \
    python setup.py \
        build_ecodes \
        --evdev-headers /opt/include/linux/input.h:/opt/include/linux/input-event-codes.h \
        bdist_wheel
    pip install dist/evdev-*.whl
    cd /tmp
    rm -rf evdev-*
fi
pip uninstall -qy libremarkable
pip install \
  --extra-index-url https://wheels.eeems.codes \
  /tmp/libremarkable-${VERSION}-py3-none-any.whl
endef
export INSTALL_SCRIPT
define EXECUTABLE_SCRIPT
echo "[info] Installing dependencies"
export DEBIAN_FRONTEND="noninteractive"
apt-get -y update
apt-get install -y \
  ccache \
  libtiff5 \
  libjpeg62-turbo \
  libopenjp2-7 \
  zlib1g \
  libfreetype6 \
  tcl8.6 \
  tk8.6 \
  python3-tk \
  libxcb1
cd /src
source /opt/lib/nuitka/bin/activate
python -m pip install wheel
python -m pip install \
	--extra-index-url=https://wheels.eeems.codes/ \
	nuitka \
	-r requirements.txt
echo "[info] Building"
export NUITKA_CACHE_DIR=/src/.nuitka
python -m nuitka \
    --assume-yes-for-downloads \
    --remove-output \
    --output-dir=dist \
    --onefile \
    --report=compilation-report.xml \
    --user-package-configuration-file=libremarkable/libremarkable.config.yml \
    $$file
endef
export EXECUTABLE_SCRIPT

ifeq ($(VENV_BIN_ACTIVATE),)
VENV_BIN_ACTIVATE := .venv/bin/activate
endif

ifeq ($(VENV_BIN_SPHINX),)
VENV_BIN_SPHINX := .venv/bin/sphinx-build
endif

ifeq ($(VENV_BIN_SPHINX_AUTOBUILD),)
VENV_BIN_SPHINX_AUTOBUILD := .venv/bin/sphinx-autobuild
endif

ifeq ($(PYTHON),)
PYTHON := python
endif

REMOTE_PYTHON := ssh root@10.11.99.1 -- PATH=${PATH} /opt/bin/python -ttu

$(VENV_BIN_ACTIVATE): requirements.txt
	$(PYTHON) -m venv .venv
	. $(VENV_BIN_ACTIVATE); \
	python -m pip install \
	    --extra-index-url=https://wheels.eeems.codes/ \
	    ruff \
	    build \
	    -r requirements.txt

$(VENV_BIN_SPHINX): $(VENV_BIN_ACTIVATE) doc/requirements.txt
	. $(VENV_BIN_ACTIVATE); \
	python -m pip install \
	    --extra-index-url=https://wheels.eeems.codes/ \
	    ruff \
	    build \
	    -r doc/requirements.txt

$(VENV_BIN_SPHINX_AUTOBUILD): $(VENV_BIN_SPHINX)

dist/libremarkable-${VERSION}.tar.gz: $(VENV_BIN_ACTIVATE) $(OBJ)
	. $(VENV_BIN_ACTIVATE); \
	python -m build --sdist

dist/libremarkable-${VERSION}-py3-none-any.whl: $(VENV_BIN_ACTIVATE)  $(OBJ)
	. $(VENV_BIN_ACTIVATE); \
	python -m build --wheel

.PHONY: clean # Clean the directory of any build artifacts
clean:
	git clean --force -dX

.PHONY: wheel # build a wheel for the library
wheel: dist/libremarkable-${VERSION}-py3-none-any.whl

.PHONY: srcdist # Build a srcdist for the library
srcdist: dist/libremarkable-${VERSION}.tar.gz

.PHONY: deploy # Deploy the library to the tablet
deploy: dist/libremarkable-${VERSION}-py3-none-any.whl
	ssh root@10.11.99.1 mkdir -p /opt/include/linux
	rsync vendor/input-event-codes.h root@10.11.99.1:/opt/include/linux/
	rsync dist/libremarkable-${VERSION}-py3-none-any.whl root@10.11.99.1:/tmp

.PHONY: install # Install the library on the tablet
install: deploy
	printf "%s\n" "$$INSTALL_SCRIPT" | ssh root@10.11.99.1 bash -le

.PHONY: test-device # Run test.py on the tablet
test-device: lint format install
	cat test.py | $(REMOTE_PYTHON)

.PHONY: test # Run test.py
test: lint format $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python test.py

dist/test.bin: $(OBJ) test.py
	docker run --privileged --rm tonistiigi/binfmt --install linux/arm/v7
	docker run \
	  --rm \
	  --platform=linux/arm/v7 \
	  -v "$$(pwd)":/src \
	  -e file=test.py \
	  eeems/nuitka-arm-builder:bullseye-3.11 \
	  bash -ec "$$EXECUTABLE_SCRIPT"

.PHONY: deploy-executable # Deploy an executable of test.py to the tablet
deploy-executable: dist/test.bin
	ssh root@10.11.99.1 "mkdir -p /tmp/libremarkable"
	rsync dist/test.bin root@10.11.99.1:/tmp/libremarkable

.PHONY: test-executable # Run an executable of test.py on the tablet
test-executable: deploy-executable
	ssh root@10.11.99.1 "LD_LIBRARY_PATH=/tmp/libremarkable /tmp/libremarkable/test.bin"

.PHONY: lint # Lint the project
lint: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff check

.PHONY: lint-fix # Lint the project and apply any fixes
lint-fix: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff check

.PHONY: format # Check the format of the project
format: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff format --diff

.PHONY: format-fix # Check the format of the project and apply any fixes
format-fix: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff format

EXAMPLES := $(wildcard examples/*.py)

EXAMPLE_TARGETS = $(patsubst examples/%.py, example_%, $(EXAMPLES))
.PHONY: $(EXAMPLE_TARGETS) # Run an example script on the tablet
$(EXAMPLE_TARGETS):example_%: lint format install examples/%.py
	name=$@; \
	name=$${name:8}; \
	cat examples/$$name.py | $(REMOTE_PYTHON)

$$(EXAMPLE_TARGETS):
	@echo ${EXAMPLE_TARGETS} | xargs -n1

EXAMPLE_BIN_TARGETS = $(patsubst examples/%.py, dist/%.bin, $(EXAMPLES))
$(EXAMPLE_BIN_TARGETS):dist/%.bin:  $(OBJ) examples/%.py
	docker run --privileged --rm tonistiigi/binfmt --install linux/arm/v7
	docker run \
	  --rm \
	  --platform=linux/arm/v7 \
	  -v "$$(pwd)":/src \
	  -e file=examples/$$(basename --suffix .bin $@).py \
	  eeems/nuitka-arm-builder:bullseye-3.11 \
	  bash -ec "$$EXECUTABLE_SCRIPT"

EXAMPLE_DEPLOY_TARGETS = $(patsubst examples/%.py, deploy-example_%, $(EXAMPLES))
$(EXAMPLE_DEPLOY_TARGETS):deploy-example_%: dist/%.bin
	ssh root@10.11.99.1 "mkdir -p /tmp/libremarkable"
	name=$@; \
	name=$${name:15}; \
	rsync dist/$$name.bin root@10.11.99.1:/tmp/libremarkable

EXAMPLE_TEST_TARGETS = $(patsubst examples/%.py, test-example_%, $(EXAMPLES))
.PHONY: $(EXAMPLE_TEST_TARGETS) # Run a binary of an example script on the tablet
$(EXAMPLE_TEST_TARGETS):test-example_%: deploy-example-%
	name=$@; \
	name=$${name:13}; \
	ssh root@10.11.99.1 "LD_LIBRARY_PATH=/tmp/libremarkable /tmp/libremarkable/$$name.bin"

$$(EXAMPLE_TEST_TARGETS):
	@echo ${EXAMPLE_TEST_TARGETS} | xargs -n1

.PHONY: doc # Build documentation
doc: $(VENV_BIN_SPHINX)
	$(VENV_BIN_SPHINX) -a -n -E -b html doc dist/doc

.PHONY: doc-dev # Automatically build documentation when there are changes
doc-dev: $(VENV_BIN_SPHINX_AUTOBUILD)
	$(VENV_BIN_SPHINX_AUTOBUILD) \
	    --port=0 \
	    --open-browser \
	    --watch libremarkable \
	    -a doc dist/doc

.PHONY: help # List all available targets
help:
	@expand_variables(){ \
	  col=24; \
	  size=$$(tput cols); \
	  size=$$(($$size - $$col)); \
	  indent=$$(echo "\t" | expand -t10); \
	  while read -r line; do \
	    name=$$(echo "$$line" | cut -f1); \
	    echo -e "$$name$$( \
	      echo "$$line" \
	      | cut -f2 \
	      | xargs -I % echo -e "\t%" \
	      | fmt -w$$size \
	    )" \
	    | expand -t$$col; \
	    if [[ "$$name" != "$$"* ]];then \
	      continue; \
	    fi; \
	    $(MAKE) --debug=none --no-print-directory $$name \
	    | xargs -I % echo -e "  %" \
	    | expand -t$$col; \
	  done; \
	}; \
	grep '^.PHONY: .* #' Makefile \
	| sed 's/\.PHONY: \(.*\) # \(.*\)/\1\t\2/' \
	| expand_variables
