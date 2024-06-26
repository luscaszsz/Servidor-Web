#implementação de um servidor base para interpratação de métodos HTTP
import socket

#definindo o endereço IP do host
SERVER_HOST = "localhost"

#definindo o número da porta em que o servidor irá escutar pelas requisições HTTP
SERVER_PORT = 80

#vamos criar o socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#vamos setar a opção de reutilizar sockets já abertos
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#atrela o socket ao endereço da máquina e ao número de porta definido
server_socket.bind((SERVER_HOST, SERVER_PORT))

#coloca o socket para escutar por conexões
server_socket.listen(1)

#mensagem inicial do servidor
print("Servidor em execução...")
print("Escutando por conexões na porta %s" % SERVER_PORT)

#cria o while que irá receber as conexões
while True:
    #espera por conexões
    #client_connection: o socket que será criado para trocar dados com o cliente de forma dedicada
    #client_address: tupla (IP do cliente, Porta do cliente)
    client_connection, client_address = server_socket.accept()

    #pega a solicitação do cliente
    request = client_connection.recv(1024).decode()
    #verifica se a request possui algum conteúdo (pois alguns navegadores ficam periodicamente enviando alguma string vazia)
    if request:
        #imprime a solicitação do cliente
        print(request)
        
        #analisa a solicitação HTTP
        headers = request.split("\n")
        #print(headers)#impressão dos cabeçalhos
        #pega o nome do arquivo sendo solicitado
        filename = headers[0].split()[1]

        #verifica qual arquivo está sendo solicitado e envia a resposta para o cliente
        if filename == "/":
            filename = "/index.html"
        #try e except para tratamento de erro quando um arquivo solicitado não existir
        #tratamento do GET primeiro
        if headers[0].split()[0]=="GET":
            try:
                if filename.split('.')[-1] in ['html','css','js']:
                    #abrir o arquivo e enviar para o cliente
                    fin = open("htdocs" + filename)
                    
                else:
                    #leio o conteúdo do arquivo para uma variável
                    fin = open("htdocs" + filename, 'rb')
                content = fin.read()
                #fecho o arquivo
                fin.close()
                #envia a resposta html
                if filename.split('.')[-1] in ['html','css','js']:
                    response = "HTTP/1.1 200 OK\n\n" + content
                    client_connection.sendall(response.encode())
                #envia resposta nao html
                else:
                    response = bytes("HTTP/1.1 200 OK\n\n", 'utf-8') + content
                    client_connection.sendall(response)
            except FileNotFoundError:
                #caso o arquivo solicitado não exista no servidor, gera uma resposta de erro
                response = "HTTP/1.1 404 NOT FOUND\n\n<h1>ERROR 404!<br>{} nao encontrado</h1>".format(filename)
                client_connection.sendall(response.encode())
            client_connection.close()
        
        
        #tratamento do put
        elif headers[0].split()[0]=="PUT":
            #cria o arquivo em htdocs com nome passado
            nomeArq = open("htdocs" + headers[0].split()[1], 'x')

            #procura onde começa o body
            for linha in reversed(headers):
                if linha == '\r' or linha == '':
                    indice=headers.index(linha)

                    #escreve no arquivo criado linhas do body
                    nomeArq.writelines(headers[indice+1:])
            response = "HTTP/1.1 201 CREATED\n\n"
            client_connection.sendall(response.encode())
            
            #arquivo criado e já em htdocs
            nomeArq.close()
            client_connection.close()



server_socket.close()


