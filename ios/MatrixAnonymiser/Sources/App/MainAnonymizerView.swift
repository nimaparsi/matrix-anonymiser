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
    @State private var copyJustCompleted = false
    @State private var resultHighlight = false
    @State private var resultOpacity = 1.0
    @State private var inputHeight: CGFloat = 220

    private let speechSynthesizer = AVSpeechSynthesizer()

    private var canSubmit: Bool {
        viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false && !viewModel.isLoading
    }

    private var hasResult: Bool {
        viewModel.hasOutput
    }

    var body: some View {
        NavigationStack {
            ScrollViewReader { scrollProxy in
                ZStack(alignment: .bottom) {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 14) {
                            headerSection
                            inputSection
                            resultSection
                        }
                        .padding(.horizontal, 16)
                        .padding(.top, 8)
                        .padding(.bottom, 4)
                    }
                    .onChange(of: viewModel.outputText) { newValue in
                        guard newValue.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false else { return }
                        compareTab = .result
                        withAnimation(.easeInOut(duration: 0.25)) {
                            scrollProxy.scrollTo("resultSection", anchor: .top)
                        }
                        animateResultReveal()
                        highlightResultBriefly()
                    }
                    .background(Color(.systemGroupedBackground))
                }
                .safeAreaInset(edge: .bottom) {
                    bottomActionBar(scrollProxy: scrollProxy)
                }
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar(.hidden, for: .navigationBar)
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
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .center, spacing: 10) {
                Label("Matrix Anonymiser", systemImage: "shield.lefthalf.filled")
                    .font(.headline)
                    .foregroundStyle(.secondary)

                Spacer(minLength: 8)

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

            Text("Sanitise your text before AI sees it.")
                .font(.title3)
                .fontWeight(.semibold)
                .shadow(color: .green.opacity(0.25), radius: 10)
        }
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
                GrowingTextEditor(text: $viewModel.inputText, height: $inputHeight)
                    .frame(height: max(220, inputHeight))
                    .padding(8)
                    .background(Color(.tertiarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))

                if viewModel.inputText.isEmpty {
                    Text("Paste or type text to sanitise")
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 18)
                        .padding(.vertical, 18)
                }
            }

            Text("\(viewModel.inputText.count.formatted()) characters")
                .font(.caption)
                .foregroundStyle(.secondary)

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
                    .tint(.mint)
                    .foregroundStyle(.black)
                    .controlSize(.large)
                }
                .padding(12)
                .background(Color(.secondarySystemBackground))
                .cornerRadius(16)
            }
        }
        .padding(16)
        .background(Color(.systemGroupedBackground))
        .cornerRadius(16)
    }

    private var resultSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Result", systemImage: "doc.text.magnifyingglass")
                .font(.headline)

            if hasResult, detectedEntitySummary.isEmpty == false {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Detected:")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(detectedEntitySummary.joined(separator: "  ·  "))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Picker("View", selection: $compareTab) {
                ForEach(CompareTab.allCases) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)
            .padding(.top, 6)

            Text(resultDisplayText)
                .font(.system(size: compareTab == .result ? resultFontSize : 16))
                .lineSpacing(compareTab == .result ? 4 : 2)
                .textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(14)
                .background(Color(.secondarySystemBackground))
                .cornerRadius(16)
                .opacity(resultOpacity)
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(resultHighlight ? Color.accentColor.opacity(0.8) : Color.clear, lineWidth: 2)
                )
                .accessibilityLabel(compareTab == .result ? "Anonymised text" : "Original text")

            if compareTab == .result {
                resultAccessibilityTools
            }
        }
        .padding(16)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
        .id("resultSection")
    }

    private var resultDisplayText: String {
        if compareTab == .original {
            return viewModel.inputText.isEmpty ? "Original text will appear here." : viewModel.inputText
        }
        return viewModel.outputText.isEmpty ? "Anonymised text appears here." : viewModel.outputText
    }

    @ViewBuilder
    private func bottomActionBar(scrollProxy: ScrollViewProxy) -> some View {
        VStack(spacing: 8) {
            if hasResult {
                HStack {
                    Spacer()
                    Button("Clear") {
                        viewModel.clearAll()
                        compareTab = .result
                    }
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .buttonStyle(.plain)
                }

                HStack(spacing: 10) {
                    Button {
                        triggerLightHaptic()
                        viewModel.copyOutput()
                        showCopyFeedback()
                    } label: {
                        Label(copyJustCompleted ? "Copied ✓" : "Copy", systemImage: copyJustCompleted ? "checkmark.circle.fill" : "doc.on.doc")
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    Button {
                        showShareSheet = true
                    } label: {
                        Label("Share", systemImage: "square.and.arrow.up")
                            .lineLimit(1)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    Button {
                        viewModel.openChatGPT()
                    } label: {
                        Label("Open in ChatGPT", systemImage: "bubble.left.and.bubble.right.fill")
                            .lineLimit(1)
                            .minimumScaleFactor(0.7)
                            .font(.footnote.weight(.semibold))
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .disabled(viewModel.outputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            } else {
                Button {
                    triggerLightHaptic()
                    Task {
                        await viewModel.anonymize()
                        withAnimation(.easeInOut(duration: 0.25)) {
                            scrollProxy.scrollTo("resultSection", anchor: .top)
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
                .tint(.mint)
                .foregroundStyle(.black)
                .disabled(!canSubmit)
                .accessibilityHint("Runs anonymisation on your input text")
            }
        }
        .controlSize(.large)
        .padding(.horizontal, 16)
        .padding(.top, 6)
        .padding(.bottom, 1)
        .background(.ultraThinMaterial)
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
        withAnimation(.easeInOut(duration: 0.15)) {
            copyJustCompleted = true
        }
        Task {
            try? await Task.sleep(nanoseconds: 1_500_000_000)
            await MainActor.run {
                withAnimation(.easeInOut(duration: 0.15)) {
                    copyJustCompleted = false
                }
            }
        }
    }

    private func highlightResultBriefly() {
        withAnimation(.easeInOut(duration: 0.18)) {
            resultHighlight = true
        }
        Task {
            try? await Task.sleep(nanoseconds: 900_000_000)
            await MainActor.run {
                withAnimation(.easeInOut(duration: 0.2)) {
                    resultHighlight = false
                }
            }
        }
    }

    private func animateResultReveal() {
        resultOpacity = 0.25
        withAnimation(.easeOut(duration: 0.25)) {
            resultOpacity = 1.0
        }
    }

    private func triggerLightHaptic() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.prepare()
        generator.impactOccurred()
    }

    private var detectedEntitySummary: [String] {
        let text = viewModel.outputText
        guard text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false else { return [] }

        let peopleCount = countMatches(pattern: #"(?:\[\s*)?(?:👤\s*)?Person\s+\d+(?:\s*\])?"#, in: text)
        let emailCount = countMatches(pattern: #"(?:\[\s*)?(?:📧\s*)?Email\s+\d+(?:\s*\])?"#, in: text)
        let phoneCount = countMatches(pattern: #"(?:\[\s*)?(?:📞\s*)?Phone\s+\d+(?:\s*\])?"#, in: text)
        let locationCount = countMatches(pattern: #"(?:\[\s*)?(?:📍\s*)?(?:Location|Address)\s+\d+(?:\s*\])?"#, in: text)
        let organisationCount = countMatches(pattern: #"(?:\[\s*)?(?:🏢\s*)?(?:Organisation|Organization|Org)\s+\d+(?:\s*\])?"#, in: text)
        let dateCount = countMatches(pattern: #"(?:\[\s*)?(?:📅\s*)?Date\s+\d+(?:\s*\])?"#, in: text)

        var summary: [String] = []
        if peopleCount > 0 { summary.append("\(peopleCount) \(peopleCount == 1 ? "Person" : "People")") }
        if emailCount > 0 { summary.append("\(emailCount) \(emailCount == 1 ? "Email" : "Emails")") }
        if phoneCount > 0 { summary.append("\(phoneCount) \(phoneCount == 1 ? "Phone" : "Phones")") }
        if locationCount > 0 { summary.append("\(locationCount) \(locationCount == 1 ? "Location" : "Locations")") }
        if organisationCount > 0 { summary.append("\(organisationCount) \(organisationCount == 1 ? "Organisation" : "Organisations")") }
        if dateCount > 0 { summary.append("\(dateCount) \(dateCount == 1 ? "Date" : "Dates")") }
        return summary
    }

    private func countMatches(pattern: String, in text: String) -> Int {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]) else {
            return 0
        }
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        return regex.numberOfMatches(in: text, options: [], range: range)
    }
}

private struct GrowingTextEditor: UIViewRepresentable {
    @Binding var text: String
    @Binding var height: CGFloat

    func makeUIView(context: Context) -> UITextView {
        let textView = UITextView()
        textView.delegate = context.coordinator
        textView.isScrollEnabled = false
        textView.backgroundColor = .clear
        textView.textContainerInset = UIEdgeInsets(top: 8, left: 6, bottom: 8, right: 6)
        textView.font = .preferredFont(forTextStyle: .body)
        textView.adjustsFontForContentSizeCategory = true
        textView.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        return textView
    }

    func updateUIView(_ uiView: UITextView, context: Context) {
        if uiView.text != text {
            uiView.text = text
        }
        recalculateHeight(view: uiView)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    private func recalculateHeight(view: UITextView) {
        let width = max(view.bounds.width, UIScreen.main.bounds.width - 64)
        let fitting = view.sizeThatFits(CGSize(width: width, height: .greatestFiniteMagnitude))
        let targetHeight = max(44, fitting.height)

        guard abs(height - targetHeight) > 0.5 else { return }
        let heightBinding = _height
        DispatchQueue.main.async {
            heightBinding.wrappedValue = targetHeight
        }
    }

    final class Coordinator: NSObject, UITextViewDelegate {
        private var parent: GrowingTextEditor

        init(_ parent: GrowingTextEditor) {
            self.parent = parent
        }

        func textViewDidChange(_ textView: UITextView) {
            parent.text = textView.text
            parent.recalculateHeight(view: textView)
        }
    }
}
