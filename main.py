import scrapy

class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  start_urls = ['https://pokemondb.net/pokedex/all']

  # Metodo principal da execução
  def parse(self, response):
    linhas = response.css('table#pokedex > tbody > tr')
    for linha in linhas:
      link = linha.css("td:nth-child(2) > a::attr(href)")
      yield response.follow(link.get(), self.parser_pokemon)

  # Método para extrair as habilidades do pokemon
  def parser_habilidades(self, response):
    # Extrair nome e descricação da habilidade
    nome_habilidade = response.css('h1::text').get()
    descricao_habilidade = response.xpath(
      '//*[@id="main"]/div[1]/div[1]/p/text()').getall()

    yield {
      "nome": response.meta["nome"],
      "url_pokemon": response.meta["url_pokemon"],
      "numero": response.meta["numero"],
      "peso": response.meta["peso"],
      "altura": response.meta["altura"],
      "tipos": response.meta["tipos"],
      "evolucoes": response.meta["evolucoes"],
      "habilidades": {
        "url": response.url,
        "nome": nome_habilidade,
        "descricao": descricao_habilidade
      }
    }

  # Método para extrair as informaçõoes do pokemon
  def parser_pokemon(self, response):
    # Extrair Nome do pokemon
    nome = response.css('h1::text')
    # Extrair Número do pokemon
    numero = response.css(
      'table.vitals-table > tbody > tr:nth-child(1) > td > strong::text')
    # Extrair Peso do pokemon
    peso = response.css(
      'table.vitals-table > tbody > tr:nth-child(5) > td::text')
    # Extrair Altura/tamanho do pokemon
    altura = response.css(
      'table.vitals-table > tbody > tr:nth-child(4) > td::text')
    # Extrair Tipo(s) do pokemon
    tipo = response.css('th:contains("Type") + td a::text').getall()
    tipos = [i.strip() for i in tipo]
    # Indentificar div pai/container das evoluções
    evolucao = response.css(
      'h2:contains("Evolution chart") + div.infocard-list-evo > div.infocard')
    # Declarar array de que contera as evoluções
    array_evolucoes = []
    # Percorrer a div pai e encontrar as informações de numero, nome e url
    for evolucoes in evolucao:
      numero_evolucao = evolucoes.css('small::text').get()
      nome_evolucao = evolucoes.css('a.ent-name::text').get()
      url_evolucao = evolucoes.css('a::attr(href)').get()

      if numero_evolucao and nome_evolucao and url_evolucao:
        array_evolucoes.append({
          "numero": numero_evolucao,
          "nome": nome_evolucao,
          "url": url_evolucao
        })
    # Indentificar link para acessar as habilidades
    link_habilidades = response.css(
      'table.vitals-table > tbody > tr:nth-child(6) td a::attr(href)')
    # Loop dos links
    for link_habilidade in link_habilidades:
      # Acessar link da pagina e enviar os dados até o momento extraidos
      yield response.follow(link_habilidade,
                            self.parser_habilidades,
                            meta={
                              "nome": nome.get(),
                              "url_pokemon": response.url,
                              "numero": numero.get(),
                              "peso": peso.get(),
                              "altura": altura.get(),
                              "tipos": tipos,
                              "evolucoes": array_evolucoes
                            })
