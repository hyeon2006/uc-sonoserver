import json
import re

"""
INPUT EXAMPLE:

export const Text = {
    /** en: Custom Server */
    CustomServer: '#CUSTOM_SERVER',
    /** en: Collection */
    Collection: '#COLLECTION',
    /** en: Server */
    Server: '#SERVER',
    /** en: Address */
    Address: '#ADDRESS',
    /** en: Expiration */
    Expiration: '#EXPIRATION',
    /** en: Storage */
    Storage: '#STORAGE',
    /** en: Log */
    Log: '#LOG',
} as const

export type Text = (typeof Text)[keyof typeof Text]
end
"""

text = ""

while True:
    input_ = input()

    if input_ == "end":
        break

    text += input_

result = re.findall(r"'[^']+'", text)
result = [item.strip("'") for item in result]   

print("Literal" + json.dumps(result))