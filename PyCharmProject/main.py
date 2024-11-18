import streamlit as st
import spacy

try:
    nlp = spacy.load("uk_core_news_sm")
except OSError:
    st.error("Please install the Ukrainian SpaCy model with `!python -m spacy download uk_core_news_sm`")
    st.stop()

st.title("Конкорданс")
st.write("Пошук входжень слова, його сусідів і типів залежностей")

st.header("Ввід тексту")
text = st.text_area("Вставте текст:")
uploaded_file = st.file_uploader("Або завантажте текстовий файл", type=["txt"])
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")

st.header("Параметри пошуку")
search_word = st.text_input("Введіть слово для пошуку:")
num_neighbors = st.number_input("Введіть кількість сусідів:", min_value=1, value=1, step=1)

if text and search_word:
    search_word_doc = nlp(search_word)
    if len(search_word_doc) > 0:
        search_word_lemma = search_word_doc[0].lemma_
    else:
        st.error("Некоректний ввід.")
        st.stop()

    doc = nlp(text)
    results = []
    highlighted_text = [""] * len(doc)  # Initialize the highlighted text list

    for i, token in enumerate(doc):
        if "<span style='color: green;" not in highlighted_text[i]:
            highlighted_text[i] = token.text

        if token.lemma_.lower() == search_word_lemma.lower():
            highlighted_text[i] = f"<span style='color: red; font-weight: bold;'>{token.text}</span>"

            neighbors = {"word": token.text, "dep": token.dep_}

            left_neighbors = []
            for j in range(1, num_neighbors + 1):
                if token.i - j >= 0:
                    left_neighbor = doc[token.i - j]
                    left_neighbors.insert(0, {
                        "text": left_neighbor.text,
                        "dep": left_neighbor.dep_
                    })
                    highlighted_text[token.i - j] = f"<span style='color: green;'>{left_neighbor.text}</span>"
            neighbors["left"] = left_neighbors

            right_neighbors = []
            for j in range(1, num_neighbors + 1):
                if token.i + j < len(doc):
                    right_neighbor = doc[token.i + j]
                    right_neighbors.append({
                        "text": right_neighbor.text,
                        "dep": right_neighbor.dep_
                    })
                    highlighted_text[token.i + j] = f"<span style='color: green;'>{right_neighbor.text}</span>"
            neighbors["right"] = right_neighbors

            results.append(neighbors)

    highlighted_text_str = " ".join(highlighted_text)

    if st.button("Показати текст з підсвіткою"):
        st.header("Текст з  підсвіткою")
        st.markdown(f"<div style='white-space: pre-wrap;'>{highlighted_text_str}</div>", unsafe_allow_html=True)

    if st.button("Показати список сусідів"):
        st.header("Список сусідів")
        if results:
            for result in results:
                st.write(f"Слово: {result['word']} (Функція в реченні: {result['dep']})")
                st.write(f"  - Ліві сусіди:")
                for neighbor in result["left"]:
                    st.write(f"    - {neighbor['text']} (Функція в реченні: {neighbor['dep']})")
                st.write(f"  - Праві сусіди:")
                for neighbor in result["right"]:
                    st.write(f"    - {neighbor['text']} (Функція в реченні: {neighbor['dep']})")
                st.write("---")
    st.header("Зберегти результати")
    output_file_name = st.text_input("Введіть назву файлу (наприклад, `results.txt`):", value="results.txt")
    if st.button("Завантажити"):
        output_text = []
        for r in results:
            left_text = ", ".join(f"{n['text']} (Функція в реченні: {n['dep']})" for n in r["left"])
            right_text = ", ".join(f"{n['text']} (Функція в реченні: {n['dep']})" for n in r["right"])
            output_text.append(f"Слово: {r['word']} (Функція в реченні: {r['dep']}), Ліві сусіди: [{left_text}], Праві сусіди: [{right_text}]")
        output_text = "\n".join(output_text)

        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(output_text)
        st.success(f"Результати збережено в `{output_file_name}`")
