import os
import re
import math

import tensorflow as tf
from transformers import TFBertModel, BertTokenizer
from tensorflow.keras.models import load_model

import textstat
from word_forms.word_forms import get_word_forms

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import words

from api.utils.helpers import read_file_to_array


class TextAnalysisEngine:
    def __init__(self, text):
        self.text = text
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        model_path = os.path.join(self.base_dir, 'models', 'modelo_small_01.h5')
        self.model = load_model(model_path, custom_objects={'TFBertModel': TFBertModel})
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        
        self.common_words = read_file_to_array(
            os.path.join(self.base_dir, 'data', '10k_commom_words.txt')
        )

        self.phrasal_verbs = read_file_to_array(
            os.path.join(self.base_dir, 'data', 'phrasal_verbs.txt')
        )

        self.fantasy = read_file_to_array(
            os.path.join(self.base_dir, 'data', 'fantasy.txt')
        )

    def check_creativity(self):
        if self.check_short_talk():
            return False

        if self.__check_complexity():
            return True

        if self.__check_fantasy():
            return True

        if self.__check_distant_ideas():
            return True

        return False

    def detect_phrasal_verbs(self):
        text = self.text.lower()
        found_verbs = []

        # Check each phrasal verb
        for pv in self.phrasal_verbs:
            # Split the phrasal verb into its components (verb and particle)
            parts = pv.lower().split()
            if len(parts) != 2:
                continue
            verb, particle = parts

            # Generate possible forms of the phrasal verb
            verb_forms = get_word_forms(verb)
            forms = [form + ' ' + particle for form in verb_forms['v']]

            # Check if any form is in the text
            for form in forms:
                if re.search(r'\b' + re.escape(form) + r'\b', text):
                    found_verbs.append(pv)
                    break

        return len(found_verbs) > 0

    def check_fluency(self, duration_seconds):
        if self.check_short_talk():
            return False
        return len(self.text)/duration_seconds > 11

    def check_vocabulary(self):
        if self.check_short_talk():
            return False
        return self.__vocabulary_log_exp() > 70

    def check_long_talk(self):
        words = re.findall(r'\b\w+\b', self.text)
        return len(words) > 30

    def check_short_talk(self):
        words = re.findall(r'\b\w+\b', self.text)
        return len(words) < 12

    def __vocabulary_log_exp(self, log_base=1.2, exp_factor=1.3, range_factor=2.5):
        word_pattern = r'\b\w+\b'
        words = re.findall(word_pattern, self.text.lower())

        if not words:
            return 0

        counter = 0
        for word in words:
            if len(word) == 1:
                continue

            found = False
            index = -1
            for i, elem in enumerate(self.common_words):
                if elem == word:
                    found = True
                    index = i
                    break

            if found:
                adjustment = 1 + (index // 100) * range_factor
                counter += (math.log(index + 1, log_base)
                            ** exp_factor) * adjustment
            elif self.__word_exists_in_english(word):
                # counter += (math.log(50000, log_base) ** exp_factor)
                # counter += (math.log(50000, log_base) ** exp_factor * 1.0) + 100
                counter += (math.log(50000, log_base)
                            ** exp_factor * 1.0) + 50000
                # counter += 5000

        if 0 < len(words) and len(words) < 5:
            return 0
        elif 5 <= len(words) and len(words) < 7:
            return round(counter / len(words) / 200) - 40
        elif 7 <= len(words) and len(words) < 9:
            return round(counter / len(words) / 200) - 30
        elif 9 <= len(words) and len(words) < 12:
            return round(counter / len(words) / 200) - 0
        elif 12 <= len(words) and len(words) < 15:
            return round(counter / len(words) / 200) + 10
        elif 15 <= len(words) and len(words) < 18:
            return round(counter / len(words) / 200) + 0
        elif 18 <= len(words) and len(words) < 22:
            return round(counter / len(words) / 200) + 20
        elif 22 <= len(words) and len(words) < 26:
            return round(counter / len(words) / 200) + 40
        else:
            return round(counter / len(words) / 200) + 40

    def __word_exists_in_english(self, word):
        word = word.lower()
        if self.__is_verb(word):
            word = self.__to_base_form(word)
        english_words = set(words.words())

        return word in english_words

    def __is_verb(self, word):
        synsets = wordnet.synsets(word)
        for synset in synsets:
            if synset.pos() == 'v':
                return True
        return False

    def __to_base_form(self, word):
        lemmatizer = WordNetLemmatizer()
        base_form = lemmatizer.lemmatize(word, 'v')
        return base_form

    def __check_fantasy(self):
        file_path = os.path.join(self.base_dir, 'data', 'fantasy.txt')

        with open(file_path, 'r') as file:
            words = file.read().splitlines()

        text_words = re.findall(r'\b\w+\b', self.text.lower())

        return any(word.lower() in text_words for word in words)

    def __check_complexity(self):
        return textstat.flesch_reading_ease(self.text) < 70

    def __check_fantasy(self):
        text_words = re.findall(r'\b\w+\b', self.text.lower())
        return any(word.lower() in text_words for word in self.fantasy)

    def __check_distant_ideas(self):
        inputs = self.tokenizer(self.text, padding='max_length',
                                truncation=True, max_length=30, return_tensors="tf")
        prediccion = self.model.predict(
            {'input_ids': inputs['input_ids'], 'attention_mask': inputs['attention_mask']})
        return prediccion[0, 0] >= 0.5
