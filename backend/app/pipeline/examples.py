"""
Static example bank for few-shot diversity injection into the generation prompt.

Each topic has 4 diverse, hand-curated examples.  Two are sampled randomly at
generation time and shown to the LLM as "write something different from these".
"""
import random

from app.models import Topic

# ---------------------------------------------------------------------------
# Example bank  (Topic → list of complete, working Python snippets)
# ---------------------------------------------------------------------------

TOPIC_EXAMPLES: dict[Topic, list[str]] = {

    Topic.DATA_TYPES: [
        # Celsius / Fahrenheit conversion
        """\
def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9

if __name__ == "__main__":
    assert celsius_to_fahrenheit(0) == 32.0
    assert celsius_to_fahrenheit(100) == 212.0
    assert round(fahrenheit_to_celsius(98.6), 1) == 37.0
    print("All tests passed.")
""",
        # Safe integer parsing from string
        """\
def safe_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

if __name__ == "__main__":
    assert safe_int("42") == 42
    assert safe_int("abc") == 0
    assert safe_int("abc", -1) == -1
    assert safe_int("  7  ") == 7
    print("All tests passed.")
""",
        # Byte-size formatter
        """\
def format_bytes(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size //= 1024
    return f"{size:.1f} TB"

if __name__ == "__main__":
    assert format_bytes(500) == "500.0 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1048576) == "1.0 MB"
    print("All tests passed.")
""",
        # Palindrome number check
        """\
def is_palindrome_number(n: int) -> bool:
    if n < 0:
        return False
    s = str(n)
    return s == s[::-1]

if __name__ == "__main__":
    assert is_palindrome_number(121) is True
    assert is_palindrome_number(-121) is False
    assert is_palindrome_number(0) is True
    assert is_palindrome_number(123) is False
    print("All tests passed.")
""",
    ],

    Topic.DATA_STRUCTURES: [
        # Frequency counter
        """\
def most_frequent(items: list):
    if not items:
        return None
    counts: dict = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return max(counts, key=counts.get)

if __name__ == "__main__":
    assert most_frequent([1, 2, 2, 3, 2]) == 2
    assert most_frequent(["a", "b", "a"]) == "a"
    assert most_frequent([]) is None
    print("All tests passed.")
""",
        # Set operations
        """\
def find_common(list1: list, list2: list) -> list:
    return sorted(set(list1) & set(list2))

def find_unique_to_first(list1: list, list2: list) -> list:
    return sorted(set(list1) - set(list2))

if __name__ == "__main__":
    assert find_common([1, 2, 3, 4], [3, 4, 5, 6]) == [3, 4]
    assert find_unique_to_first([1, 2, 3], [2, 3, 4]) == [1]
    assert find_common([], [1, 2]) == []
    print("All tests passed.")
""",
        # Group-by using a dict of lists
        """\
def group_by(items: list, key_fn) -> dict:
    result: dict = {}
    for item in items:
        k = key_fn(item)
        result.setdefault(k, []).append(item)
    return result

if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5, 6]
    grouped = group_by(nums, lambda x: "even" if x % 2 == 0 else "odd")
    assert grouped["even"] == [2, 4, 6]
    assert grouped["odd"] == [1, 3, 5]
    print("All tests passed.")
""",
        # Order-preserving deduplication
        """\
def deduplicate(items: list) -> list:
    seen: set = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

if __name__ == "__main__":
    assert deduplicate([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
    assert deduplicate(["a", "b", "a", "c"]) == ["a", "b", "c"]
    assert deduplicate([]) == []
    print("All tests passed.")
""",
    ],

    Topic.OPERATORS: [
        # Bitwise bit-count and power-of-two test
        """\
def count_set_bits(n: int) -> int:
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count

def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

if __name__ == "__main__":
    assert count_set_bits(13) == 3   # 1101
    assert count_set_bits(0) == 0
    assert is_power_of_two(8) is True
    assert is_power_of_two(6) is False
    print("All tests passed.")
""",
        # Floor-division / modulo for time conversion
        """\
def to_hours_minutes_seconds(total_seconds: int) -> tuple:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds

if __name__ == "__main__":
    assert to_hours_minutes_seconds(3661) == (1, 1, 1)
    assert to_hours_minutes_seconds(0) == (0, 0, 0)
    assert to_hours_minutes_seconds(7200) == (2, 0, 0)
    print("All tests passed.")
""",
        # Clamp with comparison operators
        """\
def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

def is_between(value: float, low: float, high: float) -> bool:
    return low <= value <= high

if __name__ == "__main__":
    assert clamp(5, 1, 10) == 5
    assert clamp(-3, 1, 10) == 1
    assert clamp(15, 1, 10) == 10
    assert is_between(5, 1, 10) is True
    assert is_between(11, 1, 10) is False
    print("All tests passed.")
""",
        # String repeat / multiplication operator
        """\
def build_ruler(width: int, unit: str = "-") -> str:
    return unit * width

def center_label(label: str, width: int) -> str:
    padding = (width - len(label)) // 2
    return " " * padding + label + " " * padding

if __name__ == "__main__":
    assert build_ruler(5) == "-----"
    assert build_ruler(3, "=") == "==="
    assert center_label("hi", 6) == "  hi  "
    print("All tests passed.")
""",
    ],

    Topic.LOOPS: [
        # Running statistics (no stdlib)
        """\
def compute_stats(numbers: list) -> dict:
    if not numbers:
        return {"count": 0, "total": 0, "mean": None}
    total = 0
    for n in numbers:
        total += n
    return {"count": len(numbers), "total": total, "mean": total / len(numbers)}

if __name__ == "__main__":
    r = compute_stats([1, 2, 3, 4, 5])
    assert r["count"] == 5
    assert r["total"] == 15
    assert r["mean"] == 3.0
    assert compute_stats([])["mean"] is None
    print("All tests passed.")
""",
        # Matrix transpose with nested loops
        """\
def transpose(matrix: list) -> list:
    if not matrix:
        return []
    rows, cols = len(matrix), len(matrix[0])
    result = [[0] * rows for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            result[j][i] = matrix[i][j]
    return result

if __name__ == "__main__":
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transpose([]) == []
    print("All tests passed.")
""",
        # Collatz sequence with while loop
        """\
def collatz_length(n: int) -> int:
    count = 1
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        count += 1
    return count

if __name__ == "__main__":
    assert collatz_length(1) == 1
    assert collatz_length(6) == 9
    assert collatz_length(16) == 5
    print("All tests passed.")
""",
        # Dot product with zip
        """\
def dot_product(v1: list, v2: list) -> float:
    return sum(a * b for a, b in zip(v1, v2))

def vector_add(v1: list, v2: list) -> list:
    return [a + b for a, b in zip(v1, v2)]

if __name__ == "__main__":
    assert dot_product([1, 2, 3], [4, 5, 6]) == 32
    assert dot_product([], []) == 0
    assert vector_add([1, 2], [3, 4]) == [4, 6]
    print("All tests passed.")
""",
    ],

    Topic.FUNCTIONS: [
        # Default parameters + greet
        """\
def format_name(first: str, last: str, title: str = "") -> str:
    if title:
        return f"{title} {first} {last}"
    return f"{first} {last}"

def repeat_greet(name: str, times: int = 1) -> list:
    return [f"Hello, {name}!" for _ in range(times)]

if __name__ == "__main__":
    assert format_name("Jane", "Doe") == "Jane Doe"
    assert format_name("Jane", "Doe", "Dr.") == "Dr. Jane Doe"
    assert repeat_greet("Alice", 3) == ["Hello, Alice!"] * 3
    print("All tests passed.")
""",
        # Closures / factory functions
        """\
def make_multiplier(factor: float):
    def multiply(x: float) -> float:
        return x * factor
    return multiply

def make_adder(n: float):
    def add(x: float) -> float:
        return x + n
    return add

if __name__ == "__main__":
    double = make_multiplier(2)
    triple = make_multiplier(3)
    add_ten = make_adder(10)
    assert double(5) == 10
    assert triple(4) == 12
    assert add_ten(double(3)) == 16
    print("All tests passed.")
""",
        # Recursive binary search
        """\
def binary_search(arr: list, target, low: int = 0, high: int = None) -> int:
    if high is None:
        high = len(arr) - 1
    if low > high:
        return -1
    mid = (low + high) // 2
    if arr[mid] == target:
        return mid
    if arr[mid] < target:
        return binary_search(arr, target, mid + 1, high)
    return binary_search(arr, target, low, mid - 1)

if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11]
    assert binary_search(arr, 7) == 3
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 4) == -1
    print("All tests passed.")
""",
        # Higher-order / compose
        """\
def apply_to_all(func, items: list) -> list:
    return [func(item) for item in items]

def compose(f, g):
    return lambda x: f(g(x))

if __name__ == "__main__":
    doubled = apply_to_all(lambda x: x * 2, [1, 2, 3, 4])
    assert doubled == [2, 4, 6, 8]
    square_of_increment = compose(lambda x: x ** 2, lambda x: x + 1)
    assert square_of_increment(3) == 16
    assert square_of_increment(0) == 1
    print("All tests passed.")
""",
    ],

    Topic.CLASSES: [
        # 2D vector
        """\
class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def add(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def scale(self, factor: float) -> "Vector2D":
        return Vector2D(self.x * factor, self.y * factor)

if __name__ == "__main__":
    v = Vector2D(3, 4)
    assert v.magnitude() == 5.0
    v2 = v.add(Vector2D(1, 0))
    assert v2.x == 4 and v2.y == 4
    print("All tests passed.")
""",
        # Simple bank account
        """\
class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self._balance = balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> float:
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        return self._balance

    @property
    def balance(self) -> float:
        return self._balance

if __name__ == "__main__":
    acc = BankAccount("Alice", 100.0)
    acc.deposit(50.0)
    assert acc.balance == 150.0
    acc.withdraw(30.0)
    assert acc.balance == 120.0
    print("All tests passed.")
""",
        # Temperature unit converter class
        """\
class Temperature:
    def __init__(self, value: float, unit: str = "C"):
        self.value = value
        self.unit = unit.upper()

    def to_celsius(self) -> float:
        if self.unit == "C":
            return self.value
        if self.unit == "F":
            return (self.value - 32) * 5 / 9
        if self.unit == "K":
            return self.value - 273.15
        raise ValueError(f"Unknown unit: {self.unit}")

    def to_fahrenheit(self) -> float:
        return self.to_celsius() * 9 / 5 + 32

if __name__ == "__main__":
    assert Temperature(100, "C").to_fahrenheit() == 212.0
    assert Temperature(32, "F").to_celsius() == 0.0
    assert round(Temperature(273.15, "K").to_celsius(), 2) == 0.0
    print("All tests passed.")
""",
        # Minimal linked list
        """\
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

def list_to_linked(items: list) -> Node:
    if not items:
        return None
    head = Node(items[0])
    cur = head
    for item in items[1:]:
        cur.next = Node(item)
        cur = cur.next
    return head

def linked_to_list(head: Node) -> list:
    result = []
    while head:
        result.append(head.value)
        head = head.next
    return result

if __name__ == "__main__":
    assert linked_to_list(list_to_linked([1, 2, 3])) == [1, 2, 3]
    assert linked_to_list(None) == []
    print("All tests passed.")
""",
    ],

    Topic.ERROR_HANDLING: [
        # Safe division with default
        """\
def safe_divide(a: float, b: float, default: float = None):
    try:
        return a / b
    except ZeroDivisionError:
        return default

if __name__ == "__main__":
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 0, -1.0) == -1.0
    print("All tests passed.")
""",
        # Safe list access
        """\
def safe_get(lst: list, index: int, default=None):
    try:
        return lst[index]
    except IndexError:
        return default

def safe_pop(lst: list):
    try:
        return lst.pop()
    except IndexError:
        return None

if __name__ == "__main__":
    nums = [10, 20, 30]
    assert safe_get(nums, 1) == 20
    assert safe_get(nums, 99) is None
    assert safe_get(nums, 99, -1) == -1
    assert safe_pop([]) is None
    print("All tests passed.")
""",
        # Custom validation exception
        """\
class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"'{field}': {message}")

def validate_age(age: int) -> int:
    if not isinstance(age, int):
        raise ValidationError("age", "must be an integer")
    if not (0 <= age <= 150):
        raise ValidationError("age", f"{age} is out of range")
    return age

if __name__ == "__main__":
    assert validate_age(25) == 25
    try:
        validate_age(-1)
        assert False
    except ValidationError as e:
        assert e.field == "age"
    print("All tests passed.")
""",
        # Finally for guaranteed cleanup
        """\
def process_with_cleanup(data: list, fail_at: int = -1) -> dict:
    result = {"processed": 0, "cleaned_up": False}
    try:
        for i, item in enumerate(data):
            if i == fail_at:
                raise RuntimeError(f"Forced failure at {i}")
            result["processed"] += 1
    except RuntimeError:
        result["error"] = True
    finally:
        result["cleaned_up"] = True
    return result

if __name__ == "__main__":
    r1 = process_with_cleanup([1, 2, 3])
    assert r1["processed"] == 3 and r1["cleaned_up"] is True
    r2 = process_with_cleanup([1, 2, 3], fail_at=1)
    assert r2["processed"] == 1 and r2["cleaned_up"] is True
    print("All tests passed.")
""",
    ],

    Topic.COMPREHENSIONS: [
        # Filter + transform list comprehension
        """\
def even_squares(n: int) -> list:
    return [x ** 2 for x in range(n) if x % 2 == 0]

def words_longer_than(words: list, min_length: int) -> list:
    return [w.upper() for w in words if len(w) > min_length]

if __name__ == "__main__":
    assert even_squares(7) == [0, 4, 16, 36]
    assert words_longer_than(["hi", "hello", "hey", "world"], 3) == ["HELLO", "WORLD"]
    print("All tests passed.")
""",
        # Dict comprehension
        """\
def invert_dict(d: dict) -> dict:
    return {v: k for k, v in d.items()}

def zip_to_dict(keys: list, values: list) -> dict:
    return {k: v for k, v in zip(keys, values) if v is not None}

if __name__ == "__main__":
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert zip_to_dict(["a", "b", "c"], [1, None, 3]) == {"a": 1, "c": 3}
    print("All tests passed.")
""",
        # Flatten nested list
        """\
def flatten(nested: list) -> list:
    return [item for sublist in nested for item in sublist]

def flatten_and_filter(nested: list, min_val: int) -> list:
    return [x for sublist in nested for x in sublist if x >= min_val]

if __name__ == "__main__":
    assert flatten([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]
    assert flatten([]) == []
    assert flatten_and_filter([[1, 5], [2, 6], [3, 7]], 5) == [5, 6, 7]
    print("All tests passed.")
""",
        # Set comprehension + conditional expression
        """\
def unique_lengths(words: list) -> set:
    return {len(w) for w in words}

def label_numbers(numbers: list) -> list:
    return [
        "zero" if n == 0 else ("positive" if n > 0 else "negative")
        for n in numbers
    ]

if __name__ == "__main__":
    assert unique_lengths(["cat", "dog", "elephant"]) == {3, 8}
    assert label_numbers([-2, 0, 3]) == ["negative", "zero", "positive"]
    print("All tests passed.")
""",
    ],

    Topic.DECORATORS: [
        # Call counter
        """\
def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper

@count_calls
def add(a, b):
    return a + b

if __name__ == "__main__":
    assert add(1, 2) == 3
    assert add(10, 20) == 30
    assert add.call_count == 2
    print("All tests passed.")
""",
        # Input validator
        """\
def require_positive(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (int, float)) and arg <= 0:
                raise ValueError(f"All args must be positive, got {arg}")
        return func(*args, **kwargs)
    return wrapper

@require_positive
def square_root(n: float) -> float:
    return n ** 0.5

if __name__ == "__main__":
    assert square_root(9) == 3.0
    try:
        square_root(-1)
        assert False
    except ValueError:
        pass
    print("All tests passed.")
""",
        # Simple memoize
        """\
def memoize(func):
    cache: dict = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    wrapper.cache = cache
    return wrapper

@memoize
def slow_multiply(a: int, b: int) -> int:
    return a * b

if __name__ == "__main__":
    assert slow_multiply(3, 4) == 12
    assert slow_multiply(3, 4) == 12   # from cache
    assert (3, 4) in slow_multiply.cache
    print("All tests passed.")
""",
        # Uppercase result
        """\
def uppercase_result(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper() if isinstance(result, str) else result
    return wrapper

@uppercase_result
def get_greeting(name: str) -> str:
    return f"hello, {name}"

@uppercase_result
def get_number() -> int:
    return 42

if __name__ == "__main__":
    assert get_greeting("alice") == "HELLO, ALICE"
    assert get_number() == 42   # non-string unchanged
    print("All tests passed.")
""",
    ],

    Topic.GENERATORS: [
        # Float range generator
        """\
def float_range(start: float, stop: float, step: float):
    current = start
    while current < stop:
        yield current
        current += step

if __name__ == "__main__":
    result = list(float_range(0, 1, 0.25))
    assert result == [0, 0.25, 0.5, 0.75]
    assert list(float_range(1, 0, 0.1)) == []
    print("All tests passed.")
""",
        # Chunked batches
        """\
def chunks(sequence, size: int):
    for i in range(0, len(sequence), size):
        yield sequence[i:i + size]

if __name__ == "__main__":
    result = list(chunks([1, 2, 3, 4, 5, 6, 7], 3))
    assert result == [[1, 2, 3], [4, 5, 6], [7]]
    assert list(chunks([], 2)) == []
    assert list(chunks("abcde", 2)) == ["ab", "cd", "e"]
    print("All tests passed.")
""",
        # Running total
        """\
def running_total(numbers):
    total = 0
    for n in numbers:
        total += n
        yield total

if __name__ == "__main__":
    assert list(running_total([1, 2, 3, 4, 5])) == [1, 3, 6, 10, 15]
    assert list(running_total([])) == []
    assert list(running_total([10])) == [10]
    print("All tests passed.")
""",
        # Unique elements preserving order
        """\
def unique_ordered(iterable):
    seen: set = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item

if __name__ == "__main__":
    result = list(unique_ordered([3, 1, 4, 1, 5, 9, 2, 6, 5]))
    assert result == [3, 1, 4, 5, 9, 2, 6]
    assert list(unique_ordered("aabbcc")) == ["a", "b", "c"]
    print("All tests passed.")
""",
    ],

    Topic.FILE_IO: [
        # CSV-like text parsing (no actual file needed)
        """\
def parse_csv(text: str, delimiter: str = ",") -> list:
    result = []
    for line in text.strip().split("\\n"):
        if line.strip():
            result.append(line.split(delimiter))
    return result

def get_column(rows: list, index: int) -> list:
    return [row[index] for row in rows if index < len(row)]

if __name__ == "__main__":
    data = "name,age\\nAlice,30\\nBob,25"
    parsed = parse_csv(data)
    assert parsed[0] == ["name", "age"]
    assert get_column(parsed, 0) == ["name", "Alice", "Bob"]
    print("All tests passed.")
""",
        # Word frequency from text
        """\
def word_frequency(text: str) -> dict:
    freq: dict = {}
    for word in text.lower().split():
        word = word.strip(".,!?;:")
        freq[word] = freq.get(word, 0) + 1
    return freq

def top_n_words(text: str, n: int) -> list:
    freq = word_frequency(text)
    return sorted(freq, key=freq.get, reverse=True)[:n]

if __name__ == "__main__":
    text = "the cat sat on the mat the cat"
    assert word_frequency(text)["the"] == 3
    assert top_n_words(text, 2) == ["the", "cat"]
    print("All tests passed.")
""",
        # Key=value config parser
        """\
def parse_config(text: str) -> dict:
    config: dict = {}
    for line in text.strip().split("\\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip()
    return config

if __name__ == "__main__":
    cfg = parse_config("# comment\\nhost = localhost\\nport = 5432")
    assert cfg["host"] == "localhost"
    assert cfg["port"] == "5432"
    assert len(cfg) == 2
    print("All tests passed.")
""",
        # Markdown heading extractor
        """\
def extract_headings(markdown: str) -> list:
    headings = []
    for line in markdown.split("\\n"):
        line = line.strip()
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            headings.append({"level": level, "text": text})
    return headings

if __name__ == "__main__":
    md = "# Title\\n## Section\\n### Sub\\nplain text\\n## Another"
    headings = extract_headings(md)
    assert len(headings) == 4
    assert headings[0] == {"level": 1, "text": "Title"}
    print("All tests passed.")
""",
    ],

    Topic.EXCEPTIONS: [
        # Custom exception hierarchy
        """\
class AppError(Exception):
    pass

class QueryError(AppError):
    def __init__(self, query: str, reason: str):
        self.query = query
        super().__init__(f"Query failed — {reason}")

def execute_query(query: str) -> str:
    if not query.strip():
        raise QueryError(query, "empty query")
    if "DROP" in query.upper():
        raise QueryError(query, "DROP not allowed")
    return "OK"

if __name__ == "__main__":
    assert execute_query("SELECT 1") == "OK"
    try:
        execute_query("")
        assert False
    except QueryError as e:
        assert "empty" in str(e)
    print("All tests passed.")
""",
        # Exception chaining
        """\
class ParseError(Exception):
    pass

def parse_int_list(text: str) -> list:
    try:
        return [int(x.strip()) for x in text.split(",")]
    except ValueError as e:
        raise ParseError(f"Invalid integer list: '{text}'") from e

if __name__ == "__main__":
    assert parse_int_list("1, 2, 3") == [1, 2, 3]
    try:
        parse_int_list("1, two, 3")
        assert False
    except ParseError as e:
        assert e.__cause__ is not None
        assert "two" in str(e)
    print("All tests passed.")
""",
        # Multiple except branches
        """\
def parse_config_value(key: str, value: str, expected_type: type):
    try:
        return expected_type(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to {expected_type.__name__} for '{key}'")
    except TypeError as e:
        raise TypeError(f"Bad type for '{key}': {e}") from e

if __name__ == "__main__":
    assert parse_config_value("port", "8080", int) == 8080
    assert parse_config_value("rate", "3.14", float) == 3.14
    try:
        parse_config_value("count", "abc", int)
        assert False
    except ValueError as e:
        assert "count" in str(e)
    print("All tests passed.")
""",
        # Retry on exception
        """\
def retry(func, times: int = 3, catch=(Exception,)):
    last_error = None
    for _ in range(times):
        try:
            return func()
        except catch as e:
            last_error = e
    raise last_error

_counter = [0]

def sometimes_fails():
    _counter[0] += 1
    if _counter[0] < 3:
        raise RuntimeError("not ready")
    return "success"

if __name__ == "__main__":
    _counter[0] = 0
    result = retry(sometimes_fails, times=5)
    assert result == "success"
    assert _counter[0] == 3
    print("All tests passed.")
""",
    ],
}


def sample_examples(topic: Topic, n: int = 2) -> list[str]:
    """Return up to *n* randomly chosen examples for *topic*."""
    pool = TOPIC_EXAMPLES.get(topic, [])
    return random.sample(pool, min(n, len(pool)))
