from src.text_splitter import split_text

text = "Machine learning learns patterns from data. " * 50

chunks = split_text(text)

empty_chunks = split_text("")

print("Total chunks:", len(chunks))

print("Chunk lengths:", [len(chunk) for chunk in chunks])

print("Empty input result:", empty_chunks)

print(
    "Overlap verified:",
    chunks[0][-50:] == chunks[1][:50]
)
print("First chunk ending:", repr(chunks[0][-80:]))
print("Second chunk beginning:", repr(chunks[1][:80]))
