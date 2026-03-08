import Foundation
import SwiftUI

enum AppAppearance: String, CaseIterable, Codable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var title: String {
        switch self {
        case .system:
            return "System"
        case .light:
            return "Light"
        case .dark:
            return "Dark"
        }
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system:
            return nil
        case .light:
            return .light
        case .dark:
            return .dark
        }
    }
}

struct AppSettings: Codable {
    var appearance: AppAppearance
    var chatGPTIntegrationEnabled: Bool
    var protectAllSensitiveDataEnabled: Bool
    var enabledEntityTypes: [String]
    var emojiTagsEnabled: Bool
    var highlightChangedTextEnabled: Bool
    var reversePronounsEnabled: Bool
    var redactionModeEnabled: Bool

    static let `default` = AppSettings(
        appearance: .system,
        chatGPTIntegrationEnabled: false,
        protectAllSensitiveDataEnabled: true,
        enabledEntityTypes: ["PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG", "DATE", "URL"],
        emojiTagsEnabled: false,
        highlightChangedTextEnabled: true,
        reversePronounsEnabled: false,
        redactionModeEnabled: false
    )

    private enum CodingKeys: String, CodingKey {
        case appearance
        case chatGPTIntegrationEnabled
        case protectAllSensitiveDataEnabled
        case enabledEntityTypes
        case emojiTagsEnabled
        case highlightChangedTextEnabled
        case reversePronounsEnabled
        case redactionModeEnabled
    }

    init(
        appearance: AppAppearance,
        chatGPTIntegrationEnabled: Bool,
        protectAllSensitiveDataEnabled: Bool,
        enabledEntityTypes: [String],
        emojiTagsEnabled: Bool,
        highlightChangedTextEnabled: Bool,
        reversePronounsEnabled: Bool,
        redactionModeEnabled: Bool
    ) {
        self.appearance = appearance
        self.chatGPTIntegrationEnabled = chatGPTIntegrationEnabled
        self.protectAllSensitiveDataEnabled = protectAllSensitiveDataEnabled
        self.enabledEntityTypes = enabledEntityTypes
        self.emojiTagsEnabled = emojiTagsEnabled
        self.highlightChangedTextEnabled = highlightChangedTextEnabled
        self.reversePronounsEnabled = reversePronounsEnabled
        self.redactionModeEnabled = redactionModeEnabled
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        appearance = try container.decodeIfPresent(AppAppearance.self, forKey: .appearance) ?? .system
        chatGPTIntegrationEnabled = try container.decodeIfPresent(Bool.self, forKey: .chatGPTIntegrationEnabled) ?? false
        protectAllSensitiveDataEnabled = try container.decodeIfPresent(Bool.self, forKey: .protectAllSensitiveDataEnabled) ?? true
        enabledEntityTypes = try container.decodeIfPresent([String].self, forKey: .enabledEntityTypes) ?? AnonymizeEntityType.allCases.map(\.rawValue)
        emojiTagsEnabled = try container.decodeIfPresent(Bool.self, forKey: .emojiTagsEnabled) ?? false
        highlightChangedTextEnabled = try container.decodeIfPresent(Bool.self, forKey: .highlightChangedTextEnabled) ?? true
        reversePronounsEnabled = try container.decodeIfPresent(Bool.self, forKey: .reversePronounsEnabled) ?? false
        redactionModeEnabled = try container.decodeIfPresent(Bool.self, forKey: .redactionModeEnabled) ?? false
    }
}

@MainActor
final class AppSettingsStore: ObservableObject {
    static let shared = AppSettingsStore()

    private enum Keys {
        static let settings = "shared.app.settings"
    }

    @Published private(set) var settings: AppSettings

    private let defaults: UserDefaults

    init(appGroupID: String = AppConfig.appGroupID) {
        self.defaults = UserDefaults(suiteName: appGroupID) ?? .standard

        if let data = defaults.data(forKey: Keys.settings),
           let decoded = try? JSONDecoder().decode(AppSettings.self, from: data) {
            self.settings = decoded
        } else {
            self.settings = .default
        }
    }

    func setAppearance(_ appearance: AppAppearance) {
        settings.appearance = appearance
        persist()
    }

    func setChatGPTIntegration(_ enabled: Bool) {
        settings.chatGPTIntegrationEnabled = enabled
        persist()
    }

    func setProtectAllSensitiveDataEnabled(_ enabled: Bool) {
        settings.protectAllSensitiveDataEnabled = enabled
        persist()
    }

    func setEmojiTagsEnabled(_ enabled: Bool) {
        settings.emojiTagsEnabled = enabled
        persist()
    }

    func setHighlightChangedTextEnabled(_ enabled: Bool) {
        settings.highlightChangedTextEnabled = enabled
        persist()
    }

    func setReversePronounsEnabled(_ enabled: Bool) {
        settings.reversePronounsEnabled = enabled
        persist()
    }

    func setRedactionModeEnabled(_ enabled: Bool) {
        settings.redactionModeEnabled = enabled
        persist()
    }

    func isEntityEnabled(_ entity: AnonymizeEntityType) -> Bool {
        settings.enabledEntityTypes.contains(entity.rawValue)
    }

    func canDisableEntity(_ entity: AnonymizeEntityType) -> Bool {
        if isEntityEnabled(entity) == false { return true }
        return selectedEntityTypes().count > 1
    }

    func setEntity(_ entity: AnonymizeEntityType, enabled: Bool) {
        var selected = settings.enabledEntityTypes
        if enabled {
            if selected.contains(entity.rawValue) == false {
                selected.append(entity.rawValue)
            }
        } else {
            selected.removeAll { $0 == entity.rawValue }
            if selected.isEmpty {
                return
            }
        }
        settings.enabledEntityTypes = selected
        persist()
    }

    func selectedEntityTypes() -> [String] {
        if settings.protectAllSensitiveDataEnabled {
            return AnonymizeEntityType.allCases.map(\.rawValue)
        }
        let configured = settings.enabledEntityTypes
        let allowed = Set(AnonymizeEntityType.allCases.map(\.rawValue))
        let filtered = configured.filter { allowed.contains($0) }
        return filtered.isEmpty ? AnonymizeEntityType.allCases.map(\.rawValue) : filtered
    }

    private func persist() {
        if let data = try? JSONEncoder().encode(settings) {
            defaults.set(data, forKey: Keys.settings)
        }
    }
}
