import Foundation

enum AnonymizeEntityType: String, CaseIterable, Codable, Identifiable {
    case person = "PERSON"
    case email = "EMAIL"
    case phone = "PHONE"
    case webAddress = "URL"
    case address = "ADDRESS"
    case organisation = "ORG"
    case date = "DATE"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .person:
            return "Person"
        case .email:
            return "Email"
        case .phone:
            return "Phone"
        case .webAddress:
            return "Web Address"
        case .address:
            return "Address"
        case .organisation:
            return "Organisation"
        case .date:
            return "Date"
        }
    }
}

struct AnonymizeRequest: Encodable {
    let text: String
    let entity_types: [String]
    let tag_style: String

    init(
        text: String,
        entityTypes: [String] = AnonymizeEntityType.allCases.map(\.rawValue),
        tagStyle: String = "standard"
    ) {
        self.text = text
        self.entity_types = entityTypes
        self.tag_style = tagStyle
    }
}

struct AnonymizeResponse: Decodable {
    let result: String?
    let anonymized_text: String?

    var sanitizedText: String {
        let direct = (result ?? anonymized_text ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        return direct
    }
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
