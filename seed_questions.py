import json, os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Extended Question Bank for Robustness
# Format: (Category, Subject, Difficulty, QuestionText, Type, Options/Solution, CorrectAnswer)
raw_questions = [
    # ── QUIZ ────────────────────────────────────────────────────────────────
    ("Quiz", "Python", 1, "Which of these is a immutable type in Python?", "mcq", ["list", "dict", "tuple", "set"], "tuple"),
    ("Quiz", "Python", 2, "What is the output of 2**3?", "mcq", ["6", "8", "9", "12"], "8"),
    ("Quiz", "Python", 3, "Which keyword is used for function definition?", "mcq", ["func", "define", "def", "function"], "def"),
    ("Quiz", "Python", 4, "What does 'self' represent in a class method?", "mcq", ["The class itself", "The instance of the class", "A global variable", "A keyword"], "The instance of the class"),
    ("Quiz", "Python", 5, "What is the time complexity of a dict lookup in average case?", "mcq", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], "O(1)"),
    
    ("Quiz", "Java", 1, "Which data type is used to create a variable that should store text?", "mcq", ["String", "myString", "Txt", "string"], "String"),
    ("Quiz", "Java", 2, "How do you create a method in Java?", "mcq", ["methodName()", "methodName.", "(methodName)", "None of these"], "methodName()"),
    ("Quiz", "Java", 3, "Which keyword is used to create a class in Java?", "mcq", ["class", "className", "void", "static"], "class"),
    ("Quiz", "Java", 4, "What is the purpose of the 'final' keyword?", "mcq", ["To end the program", "To make a variable unchangeable", "To define a loop", "None"], "To make a variable unchangeable"),
    ("Quiz", "Java", 5, "Which collection allows unique elements only?", "mcq", ["List", "Set", "Map", "Queue"], "Set"),

    ("Quiz", "General Tech", 1, "What does RAM stand for?", "mcq", ["Random Access Memory", "Read Access Memory", "Rapid Access Memory", "Remote Access Memory"], "Random Access Memory"),
    ("Quiz", "General Tech", 2, "Which company developed Windows?", "mcq", ["Apple", "IBM", "Microsoft", "Google"], "Microsoft"),
    ("Quiz", "General Tech", 3, "What is the main function of an Operating System?", "mcq", ["Word Processing", "Resource Management", "Web Browsing", "Gaming"], "Resource Management"),
    ("Quiz", "General Tech", 4, "Which protocol is used for secure web browsing?", "mcq", ["HTTP", "HTTPS", "FTP", "SSH"], "HTTPS"),
    ("Quiz", "General Tech", 5, "What is the binary representation of decimal 5?", "mcq", ["100", "101", "110", "111"], "101"),

    ("Quiz", "Data Structures", 1, "A linear data structure where elements are added at one end and removed from the other?", "mcq", ["Stack", "Queue", "Tree", "Graph"], "Queue"),
    ("Quiz", "Data Structures", 2, "In a stack, which principle is used for addition/removal?", "mcq", ["FIFO", "LIFO", "LILO", "None"], "LIFO"),
    ("Quiz", "Data Structures", 3, "What is the time complexity of searching in a sorted array using binary search?", "mcq", ["O(n)", "O(log n)", "O(1)", "O(n^2)"], "O(log n)"),
    ("Quiz", "Data Structures", 4, "Which data structure is used in BFS (Breadth-First Search)?", "mcq", ["Stack", "Queue", "Heap", "Tree"], "Queue"),
    ("Quiz", "Data Structures", 5, "Which tree data structure maintains its height balanced?", "mcq", ["Binary Tree", "AVL Tree", "Binary Search Tree", "None"], "AVL Tree"),

    # ── CODING ──────────────────────────────────────────────────────────────
    ("Coding", "Python", 1, "Write a program to print the first 5 numbers.", "coding", [], "for i in range(1, 6): print(i)"),
    ("Coding", "Python", 3, "Write a function to check if a number is even.", "coding", [], "def is_even(n): return n % 2 == 0"),
    ("Coding", "Python", 5, "Write a recursive function for Fibonacci sequence.", "coding", [], "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)"),

    # ── DEBUGGING ───────────────────────────────────────────────────────────
    ("Debugging", "Python", 2, "### Problem:\nFix the syntax error.\n\n### Code:\n```python\nif x = 5:\n    print('True')\n```", "debugging", [], "if x == 5:\n    print('True')"),

    # ── DESCRIPTIVE ─────────────────────────────────────────────────────────
    ("Descriptive", "DBMS", 3, "Explain ACID properties in a database.", "descriptive", [], "Atomicity, Consistency, Isolation, Durability ensure reliable transaction processing."),
    ("Descriptive", "OS", 4, "Explain the difference between a process and a thread.", "descriptive", [], "A process is an executing instance of a program. A thread is a path of execution within a process."),
]

questions = {}
for i, (cat, sub, diff, q_text, q_type, opts, corr) in enumerate(raw_questions):
    qid = f"v5_{i+1:03d}"
    questions[qid] = {
        "question_id": qid,
        "category": cat.lower(),
        "topic": sub,
        "language": sub,
        "difficulty": diff,
        "question_text": q_text,
        "type": q_type,
        "options": opts,
        "correct_answer": corr,
        "marks": diff
    }

with open(os.path.join(DATA_DIR, "questions.json"), "w") as f:
    json.dump(questions, f, indent=2)

print(f"✅ V5 Question Engine Initialized with {len(questions)} items across all benchmarks.")
