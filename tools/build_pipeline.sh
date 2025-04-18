#!/usr/bin/env bash

# Requires dpkg (sudo dnf install dpkg, if on Fedora), PyInstaller (pip install pyinstall), &
# flatpak SDK (flatpak install flathub org.freedesktop.Sdk//23.08)

set -e

LOG_DATE=$(date +"%Y.%m.%d.%H.%M")
LOG_NAME="build_${LOG_DATE}"
mkdir -p "logs"
exec > >(tee "logs/${LOG_NAME}.log") 2>&1

# =======================
# CONFIG & VERSION BUMP
# =======================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$ROOT_DIR"

APP_NAME="novelistr"
VERSION_FILE="$ROOT_DIR/VERSION"
CHANGELOG_FILE="$ROOT_DIR/changelog.txt"

BUILD_DATE=$(date +"%Y-%m-%d_%H-%M")
METAINFO_FILE="flatpak/files/share/metainfo/com.novelistr.app.metainfo.xml"

if [[ "$1" =~ ^--bump(=major|=minor|=patch)?$ ]]; then
  if [[ ! -f "$VERSION_FILE" ]]; then
    echo "VERSION file not found!"
    exit 1
  fi
  VERSION=$(cat "$VERSION_FILE")
  IFS='.' read -r major minor patch <<< "$VERSION"
  case "$1" in
    "--bump=major") ((major+=1)); minor=0; patch=0 ;;
    "--bump=minor") ((minor+=1)); patch=0 ;;
    "--bump"|"--bump=patch"|*) ((patch+=1)) ;;
  esac
  NEW_VERSION="$major.$minor.$patch"
  echo "$NEW_VERSION" > "$VERSION_FILE"
  echo "Version bumped to $NEW_VERSION"
  read -p "Changelog message: " changelog_msg
  echo "- $(date +"%Y-%m-%d %H:%M") - v$NEW_VERSION: $changelog_msg" >> "$CHANGELOG_FILE"

  # Update metainfo.xml
  sed -i "/<releases>/a \ \ \ \ <release version=\"$NEW_VERSION\" date=\"$(date +%Y-%m-%d)\">\n\ \ \ \ \ \ \ <description>$changelog_msg</description>\n\ \ \ \ \ </release>" "$METAINFO_FILE"
  echo "AppStream metadata updated with release $NEW_VERSION"
fi

# =======================
# PYINSTALLER BUILD
# =======================

echo "=== Building PyInstaller binary ==="
pyinstaller --onefile --noconfirm --windowed \
  --icon=assets/icon_64x64.png \
  --add-data "assets:assets" \
  --hidden-import=customtkinter \
  novelistr.py

rm -rf build/ *.spec

# =======================
# DEB PACKAGE
# =======================

echo "=== Building .deb package ==="
VERSION=$(cat "$VERSION_FILE")
ARCH="amd64"
BUILD_DIR="packaging"
DEB_DIR="$BUILD_DIR/${APP_NAME}-deb" #packaging/novelistr-deb
BIN_SRC="dist/$APP_NAME" #dist/novelistr
ICON_SRC="assets/icon_64x64.png"
DESKTOP_FILE="$DEB_DIR/usr/share/applications/$APP_NAME.desktop" #packaging/novelistr-deb/usr/share/applications/novelistr.desktop
CONTROL_FILE="$DEB_DIR/DEBIAN/control" #packaging/novelistr-deb/DEBIAN/control

rm -rf "$DEB_DIR" # nukes packaging/novelistr-deb
mkdir -p "$DEB_DIR/DEBIAN" #rebuilds packaging/novelistr-deb/DEBIAN
mkdir -p "$DEB_DIR/usr/bin" #rebuilds packaging/novelistr-deb/usr/bin
mkdir -p "$DEB_DIR/usr/share/applications" #rebuilds packaging/novelistr-deb/usr/share/applications
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/64x64/apps" #rebuilds packaging/novelistr-deb/usr/share/icons/hicolor/64x64/apps

cp "$BIN_SRC" "$DEB_DIR/usr/bin/$APP_NAME" #cp dist/novelistr packaging/novelistr-deb/usr/bin/novelistr
chmod +x "$DEB_DIR/usr/bin/$APP_NAME" #makes executable
cp "$ICON_SRC" "$DEB_DIR/usr/share/icons/hicolor/64x64/apps/$APP_NAME.png" #cp assets/icon_64x64.png packaging/novelistr-deb/usr/share/icons/hicolor/64x64/apps/novelistr.png

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

cat > "$CONTROL_FILE" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends:
Maintainer: Alex Haskins - alexanderhaskins@proton.me
Description: Novelistr - A dark-mode, markdown-friendly writing editor
 A minimalist writing tool with formatting support, autosave, and recent file tracking.
EOF

dpkg-deb --build "$DEB_DIR"
mv "$DEB_DIR.deb" "dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
rm -rf "$DEB_DIR" "$BUILD_DIR"
echo ".deb file created at dist/${APP_NAME}_${VERSION}_${ARCH}.deb"

# =======================
# FLATPAK BUNDLE
# =======================

echo "=== Building Flatpak ==="
FLATPAK_APP_ID="com.novelistr.app"
FLATPAK_MANIFEST="flatpak/${FLATPAK_APP_ID}.yaml"
FLATPAK_BUILD_DIR="flatpak-build"
FLATPAK_REPO_DIR="flatpak-repo"
FLATPAK_BUNDLE_NAME="novelistr.flatpak"

rm -rf "$FLATPAK_BUILD_DIR" "$FLATPAK_REPO_DIR"

flatpak-builder --force-clean --repo="$FLATPAK_REPO_DIR" \
  "$FLATPAK_BUILD_DIR" "$FLATPAK_MANIFEST"

flatpak build-bundle "$FLATPAK_REPO_DIR" "dist/$FLATPAK_BUNDLE_NAME" "$FLATPAK_APP_ID"
echo "Flatpak bundle created at dist/$FLATPAK_BUNDLE_NAME"

rm -rf .flatpak-builder build-dir "$FLATPAK_BUILD_DIR" "$FLATPAK_REPO_DIR" repo

# =======================
# GIT COMMIT & TAG (if changelog_msg exists; and if it does, we're triggering GitHub workflows)
# =======================
if [[ -n "$changelog_msg" ]]; then
  echo "=== Committing and tagging for version v$NEW_VERSION ==="

  # Check if working directory is clean
  if [[ -n $(git status --porcelain) ]]; then
    git add .
    git commit -m "$changelog_msg"
  else
    echo "No changes to commit."
  fi

  # Tag only if it doesn't already exist
  if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
    echo "Tag v$NEW_VERSION already exists, skipping tag creation."
  else
    git tag "v$NEW_VERSION"
    git push origin "v$NEW_VERSION"
    echo "Tag v$NEW_VERSION pushed to origin."
  fi

  # Always push the commit (even if tag exists)
  git push origin main
fi

# =======================
# ALL DONE
# =======================
echo "🎉 All builds complete! Distributables available in ./dist/"
