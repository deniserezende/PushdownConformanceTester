import sys
from copy import deepcopy
import logging
from iovpts import IOVPTS, read_iovpts_file
from faultModel import FaultModel
from balancedRunChecker import BalancedRunChecker
from product import Product
import product as simplifyProduct
import streamlit as st
import io  # Import to handle in-memory binary files

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s  \n%(filename)s - %(funcName)s\n',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# Título e subtítulo no Streamlit
st.title("ioco-like")
st.subheader("Verificação de Conformidade")

# Seção de Ajuda
with st.expander("Ajuda", expanded=False):
    st.markdown("""
    **Como usar esta ferramenta:**
    
    1. **Upload dos Arquivos:** Carregue dois arquivos em formato `.txt`. Um deve conter a especificação e o outro a implementação.
    2. **Verificação de Conformidade:** Após o upload dos arquivos, clique no botão "Verificar Conformidade". A ferramenta irá analisar a conformidade ioco-like.
    3. **Resultado:** O resultado da verificação será exibido na tela, juntamente com detalhes do processo.
    4. **Download dos Detalhes:** Você pode baixar um arquivo contendo todos os detalhes da verificação clicando no botão "Baixar Detalhamento Completo".
    
    **Observações:**
    - Ambos os arquivos são necessários para realizar a verificação.
    - Certifique-se de que os arquivos estão formatados corretamente. Eles devem seguir esta estrutura:
      - **Linha 1:** Ações CALL (empilham símbolos).
      - **Linha 2:** Ações RETURN (desempilham símbolos).
      - **Linha 3:** Ações INTERNAL (não afetam a pilha).
      - **Linha 4:** Ações INPUT (eventos do ambiente externo).
      - **Linha 5:** Ações OUTPUT (eventos gerados pelo sistema).
      - **Linha 6:** Símbolos de pilha, incluindo `@` (transições internas) e `*` (estado de pilha vazia).
      - **Linhas 7:** Estados do modelo.
      - **Linhas 8 até x:** Transições do modelo no formato: estado_origem,ação,símbolo_de_pilha,estado_destino
      - **Linhas (x+1):** Símbolo # que indica o fim da descrição de transições.
      - **Linhas (x+2):** Estado inicial do modelo.
      - **Linhas (x+3):** Símbolo - para indicar o fim da descrição do modelo. 

    Lembre-se de que cada linha deve ser formatada corretamente, sem símbolos adicionais no final, e uma linha em branco deve ser deixada para conjuntos vazios.
    Sempre quando houver múltiplos itens (símbolos, estados, ações, etc) por linha separe por vírgula sem espaço.
    """)
# Instruções para o usuário
st.markdown("Por favor, faça o upload dos arquivos de especificação e implementação em formato `.txt`. Ambos os arquivos são necessários para verificar a conformidade ioco-like.")

# Upload dos arquivos
specificationFile = st.file_uploader("Escolha o arquivo de Especificação", type=['txt'], key="file1")
implementationFile = st.file_uploader("Escolha o arquivo de Implementação", type=['txt'], key="file2")

if specificationFile:
    st.success(f"Especificação carregada: {specificationFile.name}")
if implementationFile:
    st.success(f"Implementação carregada: {implementationFile.name}")

if st.button("Verificar Conformidade"):
    if not specificationFile or not implementationFile:
        st.error("Por favor, carregue ambos os arquivos de especificação e implementação.")
    else:
        with st.spinner("Processando arquivos..."):
            # Armazenar as saídas detalhadas
            details = []

            # Criando os modelos de IOVPTS para a especificação e implementação
            specificationIOVPTS = IOVPTS()
            specificationIOVPTS = read_iovpts_file(specificationFile)
            implementationIOVPTS = IOVPTS()
            implementationIOVPTS = read_iovpts_file(implementationFile)

            specificationPath = specificationFile.name
            implementationPath = implementationFile.name

            # Logging de informações iniciais
            st.info(f"Testando o IUT descrito no arquivo {implementationPath} contra a especificação (SPEC) no arquivo {specificationPath}\n")
            details.append(f"Testando o IUT descrito no arquivo {implementationPath} contra a especificação (SPEC) no arquivo {specificationPath}\n")
            details.append(f"\nIOVPTS specification:")
            specificationIOVPTS.save_iovpts_info_to_list(details)
            details.append(f"\nIOVPTS implementation:")
            implementationIOVPTS.save_iovpts_info_to_list(details)

            # Criando o Fault Model (FM)
            fault_model = FaultModel(specificationIOVPTS)
            fault_model.generate_fault_model()

            # Logging Fault Model
            details.append(f"\nFault model para a especificação dada:")
            fault_model.save_faultmodel_info_to_list(details)

            # Construção do produto entre FM e implementação
            product = Product(fault_model, implementationIOVPTS)
            product.compute_product()
            product.save_product_info_to_list(details)

            # Simplificação dos resultados do produto
            estados = simplifyProduct.compute_estados(product, specificationIOVPTS, implementationIOVPTS)
            pilha = simplifyProduct.compute_pilha(product)
            novosestados, transicoes, str_estados = simplifyProduct.compute_transicoes(product, estados, pilha)
            simplifyProduct.save_dictionaries_info_to_list(estados, pilha, str_estados, transicoes, details)

            # Verificação de balanced run
            checker = BalancedRunChecker(specificationIOVPTS.calls, specificationIOVPTS.returns, specificationIOVPTS.internal, str_estados, transicoes, 0, len(str_estados) - 1)
            balanced_run, string = checker.check_balanced_run()

            # Resultado final para o usuário
            if not balanced_run:
                st.info("O IUT está em conformidade ioco-like com a especificação.")
                details.append("\nVeredito: O IUT está em conformidade ioco-like com a especificação.\n")
            else:
                st.info(f"O IUT não está em conformidade com a especificação. {string}")
                details.append(f"\nVeredito: O IUT não está em conformidade com a especificação.\n")
                details.append(f"Um caso de teste que mostra essa condição é: {string}\n")

            print(f"details: {details}")

            # Salvar detalhes em um arquivo de log na memória
            # buffer = io.BytesIO()
            # buffer.write("\n".join(details).encode('utf-8'))  # Write as binary (utf-8)
            # buffer.seek(0)  # Reset the buffer's position to the beginning
            
            import io

            # Função para garantir que todos os itens em details sejam strings
            def convert_to_string(item):
                if isinstance(item, list) or isinstance(item, dict):
                    return str(item)  # Converte listas e dicionários para strings
                return item  # Mantém os outros itens como estão

            # Converte cada item da lista para string se necessário
            details = [convert_to_string(item) for item in details]

            # Criação do buffer em memória
            buffer = io.BytesIO()

            # Escreve os detalhes no buffer, convertendo a lista em uma string separada por quebras de linha
            buffer.write("\n".join(details).encode('utf-8'))  # Escreve em binário (utf-8)

            # Posiciona o buffer de volta no início
            buffer.seek(0)

            # Remove .txt extension if it exists
            spec_name = specificationFile.name.lower().replace(" ", "_").replace(".txt", "")
            impl_name = implementationFile.name.lower().replace(" ", "_").replace(".txt", "")

            # Generate the filename
            filename = f"{spec_name}-{impl_name}.txt"
            # Exemplo de como salvar o buffer em um arquivo
            with open(filename, "wb") as f:
                f.write(buffer.getvalue())
                
            # Fornecer o botão de download
            st.download_button('Baixar Detalhamento Completo', buffer, file_name=filename)