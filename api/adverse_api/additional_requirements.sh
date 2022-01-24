#!bin/bash

sudo apt-get install firefox make
wget https://github.com/hroptatyr/finner/releases/download/v0.2.0/finner-0.2.0.tar.xz
tar -xvf finner-0.2.0.tar.xz
cd ./finner-0.2.0/
./configure  
make  
make install

python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
python -m nltk.downloader punkt
python -m nltk.downloader stopwords
python -m nltk.downloader wordnet
python -m nltk.downloader averaged_perceptron_tagger
python -m nltk.downloader maxent_ne_chunker
python -m nltk.downloader maxent_treebank_pos_tagger
python -m nltk.downloader words
