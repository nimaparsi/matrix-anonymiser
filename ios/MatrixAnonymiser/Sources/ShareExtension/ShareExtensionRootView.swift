import SwiftUI

struct ShareExtensionRootView: View {
    @ObservedObject var viewModel: ShareExtensionViewModel
    let onDone: () -> Void
    let onOpenMainApp: () -> Void

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                GroupBox("Original Text") {
                    ScrollView {
                        Text(viewModel.originalText.isEmpty ? "No text loaded" : viewModel.originalText)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .textSelection(.enabled)
                    }
                    .frame(minHeight: 100, maxHeight: 160)
                }

                GroupBox("Anonymised Text") {
                    if viewModel.isLoading {
                        HStack(spacing: 10) {
                            ProgressView()
                            Text("Sanitising...")
                                .foregroundStyle(.secondary)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 8)
                    } else {
                        ScrollView {
                            Text(viewModel.anonymizedText.isEmpty ? "No anonymised output yet" : viewModel.anonymizedText)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .textSelection(.enabled)
                        }
                        .frame(minHeight: 100, maxHeight: 160)
                    }
                }

                if let error = viewModel.errorMessage {
                    Text(error)
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else if let usageLimit = viewModel.usageLimitState {
                    VStack(alignment: .leading, spacing: 6) {
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
                            onOpenMainApp()
                        } label: {
                            Label("Open Main App to Go Pro", systemImage: "arrow.up.right.square")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .foregroundStyle(BrandTheme.prominentButtonText)
                        .padding(.top, 4)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                } else if let status = viewModel.statusMessage {
                    Text(status)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                HStack(spacing: 10) {
                    Button {
                        viewModel.copyResult()
                    } label: {
                        Label("Copy", systemImage: "doc.on.doc")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .foregroundStyle(BrandTheme.prominentButtonText)
                    .disabled(viewModel.anonymizedText.isEmpty)

                    Button {
                        onOpenMainApp()
                    } label: {
                        Label("Open Main App", systemImage: "arrow.up.right.square")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }

                Button("Done", role: .cancel) {
                    onDone()
                }
                .frame(maxWidth: .infinity)
                .buttonStyle(.bordered)
            }
            .padding(14)
            .navigationTitle("Sanitise for AI")
            .navigationBarTitleDisplayMode(.inline)
        }
        .tint(BrandTheme.accent)
    }
}
