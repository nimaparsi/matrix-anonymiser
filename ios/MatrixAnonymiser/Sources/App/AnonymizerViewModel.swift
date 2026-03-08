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
        settingsStore: AppSettingsStore = .shared
    ) {
        self.apiClient = apiClient
        self.sharedStore = sharedStore
        self.settingsStore = settingsStore
    }

    var hasOutput: Bool {
        outputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false
    }

    func loadSharedInputIfNeeded() {
        if let pending = sharedStore.consumePendingInput(), pending.isEmpty == false {
            inputText = pending
        }

        if hasOutput == false,
           let payload = sharedStore.fetchLastPayload(),
           payload.anonymizedText.isEmpty == false {
            outputText = payload.anonymizedText
        }
    }

    func anonymize() async {
        errorMessage = nil
        usageLimitState = nil
        isLoading = true
        defer { isLoading = false }

        do {
            let entities = settingsStore.selectedEntityTypes()
            let result = try await apiClient.anonymize(text: inputText, entityTypes: entities)
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
        guard settingsStore.settings.chatGPTIntegrationEnabled else { return }
        guard let url = URL(string: "chatgpt://") else { return }
        guard UIApplication.shared.canOpenURL(url) else { return }
        UIApplication.shared.open(url)
    }

    func openUpgradePage() {
        UIApplication.shared.open(AppConfig.defaultAPIBaseURL)
    }
}
