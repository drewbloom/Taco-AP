# Taco AP Review

Taco AP Review is an interactive study tool designed to help students prepare for AP exams. It offers a user-friendly interface with options for both **text** and **speech** inputs, allowing users to practice writing, review course content, and test their knowledge with multiple-choice questions. The system is customizable, allowing users to choose from various AP History courses, interact with different AI models, and practice different types of questions.

## Features

- **Input Modalities**: Students can interact with Taco AP Review via text (`TacoText`) or speech (`TacoTalk`).
- **Course Selection**: Choose from various AP History courses, such as AP World History, AP US History, and AP Human Geography. Each course has tailored study prompts and resources.
- **AI Models**: Pick from several AI models optimized for different tasks—fastest, best writing, or smartest models, giving flexibility based on student preferences.
- **Study Prompts**: Access pre-written study prompts that cover writing practice, multiple-choice questions, and content review.
- **Real-Time Feedback**: Receive automatic AI feedback on writing and content review, based on official AP guidelines and exam descriptions.
- **Course-Specific System Prompts**: System prompts dynamically adjust based on the selected course to help guide students’ study sessions effectively.

## How It Works

The app leverages **Streamlit** to provide a user-friendly interface for interacting with AI models, using the following workflow:

1. **Vector Store**: Each AP course is linked to a **vector store** containing relevant course materials and study prompts.
2. **AI Models**: Taco AP Review uses different AI models to provide tailored responses based on the course selected, user input, and study focus.
3. **System Prompts**: The app adjusts system prompts dynamically based on the selected course, ensuring that the AI responses are aligned with the AP exam structure and guidelines.
4. **Study Session Flow**: Depending on the user’s selections, Taco will guide them through various study modes—writing practice, MCQs, content review—while providing helpful feedback and suggestions.

## Contributing

We welcome contributions! If you'd like to improve Taco AP Review, here are a few ways you can help:

- **Fix bugs** or **add features** to improve user experience.
- **Create new study prompts** or **improve existing ones** to align better with AP guidelines.
- **Improve documentation** to make the tool even easier to use.

To contribute, please fork the repository, create a new branch for your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/MIT) for details.

---

## Contact

For any questions or feedback, feel free to reach out to [Drew Bloom](mailto:drewbloom9@gmail.com).