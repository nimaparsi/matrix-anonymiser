#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IOS_DIR="$ROOT_DIR/ios/MatrixAnonymiser"
PROJECT_PATH="$IOS_DIR/MatrixAnonymiser.xcodeproj"
SCHEME="MatrixAnonymiser"
BUNDLE_ID="com.matrix.anonymiser"
DEFAULT_SIMULATOR="iPhone 17"
SIMULATOR_NAME="${IOS_SIMULATOR_NAME:-$DEFAULT_SIMULATOR}"
CONFIGURATION="${IOS_CONFIGURATION:-Debug}"

if [[ ! -d "$PROJECT_PATH" ]]; then
  echo "Missing Xcode project: $PROJECT_PATH" >&2
  exit 1
fi

if [[ -z "${DEVELOPER_DIR:-}" ]] && [[ -d "/Applications/Xcode.app/Contents/Developer" ]]; then
  export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
fi

if ! command -v xcodebuild >/dev/null 2>&1; then
  echo "xcodebuild is unavailable. Install Xcode and ensure DEVELOPER_DIR points to Xcode.app." >&2
  exit 1
fi

if ! command -v xcrun >/dev/null 2>&1; then
  echo "xcrun is unavailable. Install Xcode command line tools." >&2
  exit 1
fi

find_simulator_udid() {
  local name="$1"
  while IFS= read -r line; do
    case "$line" in
      *"$name ("*)
        printf '%s\n' "$line" | sed -E 's/.*\(([A-F0-9-]+)\).*/\1/'
        return 0
        ;;
    esac
  done < <(xcrun simctl list devices available)
}

SIMULATOR_UDID="$(find_simulator_udid "$SIMULATOR_NAME")"

if [[ -z "$SIMULATOR_UDID" ]]; then
  echo "Simulator \"$SIMULATOR_NAME\" not found. Set IOS_SIMULATOR_NAME to an available device." >&2
  echo "Available simulators:" >&2
  xcrun simctl list devices available >&2
  exit 1
fi

echo "Using simulator: $SIMULATOR_NAME ($SIMULATOR_UDID)"
xcrun simctl bootstatus "$SIMULATOR_UDID" >/dev/null 2>&1 || xcrun simctl boot "$SIMULATOR_UDID"
open -a Simulator --args -CurrentDeviceUDID "$SIMULATOR_UDID"
xcrun simctl bootstatus "$SIMULATOR_UDID" -b

BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

echo "Building $SCHEME for iOS Simulator..."
xcodebuild \
  -project "$PROJECT_PATH" \
  -scheme "$SCHEME" \
  -configuration "$CONFIGURATION" \
  -sdk iphonesimulator \
  -destination "id=$SIMULATOR_UDID" \
  -derivedDataPath "$BUILD_DIR" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  build

APP_PATH="$(find "$BUILD_DIR/Build/Products" -maxdepth 3 -type d -name '*.app' ! -path '*/PlugIns/*' | head -n 1)"

if [[ -z "$APP_PATH" ]]; then
  echo "Built app not found in $BUILD_DIR/Build/Products" >&2
  exit 1
fi

echo "Installing app from: $APP_PATH"
xcrun simctl install "$SIMULATOR_UDID" "$APP_PATH"

echo "Launching app..."
xcrun simctl launch "$SIMULATOR_UDID" "$BUNDLE_ID"

echo "App launched in Simulator."
