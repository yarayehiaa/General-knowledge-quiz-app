import socket
import json
import random
import threading

def load_questions():
    with open('Questions.json', 'r') as file:
        data = json.load(file)
        questions = data['question']
        answers = data['answer']
        options = data['options']
    return questions, answers, options

def select_random_questions(questions, answers, options):
    selected_data = []
    indices = random.sample(range(len(questions)), 5)  # Select 5 random indices
    for index in indices:
        question_data = {
            "question": questions[index],
            "options": options[index],
            "answer": answers[index]
        }
        selected_data.append(question_data)
    return selected_data

def handle_client(client_socket):
    # Load questions from JSON file
    questions, answers, options = load_questions()

    # Select random questions
    selected_data = select_random_questions(questions, answers, options)

    # Send selected questions to the client
    client_socket.sendall(json.dumps(selected_data).encode())

    current_question_index = 0

    while True:
        # Receive client's answer
        try:
            client_answer = client_socket.recv(4096).decode()
        except ConnectionAbortedError:
            print("Client disconnected.")
            break

        if not client_answer:
            break

        # Process client's answer
        question_data = selected_data[current_question_index]
        correct_answer = question_data["answer"]
        response = "Correct" if client_answer == str(correct_answer) else "Incorrect"

        # Send response to the client
        client_socket.sendall(response.encode())

        current_question_index += 1

    # Close the client socket
    client_socket.close()

def start_server():
    # Create a socket object
    host = ''
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((host, port))

    # Listen for client connections

    print("Server is listening on {}:{}".format(host, port))
    threads = []
    server_socket.listen(5)
    while True:

        # Accept a client connection
        client_socket, addr = server_socket.accept()
        print("Connection established with {}".format(addr))


        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        threads.append(client_thread)

start_server()
