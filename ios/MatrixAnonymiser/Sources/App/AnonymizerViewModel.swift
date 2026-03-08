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
    @Published var outputCounts: [String: Int] = [:]
    @Published var processingMs: Int?
    @Published var detectedLanguage: String?

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

    var totalDetectedEntities: Int {
        outputCounts.values.reduce(0, +)
    }

    var summaryLine: String {
        let total = totalDetectedEntities
        let entitiesText = "\(total) \(total == 1 ? "entity" : "entities") detected"
        let processingText = "Processing time: \(processingMs.map { "\($0)ms" } ?? "n/a")"
        let languageText = "Language: \(detectedLanguage ?? inferLanguageLabel(from: inputText))"
        return "\(entitiesText) · \(processingText) · \(languageText)"
    }

    func loadSharedInputIfNeeded() {
        outputText = ""
        outputCounts = [:]
        processingMs = nil
        detectedLanguage = nil
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
            let started = Date()
            let entities = settingsStore.selectedEntityTypes()
            let tagStyle: AnonymizeTagStyle = settingsStore.settings.emojiTagsEnabled ? .emoji : .standard
            let reversePronouns = settingsStore.settings.reversePronounsEnabled
            let response = try await apiClient.anonymize(
                text: inputText,
                entityTypes: entities,
                tagStyle: tagStyle,
                reversePronouns: reversePronouns
            )
            let sanitized = response.sanitizedText
            let finalOutput = settingsStore.settings.redactionModeEnabled
                ? applyRedactionMode(sanitized)
                : sanitized
            outputText = finalOutput
            outputCounts = response.counts ?? [:]
            processingMs = response.meta?.processing_ms ?? Int(Date().timeIntervalSince(started) * 1000)
            detectedLanguage = normalizedLanguage(response.meta?.language) ?? inferLanguageLabel(from: inputText)
            sharedStore.saveLastPayload(original: inputText, anonymized: finalOutput)
            usageLimitState = nil
        } catch {
            if case .usageLimitReached(let limitState) = (error as? AnonymizeClientError) {
                outputText = ""
                outputCounts = [:]
                processingMs = nil
                detectedLanguage = nil
                usageLimitState = limitState
                errorMessage = nil
            } else {
                outputText = ""
                outputCounts = [:]
                processingMs = nil
                detectedLanguage = nil
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
        outputCounts = [:]
        processingMs = nil
        detectedLanguage = nil
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

    func inferLanguageLabel(from input: String) -> String {
        let lower = input.lowercased()
        guard let regex = try? NSRegularExpression(pattern: "[a-z]{2,}", options: []) else {
            return "Unknown (English recommended)"
        }
        let range = NSRange(lower.startIndex..<lower.endIndex, in: lower)
        let words = regex.matches(in: lower, options: [], range: range)
            .compactMap { Range($0.range, in: lower).map { String(lower[$0]) } }
        guard words.count >= 5 else {
            return "Unknown (English recommended)"
        }

        let hints: Set<String> = [
            "the", "and", "with", "for", "from", "that", "this", "is", "are", "was", "were",
            "have", "has", "will", "would", "you", "your", "their", "there", "about", "before",
            "after", "meeting", "email", "phone", "address", "project", "report", "document"
        ]

        let hitCount = words.reduce(into: 0) { total, word in
            if hints.contains(word) { total += 1 }
        }
        let ratio = Double(hitCount) / Double(words.count)
        return ratio >= 0.08 ? "English" : "Unknown (English recommended)"
    }

    private func normalizedLanguage(_ language: String?) -> String? {
        guard let language else { return nil }
        let cleaned = language.trimmingCharacters(in: .whitespacesAndNewlines)
        guard cleaned.isEmpty == false else { return nil }
        if cleaned.lowercased() == "unknown" {
            return "Unknown (English recommended)"
        }
        return cleaned
    }
}
