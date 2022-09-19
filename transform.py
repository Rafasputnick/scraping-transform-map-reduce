from pandas import read_json

df = read_json('pokemons.json')

df[df.columns[11:29]] = df[df.columns[11:29]].replace('½', '0.5', regex=True)
df[df.columns[11:29]] = df[df.columns[11:29]].replace('¼', '0.25', regex=True)
df[df.columns[11:29]] = df[df.columns[11:29]].astype(float)

df['Name'] = df['Name'].replace('♂','-male', regex=True)
df['Name'] = df['Name'].replace('♀','-female', regex=True)

print(df)

df.to_json("pokemons_tratado.json", orient="records", lines=True)
