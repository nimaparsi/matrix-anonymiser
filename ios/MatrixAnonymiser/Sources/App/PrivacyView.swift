import SwiftUI

struct PrivacyView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Group {
                    Text("How Matrix Anonymiser handles data")
                        .font(.headline)
                    Text("Text you submit is sent to the anonymisation service to produce redacted output.")
                    Text("The app does not keep a history of your prompts by default. Shared extension content is passed through the app group only for handoff between the extension and app.")
                    Text("Always review anonymised output before sharing it with external AI tools.")
                }
                .foregroundStyle(.primary)
            }
            .padding()
        }
        .navigationTitle("Privacy")
        .background(Color(.systemGroupedBackground))
    }
}
