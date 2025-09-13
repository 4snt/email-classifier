from app.infrastructure.nlp.tokenizer_simple import SimpleTokenizer

tk = SimpleTokenizer(lang="pt")

sample = """
A mineralogia é a ciência que estuda os minerais, o que são, como são formados e onde 
ocorrem. O termo mineralogia deriva da palavra latina minera, de provável origem céltica 
(mina). Forma o adjetivo do latim mineralis, relativo às minas e o substantivo do latim 
minerale (produto das minas), que deu origem ao adjetivo e substantivo português mineral, 
acrescido do sufixo grego logos (ciência, estudo).
Uma vez que os minerais estão por toda parte e fornecem uma grande parte das matérias 
primas usadas em aplicações tecnológicas e industriais, o potencial de aplicação deste 
conhecimento é vasto, embora estabelecer um conceito claro e preciso de mineral gera 
algumas controvérsias. O conceito mais utilizado é o de Klein e Hurlbut (1999)
"""

print("Texto original:")
print(sample)

pre = tk.preprocess(sample)
print("\nPré-processado:")
print(pre)

tokens = tk.tokenize(pre)
print("\nTokens:")
print(tokens)
