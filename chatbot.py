import time

import numpy as np
import openai
from questionanswer import questions, questions_embeddings, answers

openai.api_key = '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'


class chatBot:
    def __init__(self):
        self.received_answer = ''
        self.received_question = ''

    def get_openai_embedding(self, text):
        self.received_question = text
        resp = openai.Embedding.create(
            input=text,
            engine="text-similarity-davinci-001",
            max_tokens=128,
            n=1,
            stop=None,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
        return resp['data'][0]


    def get_answer(self, user_question):
        user_question_embedding = self.get_openai_embedding([user_question])['embedding']
        similarity_scores = np.dot(questions_embeddings, user_question_embedding)
        most_similar_index = np.argmax(similarity_scores)
        if np.max(similarity_scores) < 0.8:
            self.received_answer = "Iam sorry! could you please rephrase the question"
        else:
            most_similar_question = questions[most_similar_index]
            supported_answer = answers[most_similar_index]
            self.received_answer = supported_answer
        return self.received_answer

