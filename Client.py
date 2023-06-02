import tkinter as tk
from tkinter import ttk
import socket
import json


class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz App")
        self.master.geometry("700x350")
        self.master.resizable(False, False)

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        self.style.configure("TButton", background="#007bff", font=("Arial", 10, "bold"))
        self.style.configure("Green.TButton", background="green", foreground="green", font=("Arial", 10, "bold"))

        self.selected_data = []
        self.current_question_index = 0
        self.score = 0
        self.timer_seconds = 20
        self.timer_label = None
        self.timer_id = None
        self.connect_to_server()
        self.load_questions()

        self.question_label = ttk.Label(self.master, text="", anchor="center", wraplength=380)
        self.question_label.pack(pady=20)

        self.option_buttons = []
        for i in range(4):
            button = ttk.Button(self.master, text="", command=lambda i=i: self.check_answer(i))
            button.pack(pady=5)
            self.option_buttons.append(button)

        self.next_button = ttk.Button(self.master, text="Next", command=self.next_question)
        self.next_button.pack(pady=10)
        self.next_button.config(state=tk.DISABLED)

        self.result_label = ttk.Label(self.master, text="", anchor="center")
        self.result_label.pack(pady=10)

        self.timer_label = ttk.Label(self.master, text="Time left: 20 seconds")
        self.timer_label.pack(pady=10)

        self.update_question()
        self.start_timer()

    def connect_to_server(self):
        host = "139.177.176.194"
        port = 12345

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def load_questions(self):
        selected_data = self.client_socket.recv(4096).decode()
        self.selected_data = json.loads(selected_data)

    def update_question(self):
        if self.current_question_index < len(self.selected_data):
            question_data = self.selected_data[self.current_question_index]
            question = question_data["question"]
            options = question_data["options"]

            self.question_label.config(text=question)

            for i, option in enumerate(options):
                self.option_buttons[i].config(text=option)

            self.next_button.config(state=tk.DISABLED)
            self.result_label.config(text="")

        else:
            if self.current_question_index == len(self.selected_data):
                self.show_result()

    def check_answer(self, option_index):
        client_answer = option_index + 1
        self.client_socket.sendall(str(client_answer).encode())

        self.result_label.config(text="Checking...", foreground="blue")
        self.next_button.config(state=tk.DISABLED)
        for button in self.option_buttons:
            button.config(state=tk.DISABLED)

        self.master.after(500, self.process_answer)

    def process_answer(self):
        response = self.client_socket.recv(4096).decode()
        if response == "Correct":
            self.score += 1
            self.result_label.config(text="Correct", foreground="green")
        else:
            self.result_label.config(text="Incorrect", foreground="red")

        self.next_button.config(state=tk.NORMAL, style="Green.TButton")

    def next_question(self):
        for button in self.option_buttons:
            button.config(state=tk.NORMAL)

        self.current_question_index += 1
        self.update_question()

    def show_result(self):
        self.question_label.pack_forget()
        for button in self.option_buttons:
            button.pack_forget()
        self.next_button.pack_forget()
        self.result_label.pack_forget()
        self.timer_label.pack_forget()

        if self.timer_seconds == 0:
            result_text = "Time's up! Final score: {}/{}".format(self.score, len(self.selected_data))
        else:
            result_text = f"Quiz completed! Your score: {self.score}/{len(self.selected_data)}"

        self.result_label = ttk.Label(self.master, text=result_text, anchor="center")
        self.result_label.pack(pady=50)

        self.close_connection()

    def close_connection(self):
        self.client_socket.close()

    def start_timer(self):
        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"Time left: {self.timer_seconds} seconds")

        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Time's up!")
            self.show_result()

    def restart_timer(self):
        self.master.after_cancel(self.timer_id)
        self.timer_seconds = 20
        self.update_timer()


root = tk.Tk()
app = QuizApp(root)
root.mainloop()
