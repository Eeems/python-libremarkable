VERSION := $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
PATH := "/opt/bin:/opt/sbin:/home/root/.local/bin:/opt/bin:/opt/sbin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"

define SCRIPT
export PATH=${PATH}
if ! type pip &> /dev/null; then
    if ! type opkg &> /dev/null; then
        echo "Opkg not found, please install toltec"
        exit 1
    fi
    opkg update
    opkg install python3-pip
fi
pip install \
  --force-reinstall \
  --extra-index-url https://wheels.eeems.codes \
  /tmp/libremarkable-${VERSION}-py3-none-any.whl
endef
export SCRIPT

dist/libremarkable-${VERSION}.tar.gz: $(shell find libremarkable -type f)
	python -m build --sdist

dist/libremarkable-${VERSION}-py3-none-any.whl: $(shell find libremarkable -type f)
	python -m build --wheel

clean:
	git clean --force -dX

deploy: dist/libremarkable-${VERSION}-py3-none-any.whl
	rsync dist/libremarkable-${VERSION}-py3-none-any.whl root@10.11.99.1:/tmp

install: deploy
	echo -e "$$SCRIPT" | ssh root@10.11.99.1 bash -le

test: install
	cat test.py \
	| ssh root@10.11.99.1 \
	  "bash -ec 'PATH=${PATH} /opt/bin/python -u'"

.PHONY: clean install test deploy
