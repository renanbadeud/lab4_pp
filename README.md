# lab4_pp

## Funcionamento:

Inicialmente espera-se que os 10 clients sejam iniciados e estejam conectados. Em seguida cada client manda seu client_id (Timestamp em que foi criado) para 
os demais a fim de ser identificado. Então é realizada a eleição, onde cada client envia seu voto (número aleatório entre 0 e 9), o lider é o client que recebe 
o maior número de votos, em caso de empate é utilizado o maior client_id. Por fim, o líder envia um challenge para ele e os demais clients, cada client busca a
seed que soluciona o desafio e assim que a encontra, submete aos demais clients que verificam se ela é válida, se for válida o client que a submeteu vence.
O processo se repete, o challenge muda a cada iteração e o líder continua fixo.

## Topicos utilizados:

- 'init': topico onde é submetido o id de cada client, após cada client ter a lista com seu id e dos demais começa a fase da eleição onde os votos são enviados para o topico election.
- 'election': topico onde é submetido o voto de cada client, após cada client ter a lista com seu voto e dos demais, é verificado o numero mais frequente da lista, que é eleito o líder.
Em caso de empate é utilizado o maior client_id. Em seguida o líder publica o desafio no tópico challenge.
- 'challenge': tópico onde os clients recebem os desafios, cada client resolve o desafio, assim que encontra a seed o client a submete ao tópico ppd/seed.
- 'ppd/seed': tópico onde é recebido a seed, os clients verificam se essa seed é valida, se todos os clients aprovaram a seed, o client que a submeteu vence, posteriomente é publicado pelo líder um novo desafio no tópico challenge.


