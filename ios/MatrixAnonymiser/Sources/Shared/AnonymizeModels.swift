import Foundation

enum AnonymizeEntityType: String, CaseIterable, Codable, Identifiable {
    case person = "PERSON"
    case email = "EMAIL"
    case apiKey = "API_KEY"
    case privateKey = "PRIVATE_KEY"
    case governmentID = "GOVERNMENT_ID"
    case bankAccount = "BANK_ACCOUNT"
    case creditCard = "CREDIT_CARD"
    case phone = "PHONE"
    case ipAddress = "IP_ADDRESS"
    case webAddress = "URL"
    case address = "ADDRESS"
    case organisation = "ORG"
    case date = "DATE"
    case username = "USERNAME"
    case coordinate = "COORDINATE"
    case filePath = "FILE_PATH"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .person:
            return "Person"
        case .email:
            return "Email"
        case .apiKey:
            return "API Key"
        case .privateKey:
            return "Private Key"
        case .governmentID:
            return "Government ID"
        case .bankAccount:
            return "Bank Account"
        case .creditCard:
            return "Credit Card"
        case .phone:
            return "Phone"
        case .ipAddress:
            return "IP Address"
        case .webAddress:
            return "URL"
        case .address:
            return "Address"
        case .organisation:
            return "Organisation"
        case .date:
            return "Date"
        case .username:
            return "Username"
        case .coordinate:
            return "Coordinate"
        case .filePath:
            return "File Path"
        }
    }
}

struct AnonymizeRequest: Encodable {
    let text: String
    let entity_types: [String]
    let tag_style: String
    let reverse_pronouns: Bool

    init(
        text: String,
        entityTypes: [String] = AnonymizeEntityType.allCases.map(\.rawValue),
        tagStyle: String = "standard",
        reversePronouns: Bool = false
    ) {
        self.text = text
        self.entity_types = entityTypes
        self.tag_style = tagStyle
        self.reverse_pronouns = reversePronouns
    }
}

enum AnonymizeTagStyle: String {
    case standard
    case emoji
}

struct AnonymizeResponse: Decodable {
    let result: String?
    let anonymized_text: String?
    let counts: [String: Int]?
    let meta: Meta?

    struct Meta: Decodable {
        let processing_ms: Int?
        let language: String?
    }

    var sanitizedText: String {
        let direct = (result ?? anonymized_text ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        return direct
    }
}

func applyRedactionMode(_ text: String) -> String {
    let pattern = #"(?:\[[^\]\n]{2,80}\]|\b(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b)"#
    guard let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]) else {
        return text
    }
    let range = NSRange(text.startIndex..<text.endIndex, in: text)
    return regex.stringByReplacingMatches(in: text, options: [], range: range, withTemplate: "[REDACTED]")
}

struct APIErrorResponse: Decodable {
    let detail: APIErrorDetail?

    enum APIErrorDetail: Decodable {
        case text(String)
        case object(ErrorObject)

        struct ErrorObject: Decodable {
            let message: String?
            let code: String?
            let used: Int?
            let limit: Int?
        }

        init(from decoder: Decoder) throws {
            let container = try decoder.singleValueContainer()
            if let text = try? container.decode(String.self) {
                self = .text(text)
                return
            }
            if let object = try? container.decode(ErrorObject.self) {
                self = .object(object)
                return
            }
            self = .text("Unexpected API error")
        }

        var message: String {
            switch self {
            case .text(let text):
                return text
            case .object(let object):
                return object.message ?? object.code ?? "Unexpected API error"
            }
        }
    }
}

struct UsageLimitState: Equatable {
    let message: String
    let used: Int?
    let limit: Int?

    var usageText: String? {
        guard let used, let limit else { return nil }
        return "\(used)/\(limit) used today"
    }
}
