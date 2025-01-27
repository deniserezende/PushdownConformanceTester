O arquivo texto de entrada com o modelo IOVPTS deve ser descrito da seguinte forma:
1) Nas 5 primeiras linhas defina os conjuntos de ações: linha 1 os CALLs, linha 2 os RETURN, linha 3 os INTERNAL, linha 4 os INPUT, e finalmente na linha 5 os OUTPUT.
2) Na sexta linha defina os símbolos de pilha
3) Na linha 7 descreva os estados do modelo
4) Da linha 8 em diante defina as transições do modelo. Cada transição deve ser escrita formato s,a,Z,q em linhas separadas: s é o estado origem, a é a ação, Z o símbolo de pilha e q o estado destino. 
5) Após definir todas as transições, use o símbolo # para indicar na próxima linha o estado inicial do modelo. E por fim o símbolo - (traço) para indicar o fim da especificação:
#
s0
-

Observações:

1- Sempre quando houver mais itens (símbolos, estados, ações, etc) por linha, separe por vírgula. 
2- No final de cada linha NÃO deve conter nenhum símbolo, tais como ponto, ponto e vírgula, etc. 
3- Se um conjunto for vazio (por exemplo, o modelo não tem ações internas), deixe uma linha em branco.
4- Uma transição simples (de Li) ou uma transição interna (com \varsigma) é definida com @ como símbolo de pilha.
5- Já o símbolo de pilha vazia (\bot) é definido como *. 
