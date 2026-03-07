import SwiftUI

struct MainAnonymizerView: View {
    @StateObject private var viewModel = AnonymizerViewModel()
    @State private var showShareSheet = false

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
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink {
                        PrivacyView()
                    } label: {
                        Label("Privacy", systemImage: "lock.shield")
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
        }
    }

    private var inputCard: some View {
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
        }
        .padding(14)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var outputCard: some View {
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
        .padding(14)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var actionCard: some View {
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
        }
        .padding(14)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}
