import nltk
import jieba
import os

def __is_punkt_exist(nltk_data_dir):
    folder_path = f"{nltk_data_dir}/tokenizers/punkt"
    file_path = f"{nltk_data_dir}/tokenizers/punkt.zip"
    return os.path.exists(folder_path) and os.path.isfile(file_path)


# default is download to: /root/nltk_data
# use download_dir to change path.
download_dir = './nltk_data'
nltk.data.path.append(download_dir)
print(f"nltk.data.path: {nltk.data.path}")

if not __is_punkt_exist(download_dir):
    nltk.download('punkt', download_dir=download_dir)
else:
    print('punkt already exist.')


def get_sentences(text):
    special_separator = '|||||'
    sentences = nltk.sent_tokenize(text)
    #print("\nnltk:")
    #for sentence in sentences:
        #print(sentence)

    #join backed
    text = special_separator.join(sentences)
    #print("\njoin backed:")
    #print(text)


    # Segment text into words
    words = jieba.lcut(text, cut_all=False, HMM=True)
    #print("\njieba words:")
    #print(words)

    # Define sentence separator
    separators = ["。", "？", "！"]

    # Join words back into sentences using separator
    sentences = []
    sentence = ""
    for word in words:
        sentence += word
        if word in separators:
            sentences.append(sentence.strip())
            sentence = ""
    # join back the remainings
    sentences.append(sentence.strip())
    sentence = ""

    # Print the final list of sentences
    #print("\njieba:")
    #for sentence in sentences:
        #print(sentence)

    #join backed
    text = special_separator.join(sentences)
    #print("\njoin backed:")
    #print(text)

    #split
    sentences = text.split(special_separator)
    #print("\nsplit:")
    #for sentence in sentences:
        #print(sentence)

    return sentences

'''
sentences = get_sentences("hello all. 你好。 Hi hi ho ho? 可以吗？angry angry! 生气了咯！what?! Huh?")
print(result)
for sentence in sentences:
        print(sentence)
'''
