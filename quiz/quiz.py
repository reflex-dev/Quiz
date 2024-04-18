"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from rxconfig import config

import reflex as rx

docs_url = "https://reflex.dev/docs/getting-started/introduction/"

questions = [
    {
        "id": 0,
        "question_type": "multiple_choice",
        "question_body": "Which of the following are fruits?",
        "question_image": None,
        "options": ["Apple", "Carrot", "Banana", "Lettuce", "Orange"],
        "correct_answers": ["Apple", "Banana", "Orange"]
    },
    {
        "id": 1,
        "question_type": "single_choice",
        "question_body": "What is the capital of Canada?",
        "question_image": None,
        "options": ["Toronto", "Vancouver", "Ottawa", "Montreal"],
        "correct_answers": ["Ottawa"]
    },
    {
        "id": 2,
        "question_type": "multiple_choice",
        "question_body": "Which of the following are mammals?",
        "question_image": None,
        "options": ["Penguin", "Bat", "Dolphin", "Eagle", "Shark"],
        "correct_answers": ["Bat", "Dolphin"]
    },
    {
        "id": 3,
        "question_type": "single_choice",
        "question_body": "What is the largest planet in our solar system?",
        "question_image": None,
        "options": ["Mars", "Jupiter", "Saturn", "Neptune"],
        "correct_answers": ["Jupiter"]
    },
    {
        "id": 4,
        "question_type": "multiple_choice",
        "question_body": "Which of the following are programming languages?",
        "question_image": None,
        "options": ["Python", "English", "Java", "French", "C++"],
        "correct_answers": ["Python", "Java", "C++"]
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

def result_comp() -> rx.Component:
    return rx.center(
        rx.text("Test Result"),
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
