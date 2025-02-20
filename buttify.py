import random
import re
import nltk
from nltk.tokenize import SyllableTokenizer, NLTKWordTokenizer

class Buttifier:
    def __init__(self):
        # Ensure necessary NLTK resources are downloaded
        try:
            nltk.data.find('corpora/cmudict')
        except LookupError:
            nltk.download('cmudict')

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def count_syllables(self, word):
        """Counts syllables in a word using the CMU Pronouncing Dictionary and a fallback method."""
        try:
            d = nltk.corpus.cmudict.dict()
            return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
        except KeyError:
            # Fallback: Use a simpler heuristic (less accurate)
            vowels = "aeiouy"
            count = 0
            word = word.lower()
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count += 1
            return count

    def is_alternating_case(self, word):
        """Checks if a word is in alternating case (e.g., 'aLtErNaTiNg')."""
        if len(word) < 2:
            return False

        start_index = -1
        for i in range(len(word)):
            if word[i].isalpha():
                start_index = i
                break
        if start_index == -1:
            return False

        case1 = word[start_index].islower()
        alpha_count = 0

        for i in range(len(word)):
            if not word[i].isalpha():
                continue
            current_case = word[i].islower()

            if (alpha_count % 2 == 0 and current_case != case1) or \
               (alpha_count % 2 != 0 and current_case == case1):
                return False
            alpha_count += 1
        return True

    def alternate_case(self, word):
        """Converts a word to alternating case (e.g., 'alternating' -> 'aLtErNaTiNg')."""
        result = ""
        alpha_count = 0
        for char in word:
            if not char.isalpha():
                result += char
                continue
            if alpha_count % 2 == 0:
                result += char.lower()
            else:
                result += char.upper()
            alpha_count += 1
        return result

    def replace_nth_syllable(self, text, n, replacement, forbidden_words):
        """Replaces syllables, preserving case/plurality, including alternating."""
        forbidden_words = set(forbidden_words)
        word_spans = list(NLTKWordTokenizer().span_tokenize(text))
        words = [text[start:end] for start, end in word_spans]
        
        result_words = []
        skip_count = 0

        for word in words:
            original_word = word  # Keep the original
            if not word.isalpha():
                result_words.append(word)
                continue
            if word in forbidden_words:
                result_words.append(word)
                continue
            SSP = SyllableTokenizer()

            # Tokenize *once* per word.
            try:
                syllables = SSP.tokenize(original_word)
            except (KeyError, IndexError):  # Handle both KeyError and potential IndexError
                syllables = [original_word]

            word_syllable_count = len(syllables) # Use the number of syllables from SSP
            word_replaced = False

            for i in range(word_syllable_count):
                if skip_count > 0:
                    skip_count -= 1
                    continue

                if random.random() < (1 / n) and not word_replaced:

                    # --- Case Preservation ---
                    if syllables[i].isupper():
                        new_word = replacement.upper()
                    elif syllables[i][0].isupper():
                        new_word = replacement.capitalize()
                    elif self.is_alternating_case(syllables[i]):
                        new_word = self.alternate_case(replacement)
                    else:
                        new_word = replacement.lower()
                    
                    # --- Syllable Replacement ---
                    syllables[i] = new_word   # Directly modify the syllables list
                    if len(new_word) >= 2 and new_word[-1] == new_word[-2] and i < word_syllable_count - 1 and syllables[i+1].startswith(new_word[-1]):
                        syllables[i] = new_word[:-1]  # Remove the last character if the next syllable starts with it
                    word_replaced = True      # Mark as replaced
                    skip_count = round(random.gauss(n, n / 2)) - 1
                    skip_count = max(0, skip_count)

            # Join syllables and append to results
            new_word = "".join(syllables)
            if original_word.lower().endswith('s') and not new_word.lower().endswith('s'):
                new_word += 's'
            result_words.append(new_word)
        def get_word_continuation(i):
            frm = word_spans[i][1]
            to = word_spans[i+1][0] if i+1 < len(word_spans) else len(text)
            return text[frm:to]
        result_words = [word + get_word_continuation(i) for i, word in enumerate(result_words)]  # Remove empty strings
        return "".join(result_words)

# --- Example Usage ---
# buttifier = Buttifier()

# text = "This is an alternating case Example: aLtErNaTiNg CaSe."
# modified_text = buttifier.replace_nth_syllable(text, 10)
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "Apples and bananas are delicious fruits."
# modified_text = buttifier.replace_nth_syllable(text, 2, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "I AM YELLING"
# modified_text = buttifier.replace_nth_syllable(text, 5, "test")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "This is a TeSt."
# modified_text = buttifier.replace_nth_syllable(text, 2, "example")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "tHiS iS aLtErNaTiNg."
# modified_text = buttifier.replace_nth_syllable(text, 2, "example")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "aLtErNaTiNg"
# modified_text = buttifier.replace_nth_syllable(text, 1, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "aLtErNaTiNg"
# modified_text = buttifier.replace_nth_syllable(text, 2, "b")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "onomatopoeia"
# modified_text = buttifier.replace_nth_syllable(text, 2, "b")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "mississippi"
# modified_text = buttifier.replace_nth_syllable(text, 2, "b")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "Hello, world!"
# modified_text = buttifier.replace_nth_syllable(text, 2, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "Hello, world!"
# modified_text = buttifier.replace_nth_syllable(text, 1, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")
# import re
# import nltk
# from nltk.tokenize import SyllableTokenizer, NLTKWordTokenizer

# # Ensure necessary NLTK resources are downloaded
# try:
#     nltk.data.find('corpora/cmudict')
# except LookupError:
#     nltk.download('cmudict')

# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt')


# def count_syllables(word):
#     """Counts syllables in a word using the CMU Pronouncing Dictionary and a fallback method."""
#     try:
#         d = nltk.corpus.cmudict.dict()
#         return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
#     except KeyError:
#         # Fallback: Use a simpler heuristic (less accurate)
#         vowels = "aeiouy"
#         count = 0
#         word = word.lower()
#         if word[0] in vowels:
#             count += 1
#         for index in range(1, len(word)):
#             if word[index] in vowels and word[index - 1] not in vowels:
#                 count += 1
#         if word.endswith("e"):
#             count -= 1
#         if count == 0:
#             count += 1
#         return count

# def is_alternating_case(word):
#     """Checks if a word is in alternating case (e.g., 'aLtErNaTiNg')."""
#     if len(word) < 2:
#         return False

#     start_index = -1
#     for i in range(len(word)):
#         if word[i].isalpha():
#             start_index = i
#             break
#     if start_index == -1:
#         return False

#     case1 = word[start_index].islower()
#     alpha_count = 0

#     for i in range(len(word)):
#         if not word[i].isalpha():
#             continue
#         current_case = word[i].islower()

#         if (alpha_count % 2 == 0 and current_case != case1) or \
#            (alpha_count % 2 != 0 and current_case == case1):
#             return False
#         alpha_count += 1
#     return True

# def alternate_case(word):
#     """Converts a word to alternating case (e.g., 'alternating' -> 'aLtErNaTiNg')."""
#     result = ""
#     alpha_count = 0
#     for char in word:
#         if not char.isalpha():
#             result += char
#             continue
#         if alpha_count % 2 == 0:
#             result += char.lower()
#         else:
#             result += char.upper()
#         alpha_count += 1
#     return result


# def replace_nth_syllable(text, n, replacement="butt"):
#     """Replaces syllables, preserving case/plurality, including alternating."""

#     # words = #nltk.word_tokenize(text)
#     word_spans = list(NLTKWordTokenizer().span_tokenize(text))
#     words = [text[start:end] for start, end in word_spans]
    
#     print("WORDS", words)
#     result_words = []
#     skip_count = 0

#     for word in words:
#         original_word = word  # Keep the original
#         if not word.isalpha():
#             result_words.append(word)
#             continue
#         SSP = SyllableTokenizer()

#         # Tokenize *once* per word.
#         try:
#             syllables = SSP.tokenize(original_word)
#         except (KeyError, IndexError):  # Handle both KeyError and potential IndexError
#             syllables = [original_word]

#         word_syllable_count = len(syllables) # Use the number of syllables from SSP
#         word_replaced = False

#         for i in range(word_syllable_count):
#             if skip_count > 0:
#                 skip_count -= 1
#                 continue

#             if random.random() < (1 / n) and not word_replaced:

#                 # --- Case Preservation ---
#                 if original_word.isupper():
#                     new_word = replacement.upper()
#                 elif original_word[0].isupper():
#                     new_word = replacement.capitalize()
#                 elif is_alternating_case(original_word):
#                     new_word = alternate_case(replacement)
#                 else:
#                     new_word = replacement.lower()
                
#                 # --- Syllable Replacement ---
#                 syllables[i] = new_word   # Directly modify the syllables list
#                 if len(new_word) >= 2 and new_word[-1] == new_word[-2] and i < word_syllable_count - 1 and syllables[i+1].startswith(new_word[-1]):
#                     syllables[i] = new_word[:-1]  # Remove the last character if the next syllable starts with it
#                 word_replaced = True      # Mark as replaced
#                 skip_count = round(random.gauss(n, n / 2)) - 1
#                 skip_count = max(0, skip_count)

#         # Join syllables and append to results
#         new_word = "".join(syllables)
#         if original_word.lower().endswith('s') and not new_word.lower().endswith('s'):
#             new_word += 's'
#         result_words.append(new_word)
#     def get_word_continuation(i):
#         frm = word_spans[i][1]
#         to = word_spans[i+1][0] if i+1 < len(word_spans) else len(text)
#         return text[frm:to]
#     result_words = [word + get_word_continuation(i) for i, word in enumerate(result_words)]  # Remove empty strings
#     return "".join(result_words)

# # --- Example Usage ---
# text = "This is an alternating case Example: aLtErNaTiNg CaSe."
# modified_text = replace_nth_syllable(text, 10)
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")
# exit(0)
# text = "Apples and bananas are delicious fruits."
# modified_text = replace_nth_syllable(text, 2, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "I AM YELLING"
# modified_text = replace_nth_syllable(text, 5, "test")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "This is a TeSt."
# modified_text = replace_nth_syllable(text, 2, "example")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "tHiS iS aLtErNaTiNg."
# modified_text = replace_nth_syllable(text, 2, "example")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "aLtErNaTiNg"
# modified_text = replace_nth_syllable(text, 1, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "aLtErNaTiNg"
# modified_text = replace_nth_syllable(text, 2, "b")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "onomatopoeia"
# modified_text = replace_nth_syllable(text, 2, "b")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "mississippi"
# modified_text = replace_nth_syllable(text, 2, "b")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "Hello, world!"
# modified_text = replace_nth_syllable(text, 2, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")

# text = "Hello, world!"
# modified_text = replace_nth_syllable(text, 1, "butt")
# print(f"Original: {text}")
# print(f"Modified: {modified_text}")