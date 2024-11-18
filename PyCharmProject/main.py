import streamlit as st
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Streamlit App
st.title("Word Dependency Finder")
st.write("Find all occurrences of a word, its neighbors, and dependency types.")

# Input: Text or File
st.header("Input Text")
text = st.text_area("Paste text below:")
uploaded_file = st.file_uploader("Or upload a text file", type=["txt"])
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")

# Input: Search Word
st.header("Search Word")
search_word = st.text_input("Enter the word to search for (lemma-based matching):")

# Output
if text and search_word:
    st.header("Results")
    doc = nlp(text)
    results = []

    for token in doc:
        if token.lemma_.lower() == search_word.lower():
            left_neighbor = token.nbor(-1).text if token.i > 0 else None
            right_neighbor = token.nbor(1).text if token.i < len(doc) - 1 else None
            results.append({
                "word": token.text,
                "left": left_neighbor,
                "right": right_neighbor,
                "dep_left": token.nbor(-1).dep_ if left_neighbor else None,
                "dep_right": token.nbor(1).dep_ if right_neighbor else None
            })

    if results:
        for result in results:
            st.write(f"Word: {result['word']}")
            st.write(f"  - Left Neighbor: {result['left']} (Dep: {result['dep_left']})")
            st.write(f"  - Right Neighbor: {result['right']} (Dep: {result['dep_right']})")
            st.write("---")

        # Save to file option
        st.header("Save Results")
        if st.button("Download Results as Text File"):
            output_text = "\n".join(
                f"Word: {r['word']}, Left: {r['left']}, Right: {r['right']}, Dep Left: {r['dep_left']}, Dep Right: {r['dep_right']}"
                for r in results
            )
            with open("results.txt", "w") as f:
                f.write(output_text)
            st.success("Results saved to `results.txt`")
    else:
        st.write("No matches found for the given word.")
else:
    st.write("Enter text and a word to search for matches.")

