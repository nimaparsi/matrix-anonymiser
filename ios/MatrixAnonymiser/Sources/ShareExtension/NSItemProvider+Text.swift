import Foundation
import UniformTypeIdentifiers

extension NSItemProvider {
    func loadTextIfAvailable(type: String) async -> String? {
        guard hasItemConformingToTypeIdentifier(type) else {
            return nil
        }

        return await withCheckedContinuation { continuation in
            loadItem(forTypeIdentifier: type, options: nil) { item, _ in
                if let text = item as? String {
                    continuation.resume(returning: text.trimmingCharacters(in: .whitespacesAndNewlines))
                    return
                }
                if let attributed = item as? NSAttributedString {
                    continuation.resume(returning: attributed.string.trimmingCharacters(in: .whitespacesAndNewlines))
                    return
                }
                if let url = item as? URL,
                   let value = try? String(contentsOf: url),
                   value.isEmpty == false {
                    continuation.resume(returning: value.trimmingCharacters(in: .whitespacesAndNewlines))
                    return
                }
                continuation.resume(returning: nil)
            }
        }
    }
}
