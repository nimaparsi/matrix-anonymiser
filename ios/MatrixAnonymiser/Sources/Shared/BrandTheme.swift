import SwiftUI
import UIKit

enum BrandTheme {
    static let accent = Color(
        uiColor: UIColor { traits in
            if traits.userInterfaceStyle == .dark {
                return UIColor(red: 0.24, green: 1.0, blue: 0.62, alpha: 1.0)
            }
            return UIColor(red: 0.06, green: 0.56, blue: 0.33, alpha: 1.0)
        }
    )

    static let cardBorder = Color(
        uiColor: UIColor { traits in
            if traits.userInterfaceStyle == .dark {
                return UIColor(red: 0.24, green: 1.0, blue: 0.62, alpha: 0.22)
            }
            return UIColor(red: 0.06, green: 0.56, blue: 0.33, alpha: 0.14)
        }
    )
}
