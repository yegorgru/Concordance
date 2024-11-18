import streamlit as st
import spacy

# Load spaCy model for Ukrainian
try:
    nlp = spacy.load("uk_core_news_sm")
except OSError:
    st.error("Please install the Ukrainian SpaCy model with `!python -m spacy download uk_core_news_sm`")
    st.stop()

# Streamlit App
st.title("Word Dependency Finder (Ukrainian)")
st.write("Find all occurrences of a word, its neighbors, and dependency types in Ukrainian text.")

# Input: Text or File
st.header("Input Text")
text = st.text_area("Paste text below:")
uploaded_file = st.file_uploader("Or upload a text file", type=["txt"])
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")

# Input: Search Word
st.header("Search Parameters")
search_word = st.text_input("Enter the word to search for (it will be lemmatized automatically):")
num_neighbors = st.number_input("Number of neighbors to extract (left and right):", min_value=1, value=1, step=1)
output_file_name = st.text_input("Enter output file name (e.g., `results.txt`):", value="results.txt")

# Output
if text and search_word:
    # Lemmatize the search word
    search_word_doc = nlp(search_word)
    if len(search_word_doc) > 0:
        search_word_lemma = search_word_doc[0].lemma_
        print(search_word_lemma)
    else:
        st.error("Invalid input for search word.")
        st.stop()

    st.header("Results")
    doc = nlp(text)
    results = []

    for token in doc:
        if token.lemma_.lower() == search_word_lemma.lower():
            neighbors = {"word": token.text}

            # Extract left neighbors
            left_neighbors = []
            for i in range(1, num_neighbors + 1):
                if token.i - i >= 0:
                    left_neighbors.append({
                        "text": doc[token.i - i].text,
                        "dep": doc[token.i - i].dep_
                    })
                else:
                    break
            neighbors["left"] = left_neighbors

            # Extract right neighbors
            right_neighbors = []
            for i in range(1, num_neighbors + 1):
                if token.i + i < len(doc):
                    right_neighbors.append({
                        "text": doc[token.i + i].text,
                        "dep": doc[token.i + i].dep_
                    })
                else:
                    break
            neighbors["right"] = right_neighbors

            results.append(neighbors)

    if results:
        for result in results:
            st.write(f"Word: {result['word']}")
            st.write(f"  - Left Neighbors:")
            for neighbor in result["left"]:
                st.write(f"    - {neighbor['text']} (Dep: {neighbor['dep']})")
            st.write(f"  - Right Neighbors:")
            for neighbor in result["right"]:
                st.write(f"    - {neighbor['text']} (Dep: {neighbor['dep']})")
            st.write("---")

        # Save to file option
        st.header("Save Results")
        if st.button("Download Results"):
            output_text = []
            for r in results:
                left_text = ", ".join(f"{n['text']} (Dep: {n['dep']})" for n in r["left"])
                right_text = ", ".join(f"{n['text']} (Dep: {n['dep']})" for n in r["right"])
                output_text.append(f"Word: {r['word']}, Left: [{left_text}], Right: [{right_text}]")
            output_text = "\n".join(output_text)

            with open(output_file_name, "w", encoding="utf-8") as f:
                f.write(output_text)
            st.success(f"Results saved to `{output_file_name}`")
    else:
        st.write("No matches found for the given word.")
else:
    st.write("Enter text and a word to search for matches.")
