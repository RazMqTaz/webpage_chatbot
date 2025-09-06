from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
from PySide6.QtCore import Signal, Qt

class Settings(QWidget):
    model_changed = Signal(str)
    top_k_changed = Signal(str)
    system_prompt_changed = Signal(str)
    def __init__(self):
        super().__init__()

        self.model_label = QLabel("Select GPT Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-4o",
        ])

        self.top_k_label = QLabel("Maximum Context Chunks")
        self.top_k_field = QLineEdit()
        self.top_k_field.setText("10")
        self.top_k_info = QLabel("?")
        self.top_k_info.setFixedSize(18, 18)
        self.top_k_info.setAlignment(Qt.AlignCenter)
        self.top_k_info.setToolTip("Maximum context chunks determines how many relevant chunks\n" \
                                   "will be appended to your prompt as context. By default this\n"
                                   "is set to 10. Higher values will provide the model with more\n"
                                   "context, but this may lose accuracy.")
        self.top_k_info.setStyleSheet(
            """
            QLabel {
                border-radius: 9px:
                border: 1px solid #666666;;
                background-color: #2d2d2d;
                font-weight: bold;
                font-size: 10px;
                color: #dddddd;
            }
            QLabel:hover{
                background-color: #3a3a3a;
            }
        """)
        top_k_layout = QHBoxLayout()
        top_k_layout.addWidget(self.top_k_label)
        top_k_layout.addWidget(self.top_k_info)

        self.system_prompt_label = QLabel("Set System Prompt")
        self.system_prompt_info = QLabel("?")
        self.system_prompt_info.setFixedSize(18, 18)
        self.system_prompt_info.setAlignment(Qt.AlignCenter)
        self.system_prompt_info.setToolTip("The system prompt is a persistent instruction that guides\nChatGPT's responses throughout the conversation.")
        self.system_prompt_info.setStyleSheet(
            """
            QLabel {
                border-radius: 9px:
                border: 1px solid #666666;;
                background-color: #2d2d2d;
                font-weight: bold;
                font-size: 10px;
                color: #dddddd;
            }
            QLabel:hover{
                background-color: #3a3a3a;
            }
        """)
        system_prompt_layout = QHBoxLayout()
        system_prompt_layout.addWidget(self.system_prompt_label)
        system_prompt_layout.addWidget(self.system_prompt_info)
        self.system_prompt_field = QTextEdit("You are a helpful assistant. Use the following extracted parts of documents to answer the user's questions. " +
                                            "Do not make up answers. Stay grounded in the context provided. Do not create files unless instructed to.\n\n")
        self.system_prompt_field.setFixedHeight(60)
        
        self.model_combo.currentTextChanged.connect(self.model_changed)
        self.top_k_field.textChanged.connect(self.top_k_changed)
        self.system_prompt_field.textChanged.connect(self.emit_system_prompt_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_combo)
        layout.addLayout(top_k_layout)
        layout.addWidget(self.top_k_field)
        layout.addLayout(system_prompt_layout)
        layout.addWidget(self.system_prompt_field)
        self.setLayout(layout)
        self.setMaximumHeight(300)
    
    def emit_system_prompt_changed(self):
        text = self.system_prompt_field.toPlainText()
        self.system_prompt_changed.emit(text)

