import SwiftUI

struct MainAnonymizerView: View {
    @StateObject private var viewModel = AnonymizerViewModel()
    @EnvironmentObject private var settingsStore: AppSettingsStore
    @State private var showShareSheet = false
    @State private var showSettingsSheet = false
    @State private var showPrivacySheet = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    inputCard
                    outputCard
                    actionCard
                }
                .padding(16)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Matrix Anonymiser")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
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
                        .frame(minHeight: 170)
                        .padding(8)
                        .background(Color(.tertiarySystemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))

                    if viewModel.inputText.isEmpty {
                        Text("Paste text to anonymise")
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 18)
                    }
                }

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
                .disabled(viewModel.isLoading)

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

    private var outputCard: some View {
        cardContainer {
            VStack(alignment: .leading, spacing: 12) {
                Label("Output", systemImage: "doc.text.magnifyingglass")
                    .font(.headline)

                ZStack(alignment: .topLeading) {
                    TextEditor(text: .constant(viewModel.outputText))
                        .frame(minHeight: 170)
                        .padding(8)
                        .background(Color(.tertiarySystemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        .disabled(true)

                    if viewModel.outputText.isEmpty {
                        Text("Anonymised text appears here")
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 18)
                    }
                }
            }
        }
    }

    private var actionCard: some View {
        cardContainer {
            VStack(spacing: 10) {
                HStack(spacing: 10) {
                    Button {
                        viewModel.copyOutput()
                    } label: {
                        Label("Copy", systemImage: "doc.on.doc")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .disabled(viewModel.hasOutput == false)

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
                        .disabled(viewModel.hasOutput == false)

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
                    .disabled(viewModel.hasOutput == false)
                }
            }
        }
    }
}
