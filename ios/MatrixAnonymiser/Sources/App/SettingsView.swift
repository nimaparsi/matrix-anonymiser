import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var settingsStore: AppSettingsStore

    var body: some View {
        Form {
            Section("Appearance") {
                Picker("Theme", selection: Binding(
                    get: { settingsStore.settings.appearance },
                    set: { settingsStore.setAppearance($0) }
                )) {
                    ForEach(AppAppearance.allCases) { appearance in
                        Text(appearance.title).tag(appearance)
                    }
                }
                .pickerStyle(.segmented)
            }
        }
        .navigationTitle("Settings")
    }
}
