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

            Section("Anonymisation Tags") {
                ForEach(AnonymizeEntityType.allCases) { entity in
                    Toggle(entity.title, isOn: Binding(
                        get: { settingsStore.isEntityEnabled(entity) },
                        set: { settingsStore.setEntity(entity, enabled: $0) }
                    ))
                    .disabled(settingsStore.canDisableEntity(entity) == false)
                }

                Text("At least one tag must stay enabled.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            Section("Integrations") {
                Toggle("Integrate with ChatGPT", isOn: Binding(
                    get: { settingsStore.settings.chatGPTIntegrationEnabled },
                    set: { settingsStore.setChatGPTIntegration($0) }
                ))
                .toggleStyle(.switch)

                Text("When enabled, the home screen shows an Open ChatGPT action.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
        .navigationTitle("Settings")
    }
}
