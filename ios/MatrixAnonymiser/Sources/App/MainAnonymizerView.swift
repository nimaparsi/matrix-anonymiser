import SwiftUI
import AVFoundation
import UIKit

private enum CompareTab: String, CaseIterable, Identifiable {
    case original = "Original"
    case result = "Result"

    var id: String { rawValue }
}

struct MainAnonymizerView: View {
    @StateObject private var viewModel = AnonymizerViewModel()
    @EnvironmentObject private var settingsStore: AppSettingsStore
    @State private var showShareSheet = false
    @State private var showSettingsSheet = false
    @State private var showPrivacySheet = false
    @State private var compareTab: CompareTab = .result
    @State private var resultFontSize: CGFloat = 17
    @State private var isSpeakingResult = false
    @State private var showCopyToast = false

    private let speechSynthesizer = AVSpeechSynthesizer()

    private var canSubmit: Bool {
        viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false && !viewModel.isLoading
    }

    private var hasResult: Bool {
        viewModel.hasOutput
    }

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottom) {
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        headerSection
                        inputSection
                        primaryAction
                        resultSection

                        if hasResult {
                            actionsSection
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
                    .padding(.bottom, 28)
                }
                .background(Color(.systemGroupedBackground))

                if showCopyToast {
                    toastView("Copied to clipboard")
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                        .padding(.bottom, 14)
                }
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if hasResult {
                    ToolbarItem(placement: .topBarLeading) {
                        Button {
                            compareTab = .result
                            viewModel.outputText = ""
                            viewModel.errorMessage = nil
                            viewModel.usageLimitState = nil
                        } label: {
                            Image(systemName: "chevron.backward")
                                .padding(8)
                                .background(.ultraThinMaterial)
                                .clipShape(Circle())
                        }
                        .accessibilityLabel("Back to input")
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Button {
                            showSettingsSheet = true
                        } label: {
                            Label("Settings", systemImage: "slider.horizontal.3")
                        }

                        Button {
                            showPrivacySheet = true
                        } label: {
                            Label("Privacy", systemImage: "lock.shield")
                        }
                    } label: {
                        Image(systemName: "line.3.horizontal")
                            .padding(8)
                            .background(.ultraThinMaterial)
                            .clipShape(Circle())
                    }
                }
            }
            .task {
                viewModel.loadSharedInputIfNeeded()
            }
            .sheet(isPresented: $showShareSheet) {
                ShareSheetView(items: [viewModel.outputText])
            }
            .sheet(isPresented: $showSettingsSheet) {
                NavigationStack {
                    SettingsView()
                        .environmentObject(settingsStore)
                }
            }
            .sheet(isPresented: $showPrivacySheet) {
                NavigationStack {
                    PrivacyView()
                }
            }
        }
    }

    private var headerSection: some View {
        Text("Sanitise your text before AI sees it.")
            .font(.title3)
            .fontWeight(.semibold)
            .padding(.top, 8)
            .padding(.horizontal, 2)
    }

    private var inputSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Input", systemImage: "square.and.pencil")
                .font(.headline)

            Button {
                viewModel.inputText = UIPasteboard.general.string ?? ""
            } label: {
                Label("Paste from Clipboard", systemImage: "doc.on.clipboard")
            }
            .buttonStyle(.bordered)
            .controlSize(.large)

            ZStack(alignment: .topLeading) {
                    TextEditor(text: $viewModel.inputText)
                        .frame(minHeight: 220)
                        .padding(6)
                        .scrollContentBackground(.hidden)
                        .background(Color(.tertiarySystemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))

                if viewModel.inputText.isEmpty {
                    Text("Paste text to anonymise")
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 14)
                }
            }

            HStack(spacing: 4) {
                Text("You can customise anonymisation tags and app behavior in")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                Button("Settings") {
                    showSettingsSheet = true
                }
                .font(.footnote.weight(.semibold))
            }

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.red)
            }

            if let usageLimit = viewModel.usageLimitState {
                VStack(alignment: .leading, spacing: 8) {
                    Label("Daily free limit reached", systemImage: "lock.circle")
                        .font(.subheadline.weight(.semibold))
                    Text(usageLimit.message)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    if let usage = usageLimit.usageText {
                        Text(usage)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                    Button {
                        viewModel.openUpgradePage()
                    } label: {
                        Label("Go Pro", systemImage: "arrow.up.right.square")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                }
                .padding(12)
                .background(Color(.secondarySystemBackground))
                .cornerRadius(16)
            }
        }
        .padding(14)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }

    private var primaryAction: some View {
        Button {
            Task {
                await viewModel.anonymize()
                if viewModel.hasOutput {
                    compareTab = .result
                }
            }
        } label: {
            if viewModel.isLoading {
                HStack(spacing: 10) {
                    ProgressView()
                    Text("Sanitising...")
                }
                .frame(maxWidth: .infinity)
            } else {
                Text("Sanitise Text")
                    .frame(maxWidth: .infinity)
            }
        }
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .disabled(!canSubmit)
        .accessibilityHint("Runs anonymisation on your input text")
    }

    private var resultSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Result", systemImage: "doc.text.magnifyingglass")
                .font(.headline)

            Picker("View", selection: $compareTab) {
                ForEach(CompareTab.allCases) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)

            if compareTab == .result {
                resultAccessibilityTools
            }

            ScrollView {
                Text(resultDisplayText)
                    .font(.system(size: compareTab == .result ? resultFontSize : 16))
                    .lineSpacing(compareTab == .result ? 4 : 2)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 2)
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(16)
            .accessibilityLabel(compareTab == .result ? "Anonymised text" : "Original text")
        }
    }

    private var resultDisplayText: String {
        if compareTab == .original {
            return viewModel.inputText.isEmpty ? "Original text will appear here." : viewModel.inputText
        }
        return viewModel.outputText.isEmpty ? "Anonymised text appears here." : viewModel.outputText
    }

    private var actionsSection: some View {
        VStack(spacing: 10) {
            HStack(spacing: 10) {
                Button {
                    viewModel.copyOutput()
                    showCopyFeedback()
                } label: {
                    Label("Copy", systemImage: "doc.on.doc")
                        .frame(maxWidth: .infinity)
                }

                Button {
                    showShareSheet = true
                } label: {
                    Label("Share", systemImage: "square.and.arrow.up")
                        .frame(maxWidth: .infinity)
                }
            }
            .buttonStyle(.bordered)
            .controlSize(.large)

            HStack(spacing: 10) {
                Button {
                    viewModel.clearAll()
                    compareTab = .result
                } label: {
                    Label("Clear", systemImage: "trash")
                        .frame(maxWidth: .infinity)
                }

                Button {
                    viewModel.openChatGPT()
                } label: {
                    Label("Open ChatGPT", systemImage: "bubble.left.and.bubble.right")
                        .frame(maxWidth: .infinity)
                }
                .disabled(!settingsStore.settings.chatGPTIntegrationEnabled)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
        }
    }

    private var resultAccessibilityTools: some View {
        HStack(spacing: 10) {
            Button {
                resultFontSize = max(14, resultFontSize - 1)
            } label: {
                Label("Smaller", systemImage: "textformat.size.smaller")
            }
            .buttonStyle(.bordered)

            Button {
                resultFontSize = min(28, resultFontSize + 1)
            } label: {
                Label("Larger", systemImage: "textformat.size.larger")
            }
            .buttonStyle(.bordered)

            Button {
                toggleReadAloud()
            } label: {
                Label(isSpeakingResult ? "Stop" : "Read Aloud", systemImage: isSpeakingResult ? "stop.circle" : "speaker.wave.2")
            }
            .buttonStyle(.bordered)
        }
    }

    private func toggleReadAloud() {
        if speechSynthesizer.isSpeaking {
            speechSynthesizer.stopSpeaking(at: .immediate)
            isSpeakingResult = false
            return
        }
        let text = viewModel.outputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard text.isEmpty == false else { return }
        let utterance = AVSpeechUtterance(string: text)
        utterance.rate = 0.47
        speechSynthesizer.speak(utterance)
        isSpeakingResult = true
    }

    private func showCopyFeedback() {
        withAnimation(.easeInOut(duration: 0.2)) {
            showCopyToast = true
        }
        Task {
            try? await Task.sleep(nanoseconds: 1_500_000_000)
            await MainActor.run {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showCopyToast = false
                }
            }
        }
    }

    private func toastView(_ message: String) -> some View {
        Text(message)
            .font(.footnote.weight(.medium))
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(.ultraThinMaterial)
            .clipShape(Capsule())
            .shadow(radius: 8, y: 2)
    }
}
