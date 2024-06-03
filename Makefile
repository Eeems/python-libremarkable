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
NUITKA_CACHE_DIR=$(pwd)/.nuitka \
python -m nuitka \
    --assume-yes-for-downloads \
    --remove-output \
    --output-dir=dist \
    --report=compilation-report.xml \
    test.py
endef
export EXECUTABLE_SCRIPT
define TAR_SCRIPT
echo "[info] Installing dependencies"
export DEBIAN_FRONTEND="noninteractive"
apt-get -y update
apt-get install -y \
  libtiff5 \
  libjpeg62-turbo \
  libopenjp2-7 \
  zlib1g \
  libfreetype6 \
  tcl8.6 \
  tk8.6 \
  python3-tk \
  libxcb1
cd /usr/lib/arm-linux-gnueabihf
tar -czf /src/dist/test.tar.gz \
  libopenjp2.so.* \
  libxcb.so.* \
  libXau.so.* \
  libXdmcp.so.* \
  libbsd.so.* \
  libmd.so.* \
  -C /src/dist \
  test.bin
endef
export TAR_SCRIPT


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

dist/libremarkable-${VERSION}.tar.gz: $(VENV_BIN_ACTIVATE) $(OBJ)
	. $(VENV_BIN_ACTIVATE); \
	python -m build --sdist

dist/libremarkable-${VERSION}-py3-none-any.whl: $(VENV_BIN_ACTIVATE)  $(OBJ)
	. $(VENV_BIN_ACTIVATE); \
	python -m build --wheel

clean:
	git clean --force -dX

wheel: dist/libremarkable-${VERSION}-py3-none-any.whl

srcdist: dist/libremarkable-${VERSION}.tar.gz

deploy: dist/libremarkable-${VERSION}-py3-none-any.whl
	ssh root@10.11.99.1 mkdir -p /opt/include/linux
	rsync vendor/input-event-codes.h root@10.11.99.1:/opt/include/linux/
	rsync dist/libremarkable-${VERSION}-py3-none-any.whl root@10.11.99.1:/tmp

install: deploy
	echo -e "$$INSTALL_SCRIPT" | ssh root@10.11.99.1 bash -le

test: install
	cat test.py \
	| ssh root@10.11.99.1 \
	  "bash -ec 'PATH=${PATH} /opt/bin/python -u'"

dist/test.bin: $(shell find libremarkable -type f) test.py
	docker run --privileged --rm tonistiigi/binfmt --install linux/arm/v7
	docker run \
	  --rm \
	  --platform=linux/arm/v7 \
	  -v "$$(pwd)":/src \
	  eeems/nuitka-arm-builder:bullseye-3.11 \
	  bash -ec "$$EXECUTABLE_SCRIPT"

dist/test.tar.gz: dist/test.bin
	docker run --privileged --rm tonistiigi/binfmt --install linux/arm/v7
	docker run \
	  --rm \
	  --platform=linux/arm/v7 \
	  -v "$$(pwd)":/src \
	  eeems/nuitka-arm-builder:bullseye-3.11 \
	  bash -ec "$$TAR_SCRIPT"

deploy-executable: dist/test.tar.gz
	ssh root@10.11.99.1 "mkdir -p /tmp/test"
	rsync dist/test.tar.gz root@10.11.99.1:/tmp
	ssh root@10.11.99.1 "tar -C /tmp/test -zxf /tmp/test.tar.gz"

test-executable: deploy-executable
	ssh root@10.11.99.1 "LD_LIBRARY_PATH=/tmp/test /tmp/test/test.bin"

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
