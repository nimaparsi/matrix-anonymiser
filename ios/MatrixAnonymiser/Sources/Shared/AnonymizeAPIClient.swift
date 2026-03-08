import Foundation

enum AnonymizeClientError: LocalizedError {
    case emptyInput
    case invalidResponse
    case serverError(String)
    case usageLimitReached(UsageLimitState)
    case emptyOutput

    var errorDescription: String? {
        switch self {
        case .emptyInput:
            return "Paste or share text first."
        case .invalidResponse:
            return "The anonymisation service returned an invalid response."
        case .serverError(let message):
            return message
        case .usageLimitReached(let state):
            return state.message
        case .emptyOutput:
            return "No anonymised text was returned."
        }
    }
}

protocol AnonymizeServicing {
    func anonymize(text: String, entityTypes: [String], tagStyle: AnonymizeTagStyle, reversePronouns: Bool) async throws -> String
}

final class AnonymizeAPIClient: AnonymizeServicing {
    private let session: URLSession
    private let baseURL: URL

    init(baseURL: URL = AppConfig.defaultAPIBaseURL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    func anonymize(
        text: String,
        entityTypes: [String] = AnonymizeEntityType.allCases.map(\.rawValue),
        tagStyle: AnonymizeTagStyle = .standard,
        reversePronouns: Bool = false
    ) async throws -> String {
        let cleaned = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard cleaned.isEmpty == false else {
            throw AnonymizeClientError.emptyInput
        }

        let endpoint = baseURL.appending(path: "api/anonymize")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(
            AnonymizeRequest(
                text: cleaned,
                entityTypes: entityTypes,
                tagStyle: tagStyle.rawValue,
                reversePronouns: reversePronouns
            )
        )

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw AnonymizeClientError.invalidResponse
        }

        guard (200 ... 299).contains(http.statusCode) else {
            let payload = try? JSONDecoder().decode(APIErrorResponse.self, from: data)
            if case .object(let detail)? = payload?.detail,
               detail.code == "USAGE_LIMIT_EXCEEDED" {
                throw AnonymizeClientError.usageLimitReached(
                    UsageLimitState(
                        message: detail.message ?? "Daily limit reached",
                        used: detail.used,
                        limit: detail.limit
                    )
                )
            }
            throw AnonymizeClientError.serverError(payload?.detail?.message ?? "Request failed with status \(http.statusCode)")
        }

        let decoded = try JSONDecoder().decode(AnonymizeResponse.self, from: data)
        let output = decoded.sanitizedText
        guard output.isEmpty == false else {
            throw AnonymizeClientError.emptyOutput
        }
        return output
    }
}
