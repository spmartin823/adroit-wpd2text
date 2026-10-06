#!/usr/bin/env bash
set -euo pipefail

ARCHITECTURE="$1"
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$ARCHITECTURE" = "arm64" ]; then
  WHEEL_ARCHITECTURE="aarch64"
else
  WHEEL_ARCHITECTURE="x86_64"
fi

mkdir -p "$PACKAGE_DIR/src/adroit_wpd2text"
rm -rf "$PACKAGE_DIR/src/adroit_wpd2text/bin" \
  "$PACKAGE_DIR/src/adroit_wpd2text/lib" \
  "$PACKAGE_DIR/src/adroit_wpd2text/licenses"
docker run --rm --platform "linux/$ARCHITECTURE" \
  --volume "$PACKAGE_DIR/src/adroit_wpd2text:/package" \
  amazonlinux:2023 \
  sh -c '
    dnf install -y libwpd-tools >/dev/null
    mkdir -p /package/bin /package/lib /package/licenses
    cp /usr/bin/wpd2text /package/bin/
    cp -L /lib64/libwpd-0.10.so.10 /package/lib/
    cp -L /lib64/librevenge-0.0.so.0 /package/lib/
    cp -L /lib64/librevenge-generators-0.0.so.0 /package/lib/
    cp -L /lib64/librevenge-stream-0.0.so.0 /package/lib/
    cp /usr/share/licenses/libwpd/COPYING.MPL /package/licenses/libwpd-MPL-2.0.txt
    cp /usr/share/licenses/libwpd/COPYING.LGPL /package/licenses/libwpd-LGPL-2.1.txt
    cp /usr/share/licenses/librevenge/COPYING.MPL /package/licenses/librevenge-MPL-2.0.txt
    cp /usr/share/licenses/librevenge/COPYING.LGPL /package/licenses/librevenge-LGPL-2.1.txt
  '

cd "$PACKAGE_DIR"
rm -rf build
python -m build --wheel
python -m wheel tags --remove --python-tag py3 --abi-tag none \
  --platform-tag "manylinux_2_34_$WHEEL_ARCHITECTURE" dist/*-cp*-cp*-*.whl
