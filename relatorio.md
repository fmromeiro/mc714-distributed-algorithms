# Relatório

## Montagem de ambiente

Para montar um ambiente de sistemas distribuídos, optamos por usar imagens Docker. Para isso, criamos um Dockerfile que usa uma imagem Docker com Python 3.10 como base, copia os arquivos da pasta para a imagem Docker e executa o arquivo app.py. Então, montamos um arquivo docker-compose que sobe 4 cópias dessa imagem, possibilitando um sistema distribuído com 4 instâncias.

## Relógio Lógico

Para implementar o relógio lógico, criamos uma aplicação que sobe um servidor RPC que responde um número aleatório. Para fazer o relógio lógico, encapsulamos as chamadas do RPC, tanto de solicitação quanto de resposta, com chamadas ao relógio lógico.

### Implementação

#### RPC

A implementação do servidor RPC foi feita no arquivo _app.py_ usando a biblioteca `xmlrpc` por ser uma biblioteca padrão do Python, facilitando a montagem do ambiente. Para isso, nos baseamos no [exemplo do PythonBrasil](https://wiki.python.org.br/XmlRpc) e na [documentação oficial do Python](https://docs.python.org/3/library/xmlrpc.server.html).

A comunicação RPC foi fácil de implementar, a interface da biblioteca é bem explícita. Tivemos um único problema em que estávamos criando o servidor usando o endereço `"localhost"`, e por isso ele não estava visível para os demais serviços Docker. Porém, seguimos [essa resposta do StackOverflow](https://stackoverflow.com/questions/30771113/python-simplexmlrpcserver-socket-error-connection-refused), substituímos o endereço por `"0.0.0.0"` e conseguimos conectar cliente e servidor RPC sem problemas.

Para comunicar os serviços Docker, simplesmente usamos o nome declarado no _docker-compose.yml_, como explicado nessa [resposta do StackOverflow](https://stackoverflow.com/questions/59657860/how-to-access-a-service-in-docker-compose-from-another-sevice), e o mapeamento entre IP e DNS foi realizado automaticamente pelo Docker.

Visando o compartilhamento de relógio entre cliente e servidor RPC, fizemos as duas aplicações rodarem no mesmo processo, usando a API de threads do Python. Para isso, fizemos o servidor rodar numa thread própria e deixamos o cliente rodando na thread principal. Para implementar as threads, nos baseamos nesse [artigo do Real Python](https://realpython.com/intro-to-python-threading/). Sobre as threads, tomamos o cuidado de criar a thread do servidor como um _daemon_ para que a instância não espere o servidor encerrar para fechar o processo, já que o processo do servidor é infinito.

#### Relógio Lógico

Para implementar o relógio lógico, criamos uma classe Python que mantém o estado do relógio.

Pensando no caso de eventos que não envolvem a comunicação entre processos, criamos um método `event` que simplesmente atualiza o relógio.

Já visando a comunicação entre os processos, criamos os métodos `send` e `recv` que recebem uma função, encapsulam a comunicação com as atualizações e comunicações de relógio necessárias e retornam uma função pronta para atualizar o relógio com a mesma interface que a original.

A implementação desses métodos foi baseada no algoritmo do Slide 10 da aula 17.

#### Paralelismo

Durante os testes, percebemos que primeiro várias requisições RPC ocorriam e depois o log de todas as requisições aparecia da uma vez. Pensamos que isso poderia ser um problema de threads, então começamos a usar implementações _thread safe_. Nos baseando [nesse artigo do Real Python](https://realpython.com/python-sleep/#adding-a-python-sleep-call-with-threads), substituímos os usos de `sleep` por `event.wait`. Nesse mesmo artigo, percebemos que `print` não é _thread safe_, então substituímos o seu uso pela biblioteca de logging, nos baseando em [sua documentação](https://docs.python.org/3/howto/logging.html#logging-basic-tutorial).

Não observamos nenhum caso, mas percebemos que poderiam haver _race conditions_ no relógio entre cliente e servidor, então encapsulamos os acessos à variável de relógio com um semáforo, nos baseando no [artigo de threading do Real Python](https://realpython.com/intro-to-python-threading/#basic-synchronization-using-lock).

### Testes

Para testar o funcionamento do relógio lógico, fizemos o cliente esperar um tempo aleatório e fazer uma chamada RPC para alguma outra instância aleatória. Com isso, conseguimos observar o funcionamento do relógio lógico a partir dos logs da classe `Clock`.

O comportamento aleatório do cliente viabilizou a criação de vários casos, permitindo averiguar o funcionamento do relógio em cada um deles.

Para executar as instâncias de teste com os logs, basta rodar `docker compose up --build`.