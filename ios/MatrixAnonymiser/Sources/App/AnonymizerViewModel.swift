import Foundation
import UIKit

@MainActor
final class AnonymizerViewModel: ObservableObject {
    @Published var inputText: String = ""
    @Published var outputText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var usageLimitState: UsageLimitState?
    @Published var showCopiedToast: Bool = false

    private let apiClient: AnonymizeServicing
    private let sharedStore: SharedDataStore
    private let settingsStore: AppSettingsStore

    init(
        apiClient: AnonymizeServicing = AnonymizeAPIClient(),
        sharedStore: SharedDataStore = SharedDataStore(),
        settingsStore: AppSettingsStore? = nil
    ) {
        self.apiClient = apiClient
        self.sharedStore = sharedStore
        self.settingsStore = settingsStore ?? AppSettingsStore.shared
    }

    var hasOutput: Bool {
        outputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false
    }

    func loadSharedInputIfNeeded() {
        outputText = ""
        if let pending = sharedStore.consumePendingInput(), pending.isEmpty == false {
            inputText = pending
        }
    }

    func anonymize() async {
        errorMessage = nil
        usageLimitState = nil
        isLoading = true
        defer { isLoading = false }

        do {
            let entities = settingsStore.selectedEntityTypes()
            let tagStyle: AnonymizeTagStyle = settingsStore.settings.emojiTagsEnabled ? .emoji : .standard
            let result = try await apiClient.anonymize(text: inputText, entityTypes: entities, tagStyle: tagStyle)
            outputText = result
            sharedStore.saveLastPayload(original: inputText, anonymized: result)
            usageLimitState = nil
        } catch {
            if case .usageLimitReached(let limitState) = (error as? AnonymizeClientError) {
                outputText = ""
                usageLimitState = limitState
                errorMessage = nil
            } else {
                outputText = ""
                errorMessage = error.localizedDescription
            }
        }
    }

    func copyOutput() {
        guard hasOutput else { return }
        UIPasteboard.general.string = outputText
        showCopiedToast = true
    }

    func clearAll() {
        inputText = ""
        outputText = ""
        errorMessage = nil
        usageLimitState = nil
    }

    func openChatGPT() {
        guard let url = URL(string: "chatgpt://") else { return }
        guard UIApplication.shared.canOpenURL(url) else { return }
        UIApplication.shared.open(url)
    }

    func openUpgradePage() {
        UIApplication.shared.open(AppConfig.defaultAPIBaseURL)
    }
}
