# What I Learned While Building a RAG Chatbot With a Free Model

This week I worked on a practical RAG chatbot project.

RAG stands for Retrieval-Augmented Generation. In simple words, it means the AI does not answer from memory first. It searches the documents first, finds the most relevant parts, and then writes an answer using only that context.

That one idea changes the whole behavior of a chatbot.

A normal chatbot may sound confident even when it is guessing. A RAG chatbot should be more controlled. If the answer is inside the knowledge base, it answers with sources. If the answer is not there, it should say it could not find it.

For practice, I used two knowledge sources:

1. A recent Agentic AI article from arXiv
2. My own GitHub repo with notebooks and project files

The full flow was:

- Load the documents
- Extract text
- Split long text into smaller chunks
- Create embeddings so chunks become searchable
- Retrieve the most relevant chunks for a question
- Send only those chunks to the model
- Ask the model to answer strictly from that context
- Show the sources used

The most important concept for me was chunking.

At first, I thought the model simply reads the full PDF or full repo. But real RAG does not work like that. Large documents are split into focused sections, because the model only needs the most relevant parts to answer a specific question.

Another important concept was embeddings.

An embedding is a numeric representation of text. It helps the system compare a user question with document chunks and find what is most similar. In a production system, I would use a stronger embedding model and a vector database like Chroma, Pinecone, Weaviate, or FAISS.

For learning, I kept the setup free and simple:

- Local retrieval logic
- Free-tier Groq model for answering
- Gradio UI for testing
- Source-based answers

This is the same idea clients ask for when they want a chatbot that answers from Google Drive, PDFs, company policies, help docs, or internal knowledge bases.

My key takeaway:

RAG is not just a chatbot feature. It is a trust system.

It helps the chatbot stay grounded, cite sources, and avoid making up answers when the information is not available.

Next step: connect this same RAG pipeline to Google Drive and build a full document-based assistant.

#RAG #AIAgents #LangChain #Python #GenerativeAI #Gradio #LearningInPublic
