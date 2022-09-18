import scrapy

LAST_POKEMON_NAME = "Mew"

def normalize_pokemon_number(pokemon_number: str):
  return '#' + (str(pokemon_number).strip())[2:].strip()

def normalize_str(pokemon_name: str):
  return str(pokemon_name).strip()

class PokemonScrapper(scrapy.Spider):
  name = 'pokemon_scrapper'
  domain = 'https://www.pokemon.com'

  start_urls = ["https://www.pokemon.com/br/pokedex/bulbasaur"]

  new_url = ''

  def parse(self, response):
    pokemon_details = {}

    div_titulo = response.css("div.pokedex-pokemon-pagination-title")
    pokemon_details['Name'] = normalize_str(div_titulo.css(".pokedex-pokemon-pagination-title div::text").extract_first())
    pokemon_details['Number'] = normalize_pokemon_number(div_titulo.css("span.pokemon-number::text").extract_first())

    pokemon_evolution_list = response.css(".evolution-profile > li")

    current_pokemon = False
    already_satisfied = False
    for li in pokemon_evolution_list:
      evolution_name = normalize_str(li.css("a h3::text").extract_first())
      evolution_number = normalize_pokemon_number(li.css("a h3 span::text").extract_first())
      if current_pokemon and not already_satisfied:
        pokemon_details['Evolution Name'] = evolution_name
        pokemon_details['Evolution Number'] = evolution_number
        already_satisfied = True

      if evolution_name == pokemon_details['Name']:
        current_pokemon = True


    info_table = response.css("div.column-7 > ul li")
    for i in range(5):
      detail = info_table[i]
      detail_name = normalize_str(detail.css("span.attribute-title::text").extract_first())
      if detail_name == "Gender":
        detail_value = detail.css("span.attribute-value i")
        genders = []
        if detail_value.css(".icon_male_symbol").extract_first() != None:
          genders.append('M')
        if detail_value.css(".icon_female_symbol").extract_first() != None:
          genders.append('F')
        if not genders:
          detail_value = 'Unknown'
        else:
          detail_value = ', '.join(genders)
      else:
        detail_value = normalize_str(detail.css("span.attribute-value::text").extract_first())
      
      pokemon_details[detail_name] = detail_value

    types = response.css("a[href*=type]::text").extract()
    pokemon_details['Types'] = ', '.join(types)

    weaknesses = response.css("a[href*=weakness] span::text").extract()
    weaknesses_stripped = list(map(normalize_str, weaknesses))
    pokemon_details['Weaknesses'] = ', '.join(weaknesses_stripped)

    pokemon_path = response.css("div.pokedex-pokemon-pagination a.next::attr(href)").extract_first()
    pokemon_name = pokemon_details['Name']
    if pokemon_name == LAST_POKEMON_NAME:
      new_url = None
    else:
      self.new_url = response.urljoin(pokemon_path)

    pokemon_name = self.avoid_error_404(pokemon_name)
    damage_url = f"https://pokemondb.net/pokedex/{pokemon_name.lower()}" 
    yield scrapy.Request(damage_url, callback=self.parse_damage_value, meta={'item': pokemon_details})
    
  def parse_damage_value(self, response):
    pokemon_details = response.meta['item']
    types = response.css("th a.type-icon::text").extract()
    damage_html = response.css("td.type-fx-cell")
    damage_value_list = []
    for damage in damage_html:
      damage_value = damage.css("::text").extract_first()
      if damage_value == None:
        damage_value_list.append('1')
      else:
        damage_value_list.append(damage_value)
    for index, type in enumerate(types):
      key = f"Damage_by_{type}"
      pokemon_details[key] = damage_value_list[index]
    
    pok_color_url = f"https://pokemon.fandom.com/wiki/{pokemon_details['Name']}" 
    yield scrapy.Request(pok_color_url, callback=self.parse_pokedex_color, meta={'item': pokemon_details})
    
    

  def parse_pokedex_color(self, response):
    pokemon_details = response.meta['item']
    color = response.css("div[data-source=color] font::text").extract_first()
    pokemon_details['Pokedex Color'] = color
    yield(pokemon_details)
    if self.new_url != None: 
      yield scrapy.Request(self.new_url, callback=self.parse)

  def avoid_error_404(self, pokemon_name):
    if pokemon_name == 'Nidoran♀':
      return 'nidoran-m'
    if pokemon_name == 'Nidoran♂':
      return 'nidoran-f'
    if pokemon_name == 'Mr. Mime':
      return 'mr-mime'
    return pokemon_name
