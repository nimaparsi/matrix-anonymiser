import SwiftUI

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
    @State private var compareTab: CompareTab = .original
    
    private var isResultMode: Bool {
        viewModel.hasOutput
    }

    private var canSubmit: Bool {
        viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false && !viewModel.isLoading
    }

    private var inputEditorHeight: CGFloat {
        let h = UIScreen.main.bounds.height * 0.52
        return min(max(h, 260), 540)
    }

    private var compareEditorHeight: CGFloat {
        let h = UIScreen.main.bounds.height * 0.48
        return min(max(h, 240), 500)
    }

    private var shouldShowFloatingBar: Bool {
        true
    }

    var body: some View {
        NavigationStack {
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(spacing: 16) {
                        if isResultMode {
                            compareCard
                                .id("output-card")
                        } else {
                            headlineCard
                            inputCard
                        }
                    }
                    .padding(16)
                    .padding(.bottom, shouldShowFloatingBar ? 108 : 24)
                }
                .onChange(of: viewModel.outputText) { newValue in
                    guard newValue.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false else { return }
                    compareTab = .result
                    withAnimation(.easeInOut(duration: 0.3)) {
                        proxy.scrollTo("output-card", anchor: .top)
                    }
                }
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if isResultMode {
                    ToolbarItem(placement: .topBarLeading) {
                        Button {
                            compareTab = .original
                            viewModel.outputText = ""
                            viewModel.errorMessage = nil
                            viewModel.usageLimitState = nil
                        } label: {
                            Label("Back", systemImage: "chevron.backward")
                        }
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
                        Image(systemName: "line.3.horizontal.circle")
                    }
                }
            }
            .task {
                viewModel.loadSharedInputIfNeeded()
            }
            .alert("Safe prompt copied", isPresented: $viewModel.showCopiedToast) {
                Button("OK", role: .cancel) {}
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
            .safeAreaInset(edge: .bottom) {
                if shouldShowFloatingBar {
                    floatingActionBar
                }
            }
        }
    }

    @ViewBuilder
    private func cardContainer<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        content()
            .padding(14)
            .background {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color(.secondarySystemBackground))
            }
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(BrandTheme.cardBorder, lineWidth: 1)
            }
    }

    private var inputCard: some View {
        cardContainer {
            VStack(alignment: .leading, spacing: 12) {
                Label("Input", systemImage: "square.and.pencil")
                    .font(.headline)

                ZStack(alignment: .topLeading) {
                    TextEditor(text: $viewModel.inputText)
                        .frame(height: inputEditorHeight)
                        .padding(12)
                        .scrollContentBackground(.hidden)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(Color(.systemBackground).opacity(0.65))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(Color(.separator).opacity(0.35), lineWidth: 0.8)
                        )

                    if viewModel.inputText.isEmpty {
                        Text("Paste text to anonymise")
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 18)
                            .padding(.vertical, 20)
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
                        .foregroundStyle(BrandTheme.prominentButtonText)
                    }
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(Color(.tertiarySystemBackground))
                    )
                }
            }
        }
    }

    private var headlineCard: some View {
        cardContainer {
            Text("Sanitise your text before AI sees it.")
                .font(.headline.weight(.bold))
                .foregroundStyle(
                    LinearGradient(
                        colors: [
                            BrandTheme.accent,
                            BrandTheme.accent.opacity(0.8),
                            .mint
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var compareCard: some View {
        cardContainer {
            VStack(alignment: .leading, spacing: 12) {
                Label("Compare", systemImage: "rectangle.split.2x1")
                    .font(.headline)

                Picker("View", selection: $compareTab) {
                    ForEach(CompareTab.allCases) { tab in
                        Text(tab.rawValue).tag(tab)
                    }
                }
                .pickerStyle(.segmented)

                ZStack(alignment: .topLeading) {
                    TextEditor(text: .constant(compareTab == .original ? viewModel.inputText : viewModel.outputText))
                        .frame(height: compareEditorHeight)
                        .padding(12)
                        .scrollContentBackground(.hidden)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(Color(.systemBackground).opacity(0.65))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(Color(.separator).opacity(0.35), lineWidth: 0.8)
                        )
                        .disabled(true)

                    if compareTab == .result && viewModel.outputText.isEmpty {
                        Text("Anonymised text appears here")
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 18)
                            .padding(.vertical, 20)
                    }
                }
            }
        }
    }

    private var floatingActionBar: some View {
        VStack(spacing: 10) {
            if !isResultMode {
                Button {
                    Task {
                        await viewModel.anonymize()
                    }
                } label: {
                    if viewModel.isLoading {
                        HStack(spacing: 10) {
                            ProgressView()
                            Text("Anonymising...")
                        }
                        .frame(maxWidth: .infinity)
                    } else {
                        Label("Anonymise", systemImage: "text.redaction")
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .foregroundStyle(BrandTheme.prominentButtonText)
                .disabled(!canSubmit)
            } else {
                HStack(spacing: 10) {
                    Button {
                        viewModel.copyOutput()
                    } label: {
                        Label("Copy", systemImage: "doc.on.doc")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    Button {
                        viewModel.clearAll()
                    } label: {
                        Label("Clear", systemImage: "trash")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }

                if settingsStore.settings.chatGPTIntegrationEnabled {
                    HStack(spacing: 10) {
                        Button {
                            showShareSheet = true
                        } label: {
                            Label("Share", systemImage: "square.and.arrow.up")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)

                        Button {
                            viewModel.openChatGPT()
                        } label: {
                            Label("Open ChatGPT", systemImage: "bubble.left.and.bubble.right")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                    }
                } else {
                    Button {
                        showShareSheet = true
                    } label: {
                        Label("Share", systemImage: "square.and.arrow.up")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }
            }
        }
        .padding(12)
        .background(.ultraThinMaterial)
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(BrandTheme.cardBorder, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .padding(.horizontal, 16)
        .padding(.bottom, 6)
    }
}
