#!/usr/bin/env bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$ROOT_DIR"

APP_ID="com.novelistr.app"
MANIFEST="flatpak/${APP_ID}.yaml"
BUILD_DIR="flatpak-build"
REPO_DIR="flatpak-repo"
BUNDLE_NAME="novelistr.flatpak"

echo "==> Cleaning up old build..."
rm -rf "$BUILD_DIR" "$REPO_DIR"

echo "==> Building Flatpak app..."
flatpak-builder --force-clean --repo="$REPO_DIR" "$BUILD_DIR" "$MANIFEST"

echo "==> Creating bundle..."
flatpak build-bundle "$REPO_DIR" "dist/$BUNDLE_NAME" "$APP_ID"

echo "Flatpak bundle created at dist/$BUNDLE_NAME"