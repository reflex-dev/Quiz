"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from rxconfig import config

import reflex as rx

docs_url = "https://reflex.dev/docs/getting-started/introduction/"

questions = [
    {
        "id": 0,
        "question_type": "multiple_choice",
        "question_body": "Which of the following are types of variables in a Reflex State?",
        "question_image": None,
        "options": ["Base Var", "Computed Var", "Dynamic Var", "Static Var"],
        "correct_answers": ["Base Var", "Computed Var"]
    },
    {
        "id": 1,
        "question_type": "single_choice",
        "question_body": "What type of function is used to modify base variables in Reflex?",
        "question_image": None,
        "options": ["Event Handler", "Computed Function", "Event Trigger", "State Method"],
        "correct_answers": ["Event Handler"]
    },
    {
        "id": 2,
        "question_type": "multiple_choice",
        "question_body": "Which operators are supported by Reflex for performing operations on vars?",
        "question_image": None,
        "options": ["+", "to_string()", "reverse()", "substring()"],
        "correct_answers": ["+", "to_string()", "reverse()"]
    },
    {
        "id": 3,
        "question_type": "single_choice",
        "question_body": "What does the @rx.cached_var decorator indicate about a var?",
        "question_image": None,
        "options": ["It is updated every time the state changes", "It is never updated", "It is only recomputed when dependent vars change", "It can be directly set by event handlers"],
        "correct_answers": ["It is only recomputed when dependent vars change"]
    },
    {
        "id": 4,
        "question_type": "multiple_choice",
        "question_body": "Which statements are true about base vars in Reflex?",
        "question_image": None,
        "options": ["They can be modified directly by event handlers", "They must be JSON serializable", "They are automatically recomputed", "They can store backend-only data"],
        "correct_answers": ["They can be modified directly by event handlers", "They must be JSON serializable"]
    }
]

class Question(rx.Base):
    id: int
    question_type: str
    question_body: str
    question_image: str | None
    options: list[str]
    correct_answers: list[str]
    selected_answers: list[str] = []
    is_correct: bool = False

    def _check_correct_answers(self, answers):
        return answers == self.correct_answers

class State(rx.State):
    """The app state."""
    index : int = 0
    quiz_completed: bool = False
    questions: list[Question] = [Question.parse_obj(q) for q in questions]
    submitted_answers: dict[int, list[str]] = {}

    def submit_question(self, data, question_id):
        print(data),
        if "_selected_option" in data:
            submitted_answer = [data["_selected_option"]]
        else:  # multiple_choice
            submitted_answer = [key for key, value in data.items() if value == "on"]
        self.submitted_answers[question_id] = submitted_answer
        self.questions[question_id].selected_answers = submitted_answer

        question = self.questions[question_id]
        question.is_correct = question._check_correct_answers(submitted_answer)

    @rx.var
    def current_question(self) -> Question:
        return self.questions[self.index]

    def next_question(self):
        if self.index < len(self.questions) - 1:
            self.index += 1

    def prev_question(self):
        if self.index > 0:
            self.index -= 1

    def submit_quiz(self):
        self.quiz_completed = True

    @rx.var
    def last_question(self):
        return self.index >= len(self.questions) - 1

def multi_choice_question_comp(question : Question) -> rx.Component:
    def is_selected(option: str) -> bool:
        return question.selected_answers.contains(option)

    return rx.form(
        rx.text(question.question_body),
        rx.foreach(
            question.options,
            lambda option: rx.checkbox(
                option,
                name=option,
                default_checked=is_selected(option),
            ),
        ),
        rx.hstack(
            previous_button(),
            rx.cond(
                State.last_question,
                rx.button("Submit", on_click=State.submit_quiz),
                next_button(),
            ),
        ),
        on_submit=lambda data: State.submit_question(data, question.id),
    )

def single_choice_question_comp(question : Question) -> rx.Component:
    return rx.form(
        rx.text(question.question_body),
        rx.radio(
            question.options,
            name="_selected_option",
            default_value=rx.cond(
                question.selected_answers.length() > 0,
                question.selected_answers[0],
                "",
            ),
        ),
        rx.hstack(
            previous_button(),
            rx.cond(
                State.last_question,
                rx.button("Submit", on_click=State.submit_quiz),
                next_button(),
            ),
        ),
        on_submit=lambda data: State.submit_question(data, question.id),
    )

def next_button():
    return rx.button(
        "Next",
        on_click=State.next_question,
    ) 

def previous_button():
    return rx.button(
        "Previous",
        on_click=State.prev_question,
    )

def quiz_comp() -> rx.Component:
    cur_question = State.current_question
    return rx.vstack(
        rx.cond(
            cur_question.question_type == "single_choice",
            single_choice_question_comp(cur_question),
            multi_choice_question_comp(cur_question),
        ),
    )

def question_result(question : Question) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Question: "),
            rx.text(question.id),
        ),
        rx.vstack(
            rx.cond(
                # fix the comparison
                question.is_correct,
                rx.text("Correct!"),
                rx.text("Incorrect!"),
            ),
        )
    )

def result_comp() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.text("-----Test Result-----"),
            rx.foreach(
                State.questions,
                question_result,
            ),
        )
    )

def index() -> rx.Component:
    return rx.center(
        rx.hstack(
            rx.cond(
                State.quiz_completed,
                result_comp(),
                quiz_comp(),
            ),
            align="center",
            spacing="7",
            font_size="2em",
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(index)

