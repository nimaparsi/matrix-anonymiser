import SwiftUI

struct AboutPrivacyView: View {
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
