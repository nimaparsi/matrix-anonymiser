# Matrix Anonymiser iOS (Native SwiftUI)

Native iOS app + Share Extension for Matrix Anonymiser.

## Stack
- Swift + SwiftUI
- iOS 16+
- Share Extension (text-only activation)
- App Group shared storage (`group.com.matrix.anonymiser.shared`)
- API client wired to `https://matrix-anonymiser.netlify.app/api/anonymize`

## Structure
- `Sources/App`: main iOS app UI and view models
- `Sources/ShareExtension`: share sheet extension UI/controller
- `Sources/Shared`: shared API client, models, and app-group data store
- `Config`: plist + entitlements
- `project.yml`: XcodeGen spec

## Generate Xcode Project
1. Install [XcodeGen](https://github.com/yonaskolb/XcodeGen)
2. From `ios/MatrixAnonymiser` run:

```bash
xcodegen generate
```

3. Open `MatrixAnonymiser.xcodeproj` in Xcode.

## Signing / Capabilities
Set your Apple Team and ensure both targets include:
- App Groups capability: `group.com.matrix.anonymiser.shared`

Bundle IDs in this scaffold:
- App: `com.matrix.anonymiser`
- Share extension: `com.matrix.anonymiser.share`

Adjust as needed in `project.yml` before generating.

## Notes
- Share extension activates for text (`NSExtensionActivationSupportsText = YES`).
- Main app includes a Privacy screen and optional `Open ChatGPT` button (`chatgpt://` scheme).
- No webview is used; UI is fully native SwiftUI.
