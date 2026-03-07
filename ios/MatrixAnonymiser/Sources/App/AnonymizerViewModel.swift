import Foundation
import UIKit

@MainActor
final class AnonymizerViewModel: ObservableObject {
    @Published var inputText: String = ""
    @Published var outputText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showCopiedToast: Bool = false

    private let apiClient: AnonymizeServicing
    private let sharedStore: SharedDataStore

    init(
        apiClient: AnonymizeServicing = AnonymizeAPIClient(),
        sharedStore: SharedDataStore = SharedDataStore()
    ) {
        self.apiClient = apiClient
        self.sharedStore = sharedStore
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
        isLoading = true
        defer { isLoading = false }

        do {
            let result = try await apiClient.anonymize(text: inputText)
            outputText = result
            sharedStore.saveLastPayload(original: inputText, anonymized: result)
        } catch {
            outputText = ""
            errorMessage = error.localizedDescription
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
    }

    func openChatGPT() {
        guard let url = URL(string: "chatgpt://") else { return }
        guard UIApplication.shared.canOpenURL(url) else { return }
        UIApplication.shared.open(url)
    }
}
