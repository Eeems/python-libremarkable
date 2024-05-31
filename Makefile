VERSION := $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
PATH := "/opt/bin:/opt/sbin:/home/root/.local/bin:/opt/bin:/opt/sbin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"

define INSTALL_SCRIPT
export PATH=${PATH}
if ! type pip &> /dev/null; then
    if ! type opkg &> /dev/null; then
        echo "Opkg not found, please install toltec"
        exit 1
    fi
    opkg update
    opkg install python3-pip
fi
if ! python -c 'import PIL' &> /dev/null; then
    if ! type opkg &> /dev/null; then
        echo "Opkg not found, please install toltec"
        exit 1
    fi
    opkg update
    opkg install python3-pillow
fi
pip uninstall -qy libremarkable
pip install \
  --extra-index-url https://wheels.eeems.codes \
  /tmp/libremarkable-${VERSION}-py3-none-any.whl
endef
export INSTALL_SCRIPT
define EXECUTABLE_SCRIPT
cd /src
source /opt/lib/nuitka/bin/activate
echo "[info] Installing dependencies"
python -m pip install \
	--extra-index-url=https://wheels.eeems.codes/ \
	wheel \
	nuitka \
	-r requirements.txt
echo "[info] Building"
NUITKA_CACHE_DIR=$(pwd)/.nuitka \
python -m nuitka \
    --assume-yes-for-downloads \
    --remove-output \
    --output-dir=dist \
    --report=compilation-report.xml \
    test.py
endef
export EXECUTABLE_SCRIPT


ifeq ($(VENV_BIN_ACTIVATE),)
VENV_BIN_ACTIVATE := .venv/bin/activate
endif

$(VENV_BIN_ACTIVATE):
	python -m venv .venv
	. $(VENV_BIN_ACTIVATE); \
	python -m pip install \
	    --extra-index-url=https://wheels.eeems.codes/ \
	    ruff \
	    build

dist/libremarkable-${VERSION}.tar.gz: $(VENV_BIN_ACTIVATE) $(shell find libremarkable -type f) pyproject.toml
	. $(VENV_BIN_ACTIVATE); \
	python -m build --sdist

dist/libremarkable-${VERSION}-py3-none-any.whl: $(VENV_BIN_ACTIVATE)  $(shell find libremarkable -type f) pyproject.toml
	. $(VENV_BIN_ACTIVATE); \
	python -m build --wheel

clean:
	git clean --force -dX

wheel: dist/libremarkable-${VERSION}-py3-none-any.whl

srcdist: dist/libremarkable-${VERSION}.tar.gz

deploy: dist/libremarkable-${VERSION}-py3-none-any.whl
	rsync dist/libremarkable-${VERSION}-py3-none-any.whl root@10.11.99.1:/tmp

install: deploy
	echo -e "$$INSTALL_SCRIPT" | ssh root@10.11.99.1 bash -le

test: install
	cat test.py \
	| ssh root@10.11.99.1 \
	  "bash -ec 'PATH=${PATH} /opt/bin/python -u'"

dist/test.bin: $(shell find libremarkable -type f)
	docker run --privileged --rm tonistiigi/binfmt --install all
	docker run \
	  --rm \
	  --platform=linux/arm/v7 \
	  -v "$$(pwd)":/src \
	  eeems/nuitka-arm-builder:bullseye-3.11 \
	  bash -ec "$$EXECUTABLE_SCRIPT"

deploy-executable: dist/test.bin
	rsync dist/test.bin root@10.11.99.1:/tmp

test-executable: deploy-executable
	ssh root@10.11.99.1 /tmp/test.bin

lint: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff check

lint-fix: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff check

format: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff format --check

format-fix: $(VENV_BIN_ACTIVATE)
	. $(VENV_BIN_ACTIVATE); \
	python -m ruff format --check


.PHONY: clean install test deploy test-executable deploy-executable lint format _ruff wheel srcdist
