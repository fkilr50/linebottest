from transformers import pipeline

# Initialize the Hugging Face pipeline for question-answering
qa_pipeline = pipeline("question-answering")

def answer_question(question: str, context: str):
    """
    This function uses Hugging Face's QA model to answer a question based on the provided context.
    """
    result = qa_pipeline({"question": question, "context": context})
    return result["answer"]
