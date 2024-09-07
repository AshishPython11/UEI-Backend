from dataclasses import fields
import json
import nltk
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import func
from flask import Blueprint, jsonify, request,current_app
from app import db, app, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity, jwt_required
from openai import OpenAI
from app.models.chatbot import *
from fuzzywuzzy import fuzz
import re
import os

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


# nlp = spacy.load("en_core_web_md")
# nlp = spacy.load("en_core_web_md")
# from sentence_transformers import SentenceTransformer
# Example of TfidfVectorizer and cosine_similarity usage
# vectorizer = TfidfVectorizer()
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# bert_model = SentenceTransformer('bert-base-nli-mean-tokens')
class ChatController:
    def __init__(self, api):
        self.api = api
        self.chat_model = self.api.model(
            "Chat",
            {
                "question": fields.String(required=True, description="Chat Question"),
                "prompt": fields.String(required=True, description="Chat Prompt"),
            },
        )
        self.chat_conversation_model = self.api.model(
            "ChatConversationData",
            {
                "question": fields.String(required=True, description="Chat Question"),
                "prompt": fields.String(required=True, description="Chat Prompt"),
            },
        )
        

        self.chat_ns = Namespace(
            "chat", description="Chat Data", authorizations=authorizations
        )
        self.chat_bp = Blueprint("chat", __name__)
        self.register_routes()
        # self.api.add_namespace(self.chat_ns)
        # self.api.init_app(self.chat_bp)

    def register_routes(self):
        @self.chat_ns.route("/chat")
        class ChatAdd(Resource):
            client = OpenAI(
                api_key=os.environ.get('API_KEY'),
            )

            def get_gpt3_prompt(self, prompt):
                gpt3_system_prompt = (
                    # f"Hi I am first_name last_name .Currenly I am studying at institution_name at address1,address2,city,district,state,country,pincode in course_name and persuing subject_name can you please provide question based on given course and subject_name"
                    # f"Please provide the answer to this question: '{prompt}'\n\n"
                    f"'{prompt}'\n\n"
                )

                return gpt3_system_prompt

            @self.chat_ns.doc("chat")
            @self.api.expect(self.chat_model)
            def post(self):
                try:
                    data = request.json
                    question = data.get("question")
                    prompt = data.get("prompt")
                    print(data)
                    if not question:
                        return jsonify(
                            {"message": "Please Provide Question", "status": 201}
                        )
                    if not prompt:
                        return jsonify({"message": "Please Provide Prompt", "status": 201})
                    else:
                        gpt3_system_prompt = self.get_gpt3_prompt(prompt)
                        conversation = [{"role": "system", "content": gpt3_system_prompt}]

                        # model_name = "gpt-3.5-turbo-1106"
                        model_name = "gpt-4"

                        try:
                            # response = self.client.chat.completions.create(
                            #     model=model_name,
                            #     response_format={"type": "text"},
                            #     messages=conversation,
                            #     temperature=0.5,
                            #     max_tokens=7895
                            # )
                            response = self.client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=conversation,
                                stream=True,
                            )
                            print(response)
                            # result = response.choices[0].message.content.strip()
                            result = []
                            for chunk in response:
                                if chunk.choices[0].delta.content is not None:
                                    result.append(chunk.choices[0].delta.content)
                            chatdata = {
                                "question": question,
                                "answer": result,
                                "prompt": prompt,
                            }
                        except Exception as e:
                            error_message = str(e)
                            logger.error("Error while calling GPT-3 API")
                            return jsonify(
                                {
                                    "message": "Error while calling GPT-3 API",
                                    "error": error_message,
                                    "status": 500,
                                }
                            )
                        logger.info("Answer getting successfully")
                        return jsonify(
                            {
                                "message": "Answer getting successfully",
                                "data": chatdata,
                                "status": 200,
                            }
                        )
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding  chat information: {str(e)}")
                        return jsonify({'message': 'Internal Server Error', 'status': 500})

        @self.chat_ns.route("/chatadd")
        class ChatbotAdd(Resource):
            client = OpenAI(
                api_key=os.environ.get('API_KEY'),
            )

            def get_similar_question(self, question, stream, course):
                # cached_responses = ChatCache.query.filter_by(
                #     student_stream=stream, student_course=course
                # ).all()
                cached_responses = ChatConversionData.query.all()
                for cached_response in cached_responses:
                    # similarity_question = fuzz.ratio(
                    #     question, cached_response.chat_question
                    # )
                    print("similarity_question >> ", cached_response.chat_question.strip().lower(),question.strip().lower())
                    if cached_response.chat_question.strip().lower()  == question.strip().lower():
                    # if similarity_question > 95:
                        logger.info(f"Found similar question: {cached_response.chat_question}")
                        return {
                            "cached_response": cached_response,
                            # "similarity": similarity_question,
                        }
                return None

            def get_gpt3_prompt(self, prompt):
                gpt3_system_prompt = (
                    # f"Hi I am first_name last_name .Currenly I am studying at institution_name at address1,address2,city,district,state,country,pincode in course_name and persuing subject_name can you please provide question based on given course and subject_name"
                    # f"Please provide the answer to this question: '{prompt}'\n\n"
                    f"'{prompt}'\n\n"
                )

                return gpt3_system_prompt

            def extract_between_words(self, input_string, start_word, end_word):
                pattern = re.compile(
                    rf"{re.escape(start_word)}\s+(.*?)\s+{re.escape(end_word)}",
                    re.IGNORECASE,
                )
                match = pattern.search(input_string)
                if match:
                    return match.group(1)
                else:
                    return None
            def contains_greeting(self, text):
                greetings = ["hi", "hello", "hey", "howdy", "greetings", "good morning", "good afternoon", "good evening"]
                normalized_text = text.lower()  
                for greeting in greetings:
                    if greeting in normalized_text:
                        return True
                return False
            def should_store_response(self, question, response):
                if self.contains_greeting(question):
                    return False
                return True
            
            def contains_exclusion(self, text):
                exclusion_statement1 = "I 'm sorry"
                exclusion_statement2='I apologize'
                text = ' '.join(text)
                text_lower = text.lower()
                print(text)
                exclusion_statement2=exclusion_statement2.lower()
                exclusion_lower1 = exclusion_statement1.lower()
                if exclusion_lower1 in text_lower:
                    print("hello")
                    return False 
                elif exclusion_statement2 in text_lower:
                    print("hello2")
                    return False
                else:
                    return True

            @self.chat_ns.doc("chatadd")
            @self.api.expect(self.chat_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    question = data.get("question")
                    prompt = data.get("prompt")
                    course = data.get("course")
                    stud_stream = data.get("stream")
                    chat_history = data.get("chat_history", []) 
                    current_user_id = get_jwt_identity()
                    print("stream >> ", stud_stream)
                    start_word = "provide"
                    end_word = "based"

                    # question = self.extract_between_words(prompt, start_word, end_word)
        
                    base_prompt = """You are an expert student helpdesk worker with knowledge in every field of study. 
                    Your role is to assist students with their queries. If a question falls outside the scope of their curriculum and curriculum's subject, 
                    DO NOT provide answer. politely inform them that the question is beyond their syllabus. 
                    Explain that the topic is outside the student's provided subject. 
                    Your responses should be detailed and informative, covering various aspects of the asked topic.
                    
                    If aked about you details, tell them that you are 'AI created by gyan setu'"""

                    criteria = f". Provide your answers based on '{course}' course and '{stud_stream}' subject only."
                    # prompt = prompt.replace(question, "answer")
                    prompt += criteria
                    # print('prompt',prompt)

                    similar_question = self.get_similar_question(
                        question, stud_stream, course
                    )
                    print("similar_question",similar_question)
                    # if similar_question and similar_question["similarity"] > 95:
                    if similar_question:
                        cached_response = similar_question["cached_response"]
                        return jsonify(
                            {
                                "message": "Answer retrieved from similar question in cache",
                                "data": {
                                    "question": question,
                                    "answer": cached_response.response,
                                    "prompt": prompt,
                                },
                                "status": 200,
                            }
                        )

                    if not question:
                        logger.warning("Missing question")
                        return jsonify(
                            {"message": "Please Provide Question", "status": 201}
                        )
                    if not prompt:
                        logger.warning("Missing prompt")
                        return jsonify({"message": "Please Provide Prompt", "status": 201})

                    gpt3_system_prompt = self.get_gpt3_prompt(base_prompt)

                    conversation = [
                        {"role": "system", "content": gpt3_system_prompt},
                        {
                            "role": "assistant",
                            "content": "Hi Student, Please share your information and field of intrest or course yo are persuing.",
                        },
                        {"role": "user", "content": prompt},
                        {
                            "role": "assistant",
                            "content": "What would you like to know related to your subject of intrest?",
                        },
                        # {"role": "user", "content": question},
                    ]
                    
                    conversation.extend([{"role": history["role"], "content": history["content"]} for history in chat_history])

                    conversation.append({"role": "user", "content": question})
                    
                    model_name = "gpt-3.5-turbo-1106"
                    # model_name = "gpt-4"
                    # print("convo >> ", conversation)

                    try:
                        # response = self.client.chat.completions.create(
                        #     model=model_name,
                        #     response_format={"type": "text"},
                        #     messages=conversation,
                        #     temperature=0.5,
                        #     max_tokens=7895
                        # )
                        stream = self.client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=conversation,
                            # stream=True,
                            max_tokens=2048,  # Set the desired response length here
                            temperature=0.7,
                            n=1,
                            stop=None,
                        )
                        print('streamccccccc', type(stream))
                        filtered_responses = None  # Initialize to None or appropriate default value

                        # Assuming `stream` is your `ChatCompletion` object
                        if hasattr(stream, 'choices') and len(stream.choices) > 0:
                            message = stream.choices[0].message
                            filtered_responses = message.content if hasattr(message, 'content') else None
                        print('filtered_response',filtered_responses)
                        if not filtered_responses:
                            return jsonify({'message': 'No relevant answer found', 'status': 404})
                        response_array = filtered_responses.split(' ')
                        if self.should_store_response(question, filtered_responses) and self.contains_exclusion(filtered_responses):
                            new_chat_entry = ChatConversionData(
                                chat_question=question,
                                student_id=current_user_id,
                                response=filtered_responses,  # Store the single relevant response
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                is_deleted=False
                            )
                            db.session.add(new_chat_entry)
                            db.session.commit()
                            logger.info(f"GPT-3 response stored successfully for question: {question}")
                        return jsonify({
                            'message': 'Answer stored successfully',
                            'data': {
                                'question': question,
                                # 'answer': '\n'.join(filtered_responses),
                                # 'answer': filtered_responses,
                                'answer': response_array,
                                'prompt': prompt,
                            },
                            'status': 200,
                        })
                        
                        response_data= []
                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                response_data.append(chunk.choices[0].delta.content)

                                # print(stream)
                                # result = response.choices[0].message.content.strip()
                                
                        new_cache_entry = ChatCache(
                            student_stream=stud_stream,
                            student_course=course,
                            chat_question=question,
                            response=response_data,
                        )
                        db.session.add(new_cache_entry)
                        db.session.commit()

                        chatdata = {
                            "question": question,
                            "answer": response_data,
                            "prompt": prompt,
                        }
                    except Exception as e:
                        logger.error(f"Error in post method: {str(e)}")
                        error_message = str(e)
                        return jsonify(
                            {
                                "message": "Error while calling GPT-3 API",
                                "error": error_message,
                                "status": 500,
                            }
                        )

                    return jsonify(
                        {
                            "message": "Answer getting successfully",
                            "data": chatdata,
                            "status": 200,
                        }
                    )
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding  chat information: {str(e)}")
                        return jsonify({'message': 'Internal Server Error', 'status': 500})
        
        @self.chat_ns.route("/chatconversation")
        
        class ChatAdd(Resource):
            client = OpenAI(
                api_key=os.environ.get('API_KEY'),)

            def get_gpt3_prompt(self, prompt):
                gpt3_system_prompt = f"'{prompt}'\n\n"
                return gpt3_system_prompt
 

            def contains_greeting(self, text):
                greetings = ["hi", "hello", "hey", "howdy", "greetings", "good morning", "good afternoon", "good evening"]
                normalized_text = text.lower()  
                for greeting in greetings:
                    if greeting in normalized_text:
                        return True
                return False
            def should_store_response(self, question, response):
                if self.contains_greeting(question):
                    return False
                return True
            
            def contains_exclusion(self, text):
                exclusion_statements = ["I'm sorry", "I apologize","However,I don't have real time access","As an AI created by gyan setu, my responses are based on the 'BE' course and 'Python' subject only.","I'm unable to provide a detailed answer for this topic."]
                normalized_text = text.lower()
                for statement in exclusion_statements:
                    if statement.lower() in normalized_text:
                        return False
                return True
            @self.api.expect(self.chat_conversation_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    question = data.get('question')
                    prompt = data.get('prompt')
                    current_user_id = get_jwt_identity()
                    if not question:
                        return jsonify({'message': 'Please provide a question', 'status': 400})

                    if not prompt:
                        return jsonify({'message': 'Please provide a prompt', 'status': 400})

                    gpt3_system_prompt = self.get_gpt3_prompt(prompt)
                    conversation = [{'role': 'system', 'content': gpt3_system_prompt}]

                    model_name = 'gpt-3.5-turbo'
                    try:
                        response = self.client.chat.completions.create(
                            model=model_name,
                            messages=conversation,
                            stream=True,
                            max_tokens=2048,  # Set the desired response length here
                            temperature=0.7,
                            n=1,
                            stop=None,
                        )

                        filtered_responses = []
                        for chunk in response:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content.strip()
                                if not self.contains_greeting(content):
                                # if 'greeting' not in content.lower() and 'hello' not in content.lower():
                                    filtered_responses.append(content)
                        
                        if not filtered_responses:
                            logger.warning("No relevant answer found")
                            return jsonify({'message': 'No relevant answer found', 'status': 404})
                        
                        # Store only the first relevant response, assuming it's the most relevant
                        # answer = filtered_responses[0]
                        if self.should_store_response(question, filtered_responses) and self.contains_exclusion(filtered_responses):
                            new_chat_entry = ChatConversionData(
                                chat_question=question,
                                student_id=current_user_id,
                                response=filtered_responses,  # Store the single relevant response
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                is_deleted=False
                            )
                            db.session.add(new_chat_entry)
                            db.session.commit()
                        logger.info("Answer stored successfully")
                        return jsonify({
                            'message': 'Answer stored successfully',
                            'data': {
                                'question': question,
                                # 'answer': '\n'.join(filtered_responses),
                                'answer': filtered_responses,
                                'prompt': prompt,
                            },
                            'status': 200,
                        })

                    except Exception as e:
                        error_message = str(e)
                        logger.error("Error while calling GPT-3 API")
                        return jsonify({
                            'message': 'Error while calling GPT-3 API',
                            'error': error_message,
                            'status': 500,
                        })
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding  chat information: {str(e)}")
                        return jsonify({'message': 'Internal Server Error', 'status': 500})
        
        @self.chat_ns.route('/api/chat-count/<int:student_id>')
        class GetChatCount(Resource):
            def get(self,student_id):
                try:
                    logger.info(f"Chat count for student_id {student_id}: {chat_count}")
                    chat_count = ChatConversionData.query.filter_by(is_deleted=False).filter_by(student_id=student_id).count()

                    return jsonify({'student_id': student_id, 'chat_count': chat_count,'status': 200})

                except Exception as e:
                    logger.error(f"Error occurred in GetChatCount: {str(e)}")
                    return jsonify({'message': 'Error occurred', 'error': str(e),'status': 500})

        # @self.chat_ns.route("/chat/fetch-or-generate", methods=["POST"])    
        # class FetchOrGenerateChat(Resource):
        #     client = OpenAI(
             #   api_key=os.environ.get('API_KEY'),
        #     )
        #     executor = ThreadPoolExecutor()
        #     # bert_model = SentenceTransformer('bert-base-nli-mean-tokens')
        #     nlp = spacy.load("en_core_web_lg")
        #     stop_words = set(stopwords.words('english'))
        #     lemmatizer = WordNetLemmatizer()
        #     unwanted_phrases = [
        #         "what can you tell me about",
        #         "can you tell me about",
        #         "brief explanation",
        #         "explain",
        #         "define",
        #         "tell me about",
        #         "something about",
        #         "what is"
        #     ]
        #     def preprocess_text(self, text):
        #         for phrase in self.unwanted_phrases:
        #             text = text.replace(phrase, "")
        #         tokens = word_tokenize(text.lower())
        #         tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalnum() and token not in self.stop_words]
        #         return tokens
        #         # return text.lower().strip()
        #         # tokens = word_tokenize(text.lower())
        #         # tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalnum() and token not in self.stop_words]
        #         # return tokens

        #         # def calculate_similarity(self, text1, text2):
        #         #     tokens1 = self.preprocess_text(text1)
        #         #     tokens2 = self.preprocess_text(text2)

        #         #     synset_scores = []
        #         #     for token1 in tokens1:
        #         #         synsets1 = self.get_synsets(token1)
        #         #         for token2 in tokens2:
        #         #             synsets2 = self.get_synsets(token2)
        #         #             max_score = 0
        #         #             for synset1 in synsets1:
        #         #                 for synset2 in synsets2:
        #         #                     score = synset1.wup_similarity(synset2)
        #         #                     if score:
        #         #                         max_score = max(max_score, score)
        #         #             synset_scores.append(max_score)
                    
        #         #     if synset_scores:
        #         #         average_score = sum(synset_scores) / len(synset_scores)
        #         #     else:
        #         #         average_score = 0.0
        #         #     print(average_score)
        #         #     return average_score
        #             # text1_embedding = self.bert_model.encode([text1])
        #             # text2_embedding = self.bert_model.encode([text2])
        #             # similarity_score = cosine_similarity(text1_embedding, text2_embedding)[0][0]
        #             # print(similarity_score)
        #             # return float(similarity_score) 
        #             # text1_embedding = self.get_embedding(text1)
        #             # text2_embedding = self.get_embedding(text2)
                    
        #             # similarity_score = cosine_similarity([text1_embedding], [text2_embedding])[0][0]
        #             # print(similarity_score)
        #             # return float(similarity_score)
        #     def get_synsets(self, word):
        #         synsets = wordnet.synsets(word)
        #         return synsets
        #     def get_embedding(self,text):
        #         doc = self.nlp(text)
        #         return doc.vector
        #         # text = text.replace("\n", " ")
        #         # response = self.client.embeddings.create(input=[text], model="text-embedding-ada-002")
        #         # embedding = response.data[0].embedding
        #         # return embedding

            
            
        #     def parse_response_string(self, response_string):
        
        #         cleaned_string = response_string.strip('{}"')
                
        #         cleaned_string = cleaned_string.replace('\"', ',')
                
        #         words = [word.strip() for word in cleaned_string.split(',') if word.strip()]
        #         return words
        #     def extract_keywords(self, text):
        #         return self.preprocess_text(text)
        #     def get_similar_question(self, question):
        #         question_keywords = self.extract_keywords(question)
        #         cached_responses = ChatConversionData.query.filter(
        #             ChatConversionData.is_deleted == False
        #         ).all()

        #          # for cached_response in cached_responses:
        #         for response in cached_responses:
        #             stored_question_keywords = self.extract_keywords(response.chat_question)
        #             if any(keyword in stored_question_keywords for keyword in question_keywords):
                         

        #                 return response
        #         return None
            
                
        #     def get_gpt3_prompt(self, prompt):
        #         gpt3_system_prompt = f"'{prompt}'\n\n"
        #         return gpt3_system_prompt

        #     def extract_between_words(self, input_string, start_word, end_word):
        #         pattern = re.compile(
        #             rf"{re.escape(start_word)}\s+(.*?)\s+{re.escape(end_word)}",
        #             re.IGNORECASE,
        #         )
        #         match = pattern.search(input_string)
        #         if match:
        #             return match.group(1)
        #         else:
        #             return None

        #     def contains_greeting(self, text):
        #         greetings = [
        #             "hi", "hello", "hey", "howdy", "greetings",
        #             "good morning", "good afternoon", "good evening"
        #         ]
        #         normalized_text = text.lower()  
        #         for greeting in greetings:
        #             if greeting in normalized_text:
        #                 return True
        #         return False

        #     def should_store_response(self, question, response):
        #         if self.contains_greeting(question):
        #             return False
        #         return True

        #     def contains_exclusion(self, text):
        #         exclusion_statements = ["I'm sorry", "I apologize","However,I don't have real time access","As an AI created by gyan setu, my responses are based on the 'BE' course and 'Python' subject only.","I'm unable to provide a detailed answer for this topic."]
        #         normalized_text = text.lower()
        #         for statement in exclusion_statements:
        #             if statement.lower() in normalized_text:
        #                 return False
        #         return True
            
        #     @self.api.expect(self.chat_model)
        #     @jwt_required()
        #     def post(self):
        #         data = request.json
        #         question = data.get("question")
        #         prompt = data.get("prompt")
        #         course = data.get("course")
        #         stud_stream = data.get("stream")
        #         chat_history = data.get("chat_history", []) 
        #         current_user_id = get_jwt_identity()

        #         base_prompt = """You are an expert student helpdesk worker with knowledge in every field of study. 
        #         Your role is to assist students with their queries.If a question falls outside the scope of their curriculum and curriculum's subject, 
        #         DO NOT provide answer. Politely inform them that the question is beyond their syllabus. 
        #         Explain that the topic is outside the student's provided subject.
        #         Your responses should be detailed and informative, covering various aspects of the asked topic.
                
        #         If asked about you details, tell them that you are 'AI created by gyan setu'"""

        #         criteria = f". Provide your answers based on '{course}' course and '{stud_stream}' subject only."
        #         prompt += criteria

        #         # Check if question is in cache
        #         start_time = time.time()
        #         cached_response = self.get_similar_question(question)
        #         end_time = time.time()
        #         retrieval_time = end_time - start_time
        #         print(retrieval_time)
        #         if cached_response:
        #             response_string = cached_response.response  # Access the response attribute
        #             if response_string.startswith('{\"') and response_string.endswith('}'):
        #                     response_array = self.parse_response_string(response_string)
        #             else:
        #                 response_array = cached_response.response.split(' ')
        #             return jsonify({
        #                 'message': 'Answer retrieved from similar question in cache',
        #                 'status':200,
        #                 'data': {
        #                     'question': question,
        #                     # 'answer': cached_response["response"],
        #                     'answer': response_array,
        #                     'prompt': prompt,
        #                     }
                        
        #             })
                     

        #         # If not found in cache, proceed with GPT-3 query
        #         gpt3_system_prompt = self.get_gpt3_prompt(base_prompt)

        #         conversation = [
        #             {"role": "system", "content": gpt3_system_prompt},
        #             {
        #                 "role": "assistant",
        #                 "content": "Hi Student, Please share your information and field of interest or course you are pursuing.",
        #             },
        #             {"role": "user", "content": prompt},
        #             {
        #                 "role": "assistant",
        #                 "content": "What would you like to know related to your subject of interest?",
        #             },
        #         ]

        #         conversation.extend([
        #             {"role": history["role"], "content": history["content"]} for history in chat_history
        #         ])

        #         conversation.append({"role": "user", "content": question})

        #         model_name = "gpt-3.5-turbo-1106"

        #         try:
        #             start_time = time.time()
        #             stream = self.client.chat.completions.create(
        #                 model=model_name,
        #                 messages=conversation,
        #                 max_tokens=2048,
        #                 temperature=0.7,
        #                 n=1,
        #                 stop=None,
        #             )
        #             end_time = time.time()
        #             execution_time = end_time - start_time
        #             print(execution_time)
        #             filtered_responses = None

        #             if hasattr(stream, 'choices') and len(stream.choices) > 0:
        #                 message = stream.choices[0].message
        #                 filtered_responses = message.content if hasattr(message, 'content') else None
                    
        #             if not filtered_responses:
        #                 return jsonify({'message': 'No relevant answer found', 'status': 404})

        #             if self.should_store_response(question, filtered_responses) and self.contains_exclusion(filtered_responses) and not cached_response:
        #                 new_chat_entry = ChatConversionData(
        #                     chat_question=question,
        #                     student_id=current_user_id,
        #                     response=filtered_responses,
        #                     created_at=datetime.now(),
        #                     updated_at=datetime.now(),
        #                     is_deleted=False
        #                 )
        #                 db.session.add(new_chat_entry)
        #                 db.session.commit()

        #             response_array = filtered_responses.split(' ')
        #             return jsonify({
        #                 'message': 'Answer stored successfully',
        #                 'status':200,
        #                 'data': {
        #                     'question': question,
        #                     'answer': response_array,
        #                     'prompt': prompt,
        #                    }
                        
        #             })

        #         except Exception as e:
        #             error_message = str(e)
        #             return jsonify(
        #                 {
        #                     "message": "Error while calling GPT-3 API",
        #                     "error": error_message,
        #                     "status": 500,
        #                 }
        #             )
        @self.chat_ns.route("/fetch-from-db", methods=["POST"])
        class FetchChat(Resource):
            
            stop_words = set(stopwords.words('english'))
            lemmatizer = WordNetLemmatizer()
            general_keywords = {"python", "java", "programming", "language"}
            unwanted_phrases = [
                "what can you tell me about",
                "can you tell me about",
                "brief explanation",
                "explain",
                "define",
                "tell me about",
                "something about",
                "what is"
            ]
            def parse_response_string(self, response_string):
        
                cleaned_string = response_string.strip('{}"')
                
                cleaned_string = cleaned_string.replace('\"', ',')
                
                words = [word.strip() for word in cleaned_string.split(',') if word.strip()]
                return words

            def preprocess_text(self, text):
                for phrase in self.unwanted_phrases:
                    text = text.replace(phrase, "")
                tokens = word_tokenize(text.lower())
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalnum() and token not in self.stop_words]
                return tokens

            def extract_keywords(self, text):
                return self.preprocess_text(text)

            def get_similar_question(self, question):
                question_keywords = self.extract_keywords(question)
                if not question_keywords:
                    return "No relevant data available."

                cached_responses = ChatConversionData.query.filter(
                    ChatConversionData.is_deleted == False
                ).all()

                best_response = None
                best_score = 0
                minimum_score_threshold = 1  # Allow for at least one specific keyword match

                for response in cached_responses:
                    stored_question_keywords = self.extract_keywords(response.chat_question)
                    match_count = 0
                    general_keyword_present = False

                  
                    for keyword in question_keywords:
                        if keyword in stored_question_keywords:
                            match_count += 1
                            if keyword in self.general_keywords:
                                general_keyword_present = True

                   
                    if match_count == len(question_keywords):
                        score = match_count

                        if score > best_score or (score == best_score and not general_keyword_present):
                            best_score = score
                            best_response = response

              
                if best_score >= minimum_score_threshold:
                    return best_response
                else:
                    return None
                # question_keywords = self.extract_keywords(question)
                # cached_responses = ChatConversionData.query.filter(
                #     ChatConversionData.is_deleted == False
                # ).all()

                # for response in cached_responses:
                #     stored_question_keywords = self.extract_keywords(response.chat_question)
                #     if any(keyword in stored_question_keywords for keyword in question_keywords):
                #         return response
                # return None

            @self.api.expect(self.chat_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    question = data.get("question")
                    
                    cached_response = self.get_similar_question(question)
                    if cached_response:
                        response_string = cached_response.response  # Access the response attribute
                        if response_string.startswith('{\"') and response_string.endswith('}'):
                                response_array = self.parse_response_string(response_string)
                        else:
                            response_array = cached_response.response.split(' ')
                        return jsonify({
                            'message': 'Answer retrieved from similar question in cache',
                            'status':200,
                            'data': {
                                'question': question,
                                # 'answer': cached_response["response"],
                                'answer': response_array,
                                # 'prompt': prompt,
                                }
                            
                        })
                    else:
                        return jsonify({
                            'message': 'No similar question found in cache',
                            'status': 404
                        })
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding  chat information: {str(e)}")
                        return jsonify({'message': 'Internal Server Error', 'status': 500})
        @self.chat_ns.route("/generate-from-api", methods=["POST"])
        class GenerateChat(Resource):
            client = OpenAI(
                api_key=os.environ.get('API_KEY'),
            )

            def get_gpt3_prompt(self, prompt):
                gpt3_system_prompt = f"'{prompt}'\n\n"
                return gpt3_system_prompt

            def should_store_response(self, question, response):
                if self.contains_greeting(question):
                    return False
                return True

            def contains_greeting(self, text):
                greetings = [
                    "hi", "hello", "hey", "howdy", "greetings",
                    "good morning", "good afternoon", "good evening"
                ]
                normalized_text = text.lower()  
                for greeting in greetings:
                    if greeting in normalized_text:
                        return True
                return False

            def contains_exclusion(self, text):
                exclusion_statements = ["I'm sorry", "I apologize","However,I don't have real time access","As an AI created by gyan setu, my responses are based on the 'BE' course and 'Python' subject only.","I'm unable to provide a detailed answer for this topic."]
                normalized_text = text.lower()
                for statement in exclusion_statements:
                    if statement.lower() in normalized_text:
                        return False
                return True

            @self.api.expect(self.chat_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    question = data.get("question")
                    prompt = data.get("prompt")
                    course = data.get("course")
                    stud_stream = data.get("stream")
                    chat_history = data.get("chat_history", [])
                    current_user_id = get_jwt_identity()

                    base_prompt = """You are an expert student helpdesk worker with knowledge in every field of study. 
                    Your role is to assist students with their queries.If a question falls outside the scope of their curriculum and curriculum's subject, 
                    DO NOT provide answer. Politely inform them that the question is beyond their syllabus. 
                    Explain that the topic is outside the student's provided subject.
                    Your responses should be detailed and informative, covering various aspects of the asked topic.

                    If asked about you details, tell them that you are 'AI created by gyan setu'"""

                    criteria = f". Provide your answers based on '{course}' course and '{stud_stream}' subject only."
                    prompt += criteria

                    gpt3_system_prompt = self.get_gpt3_prompt(base_prompt)

                    conversation = [
                        {"role": "system", "content": gpt3_system_prompt},
                        {
                            "role": "assistant",
                            "content": "Hi Student, Please share your information and field of interest or course you are pursuing.",
                        },
                        {"role": "user", "content": prompt},
                        {
                            "role": "assistant",
                            "content": "What would you like to know related to your subject of interest?",
                        },
                    ]

                    conversation.extend([
                        {"role": history["role"], "content": history["content"]} for history in chat_history
                    ])

                    conversation.append({"role": "user", "content": question})

                    model_name = "gpt-3.5-turbo-1106"

                    try:
                        start_time = time.time()
                        stream = self.client.chat.completions.create(
                            model=model_name,
                            messages=conversation,
                            max_tokens=2048,
                            temperature=0.7,
                            n=1,
                            stop=None,
                        )
                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(execution_time)
                        filtered_responses = None

                        if hasattr(stream, 'choices') and len(stream.choices) > 0:
                            message = stream.choices[0].message
                            filtered_responses = message.content if hasattr(message, 'content') else None

                        if not filtered_responses:
                            return jsonify({'message': 'No relevant answer found', 'status': 404})

                        if self.should_store_response(question, filtered_responses) and self.contains_exclusion(filtered_responses):
                            new_chat_entry = ChatConversionData(
                                chat_question=question,
                                student_id=current_user_id,
                                response=filtered_responses,
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                is_deleted=False
                            )
                            db.session.add(new_chat_entry)
                            db.session.commit()

                        response_array = filtered_responses.split(' ')
                        logger.info("Answer generated and stored successfully")
                        return jsonify({
                            'message': 'Answer generated and stored successfully',
                            'status': 200,
                            'data': {
                                'question': question,
                                'answer': response_array,
                                'prompt': prompt,
                            }
                        })

                    except Exception as e:
                        error_message = str(e)
                        logger.error("Error while calling GPT-3 API")
                        return jsonify(
                            {
                                "message": "Error while calling GPT-3 API",
                                "error": error_message,
                                "status": 500,
                            }
                        )
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding  chat information: {str(e)}")
                        return jsonify({'message': 'Internal Server Error', 'status': 500})
        @self.chat_ns.route('/store')
        class StoreChat(Resource):
            @self.chat_ns.doc('store_chat', security='jwt')
            @self.chat_ns.expect(self.chat_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    chat_question = data.get('chat_question')
                    response = data.get('response')

                    if not student_id or not chat_question or not response:
                        return {'message': 'Invalid data provided', 'status': 400}, 400

                    chat_data = ChatConversionData(
                        student_id=student_id,
                        chat_question=chat_question,
                        response=response
                    )

                    db.session.add(chat_data)
                    db.session.commit()
                    logger.info("Chat data stored successfully")
                    return {'message': 'Chat data stored successfully', 'status': 201}
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding  chat information: {str(e)}")
                        return jsonify({'message': 'Internal Server Error', 'status': 500})

                                
                       


        self.api.add_namespace(self.chat_ns)
