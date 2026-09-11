#!/bin/bash

VERSION="1.0.0"
APP_NAME="betternote"
ARCH="amd64"

echo "Creating virtual environment..."
python3 -m venv .venv-linux
source .venv-linux/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo "Building Linux executable..."
# PyInstaller needs the --add-data format as "source:dest" on Linux
pyinstaller --name="BetterNote" \
            --windowed \
            --onefile \
            --add-data="resources:resources" \
            --clean \
            main.py

echo "Preparing .deb package structure in /tmp to avoid NTFS permission issues..."
DEB_BUILD_DIR="/tmp/${APP_NAME}_${VERSION}_${ARCH}"
rm -rf "$DEB_BUILD_DIR"
mkdir -p "$DEB_BUILD_DIR/DEBIAN"
mkdir -p "$DEB_BUILD_DIR/usr/bin"
mkdir -p "$DEB_BUILD_DIR/usr/share/applications"
mkdir -p "$DEB_BUILD_DIR/usr/share/icons/hicolor/256x256/apps"

# Ensure proper permissions for the build directory
chmod 0755 "$DEB_BUILD_DIR"
chmod 0755 "$DEB_BUILD_DIR/DEBIAN"

# Create the control file
cat <<EOF > "$DEB_BUILD_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: BetterNote Developer
Description: A minimal, distraction-free handwritten digital notebook for Windows & Linux.
EOF
chmod 0644 "$DEB_BUILD_DIR/DEBIAN/control"

# Create the .desktop file
cat <<EOF > "$DEB_BUILD_DIR/usr/share/applications/betternote.desktop"
[Desktop Entry]
Version=1.0
Name=BetterNote
Comment=Distraction-free handwritten digital notebook
Exec=/usr/bin/betternote
Icon=betternote
Terminal=false
Type=Application
Categories=Office;Utility;
EOF
chmod 0644 "$DEB_BUILD_DIR/usr/share/applications/betternote.desktop"

# Copy the executable and icon
cp "dist/BetterNote" "$DEB_BUILD_DIR/usr/bin/betternote"
chmod 0755 "$DEB_BUILD_DIR/usr/bin/betternote"

# Make sure we have an icon to copy (falling back gracefully if not found)
if [ -f "resources/icons/app_icon.png" ]; then
    cp "resources/icons/app_icon.png" "$DEB_BUILD_DIR/usr/share/icons/hicolor/256x256/apps/betternote.png"
    chmod 0644 "$DEB_BUILD_DIR/usr/share/icons/hicolor/256x256/apps/betternote.png"
fi

echo "Building .deb package..."
dpkg-deb --build "$DEB_BUILD_DIR"

echo "Copying back to dist directory..."
cp "/tmp/${APP_NAME}_${VERSION}_${ARCH}.deb" "dist/"
rm -rf "$DEB_BUILD_DIR" "/tmp/${APP_NAME}_${VERSION}_${ARCH}.deb"

echo "Build complete!"
echo "- Linux Executable: dist/BetterNote"
echo "- Debian Package: dist/${APP_NAME}_${VERSION}_${ARCH}.deb"

