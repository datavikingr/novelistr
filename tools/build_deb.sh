#!/usr/bin/env bash

# Run after newbinary.sh; requires dpkg. If on Fedora/etc, run `sudo dnf install dpkg -y`; yes, really.
# Outputs to dist/novelistr_X.X.X_amd64.deb
#NOTE: Don't forget the --bump syntax!

set -e

# Find and move to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$ROOT_DIR"
VERSION_FILE="$ROOT_DIR/VERSION"

# Optional bump argument for automatic versioning and changelog.txt generation
if [[ "$1" =~ ^--bump(=major|=minor|=patch)?$ ]]; then
	if [[ ! -f "$VERSION_FILE" ]]; then
		echo "VERSION file not found!"
		exit 1
	fi
	VERSION=$(cat "$VERSION_FILE")
	IFS='.' read -r major minor patch <<< "$VERSION"
	case "$1" in
		"--bump=major")
			((major+=1)); minor=0; patch=0 ;;
		"--bump=minor")
			((minor+=1)); patch=0 ;;
		"--bump"|"--bump=patch"|*)
			((patch+=1)) ;;
	esac
	NEW_VERSION="$major.$minor.$patch"
	echo "$NEW_VERSION" > "$VERSION_FILE"
	echo "Version bumped to $NEW_VERSION"
	# Ask for changelog message
	read -p "📝 Changelog message: " changelog_msg
	echo "- $(date +"%Y-%m-%d %H:%M") - v$NEW_VERSION: $changelog_msg" >> changelog.txt
fi

# Setup
APP_NAME="novelistr"
VERSION=$(cat "$ROOT_DIR/VERSION")
ARCH="amd64"
BUILD_DIR="packaging"
DEB_DIR="$BUILD_DIR/${APP_NAME}-deb" #packaging/novelistr-deb
BIN_SRC="dist/$APP_NAME" #dist/novelistr
ICON_SRC="assets/icon_64x64.png"
DESKTOP_FILE="$DEB_DIR/usr/share/applications/$APP_NAME.desktop" #packaging/novelistr-deb/usr/share/applications/novelistr.desktop
CONTROL_FILE="$DEB_DIR/DEBIAN/control" #packaging/novelistr-deb/DEBIAN/control

echo "Creating .deb package structure..."

# Clean previous builds
rm -rf "$DEB_DIR" # nukes packaging/novelistr-deb
mkdir -p "$DEB_DIR/DEBIAN" #rebuilds packaging/novelistr-deb/DEBIAN
mkdir -p "$DEB_DIR/usr/bin" #rebuilds packaging/novelistr-deb/usr/bin
mkdir -p "$DEB_DIR/usr/share/applications" #rebuilds packaging/novelistr-deb/usr/share/applications
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/64x64/apps" #rebuilds packaging/novelistr-deb/usr/share/icons/hicolor/32x32/apps

echo "Copying binary..."

# Copy binary
cp "$BIN_SRC" "$DEB_DIR/usr/bin/$APP_NAME" #cp dist/novelistr packaging/novelistr-deb/usr/bin/novelistr
chmod +x "$DEB_DIR/usr/bin/$APP_NAME" #makes executable

# Copy icon
cp "$ICON_SRC" "$DEB_DIR/usr/share/icons/hicolor/64x64/apps/$APP_NAME.png" #cp assets/icon_32x32.png packaging/novelistr-deb/usr/share/icons/hicolor/32x32/apps/novelistr.png

echo "Building .desktop file..."

# Create desktop entry
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Novelistr
Comment=Minimalist markdown-friendly writing app
Exec=$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Utility;TextEditor;
EOF

echo "Building control file..."

# Create control file
cat > "$CONTROL_FILE" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: 
Maintainer: Alex Haskins alexanderhaskins@proton.me
Description: Novelistr - A dark-mode, markdown-friendly writing editor
 A minimalist writing tool with formatting support, autosave, and recent file tracking.
EOF

# Build the .deb
echo "Building package..."
dpkg-deb --build "$DEB_DIR"

# Rename for clarity
mv "$DEB_DIR.deb" "dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "Done! .deb created at $BUILD_DIR/${APP_NAME}_${VERSION}_${ARCH}.deb"