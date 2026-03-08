import SwiftUI
import UIKit

private enum CompareTab: String, CaseIterable, Identifiable {
    case original = "Original"
    case result = "Result"

    var id: String { rawValue }
}

private enum ViewState {
    case empty
    case ready
    case processing
    case result
}

struct MainAnonymizerView: View {
    @StateObject private var viewModel = AnonymizerViewModel()
    @EnvironmentObject private var settingsStore: AppSettingsStore
    @Environment(\.colorScheme) private var colorScheme

    @State private var showShareSheet = false
    @State private var showSettingsSheet = false
    @State private var showAboutSheet = false
    @State private var showAdvancedDetectionSheet = false
    @State private var compareTab: CompareTab = .result
    @State private var resultFontSize: CGFloat = 17
    @State private var copyJustCompleted = false
    @State private var pasteJustCompleted = false
    @State private var showCopyToast = false
    @State private var resultHighlight = false
    @State private var resultOpacity = 1.0
    @State private var inputHeight: CGFloat = 220
    @State private var isReturningToInput = false
    @State private var smallerControlPressed = false
    @State private var largerControlPressed = false
    @State private var isAccentGradientShifted = false

    private let primaryGreen = Color(red: 0.0, green: 227.0 / 255.0, blue: 140.0 / 255.0)
    private let secondaryCyan = Color(red: 46.0 / 255.0, green: 200.0 / 255.0, blue: 1.0)

    private var viewState: ViewState {
        if viewModel.hasOutput { return .result }
        if viewModel.isLoading { return .processing }
        if viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { return .empty }
        return .ready
    }

    private var scrollBottomPadding: CGFloat { 96 }

    private var canUseResultActions: Bool {
        viewModel.outputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false
    }

    private var charCountLabel: String {
        "\(viewModel.inputText.count.formatted()) / 50,000"
    }

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottom) {
                ScrollViewReader { scrollProxy in
                    ScrollView {
                        VStack(alignment: .leading, spacing: 14) {
                            headerSection

                            if viewState == .result {
                                Color.clear
                                    .frame(height: 0)
                                    .id("resultTop")

                                VStack(alignment: .leading, spacing: 10) {
                                    backButton
                                    resultSection
                                }
                                .transition(resultTransition)
                            } else {
                                inputSection
                                    .transition(inputTransition)
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.top, 8)
                        .padding(.bottom, scrollBottomPadding)
                    }
                    .animation(stateTransitionAnimation, value: viewState)
                    .onChange(of: viewModel.outputText) { newValue in
                        guard newValue.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false else { return }
                        isReturningToInput = false
                        compareTab = .result
                        withAnimation(.easeInOut(duration: 0.28)) {
                            scrollProxy.scrollTo("resultTop", anchor: .top)
                        }
                        animateResultReveal()
                        highlightResultBriefly()
                    }
                    .background(Color(.systemGroupedBackground))
                    .safeAreaInset(edge: .bottom) {
                        Group {
                            if viewState == .result {
                                resultActionBar
                                    .transition(.offset(y: 40).combined(with: .opacity))
                            } else {
                                primaryToolbar(scrollProxy: scrollProxy)
                                    .transition(.offset(y: 40).combined(with: .opacity))
                            }
                        }
                        .animation(.easeInOut(duration: 0.30).delay(viewState == .result ? 0.08 : 0), value: viewState)
                    }
                }

                if showCopyToast {
                    Text("Copied ✓")
                        .font(.subheadline.weight(.semibold))
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                        .background(Color(.systemBackground))
                        .clipShape(Capsule())
                        .shadow(color: .black.opacity(0.18), radius: 10, x: 0, y: 4)
                        .padding(.bottom, 96)
                        .transition(.offset(y: -10).combined(with: .opacity))
                }
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar(.hidden, for: .navigationBar)
            .task {
                viewModel.loadSharedInputIfNeeded()
            }
            .onAppear {
                guard isAccentGradientShifted == false else { return }
                withAnimation(.linear(duration: 18.0).repeatForever(autoreverses: true)) {
                    isAccentGradientShifted = true
                }
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
            .sheet(isPresented: $showAdvancedDetectionSheet) {
                NavigationStack {
                    AdvancedDetectionSheetView()
                        .environmentObject(settingsStore)
                }
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
            }
            .sheet(isPresented: $showAboutSheet) {
                NavigationStack {
                    AboutPrivacySheetView()
                }
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
            }
        }
    }

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 7) {
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
                        showAboutSheet = true
                    } label: {
                        Label("About & Privacy", systemImage: "lock.shield")
                    }
                } label: {
                    Image(systemName: "line.3.horizontal")
                        .padding(8)
                        .background(.ultraThinMaterial)
                        .clipShape(Circle())
                }
            }

            Text("Sanitise sensitive text before AI sees it.")
                .font(.title3)
                .fontWeight(.semibold)
                .foregroundStyle(animatedAccentGradient)

            Text("Your text is processed in memory and never stored.")
                .font(.caption.monospaced())
                .foregroundStyle(.secondary.opacity(0.8))
        }
        .padding(.horizontal, 2)
    }

    private var backButton: some View {
        Button {
            backToInput()
        } label: {
            HStack(spacing: 4) {
                Image(systemName: "chevron.left")
                Text("Back")
            }
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(.secondary)
        }
        .buttonStyle(.plain)
    }

    private var inputSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Your text", systemImage: "square.and.pencil")
                .font(.headline)

            HStack(spacing: 10) {
                Button {
                    viewModel.inputText = UIPasteboard.general.string ?? ""
                    showPasteFeedback()
                } label: {
                    Label(pasteJustCompleted ? "✓ Pasted" : "Paste from Clipboard", systemImage: pasteJustCompleted ? "checkmark.circle.fill" : "doc.on.clipboard")
                        .lineLimit(1)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)

                if viewModel.inputText.isEmpty == false {
                    Button {
                        triggerLightHaptic()
                        viewModel.inputText = ""
                    } label: {
                        Image(systemName: "trash")
                            .frame(width: 20, height: 20)
                    }
                    .buttonStyle(.bordered)
                    .tint(.red)
                    .controlSize(.large)
                }
            }

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

            Text(charCountLabel)
                .font(.caption)
                .foregroundStyle(.secondary)

            Button {
                settingsStore.setProtectAllSensitiveDataEnabled(!settingsStore.settings.protectAllSensitiveDataEnabled)
            } label: {
                HStack {
                    Text("Protect all sensitive data")
                    Spacer()
                    Text(settingsStore.settings.protectAllSensitiveDataEnabled ? "✓" : "")
                        .fontWeight(.semibold)
                }
                .font(.subheadline)
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .background(Color(.tertiarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
            .buttonStyle(.plain)

            Button {
                showAdvancedDetectionSheet = true
            } label: {
                HStack {
                    Text("Advanced detection settings")
                    Spacer()
                    Text("▸")
                        .foregroundStyle(.secondary)
                }
                .font(.footnote)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .background(Color(.tertiarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 8) {
                Text("Text transformations")
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(.secondary)

                Toggle("Emoji entity tags", isOn: Binding(
                    get: { settingsStore.settings.emojiTagsEnabled },
                    set: { settingsStore.setEmojiTagsEnabled($0) }
                ))
                .toggleStyle(.switch)

                Toggle("Reverse pronouns", isOn: Binding(
                    get: { settingsStore.settings.reversePronounsEnabled },
                    set: { settingsStore.setReversePronounsEnabled($0) }
                ))
                .toggleStyle(.switch)

                Toggle("Replace entities with [REDACTED]", isOn: Binding(
                    get: { settingsStore.settings.redactionModeEnabled },
                    set: { settingsStore.setRedactionModeEnabled($0) }
                ))
                .toggleStyle(.switch)
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
                    .tint(primaryGreen)
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
            HStack(alignment: .center, spacing: 10) {
                Label("Result", systemImage: "doc.text.magnifyingglass")
                    .font(.headline)
                Spacer()
                resultControls
            }

            Text("✓ \(viewModel.totalDetectedEntities) \(viewModel.totalDetectedEntities == 1 ? "entity" : "entities") anonymised")
                .font(.caption.weight(.semibold))
                .foregroundStyle(primaryGreen)

            Text(viewModel.summaryLine)
                .font(.caption)
                .foregroundStyle(.secondary)

            Picker("View", selection: $compareTab) {
                ForEach(CompareTab.allCases) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)
            .padding(4)
            .background(colorScheme == .dark ? Color.white.opacity(0.14) : Color.black.opacity(0.06))
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))

            ZStack {
                if compareTab == .original {
                    resultTextBlock(
                        text: viewModel.inputText,
                        fontSize: resultFontSize,
                        accessibilityLabel: "Original text",
                        highlightChanges: false
                    )
                        .transition(.opacity)
                } else {
                    resultTextBlock(
                        text: viewModel.outputText,
                        fontSize: resultFontSize,
                        accessibilityLabel: "Anonymised text",
                        highlightChanges: settingsStore.settings.highlightChangedTextEnabled
                    )
                        .transition(.opacity)
                }
            }
            .animation(.easeInOut(duration: 0.2), value: compareTab)
        }
        .padding(16)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
        .id("resultSection")
    }

    private var resultControls: some View {
        HStack(spacing: 8) {
            Button {
                triggerLightHaptic()
                animateControlPress(isPressed: $smallerControlPressed)
                resultFontSize = max(14, resultFontSize - 1)
            } label: {
                Text("A−")
                    .font(.caption.weight(.semibold))
                    .frame(width: 28, height: 28)
            }
            .buttonStyle(.bordered)
            .scaleEffect(smallerControlPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.16), value: smallerControlPressed)
            .accessibilityLabel("Smaller")

            Button {
                triggerLightHaptic()
                animateControlPress(isPressed: $largerControlPressed)
                resultFontSize = min(28, resultFontSize + 1)
            } label: {
                Text("A+")
                    .font(.caption.weight(.semibold))
                    .frame(width: 28, height: 28)
            }
            .buttonStyle(.bordered)
            .scaleEffect(largerControlPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.16), value: largerControlPressed)
            .accessibilityLabel("Larger")

        }
        .font(.caption)
        .minimumScaleFactor(0.85)
    }

    private var resultActionBar: some View {
        HStack(spacing: 12) {
            Button {
                triggerLightHaptic()
                viewModel.copyOutput()
                showCopyFeedback()
            } label: {
                Label(copyJustCompleted ? "Copied ✓" : "Copy", systemImage: copyJustCompleted ? "checkmark.circle.fill" : "doc.on.doc")
                    .lineLimit(1)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(primaryGreen)
            .foregroundStyle(.black)
            .disabled(!canUseResultActions)

            Button {
                showShareSheet = true
            } label: {
                Label("Share", systemImage: "square.and.arrow.up")
                    .lineLimit(1)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .tint(secondaryCyan)
            .disabled(!canUseResultActions)

            Button(role: .destructive) {
                viewModel.clearAll()
                compareTab = .result
            } label: {
                Image(systemName: "trash")
                    .frame(width: 24, height: 24)
            }
            .buttonStyle(.bordered)
            .tint(.red)
            .disabled(!canUseResultActions)
        }
        .controlSize(.regular)
        .frame(height: 64)
        .padding(.horizontal, 16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .shadow(color: .black.opacity(0.12), radius: 10, x: 0, y: 4)
        .padding(.horizontal, 20)
        .padding(.top, 4)
        .padding(.bottom, 12)
        .offset(y: viewState == .result ? 0 : 40)
        .opacity(viewState == .result ? 1 : 0)
    }

    @ViewBuilder
    private func primaryToolbar(scrollProxy: ScrollViewProxy) -> some View {
        Button {
            triggerLightHaptic()
            guard viewState == .ready else { return }
            Task {
                await viewModel.anonymize()
                withAnimation(.easeInOut(duration: 0.28)) {
                    scrollProxy.scrollTo("resultTop", anchor: .top)
                }
            }
        } label: {
            HStack(spacing: 10) {
                if viewState == .processing {
                    ProgressView()
                        .tint(.black)
                }
                Text(viewState == .processing ? "Sanitising..." : "Sanitise Text")
                    .font(.headline)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .foregroundStyle(.black)
            .background(primaryGreen)
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .shadow(color: .black.opacity(0.12), radius: 10, x: 0, y: 4)
        }
        .buttonStyle(ScalePressStyle(scale: 0.96))
        .padding(.horizontal, 20)
        .padding(.top, 4)
        .padding(.bottom, 24)
        .opacity(viewState == .empty ? 0.45 : 1.0)
        .allowsHitTesting(viewState == .ready)
        .offset(y: viewState == .result ? 40 : 0)
        .opacity(viewState == .result ? 0 : 1)
    }

    private func backToInput() {
        isReturningToInput = true
        viewModel.outputText = ""
        viewModel.errorMessage = nil
        viewModel.usageLimitState = nil
        compareTab = .result
        copyJustCompleted = false
        resultHighlight = false
        resultOpacity = 1.0
    }

    private func showCopyFeedback() {
        withAnimation(.easeInOut(duration: 0.15)) {
            copyJustCompleted = true
            showCopyToast = true
        }
        Task {
            try? await Task.sleep(nanoseconds: 1_400_000_000)
            await MainActor.run {
                withAnimation(.easeInOut(duration: 0.15)) {
                    copyJustCompleted = false
                    showCopyToast = false
                }
            }
        }
    }

    private func showPasteFeedback() {
        withAnimation(.easeInOut(duration: 0.15)) {
            pasteJustCompleted = true
        }
        Task {
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            await MainActor.run {
                withAnimation(.easeInOut(duration: 0.15)) {
                    pasteJustCompleted = false
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
        resultOpacity = 0.0
        withAnimation(.easeInOut(duration: 0.30)) {
            resultOpacity = 1.0
        }
    }

    private func triggerLightHaptic() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.prepare()
        generator.impactOccurred()
    }

    private func animateControlPress(isPressed: Binding<Bool>) {
        isPressed.wrappedValue = true
        Task {
            try? await Task.sleep(nanoseconds: 120_000_000)
            await MainActor.run {
                isPressed.wrappedValue = false
            }
        }
    }

    private func resultTextBlock(
        text: String,
        fontSize: CGFloat,
        accessibilityLabel: String,
        highlightChanges: Bool
    ) -> some View {
        Text(styledResultText(text: text, highlightChanges: highlightChanges))
            .font(.system(size: fontSize))
            .lineSpacing(4)
            .textSelection(.enabled)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(16)
            .background(Color(.secondarySystemBackground))
            .cornerRadius(16)
            .opacity(resultOpacity)
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(resultHighlight ? Color.accentColor.opacity(0.8) : Color.clear, lineWidth: 2)
            )
            .accessibilityLabel(accessibilityLabel)
    }

    private func styledResultText(text: String, highlightChanges: Bool) -> AttributedString {
        var attributed = AttributedString(text)
        guard highlightChanges else { return attributed }

        let pattern = #"\[[^\]\n]+\]"#
        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
            return attributed
        }

        let nsRange = NSRange(text.startIndex..<text.endIndex, in: text)
        let matches = regex.matches(in: text, options: [], range: nsRange)
        for match in matches {
            guard let stringRange = Range(match.range, in: text),
                  let lower = AttributedString.Index(stringRange.lowerBound, within: attributed),
                  let upper = AttributedString.Index(stringRange.upperBound, within: attributed) else {
                continue
            }

            attributed[lower..<upper].backgroundColor = Color.accentColor.opacity(0.22)
            attributed[lower..<upper].foregroundColor = .primary
        }

        return attributed
    }

    private var animatedAccentGradient: LinearGradient {
        LinearGradient(
            colors: [primaryGreen, secondaryCyan, primaryGreen],
            startPoint: isAccentGradientShifted ? .topLeading : .leading,
            endPoint: isAccentGradientShifted ? .bottomTrailing : .trailing
        )
    }

    private var inputTransition: AnyTransition {
        if isReturningToInput {
            return .asymmetric(
                insertion: .offset(x: -40).combined(with: .opacity),
                removal: .opacity
            )
        }
        return .asymmetric(
            insertion: .opacity,
            removal: .opacity
        )
    }

    private var resultTransition: AnyTransition {
        if isReturningToInput {
            return .asymmetric(
                insertion: .opacity,
                removal: .offset(x: 40).combined(with: .opacity)
            )
        }
        return .asymmetric(
            insertion: .scale(scale: 0.96).combined(with: .offset(y: 20)).combined(with: .opacity),
            removal: .opacity
        )
    }

    private var stateTransitionAnimation: Animation {
        if viewState == .result, !isReturningToInput {
            return .easeOut(duration: 0.30).delay(0.05)
        }
        return .easeInOut(duration: 0.28)
    }
}

private struct ScalePressStyle: ButtonStyle {
    let scale: CGFloat

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? scale : 1)
            .animation(.easeInOut(duration: 0.16), value: configuration.isPressed)
    }
}

private struct AboutPrivacySheetView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                card(title: "Matrix Anonymiser") {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Matrix Anonymiser removes personal information from text before it is shared with AI tools or other services.")
                        Text("Sanitise your text before AI sees it.")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.secondary)
                    }
                }

                card(title: "Privacy") {
                    VStack(alignment: .leading, spacing: 8) {
                        bullet("Your text is processed only when you choose to sanitise it.")
                        bullet("The app does not permanently store your input.")
                        bullet("Text is anonymised before being shared with external apps.")
                        bullet("No account is required to use the app.")
                        bullet("Text may be sent to a processing service to detect entities, but input is not stored after processing.")
                    }
                }

                card(title: "Share Extension / Web Content") {
                    Text("Matrix Anonymiser can process text shared from other apps, including web pages, documents, and messaging apps through the Share Extension.")
                }

                card(title: "Built by") {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Nima Parsi")
                            .font(.body.weight(.semibold))
                        Text("Senior Frontend Engineer")
                            .foregroundStyle(.secondary)
                        Link("nimaparsi.uk", destination: URL(string: "https://nimaparsi.uk")!)
                            .font(.subheadline)
                    }
                }

                Text("Version 1.0")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.top, 4)
            }
            .padding(16)
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("About")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func card<Content: View>(title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
            Divider()
                .opacity(0.35)
            content()
                .font(.body)
                .foregroundStyle(.primary)
        }
        .padding(16)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func bullet(_ text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Text("•")
            Text(text)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct AdvancedDetectionCategory: Identifiable {
    let id: String
    let title: String
    let entities: [AnonymizeEntityType]
}

private struct AdvancedDetectionSheetView: View {
    @EnvironmentObject private var settingsStore: AppSettingsStore

    private let categories: [AdvancedDetectionCategory] = [
        AdvancedDetectionCategory(id: "identity", title: "Identity", entities: [.person, .organisation, .username]),
        AdvancedDetectionCategory(id: "contact", title: "Contact", entities: [.email, .phone, .address]),
        AdvancedDetectionCategory(id: "security", title: "Security", entities: [.apiKey, .privateKey, .ipAddress]),
        AdvancedDetectionCategory(id: "financial", title: "Financial", entities: [.creditCard, .bankAccount, .governmentID]),
        AdvancedDetectionCategory(id: "technical", title: "Technical", entities: [.webAddress, .filePath, .coordinate]),
        AdvancedDetectionCategory(id: "metadata", title: "Metadata", entities: [.date]),
    ]

    var body: some View {
        List {
            Section {
                Toggle("Protect all sensitive data", isOn: Binding(
                    get: { settingsStore.settings.protectAllSensitiveDataEnabled },
                    set: { settingsStore.setProtectAllSensitiveDataEnabled($0) }
                ))
                .toggleStyle(.switch)
            }

            ForEach(categories) { category in
                Section(category.title) {
                    ForEach(category.entities) { entity in
                        Toggle(entity.title, isOn: Binding(
                            get: {
                                settingsStore.settings.protectAllSensitiveDataEnabled || settingsStore.isEntityEnabled(entity)
                            },
                            set: { isEnabled in
                                if settingsStore.settings.protectAllSensitiveDataEnabled {
                                    settingsStore.setProtectAllSensitiveDataEnabled(false)
                                }
                                settingsStore.setEntity(entity, enabled: isEnabled)
                            }
                        ))
                        .disabled(settingsStore.settings.protectAllSensitiveDataEnabled)
                    }
                }
            }
        }
        .navigationTitle("Advanced Detection")
        .navigationBarTitleDisplayMode(.inline)
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
        textView.textContainerInset = UIEdgeInsets(top: 16, left: 16, bottom: 16, right: 16)
        textView.textContainer.lineFragmentPadding = 0
        textView.font = .preferredFont(forTextStyle: .body)
        textView.adjustsFontForContentSizeCategory = true
        textView.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        context.coordinator.applyTextStyle(textView)
        return textView
    }

    func updateUIView(_ uiView: UITextView, context: Context) {
        if uiView.text != text {
            uiView.text = text
        }
        context.coordinator.applyTextStyle(uiView)
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

        func applyTextStyle(_ textView: UITextView) {
            let selected = textView.selectedRange
            let font = UIFont.preferredFont(forTextStyle: .body)
            let paragraph = NSMutableParagraphStyle()
            paragraph.lineSpacing = 4

            let attributes: [NSAttributedString.Key: Any] = [
                .font: font,
                .paragraphStyle: paragraph,
                .foregroundColor: UIColor.label
            ]
            let fullRange = NSRange(location: 0, length: textView.textStorage.length)
            textView.textStorage.setAttributes(attributes, range: fullRange)
            textView.typingAttributes = attributes
            textView.selectedRange = selected
        }

        func textViewDidChange(_ textView: UITextView) {
            parent.text = textView.text
            applyTextStyle(textView)
            parent.recalculateHeight(view: textView)
        }
    }
}
