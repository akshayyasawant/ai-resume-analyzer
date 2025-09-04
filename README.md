🤖 AI Resume Analyzer
An intelligent resume screening tool that automatically parses, analyzes, and ranks resumes based on a job description. This application is built with Python and the Streamlit framework, providing a clean, interactive web interface.

🎯 Features
PDF Resume Parsing: Extracts text and key information from uploaded PDF files.

Intelligent Matching: Uses a custom scoring algorithm to rank candidates based on keyword relevance and experience.

Customizable Scoring: The scoring system is weighted to prioritize critical skills like Python, Django, and Flask.

Interactive Web UI: A user-friendly interface built with Streamlit for easy uploading and analysis.

Visual Analytics: Provides a clear, color-coded chart to visualize candidate scores and rankings.

Export Functionality: Download detailed reports in Excel and CSV formats.

🚀 How to Use
Follow these simple steps to run the application on your local machine.

1. Clone the Repository
First, clone the project from GitHub to your local machine:

git clone [https://github.com/akshayyasawant/ai-resume-analyzer.git](https://github.com/akshayyasawant/ai-resume-analyzer.git)
cd ai-resume-analyzer

2. Install Dependencies
Install the necessary Python libraries using pip. The requirements.txt file contains a list of all dependencies.

pip install -r requirements.txt

3. Run the Application
Once the libraries are installed, you can launch the Streamlit application from your terminal:

streamlit run app.py

Your web browser will automatically open a new tab with the application running.

📊 Sample Output
After uploading resumes and a job description, the application generates a detailed report and a visual ranking of candidates.

🛠️ Tech Stack
Python 3.9+

Streamlit: For building the interactive web interface.

scikit-learn: Used for TF-IDF vectorization and cosine similarity.

pandas: For efficient data manipulation and export.

PyPDF2: For extracting text from PDF documents.

plotly: For creating interactive data visualizations.

openpyxl: A dependency for exporting data to Excel files.

📜 License
This project is licensed under the MIT License.
