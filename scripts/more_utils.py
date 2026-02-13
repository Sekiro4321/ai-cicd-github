def is_palindrome(text):
    """Check if a string is a palindrome."""
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

def armstrong_number(n):
    """Check if a number is an Armstrong number."""
    digits = str(n)
    num_digits = len(digits)
    armstrong_sum = sum(int(digit) ** num_digits for digit in digits)
    return armstrong_sum == n
