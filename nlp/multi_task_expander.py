# nlp/multi_task_expander.py
# S1 Assistant - Multi-Task Expander
# Focus: Splitting complex sentences into individual command strings.

class MultiTaskExpander:
    """
    Detects and splits multi-step commands into a list of strings.
    Example: "open chrome and search cats then create file test.txt"
    -> ["open chrome", "search cats", "create file test.txt"]
    """
    def __init__(self):
        # Delimiters that indicate a new task step
        self.delimiters = [" and ", " then ", " then also ", " , ", " and also "]

    def split_tasks(self, raw_text: str) -> list:
        """
        Splits raw text into a list of individual command strings.
        """
        if not raw_text:
            return []

        text = raw_text.lower().strip()
        tasks = [text]

        # Iteratively split by each delimiter
        for delim in self.delimiters:
            new_tasks = []
            for task in tasks:
                if delim in task:
                    parts = task.split(delim)
                    new_tasks.extend([p.strip() for p in parts if p.strip()])
                else:
                    new_tasks.append(task)
            tasks = new_tasks

        return tasks

# Global Access
_multi_expander_instance = MultiTaskExpander()

def get_multi_tasks(text: str) -> list:
    return _multi_expander_instance.split_tasks(text)
