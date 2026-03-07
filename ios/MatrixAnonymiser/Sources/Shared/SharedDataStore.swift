import Foundation

struct SharedAnonymizePayload: Codable {
    let originalText: String
    let anonymizedText: String
    let createdAt: Date
}

final class SharedDataStore {
    private enum Keys {
        static let pendingInput = "shared.pending.input"
        static let lastPayload = "shared.last.payload"
    }

    private let defaults: UserDefaults

    init(appGroupID: String = AppConfig.appGroupID) {
        self.defaults = UserDefaults(suiteName: appGroupID) ?? .standard
    }

    func savePendingInput(_ text: String) {
        defaults.set(text, forKey: Keys.pendingInput)
    }

    func consumePendingInput() -> String? {
        let value = defaults.string(forKey: Keys.pendingInput)
        defaults.removeObject(forKey: Keys.pendingInput)
        return value
    }

    func saveLastPayload(original: String, anonymized: String) {
        let payload = SharedAnonymizePayload(
            originalText: original,
            anonymizedText: anonymized,
            createdAt: Date()
        )
        if let data = try? JSONEncoder().encode(payload) {
            defaults.set(data, forKey: Keys.lastPayload)
        }
    }

    func fetchLastPayload() -> SharedAnonymizePayload? {
        guard let data = defaults.data(forKey: Keys.lastPayload) else {
            return nil
        }
        return try? JSONDecoder().decode(SharedAnonymizePayload.self, from: data)
    }
}
