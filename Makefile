test.vocab: test.words
	python ./build_vocab.py < test.words > test.vocab
clean:
	rm test.vocab
