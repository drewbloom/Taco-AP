import streamlit as st
from pathlib import Path
import json

class Assistant:

    def __init__(self, client):
        """
        Initializes the assistant with the given AI client and settings. Also initializes necessary session state keys for this class

        Args:
            client: The AI client (OpenAI, etc.) that handles chat and function calls.
            system_message: Default system message to provide context to the assistant.
            model (str): The AI model identifier to be used for generating responses.
        """

        self.client = client # currently OpenAI client, but could pass a different client from app.py
        
        # Offer UI dropdown for selecting a model and set model based on user selection
        self.model = "4o-mini" # can set model needed - will set default and allow user to pick others
        self.models = {"Instant Taco (Fastest)": "4o-mini", "Taco Supreme (Best Writing)": "4o", "Street Taco (Can Think)": "o3-mini"}
        st.session_state.model_selected = st.session_state.get('model_selected', None)

        self.vector_stores = {
            "AP World History": "vs_lu6EGQwhpKqUAyOXQrZammXo",
            "AP Human Geography": "",
            "AP US History": ""
                              }
        st.session_state.vector_store_selected = st.session_state.get('vector_store_selected', None)
        # Add vs files to session state so they can be retrieved when vs selected
        st.session_state.vector_store_files = st.session_state.get('vector_store_files', [])

        # Add tracker for local files for edit_file use
        st.session_state.session_files = st.session_state.get('session_files', [])

        st.session_state.modality = st.session_state.get('modality', None)
        self.modality = st.session_state.modality

        st.session_state.modality_change = st.session_state.get('modality_change', False)

        self.new_message = False
        self.text_response = ""

        # Define base system message
        self.system_message = """Welcome to Your AP Course Review Assistant!

Hello, and welcome! I'm here to help you with your studies. To get started, simply pick a course from the list on the left. Once you've selected your course, you'll be able to choose from various models to best suit your needs.

You can interact with me in two ways:

Text: Just type your questions, and I'll respond with helpful information and guidance.

Talk: Feel free to talk to me! I’ll listen and reply just like I would in a conversation.

Whether you're preparing for an exam, need help with course content, or just want to practice, I’m here to assist. Let’s make your learning experience enjoyable and efficient. Choose your course, and let's get started!"""


        st.session_state.system_message = st.session_state.get('system_message', self.system_message)
        # Define system messages for each course type
        self.system_messages = {
            "AP World History": """You are an expert AP World History teacher preparing students for the AP Test. Students can come to you with questions or pick from prewritten prompts that guide them in study sessions, focusing on writing practice, course content, or multiple-choice practice. You have access to a vector store containing the AP World History: Modern Course and Exam Description, which outlines the content covered by the course, the thinking and analytical skills necessary to synthesize and communicate knowledge on the test, and samples of multiple-choice (MCQ), short-answer (SAQ), document-based (DBQ), and long-essay (LEQ) questions. These questions comprise the exam.

You should use your file search tool to help you gain the necessary context to assist students with their requests. In addition, when suitable, you may search online to provide supplementary resources such as practice examples, explanations, or trusted content from educational platforms. For example, you can link students to Heimler's History, a YouTube series that is excellent for reviewing AP World History content, or other trustworthy educational sites.

Remember to be helpful and empathetic, providing simple answers while diving deeper into concepts to assist students in improving their writing. Offer constructive criticism regarding their reasoning, use of evidence, and other exam-related indicators. You will sometimes be asked to create practice questions — when writing or multiple-choice, default to providing one prompt or question at a time to help students focus and receive targeted feedback.

You may alter your instructions to fit student study requests, as long as you do not speak unkindly or cause harm. Take a deep breath and provide an excellent review experience using your vector store, educational expertise, and the power of trusted online resources.""",
            "AP Human Geography": """You are an expert AP Human Geography teacher preparing students for the AP Test. Students can come to you with questions or pick from prewritten prompts that guide them in study sessions, focusing on writing practice, course content, or multiple-choice practice. You have access to a vector store containing the AP Human Geography: Modern Course and Exam Description, which outlines the content covered by the course, the thinking and analytical skills necessary to synthesize and communicate knowledge on the test, and samples of multiple-choice (MCQ), short-answer (SAQ), document-based (DBQ), and long-essay (LEQ) questions. These questions comprise the exam.

You should use your file search tool to help you gain the necessary context to assist students with their requests. In addition, when suitable, you may search online to provide supplementary resources such as practice examples, explanations, or trusted content from educational platforms. For example, you can link students to Heimler's History, a YouTube series that is excellent for reviewing AP Human Geography content, or other trustworthy educational sites.

Remember to be helpful and empathetic, providing simple answers while diving deeper into concepts to assist students in improving their writing. Offer constructive criticism regarding their reasoning, use of evidence, and other exam-related indicators. You will sometimes be asked to create practice questions — when writing or multiple-choice, default to providing one prompt or question at a time to help students focus and receive targeted feedback.

You may alter your instructions to fit student study requests, as long as you do not speak unkindly or cause harm. Take a deep breath and provide an excellent review experience using your vector store, educational expertise, and the power of trusted online resources.""",
            "AP US History": """You are an expert AP US History teacher preparing students for the AP Test. Students can come to you with questions or pick from prewritten prompts that guide them in study sessions, focusing on writing practice, course content, or multiple-choice practice. You have access to a vector store containing the AP US History: Modern Course and Exam Description, which outlines the content covered by the course, the thinking and analytical skills necessary to synthesize and communicate knowledge on the test, and samples of multiple-choice (MCQ), short-answer (SAQ), document-based (DBQ), and long-essay (LEQ) questions. These questions comprise the exam.

You should use your file search tool to help you gain the necessary context to assist students with their requests. In addition, when suitable, you may search online to provide supplementary resources such as practice examples, explanations, or trusted content from educational platforms. For example, you can link students to Heimler's History, a YouTube series that is excellent for reviewing AP US History content, or other trustworthy educational sites.

Remember to be helpful and empathetic, providing simple answers while diving deeper into concepts to assist students in improving their writing. Offer constructive criticism regarding their reasoning, use of evidence, and other exam-related indicators. You will sometimes be asked to create practice questions — when writing or multiple-choice, default to providing one prompt or question at a time to help students focus and receive targeted feedback.

You may alter your instructions to fit student study requests, as long as you do not speak unkindly or cause harm. Take a deep breath and provide an excellent review experience using your vector store, educational expertise, and the power of trusted online resources."""
        }

        # Host a series of prompts that help students review for each course
        self.prompts = {
            "Writing Practice": "Help the user practice their AP writing skills. You will lead the conversation and facilitate the learning by asking the student what they'd like to practice, then allowing the session to flow from there. Use your course and exam description to locate the main writing tasks and offer the student choices for which writing sections to practice. For example, AP World History has short-answer questions, document-based questions, and long-essay questions. By asking the user what they would like to focus on, you can help them by retrieving the writing requirements and scoring guidelines for that writing task. If the user asks for more general help, e.g. thesis writing, providing evidence, how much evidence to use, you can combine your tools along with your knowledge of the courses to help them. You should always rely on the course materials you have been given to guide students on writing. Do not rely on your knowledge of other kinds of writing to inform students, as AP courses often have their own, strict definitions of what writing should look like and how it should be scored. When in doubt, communicate that you are unsure and direct the student to their teacher. When possible, however, try to give the student feedback and support that will help them with their writing generally, even if those changes may not directly pertain to scoring guidelines that you have found for the course. Take a deep breath and begin by asking the student what kind of writing they'd like to work on with you.",
            
            
            "Multiple Choice Practice": """Help the user practice their AP multiple-choice skills.
You will guide the conversation and facilitate the learning by asking the student what kind of AP multiple-choice practice they would like to focus on. Start by offering a brief explanation of the types of content they might be practicing, such as historical quotes, excerpts from historians, or images related to the course material. You should use the AP course and exam description to locate the main topics and concepts relevant to the multiple-choice questions.

For example, AP World History might involve topics like significant historical events, key figures, or major thematic trends across time periods. Based on what the student wants to focus on, you can offer them choices that are consistent with the course content and relevant to the exam structure.

Once the student has selected an area to focus on, you will create multiple-choice questions by:

Using the course and exam description to guide question difficulty and topic selection.

Ensuring the questions are structured to match the difficulty and format of sample MCQs found in the course description documents.

Incorporating content such as historical quotes, historian excerpts, or relevant images/cartoons that help contextualize the material, whenever possible.

Retrieving historical quotes or images through internet searches (if necessary), while ensuring the content is appropriate, safe, and educational for high school students. Be sure to make clear which content comes from the internet, and do not use anything unsafe or inappropriate.

Your goal is to offer students practice that closely resembles what they will encounter on the exam. Always provide brief feedback after each question, explaining why the correct answer is right and why the distractors are not. This will help students improve their reasoning skills and understanding of the material.

If the student requests general guidance, such as how to approach answering multiple-choice questions or tips for studying, use the course materials and your knowledge of the AP exam to guide them. Be clear that you are using the AP guidelines, and direct them to their teacher if the question goes beyond what you can help with.

Take a deep breath and begin by asking the student what kind of multiple-choice practice they’d like to focus on!""",
            
            
            "Content Review": """Help the user review and study key concepts, topics, or units in the AP History course.
Begin by asking the student what specific area of the course they would like to review. This could be a broad concept, a specific event in history, a unit of study, or even connections between different regions and themes. Use your knowledge of the AP course content and your access to the course and exam descriptions to guide the student in focusing on the right materials.

For example, the student might want to understand the causes of a historical event, explore the effects of a particular movement, or dive deeper into the connections between different regions during a specific time period. After asking the student what they’d like to focus on, you will:

Retrieve the relevant materials from the course description and present them in a clear, structured manner.

Break down complex ideas into more digestible explanations. Use analogies, real-world examples, or simpler language to help students understand difficult concepts.

Clarify connections between topics. If the student is struggling to understand how different themes or regions are interconnected, take the time to explain those relationships. Use visuals, timelines, or comparative examples where possible to illustrate these links.

For instance, if the student is having difficulty understanding the connections between industrialization and the rise of imperialism, you could explain how one led to the other, using historical examples to make the link clearer. Use your knowledge of history and course materials to weave together these ideas in a way that’s engaging and easy to grasp.

Encourage the student to ask questions throughout the review process. If they are struggling with a particular idea, give them extra time to focus on that area, ensuring you don’t rush through the content. You might ask follow-up questions to help them think critically about the material and explore it more deeply.

Educational strategies to consider:

Analogies: When a student struggles to understand a complex concept, compare it to something they are more familiar with (e.g., comparing the rise of political ideologies in the 20th century to the emergence of different kinds of “teams” in a sport).

Simplification: Break down ideas into smaller, more manageable pieces. Use easy-to-understand definitions and concepts to build understanding before introducing more advanced terminology.

Comparisons: Use comparisons to help students see the connections between different regions, time periods, or historical events, illustrating how they are linked.

Visuals: If appropriate, provide links to visual aids like maps, charts, or infographics to help the student visualize connections or understand the material better.

Your goal is to help the student build a deeper, more nuanced understanding of the material. Use your access to course materials and your ability to explain difficult ideas in simpler terms to guide them through any confusion or uncertainty.

Take a deep breath, ask the student what they’d like to review, and help them dive deeper into the subject!"""
        }

        # Initialize a messages list
        st.session_state.messages = st.session_state.get('messages', [])


        # Define available tools for interaction

        self.tools = [
            {
                "type": "file_search",
                "vector_store_ids": [st.session_state.vector_store_selected],
                "max_num_results": 20
            },
            {
                "type": "web_search_preview"
            }
        ]

    def setup_ui(self):
        """Setup the user interface components for interaction."""
        st.title(":taco:Taco:taco: AP Review")
        st.sidebar.title(":material/mic: TacoTalk or TacoText :material/chat:")
        st.write("## Writing, Test Prep, Quizzes - Taco can help!")
        st.write("*Begin by choosing TacoTalk or TacoText and picking your course on the left*")

        new_modality = st.sidebar.selectbox(
            "Input Modality", ("Talk", "Text"), index=None, placeholder="How you'll talk to Taco", label_visibility="collapsed", key="modality"
        )
        
        if new_modality != self.modality:
            st.session_state["modality_change"] = True
            self.modality = new_modality


        # Place vector store region in sidebar below input type
        upload_widget = st.sidebar

        # AP Courses / Vector Stores
        upload_widget.title(':material/topic: Available Courses')
        vs_container = upload_widget.container()
        vs_selected = vs_container.selectbox(label=':material/left_click: Choose your course', index=0, options=self.vector_stores)
        if vs_selected != st.session_state.vector_store_selected:
            with st.spinner("Updating the AI for your course..."):
                st.session_state.vector_store_selected = vs_selected
                st.session_state.system_message_selected = self.system_messages.get(vs_selected, self.system_message)
                st.success(f"AI Updated for your course: {st.session_state.vector_store_selected}")

        # Study Suggestions (Prompts)
        if st.session_state.vector_store_selected:
            upload_widget.title("Study Suggestions")
            study_prompts = {
                "Writing Practice": "Practice essay writing: Short Answer, DBQs, Long Essays",
                "MCQ Practice": "Practice multiple-choice questions with real exam content",
                "Content Review": "Dive deeper into key historical concepts and connections"
            }
            selected_prompt = upload_widget.radio("Choose a prompt", options=study_prompts)

            # Displaying prompt descriptions on hover
            with st.sidebar:
                for prompt in study_prompts:
                    if st.button(prompt):
                        st.session_state.selected_prompt = prompt
                        # Send the prompt to AI for completion, but don't display it
                        self.handle_prompt_selection(prompt)        
        
        
        # Offer choice of AI Models
        st.sidebar.title(":material/smart_toy: Customize Tacos as needed")
        model_selection = st.sidebar.selectbox(label='Pick an AI model', options=self.models, index=0, label_visibility='collapsed')
        st.session_state.model_selection = model_selection


    def handle_input(self):
        """Handle user input based on selected modality (Text or Speech)."""
        if st.session_state["modality"] == "Text":
            self.handle_text_input()
        elif st.session_state["modality"] == "Talk":
            self.handle_speech_input()

    def handle_text_input(self):
        """Process text input from the user."""
        text_input = st.chat_input("Type your message", disabled=(self.modality != "Text"))
        if text_input and not self.new_message:
            st.session_state.messages.append({"role": "user", "content": text_input})
            self.new_message = True
            with st.chat_message("user"):
                st.markdown(text_input)

    def handle_speech_input(self):
        """Process speech input from the user."""
        audio_input = st.audio_input('Click the icon to start and stop recording', disabled=(self.modality != "Talk"))
        if audio_input and not self.new_message:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_input, response_format="text"
            )
            st.session_state.messages.append({"role": "user", "content": transcription})
            self.new_message = True
            with st.chat_message("user"):
                st.markdown(transcription)

    def stream_handler(self):
    
        for chunk in self.stream:
            try:
                if chunk.type == "response.output_text.delta":
                    yield chunk.delta
                
            except Exception as e:
                print(f"Error in stream: {e}")
                st.error(f"Error in stream: {e}")

    def generate_assistant_response(self):
        """Generate assistant's response using AI model."""

        if self.new_message:
            with st.chat_message("assistant"):

                # If stream is True, use the helper stream_handler()
                self.stream = self.client.responses.create(
                    model=self.model,
                    input=st.session_state.messages,
                    stream=True,
                    tools=self.tools,
                    truncation="auto"
                )
                
                
                response = self.stream_handler()
                final_response = st.write_stream(response)
                
                # Use a handler to yield text stream
                for text in self.stream_handler():
                   st.write_stream(text)
                # Add final response to messages list
                st.session_state.messages.append({"role": "assistant", "content": final_response})




                        

                

    def process_stream_placeholder(self, response):
            
            # Original logic for handling tools
            # may eliminate streaming to simplify responses.

            for chunk in response:
                tool_calls = None
                if chunk.choices[0].message.tool_calls is not None:
                    tool_calls = chunk.choices[0].message.tool_calls
                # Write message if no tool call

                if tool_calls is not None:
                    # You MUST append the tool call message as its native message object or OpenAI will throw errors
                    st.session_state.messages.append(response.choices[0].message)
                    
                    for tool_call in tool_calls:
                        func_name = tool_call.function.name
                        args = tool_call.function.arguments
                        args = json.loads(args)
                        tool_call_id = tool_call.id
                        
                        self.handle_function_input(
                            func_name,
                            args,
                            tool_call_id
                        )
                    self.tool_use_completion()


                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=st.session_state.messages,
                    stream=False,
                    tools=self.tools,
                )
                self.process_unstreamed_response(response)
                self.new_message = False

    def process_unstreamed_response(self, response):
        """
        Process AI model response, including any tool calls, and update messages.

        Args:
            response: The response object from the AI model.
        """
        tool_calls = None

        if response.choices[0].message.tool_calls is not None:
            tool_calls = response.choices[0].message.tool_calls
        
        # Debug
        print(f"Here is the full assistant response:\n>>>{response}")

        if tool_calls is not None:
            # You MUST append the tool call message as its native message object or OpenAI will throw errors
            st.session_state.messages.append(response.choices[0].message)
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                args = tool_call.function.arguments
                args = json.loads(args)
                tool_call_id = tool_call.id
                
                self.handle_function_input(
                    func_name,
                    args,
                    tool_call_id
                )
            self.tool_use_completion()
        else: # this doesn't work when called, bypassing in Tool Use Completion
            text_response = response.choices[0].message.content
            if text_response:
                st.markdown(text_response)
                st.session_state.messages.append({"role": "assistant", "content": text_response})
                self.text_response = text_response

    def handle_function_input(self, func_name, args, tool_call_id):
        """Handle a user input by making a request to the MicrosoftGraphAgent."""
        try:
            if func_name == 'call_graph_agent':
                st.markdown("Making a request to the Microsoft Graph Agent...")
                result = self.call_graph_agent(args.get('operator_request'))
                print(f"Here is the full call_graph_agent result:\n>>>{result}") #debug
                function_call_result_message = {"role": "tool", "content": str(result), "tool_call_id": tool_call_id}
                
                # Debug
                print(f"Here is the full function call result message:\n>>>{function_call_result_message}")
                
                st.session_state.messages.append(function_call_result_message)
        except Exception as e:
            st.error(f"Function call error: {e}")

    def tool_use_completion(self):
        """Generate a completion from the AI model after a tool use."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=st.session_state.messages,
                stream=False,
                tools=self.tools,
            )
            # Keep processing via recursion if agent wants to use tools again
            if response.choices[0].message.tool_calls is not None:
                self.process_unstreamed_response(response)

            elif response.choices[0].message.content is not None:
                st.session_state.messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
                print(f"Printing full messages from tool_use_completion:\n>>>{st.session_state.messages}")
                # Already inside an assistant message, can print content in markdown
                st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Tool use completion error: {e}")

    def display_messages(self):
        """Display all user and assistant messages to the chat interface."""
        # if st.session_state["modality_change"]:
        for message in st.session_state.messages:
            # Dispense with any tool message prior to processing messages into chat flow
            if isinstance(message, dict):
                if message["role"] not in ["system", "tool"]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                # st.session_state["modality_change"] = False

            # Check if the message is a ChatCompletion object (response from OpenAI API)
            elif isinstance(message, object):  # This will catch all messages, but we narrow down with attributes below
                # Ensure the message has 'choices' and 'content' attributes (typical for OpenAI responses)
                if hasattr(message, "tool_calls") and hasattr(message, "refusal"):
                    # Ensure it's not a tool call (if tool_calls attribute exists)
                    if not getattr(message, "tool_calls", None):
                        # Display the assistant's message content
                        with st.chat_message(message.role):
                            st.markdown(message.content)

        # Debug
        if isinstance(st.session_state.messages, list):
            print(f"Printing all messages every time display_messages runs:\n>>>{st.session_state.messages}")

    def main(self):
        """Main function to run the Affinity Assist application."""
        self.setup_ui()
        self.display_messages()
        self.handle_input()
        self.generate_assistant_response()