import SwiftUI

@main
struct MatrixAnonymiserApp: App {
    @StateObject private var settingsStore = AppSettingsStore.shared

    var body: some Scene {
        WindowGroup {
            MainAnonymizerView()
                .environmentObject(settingsStore)
                .preferredColorScheme(settingsStore.settings.appearance.colorScheme)
                .tint(BrandTheme.accent)
        }
    }
}
