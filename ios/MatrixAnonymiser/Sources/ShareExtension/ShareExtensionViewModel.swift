import Foundation
import UIKit
import UniformTypeIdentifiers

@MainActor
final class ShareExtensionViewModel: ObservableObject {
    @Published var originalText: String = ""
    @Published var anonymizedText: String = ""
    @Published var isLoading: Bool = false
    @Published var statusMessage: String?
    @Published var errorMessage: String?

    private let apiClient: AnonymizeServicing
    private let sharedStore: SharedDataStore

    init(
        apiClient: AnonymizeServicing = AnonymizeAPIClient(),
        sharedStore: SharedDataStore = SharedDataStore()
    ) {
        self.apiClient = apiClient
        self.sharedStore = sharedStore
    }

    func loadSharedText(from context: NSExtensionContext?) async {
        errorMessage = nil
        statusMessage = nil

        guard let text = await extractText(from: context), text.isEmpty == false else {
            errorMessage = "No text was found in the shared content."
            return
        }

        originalText = text
        await anonymize()
    }

    func anonymize() async {
        let cleaned = originalText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard cleaned.isEmpty == false else {
            errorMessage = "No text available to anonymise."
            return
        }

        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let output = try await apiClient.anonymize(text: cleaned)
            anonymizedText = output
            sharedStore.saveLastPayload(original: cleaned, anonymized: output)
            sharedStore.savePendingInput(cleaned)
        } catch {
            anonymizedText = ""
            errorMessage = error.localizedDescription
        }
    }

    func copyResult() {
        guard anonymizedText.isEmpty == false else { return }
        UIPasteboard.general.string = anonymizedText
        statusMessage = "Safe prompt copied"
    }

    func openMainApp(from context: NSExtensionContext?) {
        if originalText.isEmpty == false {
            sharedStore.savePendingInput(originalText)
        }
        if anonymizedText.isEmpty == false {
            sharedStore.saveLastPayload(original: originalText, anonymized: anonymizedText)
        }

        guard let url = URL(string: AppConfig.appURLScheme) else {
            context?.completeRequest(returningItems: nil)
            return
        }

        context?.open(url) { _ in
            context?.completeRequest(returningItems: nil)
        }
    }

    private func extractText(from context: NSExtensionContext?) async -> String? {
        guard let items = context?.inputItems as? [NSExtensionItem] else {
            return nil
        }

        for item in items {
            if let attributed = item.attributedContentText {
                let inlineText = attributed.string.trimmingCharacters(in: .whitespacesAndNewlines)
                if inlineText.isEmpty == false {
                    return inlineText
                }
            }

            for provider in item.attachments ?? [] {
                if let text = await provider.loadTextIfAvailable(type: UTType.plainText.identifier), text.isEmpty == false {
                    return text
                }
                if let text = await provider.loadTextIfAvailable(type: UTType.text.identifier), text.isEmpty == false {
                    return text
                }
            }
        }

        return nil
    }
}
