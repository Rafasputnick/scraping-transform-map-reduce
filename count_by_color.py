import json

from mrjob.job import MRJob
from mrjob.step import MRStep


class CountByColor(MRJob):
    def steps(self):
        return [MRStep(mapper=self.mapper, reducer=self.reducer)]

    def mapper(self, _, line):
        pokemon_detail = json.loads(line)
        color = pokemon_detail["Pokedex Color"]
        yield (color, 1)

    def reducer(self, key, value):
        yield (key, sum(value))


if __name__ == "__main__":
    CountByColor.run()
