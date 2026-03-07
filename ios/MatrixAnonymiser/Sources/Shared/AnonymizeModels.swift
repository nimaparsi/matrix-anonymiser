import Foundation

struct AnonymizeRequest: Encodable {
    let text: String
    let entity_types: [String]
    let tag_style: String

    init(
        text: String,
        entityTypes: [String] = ["PERSON", "EMAIL", "PHONE", "URL", "ADDRESS", "ORG", "DATE"],
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
