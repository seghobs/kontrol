import re
def donustur(link_gir):
    def shortcode_to_numeric_media_id(shortcode):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        base = len(alphabet)
        numeric_id = 0

        for char in shortcode:
            numeric_id = numeric_id * base + alphabet.index(char)

        return numeric_id

    # Example usage with user input for a single link:
    link = link_gir

    # Extract shortcode from the link
    match = re.search(r'https://www\.instagram\.com/(?:p|reel)/([^/]+)/?', link)
    if match:
        shortcode = match.group(1)
        numeric_media_id = shortcode_to_numeric_media_id(shortcode)
        print(f"Link: {link}")
        print(f"Shortcode: {shortcode}")
        print(f"Numeric Media ID: {numeric_media_id}")
    else:
        print("Invalid Instagram link.")


    return numeric_media_id
