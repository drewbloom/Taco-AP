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
        self.model = "gpt-4o-mini" # can set model needed - will set default and allow user to pick others
        self.models = {"Instant Taco (Fastest)": "gpt-4o-mini", "Taco Supreme (Best Writing)": "gpt-4o", "Street Taco (Can Think)": "o3-mini"}
        st.session_state.model_selected = st.session_state.get('model_selected', None)

        self.vector_stores = {
            "AP World History": "vs_lu6EGQwhpKqUAyOXQrZammXo",
            "AP Human Geography": "vs_67f3071ccea88191bcfbb09a0ed82ace",
            "AP US History": "vs_67f30733f5cc8191be28a8aaec7c9781"
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
            "Writing Practice": """Objective: Assist students in practicing AP writing tasks (short-answer questions, document-based questions, long-essay questions) by guiding them through a structured learning process that mirrors the AP exam's rigor and format. The AI should provide feedback, challenge the student, and help them improve their writing skills based on AP guidelines and content.

Instructions for AI:

Initiate the Session:

AI: Checks the system message to determine which AP course is being studied. Then, ask the student which type of writing task they would like to focus on or if there are specific skills they'd like to work on.

Example: "Okay, so we're practicing some writing for AP U.S. History. Are you looking to practice short-answer questions, document-based questions, or long-essays today? Or do you have specific skills you want to work on, like thesis writing or contextualization?"

Get Course Content & Skills Descriptions:

User: Responds with focus areas or asks for general writing help.
Example: "I really need help with contextualization. Mine suck."

AI: Retrieves the relevant writing requirements and scoring guidelines for the student’s requested task. AI should also be ready to give general writing tips or direct the student to more specific feedback.
Example: *searches course description and exam documents for contextualization, long-essay question, document-based question*

Present Writing Task and Prompt:

AI: Present a sample writing task (e.g., a document-based question or essay prompt) designed to practice skills and elicit understandings through writing.
Example (e.g., for AP U.S. History):
"Let's try writing a contextualization for this:
**Prompt:** 'Analyze the extent to which the American Revolution marked a turning point in American political development.'"

User: The student should try to write a response so you can help them practice. You may help with questions or starter sentences if they ask follow-ups.
Example: User: "I don't even know where to begin..."
AI: "A great contextualization starts with a time period. In our history essays, we typically want to contextualize about 50 years of history up to the point of the prompt. So - when does this prompt start?"
User: "1776?"
AI: "That's right - so our contextualization would start as early as 1700. We want to discuss the things that explain the significance of our prompt - are there any themes you notice from the course?"
User: "Politics"
AI: "What could you tell me about politics in the colonies between 1700 and 1776, then?"

User and Assistant continue this interaction with the assistant eventually leading the user to discuss the three or more examples for contextualization, as stated in the course exam and description.

Provide Feedback:

User: Submits a draft or outlines their response.

AI: Provide constructive feedback. Offer guidance based on the requirements in the course descriptiong documents. You can also provide feedback on aspects like thesis clarity, evidence use, organization, and argument development. Avoid simply giving answers—encourage the student to think critically about their work.

Example: "Okay, you've got three solid examples of political developments in the colonies that led to revolution. You also wrote a thesis. Could you clarify your thesis a bit more? Perhaps focus on specifying how the Revolution’s impact on governance was different from previous periods. Remember, you'll have to write a thesis that's detailed enough to give you a chance to write about a lot of examples. That's even more true in your DBQ, where you'll need to tie together a wide range of historical documents into a single argument."

If the student’s response doesn’t fully meet the requirements or could be stronger, offer specific advice on improvement.

Example: "Your thesis is a bit broad right now. Try to narrow it down by addressing a specific political change, like how it altered relationships between states or the federal government."

Challenge and Prompt Further Development:

AI: If the student is struggling, ask them questions to guide deeper thinking, such as:
"Can you think of any examples from the course that might support your argument here?"
Or, if they're making progress, challenge them to consider more advanced elements of their response:
"You’ve made a strong case, but what about counterarguments? How might someone disagree with your point of view, and how could you address that?"

Repeat the Process:

AI: Continue to work through the writing task with the student, encouraging them to refine their writing, develop their argument, and incorporate feedback. Provide continuous, real-time feedback on each part of the writing process.

Example: "You’ve made excellent revisions to your thesis. Now, let’s make sure your evidence flows logically—can you add a sentence that connects your second piece of evidence to the first?"

Conclude the Session:

AI: Once the student feels confident in their writing, ask if they'd like to review other tasks or areas of writing. Suggest additional resources or strategies to improve further.

Example: "You’ve done great work today! Would you like to practice a different writing task, or focus on improving a particular part of your response, like evidence analysis or concluding statements?"

General Note for AI:

Throughout the interaction, ensure that feedback is specific and constructive, based on AP course materials. Always use the language and guidelines of the specific AP course in your feedback.

Avoid giving the student a direct, complete answer; the goal is to encourage the student’s own learning and development through thoughtful questioning and feedback.
""",
            
            
            "Multiple Choice": """Objective: Assist students in practicing AP multiple-choice questions by guiding them through a structured learning process that mirrors the AP exam's rigor and format.

Instructions for AI:

Initiate the Session:

AI: Checks the system message to determine which AP course is being studied, then asks the student if there are focuses for this study session.
Example: "Alright, let's practice some multiple choice for AP Human Geography -- are there particular topics or themes you'd like to practice?"

Get Course Content:

User: Responds with focus areas, or asks for general review

AI: Retrieves the exam and course description to examine the content related to the user request and familiarize itself with the course

Present Stimulus and Question:

AI: Provide a stimulus (historical quote, excerpt, or image) followed by a multiple-choice question designed to challenge the student's understanding.

Example (e.g. for AP World History): "Stimulus: "In the early 18th century, the Ottoman Empire faced significant administrative challenges. Provincial governors, known as beys, exercised considerable autonomy, often leading to inconsistent tax collection and military service. To address these issues, the central government issued a decree aiming to standardize taxation and military conscription across all provinces, reinforcing the sultan's authority."

Question: "Which of the following best describes the primary objective of the decree mentioned above?"

A) To decentralize governance by granting more power to provincial governors.

B) To standardize administrative practices across provinces to strengthen central authority.

C) To promote cultural diversity by recognizing multiple official languages.

D) To reduce the military's influence in provincial governance.

Student Response:

Student: Selects an answer choice.

Example: "C."

Provide Feedback:

AI: Offer immediate feedback on the student's choice, congratulating them if they are correct. If the student's answer is wrong, the assistant explains why the first answer they picked was not correct. The student can be prompted for another guess or can ask for an explanation of the correct answer.

Example: Assistant: "C is incorrect here. If we look at the stimulus, we don't see discussion of ethnic groups or languages, which would be good ways to spot cultural diversity. Is there another option that stands out to you, or would you like me to explain the correct answer?"

User: "I'm confused by this one, could you explain the correct answer?"

Assistant: "Sure. The correct answer is B. The Ottoman Empire's decree aimed to standardize administrative practices across provinces, thereby reinforcing central authority. Options A, C, and D are incorrect because the stimulus does not mention or pertain to those particular understandings."

Present Next Question:

AI: Introduce the next question, maintaining the sequence and difficulty appropriate to the AP exam.​

Example (e.g. for AP Human Geography):

Stimulus: "The intricate network of borders in regions like the Middle East has often led to disputes over territory, resources, and governance. These boundaries, drawn during the colonial era, frequently disregard the existing ethnic, religious, and cultural landscapes, resulting in ongoing conflicts and challenges to sovereignty."

Question: "Which type of boundary is exemplified by the borders in the Middle East, often leading to disputes over territory and resources?"

A) "Antecedent Boundary"

B) "Subsequent Boundary"

C) "Superimposed Boundary"

D) "Relic Boundary"

Repeat Process:

Continue presenting questions one at a time, providing feedback after each response, until the set of practice questions is complete.

Conclude the Session:

AI: The student may ask for tips to improve. You may suggest test-taking strategies for multiple choice. They may also alter the goal of the practice to writing or content review, at which point you should be ready to begin with those practices instead. You may use your internet search tool to offer additional resources or suggest further practice if necessary.

Note: Throughout the interaction, the AI should ensure that all content is appropriate, safe, and educational for high school students. Any external content retrieved should be clearly cited, and the AI should avoid using unsafe or inappropriate materials.""",
            
            
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
        st.write("Begin by choosing Talk or Text and picking your course on the left")

        new_modality = st.sidebar.selectbox(
            label="Input Modality", options=["Talk", "Text"], index=None, placeholder="How you'll talk to Taco", label_visibility="collapsed", key="modality"
        )
        
        if new_modality != self.modality:
            st.session_state["modality_change"] = True
            self.modality = new_modality


        # Place vector store region in sidebar below input type
        upload_widget = st.sidebar

        # AP Courses / Vector Stores
        upload_widget.title(':material/topic: Available Courses')
        vs_container = upload_widget.container()
        vs_selected = vs_container.selectbox(label=':material/left_click: Choose your course', index=None, options=self.vector_stores)
        if vs_selected != st.session_state.vector_store_selected:
            with st.spinner("Updating the AI for your course..."):
                st.session_state.vector_store_selected = self.vector_stores[vs_selected]
                st.session_state.system_message_selected = self.system_messages.get(vs_selected, self.system_message)

                # If no current messages, add the new system message. If current messages, swap old sys message for new one
                if len(st.session_state.messages) < 1:
                    st.session_state.messages.append({"role": "system", "content": st.session_state.system_message_selected})
                else:
                    st.session_state.messages[0] = {"role": "system", "content": st.session_state.system_message_selected}
                st.success(f"AI Updated for your course: {vs_selected}")

        # Study Suggestions (Prompts)
        if st.session_state.vector_store_selected:
            upload_widget.title("Study Suggestions")
            
            # Set up columns to hold buttons
            col1, col2, col3 = upload_widget.columns(3)

            with col1:
                writing_practice = st.button(type="primary", label="Writing Practice", help="Practice writing for your course assessments")
            with col2:
                mcq_practice = st.button(type="primary", label="Multiple Choice", help="Practice multiple-choice questions based on AP course outlines")
            with col3:
                content_review = st.button(type="primary", label="Content Review", help="Dive deeper into key concepts and connections")

            # Handle button callbacks to begin an interaction
            if writing_practice:
                st.session_state.selected_prompt = self.prompts.get('Writing Practice')
                self.handle_prompt_button()

            if content_review:
                st.session_state.selected_prompt = self.prompts.get('Content Review')
                self.handle_prompt_button()

            if mcq_practice:
                st.session_state.selected_prompt = self.prompts.get('Multiple Choice')
                self.handle_prompt_button()        
        
        
        # Offer choice of AI Models
        st.sidebar.title(":material/smart_toy: Customize :taco: as needed")
        model_selection = st.sidebar.selectbox(label='Pick an AI model', options=self.models, index=0, label_visibility='collapsed')
        st.session_state.model_selected = self.models[model_selection]

        print(model_selection) #debug
        print(st.session_state.model_selected) #debug

    def handle_prompt_button(self):
        
        self.handle_text_input(prompt_input=st.session_state.selected_prompt)


    def handle_input(self):
        """Handle user input based on selected modality (Text or Speech)."""
        if st.session_state["modality"] == "Text":
            self.handle_text_input()
        elif st.session_state["modality"] == "Talk":
            self.handle_speech_input()

    def handle_text_input(self, prompt_input=None):
        """Process text input from the user."""
        if prompt_input == None:
            text_input = st.chat_input("Type your message", disabled=(self.modality != "Text"))
            if text_input and not self.new_message:
                st.session_state.messages.append({"role": "user", "content": text_input})
                self.new_message = True
                with st.chat_message("user"):
                    st.markdown(text_input)
        else:
            if prompt_input and not self.new_message:
                st.session_state.messages.append({"role": "user", "content": st.session_state.selected_prompt})
                self.new_message = True

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
                    model=st.session_state.model_selected,
                    input=st.session_state.messages,
                    stream=True,
                    tools=self.tools,
                    truncation="auto"
                )
                

                response = self.stream_handler()
                final_response = st.write_stream(response)
                
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
                    # Remove any scripted prompts by checking content against the prewritten prompts
                    if message["content"] not in self.prompts.values():
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

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