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
    @Published var usageLimitState: UsageLimitState?

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

    func loadSharedText(from context: NSExtensionContext?) async {
        errorMessage = nil
        statusMessage = nil
        usageLimitState = nil

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
        usageLimitState = nil
        defer { isLoading = false }

        do {
            let entities = settingsStore.selectedEntityTypes()
            let tagStyle: AnonymizeTagStyle = settingsStore.settings.emojiTagsEnabled ? .emoji : .standard
            let reversePronouns = settingsStore.settings.reversePronounsEnabled
            let response = try await apiClient.anonymize(
                text: cleaned,
                entityTypes: entities,
                tagStyle: tagStyle,
                reversePronouns: reversePronouns
            )
            let output = settingsStore.settings.redactionModeEnabled
                ? applyRedactionMode(response.sanitizedText)
                : response.sanitizedText
            anonymizedText = output
            sharedStore.saveLastPayload(original: cleaned, anonymized: output)
            sharedStore.savePendingInput(cleaned)
        } catch {
            if case .usageLimitReached(let limitState) = (error as? AnonymizeClientError) {
                anonymizedText = ""
                usageLimitState = limitState
                errorMessage = nil
            } else {
                anonymizedText = ""
                errorMessage = error.localizedDescription
            }
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

        context?.open(url, completionHandler: nil)
        context?.completeRequest(returningItems: nil)
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
